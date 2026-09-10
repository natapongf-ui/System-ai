from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# User Schemas
class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    age: int
    gender: str
    height: float
    weight: float

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    height: Optional[float] = None
    weight: Optional[float] = None

class UserResponse(UserBase):
    id: int
    bmi: float
    created_at: datetime

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Exercise Schemas
class ExerciseBase(BaseModel):
    name: str
    display_name: str
    description: str
    target_muscles: str
    difficulty: str
    image_url: Optional[str] = None

class ExerciseResponse(ExerciseBase):
    id: int

    class Config:
        from_attributes = True

# History Schemas
class HistoryCreate(BaseModel):
    exercise_id: int
    reps: int
    duration: int
    calories: float
    accuracy: float

class HistoryResponse(HistoryCreate):
    id: int
    user_id: int
    date: datetime
    exercise_name: Optional[str] = None

    class Config:
        from_attributes = True

# Statistics Schemas
class StatisticsResponse(BaseModel):
    date: datetime
    total_reps: int
    total_calories: float
    total_duration: int
    avg_accuracy: float

    class Config:
        from_attributes = True

# Leaderboard Schema
class LeaderboardEntry(BaseModel):
    rank: int
    username: str
    full_name: str
    total_reps: int
    total_calories: float
    total_workouts: int
    avg_accuracy: float
