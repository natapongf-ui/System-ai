import numpy as np
from app.audio.voice_alert import voice_alert

class PoseComparator:
    def __init__(self):
        self.thresholds = {
            'squat': {'knee': 90, 'hip': 100},
            'pushup': {'elbow': 90, 'shoulder': 45},
            'bicep_curl': {'elbow_up': 45, 'elbow_down': 160}
        }
        
    def compare_pose(self, current_angles, reference_angles):
        if not current_angles or not reference_angles:
            return 0.0, []
            
        score = 0
        total_joints = 0
        feedback = []
        
        for joint, ref_angle in reference_angles.items():
            if joint in current_angles:
                curr_angle = current_angles[joint]
                diff = abs(curr_angle - ref_angle)
                
                # Max difference allowed is 45 degrees
                joint_score = max(0, 100 - (diff / 45 * 100))
                score += joint_score
                total_joints += 1
                
                if diff > 30:
                    if 'elbow' in joint:
                        if curr_angle > ref_angle:
                            feedback.append("กรุณางอแขนเพิ่มขึ้น")
                        else:
                            feedback.append("กรุณาเหยียดแขนให้ตรง")
                    elif 'knee' in joint:
                        if curr_angle > ref_angle:
                            feedback.append("ย่อเข่าลงอีกเล็กน้อย")
                        else:
                            feedback.append("ยืดเข่าขึ้นเล็กน้อย")
                    elif 'back' in joint or 'hip' in joint:
                        feedback.append("กรุณาทำหลังให้ตรง")
                        
        if total_joints == 0:
            return 0.0, []
            
        final_score = score / total_joints
        
        # Deduplicate feedback
        feedback = list(set(feedback))
        
        return final_score, feedback

class RepCounter:
    def __init__(self, exercise_type):
        self.exercise_type = exercise_type
        self.count = 0
        self.state = "UP" # Initial state
        self.feedback = ""
        
    def update(self, angles, accuracy_score):
        if not angles:
            return self.count, self.state, self.feedback
            
        self.feedback = ""
        
        # Use average of left and right if both available, otherwise use whichever is available
        def get_angle(joint_name):
            left = angles.get(f'left_{joint_name}')
            right = angles.get(f'right_{joint_name}')
            if left is not None and right is not None:
                return (left + right) / 2
            return left or right or 0

        # Squat logic
        if self.exercise_type == 'squat':
            knee_angle = get_angle('knee')
            hip_angle = get_angle('hip')
            
            if knee_angle > 160 and hip_angle > 160:
                if self.state == "DOWN":
                    if accuracy_score > 75:
                        self.count += 1
                        self.feedback = "สควอทยอดเยี่ยมมาก!"
                        voice_alert.play(self.feedback)
                    else:
                        self.feedback = "ย่อให้ลึกขึ้น หลังตรง"
                        voice_alert.play(self.feedback)
                self.state = "UP"
            elif knee_angle < 110 and hip_angle < 120:
                self.state = "DOWN"
                
        # Push Up logic
        elif self.exercise_type == 'pushup':
            elbow_angle = get_angle('elbow')
            
            if elbow_angle > 155:
                if self.state == "DOWN":
                    if accuracy_score > 75:
                        self.count += 1
                        self.feedback = "วิดพื้นยอดเยี่ยม!"
                        voice_alert.play(self.feedback)
                    else:
                        self.feedback = "ดันแขนให้สุด"
                        voice_alert.play(self.feedback)
                self.state = "UP"
            elif elbow_angle < 100:
                self.state = "DOWN"
                
        # Bicep Curl logic
        elif self.exercise_type == 'bicep_curl':
            elbow_angle = get_angle('elbow')
            
            if elbow_angle > 150:
                if self.state == "UP":
                    if accuracy_score > 75:
                        self.count += 1
                        self.feedback = "กล้ามแขนดีมาก!"
                        voice_alert.play(self.feedback)
                self.state = "DOWN"
            elif elbow_angle < 60:
                self.state = "UP"

        # Jumping Jack logic
        elif self.exercise_type == 'jumping_jack':
            shoulder_angle = get_angle('shoulder')
            hip_angle = get_angle('hip')
            
            if shoulder_angle > 130:
                if self.state == "IN":
                    self.count += 1
                    self.feedback = "เยี่ยมมาก จังหวะดี!"
                    voice_alert.play(self.feedback)
                self.state = "OUT"
            elif shoulder_angle < 45:
                self.state = "IN"

        # Lunge logic
        elif self.exercise_type == 'lunge':
            knee_angle = min(angles.get('left_knee', 180), angles.get('right_knee', 180))
            if knee_angle > 155:
                if self.state == "DOWN":
                    if accuracy_score > 70:
                        self.count += 1
                        self.feedback = "ลันจ์สวยมาก!"
                        voice_alert.play(self.feedback)
                self.state = "UP"
            elif knee_angle < 110:
                self.state = "DOWN"

        # Shoulder Press logic
        elif self.exercise_type == 'shoulder_press':
            elbow_angle = get_angle('elbow')
            if elbow_angle > 150:
                if self.state == "DOWN":
                    self.count += 1
                    self.feedback = "ดันไหล่ยอดเยี่ยม!"
                    voice_alert.play(self.feedback)
                self.state = "UP"
            elif elbow_angle < 85:
                self.state = "DOWN"

        # Sit Up logic
        elif self.exercise_type == 'situp':
            hip_angle = get_angle('hip')
            if hip_angle < 80:
                if self.state == "DOWN":
                    self.count += 1
                    self.feedback = "เกร็งหน้าท้องดีมาก!"
                    voice_alert.play(self.feedback)
                self.state = "UP"
            elif hip_angle > 140:
                self.state = "DOWN"

        # Fallback / General Rep Counting based on knee or elbow movement
        else:
            elbow = get_angle('elbow')
            knee = get_angle('knee')
            primary = knee if knee < 140 else elbow
            if primary > 155 and self.state == "BENT":
                self.count += 1
                self.feedback = "ทำได้ดีมาก!"
                self.state = "EXTENDED"
            elif primary < 100:
                self.state = "BENT"
                
        return self.count, self.state, self.feedback
