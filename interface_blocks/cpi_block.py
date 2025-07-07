# interface_blocks/wb_cpi_block.py – v1
# ---------------------------------------------------------------------
# • Interface block for World Bank – CPI, optimized with cache and spinner.
# ---------------------------------------------------------------------

import streamlit as st
from core.world_bank_cpi_loader import (
    load_wb_cpi_data,
    get_country_options as get_cpi_countries,
    get_series_options,
    get_year_options as get_cpi_years,
    filter_wb_cpi_data,
)

@st.cache_data(show_spinner=False)
def load_cpi_cached():
    return load_wb_cpi_data()

def display_wb_cpi_block():
    st.markdown("#### 1 – Select filters")
    with st.spinner("📊 Loading World Bank CPI data..."):
        df_cpi = load_cpi_cached()

        c1, c2 = st.columns(2)
        country = c1.selectbox("Country", get_cpi_countries(df_cpi))
        series = c2.selectbox("CPI Series", get_series_options(df_cpi))

        years_available = get_cpi_years(df_cpi)
        years = st.multiselect("Years (optional)", years_available)

        st.markdown("#### 2 – Results")
        filtered = filter_wb_cpi_data(
            df_cpi,
            country=country,
            series=series,
            years=years or None,
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
        file_name=f"wb_cpi_{country}_{series.replace(' ', '_')}.csv",
        mime="text/csv",
    )
