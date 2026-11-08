from datetime import date, datetime, time 

from pydantic import BaseModel, Field,model_validator
from enum import Enum
# from pydantic import BaseModel


class AppointmentStatus(str, Enum):
    BOOKED = "BOOKED"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"


class AppointmentStatusUpdate(BaseModel):
    status: AppointmentStatus

class AppointmentCreate(BaseModel):
    availability_id: int
    appointment_date: date

    start_time: time = Field(
        ...,
        description="Start time of the appointment"
    )

    end_time: time = Field(
        ...,
        description="End time of the appointment"
    )

    @model_validator(mode="after")
    def validate_time(self):
        if self.start_time >= self.end_time:
            raise ValueError(
                "End time must be after start time"
            )

        return self


class AppointmentResponse(BaseModel):
    id: int
    patient_id: int
    doctor_id: int
    clinic_id: int
    appointment_date: date
    start_time: time
    end_time: time
    status: AppointmentStatus   
    reason: str | None
    notes: str | None
    created_at: datetime

    model_config = {
        "from_attributes": True
    }



class AppointmentStatusUpdate(BaseModel):
    appointment_date: date | None = None
    start_time: time | None = None
    end_time: time | None = None
    status: AppointmentStatus | None = None
    reason: str | None = None
    notes: str | None = None




class AppointmentStatus(str, Enum):
    BOOKED = "BOOKED"
    CONFIRMED = "CONFIRMED"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"
    NO_SHOW = "NO_SHOW"



class AppointmentStatusUpdate(BaseModel):
    status: AppointmentResponse