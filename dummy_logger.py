import sqlite3
import time
import random
from datetime import datetime

DB_FILE = "/opt/wetterstation/data/bme280_data.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS measurements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            temperature_C REAL,
            humidity REAL,
            pressure_hPa REAL
        )
    """)
    conn.commit()
    conn.close()

def log_dummy_data():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    timestamp = datetime.utcnow().isoformat()
    temperature = round(random.uniform(18, 25), 2)
    humidity = round(random.uniform(0.3, 0.6), 2)
    pressure = round(random.uniform(990, 1020), 2)
    c.execute(
        "INSERT INTO measurements (timestamp, temperature_C, humidity, pressure_hPa) VALUES (?, ?, ?, ?)",
        (timestamp, temperature, humidity, pressure)
    )
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Dummy-Logger gestartet. (CTRL+C zum Beenden)")
    while True:
        log_dummy_data()
        print("Eintrag gespeichert.")
        time.sleep(10)
