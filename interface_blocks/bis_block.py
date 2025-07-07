# interface_blocks/bis_block.py – v2025-07-08 corrigé
# ---------------------------------------------------------------------
# • Bloc interface BIS – REER, compatible fusion intelligente
# ---------------------------------------------------------------------

import streamlit as st
from core.bis_loader import load_bis_reer_data, get_filter_options, filter_bis_data

@st.cache_data(show_spinner=False)
def load_bis_reer_cached():
    return load_bis_reer_data()

def display_bis_block():
    st.markdown("#### 1 – Select filters")
    with st.spinner("🔄 Loading BIS REER data..."):
        df_bis = load_bis_reer_cached()
        opts = get_filter_options(df_bis)

    # Interface de sélection (métadonnées)
    c1, c2, c3 = st.columns(3)
    ref = c1.selectbox("Reference Area", opts["Reference area"])
    freq = c2.selectbox("Frequency", opts["Frequency"])
    type_ = c3.selectbox("Type", opts["Type"])

    c4, c5 = st.columns(2)
    basket = c4.selectbox("Basket", opts["Basket"])
    unit = c5.selectbox("Unit", opts["Unit"])

    # Sélection des colonnes de dates disponibles
    date_cols = [c for c in df_bis.columns if c not in [
        "Dataflow ID", "Timeseries Key", "Frequency", "Type", "Basket", "Reference area", "Unit"
    ]]
    selected_dates = st.multiselect("Dates to show", options=date_cols, default=date_cols[:3])

    # Filtrage selon les métadonnées
    st.markdown("#### 2 – Results")
    filters = {
        "Reference area": [ref],
        "Frequency": [freq],
        "Type": [type_],
        "Basket": [basket],
        "Unit": [unit]
    }

    filtered = filter_bis_data(df_bis, filters)

    # Affichage avec colonnes sélectionnées
    meta_cols = ["Reference area", "Frequency", "Type", "Basket", "Unit"]
    to_show = filtered[meta_cols + selected_dates].copy()

    st.success(f"{len(to_show)} rows selected.")
    show_all = st.checkbox("Show all rows", value=False)
    st.dataframe(to_show if show_all else to_show.head(10), use_container_width=True)

    st.download_button(
        "Download CSV",
        to_show.to_csv(index=False).encode(),
        file_name=f"bis_reer_{ref.replace(' ', '_')}.csv",
        mime="text/csv"
    )
