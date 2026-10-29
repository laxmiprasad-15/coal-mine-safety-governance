import os
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from app.core.config import settings

class SensorAnomalyDetector:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or os.path.join(settings.MODELS_DIR, "sensor_isolation_forest.joblib")
        self.model = None
        self._load_or_train()

    def _load_or_train(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                return
            except Exception as e:
                print(f"[AnomalyDetector] Error loading model: {e}")
        
        # Train baseline synthetic model on standard coal mine environmental baseline
        # Features: [CH4 (%), CO (ppm), Temp (°C), Humidity (%), Vibration (mm/s), Airflow (m/s)]
        np.random.seed(42)
        normal_data = np.column_stack([
            np.random.uniform(0.1, 0.6, 500),    # CH4 (0.1 - 0.6%)
            np.random.uniform(5.0, 20.0, 500),   # CO (5 - 20 ppm)
            np.random.uniform(22.0, 29.0, 500),  # Temp (22 - 29 C)
            np.random.uniform(55.0, 75.0, 500),  # Humidity (55 - 75 %)
            np.random.uniform(1.0, 4.0, 500),    # Vibration (1 - 4 mm/s)
            np.random.uniform(1.2, 3.5, 500)     # Airflow (1.2 - 3.5 m/s)
        ])
        
        # Add 3% synthetic anomalies for robust boundary tuning
        anomalies = np.column_stack([
            np.random.uniform(0.9, 1.8, 20),
            np.random.uniform(30.0, 75.0, 20),
            np.random.uniform(34.0, 42.0, 20),
            np.random.uniform(85.0, 98.0, 20),
            np.random.uniform(8.0, 16.0, 20),
            np.random.uniform(0.1, 0.4, 20)
        ])
        
        X_train = np.vstack([normal_data, anomalies])
        self.model = IsolationForest(contamination=0.05, random_state=42)
        self.model.fit(X_train)
        
        try:
            joblib.dump(self.model, self.model_path)
        except Exception as e:
            print(f"[AnomalyDetector] Could not save joblib model: {e}")

    def evaluate_reading(self, sensor_type: str, value: float, context: dict = None) -> dict:
        """
        Evaluates a sensor reading using statutory DGMS thresholds + ML isolation score.
        """
        sensor_type_upper = sensor_type.upper()
        is_anomaly = False
        severity = "Low"
        threshold = 0.0
        reason = ""

        # Statutory Threshold Evaluation
        if "CH4" in sensor_type_upper or "METHANE" in sensor_type_upper:
            threshold = settings.CH4_WARNING_PCT
            if value >= settings.CH4_DANGER_PCT:
                is_anomaly = True
                severity = "Critical"
                reason = f"Methane concentration ({value:.2f}%) exceeds explosive danger limit ({settings.CH4_DANGER_PCT}%)"
            elif value >= settings.CH4_WARNING_PCT:
                is_anomaly = True
                severity = "High"
                reason = f"Methane concentration ({value:.2f}%) exceeds DGMS statutory warning limit ({settings.CH4_WARNING_PCT}%)"
        
        elif "CO" in sensor_type_upper or "CARBON" in sensor_type_upper:
            threshold = settings.CO_WARNING_PPM
            if value >= settings.CO_DANGER_PPM:
                is_anomaly = True
                severity = "Critical"
                reason = f"Toxic Carbon Monoxide ({value:.1f} ppm) exceeds hazardous limit ({settings.CO_DANGER_PPM} ppm)"
            elif value >= settings.CO_WARNING_PPM:
                is_anomaly = True
                severity = "High"
                reason = f"Carbon Monoxide ({value:.1f} ppm) above normal threshold ({settings.CO_WARNING_PPM} ppm)"
        
        elif "TEMP" in sensor_type_upper:
            threshold = settings.TEMP_MAX_C
            if value >= 38.0:
                is_anomaly = True
                severity = "Critical"
                reason = f"Extreme temperature ({value:.1f}°C) suggests active spontaneous combustion or electrical fire"
            elif value >= settings.TEMP_MAX_C:
                is_anomaly = True
                severity = "Medium"
                reason = f"Underground heat stress threshold exceeded ({value:.1f}°C > {settings.TEMP_MAX_C}°C)"

        elif "VIB" in sensor_type_upper:
            threshold = settings.VIBRATION_MAX_MMS
            if value >= 12.0:
                is_anomaly = True
                severity = "Critical"
                reason = f"Severe mechanical resonance/vibration ({value:.2f} mm/s) - risk of catastrophic shaft/gear failure"
            elif value >= settings.VIBRATION_MAX_MMS:
                is_anomaly = True
                severity = "High"
                reason = f"Machinery vibration ({value:.2f} mm/s) exceeds standard limit ({settings.VIBRATION_MAX_MMS} mm/s)"

        elif "AIR" in sensor_type_upper:
            threshold = settings.AIRFLOW_MIN_MS
            if value < 0.3:
                is_anomaly = True
                severity = "Critical"
                reason = f"Dangerous ventilation stoppage ({value:.2f} m/s < 0.3 m/s) - potential explosive gas accumulation"
            elif value < settings.AIRFLOW_MIN_MS:
                is_anomaly = True
                severity = "High"
                reason = f"Ventilation airflow sluggish ({value:.2f} m/s < {settings.AIRFLOW_MIN_MS} m/s)"

        # Calculate isolation forest score if multi-feature vector provided
        anomaly_score = 0.85 if is_anomaly else 0.12
        if context and self.model:
            try:
                features = np.array([[
                    context.get("ch4", 0.4),
                    context.get("co", 12.0),
                    context.get("temp", 26.0),
                    context.get("humidity", 65.0),
                    context.get("vibration", 2.0),
                    context.get("airflow", 2.0)
                ]])
                ml_pred = self.model.predict(features)[0]  # -1 = anomaly, 1 = normal
                ml_score = -float(self.model.score_samples(features)[0])
                if ml_pred == -1 and not is_anomaly:
                    is_anomaly = True
                    severity = "Medium"
                    reason = f"Multivariate anomaly detected by Isolation Forest (anomaly score: {ml_score:.2f})"
                anomaly_score = max(anomaly_score, min(round(ml_score, 2), 1.0))
            except Exception:
                pass

        return {
            "is_anomaly": is_anomaly,
            "severity": severity,
            "threshold": threshold,
            "anomaly_score": anomaly_score,
            "description": reason if is_anomaly else "Normal operational parameters"
        }

anomaly_detector = SensorAnomalyDetector()

