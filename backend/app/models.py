from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base


def utcnow():
    return datetime.now(timezone.utc)


class SensorReading(Base):
    __tablename__ = "sensor_readings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[str] = mapped_column(String(100), index=True)
    soil_moisture: Mapped[float] = mapped_column(Float)
    temperature: Mapped[float] = mapped_column(Float)
    humidity: Mapped[float] = mapped_column(Float)
    light: Mapped[float] = mapped_column(Float)
    recorded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class PlantSetting(Base):
    __tablename__ = "plant_settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    moisture_threshold: Mapped[float] = mapped_column(Float, default=35.0)
    temperature_alert: Mapped[float] = mapped_column(Float, default=38.0)
    humidity_alert: Mapped[float] = mapped_column(Float, default=25.0)
    watering_seconds: Mapped[int] = mapped_column(Integer, default=10)
    cooldown_seconds: Mapped[int] = mapped_column(Integer, default=60)


class WateringEvent(Base):
    __tablename__ = "watering_events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device_id: Mapped[str] = mapped_column(String(100), index=True)
    reason: Mapped[str] = mapped_column(String(255))
    duration_seconds: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(30), default="completed")
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)


class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    severity: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, index=True)
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)


class DeviceState(Base):
    __tablename__ = "device_states"
    device_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    pump_on: Mapped[bool] = mapped_column(Boolean, default=False)
    last_seen: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
