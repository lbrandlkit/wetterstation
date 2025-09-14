from flask import Flask, jsonify, request
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)

DB_FILE = "/opt/wetterstation/data/bme280_data.db"  # Pfad zu deiner DB

def get_latest_measurement():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT timestamp, temperature_C, humidity, pressure_hPa FROM measurements ORDER BY timestamp DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row:
        return {
            "timestamp": row[0],
            "temperature_C": row[1],
            "humidity": row[2],
            "pressure_hPa": row[3]
        }
    return {}

def get_measurements(minutes=0, hours=0, days=0):
    delta = timedelta(days=days, hours=hours, minutes=minutes)
    since = datetime.now() - delta

    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT timestamp, temperature_C, humidity, pressure_hPa
        FROM measurements
        WHERE timestamp >= ?
        ORDER BY timestamp ASC
    """, (since.isoformat(),))
    rows = c.fetchall()
    conn.close()

    return [
        {
            "timestamp": row[0],
            "temperature_C": row[1],
            "humidity": row[2],
            "pressure_hPa": row[3]
        } for row in rows
    ]

@app.route("/api/latest", methods=["GET"])
def latest():
    return jsonify(get_latest_measurement())

@app.route("/api/data", methods=["GET"])
def data():
    try:
        minutes = int(request.args.get("minutes", 0))
        hours = int(request.args.get("hours", 0))
        days = int(request.args.get("days", 0))
    except ValueError:
        return jsonify({"error": "Invalid query parameter"}), 400

    if minutes == hours == days == 0:
        return jsonify({"error": "Specify at least one of minutes, hours or days"}), 400

    return jsonify(get_measurements(minutes, hours, days))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

