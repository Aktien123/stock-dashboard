import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📊 Aktien Dashboard")

# --- Liste der 6 Aktien ---
tickers = ["MSFT", "AAPL", "GOOGL", "AMZN", "TSLA", "NVDA"]

# --- Funktionen ---
def get_data(ticker):
    try:
        df = yf.download(ticker, period="1y", interval="1d")
        df.dropna(inplace=True)
        return df
    except:
        return None

def calc_kpis(df):
    if df is None or df.empty:
        return None, None, None, None, None
    
    # Sicherstellen, dass Close-Spalte Zahlen enthält
    if df["Close"].isnull().all():
        return None, None, None, None, None

    current = df["Close"].iloc[-1]
    ath = df["Close"].max()
    
    daily = (df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2] * 100 if len(df) >= 2 else None
    monthly = (df["Close"].iloc[-1] - df["Close"].iloc[-21]) / df["Close"].iloc[-21] * 100 if len(df) >= 22 else None
    yearly = (df["Close"].iloc[-1] - df["Close"].iloc[0]) / df["Close"].iloc[0] * 100
    
    return float(current), float(ath), float(daily) if daily is not None else None, float(monthly) if monthly is not None else None, float(yearly)

def create_chart(df, ticker):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["Close"], name=ticker, line=dict(color='blue')))
    fig.update_layout(height=250, margin=dict(l=10,r=10,t=30,b=10), title=ticker)
    return fig

# --- Layout: 3 Spalten ---
cols = st.columns(3)

for i, ticker in enumerate(tickers):
    col = cols[i % 3]
    df = get_data(ticker)
    current, ath, daily, monthly, yearly = calc_kpis(df)
    fig = create_chart(df, ticker)
    
    with col:
        if current is None:
            st.error(f"Keine Daten für {ticker} gefunden.")
        else:
            st.plotly_chart(fig, use_container_width=True)
            
            # KPIs nur anzeigen, wenn Zahlen vorhanden
            st.markdown(f"**Aktueller Kurs:** {current:.2f}" if current is not None else "**Aktueller Kurs:** n/a")
            st.markdown(f"**All Time High:** {ath:.2f}" if ath is not None else "**All Time High:** n/a")
            st.markdown(f"**Tagesperformance:** {daily:.2f}%" if daily is not None else "**Tagesperformance:** n/a")
            st.markdown(f"**Monatsperformance:** {monthly:.2f}%" if monthly is not None else "**Monatsperformance:** n/a")
            st.markdown(f"**Jahresperformance:** {yearly:.2f}%" if yearly is not None else "**Jahresperformance:** n/a")
            
            st.markdown("---")
