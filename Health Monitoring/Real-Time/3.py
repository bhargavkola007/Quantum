import healthkit  # For iOS
# or
from google.oauth2 import service_account
from googleapiclient.discovery import build

def get_health_data():
    # iOS example
    hk = healthkit.HealthKit()
    heart_rate = hk.get_latest_heart_rate()
    spo2 = hk.get_latest_blood_oxygen()
    return heart_rate, spo2