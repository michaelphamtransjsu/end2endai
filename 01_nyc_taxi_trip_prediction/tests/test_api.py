from fastapi.testclient import TestClient
from taxi_duration.api import app
client=TestClient(app)
PAYLOAD={"pickup_datetime":"2016-06-15T17:30:00","pickup_latitude":40.758,"pickup_longitude":-73.9855,"dropoff_latitude":40.7306,"dropoff_longitude":-73.9352,"passenger_count":1}
def test_health():
    r=client.get('/health'); assert r.status_code==200 and r.json()["model_available"]
def test_predict():
    r=client.post('/predict',json=PAYLOAD); assert r.status_code==200 and r.json()["predicted_duration_seconds"]>0
def test_ui(): assert "NYC taxi duration" in client.get('/').text
def test_invalid_payload(): assert client.post('/predict',json={**PAYLOAD,"passenger_count":0}).status_code==422
