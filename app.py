import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📊 Aktien Dashboard")

tickers = ["MSFT", "AAPL", "GOOGL", "AMZN", "TSLA", "NVDA"]

def get_data(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d")
        df = df[['Close']].copy()  # Nur Close-Werte
        df.dropna(inplace=True)
        df.index = pd.to_datetime(df.index)  # Index in datetime umwandeln
        df.reset_index(inplace=True)
        df.rename(columns={'index':'Date'}, inplace=True)
        return df
    except:
        return None

def calc_kpis(df):
    if df is None or df.empty:
        return None, None, None, None, None
    close = df['Close']
    current = float(close.iloc[-1])
    ath = float(close.max())
    daily = (close.iloc[-1]-close.iloc[-2])/close.iloc[-2]*100 if len(close) >=2 else None
    monthly = (close.iloc[-1]-close.iloc[-21])/close.iloc[-21]*100 if len(close) >=22 else None
    yearly = (close.iloc[-1]-close.iloc[0])/close.iloc[0]*100
    return current, ath, daily, monthly, yearly

def create_line_chart(df, ticker):
    if df is None or df.empty:
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['Date'],
        y=df['Close'],
        mode='lines',
        line=dict(color='blue'),
        name=ticker
    ))
    fig.update_layout(
        height=300,
        title=ticker,
        xaxis_title="Datum",
        yaxis_title="Kurs USD",
        margin=dict(l=10,r=10,t=30,b=10)
    )
    return fig

def colorize(val):
    # val kann None oder Series sein
    try:
        val = float(val)
    except (TypeError, ValueError):
        return "n/a"
    color = "green" if val >= 0 else "red"
    return f"<span style='color: {color}'>{val:.2f}%</span>"


cols = st.columns(3)
for idx, ticker in enumerate(tickers):
    col = cols[idx % 3]
    df = get_data(ticker)
    current, ath, daily, monthly, yearly = calc_kpis(df)
    fig = create_line_chart(df, ticker)

    with col:
        if current is None or fig is None:
            st.error(f"Keine Daten für {ticker} gefunden.")
        else:
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(f"**Aktueller Kurs:** {current:.2f}")
            st.markdown(f"**All Time High:** {ath:.2f}")
            st.markdown(f"**Tagesperformance:** {colorize(daily)}", unsafe_allow_html=True)
            st.markdown(f"**Monatsperformance:** {colorize(monthly)}", unsafe_allow_html=True)
            st.markdown(f"**Jahresperformance:** {colorize(yearly)}", unsafe_allow_html=True)
            st.markdown("---")
