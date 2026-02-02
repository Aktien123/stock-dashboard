import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime
import time

# ==============================
# Streamlit Config
# ==============================
st.set_page_config(page_title="ETF & ETC Dashboard", layout="wide")

PERIOD = "1y"
REFRESH_SEC = 45  # KPI-Refresh alle 45 Sekunden

# --------------------------
# CSS für Layout und Balken
# --------------------------
st.markdown("""
<style>
.header-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: flex-start;
}

.header-top {
    display: flex;
    justify-content: space-between;
    width: 100%;
    align-items: center;
}

#refresh-bar {
    height: 15px;
    width: 300px;
    background-color: lightgray;
    border-radius: 5px;
    margin: 10px 0px;
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
# Platzhalter
# --------------------------
header_placeholder = st.empty()
refresh_bar_placeholder = st.empty()
date_placeholder = st.empty()
dashboard_placeholder = st.empty()

# --------------------------
# Dashboard Loop
# --------------------------
while True:
    # --------------------------
    # Header + Balken + Datum
    # --------------------------
    header_placeholder.markdown(f"""
    <div class="header-container">
        <div class="header-top">
            <h1>ETF & ETC Dashboard</h1>
            <div>{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</div>
        </div>
        <div id="refresh-bar">
            <div id="refresh-bar-fill" style="width:0%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # --------------------------
    # KPI & Charts
    # --------------------------
    dashboard_container = dashboard_placeholder.container()
    rows = [dashboard_container.columns(3) for _ in range(2)]

    for i, ticker in enumerate(tickers):
        row = rows[i // 3]
        col = row[i % 3]

        df = get_data(ticker)
        current, ath, daily, monthly, yearly, delta_ath = calc_kpis(df)
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
    # Refresh-Balken Animation 45s
    # --------------------------
    for sec in range(REFRESH_SEC):
        fill_pct = int((sec+1)/REFRESH_SEC*100)
        refresh_bar_placeholder.markdown(
            f"""
            <div id="refresh-bar">
                <div id="refresh-bar-fill" style="width:{fill_pct}%"></div>
            </div>
            """, unsafe_allow_html=True
        )
        # Datum + Uhrzeit oben rechts
        header_placeholder.markdown(f"""
        <div class="header-container">
            <div class="header-top">
                <h1>ETF & ETC Dashboard</h1>
                <div>{datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</div>
            </div>
            <div id="refresh-bar">
                <div id="refresh-bar-fill" style="width:{fill_pct}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(1)
