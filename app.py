import streamlit as st
import time
import datetime
import pytz

KPI_REFRESH_SEC = 45
TIMEZONE = "Europe/Berlin"

if 'last_kpi_update' not in st.session_state:
    st.session_state.last_kpi_update = time.time()

progress_placeholder = st.empty()
now_placeholder = st.empty()

while True:
    now = datetime.datetime.now(pytz.timezone(TIMEZONE))
    now_placeholder.markdown(f"**{now.strftime('%d.%m.%Y %H:%M')}**", unsafe_allow_html=True)

    elapsed = time.time() - st.session_state.last_kpi_update
    progress = (elapsed % KPI_REFRESH_SEC) / KPI_REFRESH_SEC  # modulo sorgt für Neustart bei 0%
    progress_placeholder.progress(progress)

    # Wenn 45 Sekunden vergangen → KPI Update
    if elapsed >= KPI_REFRESH_SEC:
        st.session_state.last_kpi_update = time.time()
        # Hier kannst du deine KPI neu laden
        # z.B. st.experimental_rerun() oder Funktionen aufrufen

    time.sleep(0.5)  # Update alle 0,5 Sekunde
