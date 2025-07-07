"""
update_world_indices.py
───────────────────────
• Télécharge les valeurs actuelles des indices mondiaux depuis Yahoo Finance
• Met à jour / crée le fichier world_indices.csv
• Chemin de sortie : …/global_price_indices/data/raw/yahoo/world_indices.csv
"""

import yfinance as yf
import pandas as pd
from pathlib import Path
from datetime import datetime

# ─────────── Paramètres ───────────
SYMBOLS = [
    "^GSPC", "^DJI", "^IXIC", "^NYA", "^XAX", "^BUK100P", "^RUT", "^VIX",
    "^FTSE", "^GDAXI", "^FCHI", "^STOXX50E", "^N100", "^BFX", "MOEX.ME",
    "^HSI", "^STI", "^AXJO", "^AORD", "^BSESN", "^JKSE", "^KLSE", "^NZ50",
    "^KS11", "^TWII", "^GSPTSE", "^BVSP", "^MXX", "^IPSA", "^MERV",
    "^TA125.TA", "^CASE30", "^JN0U.JO", "DX-Y.NYB", "^125904-USD-STRD",
    "^XDB", "^XDE", "000001.SS", "^N225", "^XDN", "^XDA"
]

# Chemin de sortie
BASE_DIR = Path(r"C:/Users/Timothée ABADJI/OneDrive/Desktop/global_price_indices/data/raw/yahoo")
BASE_DIR.mkdir(parents=True, exist_ok=True)
CSV_PATH = BASE_DIR / "world_indices.csv"

# ─────────── Collecte des données ───────────
records = []
tickers = yf.Tickers(" ".join(SYMBOLS))

for symbol in SYMBOLS:
    try:
        info = tickers.tickers[symbol].info
        price   = info.get("regularMarketPrice")
        change  = info.get("regularMarketChange")
        pct_chg = info.get("regularMarketChangePercent")
        volume  = info.get("regularMarketVolume")
        day_low  = info.get("regularMarketDayLow")
        day_high = info.get("regularMarketDayHigh")
        wk52_low  = info.get("fiftyTwoWeekLow")
        wk52_high = info.get("fiftyTwoWeekHigh")

        records.append({
            "Symbol": symbol,
            "Name": info.get("longName") or info.get("shortName"),
            "Price": price,
            "Change": change,
            "Change (%)": pct_chg,
            "Volume": volume,
            "Day Range": f"{day_low} – {day_high}",
            "52 Wk Range": f"{wk52_low} – {wk52_high}",
            "Last Update": datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        })
    except Exception as e:
        print(f"[!] Erreur pour {symbol} → {e}")

# ─────────── Sauvegarde CSV ───────────
df = pd.DataFrame(records)
df.to_csv(CSV_PATH, index=False)
print(f"✅ Fichier mis à jour : {CSV_PATH}")
