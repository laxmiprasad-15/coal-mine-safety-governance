from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: Dict[str, Any]

class TokenPayload(BaseModel):
    sub: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    email: str
    password: str

class UserCreate(BaseModel):
    email: str
    full_name: str
    password: str
    role_id: int
    phone: Optional[str] = None
    department: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role_id: int
    role_name: Optional[str] = None
    is_active: bool
    phone: Optional[str] = None
    department: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Role Schemas
class RoleResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    permissions: Optional[List[str]] = None

    class Config:
        from_attributes = True

# Zone Schemas
class ZoneBase(BaseModel):
    name: str
    zone_code: str
    type: str
    floor_level: Optional[str] = "Level -250m"
    risk_level: Optional[str] = "Low"
    risk_score: Optional[float] = 15.0
    map_x: Optional[float] = 0.0
    map_y: Optional[float] = 0.0
    map_width: Optional[float] = 100.0
    map_height: Optional[float] = 80.0
    description: Optional[str] = None
    is_active: Optional[bool] = True

class ZoneCreate(ZoneBase):
    mine_id: int

class ZoneResponse(ZoneBase):
    id: int
    mine_id: int
    active_cases_count: Optional[int] = 0
    worker_count: Optional[int] = 0
    sensor_count: Optional[int] = 0

    class Config:
        from_attributes = True

# Sensor & Environmental Monitoring Schemas
class SensorBase(BaseModel):
    name: str
    sensor_code: str
    type: str
    unit: str
    warning_threshold: float
    danger_threshold: float
    status: Optional[str] = "Active"
    map_x: Optional[float] = 0.0
    map_y: Optional[float] = 0.0

class SensorCreate(SensorBase):
    zone_id: int

class SensorResponse(SensorBase):
    id: int
    zone_id: int
    zone_name: Optional[str] = None
    last_reading: Optional[float] = None
    last_reading_time: Optional[datetime] = None
    is_alert: Optional[bool] = False

    class Config:
        from_attributes = True

class SensorReadingCreate(BaseModel):
    sensor_id: int
    zone_id: int
    value: float
    timestamp: Optional[datetime] = None

class SensorReadingResponse(BaseModel):
    id: int
    sensor_id: int
    zone_id: int
    value: float
    is_anomaly: bool
    anomaly_score: float
    timestamp: datetime

    class Config:
        from_attributes = True

# Worker & Health Schemas
class WorkerBase(BaseModel):
    worker_code: str
    full_name: str
    role_title: str
    zone_id: Optional[int] = None
    emergency_contact: Optional[str] = None
    blood_group: Optional[str] = "O+"
    shift: Optional[str] = "Morning Shift"
    status: Optional[str] = "On Duty"
    map_x: Optional[float] = 50.0
    map_y: Optional[float] = 50.0

class WorkerCreate(WorkerBase):
    pass

class WorkerResponse(WorkerBase):
    id: int
    zone_name: Optional[str] = None
    last_heart_rate: Optional[float] = None
    last_body_temp: Optional[float] = None
    fatigue_score: Optional[float] = None
    is_alert: Optional[bool] = False
    alert_reason: Optional[str] = None

    class Config:
        from_attributes = True

class WorkerHealthReadingCreate(BaseModel):
    worker_id: int
    heart_rate: float
    body_temp: float
    spo2: Optional[float] = 98.0
    fatigue_score: Optional[float] = 10.0
    activity_status: Optional[str] = "Active"
    shift_hours: Optional[float] = 4.0

class WorkerHealthReadingResponse(WorkerHealthReadingCreate):
    id: int
    is_alert: bool
    alert_reason: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# Equipment Schemas
class EquipmentBase(BaseModel):
    name: str
    equipment_code: str
    type: str
    status: Optional[str] = "Operational"
    health_score: Optional[float] = 90.0
    rul_days: Optional[int] = 180
    map_x: Optional[float] = 0.0
    map_y: Optional[float] = 0.0

class EquipmentCreate(EquipmentBase):
    zone_id: int

class EquipmentResponse(EquipmentBase):
    id: int
    zone_id: int
    zone_name: Optional[str] = None
    last_vibration: Optional[float] = None
    last_temp: Optional[float] = None
    last_maintenance: Optional[datetime] = None

    class Config:
        from_attributes = True

class EquipmentReadingCreate(BaseModel):
    equipment_id: int
    vibration: float
    temperature: float
    oil_pressure: Optional[float] = 4.0
    current_draw: Optional[float] = 40.0
    rpm: Optional[float] = 1450.0

class EquipmentReadingResponse(EquipmentReadingCreate):
    id: int
    is_alert: bool
    alert_reason: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# PPE Detection Schemas
class PPEDetectionResponse(BaseModel):
    id: int
    camera_id: Optional[int] = None
    zone_id: int
    zone_name: Optional[str] = None
    image_path: str
    annotated_image_path: Optional[str] = None
    detections: Optional[List[Dict[str, Any]]] = None
    violation_type: str
    confidence: float
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class PPEConfirmationRequest(BaseModel):
    confirmed: bool
    create_compliance_case: bool = True
    assigned_user_id: Optional[int] = None
    notes: Optional[str] = None

# Risk Prediction & Explainable AI Schemas
class RiskPredictionRequest(BaseModel):
    zone_id: int
    forecast_shift: Optional[str] = "Next Shift (14:00 - 22:00)"

class RiskPredictionResponse(BaseModel):
    id: Optional[int] = None
    zone_id: int
    zone_name: str
    predicted_risk: str  # Low, Medium, High, Critical
    risk_score: float
    confidence: float
    top_factors: List[Dict[str, Any]]
    xai_explanation: str
    forecast_shift: str
    timestamp: datetime

    class Config:
        from_attributes = True

# Compliance Case & Corrective Action Schemas
class ComplianceCaseCreate(BaseModel):
    title: str
    category: str  # PPE, Environmental, Equipment, Worker Health, Inspection, Operational
    source: str    # YOLOv8, Sensor Anomaly, Manual Inspection, Predictive Model
    risk_level: str
    risk_score: float
    zone_id: int
    evidence_path: Optional[str] = None
    responsible_user_id: Optional[int] = None
    deadline: datetime
    corrective_action_summary: Optional[str] = None

class ComplianceCaseUpdate(BaseModel):
    status: Optional[str] = None
    responsible_user_id: Optional[int] = None
    deadline: Optional[datetime] = None
    corrective_action_summary: Optional[str] = None
    verification_remarks: Optional[str] = None

class CorrectiveActionCreate(BaseModel):
    case_id: int
    assigned_to_user_id: int
    title: str
    description: Optional[str] = None
    due_date: datetime

class CorrectiveActionUpdate(BaseModel):
    status: Optional[str] = None  # Assigned, In Progress, Submitted for Verification, Verified, Reopened, Closed
    verification_notes: Optional[str] = None

class CorrectiveActionResponse(BaseModel):
    id: int
    case_id: int
    case_title: Optional[str] = None
    assigned_to_user_id: int
    assigned_to_name: Optional[str] = None
    title: str
    description: Optional[str] = None
    status: str
    due_date: datetime
    completed_at: Optional[datetime] = None
    verification_notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class CaseCommentCreate(BaseModel):
    comment: str

class CaseCommentResponse(BaseModel):
    id: int
    case_id: int
    user_id: int
    user_name: str
    comment: str
    created_at: datetime

    class Config:
        from_attributes = True

class ComplianceCaseResponse(BaseModel):
    id: int
    case_number: str
    title: str
    category: str
    source: str
    risk_level: str
    risk_score: float
    zone_id: int
    zone_name: Optional[str] = None
    evidence_path: Optional[str] = None
    responsible_user_id: Optional[int] = None
    responsible_user_name: Optional[str] = None
    deadline: datetime
    status: str
    corrective_action_summary: Optional[str] = None
    verification_remarks: Optional[str] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    actions_count: Optional[int] = 0

    class Config:
        from_attributes = True

# Notification & Audit Schemas
class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: str
    is_read: bool
    link_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    action: str
    entity_type: str
    entity_id: Optional[str] = None
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    ip_address: str
    tamper_token: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True

# Reports
class ReportGenerateRequest(BaseModel):
    report_type: str  # daily, weekly, ppe, environmental, equipment, audit, risk
    title: Optional[str] = None
    format: str = "pdf"  # pdf, excel
    zone_id: Optional[int] = None

class ReportResponse(BaseModel):
    id: int
    title: str
    report_type: str
    file_path: str
    file_format: str
    summary_text: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


# Contractor Management Schemas
class ContractorResponse(BaseModel):
    id: int
    name: str
    code: str
    subsidiary: str
    work_order_no: str
    category: str
    active_workers: int
    compliance_score: float
    pme_valid: bool
    vtc_trained: bool
    insurance_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Field Inspection & Mobile Reporting Schemas
class FieldInspectionCreate(BaseModel):
    zone_id: Optional[int] = 1
    latitude: Optional[float] = 23.7957
    longitude: Optional[float] = 86.4304
    location_name: str
    inspection_type: str = "Safety Observation"
    hazard_level: str = "Medium"
    observation_notes: str
    corrective_recommendation: Optional[str] = None
    photo_url: Optional[str] = None
    is_offline_synced: Optional[bool] = False

class FieldInspectionResponse(BaseModel):
    id: int
    inspector_id: Optional[int] = None
    zone_id: Optional[int] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    location_name: str
    inspection_type: str
    hazard_level: str
    observation_notes: str
    corrective_recommendation: Optional[str] = None
    photo_url: Optional[str] = None
    is_offline_synced: bool
    timestamp: datetime

    class Config:
        from_attributes = True
