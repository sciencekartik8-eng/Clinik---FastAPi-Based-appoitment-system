from pydantic import BaseModel, ConfigDict , Field

class DoctorBase(BaseModel):
    specialization: str
    qualification: str = "MBBS"
    experience_years: int = Field(default=0, ge=0,le=70, description="Years of experience must be a non-negative integer")
    license_number: str 
    consultation_fee: int = 1000


class DoctorCreate(DoctorBase):
    pass


class DoctorResponse(DoctorBase):   
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)