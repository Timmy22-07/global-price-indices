from __future__ import annotations
import streamlit as st
from core.bis_loader import load_bis_reer_data, filter_bis_data
import pandas as pd

@st.cache_data(show_spinner=False)
def _load_bis_reer():
    return load_bis_reer_data()

def _unique(df, col):
    return sorted(df[col].dropna().unique().tolist())

# ─────────────────────────────────────────────────────────────
def _filter_block(label: str, options: list[str], key: str):
    """
    Rend un multiselect + bouton ✓ All qui met à jour
    st.session_state[ key ] sans utiliser experimental_rerun.
    Retourne la sélection courante.
    """
    if key not in st.session_state:
        st.session_state[key] = []

    col_sel, col_btn = st.columns([5, 1])
    with col_sel:
        sel = st.multiselect(label, options, default=st.session_state[key], key=key)
        # synchronise la session à chaque interaction manuelle
        st.session_state[key] = sel
    with col_btn:
        if st.button("✓ All", key=f"{key}_all"):
            st.session_state[key] = options.copy()
            sel = options.copy()
    return sel
# ─────────────────────────────────────────────────────────────

def display_bis_block() -> None:
    st.markdown("#### 1 – Select filters")

    df = _load_bis_reer()
    if df.empty:
        st.error("❌ Aucune donnée BIS REER trouvée.")
        return

    # Options uniques
    ref_opts    = _unique(df, "Reference area")
    freq_opts   = _unique(df, "Frequency")
    type_opts   = _unique(df, "Type")
    basket_opts = _unique(df, "Basket")
    unit_opts   = _unique(df, "Unit")

    # Filtres principaux avec ✓ All
    ref_sel    = _filter_block("Reference Area", ref_opts, "ref_bis")
    freq_sel   = _filter_block("Frequency",      freq_opts, "freq_bis")
    type_sel   = _filter_block("Type",           type_opts, "type_bis")
    basket_sel = _filter_block("Basket",         basket_opts, "basket_bis")
    unit_sel   = _filter_block("Unit",           unit_opts, "unit_bis")

    # ───── Sélecteur Année → Mois → Jour ─────
    meta_cols = ["Dataflow ID","Timeseries Key","Frequency","Type",
                 "Basket","Reference area","Unit"]
    date_cols = [c for c in df.columns if c not in meta_cols]

    parsed = pd.to_datetime(date_cols, format="%Y-%m-%d", errors="coerce")
    valid_dates = {c: d for c, d in zip(date_cols, parsed) if pd.notna(d)}
    df_dates = (pd.DataFrame({"col": list(valid_dates.keys()),
                              "dt":  list(valid_dates.values())})
                  .assign(year=lambda d: d.dt.dt.year.astype(str),
                          month=lambda d: d.dt.dt.month.astype(str).str.zfill(2),
                          day=lambda d: d.dt.dt.day.astype(str).str.zfill(2)))

    st.markdown("#### 2 – Select date")
    year = st.selectbox("Year", ["All"]+sorted(df_dates.year.unique()))
    month_opts = (df_dates[df_dates.year==year] if year!="All" else df_dates).month.unique()
    month = st.selectbox("Month", ["All"]+sorted(month_opts))
    day_opts = (df_dates[(df_dates.year==year) if year!="All" else slice(None)]
                       [(df_dates.month==month) if month!="All" else slice(None)]
                ).day.unique()
    day = st.selectbox("Day", ["All"]+sorted(day_opts))

    mask = pd.Series(True, index=df_dates.index)
    if year  != "All": mask &= df_dates.year  == year
    if month != "All": mask &= df_dates.month == month
    if day   != "All": mask &= df_dates.day   == day
    final_dates = df_dates[mask].col.tolist()

    # ───── Filtrage de données ─────
    filters = {
        "Reference area": ref_sel or ref_opts,
        "Frequency":      freq_sel or freq_opts,
        "Type":           type_sel or type_opts,
        "Basket":         basket_sel or basket_opts,
        "Unit":           unit_sel or unit_opts,
    }
    filtered = filter_bis_data(df, filters)

    # ───── Résultats ─────
    st.markdown("#### 3 – Results")
    cols_to_show = ["Reference area","Frequency","Type","Basket","Unit"] + final_dates
    to_show = (filtered[cols_to_show] if final_dates
               else filtered[["Reference area","Frequency","Type","Basket","Unit"]])

    st.success(f"{len(to_show)} rows selected.")
    st.dataframe(to_show if st.checkbox("Show all rows", False) else to_show.head(10),
                 use_container_width=True)

    # ───── Export CSV ─────
    safe_ref = (ref_sel[0].replace(" ","_") if ref_sel else "bis_reer_filtered")
    st.download_button("📥 Download CSV",
                       data=to_show.to_csv(index=False).encode("utf-8"),
                       file_name=f"{safe_ref}.csv",
                       mime="text/csv")
