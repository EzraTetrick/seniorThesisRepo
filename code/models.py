# models.py
from sqlalchemy import String, Integer, Date, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import Optional
from database import Base

class Device(Base):
    __tablename__ = "Devices"

    device_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    hostname: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    ip_address: Mapped[str] = mapped_column(String(15), nullable=False)
    mac_address: Mapped[Optional[str]] = mapped_column(String(17))
    device_type: Mapped[str] = mapped_column(String(30))
    manufacturer: Mapped[Optional[str]] = mapped_column(String(50))
    model: Mapped[Optional[str]] = mapped_column(String(50))
    serial_number: Mapped[Optional[str]] = mapped_column(String(50))
    location: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[Optional[str]] = mapped_column(String(50))


    def __repr__(self) -> str:
        return f"<Device(hostname='{self.hostname}', ip='{self.ip_address}')>"