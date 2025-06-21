from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time

DATA_FILE = "wearable_data.csv"
MODEL = IsolationForest(contamination=0.05)
MODEL.fit(np.random.normal(loc=[80, 98], scale=[10, 1], size=(1000, 2)))

EMAIL_SENDER = "bhargavkola53@gmail.com"
EMAIL_PASSWORD = "hfdtwjscnggmlsyd"
EMAIL_RECEIVER = "220101120140@cutm.ac.in"

def send_email_alert(subject, body):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.send_message(msg)
        print("📧 Email alert sent!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

class DataHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith("wearable_data.csv"):
            df = pd.read_csv(DATA_FILE)
            if df.empty:
                return
            latest = df.iloc[-1]
            features = np.array([[latest["heart_rate"], latest["spo2"]]])
            is_anomaly = MODEL.predict(features)[0] == -1

            critical_hr = latest["heart_rate"] < 50 or latest["heart_rate"] > 130
            critical_spo2 = latest["spo2"] < 92

            if is_anomaly or critical_hr or critical_spo2:
                subject = f"🚨 Patient Alert at {datetime.now().strftime('%H:%M:%S')}"
                body = (
                    f"Heart Rate: {latest['heart_rate']} bpm\n"
                    f"SpO2: {latest['spo2']} %\n"
                    f"Anomaly: {'YES' if is_anomaly else 'NO'}\n"
                    f"Critical HR: {'YES' if critical_hr else 'NO'}\n"
                    f"Critical SpO2: {'YES' if critical_spo2 else 'NO'}"
                )
                send_email_alert(subject, body)

if __name__ == "__main__":
    event_handler = DataHandler()
    observer = Observer()
    observer.schedule(event_handler, path=os.path.dirname(os.path.abspath(DATA_FILE)), recursive=False)
    observer.start()
    print("🔍 Watching for real-time data...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
