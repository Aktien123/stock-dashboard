import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import time

# --------------------------
# Streamlit Layout
# --------------------------
st.set_page_config(page_title="ETF & ETC Dashboard", layout="wide")

PERIOD = "1y"
KPI_UPDATE_INTERVAL = 45  # Sekunden
CHART_UPDATE_INTERVAL = 30 * 60  # Sekunden

# --------------------------
# Liste der Ticker & Mapping
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
    return current, ath, daily, monthly, yearly, delta_ath

def colorize(val):
    try:
        val = float(val)
    except (TypeError, ValueError):
        return "n/a"
    color = "green" if val >= 0 else "red"
    return f"<span style='color: {color}'>{val:.2f}%</span>"

def create_line_chart(df, daily=None):
    if df is None or len(df) < 2:
        return None
    line_color = "green" if daily is not None and daily >= 0 else "red"
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        line=dict(color=line_color, width=2),
        hovertemplate='Datum: %{x|%d.%m.%Y}<br>Kurs: %{y:.2f} EUR<extra></extra>'
    ))
    fig.update_layout(
        height=300,
        yaxis_title="EUR",
        margin=dict(l=10,r=10,t=30,b=10),
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

# --------------------------
# Header Layout
# --------------------------
header_cols = st.columns([1,1,1])
with header_cols[0]:
    st.title("ETF & ETC Dashboard")

with header_cols[1]:
    progress_bar = st.progress(0)

with header_cols[2]:
    tz_berlin = pytz.timezone("Europe/Berlin")
    st.markdown(f"<div style='text-align:right; font-size:16px'>{datetime.now(tz_berlin).strftime('%H:%M')}</div>", unsafe_allow_html=True)

# --------------------------
# Charts & KPI Container
# --------------------------
charts_container = st.container()
kpi_container = st.container()

# --------------------------
# Initial Data laden
# --------------------------
data_dict = {}
kpi_dict = {}
for ticker in tickers:
    df = get_data(ticker)
    data_dict[ticker] = df
    kpi_dict[ticker] = calc_kpis(df)

# --------------------------
# Funktion: Charts & KPI rendern
# --------------------------
def render_charts_and_kpis():
    rows = [charts_container.columns(3) for _ in range(2)]
    for i, ticker in enumerate(tickers):
        row = rows[i // 3]
        col = row[i % 3]

        df = data_dict[ticker]
        current, ath, daily, monthly, yearly, delta_ath = kpi_dict[ticker]
        fig = create_line_chart(df, daily=daily)
        info = ticker_info.get(ticker, {"name": ticker, "isin": ""})

        with col:
            if df is None or fig is None:
                st.error(f"Keine Daten für {ticker} gefunden.")
            else:
                st.markdown(
                    f"**{info['name']}**  \n<small>Ticker: {ticker}&nbsp;&nbsp;&nbsp;&nbsp;ISIN: {info['isin']}</small>",
                    unsafe_allow_html=True
                )
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
# Initial Render
# --------------------------
render_charts_and_kpis()

# --------------------------
# Endlos Schleife für KPI Update & Balken
# --------------------------
last_chart_update = datetime.now()
while True:
    start_time = time.time()

    # --- KPI Update alle 45 Sekunden ---
    for ticker in tickers:
        df = get_data(ticker)
        data_dict[ticker] = df
        kpi_dict[ticker] = calc_kpis(df)

    render_charts_and_kpis()

    # --- Chart Update alle 30 Minuten ---
    if (datetime.now() - last_chart_update).total_seconds() > CHART_UPDATE_INTERVAL:
        for ticker in tickers:
            df = get_data(ticker)
            data_dict[ticker] = df
        last_chart_update = datetime.now()

    # --- Balken Animation ---
    for sec in range(KPI_UPDATE_INTERVAL+1):
        progress = sec / KPI_UPDATE_INTERVAL
        progress_bar.progress(progress)
        st.markdown(f"<div style='text-align:right; font-size:16px'>{datetime.now(tz_berlin).strftime('%H:%M')}</div>", unsafe_allow_html=True)
        time.sleep(1)

