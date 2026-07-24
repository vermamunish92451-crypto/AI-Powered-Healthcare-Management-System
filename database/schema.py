import sqlite3
import os

DB_PATH = "database/healthcare.db"

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Foreign keys enable karo
cur.execute("PRAGMA foreign_keys = ON")

# ── TABLE 1: Patients ──────────────────────────
cur.execute("""
CREATE TABLE IF NOT EXISTS patients (
    patient_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    age          INTEGER NOT NULL,
    gender       TEXT CHECK(gender IN ('Male','Female','Other')),
    blood_group  TEXT,
    contact      TEXT,
    city         TEXT,
    created_at   TEXT DEFAULT (datetime('now'))
)
""")
print("✅ Table 1: patients")

# ── TABLE 2: Diseases ──────────────────────────
cur.execute("""
CREATE TABLE IF NOT EXISTS diseases (
    disease_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    disease_name TEXT NOT NULL UNIQUE,
    description  TEXT,
    severity     TEXT CHECK(severity IN ('Mild','Moderate','Severe')),
    category     TEXT
)
""")
print("✅ Table 2: diseases")

# ── TABLE 3: Symptoms ──────────────────────────
cur.execute("""
CREATE TABLE IF NOT EXISTS symptoms (
    symptom_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    symptom_name TEXT NOT NULL UNIQUE
)
""")
print("✅ Table 3: symptoms")

# ── TABLE 4: Disease-Symptom Mapping ───────────
cur.execute("""
CREATE TABLE IF NOT EXISTS disease_symptoms (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    disease_id INTEGER REFERENCES diseases(disease_id),
    symptom_id INTEGER REFERENCES symptoms(symptom_id)
)
""")
print("✅ Table 4: disease_symptoms")

# ── TABLE 5: Medicines ─────────────────────────
cur.execute("""
CREATE TABLE IF NOT EXISTS medicines (
    medicine_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    disease_id    INTEGER REFERENCES diseases(disease_id),
    medicine_name TEXT NOT NULL,
    dosage        TEXT,
    duration      TEXT,
    side_effects  TEXT,
    notes         TEXT
)
""")
print("✅ Table 5: medicines")

# ── TABLE 6: Diet Plans ────────────────────────
cur.execute("""
CREATE TABLE IF NOT EXISTS diet_plans (
    diet_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    disease_id   INTEGER REFERENCES diseases(disease_id),
    eat_foods    TEXT,
    avoid_foods  TEXT,
    meal_timing  TEXT,
    diet_tips    TEXT
)
""")
print("✅ Table 6: diet_plans")

# ── TABLE 7: Workout Plans ─────────────────────
cur.execute("""
CREATE TABLE IF NOT EXISTS workout_plans (
    workout_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    disease_id       INTEGER REFERENCES diseases(disease_id),
    exercises        TEXT,
    avoid_exercises  TEXT,
    duration_mins    INTEGER,
    frequency        TEXT,
    special_notes    TEXT
)
""")
print("✅ Table 7: workout_plans")

# ── TABLE 8: Predictions Log ───────────────────
cur.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    pred_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id       INTEGER REFERENCES patients(patient_id),
    symptoms_entered TEXT,
    predicted_disease TEXT,
    confidence_pct   REAL,
    predicted_at     TEXT DEFAULT (datetime('now'))
)
""")
print("✅ Table 8: predictions")

conn.commit()
conn.close()

print("\n🎉 Saare 8 tables successfully ban gaye!")
print("📁 Database saved: database/healthcare.db")