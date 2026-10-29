import csv
import io
import random
from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.models import Sensor, SensorReading, Zone, Anomaly, ComplianceCase, Notification, User
from app.schemas.schemas import SensorResponse, SensorReadingResponse, SensorReadingCreate
from app.ml.anomaly_detector import anomaly_detector
from app.services.audit_service import create_audit_log

router = APIRouter(prefix="/sensors", tags=["Sensors & Environmental Telemetry"])

@router.get("/", response_model=List[SensorResponse])
def get_all_sensors(zone_id: Optional[int] = None, db: Session = Depends(get_db)):
    query = db.query(Sensor)
    if zone_id:
        query = query.filter(Sensor.zone_id == zone_id)
    sensors = query.all()

    results = []
    for s in sensors:
        last_r = db.query(SensorReading).filter(SensorReading.sensor_id == s.id).order_by(SensorReading.timestamp.desc()).first()
        is_alert = False
        if last_r:
            if s.type in ["O2", "AIRFLOW"]:
                is_alert = (last_r.value <= s.warning_threshold)
            else:
                is_alert = (last_r.value >= s.warning_threshold)

        results.append(SensorResponse(
            id=s.id,
            zone_id=s.zone_id,
            zone_name=s.zone.name if s.zone else "Zone",
            name=s.name,
            sensor_code=s.sensor_code,
            type=s.type,
            unit=s.unit,
            warning_threshold=s.warning_threshold,
            danger_threshold=s.danger_threshold,
            status=s.status,
            map_x=s.map_x,
            map_y=s.map_y,
            last_reading=last_r.value if last_r else None,
            last_reading_time=last_r.timestamp if last_r else None,
            is_alert=is_alert
        ))
    return results

@router.get("/{sensor_id}/history", response_model=List[SensorReadingResponse])
def get_sensor_history(sensor_id: int, limit: int = 50, db: Session = Depends(get_db)):
    readings = db.query(SensorReading).filter(
        SensorReading.sensor_id == sensor_id
    ).order_by(SensorReading.timestamp.asc()).all()
    return readings[-limit:]

@router.post("/reading", response_model=SensorReadingResponse)
def add_sensor_reading(data: SensorReadingCreate, db: Session = Depends(get_db)):
    sensor = db.query(Sensor).filter(Sensor.id == data.sensor_id).first()
    if not sensor:
        raise HTTPException(status_code=404, detail="Sensor not found")

    eval_res = anomaly_detector.evaluate_reading(sensor.type, data.value)
    is_ano = eval_res["is_anomaly"]
    ano_score = eval_res["anomaly_score"]

    reading = SensorReading(
        sensor_id=sensor.id,
        zone_id=sensor.zone_id,
        value=data.value,
        is_anomaly=is_ano,
        anomaly_score=ano_score,
        timestamp=data.timestamp or datetime.utcnow()
    )
    db.add(reading)
    db.flush()

    if is_ano and eval_res["severity"] in ["High", "Critical"]:
        db.add(Anomaly(
            source_type="sensor",
            source_id=sensor.id,
            zone_id=sensor.zone_id,
            severity=eval_res["severity"],
            metric_name=f"{sensor.type} ({sensor.name})",
            value=data.value,
            threshold=eval_res["threshold"],
            description=eval_res["description"]
        ))
        
        db.add(Notification(
            title=f"{eval_res['severity'].upper()} ATMOSPHERIC ALERT: {sensor.name}",
            message=eval_res["description"],
            type="critical" if eval_res["severity"] == "Critical" else "warning",
            link_url=f"/sensors"
        ))

        existing_case = db.query(ComplianceCase).filter(
            ComplianceCase.zone_id == sensor.zone_id,
            ComplianceCase.category == "Environmental",
            ComplianceCase.status.in_(["Open", "In Progress"])
        ).first()

        if not existing_case and eval_res["severity"] == "Critical":
            safety_officer = db.query(User).filter(User.role.has(name="Safety Officer")).first()
            new_case = ComplianceCase(
                case_number=f"CASE-ENV-{int(datetime.utcnow().timestamp())}",
                title=f"Critical Gas Hazard: {sensor.name} reading {data.value}{sensor.unit}",
                category="Environmental",
                source="Sensor Anomaly",
                risk_level="Critical",
                risk_score=94.0,
                zone_id=sensor.zone_id,
                responsible_user_id=safety_officer.id if safety_officer else None,
                deadline=datetime.utcnow() + timedelta(hours=2),
                status="Open",
                corrective_action_summary="Verify auxiliary ventilation, deploy evacuation advisory if CH4 sustains above limit."
            )
            db.add(new_case)

    db.commit()
    db.refresh(reading)
    return reading

@router.post("/upload-csv")
async def upload_sensors_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = await file.read()
    decoded = content.decode('utf-8')
    reader = csv.DictReader(io.StringIO(decoded))

    zone_map = {z.zone_code: z for z in db.query(Zone).all()}
    count = 0
    anomalies_detected = 0

    for row in reader:
        zcode = row.get("zone_code")
        zone = zone_map.get(zcode)
        if not zone:
            continue

        ts_str = row.get("timestamp")
        try:
            ts = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        except Exception:
            ts = datetime.utcnow()

        if "methane_pct" in row:
            ch4_sensor = db.query(Sensor).filter(Sensor.zone_id == zone.id, Sensor.type == "CH4").first()
            if ch4_sensor:
                val = float(row["methane_pct"])
                eval_res = anomaly_detector.evaluate_reading("CH4", val)
                db.add(SensorReading(
                    sensor_id=ch4_sensor.id,
                    zone_id=zone.id,
                    value=val,
                    is_anomaly=eval_res["is_anomaly"],
                    anomaly_score=eval_res["anomaly_score"],
                    timestamp=ts
                ))
                count += 1
                if eval_res["is_anomaly"]:
                    anomalies_detected += 1

    db.commit()
    return {
        "message": f"Successfully ingested {count} readings from CSV",
        "anomalies_detected": anomalies_detected
    }

@router.post("/simulate-live-pulse")
def trigger_simulated_pulse(db: Session = Depends(get_db)):
    sensors = db.query(Sensor).all()
    created = 0
    now = datetime.utcnow()

    for s in sensors:
        base_val = 0.38 if s.type == "CH4" else 14.0 if s.type == "CO" else 20.8 if s.type == "O2" else 27.0 if s.type == "TEMP" else 67.0 if s.type == "HUMIDITY" else 2.3 if s.type == "VIBRATION" else 2.1
        noise = random.uniform(-0.05, 0.05) * base_val
        val = max(0.01, round(base_val + noise, 2))
        
        if random.random() < 0.04:
            val = round(s.warning_threshold * random.uniform(1.02, 1.18), 2)

        eval_res = anomaly_detector.evaluate_reading(s.type, val)
        db.add(SensorReading(
            sensor_id=s.id,
            zone_id=s.zone_id,
            value=val,
            is_anomaly=eval_res["is_anomaly"],
            anomaly_score=eval_res["anomaly_score"],
            timestamp=now
        ))
        created += 1

    db.commit()
    return {"message": f"Generated simulated telemetry pulse for {created} sensors."}
