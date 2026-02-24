from http.server import BaseHTTPRequestHandler, HTTPServer
import sqlite3
import urllib.parse
from datetime import datetime, timedelta
from io import BytesIO
import matplotlib.pyplot as plt

DB_FILE = "data.db"
TABLE = "your_table_name"  # <-- replace with your table name
HOST = "0.0.0.0"
PORT = 8000

class SimpleAPI(BaseHTTPRequestHandler):

    def do_GET(self):
        if not self.path.startswith("/data"):
            self.send_response(404)
            self.end_headers()
            return

        try:
            # Parse query parameters
            parsed = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed.query)

            # Connect to SQLite
            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = f"SELECT * FROM {TABLE}"
            values = []

            # Option 1: limit last N rows
            if "limit" in params:
                limit = int(params["limit"][0])
                query += " ORDER BY timestamp DESC LIMIT ?"
                values.append(limit)

            # Option 2: last X minutes
            elif "minutes" in params:
                minutes = int(params["minutes"][0])
                cutoff_time = (datetime.now() - timedelta(minutes=minutes)).isoformat()
                query += " WHERE timestamp >= ? ORDER BY timestamp DESC"
                values.append(cutoff_time)

            # Default: last 10 rows
            else:
                query += " ORDER BY timestamp DESC LIMIT 10"

            cursor.execute(query, values)
            rows = cursor.fetchall()
            conn.close()

            if not rows:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"No data available")
                return

            # Extract columns
            timestamps = [row['timestamp'] for row in rows]
            temperature = [row['temperature_C'] for row in rows]
            humidity = [row['humidity'] for row in rows]
            pressure = [row['pressure_hPa'] for row in rows]

            # Create figure with 3 subplots
            fig, axs = plt.subplots(3, 1, figsize=(8, 10), sharex=True)

            axs[0].plot(timestamps, temperature, color='red', marker='o')
            axs[0].set_ylabel('Temperature (C)')
            axs[0].grid(True)

            axs[1].plot(timestamps, humidity, color='blue', marker='x')
            axs[1].set_ylabel('Humidity (%)')
            axs[1].grid(True)

            axs[2].plot(timestamps, pressure, color='green', marker='s')
            axs[2].set_ylabel('Pressure (hPa)')
            axs[2].set_xlabel('Timestamp')
            axs[2].grid(True)

            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()

            # Save to buffer
            buf = BytesIO()
            plt.savefig(buf, format='png')
            plt.close(fig)
            buf.seek(0)

            # Send image
            self.send_response(200)
            self.send_header("Content-Type", "image/png")
            self.end_headers()
            self.wfile.write(buf.read())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), SimpleAPI)
    print(f"Server running on port {PORT}")
    server.serve_forever()