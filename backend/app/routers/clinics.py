from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.dependencies import require_admin
from app.db.database import get_db
from app.models.clinic import Clinic
from app.models.user import User
from app.schemas.clinic import ClinicCreate, ClinicResponse


router = APIRouter(
    prefix="/clinics",
    tags=["Clinics"],
)


@router.get("", response_model=list[ClinicResponse])
def list_clinics(db: Session = Depends(get_db)):
    return db.query(Clinic).order_by(Clinic.id).all()


@router.post(
    "",
    response_model=ClinicResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_clinic(
    clinic_data: ClinicCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    clinic = Clinic(
        name=clinic_data.name,
        address=clinic_data.address,
        phone=clinic_data.phone,
    )
    db.add(clinic)
    db.commit()
    db.refresh(clinic)
    return clinic