import sqlite3
from pathlib import Path
import pandas as pd

# 📍 Chemin vers le fichier Numbeo
db_path = Path("data/raw/numbeo/numbeo.db")

# 🔍 Vérification de l’existence
if not db_path.exists():
    raise FileNotFoundError(f"Fichier introuvable : {db_path}")

# 🔌 Connexion à la base
with sqlite3.connect(db_path) as conn:
    # 📋 Liste des tables
    tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
    tables_df = pd.read_sql(tables_query, conn)
    table_names = tables_df["name"].tolist()

    print("📂 Tables trouvées dans la base Numbeo :")
    print(table_names)

    # 🧪 Si la table 'cities' existe
    if "cities" in table_names:
        print("\n📊 Lecture de la table 'cities'...")

        # Charger toute la table dans un DataFrame
        df = pd.read_sql("SELECT * FROM cities", conn)

        # 🧱 Colonnes disponibles
        print("\n🔎 Colonnes :", df.columns.tolist())

        # 👁️ Aperçu
        print("\n🧾 Aperçu (10 premières lignes) :")
        print(df.head(10))

        # 📏 Taille
        print(f"\n📐 Dimensions : {len(df)} lignes × {len(df.columns)} colonnes")

        # 💾 Export CSV
        output_path = Path("data/processed/numbeo_full_export.csv")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"\n✅ Données exportées : {output_path}")

        # 🌍 Aperçu des noms de villes
        if "name" in df.columns and "status" in df.columns:
            print("\n🏙️ Liste de quelques villes (max 100) :")
            for _, row in df[["name", "status"]].head(100).iterrows():
                print(f"• {row['name']} ({row['status']})")
        else:
            print("⚠️ Colonnes 'name' ou 'status' non trouvées.")
    else:
        print("❌ Table 'cities' non trouvée dans la base.")
