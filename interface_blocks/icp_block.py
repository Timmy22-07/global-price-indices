# interface_blocks/icp_block.py – v2025-07-08 (corrigé snake_case & structure en 3 étapes)
# -------------------------------------------------------------------
# Bloc interface World Bank – ICP (filtrage interactif et clair)
# -------------------------------------------------------------------

import streamlit as st
import pandas as pd

from core.world_bank_icp_loader import (
    load_icp_data,
    filter_icp_data,
)

@st.cache_data(show_spinner=False)
def load_icp_cached():
    return load_icp_data()

def display_wb_icp_block():
    st.markdown("#### 1 – Select a country")

    with st.spinner("📊 Loading ICP data..."):
        df_icp = load_icp_cached()

        # Vérification stricte des colonnes attendues (en snake_case)
        required_cols = ["country_name", "classification_name", "series_name"]
        for col in required_cols:
            if col not in df_icp.columns:
                st.error(f"❌ Column '{col}' is missing from the dataset.")
                st.dataframe(df_icp.head())
                st.stop()

        countries = sorted(df_icp["country_name"].dropna().unique())
        selected_country = st.selectbox("Country", countries)

    # Étape 2 – Sélection des métadonnées
    st.markdown("#### 2 – Choose classification and series")

    filtered_step2 = df_icp[df_icp["country_name"] == selected_country]

    classifications = sorted(filtered_step2["classification_name"].dropna().unique())
    series_names = sorted(filtered_step2["series_name"].dropna().unique())

    c1, c2 = st.columns(2)
    selected_classification = c1.selectbox("Classification", classifications)
    selected_series = c2.selectbox("Series", series_names)

    # Étape 3 – Choix des années
    st.markdown("#### 3 – Select year(s)")

    year_cols = [col for col in df_icp.columns if isinstance(col, int)]
    selected_years = st.multiselect("Years (optional)", year_cols)

    # Résultats
    st.markdown("#### 4 – Results")
    filtered = filter_icp_data(
        df_icp,
        country=selected_country,
        classification_name=selected_classification,
        series_name=selected_series,
        years=selected_years or None,
    )

    filtered = filtered.reset_index(drop=True)
    filtered.index += 1
    filtered.index.name = "Row"

    st.success(f"{len(filtered)} row(s) selected.")
    show_all = st.checkbox("Show all rows", value=False)
    st.dataframe(filtered if show_all else filtered.head(10), use_container_width=True)

    st.download_button(
        "Download CSV",
        filtered.to_csv(index=False).encode(),
        file_name=f"wb_icp_{selected_country.replace(' ', '_')}_{selected_series.replace(' ', '_')}.csv",
        mime="text/csv",
    )
