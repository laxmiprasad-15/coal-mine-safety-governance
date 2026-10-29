"""
Autonomous Real-Time Background Telemetry Streamer
Emits realistic, physically-consistent continuous sensor updates into the SQLite database.
Simulates live IoT mine telemetry (DGMS calibrated).
"""

import threading
import time
import random
from datetime import datetime
from app.core.database import SessionLocal
from app.models.models import Sensor, SensorReading, ComplianceCase, Notification, User, Anomaly
from app.ml.anomaly_detector import anomaly_detector

class RealtimeMineStreamer:
    def __init__(self):
        self._is_running = False
        self._thread = None
        self._interval = 4.0  # seconds between pulses
        self._lock = threading.Lock()
        self.total_pulses = 0

    @property
    def is_running(self):
        return self._is_running

    def start(self, interval: float = 4.0):
        with self._lock:
            if self._is_running:
                return True
            self._interval = max(1.0, interval)
            self._is_running = True
            self._thread = threading.Thread(target=self._run_loop, daemon=True)
            self._thread.start()
            return True

    def stop(self):
        with self._lock:
            self._is_running = False
            return False

    def _run_loop(self):
        while self._is_running:
            try:
                self._stream_pulse()
                self.total_pulses += 1
            except Exception as e:
                print(f"[RealtimeStreamer] Error during pulse: {e}")
            time.sleep(self._interval)

    def _stream_pulse(self):
        db = SessionLocal()
        try:
            sensors = db.query(Sensor).all()
            now = datetime.utcnow()

            for s in sensors:
                # Base realistic values per sensor type
                if s.type == "CH4":
                    base = 0.35 if "FACE" in s.name.upper() else 0.12
                    val = max(0.01, round(base + random.gauss(0, 0.03), 3))
                elif s.type == "CO":
                    base = 12.0 if "FACE" in s.name.upper() else 4.0
                    val = max(0.5, round(base + random.gauss(0, 0.8), 1))
                elif s.type == "O2":
                    val = min(21.0, max(19.2, round(20.7 + random.gauss(0, 0.05), 2)))
                elif s.type == "TEMP":
                    val = round(28.0 + random.gauss(0, 0.3), 1)
                elif s.type == "HUMIDITY":
                    val = min(95.0, max(45.0, round(65.0 + random.gauss(0, 1.5), 1)))
                elif s.type == "VIBRATION":
                    base = 3.2 if "CONVEYOR" in s.name.upper() else 1.2
                    val = max(0.2, round(base + random.gauss(0, 0.25), 2))
                else:  # AIRFLOW
                    val = max(0.3, round(1.8 + random.gauss(0, 0.1), 2))

                # Occasional realistic micro-spike (3% probability)
                if random.random() < 0.03:
                    val = round(s.warning_threshold * random.uniform(1.05, 1.22), 2)

                eval_res = anomaly_detector.evaluate_reading(s.type, val)
                
                reading = SensorReading(
                    sensor_id=s.id,
                    zone_id=s.zone_id,
                    value=val,
                    is_anomaly=eval_res["is_anomaly"],
                    anomaly_score=eval_res["anomaly_score"],
                    timestamp=now
                )
                db.add(reading)

                if eval_res["is_anomaly"] and eval_res["severity"] in ["High", "Critical"]:
                    db.add(Anomaly(
                        source_type="sensor",
                        source_id=s.id,
                        zone_id=s.zone_id,
                        severity=eval_res["severity"],
                        metric_name=f"{s.type} ({s.name})",
                        value=val,
                        threshold=eval_res["threshold"],
                        description=eval_res["description"]
                    ))

            db.commit()
        finally:
            db.close()

streamer = RealtimeMineStreamer()

