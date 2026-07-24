import sqlite3
import pandas as pd
import numpy as np
import os

DB_PATH = "database/healthcare.db"
conn = sqlite3.connect(DB_PATH)

# Database se diseases aur symptoms lo
diseases = pd.read_sql("SELECT disease_id, disease_name FROM diseases", conn)
symptoms = pd.read_sql("SELECT symptom_id, symptom_name FROM symptoms", conn)
mapping  = pd.read_sql("SELECT disease_id, symptom_id FROM disease_symptoms", conn)
conn.close()

all_symptoms  = symptoms['symptom_name'].tolist()
disease_names = diseases.set_index('disease_id')['disease_name'].to_dict()
sym_id_map    = symptoms.set_index('symptom_name')['symptom_id'].to_dict()
sym_name_map  = {v: k for k, v in sym_id_map.items()}

# Disease ke liye symptoms ka dictionary banao
dis_sym = mapping.groupby('disease_id')['symptom_id'].apply(list).to_dict()

print("🔄 Training data generate ho raha hai...")

rows = []
np.random.seed(42)

for did, sym_ids in dis_sym.items():
    dname = disease_names[did]
    disease_syms = [sym_name_map[s] for s in sym_ids if s in sym_name_map]

    # Har disease ke liye 100 samples banao
    for _ in range(100):
        row = {s: 0 for s in all_symptoms}

        # Core symptoms hamesha add karo
        for s in disease_syms:
            row[s] = 1

        # 1-2 symptoms randomly hatao (real data jaisa)
        drop_count = np.random.randint(1, 3)
        drop = np.random.choice(disease_syms,
                                size=min(drop_count, len(disease_syms)),
                                replace=False)
        for s in drop:
            row[s] = 0

        # 0-2 random symptoms add karo (noise)
        other_syms = [s for s in all_symptoms if s not in disease_syms]
        noise = np.random.randint(0, 3)
        for s in np.random.choice(other_syms, size=noise, replace=False):
            row[s] = 1

        row['disease'] = dname
        rows.append(row)

# DataFrame banao
df = pd.DataFrame(rows)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)

# CSV save karo
csv_path = "dataset/training_data.csv"
df.to_csv(csv_path, index=False)

print(f"✅ Dataset ready!")
print(f"   Rows    : {len(df)}")
print(f"   Columns : {len(df.columns)}")
print(f"   Diseases: {df['disease'].nunique()}")
print(f"   Saved at: {csv_path}")
print(f"\n📊 Sample data:")
print(df[['disease'] + all_symptoms[:5]].head(5).to_string())