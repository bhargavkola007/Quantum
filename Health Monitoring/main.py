import numpy as np
import time
from sklearn.ensemble import IsolationForest
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- SMTP Email Configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "bhargavkola53@gmail.com"  # Your email
EMAIL_PASSWORD = "hfdtwjscnggmlsyd"  # Google App Password
EMAIL_RECEIVER = "220101120140@cutm.ac.in"  # Admin email

def send_email_alert(subject, body):
    """Send an email alert via SMTP."""
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Enable TLS encryption
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("📧 Email alert sent!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# --- Simulate Wearable Data ---
def simulate_wearable_data():
    """Generate fake patient data with occasional anomalies."""
    while True:
        heart_rate = np.random.normal(loc=80, scale=10)
        spo2 = np.random.normal(loc=98, scale=1)
        
        # Inject anomalies 5% of the time
        if np.random.random() < 0.05:
            heart_rate = np.random.choice([40, 150])  # Abnormal HR
            spo2 = np.random.uniform(85, 90)         # Low SpO2
        
        yield (heart_rate, spo2)
        time.sleep(1)  # Simulate 1-second delay

# --- Anomaly Detection Model ---
def train_model():
    # Historical "normal" data (HR: 60-100, SpO2: 95-100%)
    X_normal = np.random.normal(loc=[80, 98], scale=[10, 1], size=(1000, 2))
    model = IsolationForest(contamination=0.05)  # 5% anomaly rate
    model.fit(X_normal)
    return model

# --- Real-Time Monitoring ---
def monitor_patient():
    model = train_model()
    data_stream = simulate_wearable_data()
    alert_count = 0
    
    while True:
        heart_rate, spo2 = next(data_stream)
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
                f"Heart Rate: {heart_rate:.1f} bpm\n"
                f"SpO2: {spo2:.1f}%\n\n"
                f"Anomaly: {'YES' if is_anomaly == -1 else 'NO'}\n"
                f"Critical HR: {'YES' if critical_hr else 'NO'}\n"
                f"Critical SpO2: {'YES' if critical_spo2 else 'NO'}"
            )
            
            print(f"ALERT: {body}")
            send_email_alert(subject, body)  # Send email
        
        else:
            print(f"✅ Normal: HR={heart_rate:.1f}, SpO2={spo2:.1f}")

if __name__ == "__main__":
    monitor_patient()