import numpy as np
import pandas as pd
import time
from sklearn.ensemble import IsolationForest

# Simulate real-time wearable data (heart rate, SpO2)
def simulate_wearable_data():
    """Generate fake patient data with occasional anomalies."""
    while True:
        # Normal baseline (HR: 60-100, SpO2: 95-100%)
        heart_rate = np.random.normal(loc=80, scale=10)
        spo2 = np.random.normal(loc=98, scale=1)
        
        # Inject anomalies 5% of the time
        if np.random.random() < 0.05:
            heart_rate = np.random.choice([40, 150])  # Bradycardia or Tachycardia
            spo2 = np.random.uniform(85, 90)         # Hypoxia
        
        yield (heart_rate, spo2)
        time.sleep(1)  # Simulate 1-second delay between readings