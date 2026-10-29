import os
from typing import List

class Settings:
    PROJECT_NAME: str = "AI-Driven Digital Twin & Predictive Compliance Management System for Coal Mine Safety Governance"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-coal-mine-safety-jwt-key-btech-cse-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./coal_mine_safety.db")
    
    # Upload and static directories
    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    UPLOAD_DIR: str = os.path.join(BASE_DIR, "uploads")
    PPE_UPLOAD_DIR: str = os.path.join(UPLOAD_DIR, "ppe")
    REPORTS_DIR: str = os.path.join(UPLOAD_DIR, "reports")
    MODELS_DIR: str = os.path.join(BASE_DIR, "models")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "*"
    ]

    # Mining Safety Standard Thresholds (DGMS guidelines)
    CH4_WARNING_PCT: float = 0.75     # Methane Warning threshold (%)
    CH4_DANGER_PCT: float = 1.25      # Methane Evacuation/Critical threshold (%)
    CO_WARNING_PPM: float = 25.0      # Carbon Monoxide Warning (PPM)
    CO_DANGER_PPM: float = 50.0       # Carbon Monoxide Danger (PPM)
    O2_MIN_PCT: float = 19.5          # Minimum safe Oxygen level (%)
    AIRFLOW_MIN_MS: float = 0.5       # Minimum safe ventilation velocity (m/s)
    TEMP_MAX_C: float = 33.0          # Max acceptable wet/dry bulb temperature (°C)
    HUMIDITY_MAX_PCT: float = 85.0    # High humidity heat-stress threshold (%)
    VIBRATION_MAX_MMS: float = 7.5    # Machinery vibration limit (mm/s)

settings = Settings()

# Ensure directories exist
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.PPE_UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.REPORTS_DIR, exist_ok=True)
os.makedirs(settings.MODELS_DIR, exist_ok=True)
