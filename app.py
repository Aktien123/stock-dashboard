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

    close_series = df["Close"].dropna()
    if len(close_series) == 0:
        return None, None, None, None, None

    current = float(close_series.iloc[-1])
    ath = float(close_series.max())

    daily = (close_series.iloc[-1] - close_series.iloc[-2]) / close_series.iloc[-2] * 100 if len(close_series) >= 2 else None
    monthly = (close_series.iloc[-1] - close_series.iloc[-21]) / close_series.iloc[-21] * 100 if len(close_series) >= 22 else None
    yearly = (close_series.iloc[-1] - close_series.iloc[0]) / close_series.iloc[0] * 100

    daily = float(daily) if daily is not None else None
    monthly = float(monthly) if monthly is not None else None
    yearly = float(yearly) if yearly is not None else None

    return current, ath, daily, monthly, yearly

def create_chart(df, ticker):
    if df is None or df.empty or df["Close"].dropna().empty:
        return None

    df_chart = df[["Close"]].copy()
    df_chart = df_chart.reset_index()  # Index (Datum) → Spalte
    if "Date" not in df_chart.columns:
        df_chart.rename(columns={df_chart.columns[0]: "Date"}, inplace=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_chart["Date"],
        y=df_chart["Close"],
        name=ticker,
        line=dict(color='blue')
    ))
    fig.update_layout(
        height=250,
        margin=dict(l=10,r=10,t=30,b=10),
        title=ticker,
        xaxis_title="Datum",
        yaxis_title="Kurs USD"
    )
    return fig

def colorize(val):
    if val is None:
        return "n/a"
    color = "green" if val >= 0 else "red"
    return f"<span style='color: {color}'>{val:.2f}%</span>"

# --- Layout: 3 Spalten ---
cols = st.columns(3)
for idx, ticker in enumerate(tickers):
    col = cols[idx % 3]
    df = get_data(ticker)
    current, ath, daily, monthly, yearly = calc_kpis(df)
    fig = create_chart(df, ticker)

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
