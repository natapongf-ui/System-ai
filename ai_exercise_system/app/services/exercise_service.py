from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from app.models import models

class ExerciseService:
    """Service layer for exercise-related business logic"""
    
    @staticmethod
    def calculate_calories(exercise_name: str, reps: int, duration: int, weight: float) -> float:
        """
        Calculate estimated calories burned based on exercise type, reps, duration, and user weight.
        Uses MET (Metabolic Equivalent of Task) values.
        """
        met_values = {
            'squat': 5.0,
            'pushup': 8.0,
            'situp': 4.0,
            'plank': 4.0,
            'lunge': 5.5,
            'jumping_jack': 8.0,
            'bicep_curl': 3.5,
            'shoulder_press': 4.0,
            'mountain_climber': 8.0,
            'burpee': 10.0,
        }
        
        met = met_values.get(exercise_name, 5.0)
        duration_hours = duration / 3600
        calories = met * weight * duration_hours
        return round(calories, 2)
    
    @staticmethod
    def get_weekly_stats(db: Session, user_id: int):
        """Get statistics for the last 7 days"""
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        return db.query(models.Statistics).filter(
            models.Statistics.user_id == user_id,
            models.Statistics.date >= seven_days_ago
        ).order_by(models.Statistics.date.asc()).all()
    
    @staticmethod
    def get_monthly_stats(db: Session, user_id: int):
        """Get statistics for the last 30 days"""
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        return db.query(models.Statistics).filter(
            models.Statistics.user_id == user_id,
            models.Statistics.date >= thirty_days_ago
        ).order_by(models.Statistics.date.asc()).all()
