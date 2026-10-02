import React, { useEffect, useState } from "react";

const API =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const DEVICE = "virtual-plant-01";

function Card({ title, value, unit, status }) {
  return (
    <div className="card">
      <span className="muted">{title}</span>
      <strong>
        {value ?? "--"} {unit}
      </strong>
      {status && <small>{status}</small>}
    </div>
  );
}

export default function App() {
  const [token, setToken] = useState(
    localStorage.getItem("plant_token")
  );

  const [form, setForm] = useState({
    username: "admin",
    password: "change-me",
  });

  const [data, setData] = useState({
    latest: null,
    readings: [],
    events: [],
    alerts: [],
  });

  const [error, setError] = useState("");

  const [pumpOn, setPumpOn] = useState(false);

  async function login(e) {
    e.preventDefault();
    setError("");

    try {
      const response = await fetch(`${API}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(form),
      });

      if (!response.ok) {
        setError("Login failed. Check username and password.");
        return;
      }

      const body = await response.json();

      localStorage.setItem("plant_token", body.access_token);
      setToken(body.access_token);
    } catch (err) {
      setError("Cannot connect to backend.");
      console.error(err);
    }
  }

  async function api(path, options = {}) {
    const response = await fetch(`${API}${path}`, {
      ...options,
      headers: {
        ...(options.headers || {}),
        Authorization: `Bearer ${token}`,
      },
    });

    if (response.status === 401) {
      localStorage.removeItem("plant_token");
      setToken(null);
      throw new Error("Session expired. Please login again.");
    }

    if (!response.ok) {
      throw new Error(await response.text());
    }

    return response.json();
  }

  async function refresh() {
    try {
      const [latest, readings, events, alerts] =
        await Promise.all([
          api(
            `/api/v1/readings/latest?device_id=${DEVICE}`
          ),

          api(
            `/api/v1/readings?device_id=${DEVICE}&limit=20`
          ),

          api("/api/v1/watering-events?limit=10"),

          api("/api/v1/alerts?limit=10"),
        ]);

      setData({
        latest,
        readings: [...readings].reverse(),
        events,
        alerts,
      });
    } catch (err) {
      setError(err.message);
    }
  }

  // -----------------------------------------
  // PUMP CONTROL
  // -----------------------------------------

  async function setPump(on) {
    try {
      setError("");

      const response = await fetch(
        `${API}/api/v1/devices/${DEVICE}/pump?on=${on}`,
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.status === 401) {
        localStorage.removeItem("plant_token");
        setToken(null);
        throw new Error("Session expired. Please login again.");
      }

      if (!response.ok) {
        let message = "Pump request failed.";

        try {
          const errorData = await response.json();
          message = errorData.detail || message;
        } catch {
          // Ignore JSON parsing error
        }

        throw new Error(message);
      }

      const result = await response.json();

      console.log("Pump response:", result);

      setPumpOn(result.pump_on);

      setError(
        result.pump_on
          ? "🟢 Pump turned ON successfully"
          : "⚪ Pump turned OFF successfully"
      );
    } catch (err) {
      console.error("Pump error:", err);
      setError(err.message);
    }
  }

  // -----------------------------------------
  // AUTOMATIC DASHBOARD REFRESH
  // -----------------------------------------

  useEffect(() => {
    if (!token) {
      return;
    }

    refresh();

    const interval = setInterval(() => {
      refresh();
    }, 5000);

    return () => clearInterval(interval);
  }, [token]);

  // -----------------------------------------
  // LOGIN SCREEN
  // -----------------------------------------

  if (!token) {
    return (
      <main className="login">
        <form className="panel" onSubmit={login}>
          <h1>🌱 Smart Plant Cloud</h1>

          <p className="muted">
            Cloud-connected IoT monitoring dashboard
          </p>

          <input
            value={form.username}
            onChange={(e) =>
              setForm({
                ...form,
                username: e.target.value,
              })
            }
            placeholder="Username"
          />

          <input
            type="password"
            value={form.password}
            onChange={(e) =>
              setForm({
                ...form,
                password: e.target.value,
              })
            }
            placeholder="Password"
          />

          <button type="submit">
            Sign in
          </button>

          {error && (
            <p className="error">
              {error}
            </p>
          )}
        </form>
      </main>
    );
  }

  const r = data.latest;

  // -----------------------------------------
  // DASHBOARD
  // -----------------------------------------

  return (
    <main>
      <header>
        <div>
          <h1>🌱 Cloud Smart Plant</h1>

          <p className="muted">
            Device: {DEVICE} · polling every 5 seconds
          </p>
        </div>

        <button
          className="secondary"
          onClick={() => {
            localStorage.removeItem("plant_token");
            setToken(null);
          }}
        >
          Logout
        </button>
      </header>

      {error && (
        <div className="error banner">
          {error}
        </div>
      )}

      {/* SENSOR CARDS */}

      <section className="grid">
        <Card
          title="Soil moisture"
          value={r?.soil_moisture?.toFixed(1)}
          unit="%"
          status={
            r
              ? r.soil_moisture < 35
                ? "Needs water"
                : "Healthy"
              : ""
          }
        />

        <Card
          title="Temperature"
          value={r?.temperature?.toFixed(1)}
          unit="°C"
        />

        <Card
          title="Humidity"
          value={r?.humidity?.toFixed(1)}
          unit="%"
        />

        <Card
          title="Light"
          value={r?.light?.toFixed(0)}
          unit="lux"
        />
      </section>

      {/* REMOTE PUMP CONTROL */}

      <section className="panel">
        <div className="section-title">
          <h2>Remote actuator</h2>

          <div>
            <button
              onClick={() => setPump(true)}
              disabled={pumpOn}
            >
              Pump ON
            </button>

            <button
              className="secondary"
              onClick={() => setPump(false)}
              disabled={!pumpOn}
            >
              Pump OFF
            </button>
          </div>
        </div>

        <p className="muted">
          Manual controls demonstrate cloud-to-device
          control using the virtual actuator.
        </p>

        <div className="pump-status">
          <strong>
            Pump status:
          </strong>{" "}

          {pumpOn ? (
            <span>
              🟢 ON
            </span>
          ) : (
            <span>
              ⚪ OFF
            </span>
          )}
        </div>
      </section>

      {/* MOISTURE HISTORY */}

      <section className="panel">
        <h2>Moisture history</h2>

        <div className="bars">
          {data.readings.map((x) => (
            <div
              className="bar-wrap"
              key={x.id}
              title={`${x.soil_moisture.toFixed(1)}%`}
            >
              <div
                className="bar"
                style={{
                  height: `${Math.max(
                    8,
                    x.soil_moisture
                  )}%`,
                }}
              />
            </div>
          ))}
        </div>
      </section>

      {/* WATERING + ALERTS */}

      <section className="two">
        <div className="panel">
          <h2>Recent watering</h2>

          {data.events.length === 0 ? (
            <p className="muted">
              No events yet.
            </p>
          ) : (
            data.events.map((event) => (
              <div
                className="row"
                key={event.id}
              >
                <span>
                  {event.reason}
                </span>

                <b>
                  {event.duration_seconds}s
                </b>
              </div>
            ))
          )}
        </div>

        <div className="panel">
          <h2>Alerts</h2>

          {data.alerts.length === 0 ? (
            <p className="muted">
              No alerts.
            </p>
          ) : (
            data.alerts.map((alert) => (
              <div
                className="row"
                key={alert.id}
              >
                <span>
                  {alert.message}
                </span>

                <b>
                  {alert.severity}
                </b>
              </div>
            ))
          )}
        </div>
      </section>
    </main>
  );
}