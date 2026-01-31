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
# Header + Zeitraum Toggle direkt hinter der Überschrift
# --------------------------
col = st.columns(1)[0]

with col:
    # Flexbox für Inline-Anordnung von Titel + Toggle
    st.markdown("""
    <div style="display: flex; align-items: center;">
        <h3 style="margin-right: 10px;">ETF & ETC Dashboard</h3>
        <div>
    """, unsafe_allow_html=True)

    selected_period_label = st.radio(
        "",  # Kein Label
        options=list(period_map.keys()),
        horizontal=True,
        index=1  # Default = 1Y
    )

    st.markdown("</div></div>", unsafe_allow_html=True)

selected_period = period_map[selected_period_label]

# --------------------------
# Skalierung auf 75% per CSS
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
    current = float(close.iloc[-1])
    ath = float(close.max())
    daily = float((close.iloc[-1] - close.iloc[-2]) / close.iloc[-2] * 100)

    # Monatsperformance (22 Handelstage)
    if len(close) >= 22:
        monthly = float((close.iloc[-1] - close.iloc[-22]) / close.iloc[-22] * 100)
    else:
        monthly = None

    # Jahresperformance
    yearly = float((close.iloc[-1] - close.iloc[0]) / close.iloc[0] * 100)

    # Delta zum ATH
    delta_ath = float((current - ath) / ath * 100)

    return current, ath, daily, monthly, yearly, delta_ath

def colorize(val):
    try:
        val = float(val)
    except (TypeError, ValueError):
        return "n/a"
    color = "green" if val >= 0 else "red"
    return f"<span style='color: {color}'>{val:.2f}%</span>"

def create_line_chart(df, daily=None):
    if
