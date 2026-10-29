import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from app.core.database import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)
    permissions = Column(JSON, nullable=True)  # List of allowed module permissions
    users = relationship("User", back_populates="role")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(120), unique=True, index=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    phone = Column(String(20), nullable=True)
    department = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    role = relationship("Role", back_populates="users")
    assigned_cases = relationship("ComplianceCase", foreign_keys="ComplianceCase.responsible_user_id", back_populates="responsible_user")
    corrective_actions = relationship("CorrectiveAction", back_populates="assigned_to_user")
    audit_logs = relationship("AuditLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user")

class Mine(Base):
    __tablename__ = "mines"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    code = Column(String(20), unique=True, index=True)
    location = Column(String(150), nullable=False)
    license_number = Column(String(50), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    zones = relationship("Zone", back_populates="mine")

class Zone(Base):
    __tablename__ = "zones"
    id = Column(Integer, primary_key=True, index=True)
    mine_id = Column(Integer, ForeignKey("mines.id"), nullable=False)
    name = Column(String(100), nullable=False)
    zone_code = Column(String(30), unique=True, index=True)
    type = Column(String(50), nullable=False)  # Haulage, Longwall, Continuous Miner, Ventilation, Refuge
    floor_level = Column(String(20), default="Level -250m")
    risk_level = Column(String(20), default="Low")  # Low, Medium, High, Critical
    risk_score = Column(Float, default=15.0)       # 0 - 100
    map_x = Column(Float, default=0.0)             # For 2D Digital Twin
    map_y = Column(Float, default=0.0)
    map_width = Column(Float, default=100.0)
    map_height = Column(Float, default=80.0)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    mine = relationship("Mine", back_populates="zones")
    cameras = relationship("Camera", back_populates="zone")
    sensors = relationship("Sensor", back_populates="zone")
    equipment = relationship("Equipment", back_populates="zone")
    cases = relationship("ComplianceCase", back_populates="zone")
    risk_predictions = relationship("RiskPrediction", back_populates="zone")

class Camera(Base):
    __tablename__ = "cameras"
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    name = Column(String(100), nullable=False)
    camera_code = Column(String(30), unique=True, index=True)
    stream_url = Column(String(255), nullable=True)
    status = Column(String(20), default="Online")  # Online, Offline, Warning
    resolution = Column(String(20), default="1080p")
    fps = Column(Integer, default=30)
    map_x = Column(Float, default=0.0)
    map_y = Column(Float, default=0.0)
    last_ping = Column(DateTime, default=datetime.datetime.utcnow)

    zone = relationship("Zone", back_populates="cameras")
    ppe_detections = relationship("PPEDetection", back_populates="camera")

class Sensor(Base):
    __tablename__ = "sensors"
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    name = Column(String(100), nullable=False)
    sensor_code = Column(String(30), unique=True, index=True)
    type = Column(String(30), nullable=False)  # CH4, CO, O2, TEMP, HUMIDITY, VIBRATION, AIRFLOW
    unit = Column(String(15), nullable=False)  # %, ppm, °C, mm/s, m/s
    warning_threshold = Column(Float, nullable=False)
    danger_threshold = Column(Float, nullable=False)
    status = Column(String(20), default="Active")
    map_x = Column(Float, default=0.0)
    map_y = Column(Float, default=0.0)

    zone = relationship("Zone", back_populates="sensors")
    readings = relationship("SensorReading", back_populates="sensor", cascade="all, delete-orphan")

class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id = Column(Integer, primary_key=True, index=True)
    sensor_id = Column(Integer, ForeignKey("sensors.id"), nullable=False)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    value = Column(Float, nullable=False)
    is_anomaly = Column(Boolean, default=False)
    anomaly_score = Column(Float, default=0.0)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    sensor = relationship("Sensor", back_populates="readings")

class Worker(Base):
    __tablename__ = "workers"
    id = Column(Integer, primary_key=True, index=True)
    worker_code = Column(String(30), unique=True, index=True)
    full_name = Column(String(100), nullable=False)
    role_title = Column(String(60), default="Drill Operator")
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=True)
    emergency_contact = Column(String(50), nullable=True)
    blood_group = Column(String(10), default="O+")
    shift = Column(String(20), default="Morning Shift (06:00 - 14:00)")
    status = Column(String(20), default="On Duty")  # On Duty, Break, Off Duty, Medical Alert
    map_x = Column(Float, default=50.0)
    map_y = Column(Float, default=50.0)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    health_readings = relationship("WorkerHealthReading", back_populates="worker")

class WorkerHealthReading(Base):
    __tablename__ = "worker_health_readings"
    id = Column(Integer, primary_key=True, index=True)
    worker_id = Column(Integer, ForeignKey("workers.id"), nullable=False)
    heart_rate = Column(Float, default=75.0)  # bpm
    body_temp = Column(Float, default=36.8)   # °C
    spo2 = Column(Float, default=98.0)        # %
    fatigue_score = Column(Float, default=10.0) # 0-100
    activity_status = Column(String(30), default="Active")
    shift_hours = Column(Float, default=3.5)
    is_alert = Column(Boolean, default=False)
    alert_reason = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    worker = relationship("Worker", back_populates="health_readings")

class Equipment(Base):
    __tablename__ = "equipment"
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    name = Column(String(100), nullable=False)
    equipment_code = Column(String(30), unique=True, index=True)
    type = Column(String(50), nullable=False)  # Continuous Miner, Haulage Belt, Ventilation Fan, Pump
    status = Column(String(20), default="Operational")  # Operational, Warning, Critical, Maintenance
    installation_date = Column(DateTime, nullable=True)
    last_maintenance = Column(DateTime, nullable=True)
    health_score = Column(Float, default=92.0)  # 0 - 100%
    rul_days = Column(Integer, default=180)     # Remaining Useful Life (Days)
    map_x = Column(Float, default=0.0)
    map_y = Column(Float, default=0.0)

    zone = relationship("Zone", back_populates="equipment")
    readings = relationship("EquipmentReading", back_populates="equipment")

class EquipmentReading(Base):
    __tablename__ = "equipment_readings"
    id = Column(Integer, primary_key=True, index=True)
    equipment_id = Column(Integer, ForeignKey("equipment.id"), nullable=False)
    vibration = Column(Float, default=2.1)     # mm/s
    temperature = Column(Float, default=58.0)   # °C
    oil_pressure = Column(Float, default=4.2)  # bar
    current_draw = Column(Float, default=45.0)  # Amps
    rpm = Column(Float, default=1450.0)
    is_alert = Column(Boolean, default=False)
    alert_reason = Column(String(255), nullable=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    equipment = relationship("Equipment", back_populates="readings")

class PPEDetection(Base):
    __tablename__ = "ppe_detections"
    id = Column(Integer, primary_key=True, index=True)
    camera_id = Column(Integer, ForeignKey("cameras.id"), nullable=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    image_path = Column(String(255), nullable=False)
    annotated_image_path = Column(String(255), nullable=True)
    detections_json = Column(JSON, nullable=True)  # List of detected objects with box, class, confidence
    violation_type = Column(String(100), nullable=False)  # "Missing Helmet", "Missing Safety Vest", "Compliant"
    confidence = Column(Float, default=0.88)
    status = Column(String(20), default="Pending Confirmation")  # Pending Confirmation, Confirmed, Rejected, Case Created
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    camera = relationship("Camera", back_populates="ppe_detections")

class Anomaly(Base):
    __tablename__ = "anomalies"
    id = Column(Integer, primary_key=True, index=True)
    source_type = Column(String(30), nullable=False)  # sensor, worker, equipment, ppe
    source_id = Column(Integer, nullable=False)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    severity = Column(String(20), default="Medium")  # Low, Medium, High, Critical
    metric_name = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    threshold = Column(Float, nullable=False)
    description = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

class RiskPrediction(Base):
    __tablename__ = "risk_predictions"
    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    predicted_risk = Column(String(20), nullable=False)  # Low, Medium, High, Critical
    risk_score = Column(Float, nullable=False)           # 0.0 - 100.0
    confidence = Column(Float, default=0.92)             # 0.0 - 1.0
    top_factors_json = Column(JSON, nullable=True)       # Feature importances
    xai_explanation = Column(Text, nullable=False)       # Explainable AI textual insight
    forecast_shift = Column(String(30), default="Next Shift (14:00 - 22:00)")
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    zone = relationship("Zone", back_populates="risk_predictions")

class ComplianceCase(Base):
    __tablename__ = "compliance_cases"
    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String(30), unique=True, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(50), nullable=False)  # PPE, Environmental, Equipment, Worker Health, Inspection, Operational
    source = Column(String(50), nullable=False)    # YOLOv8, Sensor Anomaly, Manual Inspection, Predictive Model
    risk_level = Column(String(20), default="Medium")  # Low, Medium, High, Critical
    risk_score = Column(Float, default=50.0)
    zone_id = Column(Integer, ForeignKey("zones.id"), nullable=False)
    evidence_path = Column(String(255), nullable=True)
    responsible_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    deadline = Column(DateTime, nullable=False)
    status = Column(String(30), default="Open")  # Open, In Progress, Pending Verification, Closed, Overdue
    corrective_action_summary = Column(Text, nullable=True)
    verification_remarks = Column(Text, nullable=True)
    closed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    zone = relationship("Zone", back_populates="cases")
    responsible_user = relationship("User", foreign_keys=[responsible_user_id], back_populates="assigned_cases")
    corrective_actions = relationship("CorrectiveAction", back_populates="case", cascade="all, delete-orphan")
    comments = relationship("CaseComment", back_populates="case", cascade="all, delete-orphan")
    attachments = relationship("Attachment", back_populates="case", cascade="all, delete-orphan")

class CorrectiveAction(Base):
    __tablename__ = "corrective_actions"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("compliance_cases.id"), nullable=False)
    assigned_to_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(30), default="Assigned")  # Assigned, In Progress, Submitted for Verification, Verified, Reopened, Closed
    due_date = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    verification_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    case = relationship("ComplianceCase", back_populates="corrective_actions")
    assigned_to_user = relationship("User", back_populates="corrective_actions")

class CaseComment(Base):
    __tablename__ = "case_comments"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("compliance_cases.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    comment = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    case = relationship("ComplianceCase", back_populates="comments")
    user = relationship("User")

class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True, index=True)
    case_id = Column(Integer, ForeignKey("compliance_cases.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=True)
    uploaded_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    case = relationship("ComplianceCase", back_populates="attachments")
    uploader = relationship("User")

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Null means broadcast to all
    title = Column(String(150), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(20), default="info")  # critical, warning, info, success
    is_read = Column(Boolean, default=False)
    link_url = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    user = relationship("User", back_populates="notifications")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)  # User, ComplianceCase, PPEDetection, Sensor, Report
    entity_id = Column(String(50), nullable=True)
    previous_state = Column(Text, nullable=True)
    new_state = Column(Text, nullable=True)
    ip_address = Column(String(50), default="127.0.0.1")
    tamper_token = Column(String(64), nullable=True)  # SHA-256 integrity hash
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_logs")

class Report(Base):
    __tablename__ = "reports"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False)  # Daily, Weekly, PPE, Environmental, Equipment, Audit, Risk Forecast
    file_path = Column(String(255), nullable=False)
    file_format = Column(String(10), default="pdf")   # pdf, excel
    generated_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    summary_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    generator = relationship("User")

