from flask import Flask, jsonify
import sqlite3

DB_FILE = "/opt/bme280/data/bme280_data.db"

app = Flask(__name__)

def get_latest_measurements(limit=10):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(f"SELECT timestamp, temperature_C, humidity, pressure_hPa FROM measurements ORDER BY id DESC LIMIT {limit}")
    rows = c.fetchall()
    conn.close()
    data = [
        {"timestamp": r[0], "temperature_C": r[1], "humidity": r[2], "pressure_hPa": r[3]}
        for r in rows
    ]
    return data

@app.route("/api/latest", methods=["GET"])
def latest():
    return jsonify(get_latest_measurements())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
