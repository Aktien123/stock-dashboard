import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📊 Aktien Dashboard")

# --- Liste der Ticker ---
tickers = ["IWDA.AS"]  # hier kannst du weitere hinzufügen

# --- Mapping: Ticker → Name + ISIN ---
ticker_info = {
    "IWDA.AS": {
        "name": "iShares Core MSCI World ETF",
        "isin": "IE00B4L5Y983"
    }
    # Weitere Ticker können hier ergänzt werden:
    # "MSFT": {"name": "Microsoft Corp", "isin": "..."}
}

# --------------------------
# Funktionen
# --------------------------
def get_data(ticker):
    try:
        df = yf.Ticker(ticker).history(period="6mo")
        if df.empty or len(df) < 2:
            return None
        df.index = pd.to_datetime(df.index)
        return df
    except:
        return None

def calc_kpis(df):
    if df is None or len(df) < 2:
        return None, None, None, None, None
    close = df['Close']
    current = float(close.iloc[-1])
    ath = float(close.max())
    daily = float((close.iloc[-1]-close.iloc[-2])/close.iloc[-2]*100)
    monthly = float((close.iloc[-1]-close.iloc[max(0,len(close)-22)])/close.iloc[max(0,len(close)-22)]*100) if len(close) >=22 else None
    yearly = float((close.iloc[-1]-close.iloc[0])/close.iloc[0]*100)
    return current, ath, daily, monthly, yearly

def colorize(val):
    try:
        val = float(val)
    except (TypeError, ValueError):
        return "n/a"
    color = "green" if val >= 0 else "red"
    return f"<span style='color: {color}'>{val:.2f}%</span>"

def create_line_chart(df):
    if df is None or len(df) < 2:
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
        y=df['Close'],
        mode='lines',
        line=dict(color='blue')
    ))
    fig.update_layout(
        height=300,
        xaxis_title="Datum",
        yaxis_title="Kurs EUR",
        margin=dict(l=10,r=10,t=30,b=10)
    )
    return fig

# --------------------------
# Dashboard Layout
# --------------------------
cols = st.columns(3)
for idx, ticker in enumerate(tickers):
    col = cols[idx % 3]
    df = get_data(ticker)
    current, ath, daily, monthly, yearly = calc_kpis(df)
    fig = create_line_chart(df)

    info = ticker_info.get(ticker, {"name": ticker, "isin": ""})

    with col:
        if df is None or fig is None:
            st.error(f"Keine Daten für {ticker} gefunden.")
        else:
            # Überschrift in zwei Zeilen
            st.markdown(f"**{info['name']}**  \n<small>Ticker: {ticker}  ISIN: {info['isin']}</small>", unsafe_allow_html=True)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"**Aktueller Kurs:** {current:.2f}")
            st.markdown(f"**All Time High:** {ath:.2f}")
            st.markdown(f"**Tagesperformance:** {colorize(daily)}", unsafe_allow_html=True)
            st.markdown(f"**Monatsperformance:** {colorize(monthly)}", unsafe_allow_html=True)
            st.markdown(f"**Jahresperformance:** {colorize(yearly)}", unsafe_allow_html=True)
            st.markdown("---")
