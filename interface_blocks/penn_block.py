# interface_blocks/penn_block.py – v1
# ---------------------------------------------------------------------
# • Interface block for Penn World Table with cache and loading spinner.
# ---------------------------------------------------------------------

import streamlit as st
from core.penn_loader import (
    load_penn_data,
    get_country_options as get_penn_countries,
    get_variable_options,
    filter_penn_data,
)

@st.cache_data(show_spinner=False)
def load_penn_cached():
    return load_penn_data()

def display_penn_block():
    st.markdown("#### 1 – Select filters")
    with st.spinner("📊 Loading Penn World Table..."):
        df_pwt = load_penn_cached()

        c1, c2 = st.columns(2)
        country = c1.selectbox("Country", get_penn_countries(df_pwt))

        all_vars = get_variable_options(df_pwt)
        select_all = c2.checkbox("Select ALL variables", value=False)
        vars_sel = st.multiselect("Variables", all_vars, default=(all_vars if select_all else all_vars[:3]))

        years_sel = st.multiselect("Years (optional)", sorted(df_pwt["year"].unique()))

        st.markdown("#### 2 – Results")
        filtered = filter_penn_data(
            df_pwt,
            country=country,
            variables=vars_sel,
            years=years_sel or None,
        )

        filtered = filtered.reset_index(drop=True)
        filtered.index += 1
        filtered.index.name = "Numéro de ligne"

    st.success(f"{len(filtered)} rows selected.")
    show_all = st.checkbox("Show all rows", value=False)
    st.dataframe(filtered if show_all else filtered.head(10), use_container_width=True)

    st.download_button(
        "Download CSV",
        filtered.to_csv(index=False).encode(),
        file_name=f"penn_{country.replace(' ', '_')}.csv",
        mime="text/csv",
    )
