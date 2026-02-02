import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# ==========================================================
# Streamlit Layout
# ==========================================================
st.set_page_config(page_title="ETF & ETC Dashboard", layout="wide")

PERIOD = "1y"

# --------------------------
# Skalierung
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

st.title("ETF & ETC Dashboard")

# ==========================================================
# Ticker
# ==========================================================
tickers = ["IWDA.AS", "VWCE.DE", "IS3N.DE", "IUSN.DE", "4GLD.DE", "XAD6.MI"]

ticker_info = {
    "IWDA.AS": {"name":"iShares Core MSCI World UCITS ETF USD Acc.","isin":"IE00B4L5Y983"},
    "VWCE.DE": {"name":"Vanguard FTSE All-World U.ETF Reg. Shs USD Acc.","isin":"IE00BK5BQT80"},
    "IS3N.DE": {"name":"iShares Core MSCI Emerging Markets IMI UCITS ETF (Acc)","isin":"IE00BKM4GZ66"},
    "IUSN.DE": {"name":"iShares MSCI World Small Cap (Acc)","isin":"IE00BF4RFH31"},
    "4GLD.DE": {"name":"Xetra Gold ETC","isin":"DE000A0S9GB0"},
    "XAD6.MI": {"name":"Xtrackers Physical Silver ETC","isin":"DE000A1E0HS6"}
}

# ==========================================================
# Daten – sauber getrennt + Cache
# ==========================================================

@st.cache_data(ttl=30 * 60)  # 30 Minuten → Historie & Chart
def get_history_1y(ticker):
    try:
        df = yf.Ticker(ticker).history(period=PERIOD)
        if df.empty or len(df) < 22:
            return None
        df.index = pd.to_datetime(df.index)
        return df
    except:
        return None


@st.cache_data(ttl=45)  # 45 Sekunden → aktuelle KPIs
def get_latest_data(ticker):
    try:
        df = yf.Ticker(ticker).history(period="2d", interval="1d")
        if df.empty or len(df) < 2:
            return None
        return df
    except:
        return None


# ==========================================================
# KPI-Logik (richtig & stabil)
# ==========================================================
def calc_kpis(latest_df, hist_df):
    close_latest = latest_df["Close"]
    close_hist = hist_df["Close"]

    current = float(close_latest.iloc[-1])
    prev = float(close_latest.iloc[-2])

    daily = (current - prev) / prev * 100

    ath = float(close_hist.max())
    delta_ath = (current - ath) / ath * 100

    monthly = (
        (current - close_hist.iloc[-22]) / close_hist.iloc[-22] * 100
        if len(close_hist) >= 22 else None
    )

    yearly = (current - close_hist.iloc[0]) / close_hist.iloc[0] * 100

    return current, daily, monthly, yearly, ath, delta_ath


def colorize(val):
    try:
        val = float(val)
    except:
        return "n/a"
    color = "green" if val >= 0 else "red"
    return f"<span style='color:{color}'>{val:.2f}%</span>"


def create_line_chart(df, daily):
    line_color = "green" if daily >= 0 else "red"

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df["Close"],
        mode="lines",
        line=dict(color=line_color, width=2),
        hovertemplate="Datum: %{x|%d.%m.%Y}<br>Kurs: %{y:.2f} EUR<extra></extra>"
    ))

    fig.update_layout(
        height=300,
        yaxis_title="EUR",
        margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig


# ==========================================================
# Dashboard
# ==========================================================
rows = [st.columns(3) for _ in range(2)]

for i, ticker in enumerate(tickers):
    row = rows[i // 3]
    col = row[i % 3]

    hist_df = get_history_1y(ticker)
    latest_df = get_latest_data(ticker)

    with col:
        if hist_df is None or latest_df is None:
            st.error(f"Keine Daten für {ticker}")
            continue

        current, daily, monthly, yearly, ath, delta_ath = calc_kpis(
            latest_df, hist_df
        )

        fig = create_line_chart(hist_df, daily)
        info = ticker_info[ticker]

        st.markdown(
            f"**{info['name']}**  \n"
            f"<small>Ticker: {ticker}&nbsp;&nbsp;&nbsp;&nbsp;ISIN: {info['isin']}</small>",
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
