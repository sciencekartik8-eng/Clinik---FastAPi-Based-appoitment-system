from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.appointment import Appointment
from app.models.availability import Availability
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.appointment import AppointmentCreate, AppointmentResponse, AppointmentStatusUpdate
# from app.models.appointment import Appointment
from app.models.patient import Patient




router = APIRouter(
    prefix="/appointments",
    tags=["Appointments"]
)


@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
def create_appointment(
    appointment_data: AppointmentCreate,
    db: Session = Depends(get_db),  current_user: User = Depends(get_current_user)
):

    #  check role 
    if current_user.role.lower() != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can create appointments"
        )

    #  finds the patient linked to the current user
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Patient profile not found "
        )   

    if appointment_data.start_time >= appointment_data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment end time must be after the start time"
        )

    # Find the doctor's availability for the requested appointment.
    availability = db.query(Availability).filter(
        Availability.id == appointment_data.availability_id
    ).first()


    if not availability:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor's availability not found"
        )

    #  validate date and time of the appointment against the doctor's availability
    if appointment_data.appointment_date != availability.date:
       raise HTTPException(
         status_code=status.HTTP_400_BAD_REQUEST,
          detail="Appointment date does not match doctor's availability"
    )

    if appointment_data.start_time < availability.start_time or appointment_data.end_time > availability.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Appointment time is outside the doctor's availability"
        )


    doctor_id = availability.doctor_id
    clinic_id = availability.clinic_id

#  check if the doctor already has an appointment during the requested time slot

    existing_appointment = db.query(Appointment).filter(
        Appointment.doctor_id == doctor_id,
        Appointment.clinic_id == clinic_id,
        Appointment.appointment_date == appointment_data.appointment_date,
        Appointment.start_time < appointment_data.end_time,
        Appointment.end_time > appointment_data.start_time
    ).first()
    if existing_appointment:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,  # the request is valid but it is conflicting with the current state of the server
            detail="The doctor already has an appointment during this time slot"
        )

    #  create the appointment
    appointment = Appointment(
    patient_id=patient.id,
    doctor_id=doctor_id,
    clinic_id=clinic_id,
    appointment_date=appointment_data.appointment_date,
    start_time=appointment_data.start_time,
    end_time=appointment_data.end_time,
    status="Booked"
    )


# save
    db.add(appointment)
    db.commit()
    db.refresh(appointment)

    return appointment



# Get all appointments for the current user (patient).
@router.get("/my", response_model=list[AppointmentResponse])
def list_my_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.lower() != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can view their appointments"
        )
    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )

    appointments = db.query(Appointment).filter(
        Appointment.patient_id == patient.id).order_by(Appointment.appointment_date.desc()).all()
    return appointments

# get all appointments for a specific doctor
@router.get("/doctor", response_model=list[AppointmentResponse])
def list_doctor_appointments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role.lower() != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view their appointments"
        )

    
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can view their appointments"
        )

    appointments = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id).order_by(Appointment.appointment_date.desc()).all()
    return appointments


    
#  update or delete an appointment
@router.patch("/{appointment_id}/cancel", response_model=AppointmentResponse)
def cancel_appointment(
    appointment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):    
    if current_user.role.lower() != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can cancel their appointments"
        )


    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )

    patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if not patient :
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient profile not found"
        )
    if appointment.patient_id != patient.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to cancel this appointment"
        )

    appointment.status = "Cancelled"
    db.commit()
    db.refresh(appointment)
    return appointment


 

@router.patch("/{appointment_id}/status", response_model=AppointmentResponse)
def update_appointment_Status(
    appointment_id: int,
    status_update: AppointmentStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # only doctors can update the status of an appointment
    if current_user.role.lower() != "doctor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only doctors can update the status of an appointment"
        )

    # find the doctor linked to the current user
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()

    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Doctor profile not found"
        )

    #  find the appointment by ID
    appointment = db.query(Appointment).filter(Appointment.id == appointment_id).first()
    if not appointment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Appointment not found"
        )


    #  check if the appointment belongs to the doctor
    if appointment.doctor_id != doctor.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to update the status of this appointment"
        )

    # Validate and apply the requested status transition.
    allowed_statuses = {
        "BOOKED",
        "CONFIRMED",
        "COMPLETED",
        "CANCELLED",
        "NO_SHOW"
    }

    status_transitions = {
        "BOOKED": {"CONFIRMED", "CANCELLED"},
        "CONFIRMED": {"COMPLETED", "CANCELLED", "NO_SHOW"},
        "COMPLETED": set(),
        "CANCELLED": set(),
        "NO_SHOW": set(),
    }

    new_status = status_update.status.upper()

    if new_status not in allowed_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid appointment status"
        )

    current_status = appointment.status.upper()

    if new_status not in status_transitions[current_status]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot change appointment from {current_status} to {new_status}"
        )

    try:
        appointment.status = new_status
        db.commit()
        db.refresh(appointment)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update appointment status due to a database integrity error"
        )
    return appointment

