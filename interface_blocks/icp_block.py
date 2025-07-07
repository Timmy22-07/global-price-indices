# interface_blocks/icp_block.py – v2025-07-08
# ---------------------------------------------------------------
# Bloc interface World Bank – ICP (filtrage interactif)
# ---------------------------------------------------------------

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

        # Vérification stricte des colonnes attendues
        required_cols = ["country_name", "classification_name", "series_name"]
        missing_cols = [col for col in required_cols if col not in df_icp.columns]

        if missing_cols:
            st.error(f"❌ The following columns are missing from the dataset: {missing_cols}")
            st.write("Available columns:", df_icp.columns.tolist())
            st.dataframe(df_icp.head())
            st.stop()

        # Étape 1 – Country
        countries = sorted(df_icp["country_name"].dropna().unique())
        country = st.selectbox("Country", countries)

        # Étape 2 – Classification et Series
        filtered_class = df_icp[df_icp["country_name"] == country]
        classifications = sorted(filtered_class["classification_name"].dropna().unique())
        classification = st.selectbox("Classification", classifications)

        filtered_series = filtered_class[filtered_class["classification_name"] == classification]
        series_names = sorted(filtered_series["series_name"].dropna().unique())
        series = st.selectbox("Series", series_names)

        # Étape 3 – Années disponibles
        year_cols = [col for col in df_icp.columns if isinstance(col, int)]
        years = st.multiselect("Years (optional)", year_cols)

    # Résultats
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
