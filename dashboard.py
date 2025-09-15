import os
import requests
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output
import dash_bootstrap_components as dbc

# API-Adresse flexibel
API_HOST = os.environ.get("WEATHER_API_HOST", "wetter")
API_URL = f"http://{API_HOST}:5000/api/data"

TIME_RANGES = {
    "15 Minuten": {"minutes": 15},
    "1 Stunde": {"hours": 1},
    "6 Stunden": {"hours": 6},
    "1 Tag": {"days": 1},
    "7 Tage": {"days": 7}
}

current_temp = 22.5
current_hum = 55.0
current_press = 1013.2

# Dash App mit Bootstrap Theme
app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
# app.title = "Wetterstation Dashboard"

# Dummy-Data für initiale Anzeige (verhindert weißen Bildschirm)
import datetime
dummy_time = [pd.Timestamp.now()]
dummy_df = pd.DataFrame({
    "timestamp": dummy_time,
    "temperature": [None],
    "humidity": [None],
    "pressure": [None]
})

temp_fig = px.line(dummy_df, x="timestamp", y="temperature",
                   title="Temperatur (°C)", line_shape='spline', template='plotly_dark')
hum_fig = px.line(dummy_df, x="timestamp", y="humidity",
                  title="Luftfeuchtigkeit (%)", line_shape='spline', template='plotly_dark')
press_fig = px.line(dummy_df, x="timestamp", y="pressure",
                    title="Luftdruck (hPa)", line_shape='spline', template='plotly_dark')

title = html.H2(
    f"Wetterstation: {current_temp} °C  {current_hum} %  {current_press} hPa",
    style={"color": "white", "textAlign": "center"}
)
app.layout = dbc.Container([
    # dbc.Row(dbc.Col(html.H1("Wetterstation Dashboard", className="text-center my-4"), width=12)),
    dbc.Row([
        dbc.Col([
            title,
            dcc.Interval(id="interval-component", interval=5*1000, n_intervals=0)
        ], width=12)
    ]),
    
    dbc.Row([
        dbc.Col(
            dcc.Dropdown(
                id="time-range",
                options=[{"label": k, "value": k} for k in TIME_RANGES.keys()],
                value="1 Stunde",
                clearable=False,
                style={"width": "200px", "minWidth": "150px"},  # automatisch breites Dropdown
                # style={"width": "200px", "backgroundColor": "#000000", "color": "#ffffff"},  # automatisch breites Dropdown
                className="dropdown-auto-width",
            ), width=4
        )
    ], className="mb-3"),
    
    dbc.Row([
        dbc.Col(dcc.Graph(id="temp-plot", figure=temp_fig), xs=12, sm=12, md=12, lg=4, xl=4),
        dbc.Col(dcc.Graph(id="hum-plot", figure=hum_fig), xs=12, sm=12, md=12, lg=4, xl=4),
        dbc.Col(dcc.Graph(id="press-plot", figure=press_fig), xs=12, sm=12, md=12, lg=4, xl=4)
    ])

], fluid=True)

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
     Output("press-plot", "figure"),],
    [Input("time-range", "value")]
)
def update_plots(selected_range):
    params = TIME_RANGES[selected_range]
    df = fetch_data(params)

    if df.empty:
        # Dummy-Data erneut zurückgeben, falls API leer
        return temp_fig, hum_fig, press_fig

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    temp_fig_new = px.line(
        df, x="timestamp", y="temperature_C", title="Temperatur (°C)",
        line_shape='spline', template='plotly_dark', color_discrete_sequence=['#FF5733']
    )
    hum_fig_new = px.line(
        df, x="timestamp", y="humidity", title="Luftfeuchtigkeit (%)",
        line_shape='spline', template='plotly_dark', color_discrete_sequence=['#33C1FF']
    )
    press_fig_new = px.line(
        df, x="timestamp", y="pressure_hPa", title="Luftdruck (hPa)",
        line_shape='spline', template='plotly_dark', color_discrete_sequence=['#75FF33']
    )

    return temp_fig_new, hum_fig_new, press_fig_new

# def update_title(n):
#     try:
#         # API Request
#         r = requests.get("http://wetter:5000/api/latest")  # URL anpassen
#         data = r.json()
#         temp = data["temperature_C"]
#         hum = data["humidity"]
#         press = data["pressure_hPa"]

#         return f"Wetterstation - Temperatur: {temp} °C | " \
#                f"Luftfeuchte: {hum} % | Luftdruck: {press} hPa"
#     except Exception as e:
#         # Fehlerfall: alte Werte oder Fehlermeldung anzeigen
#         return f"Wetterstation - Daten nicht verfügbar ({e})"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=True)
