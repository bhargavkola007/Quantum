# Example for Polar H10
from polar import Polar

polar = Polar()
polar.connect()

def get_real_time_data():
    data = polar.get_latest_measurement()
    return data.heart_rate, data.spo2