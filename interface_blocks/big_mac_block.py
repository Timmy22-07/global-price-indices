# interface_blocks/big_mac_block.py – v2 (externalized)
# ---------------------------------------------------------------------
# • Interface block for Big Mac Index, optimized with caching and spinner.
# ---------------------------------------------------------------------

import streamlit as st
from core.big_mac import load_data as load_big_mac, get_lookup_table, filter_data as filter_big_mac

@st.cache_data(show_spinner=False)
def load_big_mac_cached():
    return load_big_mac()

def display_big_mac_block():
    st.markdown("#### 1 – Pick one identifier")
    lookup = get_lookup_table()

    for k in ("iso_sel", "cur_sel", "name_sel"):
        st.session_state.setdefault(k, "")

    df_filter = lookup.copy()
    if st.session_state.iso_sel:
        df_filter = df_filter[df_filter["iso_a3"] == st.session_state.iso_sel]
    if st.session_state.cur_sel:
        df_filter = df_filter[df_filter["currency_code"] == st.session_state.cur_sel]
    if st.session_state.name_sel:
        df_filter = df_filter[df_filter["name"] == st.session_state.name_sel]

    iso_options = [""] + sorted(df_filter["iso_a3"].unique())
    cur_options = [""] + sorted(df_filter["currency_code"].unique())
    name_options = [""] + sorted(df_filter["name"].unique())

    c1, c2, c3 = st.columns([1, 1, 2])
    with c1:
        iso_sel = st.selectbox("ISO Code", iso_options, index=iso_options.index(st.session_state.iso_sel) if st.session_state.iso_sel in iso_options else 0)
        if iso_sel != st.session_state.iso_sel:
            st.session_state.iso_sel = iso_sel
            st.rerun()
    with c2:
        cur_sel = st.selectbox("Currency Code", cur_options, index=cur_options.index(st.session_state.cur_sel) if st.session_state.cur_sel in cur_options else 0)
        if cur_sel != st.session_state.cur_sel:
            st.session_state.cur_sel = cur_sel
            st.rerun()
    with c3:
        name_sel = st.selectbox("Country", name_options, index=name_options.index(st.session_state.name_sel) if st.session_state.name_sel in name_options else 0)
        if name_sel != st.session_state.name_sel:
            st.session_state.name_sel = name_sel
            st.rerun()

    if st.button("🔁 Reset identifiers"):
        st.session_state.iso_sel = ""
        st.session_state.cur_sel = ""
        st.session_state.name_sel = ""
        st.rerun()

    iso, currency, country = st.session_state.iso_sel, st.session_state.cur_sel, st.session_state.name_sel

    with st.spinner("📊 Loading Big Mac data..."):
        st.markdown("#### 2 – Select parameters")
        big_mac_df = load_big_mac_cached()
        big_mac_df.columns = [col if col else "empty_column" for col in big_mac_df.columns]
        numeric_cols = [c for c in big_mac_df.columns if c not in ["date", "iso_a3", "currency_code", "name", "empty_column"] and big_mac_df[c].dtype != object]
        select_all = st.checkbox("ALL", value=False)
        vars_sel = st.multiselect("Parameters", numeric_cols, default=(numeric_cols if select_all else numeric_cols[:2]))

        st.markdown("#### 3 – Select date")
        data_filtered = big_mac_df.copy()
        if iso:
            data_filtered = data_filtered[data_filtered["iso_a3"] == iso]
        if currency:
            data_filtered = data_filtered[data_filtered["currency_code"] == currency]
        if country:
            data_filtered = data_filtered[data_filtered["name"] == country]

        years = sorted(data_filtered["date"].dt.year.unique())
        year = st.selectbox("Year", ["All"] + [str(y) for y in years])
        months = sorted(data_filtered[data_filtered["date"].dt.year == int(year)]["date"].dt.month.unique()) if year != "All" else sorted(data_filtered["date"].dt.month.unique())
        month = st.selectbox("Month", ["All"] + [str(m) for m in months])
        days = sorted(data_filtered[(data_filtered["date"].dt.year == int(year)) & (data_filtered["date"].dt.month == int(month))]["date"].dt.day.unique()) if (month != "All" and year != "All") else sorted(data_filtered["date"].dt.day.unique())
        day = st.selectbox("Day", ["All"] + [str(d) for d in days])

        st.markdown("#### 4 – Results")
        res = filter_big_mac(
            iso=iso or None,
            currency=currency or None,
            name=country or None,
            year=None if year == "All" else int(year),
            month=None if month == "All" else int(month),
            day=None if day == "All" else int(day),
            variables=vars_sel,
        )
        res = res.loc[:, res.columns != "empty_column"]
        res["date"] = res["date"].dt.date
        res_display = res.reset_index(drop=True)
        res_display.index += 1
        res_display.index.name = "Numéro de ligne"

    st.success(f"{len(res_display)} rows selected.")
    show_all = st.checkbox("Show all rows", value=False)
    st.dataframe(res_display if show_all else res_display.head(10), use_container_width=True)

    st.download_button(
        "Download CSV",
        res_display.to_csv(index=False).encode(),
        file_name=f"big_mac_{iso or currency or country}.csv",
        mime="text/csv",
    )  