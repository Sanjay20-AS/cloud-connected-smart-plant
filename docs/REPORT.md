# Project Report
## Cloud-Connected Smart Plant Care & Watering System

### 1. Abstract

The Cloud-Connected Smart Plant Care & Watering System is a cloud-based IoT application for monitoring plant environmental conditions and automating watering decisions. Because physical IoT hardware is not required, a Python simulator acts as the sensor device and generates synthetic readings. The readings are sent to a FastAPI REST service, stored in PostgreSQL, evaluated by a watering rule engine, and displayed through a web dashboard.

### 2. Problem statement

Manual plant monitoring can result in under-watering or over-watering. A cloud-connected system can collect sensor measurements, maintain history, apply rules centrally, provide remote visibility, and support automated actuator control.

### 3. Objectives

1. Simulate IoT sensor readings.
2. Transfer sensor data using HTTP REST.
3. Store readings in a cloud database.
4. Detect dry-soil conditions.
5. Automatically create watering events.
6. Generate alerts.
7. Display current and historical readings.
8. Demonstrate authentication and secure configuration.
9. Deploy the backend and frontend to cloud platforms.
10. Provide a path to real ESP32 hardware.

### 4. Technologies

| Layer | Technology |
|---|---|
| IoT simulator | Python |
| Optional hardware | ESP32 |
| API | FastAPI |
| Database | PostgreSQL / Supabase |
| Local database | SQLite |
| Frontend | React + Vite |
| Authentication | JWT + device API key |
| Deployment | Render + Vercel/Render Static |
| Testing | Pytest |
| CI | GitHub Actions |
| Containerization | Docker |

### 5. Cloud computing concepts demonstrated

- Cloud-hosted application
- Managed relational database
- REST API
- Stateless backend service
- Environment-based configuration
- Horizontal scalability concept
- Monitoring/health endpoints
- Automated deployment
- Cloud database persistence
- Remote access
- Separation of device, application and storage layers

### 6. Data flow

1. Simulator generates sensor data.
2. Device API key authenticates the device.
3. FastAPI validates the payload.
4. Sensor reading is persisted.
5. Watering rules are evaluated.
6. A watering event is created if necessary.
7. Alert is generated.
8. Dashboard polls the API.
9. User sees current and historical information.

### 7. Database design

`SensorReading` stores time-series-like sensor observations.

`PlantSetting` stores configurable watering and alert thresholds.

`WateringEvent` records automated actuator decisions.

`Alert` records operational warnings.

`DeviceState` tracks device presence and pump state.

### 8. Algorithm

```text
receive sensor reading
        |
validate values
        |
store reading
        |
load plant settings
        |
is soil moisture below threshold?
      /   \
    no     yes
    |       |
  finish   is pump/cooldown clear?
          /       \
        no         yes
        |           |
      finish     create event
                    |
                 create alert
                    |
                run virtual pump
```

### 9. Security

The device endpoint requires a device API key. Dashboard endpoints require a JWT. Passwords are not stored directly in the application database. Secrets are environment variables and should never be committed to GitHub.

### 10. Testing

Automated tests cover health checking, login, sensor ingestion and automatic watering.

### 11. Limitations

This project uses simulated sensors and a virtual actuator. The current dashboard uses polling rather than a WebSocket/MQTT stream. Alerts are stored in the database; external email/SMS delivery can be added as a production extension.

### 12. Future enhancements

- MQTT with AWS IoT Core / Azure IoT / HiveMQ
- WebSocket dashboard
- real ESP32
- email/SMS/Telegram notifications
- weather API
- ML-based watering prediction
- multiple plants and users
- role-based access control
- time-series database
- Docker/Kubernetes deployment
- Grafana monitoring
- anomaly detection

### 13. Conclusion

The project demonstrates how an IoT workload can be separated into a device layer, cloud API, managed database, decision layer and remote dashboard. The simulator makes the project reproducible without physical hardware while the ESP32 design provides a realistic migration path.
