import plotly.graph_objects as go
from common.config import config

def create_3d_noise_map(clusters):
    """
    Generates a 3D ScatterMapbox figure.
    Height of bars = Noise Intensity.
    Color = Noise Intensity.
    """
    lats = [c['lat'] for c in clusters]
    lons = [c['lon'] for c in clusters]
    intensities = [c['intensity'] * 100 for c in clusters] # Scale for height
    texts = [f"Events: {c['count']}" for c in clusters]

    fig = go.Figure(go.Scattermapbox(
        lat=lats,
        lon=lons,
        mode='markers',
        marker=go.scattermapbox.Marker(
            size=15,
            color=intensities,
            colorscale='RdYlGn_r', # Red = Loud, Green = Quiet
            showscale=True,
            opacity=0.8,
        ),
        text=texts,
        hoverinfo='text'
    ))

    fig.update_layout(
        mapbox=dict(
            accesstoken=config.MAPBOX_TOKEN,
            style="light", # or "dark", "satellite-streets"
            center=dict(lat=13.0827, lon=80.2707), # Chennai
            zoom=11,
            pitch=45 # 3D Effect
        ),
        margin={"r":0,"t":0,"l":0,"b":0},
        height=800
    )
    return fig