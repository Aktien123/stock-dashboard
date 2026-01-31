# --------------------------
# Header + Zeitraum Toggle nebeneinander, inline + vertikal mittig
# --------------------------
col_title, col_toggle = st.columns([6, 1])  # 6:1 → Überschrift bekommt mehr Platz

with col_title:
    st.markdown("### ETF & ETC Dashboard", unsafe_allow_html=True)

with col_toggle:
    selected_period_label = st.radio(
        "",
        options=list(period_map.keys()),
        horizontal=True,
        index=1
    )

# Toggle Wert in period_map umwandeln
selected_period = period_map[selected_period_label]

# --------------------------
# Optional: CSS für vertikale Zentrierung
# --------------------------
st.markdown("""
<style>
[data-testid="stHorizontalBlock"] {
    align-items: center;
}
</style>
""", unsafe_allow_html=True)
