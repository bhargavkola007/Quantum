import numpy as np
import time
from sklearn.ensemble import IsolationForest
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pygatt  # For Bluetooth devices
import requests  # For WiFi/API-connected devices
from threading import Thread
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- SMTP Email Configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "bhargavkola53@gmail.com"  # Your email
EMAIL_PASSWORD = "hfdtwjscnggmlsyd"  # Google App Password
EMAIL_RECEIVER = "220101120140@cutm.ac.in"  # Admin email

# --- Device Configuration ---
BLUETOOTH_DEVICE_MAC = "00:11:22:33:44:55"  # Replace with your device MAC
HEART_RATE_UUID = "00002a37-0000-1000-8000-00805f9b34fb"  # Standard HR UUID
SPO2_UUID = "00002a5e-0000-1000-8000-00805f9b34fb"       # Standard SpO2 UUID

# For API-connected devices
API_ENDPOINT = "https://api.yourwearable.com/v1/data"
API_KEY = "your_api_key_here"

def send_email_alert(subject, body):
    """Send an email alert via SMTP."""
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        logger.info("Email alert sent successfully")
    except Exception as e:
        logger.error(f"Failed to send email: {e}")

class BluetoothConnection:
    """Handles Bluetooth Low Energy connections"""
    def __init__(self):
        self.adapter = pygatt.GATTToolBackend()
        self.device = None
        
    def connect(self):
        try:
            self.adapter.start()
            self.device = self.adapter.connect(BLUETOOTH_DEVICE_MAC)
            logger.info("Bluetooth device connected successfully")
            return True
        except Exception as e:
            logger.error(f"Bluetooth connection failed: {e}")
            return False
    
    def read_characteristic(self, uuid):
        try:
            value = self.device.char_read(uuid)
            return self._parse_ble_data(value, uuid)
        except Exception as e:
            logger.error(f"Failed to read characteristic {uuid}: {e}")
            return None
    
    def _parse_ble_data(self, value, uuid):
        """Parse BLE data according to standard formats"""
        if uuid == HEART_RATE_UUID:
            # Heart Rate Measurement (uint8, bpm)
            return int(value[1])
        elif uuid == SPO2_UUID:
            # SpO2 Measurement (uint8, percentage)
            return int(value[0])
        return None
    
    def disconnect(self):
        try:
            if self.device:
                self.device.disconnect()
            self.adapter.stop()
        except Exception as e:
            logger.error(f"Error during disconnection: {e}")

class WearableAPI:
    """Handles WiFi/API-connected devices"""
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {API_KEY}"})
    
    def get_data(self):
        try:
            response = self.session.get(API_ENDPOINT, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('heart_rate'), data.get('spo2')
        except Exception as e:
            logger.error(f"API request failed: {e}")
        return None, None

def train_model():
    """Train the anomaly detection model"""
    # Historical "normal" data (HR: 60-100, SpO2: 95-100%)
    X_normal = np.random.normal(loc=[80, 98], scale=[10, 1], size=(1000, 2))
    model = IsolationForest(contamination=0.05, random_state=42)
    model.fit(X_normal)
    logger.info("Anomaly detection model trained successfully")
    return model

def monitor_patient():
    """Main monitoring function"""
    model = train_model()
    bluetooth = BluetoothConnection()
    api = WearableAPI()
    alert_count = 0
    
    # Try Bluetooth first
    use_bluetooth = bluetooth.connect()
    
    while True:
        try:
            # Get data from the preferred source
            if use_bluetooth:
                heart_rate = bluetooth.read_characteristic(HEART_RATE_UUID)
                spo2 = bluetooth.read_characteristic(SPO2_UUID)
            else:
                heart_rate, spo2 = api.get_data()
            
            # Fallback to API if Bluetooth fails
            if (heart_rate is None or spo2 is None) and use_bluetooth:
                logger.warning("Falling back to API connection")
                use_bluetooth = False
                heart_rate, spo2 = api.get_data()
            
            # If still no data, wait and retry
            if heart_rate is None or spo2 is None:
                logger.warning("No data received from any source")
                time.sleep(5)
                continue
            
            logger.info(f"Received data - HR: {heart_rate}, SpO2: {spo2}")
            
            # Prepare features for anomaly detection
            features = np.array([[heart_rate, spo2]])
            
            # Predict anomaly
            is_anomaly = model.predict(features)[0]
            
            # Rule-based checks
            critical_hr = (heart_rate < 50) or (heart_rate > 130)
            critical_spo2 = spo2 < 92
            
            # Trigger alerts
            if is_anomaly == -1 or critical_hr or critical_spo2:
                alert_count += 1
                subject = f"🚨 Patient Alert #{alert_count}"
                body = (
                    f"Critical health metrics detected!\n\n"
                    f"Heart Rate: {heart_rate} bpm\n"
                    f"SpO2: {spo2}%\n\n"
                    f"Anomaly: {'YES' if is_anomaly == -1 else 'NO'}\n"
                    f"Critical HR: {'YES' if critical_hr else 'NO'}\n"
                    f"Critical SpO2: {'YES' if critical_spo2 else 'NO'}"
                )
                
                logger.warning(f"ALERT: {body}")
                # Send email in a separate thread to avoid blocking
                Thread(target=send_email_alert, args=(subject, body)).start()
            
            time.sleep(1)  # Adjust based on your device's update frequency
            
        except KeyboardInterrupt:
            logger.info("Shutting down monitoring system...")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            time.sleep(5)  # Wait before retrying
    
    # Clean up
    if use_bluetooth:
        bluetooth.disconnect()

if __name__ == "__main__":
    monitor_patient()