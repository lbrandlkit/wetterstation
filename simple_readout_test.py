import time
import board
import busio
from adafruit_bme280 import basic as adafruit_bme280

# Create I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create sensor object (address 0x76 since your scan showed 76)
bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

while True:
    print("Temperature: {:.2f} °C".format(bme280.temperature))
    print("Pressure: {:.2f} hPa".format(bme280.pressure))
    print("Humidity: {:.2f} %".format(bme280.humidity))
    print("-" * 30)
    time.sleep(2)