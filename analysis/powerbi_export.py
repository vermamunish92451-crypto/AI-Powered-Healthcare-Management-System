import sqlite3
import pandas as pd
import os

DB_PATH    = "database/healthcare.db"
EXPORT_DIR = "powerbi_export"
os.makedirs(EXPORT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

print("="*55)
print("   📤 POWER BI EXPORT SHURU HO RAHA HAI...")
print("="*55)

# ── CSV 1: Diseases ────────────────────────────
df = pd.read_sql("SELECT * FROM diseases", conn)
df.to_csv(f"{EXPORT_DIR}/01_diseases.csv", index=False)
print(f"\n✅ 01_diseases.csv        ({len(df)} rows)")

# ── CSV 2: Symptoms ────────────────────────────
df = pd.read_sql("SELECT * FROM symptoms", conn)
df.to_csv(f"{EXPORT_DIR}/02_symptoms.csv", index=False)
print(f"✅ 02_symptoms.csv        ({len(df)} rows)")

# ── CSV 3: Medicines ───────────────────────────
df = pd.read_sql("""
    SELECT m.medicine_id, d.disease_name, d.severity,
           m.medicine_name, m.dosage, m.duration,
           m.side_effects, m.notes
    FROM medicines m
    JOIN diseases d ON m.disease_id = d.disease_id
""", conn)
df.to_csv(f"{EXPORT_DIR}/03_medicines.csv", index=False)
print(f"✅ 03_medicines.csv       ({len(df)} rows)")

# ── CSV 4: Diet Plans ──────────────────────────
df = pd.read_sql("""
    SELECT dp.diet_id, d.disease_name, d.category,
           dp.eat_foods, dp.avoid_foods,
           dp.meal_timing, dp.diet_tips
    FROM diet_plans dp
    JOIN diseases d ON dp.disease_id = d.disease_id
""", conn)
df.to_csv(f"{EXPORT_DIR}/04_diet_plans.csv", index=False)
print(f"✅ 04_diet_plans.csv      ({len(df)} rows)")

# ── CSV 5: Workout Plans ───────────────────────
df = pd.read_sql("""
    SELECT wp.workout_id, d.disease_name, d.severity,
           wp.exercises, wp.avoid_exercises,
           wp.duration_mins, wp.frequency, wp.special_notes
    FROM workout_plans wp
    JOIN diseases d ON wp.disease_id = d.disease_id
""", conn)
df.to_csv(f"{EXPORT_DIR}/05_workout_plans.csv", index=False)
print(f"✅ 05_workout_plans.csv   ({len(df)} rows)")

# ── CSV 6: Patients ────────────────────────────
df = pd.read_sql("SELECT * FROM patients", conn)
df.to_csv(f"{EXPORT_DIR}/06_patients.csv", index=False)
print(f"✅ 06_patients.csv        ({len(df)} rows)")

# ── CSV 7: Predictions ─────────────────────────
df = pd.read_sql("SELECT * FROM predictions", conn)
df.to_csv(f"{EXPORT_DIR}/07_predictions.csv", index=False)
print(f"✅ 07_predictions.csv     ({len(df)} rows)")

# ── CSV 8: Disease Summary (Power BI ke liye) ──
df = pd.read_sql("""
    SELECT
        d.disease_name,
        d.severity,
        d.category,
        COUNT(DISTINCT ds.symptom_id) as total_symptoms,
        COUNT(DISTINCT m.medicine_id) as total_medicines,
        wp.duration_mins              as workout_duration,
        wp.frequency                  as workout_frequency
    FROM diseases d
    LEFT JOIN disease_symptoms ds ON d.disease_id = ds.disease_id
    LEFT JOIN medicines m         ON d.disease_id = m.disease_id
    LEFT JOIN workout_plans wp    ON d.disease_id = wp.disease_id
    GROUP BY d.disease_name
    ORDER BY d.severity DESC
""", conn)
df.to_csv(f"{EXPORT_DIR}/08_disease_summary.csv", index=False)
print(f"✅ 08_disease_summary.csv ({len(df)} rows)")

# ── CSV 9: Symptom Matrix ──────────────────────
diseases_df = pd.read_sql("SELECT disease_id, disease_name FROM diseases", conn)
symptoms_df = pd.read_sql("SELECT symptom_id, symptom_name FROM symptoms", conn)
mapping_df  = pd.read_sql("SELECT disease_id, symptom_id FROM disease_symptoms", conn)

matrix = pd.DataFrame(0,
    index  = diseases_df['disease_name'],
    columns= symptoms_df['symptom_name']
)
for _, row in mapping_df.iterrows():
    dn = diseases_df.loc[diseases_df['disease_id']==row['disease_id'],'disease_name'].values
    sn = symptoms_df.loc[symptoms_df['symptom_id']==row['symptom_id'],'symptom_name'].values
    if len(dn) and len(sn):
        matrix.loc[dn[0], sn[0]] = 1

matrix.index.name = 'disease_name'
matrix.reset_index().to_csv(f"{EXPORT_DIR}/09_symptom_matrix.csv", index=False)
print(f"✅ 09_symptom_matrix.csv  ({len(matrix)} rows)")

conn.close()

print(f"\n{'='*55}")
print("   🎉 SAARI 9 CSV FILES BAN GAYI!")
print(f"   📁 Folder: powerbi_export/")
print(f"\n   Power BI mein kaise load karein:")
print(f"   1. Power BI Desktop open karo")
print(f"   2. Get Data → Text/CSV")
print(f"   3. powerbi_export/ folder se CSV lo")
print(f"   4. Saari 9 files load karo")
print(f"{'='*55}\n")