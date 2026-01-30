import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📊 Aktien Dashboard")

# --- Liste der 6 Aktien ---
tickers = ["MSFT", "AAPL", "GOOGL", "AMZN", "TSLA", "NVDA"]

# --- Helper Funktionen ---
def get_data(ticker):
    # Lädt 1 Jahr tägliche Daten
    df = yf.download(ticker, period="1y", interval="1d")
    df.dropna(inplace=True)
    return df

def calc_kpis(df):
    # 1️⃣ Prüfen, ob DataFrame leer
    if df.empty:
        return None, None, None, None, None
    
    # 2️⃣ Prüfen, ob Close-Spalte nur NaN enthält
    if df["Close"].isnull().all():
        return None, None, None, None, None

    # 3️⃣ KPIs berechnen
    current = df["Close"].iloc[-1]
    ath = df["Close"].max()
    
    # Tagesperformance
    if len(df) >= 2:
        daily = (df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2] * 100
    else:
        daily = None
    
    # Monatsperformance (ca. 21 Handelstage)
    if len(df) >= 22:
        monthly = (df["Close"].iloc[-1] - df["Close"].iloc[-21]) / df["Close"].iloc[-21] * 100
    else:
        monthly = None
    
    # Jahresperformance
    yearly = (df["Close"].iloc[-1] - df["Close"].iloc[0]) / df["Close"].iloc[0] * 100
    
    return current, ath, daily, monthly, yearly

def create_chart(df, ticker):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name=ticker, line=dict(color='blue')))
    fig.update_layout(height=250, margin=dict(l=10,r=10,t=30,b=10), title=ticker)
    return fig

# --- Layout: 3 Spalten ---
cols = st.columns(3)

for i, ticker in enumerate(tickers):
    col = cols[i % 3]  # Spalte wählen
    df = get_data(ticker)
    current, ath, daily, monthly, yearly = calc_kpis(df)
    fig = create_chart(df, ticker)

    # --- Anzeige ---
current, ath, daily, monthly, yearly = calc_kpis(df)

if current is None:
    st.error(f"Keine Daten für {ticker} gefunden.")
else:
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(f"**Aktueller Kurs:** {current:.2f}")
    st.markdown(f"**All Time High:** {ath:.2f}")
    if daily is not None:
        st.markdown(f"**Tagesperformance:** {daily:.2f}%")
    if monthly is not None:
        st.markdown(f"**Monatsperformance:** {monthly:.2f}%")
    st.markdown(f"**Jahresperformance:** {yearly:.2f}%")
    st.markdown("---")
