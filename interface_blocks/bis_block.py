# interface_blocks/bis_block.py – v1 (externalized)
# ---------------------------------------------------------------------
# • Interface block for BIS REER, with caching and loading spinner.
# ---------------------------------------------------------------------

import streamlit as st
from core.bis_loader import load_bis_reer_data, get_filter_options, filter_bis_data

@st.cache_data(show_spinner=False)
def load_bis_reer_cached():
    return load_bis_reer_data()

def display_bis_block():
    st.markdown("#### 1 – Select filters")
    with st.spinner("🔄 Loading BIS REER data..."):
        df_bis = load_bis_reer_cached()
        opts = get_filter_options(df_bis)

    c1, c2, c3 = st.columns(3)
    ref = c1.selectbox("Reference Area", opts["reference_area"])
    freq = c2.selectbox("Frequency", opts["frequency"])
    type_ = c3.selectbox("Type", opts["type"])

    c4, c5 = st.columns(2)
    basket = c4.selectbox("Basket", opts["basket"])
    unit = c5.selectbox("Unit", opts["unit"])

    years = ["All"] + sorted(df_bis["date"].dt.year.dropna().unique().astype(int))
    year = st.selectbox("Year", years)

    st.markdown("#### 2 – Results")
    filtered = filter_bis_data(
        df_bis,
        reference_area=ref,
        frequency=freq,
        type_=type_,
        basket=basket,
        unit=unit,
        year=None if year == "All" else int(year)
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
        file_name=f"bis_reer_{ref}.csv",
        mime="text/csv"
    )
