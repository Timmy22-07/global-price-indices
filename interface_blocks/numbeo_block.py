# interface_blocks/numbeo_block.py – v3
# ---------------------------------------------------------------------
# • Bloc d’interface pour Numbeo – Cost of Living + PPP
# • Ajout : « Select all » pour la région ET les variables
# • Ajout : bouton « Show all columns » (sinon aperçu limité à 10)
# • Libellé du bouton de téléchargement changé → « Download CSV »
# ---------------------------------------------------------------------

from __future__ import annotations
import streamlit as st
from core.numbeo_loader import (
    load_numbeo_data,
    get_city_options,
    get_variable_options,
    filter_numbeo_data,
)

# ------------------------------------------------------------------ #
# Chargement en cache                                                #
# ------------------------------------------------------------------ #
@st.cache_data(show_spinner=False)
def _load_cached():
    return load_numbeo_data()

# ------------------------------------------------------------------ #
# Bloc principal                                                     #
# ------------------------------------------------------------------ #

def display_numbeo_block() -> None:
    """Interface complète Numbeo (région + variables + téléchargements)."""

    st.markdown("#### 1 – Select filters")

    with st.spinner("🏙️ Loading Numbeo data…"):
        df_all = _load_cached()

    # ---------------- Region selector -----------------
    city_options = get_city_options(df_all)

    col_r, col_sa = st.columns([4, 1])
    with col_r:
        city_selected = st.selectbox("Region (city, country)", city_options)
    with col_sa:
        select_all_city = st.checkbox("Select all", key="numbeo_select_all_city")
        if select_all_city:
            city_selected = None  # signal "all"

    # --------------- Variable selector ----------------
    variables_all = get_variable_options(df_all)

    col_v, col_vs = st.columns([4, 1])
    with col_v:
        vars_selected = st.multiselect("Variables", variables_all, default=variables_all[:5])
    with col_vs:
        if st.checkbox("Select all", key="numbeo_select_all_vars"):
            vars_selected = variables_all.copy()

    # --------------- Filtrage -------------------------
    filtered = filter_numbeo_data(df_all, city_selected, vars_selected)

    # --------------- Affichage tableau ----------------
    st.success(f"{len(filtered)} rows selected.")

    show_all_cols = st.checkbox("Show all columns", value=False, key="numbeo_show_all_cols")
    if not show_all_cols and len(filtered.columns) > 10:
        cols_to_display = filtered.columns[:10]
        st.dataframe(filtered[cols_to_display], use_container_width=True)
        st.caption("Showing first 10 columns – tick ‘Show all columns’ to view the full table.")
    else:
        st.dataframe(filtered, use_container_width=True)

    # --------------- Téléchargement -------------------
    st.download_button(
        label="Download CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="numbeo_filtered.csv",
        mime="text/csv",
    )

# ------------------------------------------------------------------ #
# Fin                                                                #
# ------------------------------------------------------------------ #
