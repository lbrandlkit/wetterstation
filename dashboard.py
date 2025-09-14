import os
import requests
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

# API-Adresse aus Umgebungsvariable oder Default
API_HOST = os.environ.get("WEATHER_API_HOST", "wetter")
API_URL = f"http://{API_HOST}:5000/api/data"

TIME_RANGES = {
    "15 Minuten": {"minutes": 15},
    "1 Stunde": {"hours": 1},
    "6 Stunden": {"hours": 6},
    "1 Tag": {"days": 1},
    "7 Tage": {"days": 7}
}

app = Dash(__name__)
app.title = "Wetterstation Dashboard"

app.layout = html.Div([
    html.H1("Wetterstation Dashboard"),
    html.Label("Zeitraum auswählen:"),
    dcc.Dropdown(
        id="time-range",
        options=[{"label": k, "value": k} for k in TIME_RANGES.keys()],
        value="1 Stunde",
        clearable=False
    ),
    dcc.Graph(id="temp-plot"),
    dcc.Graph(id="hum-plot"),
    dcc.Graph(id="press-plot")
])

def fetch_data(params):
    try:
        response = requests.get(API_URL, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        return pd.DataFrame(data) if data else pd.DataFrame()
    except Exception as e:
        print("Fehler beim API-Request:", e)
        return pd.DataFrame()

@app.callback(
    [Output("temp-plot", "figure"),
     Output("hum-plot", "figure"),
     Output("press-plot", "figure")],
    [Input("time-range", "value")]
)
def update_plots(selected_range):
    params = TIME_RANGES[selected_range]
    df = fetch_data(params)

    if df.empty:
        empty_fig = px.scatter(title="Keine Daten verfügbar")
        return empty_fig, empty_fig, empty_fig

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    temp_fig = px.line(df, x="timestamp", y="temperature_C", title="Temperatur (°C)")
    hum_fig = px.line(df, x="timestamp", y="humidity", title="Luftfeuchtigkeit (%)")
    press_fig = px.line(df, x="timestamp", y="pressure_hPa", title="Luftdruck (hPa)")

    return temp_fig, hum_fig, press_fig

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
