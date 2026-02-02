import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pytz
import time

# --------------------------
# Grundwerte
# --------------------------
KPI_UPDATE_SEC = 45
CHART_UPDATE_MIN = 30
tz = pytz.timezone("Europe/Berlin")

# --------------------------
# Header CSS für Layout
# --------------------------
st.markdown("""
<style>
.header-flex {
    display: flex;
    align-items: flex-end; /* vertikal unten bündig */
    justify-content: space-between; /* links: Titel, mitte: Balken, rechts: Uhrzeit */
}
.header-title {
    font-size: 2em;
    font-weight: bold;
}
.header-bar-container {
    width: 200px; /* ca. 3cm */
}
.header-time {
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# --------------------------
# Header Container
# --------------------------
header_cols = st.columns([3,1,2])  # relative Breite: Titel | Balken | Uhrzeit
with header_cols[0]:
    st.markdown('<div class="header-title">ETF & ETC Dashboard</div>', unsafe_allow_html=True)
with header_cols[1]:
    progress_bar = st.progress(0)
with header_cols[2]:
    time_display = st.empty()

# --------------------------
# Funktion: Fortschrittsbalken + Uhrzeit aktualisieren
# --------------------------
def update_header_and_kpis(update_kpi_callback):
    while True:
        for sec in range(KPI_UPDATE_SEC + 1):
            # Balken aktualisieren
            progress_bar.progress(sec / KPI_UPDATE_SEC)
            # Uhrzeit aktualisieren
            now_str = datetime.now(tz).strftime("%H:%M")
            time_display.markdown(f"<div class='header-time'>{now_str}</div>", unsafe_allow_html=True)
            time.sleep(1)
            # Wenn Balken 100%, KPI aktualisieren und Balken wieder auf 0
            if sec == KPI_UPDATE_SEC:
                update_kpi_callback()
                progress_bar.progress(0)
