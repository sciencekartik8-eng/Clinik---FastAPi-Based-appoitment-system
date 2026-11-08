from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    specialization: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    qualification: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    experience_years: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0
    )

    license_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    consultation_fee: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    user = relationship(
        "User",
        back_populates="doctor"
    )

    appointments = relationship(
        "Appointment",
        back_populates="doctor"
    )

    availabilities = relationship(
        "Availability",
        back_populates="doctor",
        cascade="all, delete-orphan"
    )