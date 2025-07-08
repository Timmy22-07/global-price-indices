from __future__ import annotations
import streamlit as st
from core.bis_loader import load_bis_reer_data, filter_bis_data
import pandas as pd

@st.cache_data(show_spinner=False)
def _load_bis_reer():
    return load_bis_reer_data()

def _unique(df, col):
    return sorted(df[col].dropna().unique().tolist())

def _filter_block(label: str, options: list[str], key: str):
    if key not in st.session_state:
        st.session_state[key] = []

    col_sel, col_btn = st.columns([5, 1])
    with col_sel:
        selection = st.multiselect(label, options, default=st.session_state[key], key=key)
    with col_btn:
        if st.button("✓ All", key=f"{key}_all"):
            st.session_state[key] = options.copy()
            selection = options.copy()
            st.rerun()
    return selection

def display_bis_block() -> None:
    st.markdown("#### 1 – Select filters")

    df = _load_bis_reer()

    if df.empty:
        st.error("❌ Aucune donnée BIS-REER trouvée.\n\n➡ Vérifie le dossier `data/raw/bis/` et les formats `.csv` ou `.xlsx`.")
        return

    # ── Filtres BIS ────────────────────────────────────────
    ref_sel    = _filter_block("Reference Area", _unique(df, "Reference area"), "ref")
    freq_sel   = _filter_block("Frequency", _unique(df, "Frequency"), "freq")
    type_sel   = _filter_block("Type", _unique(df, "Type"), "type")
    basket_sel = _filter_block("Basket", _unique(df, "Basket"), "basket")
    unit_sel   = _filter_block("Unit", _unique(df, "Unit"), "unit")

    # ── Dates dynamiques (année → mois → jour) ─────────────
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
        day_options = sorted(df_dates[(df_dates["year"] == year_sel) if year_sel != "All" else slice(None)]["day"].unique())
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
        "Reference area": ref_sel or _unique(df, "Reference area"),
        "Frequency": freq_sel or _unique(df, "Frequency"),
        "Type": type_sel or _unique(df, "Type"),
        "Basket": basket_sel or _unique(df, "Basket"),
        "Unit": unit_sel or _unique(df, "Unit"),
    }

    filtered = filter_bis_data(df, filters)

    st.markdown("#### 3 – Results")
    show_cols = ["Reference area", "Frequency", "Type", "Basket", "Unit"] + final_dates
    to_show = filtered[show_cols] if final_dates else filtered[show_cols[:5]]

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
