"""
core/big_mac.py
---------------
Utilities for the “Big Mac Index” data-set.

• load_data()            → charge le fichier Excel (cache mémoïsé)
• get_lookup_table()     → renvoie toutes les combinaisons ISO / currency / name
• resolve_identity()     → à partir d’une entrée unique (ISO, currency ou name),
                           retourne toutes les combinaisons possibles
• get_country_metadata() → renvoie toutes les combinaisons pour un nom de pays donné
• filter_data()          → renvoie le DataFrame filtré selon identifiants,
                           date (année / mois / jour) et variables numériques
"""

from pathlib import Path
from functools import lru_cache
import pandas as pd
import streamlit as st

# --- Chemin du fichier Excel -------------------------------------------------
DATA_PATH = (
    Path(__file__).resolve().parent.parent
    / "data" / "raw" / "big_mac" / "Big Mac Index.xlsx"
)

# --- Colonnes clés -----------------------------------------------------------
ID_COLS   = ["iso_a3", "currency_code", "name"]
DATE_COL  = "date"

@lru_cache(maxsize=1)
def load_data() -> pd.DataFrame:
    """Charge le fichier Excel et le met en cache."""
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Big Mac file not found → {DATA_PATH}")
    df = pd.read_excel(DATA_PATH, engine="openpyxl")
    df[DATE_COL] = pd.to_datetime(df[DATE_COL], errors="coerce")
    return df


# --------------------------------------------------------------------------- #
#                            OUTILS D’IDENTITÉ                                #
# --------------------------------------------------------------------------- #
@st.cache_data
def get_lookup_table() -> pd.DataFrame:
    """Renvoie toutes les combinaisons ISO / currency / name sans doublons."""
    df = load_data()
    return df[ID_COLS].drop_duplicates().reset_index(drop=True)


def resolve_identity(iso: str | None = None,
                     currency: str | None = None,
                     name: str | None = None) -> pd.DataFrame:
    """
    À partir d’un seul identifiant fourni, renvoie toutes les combinaisons
    possibles (⇢ DataFrame à 3 colonnes).  Lève ValueError si zéro ou
    plusieurs identifiants reçus.
    """
    keys = [iso, currency, name]
    if sum(k is not None for k in keys) != 1:
        raise ValueError("Provide *exactly* one of iso / currency / name")

    df = load_data()
    if iso is not None:
        mask = df["iso_a3"] == iso
    elif currency is not None:
        mask = df["currency_code"] == currency
    else:  # name
        mask = df["name"] == name

    return df.loc[mask, ID_COLS].drop_duplicates().reset_index(drop=True)

@st.cache_data
def get_country_metadata(name: str) -> pd.DataFrame:
    """
    Renvoie toutes les combinaisons iso_a3 / currency_code correspondant à un pays donné.
    Permet le remplissage automatique des champs selon le nom du pays.
    """
    df = load_data()
    mask = df["name"].str.lower() == name.lower()
    return df.loc[mask, ID_COLS].drop_duplicates().reset_index(drop=True)


# --------------------------------------------------------------------------- #
#                              FILTRAGE                                       #
# --------------------------------------------------------------------------- #
def filter_data(iso: str,
                currency: str,
                name: str,
                year: int | None = None,
                month: int | None | str = None,
                day: int | None | str = None,
                variables: list[str] | None = None) -> pd.DataFrame:
    """
    Renvoie un sous-ensemble du DataFrame filtré par identifiants, date
    (année/mois/jour) et variables numériques sélectionnées.
    • month ou day peuvent être "All" pour ignorer le filtre correspondant.
    • variables None → toutes les colonnes numériques.
    """
    df = load_data()

    # --- filtre identifiants ---
    mask = (
        (df["iso_a3"] == iso) &
        (df["currency_code"] == currency) &
        (df["name"] == name)
    )

    # --- filtre dates ---
    if year is not None:
        mask &= df[DATE_COL].dt.year == year
    if month not in (None, "All"):
        mask &= df[DATE_COL].dt.month == int(month)
    if day not in (None, "All"):
        mask &= df[DATE_COL].dt.day == int(day)

    df = df.loc[mask].copy()

    # --- sélection des variables numériques ---
    numeric_cols = [
        c for c in df.columns
        if c not in ID_COLS + [DATE_COL] and pd.api.types.is_numeric_dtype(df[c])
    ]
    if variables:
        numeric_cols = [c for c in numeric_cols if c in variables]

    return df[[DATE_COL] + numeric_cols].reset_index(drop=True)
