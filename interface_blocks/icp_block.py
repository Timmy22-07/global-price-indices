# interface_blocks/wb_icp_block.py – v2025-07-08 FIXED
# ---------------------------------------------------------------------
# • Interface block for World Bank – ICP, with cache and loading spinner.
# • Correction des noms de colonnes sensibles à la casse
# • Protection contre les erreurs de métadonnées
# ---------------------------------------------------------------------

import streamlit as st
import pandas as pd
from core.world_bank_icp_loader import (
    load_icp_data,
    get_country_options as get_icp_countries,
    get_metadata_options,
    get_year_options as get_icp_years,
    filter_icp_data,
)

@st.cache_data(show_spinner=False)
def load_icp_cached():
    return load_icp_data()

def display_wb_icp_block():
    st.markdown("#### 1 – Select filters")
    with st.spinner("📊 Loading ICP data..."):
        df_icp = load_icp_cached()
        metadata = get_metadata_options(df_icp)

        # Vérification des métadonnées
        if not isinstance(metadata, pd.DataFrame):
            st.error("❌ Metadata is not a valid DataFrame.")
            st.stop()

        required_cols = ["Classification Name", "Series Name"]
        for col in required_cols:
            if col not in metadata.columns:
                st.error(f"❌ Missing column in metadata: {col}")
                st.stop()

        c1, c2 = st.columns(2)
        country = c1.selectbox("Country", get_icp_countries(df_icp))
        classification = c2.selectbox("Classification", metadata["Classification Name"].unique())

        series = st.selectbox("Series", metadata["Series Name"].unique())
        years = st.multiselect("Years (optional)", get_icp_years(df_icp))

        st.markdown("#### 2 – Results")
        filtered = filter_icp_data(
            df_icp,
            country=country,
            classification_name=classification,
            series_name=series,
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
        file_name=f"wb_icp_{country.replace(' ', '_')}_{series.replace(' ', '_')}.csv",
        mime="text/csv",
    )
