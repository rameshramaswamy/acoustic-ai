import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from flask_caching import Cache # OPTIMIZATION 2
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from common.api_client import APIClient
from common.config import config
from components.map_view import create_3d_noise_map
from components.charts import create_impact_chart, create_time_chart

# Initialize App
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.title = "Chennai Soundscape"

# Expose server for Gunicorn
server = app.server 

#  Configure Redis Cache
cache = Cache(server, config={
    'CACHE_TYPE': 'RedisCache',
    'CACHE_REDIS_URL': config.REDIS_URL,
    'CACHE_DEFAULT_TIMEOUT': 300 # 5 Minutes
})

# Layout (Same as before)
app.layout = dbc.Container([
    dbc.NavbarSimple(
        brand="SOUND-DD: Chennai Acoustic Identity (Enterprise)",
        brand_href="#",
        color="primary",
        dark=True,
    ),
    dbc.Row([
        dbc.Col([
            html.H5("Live Acoustic Digital Twin", className="mt-3"),
            # Loading State for better UX
            dcc.Loading(dcc.Graph(id="map-3d"), type="graph") 
        ], width=8),
        dbc.Col([
            html.H5("Neighborhood Analysis", className="mt-3"),
            dcc.Dropdown(
                id="region-selector",
                options=[
                    {"label": "T. Nagar", "value": "T. Nagar"},
                    {"label": "Mylapore", "value": "Mylapore"},
                    {"label": "Adyar", "value": "Adyar"}
                ],
                value="T. Nagar",
                className="mb-3"
            ),
            dcc.Graph(id="impact-chart"),
            dcc.Graph(id="time-chart"),
        ], width=4)
    ])
], fluid=True)

# OPTIMIZED CALLBACKS
# The @cache.memoize decorator stores the result in Redis based on the arguments.
# If User A requests "T. Nagar", User B gets the result instantly from Redis.

@app.callback(
    Output("map-3d", "figure"),
    Input("region-selector", "value") # Dummy trigger to refresh map if needed, or use interval
)
@cache.memoize(timeout=60) # Cache Map for 1 min
def update_map(region):
    # In a real app, region would filter the map coordinates
    # For now, we fetch the default view
    clusters = APIClient.get_map_clusters(13.08, 80.27, 12)
    return create_3d_noise_map(clusters)

@app.callback(
    [Output("impact-chart", "figure"), Output("time-chart", "figure")],
    [Input("region-selector", "value")]
)
@cache.memoize(timeout=300) # Cache Charts for 5 mins
def update_metrics(region):
    report = APIClient.get_impact_report(region)
    return create_impact_chart(report), create_time_chart(report)

if __name__ == "__main__":
    # Dev mode
    app.run_server(debug=True, port=8050)