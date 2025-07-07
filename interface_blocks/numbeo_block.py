# interface_blocks/numbeo_block.py – v2025-07-07 c
# ------------------------------------------------------------
# • « Select all » pour régions ET variables
# • Aperçu limité à 10 colonnes  (+ Show all)
# • Bouton de DL   →  « Download CSV »
# ------------------------------------------------------------
from __future__ import annotations
import streamlit as st

from core.numbeo_loader import (
    load_numbeo_data,
    get_region_options,
    get_variable_options,
    filter_numbeo_data,
)

# -------- Cache ------------------------------------------------------
@st.cache_data(show_spinner=False)
def _load_cached():
    return load_numbeo_data()


# -------- Bloc principal --------------------------------------------
def display_numbeo_block() -> None:
    st.markdown("#### 1 – Select filters")

    # ---- Chargement unique (cache) ----
    with st.spinner("🏙️ Loading Numbeo…"):
        df_full = _load_cached()

    regions_all = get_region_options(df_full)
    vars_all = get_variable_options(df_full)

    # ---- Sélecteur de régions --------------------------------------
    col_reg, col_reg_all = st.columns([5, 1])
    with col_reg:
        regions_sel = st.multiselect("Region (city, country)", regions_all)
    with col_reg_all:
        if st.checkbox("Select all", key="numbeo_sel_all_regions"):
            regions_sel = regions_all.copy()

    # ---- Sélecteur de variables ------------------------------------
    col_var, col_var_all = st.columns([5, 1])
    with col_var:
        vars_sel = st.multiselect("Variables", vars_all, default=vars_all[:5])
    with col_var_all:
        if st.checkbox("Select all", key="numbeo_sel_all_vars"):
            vars_sel = vars_all.copy()

    # ---- Filtrage ---------------------------------------------------
    if not vars_sel:  # au moins une variable
        st.warning("Choose at least one variable.")
        return

    filtered = filter_numbeo_data(df_full, regions_sel or None, vars_sel)
    st.success(f"{len(filtered)} rows selected.")

    # ---- Affichage (10 colonnes par défaut) ------------------------
    show_all_cols = st.checkbox("Show all columns", value=False, key="numbeo_show_cols")
    if not show_all_cols and len(filtered.columns) > 10:
        st.dataframe(filtered.iloc[:, :10], use_container_width=True)
        st.caption("Showing first 10 columns. Tick the box above to view all.")
    else:
        st.dataframe(filtered, use_container_width=True)

    # ---- Téléchargement --------------------------------------------
    csv_data = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Download CSV",
        csv_data,
        file_name="numbeo_filtered.csv",
        mime="text/csv",
    )
