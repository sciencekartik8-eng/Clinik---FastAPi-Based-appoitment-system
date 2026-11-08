from datetime import date, time

from pydantic import BaseModel, ConfigDict , Field

class AvailabilityBase(BaseModel):
    clinic_id: int
    date: date
    start_time: time
    end_time: time

class AvailabilityCreate(AvailabilityBase):
    pass

class AvailabilityResponse(BaseModel):
    id: int
    doctor_id: int
    clinic_id: int
    date: date
    start_time: time
    end_time: time


    model_config = ConfigDict(from_attributes=True)