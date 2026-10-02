# Interview Preparation

## 1. Why is this a cloud computing project?

Because sensor data is transmitted to a remotely hosted API, persisted in a managed cloud database, processed by cloud-side business logic, and accessed through a web dashboard.

## 2. Why use a simulator?

It makes the project reproducible without physical hardware and allows controlled testing of dry, normal and wet conditions.

## 3. Why FastAPI?

It is lightweight, supports Python type hints and validation, provides automatic OpenAPI/Swagger documentation, and is suitable for REST APIs.

## 4. Why PostgreSQL?

The data has structured relationships and PostgreSQL provides reliable relational storage. Sensor readings can also be indexed by device and timestamp.

## 5. How does watering work?

The API evaluates every new reading. If moisture is below the configured threshold and cooldown conditions are satisfied, it creates a watering event and alert.

## 6. How is the device authenticated?

The simulator/ESP32 sends an `X-Device-Key`. Dashboard users authenticate using username/password and receive a JWT.

## 7. How would you scale it?

Use stateless API instances behind a load balancer, an MQTT broker for device ingestion, a queue for asynchronous processing, database connection pooling, indexes and time-series storage.

## 8. What happens if the dashboard is closed?

The backend and simulator continue operating. Sensor data is still stored and watering rules are evaluated server-side.

## 9. What happens if the database is unavailable?

The API readiness endpoint can expose the dependency failure. A production architecture could buffer messages in a queue or device gateway and retry later.

## 10. Why is the virtual pump useful?

It demonstrates cloud-to-device/actuator control without requiring physical hardware.

## 11. What would you improve for production?

MQTT, IoT identities/certificates, secret manager, rate limiting, RBAC, refresh tokens, background workers, external notification providers, observability, and stronger database policies.

## 12. What did you personally learn?

- REST API design
- cloud database integration
- IoT data flow
- automated rule processing
- authentication
- deployment
- testing and CI
- Git/GitHub workflow
