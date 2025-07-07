# interface_blocks/numbeo_block.py – v2025-07-08 final
# ------------------------------------------------------------
# • Sélection dynamique des régions (ville/pays)              |
# • Sélection multi-variables (avec bouton Tout sélectionner) |
# • Affichage intelligent limité à 10 colonnes                |
# • Téléchargement CSV                                        |
# ------------------------------------------------------------

from __future__ import annotations
import streamlit as st

from core.numbeo_loader import (
    load_numbeo_data,
    get_city_options,
    get_variable_options,
    filter_numbeo_data,
)

# ─────────────────────────────────────────────────────────────
# Chargement des données (cache mémoire)
@st.cache_data(show_spinner=False)
def _load_cached_data():
    return load_numbeo_data()

# ─────────────────────────────────────────────────────────────
# Bloc principal d’interface
def display_numbeo_block() -> None:
    st.markdown("#### 1 – Select filters")

    # Chargement initial des données
    df_full = _load_cached_data()
    region_list = get_city_options(df_full)
    variable_list = get_variable_options(df_full)

    # Initialisation état local
    st.session_state.setdefault("numbeo_regions", [])
    st.session_state.setdefault("numbeo_variables", variable_list[:5])

    # Sélecteurs de régions
    col1, col2 = st.columns([5, 1])
    with col1:
        selected_regions = st.multiselect(
            "Region (city, country)",
            options=region_list,
            default=st.session_state.numbeo_regions,
        )
    with col2:
        if st.button("✓ Select All", key="select_all_regions"):
            selected_regions = region_list.copy()

    # Sélecteurs de variables
    col3, col4 = st.columns([5, 1])
    with col3:
        selected_vars = st.multiselect(
            "Variables",
            options=variable_list,
            default=st.session_state.numbeo_variables,
        )
    with col4:
        if st.button("✓ Select All", key="select_all_variables"):
            selected_vars = variable_list.copy()

    # Mise à jour session
    st.session_state.numbeo_regions = selected_regions
    st.session_state.numbeo_variables = selected_vars

    # Alerte si aucune variable sélectionnée
    if not selected_vars:
        st.warning("Please select at least one variable.")
        return

    # Filtrage des données
    filtered_df = filter_numbeo_data(df_full, selected_regions or None, selected_vars)
    st.success(f"{len(filtered_df)} rows selected.")

    # Affichage des résultats (limite à 10 colonnes)
    show_all_cols = st.checkbox("Show all columns", value=False)
    if not show_all_cols and len(filtered_df.columns) > 10:
        st.dataframe(filtered_df.iloc[:, :10], use_container_width=True)
        st.caption("Only first 10 columns shown. Enable the toggle to display all.")
    else:
        st.dataframe(filtered_df, use_container_width=True)

    # Téléchargement du CSV
    st.download_button(
        label="📥 Download CSV",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="numbeo_filtered.csv",
        mime="text/csv",
    )
