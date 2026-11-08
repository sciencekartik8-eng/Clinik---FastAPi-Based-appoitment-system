from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


class UserBase(BaseModel):
    name: str
    email: EmailStr
#  these two classes are inhering from UserBase class and adding additional fields to it
#  means they have access to name and email fields of UserBase class
class UserCreate(UserBase):
    name: str
    email: str
    password: str
    role: str

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)