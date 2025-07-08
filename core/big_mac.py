import streamlit as st
from core.big_mac import load_data as load_big_mac, get_lookup_table, filter_data as filter_big_mac

# ---------------------------------------------------------------------
# Big‑Mac Index interface block — v3
# • Ajout de boutons « ✓ All » pour ISO / Currency / Country
# • Titre simplifié (« Pick one identifier »)
# • Checkbox « All » (au lieu de « Select ALL parameters »)
# ---------------------------------------------------------------------

@st.cache_data(show_spinner=False)
def load_big_mac_cached():
    return load_big_mac()

def _button_all(label: str, key: str):
    """Affiche un petit bouton "✓ All" dans la colonne de droite."""
    if st.button(label, key=key):
        st.session_state[key.replace("_btn", "")] = "All"
        st.rerun()

def display_big_mac_block():
    st.markdown("#### 1 – Pick one identifier")

    lookup = get_lookup_table()

    # Initialise les states ("All" = aucune restriction)
    for k in ("iso_sel", "cur_sel", "name_sel"):
        st.session_state.setdefault(k, "All")

    df_filt = lookup.copy()
    if st.session_state.iso_sel != "All":
        df_filt = df_filt[df_filt["iso_a3"] == st.session_state.iso_sel]
    if st.session_state.cur_sel != "All":
        df_filt = df_filt[df_filt["currency_code"] == st.session_state.cur_sel]
    if st.session_state.name_sel != "All":
        df_filt = df_filt[df_filt["name"] == st.session_state.name_sel]

    iso_opts = ["All"] + sorted(df_filt["iso_a3"].unique())
    cur_opts = ["All"] + sorted(df_filt["currency_code"].unique())
    name_opts = ["All"] + sorted(df_filt["name"].unique())

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        iso_sel = st.selectbox("ISO Code", iso_opts, index=iso_opts.index(st.session_state.iso_sel))
        if iso_sel != st.session_state.iso_sel:
            st.session_state.iso_sel = iso_sel
            st.rerun()
    with c2:
        cur_sel = st.selectbox("Currency Code", cur_opts, index=cur_opts.index(st.session_state.cur_sel))
        if cur_sel != st.session_state.cur_sel:
            st.session_state.cur_sel = cur_sel
            st.rerun()
    with c3:
        name_sel = st.selectbox("Country", name_opts, index=name_opts.index(st.session_state.name_sel))
        if name_sel != st.session_state.name_sel:
            st.session_state.name_sel = name_sel
            st.rerun()

    # Boutons "All" (réinitialise à "All")
    b1, b2, b3 = st.columns([1, 1, 1])
    with b1: _button_all("✓ All", "iso_sel_btn")
    with b2: _button_all("✓ All", "cur_sel_btn")
    with b3: _button_all("✓ All", "name_sel_btn")

    if st.button("🔁 Reset identifiers"):
        st.session_state.iso_sel = "All"
        st.session_state.cur_sel = "All"
        st.session_state.name_sel = "All"
        st.rerun()

    iso, currency, country = (
        None if st.session_state.iso_sel == "All" else st.session_state.iso_sel,
        None if st.session_state.cur_sel == "All" else st.session_state.cur_sel,
        None if st.session_state.name_sel == "All" else st.session_state.name_sel,
    )

    # ------------------------------------------------------------------
    # Paramètres numériques
    # ------------------------------------------------------------------
    st.markdown("#### 2 – Select parameters ↪")
    big_mac_df = load_big_mac_cached()
    big_mac_df.columns = [c if c else "empty_column" for c in big_mac_df.columns]
    numeric_cols = [c for c in big_mac_df.columns if c not in ["date", "iso_a3", "currency_code", "name", "empty_column"] and big_mac_df[c].dtype != object]
    select_all = st.checkbox("All", value=False)
    vars_sel = st.multiselect("Parameters", numeric_cols, default=(numeric_cols if select_all else numeric_cols[:2]))

    # ------------------------------------------------------------------
    # Sélecteur de date : année / mois / jour
    # ------------------------------------------------------------------
    st.markdown("#### 3 – Select date")
    data_filtered = big_mac_df.copy()
    if iso:       data_filtered = data_filtered[data_filtered["iso_a3"] == iso]
    if currency:  data_filtered = data_filtered[data_filtered["currency_code"] == currency]
    if country:   data_filtered = data_filtered[data_filtered["name"] == country]

    years = sorted(data_filtered["date"].dt.year.unique())
    year = st.selectbox("Year", ["All"] + [str(y) for y in years])

    month_data = data_filtered if year == "All" else data_filtered[data_filtered["date"].dt.year == int(year)]
    months = sorted(month_data["date"].dt.month.unique())
    month = st.selectbox("Month", ["All"] + [str(m) for m in months])

    day_data = month_data if month == "All" else month_data[month_data["date"].dt.month == int(month)]
    days = sorted(day_data["date"].dt.day.unique())
    day = st.selectbox("Day", ["All"] + [str(d) for d in days])

    # ------------------------------------------------------------------
    # Résultats
    # ------------------------------------------------------------------
    st.markdown("#### 4 – Results")
    res = filter_big_mac(
        iso=iso,
        currency=currency,
        name=country,
        year=None if year == "All" else int(year),
        month=None if month == "All" else int(month),
        day=None if day == "All" else int(day),
        variables=vars_sel or None,
    )
    res = res.loc[:, res.columns != "empty_column"].copy()
    res["date"] = res["date"].dt.date

    res.index += 1
    res.index.name = "#"

    st.success(f"{len(res)} rows selected.")
    st.dataframe(
        res if st.checkbox("Show all rows", value=False) else res.head(10),
        use_container_width=True,
    )

    st.download_button(
        "Download CSV",
        res.to_csv(index=False).encode(),
        file_name=f"big_mac_{iso or currency or country or 'all'}.csv",
        mime="text/csv",
    )
