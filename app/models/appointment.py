"""id
patient_id
doctor_id
clinic_id
appointment_date
start_time
end_time
status
reason
notes
created_at
updated_at"""


from datetime import datetime, date, time
from sqlalchemy import Column, Integer, Date, Time, String, ForeignKey, DateTime, CheckConstraint,Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.database import Base

class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    patient_id: Mapped[int] = mapped_column(ForeignKey("patients.id"), nullable=False)
    doctor_id: Mapped[int] = mapped_column(ForeignKey("doctors.id"), nullable=False)
    clinic_id: Mapped[int] = mapped_column(ForeignKey("clinics.id"), nullable=False)
    appointment_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="scheduled", nullable=False)  # scheduled, completed, canceled
    status_check = CheckConstraint(status.in_(["scheduled", "completed", "canceled", "Booked"]), name="status_check")
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    doctor = relationship("Doctor", back_populates="appointments")
    clinic = relationship("Clinic", back_populates="appointments")

    status_check = CheckConstraint(status.in_(["scheduled", "completed", "canceled", "Booked"]), name="status_check")

    __table_args__ = (
    CheckConstraint(
        "start_time < end_time",
        name="check_start_end_time"
    ),
    CheckConstraint(
        "status IN ('BOOKED', 'CONFIRMED', 'COMPLETED', 'CANCELLED', 'NO_SHOW')",
        name="status_check"
    ),
    Index(
        "idx_appointment_doctor_date",
        "doctor_id",
        "appointment_date"
    ),
    Index(
        "idx_appointment_patient_date",
        "patient_id",
        "appointment_date"
    ),
)