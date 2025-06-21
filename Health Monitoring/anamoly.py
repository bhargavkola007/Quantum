# Train a simple anomaly detection model (pretend we have historical data)
def train_model():
    # Historical "normal" data (HR: 60-100, SpO2: 95-100%)
    X_normal = np.random.normal(loc=[80, 98], scale=[10, 1], size=(1000, 2))
    model = IsolationForest(contamination=0.05)  # 5% anomaly rate
    model.fit(X_normal)
    return model