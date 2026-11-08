from pydantic import BaseModel, ConfigDict

class PatientBase(BaseModel):
    phone: str | None = None
    address: str | None = None

class PatientCreate(PatientBase):
    pass
class PatientResponse(PatientBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)





