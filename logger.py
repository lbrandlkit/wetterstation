import sqlite3
import time
from datetime import datetime
import board
import busio
from adafruit_bme280 import basic

DB_FILE = "/opt/wetterstation/data/bme280_data.db"

def file_creating():
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

def log(bme280):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    time = datetime.now().isoformat()
    temperature = bme280.temperature
    humidity = bme280.humidity
    pressure = bme280.pressure


    c.execute(
        "INSERT INTO measurements (timestamp, temperature_C, humidity, pressure_hPa) VALUES (?, ?, ?, ?)",
        (time, temperature, humidity, pressure)
    )
    conn.commit()
    conn.close()
    return f'{time}, {temperature}, {humidity}, {pressure}'

if __name__ == "__main__":
    file_creating()
    i2c = busio.I2C(board.SCL, board.SDA)
    bme280 = basic.Adafruit_BME280_I2C(i2c, address=0x76)
    while True:
        print(log(bme280))
        time.sleep(10)
