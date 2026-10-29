import os
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.models import (
    Role, User, Mine, Zone, Camera, Sensor, SensorReading,
    Worker, WorkerHealthReading, Equipment, EquipmentReading,
    PPEDetection, Anomaly, RiskPrediction, ComplianceCase,
    CorrectiveAction, CaseComment, Notification, AuditLog, Report
)
from app.services.report_service import generate_pdf_report
from app.ml.xai_explainer import xai_explainer

def seed_database(db: Session):
    # Check if already seeded
    if db.query(Role).first():
        print("[Seed] Database already has records, checking completeness...")
        return

    print("[Seed] Seeding Coal Mine Safety Governance database...")

    # 1. Seed Roles
    roles_data = [
        ("Admin", "Full administrative access to governance system, user management, and compliance logs", ["all"]),
        ("Safety Officer", "Manage PPE violations, atmospheric anomalies, assign corrective actions, approve cases", ["cases:read", "cases:write", "ppe:read", "ppe:write", "sensors:read", "risk:read", "actions:write"]),
        ("Mine Supervisor", "Zone oversight, worker health management, execute assigned corrective actions", ["cases:read", "actions:read", "actions:write", "workers:read", "equipment:read", "sensors:read"]),
        ("Worker", "View safety alerts, submit field observations, check wearable vitals", ["workers:read", "sensors:read", "ppe:read"]),
        ("Auditor", "Independent inspection, regulatory audit report review, immutable audit trail verification", ["audit:read", "reports:read", "cases:read", "reports:write"])
    ]
    role_objs = {}
    for name, desc, perms in roles_data:
        r = Role(name=name, description=desc, permissions=perms)
        db.add(r)
        db.flush()
        role_objs[name] = r

    # 2. Seed Users
    users_data = [
        ("admin@coalmine.gov", "Dr. Rajesh Sharma", "Admin", "+91 98765 43210", "Safety Directorate"),
        ("safety@coalmine.gov", "Vikram Rathore", "Safety Officer", "+91 98765 43211", "DGMS Mine Safety"),
        ("supervisor@coalmine.gov", "Arun Mukherjee", "Mine Supervisor", "+91 98765 43212", "Extraction Shift A"),
        ("worker@coalmine.gov", "Ramesh Yadav", "Worker", "+91 98765 43213", "Underground Haulage"),
        ("auditor@coalmine.gov", "Sanjay Deshmukh", "Auditor", "+91 98765 43214", "Central Statutory Bureau")
    ]
    user_objs = {}
    for email, name, role_name, phone, dept in users_data:
        u = User(
            email=email,
            full_name=name,
            hashed_password=get_password_hash("Admin@123" if role_name == "Admin" else f"{role_name.split()[0]}@123"),
            role_id=role_objs[role_name].id,
            phone=phone,
            department=dept
        )
        db.add(u)
        db.flush()
        user_objs[email] = u

    # 3. Seed Mine
    mine = Mine(
        name="Dhanbad Colliery No. 7 (Underground)",
        code="BCCL-DHN-07",
        location="Jharia Coalfields, Jharkhand, India",
        license_number="DGMS-UG-JH-2024-884"
    )
    db.add(mine)
    db.flush()

    # 4. Seed 8 Mine Zones (with coordinates for 2D Digital Twin Map)
    zones_raw = [
        ("Main Adit & Entry Portal", "ZN-01", "Entry/Exit", 40, 20, 160, 90, "Primary surface intake drift and man-riding portal", "Low", 12.0),
        ("Main Haulage Conveyor Drift", "ZN-02", "Conveyor Belt Area", 240, 20, 220, 90, "Central coal clearance belt conveyor corridor", "Medium", 42.0),
        ("Working Face A (Longwall Panel)", "ZN-03", "Working Face A", 500, 20, 260, 110, "Continuous shearer cutting seam III, depth 280m", "High", 74.0),
        ("Working Face B (Continuous Miner)", "ZN-04", "Working Face B", 500, 160, 260, 110, "Board and pillar panel with Joy continuous miner", "Critical", 92.0),
        ("Main Ventilation Fan & Shaft", "ZN-05", "Ventilation Zone", 240, 160, 220, 90, "Exhaust upcast shaft with twin axial fans", "Low", 18.0),
        ("Heavy Machinery Substation", "ZN-06", "Equipment Room", 40, 160, 160, 90, "Flameproof transformers and main power switchgear", "Medium", 38.0),
        ("Emergency Refuge & Assembly Chamber", "ZN-07", "Emergency Assembly Point", 140, 280, 240, 90, "Hermetically sealed shelter with 48h oxygen life support", "Low", 8.0),
        ("Return Airway & Bleeder Tunnel", "ZN-08", "Ventilation Zone", 420, 280, 260, 90, "Gas drainage bleeder drift returning to surface exhaust", "High", 78.0)
    ]
    zone_objs = []
    for name, code, ztype, x, y, w, h, desc, r_lvl, r_scr in zones_raw:
        z = Zone(
            mine_id=mine.id,
            name=name,
            zone_code=code,
            type=ztype,
            floor_level="Level -260m",
            risk_level=r_lvl,
            risk_score=r_scr,
            map_x=x,
            map_y=y,
            map_width=w,
            map_height=h,
            description=desc
        )
        db.add(z)
        db.flush()
        zone_objs.append(z)

    # 5. Seed 10 CCTV Cameras
    cameras_data = [
        ("CAM-01: Entry Portal Portal", "CAM-01", zone_objs[0].id, 80, 50),
        ("CAM-02: Shaft Bottom Drift", "CAM-02", zone_objs[0].id, 150, 60),
        ("CAM-03: Conveyor Transfer Point 1", "CAM-03", zone_objs[1].id, 280, 50),
        ("CAM-04: Conveyor Drive Station", "CAM-04", zone_objs[1].id, 400, 55),
        ("CAM-05: Shearer Canopy Camera", "CAM-05", zone_objs[2].id, 560, 60),
        ("CAM-06: Face A Roof Support Line", "CAM-06", zone_objs[2].id, 680, 65),
        ("CAM-07: Continuous Miner Cutting Head", "CAM-07", zone_objs[3].id, 560, 200),
        ("CAM-08: Shuttle Car Haul Route", "CAM-08", zone_objs[3].id, 680, 210),
        ("CAM-09: Exhaust Fan Plenum", "CAM-09", zone_objs[4].id, 320, 200),
        ("CAM-10: Substation Flameproof Area", "CAM-10", zone_objs[5].id, 100, 200)
    ]
    camera_objs = []
    for name, code, zid, cx, cy in cameras_data:
        c = Camera(
            zone_id=zid,
            name=name,
            camera_code=code,
            stream_url=f"/streams/{code.lower()}.m3u8",
            status="Online",
            map_x=cx,
            map_y=cy
        )
        db.add(c)
        db.flush()
        camera_objs.append(c)

    # 6. Seed 16 Multi-Gas & Environmental IoT Sensors
    sensor_configs = [
        ("Methane Optical Sensor 1", "SEN-CH4-01", "CH4", "%", 0.75, 1.25, zone_objs[2].id, 530, 40),
        ("Methane Optical Sensor 2", "SEN-CH4-02", "CH4", "%", 0.75, 1.25, zone_objs[3].id, 530, 180),
        ("Methane Bleeder Sensor", "SEN-CH4-03", "CH4", "%", 0.75, 1.25, zone_objs[7].id, 450, 300),
        ("Carbon Monoxide Sensor 1", "SEN-CO-01", "CO", "ppm", 25.0, 50.0, zone_objs[1].id, 300, 40),
        ("Carbon Monoxide Sensor 2", "SEN-CO-02", "CO", "ppm", 25.0, 50.0, zone_objs[3].id, 610, 190),
        ("Oxygen Deficiency Monitor 1", "SEN-O2-01", "O2", "%", 19.5, 18.0, zone_objs[0].id, 100, 35),
        ("Oxygen Deficiency Monitor 2", "SEN-O2-02", "O2", "%", 19.5, 18.0, zone_objs[6].id, 180, 300),
        ("Dry Bulb Temp Sensor", "SEN-TMP-01", "TEMP", "°C", 33.0, 38.0, zone_objs[2].id, 630, 45),
        ("Substation Thermal Sensor", "SEN-TMP-02", "TEMP", "°C", 40.0, 55.0, zone_objs[5].id, 70, 180),
        ("Relative Humidity Gauge", "SEN-HUM-01", "HUMIDITY", "%", 85.0, 95.0, zone_objs[2].id, 690, 45),
        ("Conveyor Drive Vibration Sensor", "SEN-VIB-01", "VIBRATION", "mm/s", 7.5, 12.0, zone_objs[1].id, 410, 40),
        ("Main Fan Vibration Sensor", "SEN-VIB-02", "VIBRATION", "mm/s", 6.0, 10.0, zone_objs[4].id, 350, 185),
        ("Shearer Motor Vibration Sensor", "SEN-VIB-03", "VIBRATION", "mm/s", 8.0, 14.0, zone_objs[2].id, 590, 40),
        ("Anemometer Air Velocity Sensor 1", "SEN-AIR-01", "AIRFLOW", "m/s", 0.5, 0.3, zone_objs[0].id, 120, 40),
        ("Face A Anemometer", "SEN-AIR-02", "AIRFLOW", "m/s", 0.5, 0.3, zone_objs[2].id, 510, 50),
        ("Return Drift Anemometer", "SEN-AIR-03", "AIRFLOW", "m/s", 0.5, 0.3, zone_objs[7].id, 520, 310)
    ]
    sensor_objs = []
    for sname, scode, stype, unit, w_th, d_th, zid, sx, sy in sensor_configs:
        s = Sensor(
            zone_id=zid,
            name=sname,
            sensor_code=scode,
            type=stype,
            unit=unit,
            warning_threshold=w_th,
            danger_threshold=d_th,
            status="Active",
            map_x=sx,
            map_y=sy
        )
        db.add(s)
        db.flush()
        sensor_objs.append(s)

    # 7. Seed 550+ Historical & Live Sensor Readings
    now = datetime.utcnow()
    for s in sensor_objs:
        base_val = 0.35 if s.type == "CH4" else 12.0 if s.type == "CO" else 20.8 if s.type == "O2" else 26.5 if s.type == "TEMP" else 68.0 if s.type == "HUMIDITY" else 2.4 if s.type == "VIBRATION" else 2.1
        # Generate 35 chronological records per sensor
        for i in range(35):
            t = now - timedelta(minutes=(35 - i) * 15)
            # Add spike in Working Face B (zone_objs[3]) for CH4/CO
            val = base_val + random.uniform(-0.08, 0.08) * base_val
            if s.zone_id == zone_objs[3].id and s.type in ["CH4", "CO"] and i >= 28:
                val = s.danger_threshold * random.uniform(1.05, 1.35)
            elif s.zone_id == zone_objs[1].id and s.type == "VIBRATION" and i >= 30:
                val = s.warning_threshold * random.uniform(1.02, 1.15)
            
            is_ano = val >= s.warning_threshold if s.type != "O2" and s.type != "AIRFLOW" else val <= s.warning_threshold
            db.add(SensorReading(
                sensor_id=s.id,
                zone_id=s.zone_id,
                value=round(val, 2),
                is_anomaly=is_ano,
                anomaly_score=0.92 if is_ano else 0.08,
                timestamp=t
            ))

    # 8. Seed 20 Underground Workers & Wearable Health Vitals
    worker_names = [
        "Ramesh Yadav", "Sunil Soren", "Prakash Murmu", "Ajay Kumar Singh",
        "Deepak Soren", "Anil Mahato", "Manoj Karmakar", "Sanjay Hansda",
        "Santosh Bauri", "Rajesh Besra", "Pradeep Marandi", "Dinesh Tudu",
        "Suraj Hembrom", "Kishore Kisku", "Vikash Munda", "Pankaj Gope",
        "Bijoy Mahali", "Gopal Gorai", "Subhash Mandal", "Mahesh Das"
    ]
    worker_roles = ["Longwall Operator", "Continuous Miner Pilot", "Belt Splicer & Mechanic", "Ventilation Officer", "Blasting Technician", "Electrical Fitter"]
    
    worker_objs = []
    for idx, wname in enumerate(worker_names):
        assigned_zone = zone_objs[idx % len(zone_objs)]
        w = Worker(
            worker_code=f"WKR-{100 + idx}",
            full_name=wname,
            role_title=random.choice(worker_roles),
            zone_id=assigned_zone.id,
            emergency_contact=f"+91 97711 {random.randint(10000, 99999)}",
            blood_group=random.choice(["O+", "A+", "B+", "AB+"]),
            shift="Morning Shift (06:00 - 14:00)",
            status="Medical Alert" if idx == 3 else "Break" if idx == 7 else "On Duty",
            map_x=assigned_zone.map_x + random.uniform(20, assigned_zone.map_width - 20),
            map_y=assigned_zone.map_y + random.uniform(20, assigned_zone.map_height - 20)
        )
        db.add(w)
        db.flush()
        worker_objs.append(w)

        # Worker health readings
        is_stressed = (idx == 3)  # Ajay Kumar Singh experiencing tachycardia/heat stress
        db.add(WorkerHealthReading(
            worker_id=w.id,
            heart_rate=128.0 if is_stressed else random.uniform(68, 88),
            body_temp=38.6 if is_stressed else random.uniform(36.5, 37.2),
            spo2=94.0 if is_stressed else random.uniform(97.0, 99.5),
            fatigue_score=82.0 if is_stressed else random.uniform(12.0, 35.0),
            activity_status="High Exertion" if is_stressed else "Normal Workload",
            shift_hours=6.5 if is_stressed else 4.0,
            is_alert=is_stressed,
            alert_reason="Tachycardia (128 bpm) and Elevated Core Body Temp (38.6°C)" if is_stressed else None,
            timestamp=now - timedelta(minutes=5)
        ))

    # 9. Seed 8 Industrial Mining Equipment Items & Readings
    equip_configs = [
        ("Longwall Shearer Joy 7LS", "EQ-SHR-01", "Continuous Miner", zone_objs[2].id, 92.0, 190, 580, 50),
        ("Continuous Miner Joy 12CM12", "EQ-CM-02", "Continuous Miner", zone_objs[3].id, 64.0, 45, 590, 190),
        ("Main Trunk Haulage Belt 1200mm", "EQ-BLT-01", "Haulage Belt", zone_objs[1].id, 76.0, 80, 310, 50),
        ("Gathering Face Conveyor (AFC)", "EQ-BLT-02", "Haulage Belt", zone_objs[2].id, 88.0, 140, 650, 55),
        ("Main Surface Axial Exhaust Fan 1", "EQ-FAN-01", "Ventilation Fan", zone_objs[4].id, 96.0, 310, 300, 190),
        ("Auxiliary Booster Fan Unit 3", "EQ-FAN-02", "Ventilation Fan", zone_objs[7].id, 82.0, 120, 500, 300),
        ("Underground Substation Transformer 3.3kV", "EQ-SUB-01", "Substation", zone_objs[5].id, 89.0, 240, 80, 190),
        ("Emergency Refuge Chamber Air Purifier", "EQ-REF-01", "Life Support", zone_objs[6].id, 99.0, 480, 190, 310)
    ]
    for ename, ecode, etype, zid, h_scr, rul, ex, ey in equip_configs:
        eq = Equipment(
            zone_id=zid,
            name=ename,
            equipment_code=ecode,
            type=etype,
            status="Operational" if h_scr > 70 else "Warning",
            health_score=h_scr,
            rul_days=rul,
            last_maintenance=now - timedelta(days=random.randint(10, 60)),
            map_x=ex,
            map_y=ey
        )
        db.add(eq)
        db.flush()
        db.add(EquipmentReading(
            equipment_id=eq.id,
            vibration=8.2 if h_scr < 70 else 2.5,
            temperature=68.0 if h_scr < 70 else 46.0,
            oil_pressure=3.1 if h_scr < 70 else 4.4,
            current_draw=54.0 if h_scr < 70 else 38.0,
            rpm=1480.0,
            is_alert=(h_scr < 70),
            alert_reason="High drive bearing temperature & abnormal vibration harmonics" if h_scr < 70 else None,
            timestamp=now - timedelta(minutes=10)
        ))

    # 10. Seed 55+ PPE Detections
    ppe_violations_types = [
        ("Missing Hardhat / Helmet", 0.94),
        ("Missing High-Visibility Safety Vest", 0.91),
        ("Missing Gloves in Cutter Zone", 0.89),
        ("Missing Protective Safety Goggles", 0.92),
        ("Compliant (All Mandatory PPE Present)", 0.96)
    ]
    for i in range(55):
        v_type, conf = random.choice(ppe_violations_types)
        c = random.choice(camera_objs)
        is_compliant = "Compliant" in v_type
        status = "Confirmed" if (i % 3 == 0) else "Case Created" if (not is_compliant and i % 2 == 0) else "Pending Confirmation"
        
        db.add(PPEDetection(
            camera_id=c.id,
            zone_id=c.zone_id,
            image_path="/uploads/ppe/demo_worker_frame.jpg",
            annotated_image_path="/uploads/ppe/demo_worker_frame_annotated.jpg",
            detections_json=[
                {"class": "Worker", "box": [120, 40, 480, 580], "confidence": 0.98},
                {"class": "NO-Hardhat" if "Hardhat" in v_type else "Hardhat", "box": [220, 50, 380, 160], "confidence": conf},
                {"class": "NO-Safety Vest" if "Vest" in v_type else "Safety Vest", "box": [180, 170, 420, 390], "confidence": conf}
            ],
            violation_type=v_type,
            confidence=conf,
            status=status,
            created_at=now - timedelta(hours=random.uniform(0.5, 48.0))
        ))

    # 11. Seed 32 Traceable Compliance Cases across all Categories and Lifecycle Statuses
    cases_raw = [
        ("CASE-2026-001", "Critical Methane Spike Exceeding DGMS Safe Limit (1.42%)", "Environmental", "Sensor Anomaly", "Critical", 94.0, zone_objs[3].id, "Open", 2),
        ("CASE-2026-002", "Unsafe Longwall Face Entry Without Protective Hardhat", "PPE", "YOLOv8", "High", 72.0, zone_objs[2].id, "In Progress", 6),
        ("CASE-2026-003", "Conveyor Belt Drive Bearing Excessive Thermal Vibration", "Equipment", "Sensor Anomaly", "High", 68.0, zone_objs[1].id, "Pending Verification", 12),
        ("CASE-2026-004", "Crew Heat Stress & Elevated Heart Rate (128 bpm)", "Worker Health", "Sensor Anomaly", "Critical", 88.0, zone_objs[3].id, "In Progress", 3),
        ("CASE-2026-005", "Bleeder Airway Dust Accumulation & Low Air Velocity", "Environmental", "Predictive Model", "Medium", 46.0, zone_objs[7].id, "Open", 24),
        ("CASE-2026-006", "Failure to Wear High-Vis Vest in Shuttler Haulway", "PPE", "YOLOv8", "Medium", 42.0, zone_objs[3].id, "Closed", 48),
        ("CASE-2026-007", "Overdue Flameproof Inspection on Substation Switchgear", "Inspection", "Manual Inspection", "High", 70.0, zone_objs[5].id, "Overdue", -5),
        ("CASE-2026-008", "Continuous Miner Cutting Head Vibration Exceeding 8.2 mm/s", "Equipment", "Predictive Model", "Critical", 91.0, zone_objs[3].id, "Open", 4),
        ("CASE-2026-009", "Worker Shift Duration Exceeded Statutory 8h Limit", "Operational", "Manual Inspection", "Medium", 35.0, zone_objs[0].id, "Closed", 72),
        ("CASE-2026-010", "Missing Ear Protection in Axial Fan Plenum Room", "PPE", "YOLOv8", "Low", 22.0, zone_objs[4].id, "Closed", 96)
    ]
    
    # Expand to 32 cases
    case_objs = []
    responsible_u = user_objs["safety@coalmine.gov"]

    for i in range(32):
        if i < len(cases_raw):
            cnum, title, cat, src, r_lvl, r_scr, zid, stat, hrs_left = cases_raw[i]
        else:
            cat = random.choice(["PPE", "Environmental", "Equipment", "Worker Health", "Inspection", "Operational"])
            src = random.choice(["YOLOv8", "Sensor Anomaly", "Manual Inspection", "Predictive Model"])
            r_lvl = random.choice(["Low", "Medium", "High", "Critical"])
            r_scr = 85.0 if r_lvl == "Critical" else 65.0 if r_lvl == "High" else 40.0 if r_lvl == "Medium" else 18.0
            zid = random.choice(zone_objs).id
            stat = random.choice(["Open", "In Progress", "Pending Verification", "Closed"])
            hrs_left = random.randint(4, 72)
            cnum = f"CASE-2026-{100 + i}"
            title = f"{r_lvl} {cat} Non-Compliance Event at {cnum}"

        case_deadline = now + timedelta(hours=hrs_left)
        cc = ComplianceCase(
            case_number=cnum,
            title=title,
            category=cat,
            source=src,
            risk_level=r_lvl,
            risk_score=r_scr,
            zone_id=zid,
            evidence_path="/uploads/ppe/demo_worker_frame_annotated.jpg",
            responsible_user_id=responsible_u.id,
            deadline=case_deadline,
            status=stat,
            corrective_action_summary="Deploy ventilation team, inspect gas bleeders, and enforce PPE adherence.",
            verification_remarks="Atmospheric readings restored to 0.42% CH4; PPE compliance visually verified." if stat == "Closed" else None,
            closed_at=now - timedelta(hours=2) if stat == "Closed" else None,
            created_at=now - timedelta(hours=random.uniform(2, 72))
        )
        db.add(cc)
        db.flush()
        case_objs.append(cc)

    # 12. Seed 20 Corrective Actions
    supervisor_u = user_objs["supervisor@coalmine.gov"]
    for i in range(20):
        target_case = case_objs[i % len(case_objs)]
        act_stat = "Closed" if target_case.status == "Closed" else "Submitted for Verification" if (i % 3 == 0) else "In Progress" if (i % 2 == 0) else "Assigned"
        db.add(CorrectiveAction(
            case_id=target_case.id,
            assigned_to_user_id=supervisor_u.id,
            title=f"Action Step for {target_case.case_number}: On-site Remediation",
            description=f"Inspect zone {target_case.zone_id}, verify sensor calibration, enforce PPE protocol, and log resolution in DGMS compliance register.",
            status=act_stat,
            due_date=target_case.deadline,
            completed_at=now - timedelta(hours=1) if act_stat in ["Closed", "Submitted for Verification"] else None,
            verification_notes="Remediation steps completed on site according to standard operating safety procedure." if act_stat in ["Closed", "Submitted for Verification"] else None
        ))

    # 13. Seed Risk Predictions & XAI Explanations for all 8 zones
    for z in zone_objs:
        pred_dict = {
            "predicted_risk": z.risk_level,
            "risk_score": z.risk_score,
            "confidence": 0.94 if z.risk_level == "Critical" else 0.89,
            "top_factors": [
                {"feature": "methane_pct", "label": "Methane (CH4)", "value": 1.42 if z.risk_level == "Critical" else 0.45, "contribution_score": 38.5},
                {"feature": "ppe_violations_24h", "label": "PPE Violations (24h)", "value": 3 if z.risk_level in ["High", "Critical"] else 0, "contribution_score": 24.2},
                {"feature": "vibration_mms", "label": "Machinery Vibration", "value": 8.1 if z.risk_level in ["High", "Critical"] else 2.1, "contribution_score": 18.0}
            ]
        }
        xai_text = xai_explainer.generate_explanation(pred_dict, z.name)
        db.add(RiskPrediction(
            zone_id=z.id,
            predicted_risk=z.risk_level,
            risk_score=z.risk_score,
            confidence=0.92,
            top_factors_json=pred_dict["top_factors"],
            xai_explanation=xai_text,
            forecast_shift="Next Shift (14:00 - 22:00)",
            timestamp=now
        ))

    # 14. Seed In-App Notifications
    notifs_raw = [
        ("CRITICAL ATMOSPHERIC ALERT", "Working Face B: Methane concentration reached 1.42% (DGMS Evacuation Level). Immediate action required.", "critical", "/digital-twin"),
        ("PPE VIOLATION DETECTED", "Camera CAM-05 detected worker without hardhat at Longwall Face A.", "warning", "/ppe-detection"),
        ("EQUIPMENT VIBRATION ANOMALY", "Haulage Belt Motor vibration spiked to 8.2 mm/s.", "warning", "/equipment"),
        ("WORKER HEALTH ALERT", "Worker WKR-103 (Ajay Kumar Singh) elevated heart rate 128 bpm detected.", "critical", "/workers"),
        ("AUDIT REPORT READY", "Weekly Statutory Compliance Audit Report has been compiled successfully.", "info", "/reports")
    ]
    for title, msg, ntype, link in notifs_raw:
        db.add(Notification(
            user_id=None,
            title=title,
            message=msg,
            type=ntype,
            link_url=link,
            is_read=False,
            created_at=now - timedelta(minutes=random.randint(5, 120))
        ))

    # 15. Seed Immutable Audit Logs
    audit_events = [
        ("USER_LOGIN", "User", "1", "admin@coalmine.gov logged in successfully from authorized station"),
        ("AI_PPE_DETECTION", "PPEDetection", "12", "YOLOv8 detected missing hardhat on CAM-05 feed"),
        ("COMPLIANCE_CASE_CREATED", "ComplianceCase", "CASE-2026-001", "Automated compliance case generated for Methane spike in Face B"),
        ("ACTION_ASSIGNED", "CorrectiveAction", "1", "Corrective action assigned to Mine Supervisor Arun Mukherjee"),
        ("RISK_FORECAST_RUN", "RiskPrediction", "8", "Predictive Risk Engine computed shift risk forecast for 8 active mine zones"),
        ("REPORT_GENERATED", "Report", "1", "Statutory PDF Safety Report generated with DGMS auditor sign-off block")
    ]
    for action, etype, eid, desc in audit_events:
        db.add(AuditLog(
            user_id=user_objs["admin@coalmine.gov"].id,
            action=action,
            entity_type=etype,
            entity_id=eid,
            previous_state=None,
            new_state=desc,
            ip_address="192.168.1.100",
            tamper_token=f"SHA256-{random.randint(10000000, 99999999)}a9b7c8d9e0f",
            timestamp=now - timedelta(minutes=random.randint(10, 300))
        ))

    # 16. Generate pre-packaged baseline PDF report file
    try:
        sample_cases = [{
            "case_number": c[0],
            "title": c[1],
            "category": c[2],
            "risk_level": c[4],
            "responsible_user_name": "Vikram Rathore (Safety Officer)",
            "status": c[7]
        } for c in cases_raw[:6]]
        
        pdf_path = generate_pdf_report({
            "title": "Coal Mine Safety Governance & Predictive Compliance Report",
            "summary_text": "DGMS statutory evaluation indicates safe operations across 7 of 8 monitored coal sectors. Working Face B remains flagged for methane evacuation protocol until auxiliary ventilation re-inspection is confirmed.",
            "kpis": {
                "Total Compliance Cases": len(cases_raw),
                "Critical Risk Zones": 1,
                "PPE Adherence Rate": "94.2%",
                "Active Sensors": len(sensor_configs),
                "Average Shift Risk": "38.5 / 100",
                "DGMS Audit Score": "Compliant"
            },
            "cases": sample_cases
        }, output_filename="sample_dgms_safety_audit_report.pdf")

        db.add(Report(
            title="Sample DGMS Comprehensive Safety Audit Report",
            report_type="Daily Safety",
            file_path="/uploads/reports/sample_dgms_safety_audit_report.pdf",
            file_format="pdf",
            generated_by_user_id=user_objs["admin@coalmine.gov"].id,
            summary_text="Automated pre-shift regulatory compliance summary report."
        ))
    except Exception as e:
        print(f"[Seed] Sample PDF report creation error: {e}")

    db.commit()
    print("[Seed] Successfully seeded all tables, users, zones, sensors, readings, cases, and reports!")

