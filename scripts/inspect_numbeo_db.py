import sqlite3
from pathlib import Path
import pandas as pd

# 📍 Chemin vers le fichier Numbeo
db_path = Path("data/raw/numbeo/numbeo.db")

# 🔍 Vérification de l’existence
if not db_path.exists():
    raise FileNotFoundError(f"Fichier introuvable : {db_path}")

# 🔌 Connexion à la base
conn = sqlite3.connect(db_path)

# 📋 Liste des tables
tables_query = "SELECT name FROM sqlite_master WHERE type='table';"
tables = pd.read_sql(tables_query, conn)

print("📂 Tables trouvées dans la base Numbeo :")
print(tables)

# 🧪 Aperçu de la première table (si elle existe)
if not tables.empty:
    first_table = tables.iloc[0, 0]
    print(f"\n🔍 Aperçu de la table '{first_table}':")
    preview = pd.read_sql(f"SELECT * FROM {first_table} LIMIT 10;", conn)
    print(preview)

# 🔐 Fermeture
conn.close()
# Affichage complet des noms de table
print("\n📦 Liste brute des tables (debug):")
print(tables["name"].tolist())

import sqlite3

db_path = "data/raw/numbeo/numbeo.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Combien de lignes ?
cursor.execute("SELECT COUNT(*) FROM cities;")
nb_villes = cursor.fetchone()[0]
print(f"🌍 Nombre total de villes dans la base : {nb_villes}")

# Afficher la liste des villes (limite 100 pour pas tout afficher d'un coup)
cursor.execute("SELECT name, status FROM cities LIMIT 100;")
villes = cursor.fetchall()

print("\n🧾 Quelques villes dans la base :")
for nom, statut in villes:
    print(f"• {nom} ({statut})")

conn.close()
