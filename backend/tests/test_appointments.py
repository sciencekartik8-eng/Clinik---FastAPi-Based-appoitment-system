from fastapi.testclient import TestClient
from  app.main import app


client = TestClient(app)

def test_get_appointments_without_authentication():
    response = client.get("/appointments/my")

    assert response.status_code in [401, 403]  # Depending on your authentication setupJ

def test_patient_can_access_own_appointments(
    authenticated_patient_client,
):
    response = authenticated_patient_client.get(
        "/appointments/my"
    )

    assert response.status_code == 200
    assert response.json() == []


# ```python
def test_patient_can_book_appointment(
    authenticated_patient_client,
    doctor_and_availability,
):
    availability = doctor_and_availability["availability"]

    response = authenticated_patient_client.post(
        "/appointments",
        json={
            "availability_id": availability.id,
            "appointment_date": "2026-10-15",
            "start_time": "10:00:00",
            "end_time": "10:30:00",
        },
    )

    assert response.status_code == 201
    assert response.json()["status"].upper() == "BOOKED"


def test_patient_cannot_book_overlapping_appointment(
    authenticated_patient_client,
    doctor_and_availability,
):
    availability = doctor_and_availability["availability"]

    payload = {
        "availability_id": availability.id,
        "appointment_date": "2026-10-15",
        "start_time": "10:00:00",
        "end_time": "10:30:00",
    }

    first = authenticated_patient_client.post(
        "/appointments",
        json=payload,
    )
    assert first.status_code == 201

    second = authenticated_patient_client.post(
        "/appointments",
        json={
            **payload,
            "start_time": "10:15:00",
            "end_time": "10:45:00",
        },
    )

    assert second.status_code == 409
