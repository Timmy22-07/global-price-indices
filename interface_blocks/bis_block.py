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

    if df.empty:
        st.error(
            "❌ Aucune donnée BIS-REER trouvée.\n\n"
            "➡ Vérifie que les fichiers sont bien placés dans le dossier `data/raw/bis_reer/` "
            "et qu’ils sont au format `.csv` ou `.xlsx`."
        )
        return

    # ── Préparation des options uniques ──────────────────────
    ref_options    = _unique(df, "Reference area")
    freq_options   = _unique(df, "Frequency")
    type_options   = _unique(df, "Type")
    basket_options = _unique(df, "Basket")
    unit_options   = _unique(df, "Unit")

    # ── Filtres avec bouton "✓ All" (sans crash) ─────────────
    def filter_block(label, options, key, btn_key):
        col, col_btn = st.columns([5, 1])
        with col:
            selection = st.multiselect(label, options, default=st.session_state.get(key, []), key=key)
        with col_btn:
            if st.button("✓ All", key=btn_key):
                st.session_state[key] = options.copy()
                selection = options.copy()
        return selection

    ref_sel    = filter_block("Reference Area", ref_options, "ref_bis", "ref_all_bis")
    freq_sel   = filter_block("Frequency", freq_options, "freq_bis", "freq_all_bis")
    type_sel   = filter_block("Type", type_options, "type_bis", "type_all_bis")
    basket_sel = filter_block("Basket", basket_options, "basket_bis", "basket_all_bis")
    unit_sel   = filter_block("Unit", unit_options, "unit_bis", "unit_all_bis")

    # ── Sélecteur des dates ──────────────────────────────────
    meta_cols = [
        "Dataflow ID", "Timeseries Key", "Frequency", "Type",
        "Basket", "Reference area", "Unit"
    ]
    date_cols = [c for c in df.columns if c not in meta_cols]
    date_sel = st.multiselect("Dates to show", date_cols, default=date_cols[:3] if date_cols else [])

    # ── Application des filtres ──────────────────────────────
    filters = {
        "Reference area": ref_sel or ref_options,
        "Frequency": freq_sel or freq_options,
        "Type": type_sel or type_options,
        "Basket": basket_sel or basket_options,
        "Unit": unit_sel or unit_options,
    }
    filtered = filter_bis_data(df, filters)

    # ── Résultats ────────────────────────────────────────────
    st.markdown("#### 2 – Results")
    show_cols = ["Reference area", "Frequency", "Type", "Basket", "Unit"] + date_sel
    to_show = filtered[show_cols] if date_sel else filtered[["Reference area", "Frequency", "Type", "Basket", "Unit"]]

    st.success(f"{len(to_show)} rows selected.")
    st.dataframe(
        to_show if st.checkbox("Show all rows", value=False) else to_show.head(10),
        use_container_width=True,
    )

    # ── Téléchargement ───────────────────────────────────────
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
