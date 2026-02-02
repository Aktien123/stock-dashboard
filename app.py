import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import datetime
import pytz
import time

# --------------------------
# Config
# --------------------------
st.set_page_config(page_title="ETF & ETC Dashboard", layout="wide")

PERIOD = "1y"
KPI_REFRESH_SEC = 45
CHART_REFRESH_SEC = 30*60  # 30 Minuten
TIMEZONE = "Europe/Berlin"

# --------------------------
# CSS für Header & Balken
# --------------------------
st.markdown(
    """
    <style>
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .progress-bar {
        width: 150px;  /* ca. 3cm */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------
# Tickerliste & Info
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
# Session State
# --------------------------
if 'last_kpi_update' not in st.session_state:
    st.session_state.last_kpi_update = time.time()
if 'last_chart_update' not in st.session_state:
    st.session_state.last_chart_update = time.time()
if 'data_cache' not in st.session_state:
    st.session_state.data_cache = {t: get_data(t) for t in tickers}

# --------------------------
# Header Layout
# --------------------------
header_container = st.container()
with header_container:
    cols = st.columns([3,2,1])
    with cols[0]:
        st.markdown("<h1 style='margin-bottom:0;'>ETF & ETC Dashboard</h1>", unsafe_allow_html=True)
    progress_ph = cols[1].progress(0)
    now_ph = cols[2].empty()

# --------------------------
# Dashboard Layout: Charts & KPIs
# --------------------------
rows = [st.columns(3) for _ in range(2)]
chart_phs, kpi_phs = [], []

for i, ticker in enumerate(tickers):
    row = rows[i//3]
    col = row[i%3]
    # Charts
    chart_ph = col.empty()
    df = st.session_state.data_cache[ticker]
    chart_ph.plotly_chart(create_line_chart(df), use_container_width=True)
    chart_phs.append(chart_ph)
    # KPIs
    kpi_ph = col.empty()
    current, ath, daily, monthly, yearly, delta_ath = calc_kpis(df)
    info = ticker_info.get(ticker, {"name": ticker, "isin": ""})
    kpi_ph.markdown(
        f"<b>{info['name']}</b><br>"
        f"Ticker: {ticker} &nbsp; ISIN: {info['isin']}<br>"
        f"**Aktueller Kurs:** {current:.2f} EUR<br>"
        f"**All Time High:** {ath:.2f} EUR<br>"
        f"**△ ATH:** {colorize(delta_ath)}<br>"
        f"**Tagesperformance:** {colorize(daily)}<br>"
        f"**Monatsperformance:** {colorize(monthly)}<br>"
        f"**Jahresperformance:** {colorize(yearly)}",
        unsafe_allow_html=True
    )
    kpi_phs.append(kpi_ph)

# --------------------------
# Endlos Loop für KPI, Balken & Charts
# --------------------------
while True:
    now = datetime.datetime.now(pytz.timezone(TIMEZONE))
    now_ph.markdown(f"**{now.strftime('%d.%m.%Y %H:%M')}**", unsafe_allow_html=True)

    elapsed_kpi = time.time() - st.session_state.last_kpi_update
    elapsed_chart = time.time() - st.session_state.last_chart_update

    # Balken (0→100% über KPI_REFRESH_SEC)
    progress = (elapsed_kpi % KPI_REFRESH_SEC) / KPI_REFRESH_SEC
    progress_ph.progress(progress)

    # KPI Update
    if elapsed_kpi >= KPI_REFRESH_SEC:
        st.session_state.last_kpi_update = time.time()
        for i, ticker in enumerate(tickers):
            df = st.session_state.data_cache[ticker]
            current, ath, daily, monthly, yearly, delta_ath = calc_kpis(df)
            kpi_phs[i].markdown(
                f"<b>{ticker_info[ticker]['name']}</b><br>"
                f"Ticker: {ticker} &nbsp; ISIN: {ticker_info[ticker]['isin']}<br>"
                f"**Aktueller Kurs:** {current:.2f} EUR<br>"
                f"**All Time High:** {ath:.2f} EUR<br>"
                f"**△ ATH:** {colorize(delta_ath)}<br>"
                f"**Tagesperformance:** {colorize(daily)}<br>"
                f"**Monatsperformance:** {colorize(monthly)}<br>"
                f"**Jahresperformance:** {colorize(yearly)}",
                unsafe_allow_html=True
            )

    # Chart Update alle 30min
    if elapsed_chart >= CHART_REFRESH_SEC:
        st.session_state.last_chart_update = time.time()
        st.session_state.data_cache = {t: get_data(t) for t in tickers}
        for i, ticker in enumerate(tickers):
            chart_phs[i].plotly_chart(create_line_chart(st.session_state.data_cache[ticker]), use_container_width=True)

    time.sleep(0.5)
