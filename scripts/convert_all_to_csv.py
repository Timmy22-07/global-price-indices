# convert_all_to_csv.py
import pandas as pd
from pathlib import Path

base_folder = Path("data/raw")

# Extensions et sous-dossiers à parcourir
extensions = [".xlsx"]
subfolders = ["big_mac", "bis", "penn_world_table", "world_bank"]

for sub in subfolders:
    folder = base_folder / sub
    for file in folder.glob("*.xlsx"):
        try:
            df = pd.read_excel(file)
            new_file = file.with_suffix(".csv")
            df.to_csv(new_file, index=False)
            print(f"✅ {file.name} → {new_file.name}")
        except Exception as e:
            print(f"❌ Erreur pour {file.name} : {e}")
