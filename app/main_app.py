# app/main_app.py – v2025‑07‑07 clean
# ---------------------------------------------------------------------
# ✅ Onglet d’accueil AVANT la navigation par catégorie
# ✅ Bloc Numbeo appelé une seule fois
# ✅ Message de fin clair
# ---------------------------------------------------------------------

from __future__ import annotations
import os, sys
from pathlib import Path
import streamlit as st

# Ajoute le dossier parent au chemin d'import
sys.path.append(os.path.abspath(os.path.join(Path(__file__).parent, "..")))

# ⵀ Configuration
st.set_page_config(page_title="Global Indices", layout="wide")
st.title("🌐 Global Indices")

# ⵀ Onglet Accueil + Config
from core.welcome import display_welcome_tab
from core.source_config import CATEGORY_TO_SOURCES

# ⵀ Core loaders
# from core.big_mac import load_data as load_big_mac, get_lookup_table, filter_data as filter_big_mac
# from core.bis_loader import load_bis_reer_data, get_filter_options, filter_bis_data
# from core.numbeo_loader import load_numbeo_data, filter_numbeo_data, get_variable_options
# from core.penn_loader import load_penn_data, get_country_options as get_penn_countries, get_variable_options as get_penn_vars, filter_penn_data
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

# ⵀ Interface blocks
from interface_blocks.big_mac_block import display_big_mac_block
from interface_blocks.bis_block import display_bis_block
from interface_blocks.cpi_block import display_wb_cpi_block
from interface_blocks.icp_block import display_wb_icp_block
from interface_blocks.penn_block import display_penn_block
from interface_blocks.numbeo_block import display_numbeo_block

# ⵀ Onglet accueil
st.sidebar.header("🌐 Navigation")
nav_choice = st.sidebar.radio(
    label="",  # ⬅️ Supprime le texte "Navigation"
    options=["🏠 Home", "Explore datas"],
    index=1,
    horizontal=False
)
if nav_choice == "🏠 Home":
    display_welcome_tab()
    st.stop()


# ⵀ Navigation
category = st.sidebar.radio("Category", list(CATEGORY_TO_SOURCES.keys()))
source = st.sidebar.selectbox("Source", CATEGORY_TO_SOURCES[category])
st.subheader(f"📊 {source}")

# ⵀ Affichage conditionnel selon source
with st.spinner("Chargement des données..."):
    if source == "The Economist – Big Mac Index":
        display_big_mac_block()
    elif source == "Bank for International Settlements – REER (Real Effective Exchange Rates)":
        display_bis_block()
    elif source == "World Bank – CPI (Consumer Price Index)":
        display_wb_cpi_block()
    elif source == "World Bank – ICP (International Comparison Program) Database":
        display_wb_icp_block()
    elif source == "Penn World Table":
        display_penn_block()
    elif source == "Numbeo – Cost of Living + PPP (Purchasing Power Parity)":
        display_numbeo_block()

# ⵀ Message de confirmation final
st.info("✅ Application chargée avec succès. Sélectionnez une source dans la barre latérale pour commencer.")
