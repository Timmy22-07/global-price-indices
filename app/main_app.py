# app/main_app.py – v2025‑07‑06h4 (with Welcome tab)
# ---------------------------------------------------------------------
# ✅ Suppression du préchargement massif en mémoire
# ✅ Chargement paresseux (lazy loading) selon la source sélectionnée
# ✅ Utilisation de @st.cache_data pour alléger la RAM
# ✅ Ajout d’un onglet Accueil avant la navigation
# ---------------------------------------------------------------------

from __future__ import annotations

import os, sys
from pathlib import Path
import streamlit as st

# Ajoute le dossier parent au chemin d'import
sys.path.append(os.path.abspath(os.path.join(Path(__file__).parent, "..")))

# ──────────────── Configuration de la page ──────────────── #
st.set_page_config(page_title="Global Price Indices", layout="wide")
st.title("🌐 Global Price Indices")

# ──────────────── Import du Welcome tab (défini dans numbeo_loader) ── #
from core.welcome import display_welcome_tab

# Affiche l'onglet d'accueil avant toute navigation
display_welcome_tab()

# ──────────────── Config navigation + imports ──────────────── #
from core.source_config import CATEGORY_TO_SOURCES

from core.big_mac import load_data as load_big_mac, get_lookup_table, filter_data as filter_big_mac
from core.bis_loader import load_bis_reer_data, get_filter_options, filter_bis_data
from core.numbeo_loader import load_numbeo_data, filter_numbeo_data, get_variable_options
from core.penn_loader import load_penn_data, get_country_options as get_penn_countries, get_variable_options as get_penn_vars, filter_penn_data
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

with st.spinner("Chargement des données..."):
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
