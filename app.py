import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --------------------------
# Streamlit Layout
# --------------------------
st.set_page_config(page_title="ETF & ETC Dashboard", layout="wide")

# --------------------------
# Zeitraum Mapping
# --------------------------
period_map = {
    "6M": "6mo",
    "1Y": "1y",
    "3Y": "3y"
}

# --------------------------
# Header + Zeitraum Toggle nebeneinander
# --------------------------
col_title, col_toggle = st.columns([6, 1])  # Überschrift 6 Einheiten, Toggle 1 Einheit

with col_title:
    st.markdown("### ETF & ETC Dashboard", unsafe_allow_html=True)

with col_toggle:
    selected_period_label = st.radio(
        "",  # Kein Label, damit inline
        options=list(period_map.keys()),
        horizontal=True,
        index=1  # Default = 1Y
    )

selected_period = period_map[selected_period_label]

# --------------------------
# Optional: CSS für vertikale Zentrierung des Toggles
# --------------------------
st.markdown("""
<style>
[data-testid="stHorizontalBlock"] {
    align-items: center;
}
</style>
""", unsafe_allow_html=True)

# --------------------------
# Skalierung auf 75% per CSS
# --------------------------
st.markdown(
    """
    <style>
    .main > div.block-container {
        padding-top: 0rem;
        transform: scale(0.75);
        transform-origin: top left;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------
# Liste der 6 Ticker
# --------------------------
tickers = ["IWDA.AS", "VWCE.DE", "IS3N.DE", "IUSN.DE", "4GLD.DE", "XAD6.DE"]

# Mapping: Ticker → Name + ISIN
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
def get_data(ticker, period):
    try:
        df = yf.Ticker(ticker).history(period=period)
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
    current = float(close.i
