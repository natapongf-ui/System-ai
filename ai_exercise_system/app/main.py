from fastapi import FastAPI, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
import json
import os

from app.database.database import engine, Base, get_db
from app.models import models, schemas
from app.utils.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="ระบบออกกำลังกายอัจฉริยะด้วย AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seed initial exercises if empty or missing
def seed_exercises(db: Session):
    exercises = [
        {"name": "squat", "display_name": "สควอท (Squat)", "description": "การย่อตัวลงและยืนขึ้น พัฒนากล้ามเนื้อต้นขาและสะโพก", "target_muscles": "ขา, สะโพก, ก้น", "difficulty": "ปานกลาง"},
        {"name": "pushup", "display_name": "วิดพื้น (Push Up)", "description": "การดันตัวขึ้นจากพื้น เสริมความแข็งแรงท่อนบน", "target_muscles": "หน้าอก, แขน, ไหล่", "difficulty": "ยาก"},
        {"name": "situp", "display_name": "ซิทอัพ (Sit Up)", "description": "การนอนหงายและยกลำตัวขึ้น กระชับกล้ามท้อง", "target_muscles": "หน้าท้อง, แกนกลางลำตัว", "difficulty": "ปานกลาง"},
        {"name": "plank", "display_name": "แพลงก์ (Plank)", "description": "การเกร็งลำตัวขนานกับพื้น สร้างความมั่นคงของแกนกลาง", "target_muscles": "แกนกลางลำตัว, หลัง", "difficulty": "ปานกลาง"},
        {"name": "bicep_curl", "display_name": "ยกดัมเบล (Bicep Curl)", "description": "การงอแขนยกน้ำหนัก เสริมสร้างกล้ามแขนด้านหน้า", "target_muscles": "ต้นแขนด้านหน้า", "difficulty": "ง่าย"},
        {"name": "lunge", "display_name": "ลันจ์ (Lunge)", "description": "การก้าวขาก้มตัว เสริมความแข็งแกร่งของช่วงล่างและการทรงตัว", "target_muscles": "ต้นขา, ก้น, น่อง", "difficulty": "ปานกลาง"},
        {"name": "jumping_jack", "display_name": "กระโดดตบ (Jumping Jack)", "description": "คาร์ดิโอกระตุ้นการเต้นของหัวใจและเผาผลาญไขมันทั่วร่าง", "target_muscles": "ทั้งร่างกาย, คาร์ดิโอ", "difficulty": "ง่าย"},
        {"name": "shoulder_press", "display_name": "ดันไหล่ (Shoulder Press)", "description": "การดันน้ำหนักขึ้นเหนือศีรษะ เสริมความกว้างของไหล่", "target_muscles": "หัวไหล่, แขนท่อนบน", "difficulty": "ปานกลาง"},
        {"name": "mountain_climber", "display_name": "ปีนเขา (Mountain Climber)", "description": "การดึงเข่าสลับไปข้างหน้าในท่าแพลงก์ เบิร์นไขมันระดับสูง", "target_muscles": "แกนกลางลำตัว, ขา, คาร์ดิโอ", "difficulty": "ยาก"},
        {"name": "burpee", "display_name": "เบอร์พี (Burpee)", "description": "ท่าออกกำลังกายฟูลบอดี้ ผสานสควอท วิดพื้น และกระโดด", "target_muscles": "กล้ามเนื้อทั่วร่างกาย", "difficulty": "ยาก"}
    ]
    for ex in exercises:
        existing = db.query(models.Exercise).filter(models.Exercise.name == ex["name"]).first()
        if not existing:
            db_ex = models.Exercise(**ex)
            db.add(db_ex)
        else:
            existing.display_name = ex["display_name"]
            existing.description = ex["description"]
            existing.target_muscles = ex["target_muscles"]
            existing.difficulty = ex["difficulty"]
    db.commit()

@app.on_event("startup")
def startup_event():
    db = next(get_db())
    seed_exercises(db)

@app.post("/api/register", response_model=schemas.UserResponse)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    db_email = db.query(models.User).filter(models.User.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")

    bmi = user.weight / ((user.height / 100) ** 2)
    
    hashed_password = get_password_hash(user.password)
    new_user = models.User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        age=user.age,
        gender=user.gender,
        height=user.height,
        weight=user.weight,
        bmi=bmi
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/api/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/profile", response_model=schemas.UserResponse)
def get_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.put("/api/profile", response_model=schemas.UserResponse)
def update_profile(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.age is not None:
        current_user.age = user_update.age
    if user_update.gender is not None:
        current_user.gender = user_update.gender
    if user_update.height is not None:
        current_user.height = user_update.height
    if user_update.weight is not None:
        current_user.weight = user_update.weight

    if current_user.height > 0:
        current_user.bmi = current_user.weight / ((current_user.height / 100) ** 2)

    db.commit()
    db.refresh(current_user)
    return current_user

@app.get("/api/exercises", response_model=list[schemas.ExerciseResponse])
def get_exercises(db: Session = Depends(get_db)):
    return db.query(models.Exercise).all()

@app.post("/api/history", response_model=schemas.HistoryResponse)
def create_history(history: schemas.HistoryCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    new_history = models.ExerciseHistory(
        user_id=current_user.id,
        **history.model_dump()
    )
    db.add(new_history)
    
    # Update statistics
    stat = db.query(models.Statistics).filter(models.Statistics.user_id == current_user.id).order_by(models.Statistics.date.desc()).first()
    if not stat or stat.date.date() != new_history.date.date():
        stat = models.Statistics(user_id=current_user.id)
        db.add(stat)
        db.commit()
        db.refresh(stat)
        
    stat.total_reps += history.reps
    stat.total_calories += history.calories
    stat.total_duration += history.duration
    
    # Simple moving average for accuracy
    if stat.total_reps > 0:
        stat.avg_accuracy = ((stat.avg_accuracy * (stat.total_reps - history.reps)) + (history.accuracy * history.reps)) / stat.total_reps
    else:
        stat.avg_accuracy = history.accuracy
        
    db.commit()
    db.refresh(new_history)
    
    # Get exercise name for response
    ex = db.query(models.Exercise).filter(models.Exercise.id == history.exercise_id).first()
    
    response_data = schemas.HistoryResponse.model_validate(new_history)
    response_data.exercise_name = ex.display_name if ex else None
    
    return response_data

@app.get("/api/history", response_model=list[schemas.HistoryResponse])
def get_history(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    histories = db.query(models.ExerciseHistory).filter(models.ExerciseHistory.user_id == current_user.id).order_by(models.ExerciseHistory.date.desc()).all()
    
    result = []
    for h in histories:
        ex = db.query(models.Exercise).filter(models.Exercise.id == h.exercise_id).first()
        h_resp = schemas.HistoryResponse.model_validate(h)
        h_resp.exercise_name = ex.display_name if ex else None
        result.append(h_resp)
        
    return result

@app.delete("/api/history/{history_id}")
def delete_history(history_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = db.query(models.ExerciseHistory).filter(
        models.ExerciseHistory.id == history_id,
        models.ExerciseHistory.user_id == current_user.id
    ).first()
    if not record:
        raise HTTPException(status_code=404, detail="History record not found")
    db.delete(record)
    db.commit()
    return {"message": "Record deleted successfully"}

@app.get("/api/statistics", response_model=list[schemas.StatisticsResponse])
def get_statistics(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(models.Statistics).filter(models.Statistics.user_id == current_user.id).order_by(models.Statistics.date.asc()).all()

@app.get("/api/leaderboard", response_model=list[schemas.LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    leaderboard = []
    for u in users:
        histories = db.query(models.ExerciseHistory).filter(models.ExerciseHistory.user_id == u.id).all()
        total_reps = sum(h.reps for h in histories)
        total_cals = sum(h.calories for h in histories)
        total_workouts = len(histories)
        avg_acc = (sum(h.accuracy for h in histories) / total_workouts) if total_workouts > 0 else 0.0
        leaderboard.append({
            "username": u.username,
            "full_name": u.full_name,
            "total_reps": total_reps,
            "total_calories": round(total_cals, 1),
            "total_workouts": total_workouts,
            "avg_accuracy": round(avg_acc, 1)
        })
    
    # Sort by total reps descending
    leaderboard.sort(key=lambda x: x["total_reps"], reverse=True)
    for idx, entry in enumerate(leaderboard):
        entry["rank"] = idx + 1
        
    return leaderboard

@app.get("/api/achievements")
def get_achievements(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    histories = db.query(models.ExerciseHistory).filter(models.ExerciseHistory.user_id == current_user.id).all()
    total_reps = sum(h.reps for h in histories)
    total_cals = sum(h.calories for h in histories)
    total_workouts = len(histories)
    best_acc = max((h.accuracy for h in histories), default=0.0)
    
    badges = [
        {
            "id": "first_workout",
            "title": "🥇 First Step",
            "description": "สำเร็จการออกกำลังกายครั้งแรก",
            "unlocked": total_workouts >= 1,
            "progress": min(total_workouts, 1),
            "target": 1
        },
        {
            "id": "reps_50",
            "title": "⚡ 50 Reps Warrior",
            "description": "สะสมจำนวนครั้งครบ 50 ครั้ง",
            "unlocked": total_reps >= 50,
            "progress": min(total_reps, 50),
            "target": 50
        },
        {
            "id": "reps_100",
            "title": "💯 Century Club",
            "description": "สะสมจำนวนครั้งครบ 100 ครั้ง",
            "unlocked": total_reps >= 100,
            "progress": min(total_reps, 100),
            "target": 100
        },
        {
            "id": "cal_100",
            "title": "🔥 Calorie Crusher",
            "description": "เผาผลาญพลังงานสะสม 100 kcal",
            "unlocked": total_cals >= 100,
            "progress": int(min(total_cals, 100)),
            "target": 100
        },
        {
            "id": "perfect_form",
            "title": "🎯 Form Perfectionist",
            "description": "ทำความแม่นยำสูงกว่า 90%",
            "unlocked": best_acc >= 90.0,
            "progress": int(min(best_acc, 90)),
            "target": 90
        }
    ]
    return badges

@app.get("/api/reference/{exercise_name}")
def get_reference_pose(exercise_name: str):
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    base_path = os.path.join(project_root, "reference_pose", exercise_name)
    if not os.path.exists(base_path):
        return {"error": "Reference pose not found"}
        
    poses = {}
    for filename in os.listdir(base_path):
        if filename.endswith(".json"):
            pose_name = filename.split(".")[0]
            with open(os.path.join(base_path, filename), "r", encoding="utf-8") as f:
                poses[pose_name] = json.load(f)
                
    return poses
