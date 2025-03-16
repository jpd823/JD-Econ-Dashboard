import pandas as pd
import streamlit as st
import requests
import plotly.express as px

st.set_page_config(layout="wide")

st.title("Real-Time Economic Indicators Dashboard")

# Define data sources
DATA_SOURCES = {
    "US Gross Domestic Product": "https://fred.stlouisfed.org/series/GDP",
    "Federal Funds Effective Rate": "https://fred.stlouisfed.org/series/FEDFUNDS",
    "CPI less Food & Energy": "https://fred.stlouisfed.org/series/CORESTICKM159SFRBATL",
    "Unemployment Rate": "https://fred.stlouisfed.org/series/UNRATE",
    "Oil Prices": "https://fred.stlouisfed.org/series/DCOILWTICO",
    "Corporate Bond Yield Spreads": "https://fred.stlouisfed.org/series/BAMLH0A0HYM2",
    "Auto Loan Delinquencies": "https://fred.stlouisfed.org/series/DSPDYEI",
    "Housing Starts": "https://fred.stlouisfed.org/series/HOUST",
    "Credit Card Delinquencies": "https://fred.stlouisfed.org/series/DRCCLACBS",
    "Mortgage Delinquencies": "https://fred.stlouisfed.org/series/DRSFRMACBS",
    "ISM Manufacturing PMI": "https://fred.stlouisfed.org/series/DGORDER",
    "Retail Sales": "https://fred.stlouisfed.org/series/RSXFS",
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

# Layout
col1, col2 = st.columns(2)

for i, (indicator, url) in enumerate(DATA_SOURCES.items()):
    series_id = url.split("/")[-1]  # Extracting series ID from URL
    df = fetch_fred_data(series_id)
    
    if not df.empty:
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
                titel="Value",
                range=[df["value"].min() * 0.9, df["value"].max() * 1.1],  # Dynamically set Y-axis range
                fixedrange=False  # Allows users to zoom in on Y-axis manually
            )    
        )

        # Display the chart in alternating columns
        if i % 2 == 0:
            col1.plotly_chart(fig, use_container_width=True)
        else:
            col2.plotly_chart(fig, use_container_width=True)
    else:
        st.warning(f"Could not fetch data for {indicator}")

st.write("Data sourced from Federal Reserve Economic Data (FRED)")
