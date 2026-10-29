"""
Real-Time Coal Mine Sensor & Telemetry Dataset Generator
Simulates realistic, physically-constrained time-series telemetry modeled on
Indian underground coal mines (DGMS standards, Jharia & Singareni Coalfields).

Generates:
1. uploads/realtime_jharia_telemetry_stream.csv (Multi-zone multi-gas time-series)
2. uploads/realtime_worker_wearable_health.csv (Smart helmet/band biometrics)
3. uploads/realtime_equipment_telemetry.csv (Vibration & thermal degradation)
"""

import os
import csv
import random
import math
from datetime import datetime, timedelta

random.seed(101)

ZONES = [
    {"code": "ZN-ENTRY", "name": "Main Incline & Pithead Entry", "ch4_base": 0.05, "co_base": 2.0, "temp_base": 24.5, "o2_base": 20.9, "air_base": 2.8},
    {"code": "ZN-TUNNEL", "name": "Main Haulage Roadway / Tunnel 3", "ch4_base": 0.15, "co_base": 4.5, "temp_base": 26.2, "o2_base": 20.7, "air_base": 1.9},
    {"code": "ZN-FACE-A", "name": "Working Face A (Longwall Panel 4)", "ch4_base": 0.45, "co_base": 14.0, "temp_base": 30.5, "o2_base": 20.1, "air_base": 0.95},
    {"code": "ZN-FACE-B", "name": "Working Face B (Continuous Miner)", "ch4_base": 0.52, "co_base": 18.5, "temp_base": 31.8, "o2_base": 19.9, "air_base": 0.85},
    {"code": "ZN-CONVEYOR", "name": "Conveyor Belt Transfer Point 2", "ch4_base": 0.22, "co_base": 8.0, "temp_base": 28.4, "o2_base": 20.5, "air_base": 1.4},
    {"code": "ZN-VENT", "name": "Ventilation Return Airway 1", "ch4_base": 0.65, "co_base": 12.0, "temp_base": 29.1, "o2_base": 20.0, "air_base": 2.4},
    {"code": "ZN-EQUIP", "name": "Substation & Electrical Switchgear", "ch4_base": 0.08, "co_base": 3.0, "temp_base": 27.5, "o2_base": 20.8, "air_base": 1.2},
    {"code": "ZN-ASSEMBLY", "name": "Emergency Refuge & Assembly Point", "ch4_base": 0.02, "co_base": 1.0, "temp_base": 23.0, "o2_base": 21.0, "air_base": 1.8},
]

def generate_gas_telemetry(hours=24, interval_mins=5):
    """Generate multi-zone gas and environmental telemetry with shift cycles and realistic micro-events."""
    start_time = datetime.now() - timedelta(hours=hours)
    steps = int((hours * 60) / interval_mins)
    
    rows = []
    
    for step in range(steps):
        current_time = start_time + timedelta(minutes=step * interval_mins)
        hour = current_time.hour
        minute = current_time.minute
        
        # Shift activity multiplier: peak cutting happens at mid-shift
        # Shift 1: 06:00 - 14:00 (peak 09:00-12:00)
        # Shift 2: 14:00 - 22:00 (peak 16:00-19:00)
        # Shift 3: 22:00 - 06:00 (maintenance / slow)
        shift_activity = 0.5 + 0.5 * abs(math.sin((hour + minute/60.0) * math.pi / 8.0))
        
        for z in ZONES:
            # Random Brownian drift
            noise_ch4 = random.gauss(0, 0.03)
            noise_co = random.gauss(0, 0.8)
            noise_temp = random.gauss(0, 0.3)
            noise_air = random.gauss(0, 0.05)
            
            ch4 = max(0.01, z["ch4_base"] * (0.8 + 0.4 * shift_activity) + noise_ch4)
            co = max(0.5, z["co_base"] * (0.85 + 0.35 * shift_activity) + noise_co)
            temp = z["temp_base"] + 0.8 * shift_activity + noise_temp
            humidity = min(95.0, max(50.0, 68.0 + 10.0 * math.sin(step / 30.0) + random.gauss(0, 2.0)))
            o2 = max(18.5, min(21.0, z["o2_base"] - 0.2 * (ch4 / 0.5) + random.gauss(0, 0.05)))
            airflow = max(0.2, z["air_base"] + noise_air)
            vibration = max(0.4, (2.2 if "CONVEYOR" in z["code"] or "FACE" in z["code"] else 0.8) * shift_activity + random.gauss(0, 0.2))
            
            # Inject a realistic gas spike scenario in Working Face A around hour 14 to test anomaly detection
            if z["code"] == "ZN-FACE-A" and 14 <= hour <= 15:
                ch4 += 0.45  # pushes CH4 to ~0.95% (DGMS warning limit 0.75%)
                co += 18.0   # pushes CO to ~35 ppm (DGMS warning limit 25 ppm)
                airflow -= 0.3
            
            # Inject conveyor bearing vibration anomaly in Conveyor zone around hour 18
            if z["code"] == "ZN-CONVEYOR" and 18 <= hour <= 19:
                vibration += 5.5  # pushes vibration to ~8.0 mm/s (DGMS limit 7.5 mm/s)
                temp += 4.5
            
            rows.append({
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "zone_code": z["code"],
                "zone_name": z["name"],
                "methane_pct": round(ch4, 3),
                "co_ppm": round(co, 1),
                "temperature_c": round(temp, 1),
                "humidity_pct": round(humidity, 1),
                "oxygen_pct": round(o2, 2),
                "airflow_ms": round(airflow, 2),
                "vibration_mms": round(vibration, 2)
            })
            
    return rows


def generate_wearable_health(num_workers=20, readings_per_worker=30):
    """Generate biometric telemetry from miner wearable smart helmets/wristbands."""
    base_time = datetime.now() - timedelta(hours=8)
    rows = []
    
    worker_names = [
        "Ramesh Yadav", "Suresh Kumar", "Manoj Singh", "Rajesh Soren", "Bikash Mahato",
        "Santosh Munda", "Prakash Bauri", "Dilip Murmu", "Subhas Gope", "Amit Hansda",
        "Kailash Tudu", "Binod Besra", "Gopal Karmakar", "Ashok Roy", "Pappu Shaw",
        "Dinesh Oraon", "Somra Tirkey", "Birsa Ekka", "Chotu Hembrom", "Kundan Thakur"
    ]
    
    for i, name in enumerate(worker_names):
        emp_id = f"EMP-{1000 + i}"
        zone = random.choice(ZONES)
        
        # Baseline vitals per worker
        base_hr = random.randint(68, 78)
        base_temp = random.uniform(36.4, 36.8)
        
        for step in range(readings_per_worker):
            t = base_time + timedelta(minutes=step * 15)
            fatigue_trend = (step / readings_per_worker) * 15.0 # increasing fatigue over shift
            
            # Physical exertion spike for longwall miners
            work_factor = random.choice([0.8, 1.0, 1.3, 1.6])
            hr = int(base_hr + fatigue_trend + work_factor * 18 + random.gauss(0, 3))
            body_temp = round(base_temp + (fatigue_trend / 30.0) + (0.3 if work_factor > 1.2 else 0.0) + random.gauss(0, 0.08), 2)
            spo2 = round(max(91.0, min(99.0, 98.0 - (hr - 70) * 0.05 + random.gauss(0, 0.4))), 1)
            activity = "Heavy Drilling" if work_factor > 1.4 else ("Haulage Operation" if work_factor > 1.1 else "Inspection / Rest")
            
            # Introduce heat stress on worker #4 (Santosh Munda)
            if i == 5 and step > 20:
                hr = min(155, hr + 30)
                body_temp = max(38.6, body_temp + 1.2)
                activity = "HEAT STRESS DETECTED"
            
            rows.append({
                "timestamp": t.strftime("%Y-%m-%d %H:%M:%S"),
                "employee_id": emp_id,
                "worker_name": name,
                "zone_code": zone["code"],
                "heart_rate_bpm": hr,
                "body_temperature_c": body_temp,
                "spo2_pct": spo2,
                "activity_status": activity,
                "hours_without_rest": round(step * 0.25, 2)
            })
            
    return rows


def generate_equipment_telemetry(hours=12):
    """Generate industrial equipment condition monitoring telemetry."""
    machines = [
        {"id": "EQ-LWL-01", "name": "Longwall Shearer Joy 7LS", "zone": "ZN-FACE-A", "vib_base": 3.8, "temp_base": 58.0},
        {"id": "EQ-CM-02", "name": "Continuous Miner Sandvik MB670", "zone": "ZN-FACE-B", "vib_base": 4.1, "temp_base": 62.0},
        {"id": "EQ-CV-01", "name": "Main Trunk Belt Conveyor 1500kW", "zone": "ZN-CONVEYOR", "vib_base": 2.9, "temp_base": 48.0},
        {"id": "EQ-FAN-01", "name": "Main Mine Ventilation Fan (Axial)", "zone": "ZN-VENT", "vib_base": 1.8, "temp_base": 42.0},
        {"id": "EQ-PUMP-03", "name": "Underground Dewatering Slurry Pump", "zone": "ZN-TUNNEL", "vib_base": 2.4, "temp_base": 45.0},
    ]
    
    start_time = datetime.now() - timedelta(hours=hours)
    steps = hours * 6 # every 10 mins
    rows = []
    
    for step in range(steps):
        t = start_time + timedelta(minutes=step * 10)
        for m in machines:
            vib = max(0.5, m["vib_base"] + random.gauss(0, 0.4))
            temp = max(30.0, m["temp_base"] + (step / steps) * 4.0 + random.gauss(0, 1.2))
            current_draw = round(random.uniform(110.0, 185.0), 1)
            
            # Predict RUL (Remaining Useful Life in hours)
            rul = max(10, int(850 - (temp - 40) * 8 - (vib - 2) * 40))
            
            rows.append({
                "timestamp": t.strftime("%Y-%m-%d %H:%M:%S"),
                "equipment_id": m["id"],
                "equipment_name": m["name"],
                "zone_code": m["zone"],
                "vibration_rms_mms": round(vib, 2),
                "bearing_temp_c": round(temp, 1),
                "motor_current_amp": current_draw,
                "estimated_rul_hours": rul
            })
            
    return rows


def write_csv(filepath, rows):
    if not rows:
        return
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)
    print(f"[OK] Generated {len(rows):5d} rows -> {filepath}")


def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    uploads_dir = os.path.join(root_dir, "uploads")
    
    print("=" * 65)
    print("Generating Real-World Coal Mine Telemetry Datasets (DGMS Calibrated)")
    print("=" * 65)
    
    # 1. 24-hr multi-gas telemetry
    gas_rows = generate_gas_telemetry(hours=24, interval_mins=5)
    write_csv(os.path.join(uploads_dir, "realtime_jharia_telemetry_stream.csv"), gas_rows)
    
    # 2. Worker wearable telemetry
    worker_rows = generate_wearable_health(num_workers=20, readings_per_worker=32)
    write_csv(os.path.join(uploads_dir, "realtime_worker_wearable_health.csv"), worker_rows)
    
    # 3. Equipment telemetry
    equip_rows = generate_equipment_telemetry(hours=12)
    write_csv(os.path.join(uploads_dir, "realtime_equipment_telemetry.csv"), equip_rows)
    
    print("=" * 65)
    print("Datasets successfully written to uploads/ directory.")

if __name__ == "__main__":
    main()
