import cv2
import mediapipe as mp
import numpy as np
import math

class PoseDetector:
    def __init__(self, static_image_mode=False, model_complexity=0, smooth_landmarks=True, min_detection_confidence=0.5, min_tracking_confidence=0.5):
        self.mp_pose = mp.solutions.pose
        self.mp_draw = mp.solutions.drawing_utils
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            model_complexity=model_complexity,
            smooth_landmarks=smooth_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.results = None

    def find_pose(self, img, draw=True):
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.pose.process(img_rgb)
        if self.results.pose_landmarks and draw:
            self.mp_draw.draw_landmarks(img, self.results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
        return img

    def get_position(self, img, draw=False):
        lm_list = []
        if self.results and self.results.pose_landmarks:
            h, w, _ = img.shape
            for id, lm in enumerate(self.results.pose_landmarks.landmark):
                cx, cy = int(lm.x * w), int(lm.y * h)
                lm_list.append([id, cx, cy, lm.z, lm.visibility])
                if draw:
                    cv2.circle(img, (cx, cy), 4, (0, 255, 135), cv2.FILLED)
        return lm_list
    
    def check_body_visibility(self, lm_list, img_shape):
        """
        Check if key body parts (head, shoulders, hips, knees, ankles) are visible in the frame.
        Returns: (is_good: bool, message: str, status_code: str)
        """
        if not lm_list or len(lm_list) < 33:
            return False, "❌ ไม่พบผู้ใช้งานในกล้อง กรุณายืนหน้ากล้อง", "NOT_FOUND"
            
        h, w = img_shape[:2]
        
        # Check key landmarks visibility
        # 0: nose, 11: left shoulder, 12: right shoulder, 23: left hip, 24: right hip, 27: left ankle, 28: right ankle
        key_indices = [0, 11, 12, 23, 24, 27, 28]
        low_vis_count = 0
        
        for idx in key_indices:
            if idx < len(lm_list):
                vis = lm_list[idx][4]
                y = lm_list[idx][2]
                x = lm_list[idx][1]
                if vis < 0.45 or y < 5 or y > h - 5 or x < 5 or x > w - 5:
                    low_vis_count += 1
                    
        # Check if ankles are cut off (too close to camera)
        ankles_visible = (lm_list[27][4] > 0.4 or lm_list[28][4] > 0.4)
        head_visible = (lm_list[0][4] > 0.5)
        
        if not ankles_visible and not head_visible:
            return False, "⚠️ กรุณาถอยห่างจากกล้อง ให้เห็นทั้งตัว", "TOO_CLOSE"
        elif not ankles_visible:
            return True, "💡 แนะนำ: ถอยห่างอีกนิดเพื่อให้เห็นช่วงขาชัดเจน", "PARTIAL"
        elif low_vis_count >= 3:
            return False, "⚠️ แสงสว่างไม่เพียงพอ หรือร่างกายอยู่นอกกรอบ", "LOW_LIGHT"
            
        return True, "✅ ตำแหน่งพร้อม ออกกำลังกายได้เลย!", "PERFECT"

    def calculate_angle(self, p1, p2, p3):
        # Calculate angle between three points
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        
        angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
        if angle < 0:
            angle += 360
            
        if angle > 180:
            angle = 360 - angle
            
        return angle
        
    def get_joint_angles(self, lm_list):
        if not lm_list or len(lm_list) < 33:
            return {}
            
        angles = {}
        
        def get_coords(idx):
            return (lm_list[idx][1], lm_list[idx][2])
            
        try:
            # Left side
            angles['left_elbow'] = self.calculate_angle(get_coords(11), get_coords(13), get_coords(15))
            angles['left_shoulder'] = self.calculate_angle(get_coords(13), get_coords(11), get_coords(23))
            angles['left_hip'] = self.calculate_angle(get_coords(11), get_coords(23), get_coords(25))
            angles['left_knee'] = self.calculate_angle(get_coords(23), get_coords(25), get_coords(27))
            
            # Right side
            angles['right_elbow'] = self.calculate_angle(get_coords(12), get_coords(14), get_coords(16))
            angles['right_shoulder'] = self.calculate_angle(get_coords(14), get_coords(12), get_coords(24))
            angles['right_hip'] = self.calculate_angle(get_coords(12), get_coords(24), get_coords(26))
            angles['right_knee'] = self.calculate_angle(get_coords(24), get_coords(26), get_coords(28))
        except Exception:
            pass
            
        return angles
