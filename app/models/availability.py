from datetime import date, time


from sqlalchemy import Column, Integer, Date, Time, Boolean,ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base 

class Availability(Base):
    __tablename__ = "availabilities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False)
    clinic_id: Mapped[int] = mapped_column(ForeignKey("clinics.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
#  relationships
    doctor = relationship("Doctor", back_populates="availabilities")
    clinic = relationship("Clinic", back_populates="availabilities")



    '''
    Availability #1

doctor_id = 5
clinic_id = 2
date = 2026-10-10
start_time = 10:00
end_time = 14:00

Doctor 5 is available at Clinic 2 from 10 AM to 2 PM on October 10.
    '''