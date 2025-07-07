# interface_blocks/numbeo_block.py – v2
# ---------------------------------------------------------------------
# • Bloc d’interface pour Numbeo – Cost of Living + PPP
# • Compatible avec la structure réelle du fichier .db
# ---------------------------------------------------------------------

import streamlit as st
from core.numbeo_loader import (
    load_numbeo_data,
    get_city_options,
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
        cities = get_city_options(df)
        city = st.selectbox("City", cities)

        variables = get_variable_options(df)
        default_vars = variables[:5] if len(variables) > 5 else variables
        selected_vars = st.multiselect("Variables", variables, default=default_vars)

        filtered = filter_numbeo_data(df, city, selected_vars)

    # Affichage des résultats
    st.success(f"{len(filtered)} rows selected.")
    st.dataframe(filtered, use_container_width=True)

    st.download_button(
        label="📥 Download filtered data",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name=f"numbeo_{city.replace(' ', '_')}.csv",
        mime="text/csv",
    )
