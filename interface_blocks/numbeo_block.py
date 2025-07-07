# interface_blocks/numbeo_block.py – v1
# ---------------------------------------------------------------------
# • Interface block for Numbeo – Cost of Living + PPP
# • Includes cache + spinner for performance
# ---------------------------------------------------------------------

import streamlit as st
from core.numbeo_loader import (
    load_numbeo_data,
    get_city_options,
    filter_numbeo_data,
)

@st.cache_data(show_spinner=False)
def load_numbeo_cached():
    return load_numbeo_data()

def display_numbeo_block():
    st.markdown("#### 1 – Select filters")
    with st.spinner("🏙️ Loading Numbeo data..."):
        df_num = load_numbeo_cached()

        city = st.selectbox("City", get_city_options(df_num))

        st.markdown("#### 2 – Results")
        filtered = filter_numbeo_data(df_num, city)

        filtered = filtered.reset_index(drop=True)
        filtered.index += 1
        filtered.index.name = "Numéro de ligne"

    st.success(f"{len(filtered)} rows selected.")
    show_all = st.checkbox("Show all rows", value=False)
    st.dataframe(filtered if show_all else filtered.head(10), use_container_width=True)

    st.download_button(
        "Download CSV",
        filtered.to_csv(index=False).encode(),
        file_name=f"numbeo_{city.replace(' ', '_')}.csv",
        mime="text/csv",
    )
