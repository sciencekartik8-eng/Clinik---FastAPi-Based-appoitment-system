import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.database import Base, get_db
from app.core.security import create_access_token

# Import all models so their tables register with Base.metadata
from app.models.user import User
from app.models.patient import Patient
from app.models.doctor import Doctor
from app.models.clinic import Clinic
from app.models.availability import Availability
from app.models.appointment import Appointment


TEST_DATABASE_URL = "sqlite:///./test_clinic.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

@pytest.fixture
def patient_token(db_session):
    user = User(
        name="Test Patient",
        email="testpatient@example.com",
        password_hash="unused-test-hash",
        role="Patient",
        is_active=True,
    )

    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    patient = Patient(user_id=user.id)
    db_session.add(patient)
    db_session.commit()

    return create_access_token(
        data={"sub": str(user.id)}
    )


@pytest.fixture
def authenticated_patient_client(client, patient_token):
    client.headers.update({
        "Authorization": f"Bearer {patient_token}"
    })
    return client

from datetime import date, time

# Add these fixtures to conftest.py


@pytest.fixture
def doctor_and_availability(db_session):
    doctor_user = User(
        name="Test Doctor",
        email="testdoctor@example.com",
        password_hash="unused-test-hash",
        role="Doctor",
        is_active=True,
    )

    db_session.add(doctor_user)
    db_session.commit()
    db_session.refresh(doctor_user)

    doctor = Doctor(
        user_id=doctor_user.id,
        specialization="General Medicine",
        qualification="MBBS",
        experience_years=5,
        license_number="TEST-LIC-001",
        consultation_fee=500,
    )

    clinic = Clinic(
        name="Test Clinic",
        address="Test Address",
        phone="9999999999",
    )

    db_session.add_all([doctor, clinic])
    db_session.commit()
    db_session.refresh(doctor)
    db_session.refresh(clinic)

    availability = Availability(
        doctor_id=doctor.id,
        clinic_id=clinic.id,
        date=date(2026, 10, 15),
        start_time=time(9, 0),
        end_time=time(13, 0),
        is_available=True,
    )

    db_session.add(availability)
    db_session.commit()
    db_session.refresh(availability)

    return {
        "doctor": doctor,
        "clinic": clinic,
        "availability": availability,
    }


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

    first_response = authenticated_patient_client.post(
        "/appointments",
        json=payload,
    )

    assert first_response.status_code == 201

    overlapping_payload = {
        **payload,
        "start_time": "10:15:00",
        "end_time": "10:45:00",
    }

    second_response = authenticated_patient_client.post(
        "/appointments",
        json=overlapping_payload,
    )

    assert second_response.status_code == 409

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

    data = response.json()

    assert data["doctor_id"] == doctor_and_availability["doctor"].id
    assert data["clinic_id"] == doctor_and_availability["clinic"].id
    assert data["status"].upper() == "BOOKED"

def test_patient_cannot_book_outside_availability(
    authenticated_patient_client,
    doctor_and_availability,
):
    availability = doctor_and_availability["availability"]

    response = authenticated_patient_client.post(
        "/appointments",
        json={
            "availability_id": availability.id,
            "appointment_date": "2026-10-15",
            "start_time": "13:30:00",
            "end_time": "14:00:00",
        },
    )

    assert response.status_code == 400