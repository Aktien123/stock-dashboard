import streamlit as st
from datetime import datetime
import pytz
import time

st.set_page_config(page_title="ETF & ETC Dashboard", layout="wide")

KPI_UPDATE_SEC = 45
tz = pytz.timezone("Europe/Berlin")

# Header Container
header = st.container()
progress_bar = header.progress(0)
time_display = header.empty()

# CSS für horizontale und vertikale Ausrichtung
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
.header-bar {
    width: 200px; /* ca. 3cm */
}
.header-time {
    text-align: right;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# HTML Header
header.markdown("""
<div class="header-flex">
    <div class="header-title">ETF & ETC Dashboard</div>
    <div class="header-bar"></div>
    <div class="header-time" id="time-display">--:--</div>
</div>
""", unsafe_allow_html=True)

# Endlosschleife für Balken + Uhrzeit
while True:
    for sec in range(KPI_UPDATE_SEC + 1):
        progress_bar.progress(sec / KPI_UPDATE_SEC)
        now_str = datetime.now(tz).strftime("%H:%M")
        time_display.markdown(f"<div style='text-align: right'>{now_str}</div>", unsafe_allow_html=True)
        time.sleep(1)
        if sec == KPI_UPDATE_SEC:
            progress_bar.progress(0)  # Balken sofort wieder auf 0
