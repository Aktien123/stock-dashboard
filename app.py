import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import pytz
import time

# --------------------------
# Streamlit Layout
# --------------------------
st.set_page_config(page_title="ETF & ETC Dashboard", layout="wide")

# --------------------------
# Zeitraum & Update Intervall
# --------------------------
PERIOD = "1y"
KPI_UPDATE_SEC = 45      # KPI alle 45 Sekunden
CHART_UPDATE_MIN = 30    # Charts alle 30 Minuten

# --------------------------
# Header Layout
# --------------------------
header_cols = st.columns([2,1,2])
with header_cols[0]:
    st.title("ETF & ETC Dashboard")
# Mittlerer Balken
progress_bar = header_cols[1].progress(0)
# Uhrzeit & Datum rechts
tz = pytz.timezone("Europe/Berlin")
now_str = datetime.now(tz).strftime("%d.%m.%Y %H:%M")
time_display = header_cols[2].empty()
time_display.markdown(f"<div style='text-align: right; font-weight:bold'>{now_str}</div>", unsafe_allow_html=True)

st.markdown("---")

# --------------------------
# Liste der 6 Ticker
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
    df = yf.Ticker(ticker).history(period=PERIOD)
    df.index = pd.to_datetime(df.index)
    return df

def calc_kpis(df):
    close = df['Close']
    current = close.iloc[-1]
    ath = close.max()
    daily = (close.iloc[-1]-close.iloc[-2])/close.iloc[-2]*100
    monthly = (close.iloc[-1]-close.iloc[max(0,len(close)-22)])/close.iloc[max(0,len(close)-22)]*100 if len(close)>=22 else None
    yearly = (close.iloc[-1]-close.iloc[0])/close.iloc[0]*100
    delta_ath = (current - ath)/ath*100
    return current, ath, daily, monthly, yearly, delta_ath

def colorize(val):
    color = "green" if val>=0 else "red"
    return f"<span style='color:{color}'>{val:.2f}%</span>"

def create_line_chart(df, daily=None):
    line_color = "green" if daily>=0 else "red"
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', line=dict(color=line_color, width=2)))
    fig.update_layout(height=300, yaxis_title="EUR", margin=dict(l=10,r=10,t=30,b=10), plot_bgcolor="rgba(0,0,0,0)")
    return fig

# --------------------------
# Container für Charts & KPIs
# --------------------------
chart_containers = [st.empty() for _ in tickers]

def render_dashboard():
    rows = [st.columns(3) for _ in range(2)]
    for i, ticker in enumerate(tickers):
        row = rows[i // 3]
        col = row[i % 3]
        df = get_data(ticker)
        current, ath, daily, monthly, yearly, delta_ath = calc_kpis(df)
        fig = create_line_chart(df, daily=daily)
        info = ticker_info[ticker]
        with col:
            st.markdown(f"**{info['name']}**  \n<small>Ticker: {ticker}&nbsp;&nbsp;&nbsp;&nbsp;ISIN: {info['isin']}</small>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            kpi_cols = st.columns(2)
            with kpi_cols[0]:
                st.markdown(f"**Aktueller Kurs:** {current:.2f} EUR")
                st.markdown(f"**All Time High:** {ath:.2f} EUR")
                st.markdown(f"**△ ATH:** {colorize(delta_ath)}", unsafe_allow_html=True)
            with kpi_cols[1]:
                st.markdown(f"**Tagesperformance:** {colorize(daily)}", unsafe_allow_html=True)
                st.markdown(f"**Monatsperformance:** {colorize(monthly)}", unsafe_allow_html=True)
                st.markdown(f"**Jahresperformance:** {colorize(yearly)}", unsafe_allow_html=True)
            st.markdown("---")

# --------------------------
# Initiales Rendern
# --------------------------
render_dashboard()

# --------------------------
# Endlos-Balken + KPI Update
# --------------------------
while True:
    for sec in range(KPI_UPDATE_SEC+1):
        progress_bar.progress(sec / KPI_UPDATE_SEC)
        # Uhrzeit aktualisieren
        now_str = datetime.now(pytz.timezone("Europe/Berlin")).strftime("%d.%m.%Y %H:%M")
        time_display.markdown(f"<div style='text-align: right; font-weight:bold'>{now_str}</div>", unsafe_allow_html=True)
        time.sleep(1)
        if sec == KPI_UPDATE_SEC:
            render_dashboard()
            progress_bar.progress(0)
