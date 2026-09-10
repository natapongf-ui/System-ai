import logging
import os
from datetime import datetime

def setup_logger(name: str) -> logging.Logger:
    """Setup a logger with file and console handlers"""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Create logs directory if not exists
    os.makedirs('logs', exist_ok=True)
    
    # File handler
    fh = logging.FileHandler(f'logs/{name}.log')
    fh.setLevel(logging.DEBUG)
    
    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    
    logger.addHandler(fh)
    logger.addHandler(ch)
    
    return logger

def calculate_bmi(weight: float, height: float) -> float:
    """Calculate BMI from weight (kg) and height (cm)"""
    if height <= 0:
        return 0.0
    return round(weight / ((height / 100) ** 2), 2)

def bmi_category(bmi: float) -> str:
    """Return BMI category in Thai"""
    if bmi < 18.5:
        return "น้ำหนักน้อย"
    elif bmi < 25.0:
        return "น้ำหนักปกติ"
    elif bmi < 30.0:
        return "น้ำหนักเกิน"
    else:
        return "โรคอ้วน"

def format_duration(seconds: int) -> str:
    """Format duration in seconds to human readable string"""
    minutes = seconds // 60
    secs = seconds % 60
    if minutes > 0:
        return f"{minutes} นาที {secs} วินาที"
    return f"{secs} วินาที"
