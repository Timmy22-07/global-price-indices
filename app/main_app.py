# app/main_app.py – v2025‑07‑06h2 (corrected preload & UX flow)
# ---------------------------------------------------------------------
# ✔️ Preload non-bloquant avec spinner
# ✔️ Suppression des imports en double
# ✔️ Message de confirmation de chargement
# ---------------------------------------------------------------------

from __future__ import annotations

import os, sys
from pathlib import Path
import streamlit as st

# Ajoute le dossier parent au chemin d'import
sys.path.append(os.path.abspath(os.path.join(Path(__file__).parent, "..")))

# ──────────────── Configuration de la page ──────────────── #
st.set_page_config(page_title="Global Price Indices", layout="wide")

with st.spinner("⏳ Initialisation des données..."):
    st.title("🌐 Global Price Indices")

    # Étape 1 – Préchargement des données (1 seule fois)
    if "preload_done" not in st.session_state:
        from core.big_mac import load_data as load_big_mac
        from core.bis_loader import load_bis_reer_data
        from core.numbeo_loader import load_numbeo_data
        from core.penn_loader import load_penn_data
        from core.world_bank_cpi_loader import load_wb_cpi_data
        from core.world_bank_icp_loader import load_icp_data

        load_big_mac()
        load_bis_reer_data()
        load_numbeo_data()
        load_penn_data()
        load_wb_cpi_data()
        load_icp_data()

        st.session_state["preload_done"] = True

# ──────────────── Config navigation + imports ──────────────── #
from core.source_config import CATEGORY_TO_SOURCES

from core.big_mac import (
    load_data as load_big_mac,
    get_lookup_table,
    filter_data as filter_big_mac,
)

from core.bis_loader import (
    load_bis_reer_data,
    get_filter_options,
    filter_bis_data,
)

from core.numbeo_loader import (
    load_numbeo_data,
    get_city_options,
    filter_numbeo_data,
)

from core.penn_loader import (
    load_penn_data,
    get_country_options as get_penn_countries,
    get_variable_options,
    filter_penn_data,
)

from core.world_bank_cpi_loader import (
    load_wb_cpi_data,
    get_country_options as get_cpi_countries,
    get_series_options,
    get_year_options as get_cpi_years,
    filter_wb_cpi_data,
)

from core.world_bank_icp_loader import (
    load_icp_data,
    get_country_options as get_icp_countries,
    get_metadata_options,
    get_year_options as get_icp_years,
    filter_icp_data,
)

# ──────────────── Navigation latérale ──────────────── #
st.sidebar.header("🌐 Navigation")
category = st.sidebar.radio("Category", list(CATEGORY_TO_SOURCES.keys()))
source = st.sidebar.selectbox("Source", CATEGORY_TO_SOURCES[category])
st.subheader(f"📊 {source}")

# ──────────────── Bloc de contenu par source ──────────────── #
from interface_blocks.big_mac_block import display_big_mac_block
from interface_blocks.bis_block import display_bis_block
from interface_blocks.cpi_block import display_wb_cpi_block
from interface_blocks.icp_block import display_wb_icp_block
from interface_blocks.penn_block import display_penn_block
from interface_blocks.numbeo_block import display_numbeo_block

if source == "The Economist – Big Mac Index":
    display_big_mac_block()
elif source == "BIS – Real Effective Exchange Rates (REER)":
    display_bis_block()
elif source == "World Bank – CPI (Consumer Price Index)":
    display_wb_cpi_block()
elif source == "World Bank – ICP Database":
    display_wb_icp_block()
elif source == "Penn World Table":
    display_penn_block()
elif source == "Numbeo – Cost of Living + PPP":
    display_numbeo_block()

# ──────────────── Message de confirmation ──────────────── #
st.info("✅ Application chargée avec succès.")
