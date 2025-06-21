def monitor_patient():
    model = train_model()
    data_stream = load_data_from_csv("personal_health_data.csv.csv")
    alert_count = 0

    for heart_rate, spo2 in data_stream:
        features = np.array([[heart_rate, spo2]])
        is_anomaly = model.predict(features)[0]

        critical_hr = (heart_rate < 50) or (heart_rate > 130)
        critical_spo2 = spo2 < 92

        if is_anomaly == -1 or critical_hr or critical_spo2:
            alert_count += 1
            subject = f"🚨 Patient Alert #{alert_count}"
            body = (
                f"Heart Rate: {heart_rate:.1f} bpm\n"
                f"SpO2: {spo2:.1f}%\n\n"
                f"Anomaly: {'YES' if is_anomaly == -1 else 'NO'}\n"
                f"Critical HR: {'YES' if critical_hr else 'NO'}\n"
                f"Critical SpO2: {'YES' if critical_spo2 else 'NO'}"
            )
            print(f"ALERT: {body}")
            send_email_alert(subject, body)
        else:
            print(f"✅ Normal: HR={heart_rate:.1f}, SpO2={spo2:.1f}")
