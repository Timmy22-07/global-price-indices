# interface_blocks/numbeo_block.py – v2025-07-07 updated
# ------------------------------------------------------------
# • Sélection dynamique régions + variables
# • Aperçu limité à 10 colonnes (+ Show all)
# • Bouton de téléchargement CSV
# ------------------------------------------------------------
from __future__ import annotations
import streamlit as st

from core.numbeo_loader import (
    load_numbeo_data,
    get_city_options,
    get_variable_options,
    filter_numbeo_data,
)

# -------- Cache ------------------------------------------------------
@st.cache_data(show_spinner=False)
def _load_cached():
    return load_numbeo_data()


# -------- Bloc principal --------------------------------------------
def display_numbeo_block() -> None:
    st.markdown("#### 1 – Sélection des filtres")

    # ---- Chargement unique (cache) ----
    with st.spinner("🏙️ Chargement des données Numbeo…"):
        df_full = _load_cached()

    regions_all = get_city_options(df_full)
    vars_all = get_variable_options(df_full)

    # ---- Sélecteur de régions --------------------------------------
    col_reg, col_reg_all = st.columns([5, 1])
    with col_reg:
        regions_sel = st.multiselect("Régions (ville, pays)", regions_all)
    with col_reg_all:
        if st.checkbox("Tout sélectionner", key="numbeo_sel_all_regions"):
            regions_sel = regions_all.copy()

    # ---- Sélecteur de variables ------------------------------------
    col_var, col_var_all = st.columns([5, 1])
    with col_var:
        vars_sel = st.multiselect("Variables", vars_all, default=vars_all[:5])
    with col_var_all:
        if st.checkbox("Tout sélectionner", key="numbeo_sel_all_vars"):
            vars_sel = vars_all.copy()

    # ---- Filtrage ---------------------------------------------------
    if not vars_sel:
        st.warning("Veuillez sélectionner au moins une variable.")
        return

    filtered = filter_numbeo_data(df_full, regions_sel or None, vars_sel)
    st.success(f"{len(filtered)} lignes sélectionnées.")

    # ---- Affichage (10 colonnes par défaut) ------------------------
    show_all_cols = st.checkbox("Afficher toutes les colonnes", value=False, key="numbeo_show_cols")
    if not show_all_cols and len(filtered.columns) > 10:
        st.dataframe(filtered.iloc[:, :10], use_container_width=True)
        st.caption("Affichage limité aux 10 premières colonnes. Cochez la case pour tout afficher.")
    else:
        st.dataframe(filtered, use_container_width=True)

    # ---- Téléchargement --------------------------------------------
    csv_data = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "📥 Télécharger le CSV",
        csv_data,
        file_name="numbeo_filtré.csv",
        mime="text/csv",
    )
