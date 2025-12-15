import plotly.express as px
import pandas as pd

def create_impact_chart(report_data):
    """Creates a Frequency Distribution Bar Chart"""
    dist = report_data.get("distribution", {})
    df = pd.DataFrame(list(dist.items()), columns=["Source", "Count"])
    
    fig = px.pie(
        df, 
        values="Count", 
        names="Source", 
        title=f"Noise Composition: {report_data['region']}",
        hole=0.4,
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    return fig

def create_time_chart(report_data):
    """Creates Peak Hour Line Chart"""
    hours = report_data.get("peak_pollution_hours", {})
    if not hours:
        return px.line(title="No Pollution Data")
        
    df = pd.DataFrame(list(hours.items()), columns=["Hour", "Events"])
    df = df.sort_values("Hour")
    
    fig = px.area(
        df, x="Hour", y="Events", 
        title="Hourly Pollution Trend",
        markers=True
    )
    return fig