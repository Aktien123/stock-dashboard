import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import datetime
import pytz

# --------------------------
# Einstellungen
# --------------------------
st.set_page_config(page_title="ETF & ETC Dashboard", layout="wide")
PERIOD = "1y"
REFRESH_SEC = 45  # Refresh Interval
TIMEZONE = "Europe/Berlin"

# --------------------------
# CSS Skalierung
# --------------------------
st.markdown("""
    <style>
    .main > div.block-container {
        padding-top: 0rem;
        transform: scale(0.75);
        transform-origin: top left;
    }
    </style>
""", unsafe_allow_html=True)

# --------------------------
# Header + Balken + Datum in einer Zeile
# --------------------------
header_col1, header_col2, header_col3 = st.columns([3,1,3])
with header_col1:
    st.title("ETF & ETC Dashboard")
with header_col2:
    progress_bar_placeholder = st.empty()  # hier kommt der Balken hin
with header_col3:
    now_placeholder = st.empty()  # hier kommt Datum/Zeit hin

# --------------------------
# Liste der Ticker & Infos
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
    monthly = float((close.iloc[-1]-close.iloc[max(0,len(close)-22)])/close.iloc[max(0,len(close)-22)]*100) if len(close) >=22 else None
    yearly = float((close.iloc[-1]-close.iloc[0])/close.iloc[0]*100)
    delta_ath = float((current - ath) / ath * 100)
    return current, ath, daily, monthly,
