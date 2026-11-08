from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.db.database import get_db

from app.models.patient import Patient
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientResponse


router = APIRouter(
    prefix="/patients",
    tags=["Patients"]
)

@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if the current user is an admin or a patient
    if  current_user.role.lower() != "patient":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only patients can create patient profiles"
        )

    # Check if a patient profile already exists for the given user_id
    existing_patient = db.query(Patient).filter(Patient.user_id == current_user.id).first()
    if existing_patient:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A patient profile already exists for this user"
        )

    new_patient = Patient(user_id=current_user.id)
    db.add(new_patient)
    try:
        db.commit()
        db.refresh(new_patient)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create patient profile due to database integrity error"
        )

    return new_patient