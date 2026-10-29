"""
Synthetic Dataset Generator for Coal Mine Safety Risk Prediction
Generates training data for the Random Forest risk classifier.

Run: python backend/ml/datasets/generate_dataset.py
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import random
import os

random.seed(42)
np.random.seed(42)

def generate_mine_safety_dataset(n_samples: int = 5000) -> pd.DataFrame:
    """
    Generate synthetic coal mine sensor & risk dataset.
    
    Features:
        - methane_ppm: Methane concentration (ppm). Safe < 7500 (0.75%), Danger > 12500 (1.25%)
        - co_ppm: Carbon monoxide (ppm). Safe < 25, Danger > 50
        - temperature_c: Zone temperature °C. Safe < 33
        - humidity_pct: Relative humidity %. Normal 40-80
        - vibration_mms: Equipment vibration mm/s. Safe < 7.5
        - airflow_ms: Ventilation airflow m/s. Minimum 0.5
        - oxygen_pct: Oxygen percentage. Minimum 19.5%
        - ppe_violations_24h: PPE violations in past 24 hours
        - incidents_30d: Historical incidents in 30 days
        - equipment_health_score: 0-100 score
        - worker_fatigue_score: 0-100 (higher = more fatigued)
        - shift_hours: Hours into current shift
        - zone_id: Mine zone identifier (1-8)
        - hour_of_day: 0-23
        
    Labels:
        - risk_level: Low (0), Medium (1), High (2), Critical (3)
    """
    
    data = []
    
    for _ in range(n_samples):
        # Randomly select a scenario type
        scenario = random.choices(
            ['normal', 'elevated_gas', 'equipment_issue', 'ppe_violation', 
             'multiple_hazards', 'critical_emergency'],
            weights=[40, 20, 15, 10, 10, 5]
        )[0]
        
        zone_id = random.randint(1, 8)
        hour_of_day = random.randint(0, 23)
        shift_hours = random.uniform(0, 12)
        
        if scenario == 'normal':
            methane_ppm = np.random.normal(2000, 500)          # ~0.2%, well safe
            co_ppm = np.random.normal(8, 3)                     # well safe
            temperature_c = np.random.normal(28, 2)            # safe
            humidity_pct = np.random.normal(60, 10)
            vibration_mms = np.random.normal(2.0, 0.5)        # safe
            airflow_ms = np.random.normal(1.5, 0.3)           # good
            oxygen_pct = np.random.normal(20.5, 0.3)
            ppe_violations_24h = random.randint(0, 1)
            incidents_30d = random.randint(0, 1)
            equipment_health = np.random.normal(85, 8)
            worker_fatigue = np.random.normal(25, 10)
            risk_level = 0  # Low
            
        elif scenario == 'elevated_gas':
            methane_ppm = np.random.normal(9000, 1500)         # ~0.9%, warning zone
            co_ppm = np.random.normal(30, 8)                    # moderate
            temperature_c = np.random.normal(30, 2)
            humidity_pct = np.random.normal(65, 10)
            vibration_mms = np.random.normal(3.0, 0.8)
            airflow_ms = np.random.normal(0.8, 0.2)            # lower airflow
            oxygen_pct = np.random.normal(20.0, 0.4)
            ppe_violations_24h = random.randint(0, 2)
            incidents_30d = random.randint(0, 3)
            equipment_health = np.random.normal(75, 10)
            worker_fatigue = np.random.normal(40, 15)
            risk_level = random.choices([1, 2], weights=[60, 40])[0]  # Medium/High
            
        elif scenario == 'equipment_issue':
            methane_ppm = np.random.normal(3000, 1000)
            co_ppm = np.random.normal(15, 5)
            temperature_c = np.random.normal(35, 3)            # elevated (equipment heat)
            humidity_pct = np.random.normal(55, 10)
            vibration_mms = np.random.normal(9.0, 2.0)        # above 7.5 threshold
            airflow_ms = np.random.normal(1.2, 0.4)
            oxygen_pct = np.random.normal(20.2, 0.3)
            ppe_violations_24h = random.randint(0, 3)
            incidents_30d = random.randint(1, 5)
            equipment_health = np.random.normal(45, 15)        # low health
            worker_fatigue = np.random.normal(50, 15)
            risk_level = random.choices([1, 2], weights=[30, 70])[0]  # High
            
        elif scenario == 'ppe_violation':
            methane_ppm = np.random.normal(2500, 800)
            co_ppm = np.random.normal(12, 4)
            temperature_c = np.random.normal(29, 2)
            humidity_pct = np.random.normal(60, 10)
            vibration_mms = np.random.normal(2.5, 0.8)
            airflow_ms = np.random.normal(1.3, 0.3)
            oxygen_pct = np.random.normal(20.4, 0.3)
            ppe_violations_24h = random.randint(3, 8)          # many violations
            incidents_30d = random.randint(1, 4)
            equipment_health = np.random.normal(70, 10)
            worker_fatigue = np.random.normal(45, 15)
            risk_level = random.choices([1, 2], weights=[50, 50])[0]
            
        elif scenario == 'multiple_hazards':
            methane_ppm = np.random.normal(11000, 2000)        # near danger
            co_ppm = np.random.normal(42, 8)                   # elevated
            temperature_c = np.random.normal(34, 2)
            humidity_pct = np.random.normal(70, 10)
            vibration_mms = np.random.normal(7.0, 1.5)        # near threshold
            airflow_ms = np.random.normal(0.6, 0.15)          # barely adequate
            oxygen_pct = np.random.normal(19.8, 0.4)          # near minimum
            ppe_violations_24h = random.randint(4, 10)
            incidents_30d = random.randint(3, 8)
            equipment_health = np.random.normal(55, 10)
            worker_fatigue = np.random.normal(65, 15)
            risk_level = random.choices([2, 3], weights=[40, 60])[0]  # High/Critical
            
        else:  # critical_emergency
            methane_ppm = np.random.normal(15000, 3000)        # > 1.25%, critical
            co_ppm = np.random.normal(65, 15)                  # > 50ppm, critical
            temperature_c = np.random.normal(38, 3)
            humidity_pct = np.random.normal(80, 10)
            vibration_mms = np.random.normal(12.0, 3.0)       # very high
            airflow_ms = np.random.normal(0.3, 0.1)           # insufficient
            oxygen_pct = np.random.normal(19.0, 0.5)          # below minimum
            ppe_violations_24h = random.randint(6, 15)
            incidents_30d = random.randint(5, 12)
            equipment_health = np.random.normal(30, 10)
            worker_fatigue = np.random.normal(80, 15)
            risk_level = 3  # Critical
        
        # Apply realistic bounds
        methane_ppm = max(0, methane_ppm)
        co_ppm = max(0, co_ppm)
        temperature_c = max(20, min(45, temperature_c))
        humidity_pct = max(20, min(100, humidity_pct))
        vibration_mms = max(0, vibration_mms)
        airflow_ms = max(0.1, airflow_ms)
        oxygen_pct = max(17, min(21, oxygen_pct))
        ppe_violations_24h = max(0, min(20, ppe_violations_24h))
        incidents_30d = max(0, min(20, incidents_30d))
        equipment_health = max(0, min(100, equipment_health))
        worker_fatigue = max(0, min(100, worker_fatigue))
        
        data.append({
            'methane_ppm': round(methane_ppm, 1),
            'co_ppm': round(co_ppm, 1),
            'temperature_c': round(temperature_c, 1),
            'humidity_pct': round(humidity_pct, 1),
            'vibration_mms': round(vibration_mms, 2),
            'airflow_ms': round(airflow_ms, 2),
            'oxygen_pct': round(oxygen_pct, 2),
            'ppe_violations_24h': int(ppe_violations_24h),
            'incidents_30d': int(incidents_30d),
            'equipment_health_score': round(equipment_health, 1),
            'worker_fatigue_score': round(worker_fatigue, 1),
            'shift_hours': round(shift_hours, 1),
            'zone_id': zone_id,
            'hour_of_day': hour_of_day,
            'risk_level': risk_level,
            'risk_label': ['Low', 'Medium', 'High', 'Critical'][risk_level],
        })
    
    df = pd.DataFrame(data)
    return df


def main():
    print("=" * 60)
    print("Coal Mine Safety Synthetic Dataset Generator")
    print("=" * 60)
    
    # Generate datasets
    print("\nGenerating training dataset (4000 samples)...")
    train_df = generate_mine_safety_dataset(4000)
    
    print("Generating test dataset (1000 samples)...")
    test_df = generate_mine_safety_dataset(1000)
    
    # Output directory
    output_dir = os.path.join(os.path.dirname(__file__))
    os.makedirs(output_dir, exist_ok=True)
    
    train_path = os.path.join(output_dir, 'mine_safety_train.csv')
    test_path = os.path.join(output_dir, 'mine_safety_test.csv')
    
    train_df.to_csv(train_path, index=False)
    test_df.to_csv(test_path, index=False)
    
    print(f"\n✓ Training data saved to: {train_path}")
    print(f"✓ Test data saved to:     {test_path}")
    
    print("\n--- Dataset Statistics ---")
    print(f"Training samples: {len(train_df)}")
    print(f"Test samples:     {len(test_df)}")
    print(f"\nClass Distribution (Training):")
    dist = train_df['risk_label'].value_counts()
    for label, count in dist.items():
        pct = count / len(train_df) * 100
        print(f"  {label:12s}: {count:5d} ({pct:.1f}%)")
    
    print(f"\nFeature Statistics (Training):")
    features = ['methane_ppm', 'co_ppm', 'temperature_c', 'vibration_mms', 'ppe_violations_24h']
    print(train_df[features].describe().round(2).to_string())
    
    return train_df, test_df


if __name__ == '__main__':
    main()

