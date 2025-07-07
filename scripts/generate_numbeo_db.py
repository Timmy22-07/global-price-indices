import sqlite3
import os

# === Chemin de destination final ===
db_path = r"C:\Users\Timothée ABADJI\OneDrive\Desktop\global_price_indices\data\raw\numbeo\numbeo.db"

# === Crée le dossier si besoin ===
os.makedirs(os.path.dirname(db_path), exist_ok=True)

# === Connexion à la base ===
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# === Création de la table ===
cursor.execute('''
CREATE TABLE IF NOT EXISTS cities (
    id_city INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    common_meal TEXT,
    meal_for_two TEXT,
    one_way_ticket TEXT,
    monthly_pass TEXT,
    gasoline TEXT,
    base_cost TEXT,
    internet TEXT,
    simple_apartment_centre TEXT,
    simple_apartment_outside TEXT,
    large_apartment_centre TEXT,
    large_apartment_outside TEXT,
    salary TEXT,
    status TEXT
)
''')

# === Exemple d’insertion (à adapter ou automatiser ensuite) ===
cities = [
    ("Toronto", "15", "50", "3.25", "150", "1.85", "200", "60", "1800", "1400", "2500", "2000", "3500", "juillet 2025"),
    ("Dakar", "5", "25", "0.60", "10", "1.40", "80", "25", "300", "200", "500", "350", "250", "juillet 2025")
]

cursor.executemany('''
INSERT INTO cities (
    name, common_meal, meal_for_two, one_way_ticket, monthly_pass, gasoline, base_cost,
    internet, simple_apartment_centre, simple_apartment_outside, large_apartment_centre,
    large_apartment_outside, salary, status
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
''', cities)

conn.commit()
conn.close()

print("✅ Base Numbeo créée et enregistrée avec succès.")
