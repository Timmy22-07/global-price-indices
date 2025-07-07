# explore_numbeo_db.py

import sqlite3
from pathlib import Path

# Chemin vers ta base de données Numbeo
DB_PATH = Path("data/raw/numbeo/numbeo")

def list_tables():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
    return tables

def preview_table(table_name, limit=5):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name});")
        structure = cursor.fetchall()

        df = conn.execute(f"SELECT * FROM {table_name} LIMIT {limit};").fetchall()
        return structure, df

# ─────────────────────────── Lancement ────────────────────────────
if __name__ == "__main__":
    print("📂 Tables disponibles dans la base Numbeo :\n")
    tables = list_tables()
    for t in tables:
        print(f"  • {t}")
    
    print("\n──────────────────────────────\n")

    # Affiche un aperçu de chaque table
    for table in tables:
        print(f"🔎 Structure de la table : {table}")
        structure, preview = preview_table(table)
        for col in structure:
            print(f"  - {col[1]} ({col[2]})")
        print("\nAperçu des premières lignes :")
        for row in preview:
            print("  ", row)
        print("\n──────────────────────────────\n")
