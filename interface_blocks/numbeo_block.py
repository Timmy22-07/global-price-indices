# interface_blocks/numbeo_block.py – v2025-07-08
# ------------------------------------------------------------
# • Persist. sélections via st.session_state                  |
# • Boutons “Tout sélectionner” pour régions & variables      |
# • Aperçu 10 colonnes (toggle) + téléchargement CSV          |
# ------------------------------------------------------------
from __future__ import annotations
import streamlit as st
from core.numbeo_loader import (
    load_numbeo_data,
    get_city_options,
    get_variable_options,
    filter_numbeo_data,
)

@st.cache_data(show_spinner=False)
def _load_cached():
    return load_numbeo_data()

def display_numbeo_block() -> None:
    st.markdown("#### 1 – Select filters")

    # ── Chargement (une seule fois) ───────────────────────────
    df_full = _load_cached()
    all_regions = get_city_options(df_full)
    all_vars    = get_variable_options(df_full)

    # ── Init session_state ───────────────────────────────────
    st.session_state.setdefault("num_reg_sel", [])
    st.session_state.setdefault("num_var_sel", all_vars[:5])

    # ── Sélection régions ────────────────────────────────────
    col_r1, col_r2 = st.columns([5, 1])
    with col_r1:
        reg_sel = st.multiselect(
            "Region (city, country)",
            options=all_regions,
            default=st.session_state.num_reg_sel,
        )
    with col_r2:
        if st.button("✓ All", key="numbeo_all_regions"):
            reg_sel = all_regions.copy()

    # ── Sélection variables ──────────────────────────────────
    col_v1, col_v2 = st.columns([5, 1])
    with col_v1:
        var_sel = st.multiselect(
            "Variables",
            options=all_vars,
            default=st.session_state.num_var_sel,
        )
    with col_v2:
        if st.button("✓ All", key="numbeo_all_vars"):
            var_sel = all_vars.copy()

    # ── Mémorise les choix ───────────────────────────────────
    st.session_state.num_reg_sel = reg_sel
    st.session_state.num_var_sel = var_sel

    if not var_sel:
        st.warning("Sélectionnez au moins une variable.")
        return

    # ── Filtrage + affichage ─────────────────────────────────
    filtered = filter_numbeo_data(df_full, reg_sel or None, var_sel)
    st.success(f"{len(filtered)} lignes sélectionnées.")

    show_all_cols = st.checkbox("Afficher toutes les colonnes", value=False)
    if not show_all_cols and len(filtered.columns) > 10:
        st.dataframe(filtered.iloc[:, :10], use_container_width=True)
        st.caption("Affichage limité aux 10 premières colonnes.")
    else:
        st.dataframe(filtered, use_container_width=True)

    # ── Téléchargement CSV ───────────────────────────────────
    st.download_button(
        "📥 Download CSV",
        filtered.to_csv(index=False).encode(),
        file_name="numbeo_filtered.csv",
        mime="text/csv",
    )
