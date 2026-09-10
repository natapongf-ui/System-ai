from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    age = Column(Integer)
    gender = Column(String)
    height = Column(Float) # in cm
    weight = Column(Float) # in kg
    bmi = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    histories = relationship("ExerciseHistory", back_populates="user")
    statistics = relationship("Statistics", back_populates="user")

class Exercise(Base):
    __tablename__ = "exercises"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    display_name = Column(String)
    description = Column(String)
    target_muscles = Column(String)
    difficulty = Column(String)
    image_url = Column(String)
    
    histories = relationship("ExerciseHistory", back_populates="exercise")
    reference_poses = relationship("ReferencePose", back_populates="exercise")

class ExerciseHistory(Base):
    __tablename__ = "exercise_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    date = Column(DateTime, default=datetime.utcnow)
    reps = Column(Integer)
    duration = Column(Integer) # in seconds
    calories = Column(Float)
    accuracy = Column(Float) # percentage

    user = relationship("User", back_populates="histories")
    exercise = relationship("Exercise", back_populates="histories")

class Statistics(Base):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, default=datetime.utcnow)
    total_reps = Column(Integer, default=0)
    total_calories = Column(Float, default=0.0)
    total_duration = Column(Integer, default=0)
    avg_accuracy = Column(Float, default=0.0)

    user = relationship("User", back_populates="statistics")

class ReferencePose(Base):
    __tablename__ = "reference_poses"

    id = Column(Integer, primary_key=True, index=True)
    exercise_id = Column(Integer, ForeignKey("exercises.id"))
    pose_name = Column(String) # e.g., 'start', 'end', 'front', 'side'
    json_data = Column(String) # JSON string of landmarks and angles

    exercise = relationship("Exercise", back_populates="reference_poses")
