from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import sqlite3
import urllib.parse
from datetime import datetime, timedelta

DB_FILE = "/opt/wetterstation/data/bme280_data.db"
TABLE = "measurements"   # <-- CHANGE THIS
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

            conn = sqlite3.connect(DB_FILE)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = f"SELECT * FROM {TABLE}"
            values = []

            # --- Option 1: limit ---
            if "limit" in params:
                limit = int(params["limit"][0])
                query += " ORDER BY timestamp DESC LIMIT ?"
                values.append(limit)

            # --- Option 2: last X minutes ---
            elif "minutes" in params:
                minutes = int(params["minutes"][0])
                cutoff_time = (
                    datetime.now() - timedelta(minutes=minutes)
                ).isoformat()

                query += " WHERE timestamp >= ? ORDER BY timestamp DESC"
                values.append(cutoff_time)

            # --- Default: last 10 rows ---
            else:
                query += " ORDER BY timestamp DESC LIMIT 10"

            cursor.execute(query, values)
            rows = cursor.fetchall()
            conn.close()

            data = [dict(row) for row in rows]
            response = json.dumps(data)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(response.encode())

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(str(e).encode())


if __name__ == "__main__":
    server = HTTPServer((HOST, PORT), SimpleAPI)
    print(f"Server running on port {PORT}")
    server.serve_forever()