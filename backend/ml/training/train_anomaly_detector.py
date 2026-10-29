"""
Model Training Script: Isolation Forest Unsupervised Anomaly Detector for Coal Mine IoT Sensors
Detects multi-sensor outliers, gas leaks, and severe machinery vibrations
"""

import os
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def train_anomaly_model():
    print("Training Isolation Forest on multi-sensor mining baseline...")
    np.random.seed(42)
    # Features: [CH4, CO, Temp, Humidity, Vibration, Airflow]
    normal_data = np.column_stack([
        np.random.uniform(0.1, 0.55, 3000),   # Normal methane (0.1 - 0.55%)
        np.random.uniform(5.0, 18.0, 3000),   # Normal CO (5 - 18 ppm)
        np.random.uniform(22.0, 28.5, 3000),  # Normal Temp (22 - 28.5 C)
        np.random.uniform(55.0, 75.0, 3000),  # Normal Humidity (55 - 75 %)
        np.random.uniform(1.0, 3.5, 3000),    # Normal Vibration (1 - 3.5 mm/s)
        np.random.uniform(1.2, 3.2, 3000)     # Normal Airflow (1.2 - 3.2 m/s)
    ])

    # Outliers (anomalous events: outbursts, fires, ventilation collapse)
    anomalous_data = np.column_stack([
        np.random.uniform(0.9, 2.1, 150),
        np.random.uniform(30.0, 90.0, 150),
        np.random.uniform(34.0, 44.0, 150),
        np.random.uniform(85.0, 99.0, 150),
        np.random.uniform(7.8, 16.5, 150),
        np.random.uniform(0.05, 0.35, 150)
    ])

    X = np.vstack([normal_data, anomalous_data])
    iso = IsolationForest(n_estimators=100, contamination=0.045, random_state=42)
    iso.fit(X)

    preds = iso.predict(X)
    anomaly_cnt = np.sum(preds == -1)
    normal_cnt = np.sum(preds == 1)
    print(f"Dataset: {X.shape[0]} total samples -> Predicted {anomaly_cnt} anomalies, {normal_cnt} normal.")

    model_path = os.path.join(MODELS_DIR, "sensor_isolation_forest.joblib")
    joblib.dump(iso, model_path)
    print(f"Isolation Forest model saved to: {model_path}")

if __name__ == "__main__":
    train_anomaly_model()

