# Cloud-Connected Smart Plant Care & Watering System 🌱☁️

An industry-oriented Cloud Computing + IoT project that monitors plant conditions, stores historical sensor data in a cloud database, decides when watering is required, generates alerts, and provides a web dashboard.

> **No physical hardware is required.** The included Python IoT simulator generates realistic synthetic soil-moisture, temperature, humidity and light readings.

## Architecture

```text
                    ┌─────────────────────────────┐
                    │       React/Vite UI         │
                    │ Dashboard • Charts • Alerts │
                    └──────────────┬──────────────┘
                                   │ HTTPS REST
                                   ▼
┌──────────────────┐      ┌────────────────────────┐
│ Python IoT       │ HTTPS│ FastAPI Cloud Backend  │
│ Sensor Simulator ├─────►│ REST API + Rules       │
│ / optional ESP32 │      │ Auth + Validation      │
└──────────────────┘      └────────────┬───────────┘
                                       │ SQL
                                       ▼
                            ┌──────────────────────┐
                            │ Supabase PostgreSQL  │
                            │ readings/events/     │
                            │ alerts/settings      │
                            └──────────────────────┘
```

### Main features

- Virtual IoT sensor simulation
- Soil moisture, temperature, humidity and light
- REST API for device-to-cloud communication
- Cloud PostgreSQL through Supabase
- Local SQLite fallback
- Automated watering decision engine
- Virtual pump/actuator
- Watering event history
- Alert generation
- Historical charts
- Dashboard refresh every few seconds
- JWT dashboard authentication
- Device API-key authentication
- Input validation
- CORS configuration
- Health/readiness endpoints
- Automated tests
- Docker support
- Render deployment configuration
- Optional ESP32 hardware integration
- GitHub-ready documentation

## Project structure

```text
cloud-smart-plant/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── models.py
│   │   ├── schemas.py
│   │   ├── security.py
│   │   ├── watering.py
│   │   └── main.py
│   ├── tests/
│   │   └── test_api.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── simulator/
│   ├── simulator.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   ├── .env.example
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       └── style.css
├── esp32/
│   └── smart_plant_esp32.ino
├── database/
│   └── schema.sql
├── docs/
│   ├── REPORT.md
│   ├── INTERVIEW.md
│   └── SCREENSHOTS.md
├── .github/
│   └── workflows/
│       └── backend-tests.yml
├── .gitignore
├── docker-compose.yml
└── render.yaml
```

# 1. Run locally

## Requirements

- Python 3.11+
- Node.js 20+
- Git
- Internet is only needed if using a cloud database

### Backend

Windows:

```powershell
cd backend
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Linux/macOS:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

Backend:

- API: http://127.0.0.1:8000
- Swagger: http://127.0.0.1:8000/docs
- Health: http://127.0.0.1:8000/healthz

The default local configuration uses SQLite, so no database installation is required.

### Simulator

Open another terminal:

```bash
cd simulator
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python simulator.py
```

The simulator sends one reading every 5 seconds.

To force a dry period and demonstrate watering:

```bash
python simulator.py --scenario dry
```

To generate normal readings:

```bash
python simulator.py --scenario normal
```

### Frontend

Open another terminal:

```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

Open the displayed Vite URL.

Default dashboard login:

```text
username: admin
password: change-me
```

Change these values in `backend/.env` before deployment.

# 2. Local Docker run

```bash
docker compose up --build
```

The API will be available at:

```text
http://localhost:8000
```

The dashboard can still be started with:

```bash
cd frontend
npm install
npm run dev
```

# 3. Cloud deployment

Recommended student architecture:

- **Supabase**: PostgreSQL cloud database
- **Render**: FastAPI backend
- **Vercel or Render Static Site**: frontend
- Local Python simulator or optional ESP32: IoT device

Supabase's Data API is generated from the database schema and Supabase currently lists a free Postgres database tier. Render supports native Python/FastAPI deployment with `pip install -r requirements.txt` and a Uvicorn start command. Check provider limits before deployment because free-tier terms can change.

## Supabase

1. Create a Supabase project.
2. Open SQL Editor.
3. Run `database/schema.sql`.
4. Copy the Postgres connection string.
5. Set:

```env
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/postgres?sslmode=require
```

Do not put the database password in GitHub.

## Render backend

Create a Web Service connected to this repository.

Root directory:

```text
backend
```

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Environment variables:

```text
DATABASE_URL=<Supabase connection string>
JWT_SECRET=<long random secret>
DEVICE_API_KEY=<long random device key>
ADMIN_USERNAME=admin
ADMIN_PASSWORD=<strong password>
CORS_ORIGINS=<frontend URL>
```

The included `.python-version` can be added with a supported Python version such as 3.13 if desired.

## Frontend

Set:

```env
VITE_API_URL=https://YOUR-BACKEND.onrender.com
```

Then deploy the `frontend` directory as a Vercel/Render static site.

Build:

```bash
npm run build
```

Output:

```text
dist
```

## Cloud simulator

The simulator can run from your laptop:

```bash
python simulator.py --api https://YOUR-BACKEND.onrender.com
```

This is enough to demonstrate a cloud-connected IoT system without hardware.

# 4. Watering logic

Default settings:

- Moisture threshold: 35%
- Temperature alert threshold: 38°C
- Humidity alert threshold: 25%
- Watering duration: 10 seconds
- Watering cooldown: 60 seconds

Decision:

```text
IF soil_moisture < threshold
AND pump is not already running
AND cooldown has expired
THEN:
    create watering event
    turn virtual pump ON
    create alert
ELSE:
    do not water
```

This is deliberately simple and explainable for a college project.

## Why not water every time moisture is low?

Because cloud automation should consider state and cooldown. Otherwise a noisy sensor or repeated requests could cause excessive watering.

# 5. Security

The project demonstrates:

- Device API key
- JWT authentication
- Password hashing
- Environment variables for secrets
- Pydantic request validation
- CORS allow-list
- No secrets committed to Git
- HTTPS in cloud deployment
- Health/readiness separation

For a real commercial product, add refresh tokens, a secret manager, role-based access control, rate limiting, audit logs and a managed IoT identity system.

# 6. Scalability

Current student version:

```text
1 simulator → 1 API → PostgreSQL → dashboard
```

Scalable version:

```text
Thousands of devices
       ↓
MQTT broker / IoT gateway
       ↓
Message queue / stream
       ↓
Stateless API + workers
       ↓
PostgreSQL / time-series storage
       ↓
WebSocket / realtime service
       ↓
Dashboards
```

The REST device endpoint intentionally keeps the simulator and future ESP32 loosely coupled from the backend.

# 7. Optional ESP32

See `esp32/smart_plant_esp32.ino`.

Hardware:

- ESP32
- Capacitive soil-moisture sensor
- DHT22/DHT11
- LDR
- Relay module
- Mini water pump
- External power supply

**Never connect a pump directly to an ESP32 GPIO.** Use a suitable relay/MOSFET driver and external supply, with proper isolation and protection.

The ESP32 can POST the same JSON payload used by the simulator.

# 8. API examples

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "username": "admin",
  "password": "change-me"
}
```

### Device reading

```http
POST /api/v1/readings
X-Device-Key: YOUR_DEVICE_API_KEY
Content-Type: application/json

{
  "device_id": "virtual-plant-01",
  "soil_moisture": 22.5,
  "temperature": 29.4,
  "humidity": 56.2,
  "light": 610
}
```

### Latest reading

```http
GET /api/v1/readings/latest
Authorization: Bearer YOUR_JWT
```

### Watering history

```http
GET /api/v1/watering-events
Authorization: Bearer YOUR_JWT
```

# 9. Testing

Run:

```bash
cd backend
pytest -q
```

CI is included in `.github/workflows/backend-tests.yml`.

# 10. GitHub strategy

Suggested repository name:

```text
cloud-connected-smart-plant
```

Suggested description:

> Cloud-connected IoT plant monitoring system with simulated sensors, FastAPI, PostgreSQL, automated watering, alerts and real-time dashboard.

Recommended commits:

```text
feat: initialize cloud smart plant architecture
feat: add sensor ingestion API
feat: add watering decision engine
feat: add virtual IoT simulator
feat: add dashboard
feat: add authentication and validation
test: add API and watering tests
docs: add deployment and project report
ci: add GitHub Actions backend tests
```

Do not commit:

```text
.env
node_modules/
.venv/
*.db
__pycache__/
```

# 11. Demo sequence

1. Start backend.
2. Start frontend.
3. Start simulator with `--scenario normal`.
4. Show incoming readings.
5. Start `--scenario dry`.
6. Show moisture dropping.
7. Show automatic watering event.
8. Show virtual pump state.
9. Show alert.
10. Show historical chart.
11. Open Swagger `/docs`.
12. Explain Supabase cloud database.
13. Push code to GitHub.
14. Show CI passing.
15. Explain how ESP32 would replace the simulator.

This gives you a clear Cloud Computing demonstration instead of a hardware-only demonstration.
