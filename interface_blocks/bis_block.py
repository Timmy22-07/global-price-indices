from __future__ import annotations
import streamlit as st
from core.bis_loader import load_bis_reer_data, filter_bis_data
import pandas as pd

@st.cache_data(show_spinner=False)
def _load_bis_reer():
    return load_bis_reer_data()

def _unique(df, col):
    return sorted(df[col].dropna().unique().tolist())

def display_bis_block() -> None:
    st.markdown("#### 1 – Select filters")

    df = _load_bis_reer()

    if df.empty:
        st.error("❌ Aucune donnée BIS-REER trouvée.\n\n➡ Vérifie le dossier `data/raw/bis/` et les formats `.csv` ou `.xlsx`.")
        return

    # ── Filtres BIS : init des états si nécessaires ──────────
    ref_options    = _unique(df, "Reference area")
    freq_options   = _unique(df, "Frequency")
    type_options   = _unique(df, "Type")
    basket_options = _unique(df, "Basket")
    unit_options   = _unique(df, "Unit")

    for key, opts in {
        "ref_sel": ref_options,
        "freq_sel": freq_options,
        "type_sel": type_options,
        "basket_sel": basket_options,
        "unit_sel": unit_options
    }.items():
        if key not in st.session_state:
            st.session_state[key] = []

    # ── Filtres avec boutons ✓ All visibles ─────────────────
    col_ref, col_ref_btn = st.columns([5, 1])
    with col_ref:
        ref_sel = st.multiselect("Reference Area", ref_options, default=st.session_state.ref_sel, key="ref")
    with col_ref_btn:
        if st.button("✓ All", key="ref_all_btn"):
            st.session_state.ref_sel = ref_options.copy()
            st.experimental_rerun()

    col_freq, col_freq_btn = st.columns([5, 1])
    with col_freq:
        freq_sel = st.multiselect("Frequency", freq_options, default=st.session_state.freq_sel, key="freq")
    with col_freq_btn:
        if st.button("✓ All", key="freq_all_btn"):
            st.session_state.freq_sel = freq_options.copy()
            st.experimental_rerun()

    col_type, col_type_btn = st.columns([5, 1])
    with col_type:
        type_sel = st.multiselect("Type", type_options, default=st.session_state.type_sel, key="type")
    with col_type_btn:
        if st.button("✓ All", key="type_all_btn"):
            st.session_state.type_sel = type_options.copy()
            st.experimental_rerun()

    col_basket, col_unit = st.columns(2)
    with col_basket:
        basket_sel = st.multiselect("Basket", basket_options, default=st.session_state.basket_sel, key="basket")
    with col_unit:
        unit_sel = st.multiselect("Unit", unit_options, default=st.session_state.unit_sel, key="unit")
    if st.button("✓ All", key="unit_all_btn"):
        st.session_state.unit_sel = unit_options.copy()
        st.experimental_rerun()

    # ── Dates dynamiques (année → mois → jour) ───────────────
    meta_cols = ["Dataflow ID", "Timeseries Key", "Frequency", "Type", "Basket", "Reference area", "Unit"]
    raw_date_cols = [c for c in df.columns if c not in meta_cols]

    try:
        parsed_dates = pd.to_datetime(raw_date_cols, format="%Y-%m-%d", errors="coerce")
        date_map = {d.strftime("%Y-%m-%d"): d for d in parsed_dates if not pd.isna(d)}
    except Exception:
        st.warning("⚠ Impossible d'interpréter les colonnes de dates.")
        return

    df_dates = pd.DataFrame({"col": list(date_map.keys()), "dt": list(date_map.values())})
    df_dates["year"] = df_dates["dt"].dt.year.astype(str)
    df_dates["month"] = df_dates["dt"].dt.month.astype(str).str.zfill(2)
    df_dates["day"] = df_dates["dt"].dt.day.astype(str).str.zfill(2)

    st.markdown("#### 2 – Select date")
    year_sel = st.selectbox("Year", options=["All"] + sorted(df_dates["year"].unique()), index=0)

    if year_sel == "All":
        month_options = sorted(df_dates["month"].unique())
    else:
        month_options = sorted(df_dates[df_dates["year"] == year_sel]["month"].unique())

    month_sel = st.selectbox("Month", options=["All"] + month_options, index=0)

    if month_sel == "All":
        day_options = sorted(df_dates[
            (df_dates["year"] == year_sel) if year_sel != "All" else slice(None)
        ]["day"].unique())
    else:
        day_options = sorted(df_dates[
            (df_dates["year"] == year_sel if year_sel != "All" else True) &
            (df_dates["month"] == month_sel)
        ]["day"].unique())

    day_sel = st.selectbox("Day", options=["All"] + day_options, index=0)

    mask = pd.Series(True, index=df_dates.index)
    if year_sel != "All":
        mask &= df_dates["year"] == year_sel
    if month_sel != "All":
        mask &= df_dates["month"] == month_sel
    if day_sel != "All":
        mask &= df_dates["day"] == day_sel

    final_dates = df_dates[mask]["col"].tolist()

    # ── Application du filtre global ─────────────────────────
    filters = {
        "Reference area": ref_sel or ref_options,
        "Frequency": freq_sel or freq_options,
        "Type": type_sel or type_options,
        "Basket": basket_sel or basket_options,
        "Unit": unit_sel or unit_options,
    }

    filtered = filter_bis_data(df, filters)

    st.markdown("#### 3 – Results")
    show_cols = ["Reference area", "Frequency", "Type", "Basket", "Unit"] + final_dates
    to_show = filtered[show_cols] if final_dates else filtered[["Reference area", "Frequency", "Type", "Basket", "Unit"]]

    st.success(f"{len(to_show)} rows selected.")
    st.dataframe(
        to_show if st.checkbox("Show all rows", value=False) else to_show.head(10),
        use_container_width=True,
    )

    # ── Export CSV ───────────────────────────────────────────
    safe_ref = ref_sel[0].replace(" ", "_") if ref_sel else "bis_reer_filtered"
    st.download_button(
        "📥 Download CSV",
        data=to_show.to_csv(index=False).encode("utf-8"),
        file_name=f"{safe_ref}.csv",
        mime="text/csv",
    )
