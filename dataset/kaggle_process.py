import pandas as pd
import numpy as np
import sqlite3
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

print("="*55)
print("   🔥 KAGGLE REAL DATA PROCESSING SHURU...")
print("="*55)

# ── Step 1: Data Load karo ─────────────────────
df_raw = pd.read_csv("dataset/dataset.csv")
df_raw.columns = df_raw.columns.str.strip()

print(f"\n✅ Raw Dataset:")
print(f"   Rows     : {len(df_raw)}")
print(f"   Diseases : {df_raw['Disease'].nunique()}")
print(f"   Diseases list: {sorted(df_raw['Disease'].unique().tolist())}")

# ── Step 2: Symptoms Extract karo ─────────────
symptom_cols = [c for c in df_raw.columns if c.startswith('Symptom')]
all_symptoms = set()
for col in symptom_cols:
    vals = df_raw[col].dropna().str.strip().str.replace(' ','_')
    all_symptoms.update(vals)
all_symptoms = sorted(list(all_symptoms))

print(f"\n✅ Total Unique Symptoms: {len(all_symptoms)}")

# ── Step 3: Binary Matrix banao ────────────────
print("\n🔄 Binary matrix ban raha hai...")
rows = []
for _, row in df_raw.iterrows():
    syms = []
    for col in symptom_cols:
        if pd.notna(row[col]):
            syms.append(row[col].strip().replace(' ','_'))
    vec = {s: 1 if s in syms else 0 for s in all_symptoms}
    vec['disease'] = row['Disease'].strip()
    rows.append(vec)

df = pd.DataFrame(rows)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

print(f"✅ Processed Dataset:")
print(f"   Rows     : {len(df)}")
print(f"   Features : {len(all_symptoms)}")
print(f"   Diseases : {df['disease'].nunique()}")

# ── Step 4: CSV Save karo ──────────────────────
df.to_csv("dataset/kaggle_training_data.csv", index=False)
print(f"\n✅ Saved: dataset/kaggle_training_data.csv")

# ── Step 5: Model Train karo ───────────────────
print("\n🤖 Model train ho raha hai...")
X = df[all_symptoms]
y = df['disease']

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y)

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    class_weight='balanced'
)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
acc    = accuracy_score(y_test, y_pred)

print(f"\n{'='*55}")
print(f"   🎯 MODEL ACCURACY : {acc*100:.1f}%")
print(f"{'='*55}")

# ── Step 6: Model Save karo ────────────────────
model_data = {
    'model'   : model,
    'symptoms': all_symptoms,
    'diseases': sorted(df['disease'].unique().tolist()),
    'accuracy': acc
}
with open("model/healthcare_model.pkl", 'wb') as f:
    pickle.dump(model_data, f)

print(f"\n✅ Model saved: model/healthcare_model.pkl")

# ── Step 7: Database Update karo ───────────────
print("\n🗄️  Database update ho rahi hai...")
conn = sqlite3.connect("database/healthcare.db")
cur  = conn.cursor()

# Purani diseases clear karo
cur.execute("DELETE FROM disease_symptoms")
cur.execute("DELETE FROM diseases")
cur.execute("DELETE FROM symptoms")
cur.execute("DELETE FROM medicines")
cur.execute("DELETE FROM diet_plans")
cur.execute("DELETE FROM workout_plans")

# Nayi diseases insert karo
diseases = sorted(df['disease'].unique().tolist())
for d in diseases:
    cur.execute("""
        INSERT OR IGNORE INTO diseases
        (disease_name, description, severity, category)
        VALUES (?, ?, ?, ?)
    """, (d, f"{d} ki bimari", "Moderate", "General"))

# Symptoms insert karo
for s in all_symptoms:
    cur.execute(
        "INSERT OR IGNORE INTO symptoms (symptom_name) VALUES (?)",
        (s,))

# Disease-Symptom mapping
for _, row in df_raw.iterrows():
    disease = row['Disease'].strip()
    cur.execute("SELECT disease_id FROM diseases WHERE disease_name=?",
                (disease,))
    did = cur.fetchone()
    if not did:
        continue
    did = did[0]
    for col in symptom_cols:
        if pd.notna(row[col]):
            sym = row[col].strip().replace(' ', '_')
            cur.execute(
                "SELECT symptom_id FROM symptoms WHERE symptom_name=?",
                (sym,))
            sid = cur.fetchone()
            if sid:
                cur.execute("""
                    INSERT INTO disease_symptoms (disease_id, symptom_id)
                    VALUES (?, ?)
                """, (did, sid[0]))

conn.commit()
conn.close()

print(f"✅ Database updated!")
print(f"\n{'='*55}")
print(f"   🎉 KAGGLE DATA SUCCESSFULLY PROCESS HO GAYA!")
print(f"   ✅ {len(diseases)} Diseases")
print(f"   ✅ {len(all_symptoms)} Symptoms")
print(f"   ✅ Model Accuracy: {acc*100:.1f}%")
print(f"{'='*55}\n")