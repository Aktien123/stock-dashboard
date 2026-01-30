import streamlit as st
import yfinance as yf
import plotly.graph_objects as go

st.set_page_config(page_title="Stock Dashboard", layout="wide")
st.title("📊 Aktien Dashboard")

tickers = ["MSFT", "AAPL", "GOOGL", "AMZN", "TSLA", "NVDA"]

def get_data(ticker):
    try:
        df = yf.download(ticker, period="6mo", interval="1d")
        if df.empty or len(df) < 2:
            return None
        df.index = df.index.tz_localize(None)  # Zeitzone entfernen, damit Plotly x-Achse funktioniert
        return df
    except:
        return None

def create_line_chart(df, ticker):
    if df is None:
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index,
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

cols = st.columns(3)
for idx, ticker in enumerate(tickers):
    col = cols[idx % 3]
    df = get_data(ticker)
    fig = create_line_chart(df, ticker)
    with col:
        if df is None or fig is None:
            st.error(f"Keine Daten für {ticker} gefunden.")
        else:
            st.plotly_chart(fig, use_container_width=True)
