import sqlite3

DB_PATH = "database/healthcare.db"
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON")

# ══════════════════════════════════════
#  1. DISEASES
# ══════════════════════════════════════
diseases = [
    ("Diabetes",     "Blood mein sugar ka level zyada rehta hai",      "Moderate", "Endocrine"),
    ("Hypertension", "Blood pressure normal se zyada rehta hai",       "Moderate", "Cardiovascular"),
    ("Common Cold",  "Naak aur gale ki viral infection",               "Mild",     "Respiratory"),
    ("Malaria",      "Mosquito se failne wali bimari",                 "Severe",   "Infectious"),
    ("Typhoid",      "Salmonella bacteria se pet ki bimari",           "Severe",   "Infectious"),
    ("Migraine",     "Ek taraf bahut tez sir dard",                    "Moderate", "Neurological"),
    ("Asthma",       "Saans nali mein sujan se saans lene mein dikkat","Moderate", "Respiratory"),
    ("Dengue",       "Aedes mosquito se hone wali viral fever",        "Severe",   "Infectious"),
    ("Pneumonia",    "Lungs mein infection aur sujan",                 "Severe",   "Respiratory"),
    ("Anemia",       "Khoon mein hemoglobin/iron ki kami",             "Mild",     "Blood"),
]
cur.executemany("""
    INSERT OR IGNORE INTO diseases (disease_name, description, severity, category)
    VALUES (?, ?, ?, ?)
""", diseases)
print(f"✅ {len(diseases)} Diseases insert ho gaye!")

# ══════════════════════════════════════
#  2. SYMPTOMS
# ══════════════════════════════════════
symptoms = [
    ("fatigue",), ("frequent urination",), ("increased thirst",),
    ("blurred vision",), ("slow healing wounds",), ("headache",),
    ("dizziness",), ("chest pain",), ("shortness of breath",),
    ("nausea",), ("runny nose",), ("sneezing",), ("sore throat",),
    ("cough",), ("mild fever",), ("high fever",), ("chills",),
    ("sweating",), ("body ache",), ("vomiting",), ("abdominal pain",),
    ("loss of appetite",), ("weakness",), ("severe headache",),
    ("sensitivity to light",), ("wheezing",), ("chest tightness",),
    ("rash",), ("joint pain",), ("muscle pain",), ("pale skin",),
    ("rapid heartbeat",), ("brittle nails",), ("cold hands",),
    ("eye pain",), ("bleeding gums",), ("neck stiffness",),
    ("back pain",), ("weight loss",), ("hair loss",),
]
cur.executemany(
    "INSERT OR IGNORE INTO symptoms (symptom_name) VALUES (?)",
    symptoms
)
print(f"✅ {len(symptoms)} Symptoms insert ho gaye!")

# ══════════════════════════════════════
#  3. DISEASE-SYMPTOM MAPPING
# ══════════════════════════════════════
def get_id(table, name_col, name):
    cur.execute(f"SELECT rowid FROM {table} WHERE {name_col}=?", (name,))
    row = cur.fetchone()
    return row[0] if row else None

mapping = {
    "Diabetes":     ["fatigue","frequent urination","increased thirst",
                     "blurred vision","slow healing wounds","weakness","weight loss"],
    "Hypertension": ["headache","dizziness","chest pain",
                     "shortness of breath","rapid heartbeat","back pain"],
    "Common Cold":  ["runny nose","sneezing","sore throat",
                     "cough","mild fever","headache","fatigue"],
    "Malaria":      ["high fever","chills","sweating","body ache",
                     "nausea","vomiting","headache"],
    "Typhoid":      ["high fever","abdominal pain","loss of appetite",
                     "weakness","headache","back pain","nausea"],
    "Migraine":     ["severe headache","nausea","sensitivity to light",
                     "vomiting","dizziness"],
    "Asthma":       ["wheezing","shortness of breath","chest tightness",
                     "cough","fatigue"],
    "Dengue":       ["high fever","rash","joint pain","muscle pain",
                     "eye pain","bleeding gums","nausea"],
    "Pneumonia":    ["high fever","cough","chest pain",
                     "shortness of breath","chills","fatigue"],
    "Anemia":       ["fatigue","weakness","pale skin","rapid heartbeat",
                     "brittle nails","cold hands","hair loss"],
}
for disease, syms in mapping.items():
    did = get_id("diseases", "disease_name", disease)
    for s in syms:
        sid = get_id("symptoms", "symptom_name", s)
        if did and sid:
            cur.execute("""
                INSERT INTO disease_symptoms (disease_id, symptom_id)
                VALUES (?, ?)
            """, (did, sid))
print("✅ Disease-Symptom mapping insert ho gayi!")

# ══════════════════════════════════════
#  4. MEDICINES
# ══════════════════════════════════════
medicines = {
    "Diabetes": [
        ("Metformin",      "500mg din mein 2 baar", "Ongoing",  "Weight gain ho sakti hai",   "Khaane ke saath lo"),
        ("Insulin Glargine","10 units raat ko",     "Ongoing",  "Low sugar ho sakti hai",     "Sugar daily check karo"),
        ("Glipizide",      "5mg subah",             "Ongoing",  "Nausea ho sakta hai",        "Khali pet mat lo"),
    ],
    "Hypertension": [
        ("Amlodipine",  "5mg subah 1 baar",  "Ongoing", "Pair mein sujan",          "Subah lo"),
        ("Losartan",    "50mg subah 1 baar", "Ongoing", "Chakkar aa sakte hain",    "Potassium avoid karo"),
        ("Atenolol",    "25mg subah 1 baar", "Ongoing", "Thakaan mehsoos ho sakti", "Achanak band mat karo"),
    ],
    "Common Cold": [
        ("Paracetamol", "500mg din mein 3 baar", "5 din",  "Zyada lene se liver damage", "Khaane ke baad lo"),
        ("Cetirizine",  "10mg raat ko",          "5 din",  "Neend aati hai",             "Raat ko lo"),
        ("Vitamin C",   "500mg din mein 1 baar", "7 din",  "Koi khaas nahi",             "Immunity badhata hai"),
    ],
    "Malaria": [
        ("Chloroquine", "500mg din mein 2 baar", "3 din",   "Pet dard ho sakta hai",   "Poora course khatam karo"),
        ("Primaquine",  "15mg din mein 1 baar",  "14 din",  "Kamzori aa sakti hai",    "Relapse rokta hai"),
    ],
    "Typhoid": [
        ("Azithromycin","500mg din mein 1 baar", "7 din",    "Diarrhea ho sakta hai",   "Khali pet lo"),
        ("Ceftriaxone", "1g injection",          "7-14 din", "Injection site pe dard",  "Hospital mein lagwao"),
    ],
    "Migraine": [
        ("Sumatriptan", "50mg jab dard ho",      "Zaroorat pe", "Chest tightness",      "Max 2 baar/din"),
        ("Ibuprofen",   "400mg din mein 3 baar", "3 din",       "Pet mein jalan",       "Khaane ke baad lo"),
        ("Topiramate",  "25mg raat ko",          "Long term",   "Yaadaasht kamzor ho",  "Prevention ke liye"),
    ],
    "Asthma": [
        ("Salbutamol",  "2 puff zaroorat pe",    "Ongoing",  "Dil tez dhad sakta hai", "Rescue inhaler"),
        ("Budesonide",  "2 puff din mein 2 baar","Ongoing",  "Muh mein infection",     "Kulla karo baad mein"),
    ],
    "Dengue": [
        ("Paracetamol", "500mg har 6 ghante",    "Bukhaar tak", "Liver pe asar",       "Aspirin BILKUL mat lo"),
        ("ORS",         "2 sachet/din",          "5-7 din",     "Koi nahi",            "Hydrated raho"),
    ],
    "Pneumonia": [
        ("Amoxicillin", "500mg din mein 3 baar", "7-10 din", "Allergy ho sakti hai",   "Poora course lo"),
        ("Azithromycin","500mg din mein 1 baar", "5 din",    "Pet kharab ho sakta",    "Atypical ke liye"),
    ],
    "Anemia": [
        ("Ferrous Sulfate","200mg din mein 2 baar","3 mahine","Constipation ho sakti", "Vitamin C ke saath lo"),
        ("Folic Acid",     "5mg din mein 1 baar",  "3 mahine","Koi khaas nahi",       "Mahilaon ke liye zaroori"),
    ],
}
for disease, meds in medicines.items():
    did = get_id("diseases", "disease_name", disease)
    for m in meds:
        cur.execute("""
            INSERT INTO medicines
            (disease_id, medicine_name, dosage, duration, side_effects, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (did,) + m)
print("✅ Medicines insert ho gayi!")

# ══════════════════════════════════════
#  5. DIET PLANS
# ══════════════════════════════════════
diet_plans = {
    "Diabetes":     ("Whole grains, palak, machli, akhrot, low-GI fruits",
                     "Meetha, white bread, chawal, cold drinks, alcohol",
                     "Har 3-4 ghante mein thoda thoda khao",
                     "Portion size control karo, sugar monitor karo"),
    "Hypertension": ("Kela, oats, palak, berries, low-fat dairy",
                     "Namak, processed food, red meat, caffeine, alcohol",
                     "Din mein 4-5 baar thoda khao",
                     "DASH diet follow karo, namak 2g se kam rakho"),
    "Common Cold":  ("Warm soup, adrak chai, nimbu, lahsun, shahad",
                     "Cold drinks, ice cream, fried food, dairy",
                     "Din mein 5-6 baar warm cheezein lo",
                     "8-10 glass warm paani peeo rozana"),
    "Malaria":      ("Chawal, kela, ubli sabziyan, dahi, coconut water",
                     "Mirchy masala, tel wala khana, alcohol",
                     "Din mein 5-6 baar halka khana khao",
                     "Aasaan pachne wala khana khao, rest karo"),
    "Typhoid":      ("Ubla chawal, dal, ubla aloo, kela, dahi",
                     "Kacha khaana, mirch masala, high-fiber food",
                     "Baar baar thoda thoda khao",
                     "Sirf saaf aur fresh khana khao, ubla paani peeo"),
    "Migraine":     ("Magnesium wale foods, adrak, cherry, salmon, badam",
                     "Alcohol, caffeine, aged cheese, MSG wale foods",
                     "Regular time pe khao, skip mat karo",
                     "Food diary rakho apne triggers pehchano"),
    "Asthma":       ("Seb, adrak, haldi, palak, salmon, Vitamin D foods",
                     "Sulfites, cold foods, artificial colors",
                     "Garam khana khao, zyada mat khao ek baar mein",
                     "Khana jaldi jaldi mat khao"),
    "Dengue":       ("Papaya leaf juice, coconut water, anar, orange, kiwi",
                     "Mirch masala, tel wala, alcohol, processed food",
                     "Baar baar liquid lo",
                     "Platelet badhane wale foods lo, hydration zaroori"),
    "Pneumonia":    ("Warm soup, fruit juice, shahad, haldi doodh, protein",
                     "Cold drinks, alcohol, smoking, sugary foods",
                     "Din mein 5-6 baar garam khana khao",
                     "Zyada se zyada paani aur liquid lo"),
    "Anemia":       ("Palak, masoor dal, red meat, tofu, pumpkin seeds",
                     "Chai coffee khaane ke saath, zyada calcium",
                     "Iron wala khana Vitamin C ke saath khao",
                     "Nimbu ke saath iron zyada absorb hota hai"),
}
for disease, (eat, avoid, timing, tips) in diet_plans.items():
    did = get_id("diseases", "disease_name", disease)
    cur.execute("""
        INSERT INTO diet_plans
        (disease_id, eat_foods, avoid_foods, meal_timing, diet_tips)
        VALUES (?, ?, ?, ?, ?)
    """, (did, eat, avoid, timing, tips))
print("✅ Diet plans insert ho gaye!")

# ══════════════════════════════════════
#  6. WORKOUT PLANS
# ══════════════════════════════════════
workout_plans = {
    "Diabetes":     ("Walking, cycling, swimming, yoga, light weights",
                     "Khali pet exercise, heavy lifting without monitoring",
                     30, "5 din/hafta",
                     "Exercise ke baad sugar check karo"),
    "Hypertension": ("Brisk walking, swimming, cycling, yoga, breathing",
                     "Heavy lifting, intense sprinting",
                     30, "5 din/hafta",
                     "BP check karo exercise se pehle"),
    "Common Cold":  ("Light stretching, gentle yoga",
                     "Gym, running, swimming",
                     15, "Sirf theek lage tab",
                     "Bukhaar mein bilkul mat karo"),
    "Malaria":      ("Bukhaar mein complete rest",
                     "Koi bhi exercise bukhaar mein",
                     10, "Recovery ke baad dhire dhire",
                     "Jab tak doctor na kahe mat karo"),
    "Typhoid":      ("Bed rest, recovery ke baad gentle walk",
                     "Koi bhi strenuous exercise",
                     10, "Recovery ke baad slowly",
                     "Poori tarah theek hone ke baad hi karo"),
    "Migraine":     ("Gentle yoga, walking, swimming, relaxation",
                     "High intensity workout, neck strain",
                     20, "3-4 din/hafta",
                     "Trigger avoid karo, regular routine rakho"),
    "Asthma":       ("Swimming, walking, yoga, cycling",
                     "Cold air mein exercise, high pollen area",
                     20, "4 din/hafta",
                     "Inhaler hamesha saath rakho"),
    "Dengue":       ("Complete bed rest",
                     "Koi bhi exercise bimari mein",
                     0,  "Recovery ke baad only",
                     "Platelet normal hone ke baad hi karo"),
    "Pneumonia":    ("Deep breathing exercises, gentle walk",
                     "Strenuous exercise bimari mein",
                     10, "Recovery ke baad",
                     "Breathing exercises lungs ke liye zaroori"),
    "Anemia":       ("Light walking, yoga, gentle stretching",
                     "High intensity cardio, heavy lifting",
                     20, "4 din/hafta",
                     "Hemoglobin improve hone tak halki exercise"),
}
for disease, (ex, avoid_ex, dur, freq, notes) in workout_plans.items():
    did = get_id("diseases", "disease_name", disease)
    cur.execute("""
        INSERT INTO workout_plans
        (disease_id, exercises, avoid_exercises, duration_mins, frequency, special_notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (did, ex, avoid_ex, dur, freq, notes))
print("✅ Workout plans insert ho gaye!")

# ══════════════════════════════════════
#  7. SAMPLE PATIENTS
# ══════════════════════════════════════
patients = [
    ("Rahul Sharma",  28, "Male",   "B+",  "9876543210", "Delhi"),
    ("Priya Singh",   35, "Female", "O+",  "9812345678", "Mumbai"),
    ("Amit Kumar",    45, "Male",   "A+",  "9898989898", "Jaipur"),
    ("Sunita Verma",  52, "Female", "AB+", "9765432100", "Lucknow"),
    ("Ravi Patel",    38, "Male",   "B-",  "9700012345", "Surat"),
    ("Meera Joshi",   29, "Female", "O-",  "9811112222", "Pune"),
    ("Vikram Yadav",  60, "Male",   "A-",  "9833334444", "Kanpur"),
    ("Anjali Gupta",  22, "Female", "B+",  "9855556666", "Agra"),
]
cur.executemany("""
    INSERT OR IGNORE INTO patients
    (name, age, gender, blood_group, contact, city)
    VALUES (?, ?, ?, ?, ?, ?)
""", patients)
print(f"✅ {len(patients)} Sample patients insert ho gaye!")

conn.commit()
conn.close()

print("\n" + "="*50)
print("🎉 SAARA DATA SUCCESSFULLY INSERT HO GAYA!")
print("="*50)
print("  ✅ 10 Diseases")
print("  ✅ 40 Symptoms")
print("  ✅ Disease-Symptom Mapping")
print("  ✅ 25+ Medicines")
print("  ✅ 10 Diet Plans")
print("  ✅ 10 Workout Plans")
print("  ✅ 8 Sample Patients")
print("="*50)