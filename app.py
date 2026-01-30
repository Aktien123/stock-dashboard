import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# --------------------------
# Streamlit Layout
# --------------------------
st.set_page_config(page_title="ETF & ETC Dashboard", layout="wide")

# --------------------------
# Skalierung auf 75% per CSS
# --------------------------
st.markdown(
    """
    <style>
    .main > div.block-container {
        transform: scale(0.75);
        transform-origin: top left;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --------------------------
# Header (kann durch Bild ersetzt werden)
# --------------------------
# st.title("📊 ETF & ETC Dashboard")
st.image("header.png", use_column_width=True)  # <-- eigenes Bild verwenden

# --------------------------
# Liste der 6 Ticker
# --------------------------
tickers = ["IWDA.AS", "VWCE.DE", "IS3N.DE", "IUSN.DE", "4GLD.DE", "XAD6.DE"]

# Mapping: Ticker → Name + ISIN
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
        df = yf.Ticker(ticker).history(period="1y")  # 1 Jahr
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
        xaxis_title="Datum",
        yaxis_title="Kurs",
        margin=dict(l=10,r=10,t=30,b=10),
        plot_bgcolor="rgba(0,0,0,0)"
    )
    return fig

# --------------------------
# Dashboard Layout: 2 Reihen x 3 Spalten
# --------------------------
rows = [st.columns(3) for _ in range(2)]

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
            # Überschrift: Name + Ticker + ISIN mit 4 Leerzeichen
            st.markdown(
                f"**{info['name']}**  \n<small>Ticker: {ticker}&nbsp;&nbsp;&nbsp;&nbsp;ISIN: {info['isin']}</small>",
                unsafe_allow_html=True
            )

            # Chart
            st.plotly_chart(fig, use_container_width=True)

            # KPI nebeneinander zentriert unter Chart
            kpi_cols = st.columns([1, 2, 2, 1])  # linke+rechte "Leerräume" für Zentrierung
            with kpi_cols[1]:
                st.markdown(f"**Aktueller Kurs:** {current:.2f}")
                st.markdown(f"
