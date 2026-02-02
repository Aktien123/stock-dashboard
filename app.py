import streamlit as st
from datetime import datetime
import pytz
import time

st.set_page_config(page_title="ETF & ETC Dashboard", layout="wide")

# KPI Update Intervall
KPI_UPDATE_SEC = 45

# Header Container
header_container = st.container()

# Fortschrittsbalken + Uhrzeit
progress_bar = header_container.progress(0)
time_display = header_container.empty()

# CSS für horizontale + vertikale Ausrichtung
st.markdown("""
<style>
.header-flex {
    display: flex;
    align-items: flex-end; /* vertikal unten bündig */
    justify-content: space-between; /* links: Titel, mitte: Balken, rechts: Datum */
}
.header-title {
    font-size: 2em;
    font-weight: bold;
}
.header-bar {
    width: 200px;  /* ca. 3cm */
}
.header-time {
    font-weight: bold;
    text-align: right;
}
</style>
""", unsafe_allow_html=True)

# Header HTML
header_container.markdown("""
<div class="header-flex">
    <div class="header-title">ETF & ETC Dashboard</div>
    <div class="header-bar" id="progress-bar"></div>
    <div class="header-time" id="time-display">--:--</div>
</div>
""", unsafe_allow_html=True)

# --------------------------
# Endlosschleife für Balken + Uhrzeit
# --------------------------
tz = pytz.timezone("Europe/Berlin")
while True:
    for sec in range(KPI_UPDATE_SEC + 1):
        progress_bar.progress(sec / KPI_UPDATE_SEC)
        now_str = datetime.now(tz).strftime("%d.%m.%Y %H:%M")
        time_display.markdown(f"<div style='text-align: right'>{now_str}</div>", unsafe_allow_html=True)
        time.sleep(1)
        if sec == KPI_UPDATE_SEC:
            progress_bar.progress(0)  # sofort zurücksetzen
