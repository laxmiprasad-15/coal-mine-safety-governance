"""
Model Training Script: Multi-Class Coal Mine Safety Risk Classifier
Algorithms: Random Forest Classifier & Gradient Boosting Ensemble
Metrics: Accuracy, Precision, Recall, F1-score, Confusion Matrix
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_recall_fscore_support

MODELS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "..", "models")
os.makedirs(MODELS_DIR, exist_ok=True)

def generate_synthetic_mining_telemetry(n_samples=5000):
    np.random.seed(42)
    
    # Atmospheric & IoT Sensor Features
    ch4 = np.random.exponential(scale=0.35, size=n_samples)       # Methane (%)
    co = np.random.exponential(scale=11.0, size=n_samples)        # Carbon Monoxide (ppm)
    temp = np.random.normal(loc=26.5, scale=4.2, size=n_samples) # Temperature (°C)
    hum = np.random.normal(loc=66.0, scale=12.0, size=n_samples) # Humidity (%)
    vib = np.random.exponential(scale=2.6, size=n_samples)       # Vibration (mm/s)
    ppe_viol = np.random.poisson(lam=1.3, size=n_samples)        # PPE Violations in 24h
    fatigue = np.random.beta(a=2, b=5, size=n_samples) * 100     # Fatigue Index (0-100)
    equip_health = 100.0 - np.random.exponential(scale=16.0, size=n_samples) # Condition (0-100)
    equip_health = np.clip(equip_health, 10.0, 100.0)
    incidents = np.random.poisson(lam=0.4, size=n_samples)       # Zone Historical Incidents
    shift_hr = np.random.uniform(1.0, 8.0, size=n_samples)       # Elapsed Shift Hours

    X = np.column_stack([
        ch4, co, temp, hum, vib, ppe_viol, fatigue, equip_health, incidents, shift_hr
    ])

    # Regulatory Classification Rules (DGMS standards)
    y = []
    for row in X:
        r_ch4, r_co, r_temp, r_hum, r_vib, r_ppe, r_fat, r_eq, r_inc, r_hr = row
        score = 0
        if r_ch4 >= 1.25 or r_co >= 50.0:
            score += 55
        elif r_ch4 >= 0.75 or r_co >= 25.0:
            score += 30
        elif r_ch4 >= 0.5:
            score += 15

        if r_temp >= 36.0 or r_vib >= 10.0:
            score += 25
        elif r_temp >= 32.0 or r_vib >= 6.0:
            score += 15

        if r_ppe >= 4:
            score += 25
        elif r_ppe >= 2:
            score += 12

        if r_fat >= 70.0 and r_hr >= 6.0:
            score += 20
        elif r_fat >= 50.0:
            score += 10

        if r_eq <= 40.0:
            score += 25
        elif r_eq <= 65.0:
            score += 12

        score += min(r_inc * 8, 20)

        if score >= 70:
            y.append(3)  # Critical
        elif score >= 45:
            y.append(2)  # High
        elif score >= 22:
            y.append(1)  # Medium
        else:
            y.append(0)  # Low

    feature_cols = [
        "methane_pct", "carbon_monoxide_ppm", "temperature_c", "humidity_pct",
        "vibration_mms", "ppe_violations_24h", "worker_fatigue_avg",
        "equipment_health_avg", "historical_incidents", "shift_hour"
    ]
    df = pd.DataFrame(X, columns=feature_cols)
    df["risk_level"] = y
    return df

def train_and_evaluate():
    print("Generating simulated coal mine telemetry dataset (5000 records)...")
    df = generate_synthetic_mining_telemetry(5000)

    X = df.drop(columns=["risk_level"])
    y = df["risk_level"]

    # 80/20 Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Training set: {X_train.shape[0]} samples | Testing set: {X_test.shape[0]} samples")

    # 1. Random Forest Classifier
    rf = RandomForestClassifier(n_estimators=150, max_depth=12, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)

    y_pred = rf.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="weighted")

    print("\n" + "=" * 50)
    print("RANDOM FOREST RISK CLASSIFIER EVALUATION")
    print("=" * 50)
    print(f"Accuracy:  {acc:.4f} ({acc*100:.2f}%)")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print("\nClassification Report:")
    target_names = ["Low", "Medium", "High", "Critical"]
    print(classification_report(y_test, y_pred, target_names=target_names))

    print("Confusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    model_path = os.path.join(MODELS_DIR, "mine_risk_rf.joblib")
    joblib.dump(rf, model_path)
    print(f"\nTrained risk classifier model saved to: {model_path}")

if __name__ == "__main__":
    train_and_evaluate()

