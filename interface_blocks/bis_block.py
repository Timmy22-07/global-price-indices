# interface_blocks/bis_block.py – v2025-07-09 refactor
# ------------------------------------------------------------
# • Sélecteurs multi-valeurs (multiselect) + bouton Select ALL
# • Plus de menus vides (options calculées à la volée)
# • Nom de fichier sécurisé                (« bis_reer_<ref>.csv »)
# ------------------------------------------------------------

from __future__ import annotations
import streamlit as st
from core.bis_loader import load_bis_reer_data, filter_bis_data

@st.cache_data(show_spinner=False)
def _load_bis_reer():
    return load_bis_reer_data()

def _unique(df, col):
    return sorted(df[col].dropna().unique().tolist())

def display_bis_block() -> None:
    st.markdown("#### 1 – Select filters")

    # ── Chargement des données BIS REER ──────────────────────
    df = _load_bis_reer()

    # ── Préparation des listes d’options ─────────────────────
    ref_options    = _unique(df, "Reference area")
    freq_options   = _unique(df, "Frequency")
    type_options   = _unique(df, "Type")
    basket_options = _unique(df, "Basket")
    unit_options   = _unique(df, "Unit")

    # ── Sélecteurs avec bouton Select ALL ────────────────────
    col_ref, col_ref_btn = st.columns([5, 1])
    with col_ref:
        ref_sel = st.multiselect("Reference Area", ref_options)
    with col_ref_btn:
        if st.button("✓ All", key="ref_all"):
            ref_sel = ref_options.copy()

    col_freq, col_freq_btn = st.columns([5, 1])
    with col_freq:
        freq_sel = st.multiselect("Frequency", freq_options)
    with col_freq_btn:
        if st.button("✓ All", key="freq_all"):
            freq_sel = freq_options.copy()

    col_type, col_type_btn = st.columns([5, 1])
    with col_type:
        type_sel = st.multiselect("Type", type_options)
    with col_type_btn:
        if st.button("✓ All", key="type_all"):
            type_sel = type_options.copy()

    col_basket, col_unit = st.columns(2)
    with col_basket:
        basket_sel = st.multiselect("Basket", basket_options)
    with col_unit:
        unit_sel = st.multiselect("Unit", unit_options)

    # ── Sélecteur des dates (colonnes de valeurs) ────────────
    meta_cols = [
        "Dataflow ID", "Timeseries Key", "Frequency", "Type",
        "Basket", "Reference area", "Unit"
    ]
    date_cols = [c for c in df.columns if c not in meta_cols]
    date_sel = st.multiselect("Dates to show", date_cols,
                              default=date_cols[:3])

    # ── Application des filtres ──────────────────────────────
    filters = {
        "Reference area": ref_sel or ref_options,
        "Frequency": freq_sel or freq_options,
        "Type": type_sel or type_options,
        "Basket": basket_sel or basket_options,
        "Unit": unit_sel or unit_options,
    }
    filtered = filter_bis_data(df, filters)

    # ── Affichage des résultats ──────────────────────────────
    st.markdown("#### 2 – Results")
    show_cols = ["Reference area", "Frequency", "Type", "Basket", "Unit"] + date_sel
    to_show = filtered[show_cols]

    st.success(f"{len(to_show)} rows selected.")
    st.dataframe(
        to_show if st.checkbox("Show all rows", value=False) else to_show.head(10),
        use_container_width=True,
    )

    # ── Téléchargement CSV ───────────────────────────────────
    safe_ref = (
        ref_sel[0].replace(" ", "_")
        if ref_sel else "bis_reer_filtered"
    )
    st.download_button(
        "📥 Download CSV",
        data=to_show.to_csv(index=False).encode("utf-8"),
        file_name=f"{safe_ref}.csv",
        mime="text/csv",
    )
