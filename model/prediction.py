import pickle
import sqlite3
import numpy as np

DB_PATH    = "database/healthcare.db"
MODEL_PATH = "model/healthcare_model.pkl"

# ── Model Load karo ────────────────────────────
def load_model():
    with open(MODEL_PATH, 'rb') as f:
        data = pickle.load(f)
    return data['model'], data['symptoms'], data['accuracy']

# ── Database se recommendations lo ────────────
def get_recommendations(disease_name):
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()

    # Disease info
    cur.execute("""
        SELECT disease_id, description, severity, category
        FROM diseases WHERE disease_name = ?
    """, (disease_name,))
    disease_info = cur.fetchone()

    if not disease_info:
        conn.close()
        return None

    did, desc, severity, category = disease_info

    # Medicines
    cur.execute("""
        SELECT medicine_name, dosage, duration, side_effects, notes
        FROM medicines WHERE disease_id = ?
    """, (did,))
    medicines = cur.fetchall()

    # Diet Plan
    cur.execute("""
        SELECT eat_foods, avoid_foods, meal_timing, diet_tips
        FROM diet_plans WHERE disease_id = ?
    """, (did,))
    diet = cur.fetchone()

    # Workout Plan
    cur.execute("""
        SELECT exercises, avoid_exercises, duration_mins, frequency, special_notes
        FROM workout_plans WHERE disease_id = ?
    """, (did,))
    workout = cur.fetchone()

    conn.close()

    return {
        'disease'   : disease_name,
        'description': desc,
        'severity'  : severity,
        'category'  : category,
        'medicines' : medicines,
        'diet'      : diet,
        'workout'   : workout,
    }

# ── Prediction karo ────────────────────────────
def predict_disease(model, symptom_list, user_symptoms):
    # Binary vector banao
    vector = [1 if s in user_symptoms else 0 for s in symptom_list]
    vector = np.array(vector).reshape(1, -1)

    # Predict karo
    probabilities = model.predict_proba(vector)[0]
    classes       = model.classes_

    # Top 3 results
    top3_idx = np.argsort(probabilities)[::-1][:3]
    top3     = [(classes[i], round(probabilities[i]*100, 1)) for i in top3_idx]

    predicted   = classes[top3_idx[0]]
    confidence  = probabilities[top3_idx[0]]

    return predicted, confidence, top3

# ── Report Print karo ─────────────────────────
def print_report(rec, confidence, top3, user_symptoms):
    line = "="*60

    print(f"\n{line}")
    print(f"   🏥  HEALTHCARE MANAGEMENT SYSTEM")
    print(f"        AI-POWERED DIAGNOSIS REPORT")
    print(f"{line}")

    print(f"\n👤 PATIENT SYMPTOMS:")
    for s in user_symptoms:
        print(f"   • {s}")

    print(f"\n{line}")
    print(f"📋 PREDICTED DISEASE : {rec['disease'].upper()}")
    print(f"   Category         : {rec['category']}")
    print(f"   Severity         : {rec['severity']}")
    print(f"   Description      : {rec['description']}")
    print(f"   Confidence       : {confidence*100:.1f}%")

    print(f"\n🔍 TOP 3 PREDICTIONS:")
    for i, (disease, pct) in enumerate(top3, 1):
        filled = int(pct / 5)
        bar    = "█" * filled + "░" * (20 - filled)
        print(f"   {i}. {disease:<18} {bar} {pct:.1f}%")

    print(f"\n{'─'*60}")
    print(f"💊 PRESCRIPTION / MEDICINES:")
    for i, med in enumerate(rec['medicines'], 1):
        name, dose, dur, side_fx, notes = med
        print(f"\n   {i}. {name}")
        print(f"      📌 Dosage      : {dose}")
        print(f"      ⏳ Duration    : {dur}")
        print(f"      ⚠️  Side Effects: {side_fx}")
        print(f"      💡 Notes       : {notes}")

    if rec['diet']:
        eat, avoid, timing, tips = rec['diet']
        print(f"\n{'─'*60}")
        print(f"🥗 DIET PLAN:")
        print(f"   ✅ Khao          : {eat}")
        print(f"   ❌ Avoid karo    : {avoid}")
        print(f"   🕐 Meal Timing   : {timing}")
        print(f"   💡 Tips          : {tips}")

    if rec['workout']:
        ex, avoid_ex, dur_min, freq, notes = rec['workout']
        print(f"\n{'─'*60}")
        print(f"🏃 WORKOUT ROUTINE:")
        print(f"   ✅ Exercises     : {ex}")
        print(f"   ❌ Avoid         : {avoid_ex}")
        print(f"   ⏱️  Duration      : {dur_min} minutes/session")
        print(f"   📅 Frequency     : {freq}")
        print(f"   💡 Special Notes : {notes}")

    print(f"\n{line}")
    print(f"  ⚠️  DISCLAIMER: Ye ek AI prediction hai.")
    print(f"      Asli ilaaj ke liye doctor se zaroor milein.")
    print(f"{line}\n")

# ── Prediction Log karo ────────────────────────
def log_prediction(symptoms, disease, confidence):
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO predictions
        (patient_id, symptoms_entered, predicted_disease, confidence_pct)
        VALUES (?, ?, ?, ?)
    """, (1, ", ".join(symptoms), disease, round(confidence*100, 2)))
    conn.commit()
    conn.close()

# ── Main Program ───────────────────────────────
def main():
    print("\n" + "="*60)
    print("   🏥  HEALTHCARE MANAGEMENT SYSTEM")
    print("        SYMPTOM CHECKER - AI POWERED")
    print("="*60)

    # Model load karo
    model, symptom_list, acc = load_model()
    print(f"\n✅ Model loaded! Accuracy: {acc*100:.1f}%")

    # Saare symptoms dikhao
    print(f"\n📋 Available Symptoms ({len(symptom_list)} total):")
    for i, s in enumerate(sorted(symptom_list), 1):
        print(f"   {i:2}. {s}")

    # User se symptoms lo
    print("\n" + "─"*60)
    print("💬 Apne symptoms enter karo (comma se alag karo)")
    print("   Example: fever, headache, nausea, body ache")
    print("─"*60)

    raw_input   = input("\n   Aapke symptoms: ").strip().lower()
    user_syms   = [s.strip() for s in raw_input.split(',')]

    # Match karo
    matched   = [s for s in user_syms if s in symptom_list]
    unmatched = [s for s in user_syms if s not in symptom_list]

    if unmatched:
        print(f"\n⚠️  Ye symptoms list mein nahi hain: {', '.join(unmatched)}")

    if not matched:
        print("\n❌ Koi bhi valid symptom nahi mila!")
        print("   Upar di gayi list se symptoms choose karo.")
        return

    print(f"\n✅ Matched symptoms: {', '.join(matched)}")
    print("\n🔄 Prediction ho rahi hai...")

    # Predict karo
    disease, confidence, top3 = predict_disease(model, symptom_list, matched)

    # Recommendations lo
    rec = get_recommendations(disease)

    if rec:
        # Report print karo
        print_report(rec, confidence, top3, matched)

        # Database mein save karo
        log_prediction(matched, disease, confidence)
        print("📝 Prediction database mein save ho gayi!")
    else:
        print(f"❌ {disease} ki recommendations nahi mili!")

if __name__ == "__main__":
    main()