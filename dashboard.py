import pandas as pd
import streamlit as st
import requests
import plotly.express as px

st.set_page_config(layout="wide")

st.title("Real-Time Economic Indicators Dashboard")

# Define data sources
DATA_SOURCES = {
    "Auto Loan Delinquencies": "https://fred.stlouisfed.org/series/DSPDYEI",
    "Credit Card Delinquencies": "https://fred.stlouisfed.org/series/DRCCLACBS",
    "Mortgage Delinquencies": "https://fred.stlouisfed.org/series/MORTGAGE30US",
    "Housing Starts": "https://fred.stlouisfed.org/series/HOUST",
    "ISM Manufacturing PMI": "https://fred.stlouisfed.org/series/NAPM",
    "Corporate Bond Yield Spreads": "https://fred.stlouisfed.org/series/BAMLH0A0HYM2",
    "Unemployment Rate": "https://fred.stlouisfed.org/series/UNRATE",
    "Retail Sales": "https://fred.stlouisfed.org/series/RSXFS",
    "Oil Prices": "https://fred.stlouisfed.org/series/DCOILWTICO",
    "Freight Shipment Volumes": "https://fred.stlouisfed.org/series/RAILFRTCARLOADSD",
}

# Function to fetch data from FRED API
def fetch_fred_data(series_id):
    api_key = "c303b0128dd09ac48e3b3fbc6fe281b0"
    url = f"https://api.stlouisfed.org/fred/series/observations?series_id={series_id}&api_key={api_key}&file_type=json"
    response = requests.get(url)
    data = response.json()
    
    if "observations" in data:
        df = pd.DataFrame(data["observations"])
        df["date"] = pd.to_datetime(df["date"])
        df["value"] = pd.to_numeric(df["value"], errors='coerce')
        return df
    else:
        return pd.DataFrame(columns=["date", "value"])

# Master range selector toggle
use_master_range = st.checkbox("Use master date range selector", value=False)

# Global date range selector with predefined ranges
if use_master_range:
    all_dates = [fetch_fred_data(series_id)["date"] for series_id in DATA_SOURCES.values()]
    min_global_date = min([df.min() for df in all_dates if not df.empty])
    max_global_date = max([df.max() for df in all_dates if not df.empty])
    
    range_selection = st.selectbox("Select Global Range", ["1W", "1M", "3M", "1Y", "All"], index=4)
    
    if range_selection == "1W":
        selected_global_range = (max_global_date - pd.DateOffset(weeks=1), max_global_date)
    elif range_selection == "1M":
        selected_global_range = (max_global_date - pd.DateOffset(months=1), max_global_date)
    elif range_selection == "3M":
        selected_global_range = (max_global_date - pd.DateOffset(months=3), max_global_date)
    elif range_selection == "1Y":
        selected_global_range = (max_global_date - pd.DateOffset(years=1), max_global_date)
    else:
        selected_global_range = (min_global_date, max_global_date)

# Layout
col1, col2 = st.columns(2)

for i, (indicator, url) in enumerate(DATA_SOURCES.items()):
    series_id = url.split("/")[-1]  # Extracting series ID from URL
    df = fetch_fred_data(series_id)
    
    if not df.empty:
        # Apply master date range filter if enabled
        if use_master_range:
            df = df[(df["date"] >= selected_global_range[0]) & (df["date"] <= selected_global_range[1])]
        
        fig = px.line(df, x="date", y="value", title=indicator)
        
        # Add interactive range slider
        fig.update_layout(
            xaxis=dict(
                rangeselector=dict(
                    buttons=[
                        {"count": 7, "label": "1W", "step": "day", "stepmode": "backward"},
                        {"count": 30, "label": "1M", "step": "day", "stepmode": "backward"},
                        {"count": 90, "label": "3M", "step": "day", "stepmode": "backward"},
                        {"count": 365, "label": "1Y", "step": "day", "stepmode": "backward"},
                        {"step": "all"}  # Show full history
                    ]
                ),
                rangeslider=dict(visible=True),
                type="date"
            ),
            yaxis=dict(
                title="Value",
                autorange=True,  # Enables full dynamic Y-axis scaling
                fixedrange=False  # Allows users to zoom in manually
            )    
        )
        
        if i % 2 == 0:
            col1.plotly_chart(fig, use_container_width=True)
        else:
            col2.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"Could not fetch data for {indicator}")

st.write("Data sourced from Federal Reserve Economic Data (FRED)")
