# Step 1: Libraries import karo
import sqlite3
import os

# Step 2: Database ka path set karo
DB_PATH = "database/healthcare.db"

# Step 3: Database se connect karo
conn = sqlite3.connect(DB_PATH)

# Step 4: Cursor banao (cursor se SQL commands chalate hain)
cur = conn.cursor()

print("✅ Database connected successfully!")

# Step 5: Pehla table banao - Diseases
cur.execute("""
CREATE TABLE IF NOT EXISTS diseases (
    disease_id   INTEGER PRIMARY KEY,
    disease_name TEXT NOT NULL,
    description  TEXT,
    severity     TEXT
)
""")
print("✅ Diseases table created!")

# Step 6: Symptoms table banao
cur.execute("""
CREATE TABLE IF NOT EXISTS symptoms (
    symptom_id   INTEGER PRIMARY KEY,
    symptom_name TEXT NOT NULL
)
""")
print("✅ Symptoms table created!")

# Step 7: Medicines table banao
cur.execute("""
CREATE TABLE IF NOT EXISTS medicines (
    medicine_id   INTEGER PRIMARY KEY,
    disease_id    INTEGER,
    medicine_name TEXT,
    dosage        TEXT,
    duration      TEXT
)
""")
print("✅ Medicines table created!")

# Step 8: Diet Plans table banao
cur.execute("""
CREATE TABLE IF NOT EXISTS diet_plans (
    diet_id     INTEGER PRIMARY KEY,
    disease_id  INTEGER,
    eat_foods   TEXT,
    avoid_foods TEXT
)
""")
print("✅ Diet Plans table created!")

# Step 9: Workout Plans table banao
cur.execute("""
CREATE TABLE IF NOT EXISTS workout_plans (
    workout_id  INTEGER PRIMARY KEY,
    disease_id  INTEGER,
    exercises   TEXT,
    duration    TEXT
)
""")
print("✅ Workout Plans table created!")

# Step 10: Save karo aur band karo
conn.commit()
conn.close()

print("\n🎉 Database aur saare tables successfully ban gaye!")