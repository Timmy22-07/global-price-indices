# interface_blocks/numbeo_block.py – v2025-07-08 FINAL
# ------------------------------------------------------------
# • Bloc interface pour les données Numbeo (base SQLite/table cities)
# • Sélection de régions et de variables avec persistance
# • Affichage des résultats (max 10 colonnes par défaut)
# • Export des résultats filtrés en CSV
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
@st.cache_data(show_spinner=False)
def _load_cached_data():
    return load_numbeo_data()

# ─────────────────────────────────────────────────────────────
def display_numbeo_block() -> None:
    st.markdown("#### 1 – Select filters")

    # Chargement initial (depuis SQLite ou fallback CSV)
    df_full = _load_cached_data()
    region_list = get_city_options(df_full)
    variable_list = get_variable_options(df_full)

    # Initialisation de l’état local Streamlit
    st.session_state.setdefault("numbeo_regions", [])
    st.session_state.setdefault("numbeo_variables", variable_list[:5])

    # 🏙️ Sélecteur de régions
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

    # 📊 Sélecteur de variables
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

    # 🔄 Mise à jour de l’état local
    st.session_state.numbeo_regions = selected_regions
    st.session_state.numbeo_variables = selected_vars

    # ⚠️ Validation minimale
    if not selected_vars:
        st.warning("Please select at least one variable.")
        return

    # 📥 Filtrage des données
    filtered_df = filter_numbeo_data(df_full, selected_regions or None, selected_vars)
    st.success(f"{len(filtered_df)} rows selected.")

    # 📋 Aperçu interactif (limité à 10 colonnes par défaut)
    show_all_cols = st.checkbox("Show all columns", value=False)
    if not show_all_cols and len(filtered_df.columns) > 10:
        st.dataframe(filtered_df.iloc[:, :10], use_container_width=True)
        st.caption("Only the first 10 columns are shown. Enable toggle to see all.")
    else:
        st.dataframe(filtered_df, use_container_width=True)

    # 💾 Export CSV
    st.download_button(
        label="📥 Download CSV",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="numbeo_filtered.csv",
        mime="text/csv",
    )
