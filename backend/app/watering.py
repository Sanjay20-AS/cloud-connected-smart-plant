from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session

from .config import settings
from .models import (
    Alert,
    DeviceState,
    PlantSetting,
    SensorReading,
    WateringEvent,
)


def utc_now():
    """
    Return a timezone-aware UTC datetime.
    """
    return datetime.now(timezone.utc)


def make_aware(dt):
    """
    Convert database datetime to timezone-aware UTC.

    SQLite may return datetime values without timezone information.
    """
    if dt is None:
        return None

    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)

    return dt.astimezone(timezone.utc)


def get_or_create_settings(db: Session) -> PlantSetting:
    settings = db.query(PlantSetting).first()

    if settings is None:
        settings = PlantSetting(
            moisture_threshold=35.0,
            temperature_alert=38.0,
            humidity_alert=25.0,
            watering_duration_seconds=10,
            cooldown_seconds=60,
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)

    return settings


def evaluate_reading(db: Session, reading: SensorReading):
    """
    Evaluate a new sensor reading and decide whether watering
    or an alert should be triggered.
    """

    settings = get_or_create_settings(db)

    now = utc_now()

    # ---------------------------------------------------------
    # Update device state
    # ---------------------------------------------------------

    device = (
        db.query(DeviceState)
        .filter(DeviceState.device_id == reading.device_id)
        .first()
    )

    if device is None:
        device = DeviceState(
            device_id=reading.device_id,
            pump_on=False,
            last_seen=now,
        )
        db.add(device)
    else:
        device.last_seen = now

    db.flush()

    # ---------------------------------------------------------
    # Check previous watering event
    # ---------------------------------------------------------

    latest = (
        db.query(WateringEvent)
        .filter(WateringEvent.device_id == reading.device_id)
        .order_by(WateringEvent.started_at.desc())
        .first()
    )

    cooldown_finished = True

    if latest is not None:
        latest_started_at = make_aware(latest.started_at)

        cooldown_finished = (
            now - latest_started_at
        ) >= timedelta(seconds=settings.cooldown_seconds)

    # ---------------------------------------------------------
    # Automatic watering
    # ---------------------------------------------------------

    should_water = (
    reading.soil_moisture < settings.moisture_threshold
    and not device.pump_on
    and cooldown_finished
    )

    print(
        f"[WATERING CHECK] "
        f"moisture={reading.soil_moisture}, "
        f"threshold={settings.moisture_threshold}, "
        f"pump_on={device.pump_on}, "
        f"cooldown_finished={cooldown_finished}, "
        f"should_water={should_water}"
    )

    if should_water:

        event = WateringEvent(
            device_id=reading.device_id,
            reason=(
                f"Soil moisture {reading.soil_moisture:.1f}% "
                f"is below threshold "
                f"{settings.moisture_threshold:.1f}%"
            ),
            duration_seconds=settings.watering_duration_seconds,
            status="completed",
            started_at=now,
        )

        db.add(event)

        # Virtual pump
        device.pump_on = True

        db.flush()

        # For the simulator we immediately complete the watering cycle.
        device.pump_on = False

        alert = Alert(
            severity="info",
            message=(
                f"Automatic watering triggered for "
                f"{reading.device_id}. "
                f"Duration: "
                f"{settings.watering_duration_seconds} seconds."
            ),
            created_at=now,
            acknowledged=False,
        )

        db.add(alert)

    # ---------------------------------------------------------
    # High temperature alert
    # ---------------------------------------------------------

    if reading.temperature >= settings.temperature_alert:

        alert = Alert(
            severity="warning",
            message=(
                f"High temperature detected: "
                f"{reading.temperature:.1f}°C"
            ),
            created_at=now,
            acknowledged=False,
        )

        db.add(alert)

    # ---------------------------------------------------------
    # Low humidity alert
    # ---------------------------------------------------------

    if reading.humidity <= settings.humidity_alert:

        alert = Alert(
            severity="warning",
            message=(
                f"Low humidity detected: "
                f"{reading.humidity:.1f}%"
            ),
            created_at=now,
            acknowledged=False,
        )

        db.add(alert)

    db.commit()