# interface_blocks/icp_block.py – v2025-07-08b
# ---------------------------------------------------------------------
# Bloc interface World Bank – ICP (filtrage structuré : pays → classification → série → année)
# ---------------------------------------------------------------------

import streamlit as st
import pandas as pd

from core.world_bank_icp_loader import (
    load_icp_data,
    get_country_options as get_icp_countries,
    get_year_options as get_icp_years,
    filter_icp_data,
)

@st.cache_data(show_spinner=False)
def load_icp_cached():
    return load_icp_data()

def display_wb_icp_block():
    st.markdown("#### 1 – Select country")

    with st.spinner("📊 Loading ICP data..."):
        df_icp = load_icp_cached()

        # Vérifie les colonnes nécessaires
        required_cols = ["country_name", "classification_name", "series_name"]
        for col in required_cols:
            if col not in df_icp.columns:
                st.error(f"❌ Column '{col}' is missing from the dataset.")
                st.dataframe(df_icp.head())
                st.stop()

        # Sélection du pays
        countries = sorted(df_icp["country_name"].dropna().unique())
        country = st.selectbox("Country", countries)

        # Filtrage des classifications disponibles pour le pays
        df_filtered_country = df_icp[df_icp["country_name"] == country]
        classifications = sorted(df_filtered_country["classification_name"].dropna().unique())

    st.markdown("#### 2 – Select classification and series")

    c1, c2 = st.columns(2)
    classification = c1.selectbox("Classification", classifications)

    # Filtrage des séries selon classification choisie
    df_filtered_classif = df_filtered_country[df_filtered_country["classification_name"] == classification]
    series_names = sorted(df_filtered_classif["series_name"].dropna().unique())
    series = c2.selectbox("Series", series_names)

    st.markdown("#### 3 – Select years (optional)")

    # Filtrage final pour détecter les colonnes d’années disponibles
    df_filtered_series = df_filtered_classif[df_filtered_classif["series_name"] == series]
    year_cols = [col for col in df_filtered_series.columns if isinstance(col, int)]
    years = st.multiselect("Years", year_cols)

    st.markdown("#### 4 – Results")

    filtered = filter_icp_data(
        df_icp,
        country=country,
        classification_name=classification,
        series_name=series,
        year=years or None,
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
