import numpy as np
import time
import pandas as pd
from sklearn.ensemble import IsolationForest
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# --- Configuration ---
DATA_FILE = "wearable_data.csv"  # File to store the dataset
INTERVAL_SECONDS = 30           # Generate data every 30 seconds

# --- SMTP Email Configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "bhargavkola53@gmail.com"  # Replace with your email
EMAIL_PASSWORD = "hfdtwjscnggmlsyd"      # Replace with your app password
EMAIL_RECEIVER = "220101120140@cutm.ac.in"

# --- Helper Functions ---
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
        print("📧 Email alert sent!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def generate_data_point():
    """Generate a single data point with occasional anomalies."""
    heart_rate = np.random.normal(loc=80, scale=10)
    spo2 = np.random.normal(loc=98, scale=1)
    
    # Inject anomalies 5% of the time
    if np.random.random() < 0.05:
        heart_rate = np.random.choice([40, 150])  # Abnormal HR
        spo2 = np.random.uniform(85, 90)         # Low SpO2
    
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "heart_rate": heart_rate,
        "spo2": spo2,
        "is_anomaly": False  # Updated later by the model
    }

def train_model():
    """Train an Isolation Forest model on synthetic normal data."""
    X_normal = np.random.normal(loc=[80, 98], scale=[10, 1], size=(1000, 2))
    model = IsolationForest(contamination=0.05)
    model.fit(X_normal)
    return model

def save_to_csv(data, filename=DATA_FILE):
    """Append data to a CSV file."""
    df = pd.DataFrame([data])
    df.to_csv(filename, mode='a', header=not pd.io.common.file_exists(filename), index=False)

# --- Main Monitoring Loop ---
def monitor_patient():
    model = train_model()
    alert_count = 0
    
    while True:
        # Generate and store data
        data = generate_data_point()
        features = np.array([[data["heart_rate"], data["spo2"]]])
        
        # Predict anomaly
        is_anomaly = model.predict(features)[0]
        data["is_anomaly"] = (is_anomaly == -1)
        
        # Rule-based checks
        critical_hr = (data["heart_rate"] < 50) or (data["heart_rate"] > 130)
        critical_spo2 = data["spo2"] < 92
        
        # Save to CSV
        save_to_csv(data)
        print(f"📊 Recorded: HR={data['heart_rate']:.1f}, SpO2={data['spo2']:.1f}")
        
        # Trigger alerts
        if data["is_anomaly"] or critical_hr or critical_spo2:
            alert_count += 1
            subject = f"🚨 Patient Alert #{alert_count}"
            body = (
                f"Critical health metrics detected!\n\n"
                f"Heart Rate: {data['heart_rate']:.1f} bpm\n"
                f"SpO2: {data['spo2']:.1f}%\n\n"
                f"Anomaly: {'YES' if data['is_anomaly'] else 'NO'}\n"
                f"Critical HR: {'YES' if critical_hr else 'NO'}\n"
                f"Critical SpO2: {'YES' if critical_spo2 else 'NO'}"
            )
            send_email_alert(subject, body)
        
        # Wait for the next interval
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    monitor_patient()