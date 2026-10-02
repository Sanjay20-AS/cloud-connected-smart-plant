from datetime import datetime
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=100)
    password: str = Field(min_length=1, max_length=200)


class ReadingCreate(BaseModel):
    device_id: str = Field(min_length=1, max_length=100)
    soil_moisture: float = Field(ge=0, le=100)
    temperature: float = Field(ge=-40, le=100)
    humidity: float = Field(ge=0, le=100)
    light: float = Field(ge=0, le=100000)


class ReadingOut(ReadingCreate):
    id: int
    recorded_at: datetime

    model_config = {"from_attributes": True}


class SettingOut(BaseModel):
    moisture_threshold: float
    temperature_alert: float
    humidity_alert: float
    watering_seconds: int
    cooldown_seconds: int

    model_config = {"from_attributes": True}


class WateringOut(BaseModel):
    id: int
    device_id: str
    reason: str
    duration_seconds: int
    status: str
    started_at: datetime

    model_config = {"from_attributes": True}


class AlertOut(BaseModel):
    id: int
    severity: str
    message: str
    created_at: datetime
    acknowledged: bool

    model_config = {"from_attributes": True}


class PumpOut(BaseModel):
    device_id: str
    pump_on: bool
