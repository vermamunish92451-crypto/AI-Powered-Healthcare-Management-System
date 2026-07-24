import pandas as pd
import numpy as np
import sqlite3
import pickle
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

print("="*55)
print("   🤖 HEALTHCARE ML MODEL TRAINING SHURU HO RAHA HAI")
print("="*55)

# ── Step 1: Data Load karo ─────────────────────
print("\n📂 Step 1: Dataset load ho raha hai...")
df = pd.read_csv("dataset/training_data.csv")
print(f"   ✅ Rows    : {len(df)}")
print(f"   ✅ Columns : {len(df.columns)}")
print(f"   ✅ Diseases: {df['disease'].nunique()}")

# ── Step 2: X aur Y alag karo ──────────────────
print("\n✂️  Step 2: Features aur Labels alag ho rahe hain...")
X = df.drop(columns=['disease'])   # Symptoms = features
y = df['disease']                  # Disease  = label
symptom_list = X.columns.tolist()
print(f"   ✅ Features (symptoms): {len(symptom_list)}")
print(f"   ✅ Labels   (diseases): {y.nunique()}")

# ── Step 3: Train/Test Split ───────────────────
print("\n✂️  Step 3: Data train aur test mein split ho raha hai...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,       # 20% test, 80% train
    random_state=42,
    stratify=y
)
print(f"   ✅ Training samples : {len(X_train)}")
print(f"   ✅ Testing  samples : {len(X_test)}")

# ── Step 4: Model Banao ────────────────────────
print("\n🌲 Step 4: Random Forest model ban raha hai...")
model = RandomForestClassifier(
    n_estimators=200,    # 200 decision trees
    max_depth=None,
    random_state=42,
    class_weight='balanced'
)

# ── Step 5: Train karo ─────────────────────────
print("\n🏋️  Step 5: Model training ho raha hai...")
model.fit(X_train, y_train)
print("   ✅ Training complete!")

# ── Step 6: Test karo ──────────────────────────
print("\n🧪 Step 6: Model test ho raha hai...")
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print(f"\n{'='*55}")
print(f"   🎯 MODEL ACCURACY : {accuracy*100:.1f}%")
print(f"{'='*55}")

# ── Step 7: Detailed Report ────────────────────
print("\n📊 Har disease ki accuracy:\n")
report = classification_report(y_test, y_pred, output_dict=True)
for disease in sorted(df['disease'].unique()):
    if disease in report:
        prec = report[disease]['precision'] * 100
        rec  = report[disease]['recall']    * 100
        f1   = report[disease]['f1-score']  * 100
        print(f"   {disease:<18} "
              f"Precision:{prec:5.1f}%  "
              f"Recall:{rec:5.1f}%  "
              f"F1:{f1:5.1f}%")

# ── Step 8: Model Save karo ───────────────────
print("\n💾 Step 8: Model save ho raha hai...")

model_data = {
    'model'       : model,
    'symptoms'    : symptom_list,
    'diseases'    : sorted(df['disease'].unique().tolist()),
    'accuracy'    : accuracy,
}

with open("model/healthcare_model.pkl", 'wb') as f:
    pickle.dump(model_data, f)

print("   ✅ Model saved: model/healthcare_model.pkl")

print(f"\n{'='*55}")
print("   🎉 MODEL SUCCESSFULLY TRAIN HO GAYA!")
print(f"   🎯 Final Accuracy: {accuracy*100:.1f}%")
print(f"{'='*55}\n")