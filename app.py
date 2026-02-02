import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time
import pytz

# ==============================
# Streamlit Config
# ==============================
st.set_page_config(page_title="ETF & ETC Dashboard", layout="wide")

PERIOD = "1y"
REFRESH_SEC = 45
TIMEZONE = pytz.timezone("Europe/Berlin")

# --------------------------
# CSS für Layout und Balken
# --------------------------
st.markdown("""
<style>
.header-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    width: 100%;
}

#refresh-bar-container {
    display: flex;
    justify-content: center;
    margin: 20px 0;
}

#refresh-bar {
    height: 15px;
    width: 300px;
    background-color: lightgray;
    border-radius: 5px;
}

#refresh-bar-fill {
    height: 100%;
    width: 0%;
    background-color: green;
    border-radius: 5px;
    transition: width 1s linear;
}

.main > div.block-container {
    padding-top: 1rem;
    transform: scale(0.75);
    transform-origin: top left;
}
</style>
""", unsafe_allow_html=True)

# --------------------------
# Ticker Setup
# --------------------------
tickers = ["IWDA.AS", "VWCE.DE", "IS3N.DE", "IUSN.DE", "4GLD.DE", "XAD6.DE"]
ticker_info = {
    "IWDA.AS": {"name":"iShares Core MSCI World UCITS ETF USD Acc.","isin":"IE00B4L5Y983"},
    "VWCE.DE": {"name":"Vanguard FTSE All-World U.ETF Reg. Shs USD Acc.","isin":"IE00BK5BQT80"},
    "IS3N.DE": {"name":"iShares Core MSCI Emerging Markets IMI UCITS ETF (Acc)","isin":"IE00BKM4GZ66"},
    "IUSN.DE": {"name":"iShares MSCI World Small Cap (Acc)","isin":"IE00BF4RFH31"},
    "4GLD.DE": {"name":"Xetra Gold ETC","isin":"DE000A0S9GB0"},
    "XAD6.DE": {"name":"Xtrackers Physical Silver ETC","isin":"DE000A1E0HS6"}
}

# --------------------------
# Funktionen
# --------------------------
def get_data(ticker):
    try:
        df = yf.Ticker(ticker).history(period=PERIOD)
        if df.empty or len(df) < 2:
            return None
        df.index = pd.to_datetime(df.index)
        return df
    except:
        return None

def calc_kpis(df):
    if df is None or len(df) < 2:
        return None, None, None, None, None, None
    close = df['Close']
    current = float(close.iloc[-1])
    ath = float(close.max())
    daily = float((close.iloc[-1]-close.iloc[-2])/close.iloc[-2]*100)
    monthly = float((close.iloc[-1]-close.iloc[max(0,len(close)-22)])/close.iloc[max(0,len(close)-22)]*100) if le*
