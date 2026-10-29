import os
import cv2
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

os.makedirs("uploads/ppe", exist_ok=True)
os.makedirs("uploads/reports", exist_ok=True)
os.makedirs("uploads/evidence", exist_ok=True)

# 1. Generate realistic synthetic worker image with safety gear
def create_worker_image(filename: str, has_helmet: bool = True, has_vest: bool = True):
    img = np.zeros((640, 480, 3), dtype=np.uint8)
    # Mine background: dark coal seam texture with underground tunnel lighting
    for y in range(640):
        shade = int(25 + 15 * np.sin(y / 40.0) + np.random.randint(0, 10))
        img[y, :] = [shade, shade + 5, shade + 10]

    # Mine tunnel arch outline in background
    cv2.ellipse(img, (240, 320), (220, 300), 0, 180, 360, (60, 65, 75), 12)
    cv2.line(img, (20, 320), (20, 640), (60, 65, 75), 10)
    cv2.line(img, (460, 320), (460, 640), (60, 65, 75), 10)

    # Worker body silhouette (legs & dark trousers)
    cv2.rectangle(img, (180, 420), (230, 580), (40, 40, 50), -1)  # Left leg
    cv2.rectangle(img, (250, 420), (300, 580), (40, 40, 50), -1)  # Right leg
    cv2.rectangle(img, (160, 570), (235, 615), (20, 20, 25), -1)  # Left steel-toe boot
    cv2.rectangle(img, (245, 570), (320, 615), (20, 20, 25), -1)  # Right steel-toe boot

    # Torso (Vest or plain shirt)
    if has_vest:
        # High-Vis Neon Yellow/Lime Vest (BGR: 0, 230, 230 or 20, 240, 220)
        cv2.rectangle(img, (150, 200), (330, 430), (20, 230, 240), -1)
        # Reflective silver stripes on vest
        cv2.rectangle(img, (170, 210), (195, 420), (220, 220, 225), -1)
        cv2.rectangle(img, (285, 210), (310, 420), (220, 220, 225), -1)
        cv2.rectangle(img, (150, 330), (330, 360), (220, 220, 225), -1)
    else:
        # Dark non-compliant jacket
        cv2.rectangle(img, (150, 200), (330, 430), (45, 45, 55), -1)

    # Arms
    cv2.rectangle(img, (110, 210), (150, 390), (45, 50, 60), -1)
    cv2.rectangle(img, (330, 210), (370, 390), (45, 50, 60), -1)
    # Heavy duty work gloves
    cv2.rectangle(img, (110, 380), (150, 425), (10, 140, 210), -1)
    cv2.rectangle(img, (330, 380), (370, 425), (10, 140, 210), -1)

    # Head and face
    cv2.ellipse(img, (240, 140), (45, 55), 0, 0, 360, (140, 175, 215), -1)
    # Protective eye goggles
    cv2.rectangle(img, (205, 125), (275, 145), (180, 140, 30), -1)

    # Hardhat / Helmet
    if has_helmet:
        # Industrial Safety Hardhat (Bright Yellow/Orange)
        cv2.ellipse(img, (240, 95), (60, 45), 0, 180, 360, (15, 215, 245), -1)
        cv2.rectangle(img, (175, 90), (305, 105), (15, 215, 245), -1)  # Helmet brim
        # Headlamp mounted on helmet
        cv2.rectangle(img, (225, 75), (255, 95), (230, 230, 240), -1)
        cv2.circle(img, (240, 85), 7, (255, 255, 255), -1)
    else:
        # Hair / Bare head (non-compliant)
        cv2.ellipse(img, (240, 95), (45, 30), 0, 180, 360, (25, 30, 40), -1)

    cv2.imwrite(filename, img)

create_worker_image("uploads/ppe/demo_worker_frame.jpg", has_helmet=False, has_vest=False)
create_worker_image("uploads/ppe/demo_worker_compliant.jpg", has_helmet=True, has_vest=True)
create_worker_image("uploads/ppe/demo_worker_no_helmet.jpg", has_helmet=False, has_vest=True)

# 2. Generate sample CSV file for Sensor Batch Ingestion testing
sensor_rows = []
base_time = datetime.utcnow() - timedelta(hours=6)
for i in range(120):
    t = base_time + timedelta(minutes=i * 3)
    # Simulate a gas spike in row 80 to 95
    is_spike = (80 <= i <= 95)
    ch4_val = round(1.35 + np.random.uniform(0.02, 0.25) if is_spike else 0.38 + np.random.uniform(-0.05, 0.08), 2)
    co_val = round(48.0 + np.random.uniform(2.0, 12.0) if is_spike else 11.5 + np.random.uniform(-1.0, 2.0), 1)
    temp_val = round(34.2 if is_spike else 26.4 + np.random.uniform(-0.5, 0.8), 1)
    humidity_val = round(72.0 + np.random.uniform(-3.0, 4.0), 1)
    vibration_val = round(8.4 if is_spike else 2.1 + np.random.uniform(-0.2, 0.3), 2)
    airflow_val = round(0.28 if is_spike else 1.95 + np.random.uniform(-0.1, 0.2), 2)

    sensor_rows.append({
        "timestamp": t.strftime("%Y-%m-%d %H:%M:%S"),
        "zone_code": "ZN-04",
        "methane_pct": ch4_val,
        "co_ppm": co_val,
        "temperature_c": temp_val,
        "humidity_pct": humidity_val,
        "vibration_mms": vibration_val,
        "airflow_ms": airflow_val
    })

df = pd.DataFrame(sensor_rows)
df.to_csv("uploads/sensor_sample_upload.csv", index=False)
print("Generated sample PPE images and sample sensor CSV!")

