import argparse
import math
import os
import random
import time
from datetime import datetime

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
DEVICE_API_KEY = os.getenv("DEVICE_API_KEY", "change-device-key")
DEVICE_ID = os.getenv("DEVICE_ID", "virtual-plant-01")


def make_reading(step: int, scenario: str):
    if scenario == "dry":
        moisture = max(8, 70 - step * 4 + random.uniform(-3, 3))
    elif scenario == "wet":
        moisture = min(95, 75 + random.uniform(-3, 3))
    else:
        moisture = 48 + 10 * math.sin(step / 5) + random.uniform(-3, 3)

    return {
        "device_id": DEVICE_ID,
        "soil_moisture": round(moisture, 2),
        "temperature": round(27 + 4 * math.sin(step / 8) + random.uniform(-1, 1), 2),
        "humidity": round(58 - 10 * math.sin(step / 9) + random.uniform(-2, 2), 2),
        "light": round(max(50, 650 + 250 * math.sin(step / 6) + random.uniform(-40, 40)), 2),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default=API_URL)
    parser.add_argument("--scenario", choices=["normal", "dry", "wet"], default="normal")
    parser.add_argument("--interval", type=float, default=5)
    args = parser.parse_args()

    print(f"Simulator started: {DEVICE_ID} -> {args.api}")
    print(f"Scenario: {args.scenario}")

    step = 0
    while True:
        payload = make_reading(step, args.scenario)
        try:
            response = requests.post(
                f"{args.api}/api/v1/readings",
                headers={"X-Device-Key": DEVICE_API_KEY},
                json=payload,
                timeout=10,
            )
            print(datetime.now().strftime("%H:%M:%S"), payload, "->", response.status_code)
        except requests.RequestException as exc:
            print("Connection error:", exc)

        step += 1
        time.sleep(args.interval)


if __name__ == "__main__":
    main()
