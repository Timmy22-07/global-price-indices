import pandas as pd

# 🔁 Chargement
input_file = "data/raw/penn_world_table/Penn World Table.xlsx"
output_file = "data/raw/penn_world_table/Penn World Table (filtered).xlsx"

# 🔍 Lecture avec nettoyage automatique des noms de colonnes
df = pd.read_excel(input_file)
df.columns = df.columns.str.strip().str.lower()  # supprime les espaces et met en minuscules

# ✅ Vérifie que 'year' existe
if "year" not in df.columns:
    raise ValueError("❌ La colonne 'year' est introuvable dans le fichier Excel.")

# 🧹 Filtrage des années ≥ 2020
df["year"] = pd.to_numeric(df["year"], errors="coerce")  # force conversion en numérique
df_filtered = df[df["year"] >= 2020].copy()

# 💾 Sauvegarde
df_filtered.to_excel(output_file, index=False)
print(f"✅ Données filtrées sauvegardées dans : {output_file}")
