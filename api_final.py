from fastapi import FastAPI, Query, HTTPException
import sqlite3
from datetime import datetime, timedelta

DB_FILE = "/opt/wetterstation/data/bme280_data.db"

app = FastAPI(title="WeatherStation API")


def get_measurements(since_seconds: int):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    if since_seconds == 0:
        cursor.execute(
            "SELECT timestamp, temperature_C, humidity, pressure_hPa "
            "FROM measurements ORDER BY id DESC LIMIT 1"
        )
    else:
        since_time = datetime.now() - timedelta(seconds=since_seconds)
        since_iso = since_time.isoformat()
        cursor.execute(
            "SELECT timestamp, temperature_C, humidity, pressure_hPa "
            "FROM measurements WHERE timestamp >= ? ORDER BY id ASC",
            (since_iso,)
        )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return None

    return [
        {"timestamp": r[0], "temperature_C": r[1], "humidity": r[2], "pressure_hPa": r[3]}
        for r in rows
    ]


@app.get("/measurements")
def measurements(
    seconds: int = Query(0, ge=0),
    minutes: int = Query(0, ge=0),
    hours: int = Query(0, ge=0),
    days: int = Query(0, ge=0),
):
    """
    Return measurements from the last time window.
    Default (all zero) → latest measurement.
    """
    # Convert everything to seconds
    total_seconds = seconds + minutes*60 + hours*3600 + days*86400

    data = get_measurements(total_seconds)
    if not data:
        raise HTTPException(status_code=404, detail="No measurements found")
    return data

