import os
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from app.core.config import settings

FEATURE_NAMES = [
    "methane_pct",           # CH4 level (%)
    "carbon_monoxide_ppm",   # CO level (ppm)
    "temperature_c",         # Temperature (°C)
    "humidity_pct",          # Humidity (%)
    "vibration_mms",         # Machinery Vibration (mm/s)
    "ppe_violations_24h",    # Number of PPE non-compliance events in zone
    "worker_fatigue_avg",    # Mean fatigue index (0-100)
    "equipment_health_avg",  # Mean equipment condition (0-100)
    "historical_incidents",  # Prior recorded safety incidents
    "shift_hour"             # Hour of shift (0-8)
]

RISK_CLASSES = ["Low", "Medium", "High", "Critical"]

class PredictiveRiskEngine:
    def __init__(self, model_path: str = None):
        self.model_path = model_path or os.path.join(settings.MODELS_DIR, "mine_risk_rf.joblib")
        self.model = None
        self._load_or_train()

    def _load_or_train(self):
        if os.path.exists(self.model_path):
            try:
                self.model = joblib.load(self.model_path)
                return
            except Exception as e:
                print(f"[RiskEngine] Loading error: {e}")

        # Train a realistic multi-class Random Forest model for Coal Mine Safety
        np.random.seed(101)
        n_samples = 2500

        # Generate realistic synthetic mining sensor telemetry
        ch4 = np.random.exponential(scale=0.3, size=n_samples) # usually low, occasionally spikes
        co = np.random.exponential(scale=10.0, size=n_samples)
        temp = np.random.normal(loc=26.0, scale=4.0, size=n_samples)
        hum = np.random.normal(loc=65.0, scale=12.0, size=n_samples)
        vib = np.random.exponential(scale=2.5, size=n_samples)
        ppe_viol = np.random.poisson(lam=1.2, size=n_samples)
        fatigue = np.random.beta(a=2, b=5, size=n_samples) * 100
        equip_health = 100.0 - np.random.exponential(scale=15.0, size=n_samples)
        equip_health = np.clip(equip_health, 10.0, 100.0)
        incidents = np.random.poisson(lam=0.5, size=n_samples)
        shift_hr = np.random.uniform(1.0, 8.0, size=n_samples)

        X = np.column_stack([
            ch4, co, temp, hum, vib, ppe_viol, fatigue, equip_health, incidents, shift_hr
        ])

        # Formulate ground truth risk rules based on DGMS safety engineering rules
        y = []
        for row in X:
            r_ch4, r_co, r_temp, r_hum, r_vib, r_ppe, r_fat, r_eq, r_inc, r_hr = row
            score = 0
            # Gas hazard weights (primary explosion/asphyxiation risk)
            if r_ch4 >= 1.25 or r_co >= 50.0:
                score += 55
            elif r_ch4 >= 0.75 or r_co >= 25.0:
                score += 30
            elif r_ch4 >= 0.5:
                score += 15

            # Thermal and mechanical stress
            if r_temp >= 36.0 or r_vib >= 10.0:
                score += 25
            elif r_temp >= 32.0 or r_vib >= 6.0:
                score += 15

            # Behavioral & PPE compliance
            if r_ppe >= 4:
                score += 25
            elif r_ppe >= 2:
                score += 12

            # Worker health & fatigue
            if r_fat >= 70.0 and r_hr >= 6.0:
                score += 20
            elif r_fat >= 50.0:
                score += 10

            # Equipment degradation
            if r_eq <= 40.0:
                score += 25
            elif r_eq <= 65.0:
                score += 12

            # Historical safety incidents
            score += min(r_inc * 8, 20)

            # Classify
            if score >= 70:
                y.append(3)  # Critical
            elif score >= 45:
                y.append(2)  # High
            elif score >= 22:
                y.append(1)  # Medium
            else:
                y.append(0)  # Low

        X_train = np.array(X)
        y_train = np.array(y)

        rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42)
        rf.fit(X_train, y_train)
        self.model = rf

        try:
            joblib.dump(self.model, self.model_path)
            print("[RiskEngine] Trained and saved Random Forest Risk Classifier.")
        except Exception as e:
            print(f"[RiskEngine] Save failed: {e}")

    def predict_risk(self, feature_dict: dict) -> dict:
        """
        Takes raw zone indicators and returns predicted risk class, probability,
        risk score (0-100), and feature importance attribution.
        """
        # Build vector in exact feature order
        vector = [
            float(feature_dict.get("methane_pct", 0.35)),
            float(feature_dict.get("carbon_monoxide_ppm", 12.0)),
            float(feature_dict.get("temperature_c", 25.5)),
            float(feature_dict.get("humidity_pct", 65.0)),
            float(feature_dict.get("vibration_mms", 2.2)),
            float(feature_dict.get("ppe_violations_24h", 0)),
            float(feature_dict.get("worker_fatigue_avg", 18.0)),
            float(feature_dict.get("equipment_health_avg", 88.0)),
            float(feature_dict.get("historical_incidents", 0)),
            float(feature_dict.get("shift_hour", 4.0))
        ]

        if not self.model:
            self._load_or_train()

        X = np.array([vector])
        pred_idx = self.model.predict(X)[0]
        probs = self.model.predict_proba(X)[0]
        pred_class = RISK_CLASSES[pred_idx]
        confidence = float(probs[pred_idx])

        # Compute calculated continuous risk score (0-100)
        # Low=0-25, Med=26-50, High=51-75, Critical=76-100
        base_scores = {"Low": 15.0, "Medium": 42.0, "High": 68.0, "Critical": 91.0}
        spread = 15.0 * (confidence - 0.5)
        raw_score = base_scores[pred_class] + spread
        
        # Override with strict DGMS hard thresholds if severe hazards exist
        if vector[0] >= settings.CH4_DANGER_PCT or vector[1] >= settings.CO_DANGER_PPM:
            pred_class = "Critical"
            confidence = max(confidence, 0.98)
            raw_score = max(raw_score, 94.0)

        risk_score = round(max(5.0, min(99.0, raw_score)), 1)

        # Compute feature contributions using feature importances & normalized deviations
        feature_importances = self.model.feature_importances_
        factor_contributions = []

        # Safe baselines for comparison
        baselines = [0.4, 15.0, 26.0, 65.0, 2.5, 0.0, 20.0, 90.0, 0.0, 4.0]
        scales = [1.0, 30.0, 10.0, 25.0, 5.0, 3.0, 50.0, 50.0, 2.0, 4.0]

        for i, name in enumerate(FEATURE_NAMES):
            diff = (vector[i] - baselines[i]) / scales[i]
            if name == "equipment_health_avg":
                diff = -diff  # lower health means higher risk contribution
            
            # Impact factor
            impact = max(0.0, diff) * feature_importances[i] * 100
            factor_contributions.append({
                "feature": name,
                "label": name.replace("_", " ").title(),
                "value": round(vector[i], 2),
                "baseline": baselines[i],
                "importance_weight": round(float(feature_importances[i]), 3),
                "contribution_score": round(float(impact), 2)
            })

        factor_contributions.sort(key=lambda x: x["contribution_score"], reverse=True)

        return {
            "predicted_risk": pred_class,
            "risk_score": risk_score,
            "confidence": round(confidence, 3),
            "class_probabilities": {
                RISK_CLASSES[i]: round(float(probs[i]), 3) for i in range(len(RISK_CLASSES))
            },
            "top_factors": factor_contributions[:5],
            "all_factors": factor_contributions
        }

risk_engine = PredictiveRiskEngine()

