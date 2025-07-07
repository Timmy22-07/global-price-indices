# interface_blocks/numbeo_block.py – v3
# ---------------------------------------------------------------------
# • Bloc d’interface pour Numbeo – Cost of Living + PPP
# • Utilise la colonne "name" comme identifiant principal (ville, pays)
# • Exclut "id_city" et autres colonnes inutiles des sélections
# ---------------------------------------------------------------------

import streamlit as st
from core.numbeo_loader import (
    load_numbeo_data,
    get_variable_options,
    filter_numbeo_data,
)

@st.cache_data(show_spinner=False)
def load_numbeo_cached():
    return load_numbeo_data()

def display_numbeo_block():
    st.markdown("#### 1 – Select filters")

    with st.spinner("🏙️ Loading Numbeo data..."):
        df = load_numbeo_cached()

        if "name" not in df.columns:
            st.error("❌ La colonne 'name' est absente du fichier Numbeo.")
            return

        regions = sorted(df["name"].dropna().unique())
        region = st.selectbox("Region (city, country)", regions)

        variables = get_variable_options(df)
        default_vars = variables[:5] if len(variables) > 5 else variables
        selected_vars = st.multiselect("Variables", variables, default=default_vars)

        filtered = filter_numbeo_data(df, region, selected_vars)

    # Affichage des résultats
    st.success(f"{len(filtered)} rows selected.")
    st.dataframe(filtered, use_container_width=True)

    st.download_button(
        label="📥 Download filtered data",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name=f"numbeo_{region.replace(' ', '_')}.csv",
        mime="text/csv",
    )
