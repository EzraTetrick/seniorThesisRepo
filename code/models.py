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
    device_type: Mapped[Optional[str]] = mapped_column(String(30))
    manufacturer: Mapped[Optional[str]] = mapped_column(String(50))
    model: Mapped[Optional[str]] = mapped_column(String(50))
    serial_number: Mapped[Optional[str]] = mapped_column(String(50))
    location: Mapped[Optional[str]] = mapped_column(String(50))
    contact: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[Optional[str]] = mapped_column(String(50))
    snmp_template_id: Mapped[int] = mapped_column(Integer, ForeignKey("SNMP_Templates.template_id"))
    monitoring_template_id: Mapped[int] = mapped_column(Integer, ForeignKey("Monitoring_Templates.template_id"))

    def __repr__(self) -> str:
        return f"<Device(hostname='{self.hostname}', ip='{self.ip_address}')>"

class SNMP_Template(Base):
    __tablename__ = "SNMP_Templates"

    template_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    template_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(200))
    username: Mapped[Optional[str]] = mapped_column(String(50))
    community: Mapped[Optional[str]] = mapped_column(String(50))
    version: Mapped[str] = mapped_column(String(10), nullable=False)
    auth_pass: Mapped[Optional[str]] = mapped_column(String(50))
    priv_pass: Mapped[Optional[str]] = mapped_column(String(50))
    auth_proto: Mapped[Optional[str]] = mapped_column(String(20))
    priv_proto: Mapped[Optional[str]] = mapped_column(String(20))

    def __repr__(self) -> str:
        return f"<Template(name='{self.template_name}')>"


class Monitoring_Template(Base):
    __tablename__ = "Monitoring_Templates"

    template_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    template_name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(200))
    monitoring_interval: Mapped[int] = mapped_column(Integer)
    ping_count: Mapped[int] = mapped_column(Integer)
    timeout: Mapped[int] = mapped_column(Integer)
    retry_attempts: Mapped[int] = mapped_column(Integer)
    retry_ping_count: Mapped[int] = mapped_column(Integer)
    retry_timeout: Mapped[int] = mapped_column(Integer)
    retry_interval: Mapped[int] = mapped_column(Integer)
    retry_before_alert: Mapped[int] = mapped_column(Integer)

    def __repr__(self) -> str:
        return f"<Template(name='{self.template_name}')>"
