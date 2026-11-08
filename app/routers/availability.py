from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_doctor
from app.db.database import get_db
from app.models.availability import Availability
from app.models.clinic import Clinic
from app.models.doctor import Doctor
from app.models.user import User
from app.schemas.availability import AvailabilityCreate, AvailabilityResponse


router = APIRouter(
    prefix="/availability",
    tags=["Availability"]
)

@router.post("", response_model=AvailabilityResponse, status_code=status.HTTP_201_CREATED)
def create_availability(
    availability_data: AvailabilityCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_doctor)
):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Doctor profile is not linked to the current user"
        )
    clinic = db.query(Clinic).filter(Clinic.id == availability_data.clinic_id).first()
    if not clinic:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Clinic not found"
        )
    if availability_data.start_time >= availability_data.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Start time must be before end time"
        )
    availability = Availability(
        doctor_id=doctor.id,
        clinic_id=availability_data.clinic_id,
        date=availability_data.date,
        start_time=availability_data.start_time,
        end_time=availability_data.end_time,
    )


    db.add(availability)
    db.commit()
    db.refresh(availability)


    
    return availability
