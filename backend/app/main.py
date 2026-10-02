from contextlib import asynccontextmanager
from datetime import datetime, timezone
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import desc, text
from sqlalchemy.orm import Session

from .config import settings
from .database import Base, engine, get_db
from .models import Alert, DeviceState, SensorReading, WateringEvent
from .schemas import (
    AlertOut, LoginRequest, PumpOut, ReadingCreate, ReadingOut,
    SettingOut, WateringOut
)
from .security import create_token, require_auth, require_device, verify_password
from .watering import evaluate_reading, get_or_create_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Cloud Smart Plant API",
    version="1.0.0",
    description="Cloud-connected simulated IoT plant monitoring and watering API.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"name": "Cloud Smart Plant API", "version": "1.0.0", "docs": "/docs"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ready", "database": "ok"}


@app.post("/auth/login")
def login(payload: LoginRequest):
    if payload.username != settings.admin_username or not verify_password(
        payload.password, settings.admin_password
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": create_token(payload.username), "token_type": "bearer"}


@app.post("/api/v1/readings", response_model=ReadingOut)
def create_reading(
    payload: ReadingCreate,
    db: Session = Depends(get_db),
    _device=Depends(require_device),
):
    reading = SensorReading(**payload.model_dump())
    db.add(reading)
    db.commit()
    db.refresh(reading)
    evaluate_reading(db, reading)
    return reading


@app.get("/api/v1/readings/latest", response_model=ReadingOut)
def latest_reading(
    device_id: str = Query(default="virtual-plant-01"),
    db: Session = Depends(get_db),
    _user=Depends(require_auth),
):
    reading = (
        db.query(SensorReading)
        .filter(SensorReading.device_id == device_id)
        .order_by(desc(SensorReading.recorded_at))
        .first()
    )
    if not reading:
        raise HTTPException(status_code=404, detail="No readings found")
    return reading


@app.get("/api/v1/readings", response_model=list[ReadingOut])
def readings(
    limit: int = Query(default=50, ge=1, le=500),
    device_id: str = Query(default="virtual-plant-01"),
    db: Session = Depends(get_db),
    _user=Depends(require_auth),
):
    return (
        db.query(SensorReading)
        .filter(SensorReading.device_id == device_id)
        .order_by(desc(SensorReading.recorded_at))
        .limit(limit)
        .all()
    )


@app.get("/api/v1/settings", response_model=SettingOut)
def settings_endpoint(db: Session = Depends(get_db), _user=Depends(require_auth)):
    return get_or_create_settings(db)


@app.get("/api/v1/watering-events", response_model=list[WateringOut])
def watering_events(
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
    _user=Depends(require_auth),
):
    return db.query(WateringEvent).order_by(desc(WateringEvent.started_at)).limit(limit).all()


@app.get("/api/v1/alerts", response_model=list[AlertOut])
def alerts(
    limit: int = Query(default=50, ge=1, le=500),
    db: Session = Depends(get_db),
    _user=Depends(require_auth),
):
    return db.query(Alert).order_by(desc(Alert.created_at)).limit(limit).all()


@app.post("/api/v1/devices/{device_id}/pump", response_model=PumpOut)
def pump(
    device_id: str,
    on: bool = Query(...),
    db: Session = Depends(get_db),
    _user=Depends(require_auth),
):
    state = db.get(DeviceState, device_id)
    if state is None:
        state = DeviceState(device_id=device_id, pump_on=on)
        db.add(state)
    else:
        state.pump_on = on
        state.last_seen = datetime.now(timezone.utc)
    db.commit()
    return PumpOut(device_id=device_id, pump_on=state.pump_on)
