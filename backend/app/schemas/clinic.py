from pydantic import BaseModel


class ClinicBase(BaseModel):
    name: str
    address: str
    phone: str


class ClinicCreate(ClinicBase):
    pass


class ClinicResponse(ClinicBase):
    id: int

    model_config = {
        "from_attributes": True
    }