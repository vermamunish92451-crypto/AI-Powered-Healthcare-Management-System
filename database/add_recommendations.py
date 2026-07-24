import sqlite3

conn = sqlite3.connect("database/healthcare.db")
cur  = conn.cursor()

def get_did(name):
    cur.execute("SELECT disease_id FROM diseases WHERE disease_name=?", (name,))
    r = cur.fetchone()
    return r[0] if r else None

# ── Clear purana data ──────────────────────────
cur.execute("DELETE FROM medicines")
cur.execute("DELETE FROM diet_plans")
cur.execute("DELETE FROM workout_plans")
print("✅ Purana data clear!")

# ══════════════════════════════════════════════
# MEDICINES
# ══════════════════════════════════════════════
medicines = {
    "(vertigo) Paroymsal  Positional Vertigo": [
        ("Epley Maneuver", "Doctor ke saath", "1-3 sessions", "Chakkar aane par", "Ghar pe mat karo akele"),
        ("Meclizine", "25mg din mein 3 baar", "5-7 din", "Neend aa sakti hai", "Driving mat karo"),
    ],
    "AIDS": [
        ("Antiretroviral Therapy (ART)", "Doctor ke mutabiq", "Lifelong", "Side effects vary", "Kabhi band mat karo"),
        ("Tenofovir", "300mg din mein 1 baar", "Lifelong", "Kidney pe asar", "Regular checkup karo"),
    ],
    "Acne": [
        ("Benzoyl Peroxide", "Cream raat ko lagao", "3 months", "Skin dry ho sakti", "Sunscreen use karo"),
        ("Clindamycin gel", "Subah lagao", "2 months", "Mild irritation", "Face saaf rakhna"),
    ],
    "Alcoholic hepatitis": [
        ("Prednisolone", "40mg din mein 1 baar", "28 din", "Immunity kam hoti", "Alcohol bilkul band"),
        ("Pentoxifylline", "400mg din mein 3 baar", "28 din", "Nausea", "Liver function check karo"),
    ],
    "Allergy": [
        ("Cetirizine", "10mg raat ko", "Zaroorat pe", "Neend aati hai", "Trigger se door raho"),
        ("Loratadine", "10mg subah", "Zaroorat pe", "Kam neend aati", "Long term safe hai"),
    ],
    "Arthritis": [
        ("Ibuprofen", "400mg din mein 3 baar", "Doctor ke mutabiq", "Pet mein jalan", "Khaane ke baad lo"),
        ("Methotrexate", "7.5mg hafta mein 1 baar", "Long term", "Liver pe asar", "Regular blood test"),
    ],
    "Bronchial Asthma": [
        ("Salbutamol inhaler", "2 puff zaroorat pe", "Ongoing", "Dil tez dhad sakta", "Hamesha saath rakho"),
        ("Budesonide inhaler", "2 puff din mein 2 baar", "Ongoing", "Muh mein infection", "Kulla karo baad mein"),
    ],
    "Cervical spondylosis": [
        ("Diclofenac", "50mg din mein 2 baar", "2 hafta", "Pet kharab", "Khaane ke saath lo"),
        ("Physiotherapy", "Regular sessions", "1-3 months", "Koi nahi", "Ghar pe exercises karo"),
    ],
    "Chicken pox": [
        ("Acyclovir", "800mg din mein 5 baar", "7 din", "Nausea", "Khujli mat karo"),
        ("Calamine lotion", "Affected area pe lagao", "Jab tak daane hain", "Koi nahi", "Thanda paani se nahao"),
    ],
    "Chronic cholestasis": [
        ("Ursodeoxycholic acid", "13-15mg/kg/din", "Long term", "Diarrhea", "Regular liver test"),
        ("Cholestyramine", "4g din mein 2 baar", "Doctor ke mutabiq", "Constipation", "Khujli mein helpful"),
    ],
    "Common Cold": [
        ("Paracetamol", "500mg din mein 3 baar", "5 din", "Liver pe asar zyada se", "Khaane ke baad lo"),
        ("Cetirizine", "10mg raat ko", "5 din", "Neend aati hai", "Raat ko lo"),
        ("Vitamin C", "500mg din mein 1 baar", "7 din", "Koi khaas nahi", "Immunity badhata hai"),
    ],
    "Dengue": [
        ("Paracetamol", "500mg har 6 ghante", "Bukhaar tak", "Liver pe asar", "Aspirin BILKUL mat lo"),
        ("ORS", "2 sachet/din", "5-7 din", "Koi nahi", "Hydrated raho"),
    ],
    "Diabetes": [
        ("Metformin", "500mg din mein 2 baar", "Ongoing", "Nausea", "Khaane ke saath lo"),
        ("Insulin Glargine", "10 units raat ko", "Ongoing", "Low sugar", "Sugar daily check karo"),
        ("Glipizide", "5mg subah", "Ongoing", "Nausea", "Khali pet mat lo"),
    ],
    "Dimorphic hemmorhoids(piles)": [
        ("Sitz bath", "Din mein 2-3 baar", "1-2 hafta", "Koi nahi", "Garam paani mein 15 min"),
        ("Hydrocortisone cream", "Raat ko lagao", "1 hafta", "Mild irritation", "Doctor se confirm karo"),
    ],
    "Drug Reaction": [
        ("Antihistamine", "Doctor ke mutabiq", "Reaction khatam hone tak", "Neend", "Woh drug band karo"),
        ("Prednisolone", "Doctor ke mutabiq", "Short term", "Immunity kam", "Emergency mein use"),
    ],
    "Fungal infection": [
        ("Clotrimazole cream", "Din mein 2 baar lagao", "2-4 hafta", "Mild jalan", "Area saaf aur sukha rakho"),
        ("Fluconazole", "150mg ek baar", "Single dose", "Nausea", "Serious infection mein"),
    ],
    "GERD": [
        ("Omeprazole", "20mg subah khali pet", "4-8 hafta", "Headache", "Khaane se 30 min pehle"),
        ("Antacid", "Khaane ke baad", "Zaroorat pe", "Constipation", "Long term mat lo"),
    ],
    "Gastroenteritis": [
        ("ORS", "Har diarrhea ke baad", "Jab tak theek na ho", "Koi nahi", "Dehydration rokta hai"),
        ("Zinc tablet", "20mg din mein 1 baar", "10-14 din", "Nausea", "Bachon ke liye zaroori"),
    ],
    "Heart attack": [
        ("Aspirin", "325mg immediately", "Emergency", "Bleeding", "Seedha hospital jao"),
        ("Nitroglycerin", "Doctor ke mutabiq", "Emergency", "BP girna", "Doctor ki supervision mein"),
    ],
    "Hepatitis B": [
        ("Tenofovir", "300mg din mein 1 baar", "Long term", "Kidney pe asar", "Regular monitoring"),
        ("Entecavir", "0.5mg din mein 1 baar", "Long term", "Headache", "Khali pet lo"),
    ],
    "Hepatitis C": [
        ("Sofosbuvir", "400mg din mein 1 baar", "12 hafta", "Fatigue", "Cure possible hai"),
        ("Ribavirin", "Doctor ke mutabiq", "12-24 hafta", "Anemia", "Regular blood test"),
    ],
    "Hepatitis D": [
        ("Pegylated Interferon", "Doctor ke mutabiq", "48 hafta", "Flu symptoms", "Hepatitis B ke saath"),
        ("Supportive care", "Rest aur nutrition", "Ongoing", "Koi nahi", "Alcohol bilkul band"),
    ],
    "Hepatitis E": [
        ("Rest aur hydration", "Zyada paani", "4-6 hafta", "Koi nahi", "Aksar khud theek ho jaata"),
        ("Ribavirin", "Doctor ke mutabiq", "Severe cases mein", "Anemia", "Pregnant women mein dangerous"),
    ],
    "Hypertension": [
        ("Amlodipine", "5mg subah", "Ongoing", "Pair mein sujan", "Subah lo"),
        ("Losartan", "50mg subah", "Ongoing", "Chakkar", "Potassium avoid karo"),
        ("Atenolol", "25mg subah", "Ongoing", "Thakaan", "Achanak band mat karo"),
    ],
    "Hyperthyroidism": [
        ("Methimazole", "10-30mg/din", "6-18 months", "Rash", "Regular thyroid test"),
        ("Propranolol", "20-40mg din mein 3 baar", "Short term", "Thakaan", "Symptoms control karta hai"),
    ],
    "Hypoglycemia": [
        ("Glucose tablets", "15-20g sugar turant", "Emergency", "Koi nahi", "Hamesha saath rakho"),
        ("Glucagon injection", "Doctor ke mutabiq", "Emergency", "Nausea", "Severe cases mein"),
    ],
    "Hypothyroidism": [
        ("Levothyroxine", "Doctor ke mutabiq", "Lifelong", "Heart rate badh sakta", "Khali pet subah lo"),
    ],
    "Impetigo": [
        ("Mupirocin cream", "Din mein 3 baar", "7-10 din", "Mild irritation", "Haath saaf rakhna"),
        ("Amoxicillin", "500mg din mein 3 baar", "7 din", "Diarrhea", "Spreading rok ta hai"),
    ],
    "Jaundice": [
        ("Liver support supplements", "Doctor ke mutabiq", "4-8 hafta", "Koi khaas nahi", "Rest zaroori"),
        ("Ursodeoxycholic acid", "Doctor ke mutabiq", "Cause pe depend", "GI upset", "Cause pehle pata karo"),
    ],
    "Malaria": [
        ("Chloroquine", "500mg din mein 2 baar", "3 din", "Pet dard", "Poora course karo"),
        ("Primaquine", "15mg din mein 1 baar", "14 din", "Kamzori", "Relapse rokta hai"),
    ],
    "Migraine": [
        ("Sumatriptan", "50mg jab dard ho", "Zaroorat pe", "Chest tightness", "Max 2 baar/din"),
        ("Ibuprofen", "400mg din mein 3 baar", "3 din", "Pet mein jalan", "Khaane ke baad lo"),
        ("Topiramate", "25mg raat ko", "Long term", "Yaadaasht", "Prevention ke liye"),
    ],
    "Osteoarthristis": [
        ("Paracetamol", "500mg din mein 3 baar", "Zaroorat pe", "Liver pe asar", "First choice hai"),
        ("Diclofenac gel", "Affected area pe", "2-4 hafta", "Skin irritation", "Local application better"),
    ],
    "Paralysis (brain hemorrhage)": [
        ("Mannitol", "Doctor ke mutabiq", "Emergency", "Kidney pe asar", "ICU mein dete hain"),
        ("Physiotherapy", "Daily sessions", "Long term", "Koi nahi", "Jitna jaldi utna better"),
    ],
    "Peptic ulcer diseae": [
        ("Omeprazole", "20mg din mein 2 baar", "4-8 hafta", "Headache", "Khali pet lo"),
        ("Amoxicillin", "1g din mein 2 baar", "7-14 din", "Diarrhea", "H.pylori ke liye"),
        ("Clarithromycin", "500mg din mein 2 baar", "7-14 din", "Taste change", "Triple therapy"),
    ],
    "Pneumonia": [
        ("Amoxicillin", "500mg din mein 3 baar", "7-10 din", "Allergy", "Poora course lo"),
        ("Azithromycin", "500mg din mein 1 baar", "5 din", "Pet kharab", "Atypical ke liye"),
    ],
    "Psoriasis": [
        ("Betamethasone cream", "Din mein 2 baar", "2-4 hafta", "Skin thin ho sakti", "Long term mat lo"),
        ("Coal tar shampoo", "Hafte mein 2-3 baar", "Ongoing", "Strong smell", "Scalp ke liye"),
    ],
    "Tuberculosis": [
        ("Rifampicin", "600mg subah", "6 months", "Urine orange ho jaata", "Khali pet lo"),
        ("Isoniazid", "300mg subah", "6 months", "Liver pe asar", "Vitamin B6 saath lo"),
        ("Pyrazinamide", "Doctor ke mutabiq", "2 months", "Joint dard", "Poora course karo"),
    ],
    "Typhoid": [
        ("Azithromycin", "500mg din mein 1 baar", "7 din", "Diarrhea", "Khali pet lo"),
        ("Ceftriaxone", "1g injection", "7-14 din", "Injection dard", "Hospital mein lagwao"),
    ],
    "Urinary tract infection": [
        ("Nitrofurantoin", "100mg din mein 2 baar", "5-7 din", "Nausea", "Khaane ke saath lo"),
        ("Trimethoprim", "200mg din mein 2 baar", "7 din", "Rash", "Zyada paani peo"),
    ],
    "Varicose veins": [
        ("Compression stockings", "Subah se raat tak", "Ongoing", "Uncomfortable", "Pair utha ke rakho"),
        ("Diosmin", "500mg din mein 2 baar", "2-3 months", "GI upset", "Circulation improve karta"),
    ],
    "hepatitis A": [
        ("Rest aur hydration", "Zyada paani aur juice", "4-8 hafta", "Koi nahi", "Aksar khud theek hota"),
        ("Paracetamol", "500mg zaroorat pe", "Short term", "Liver pe dhyan", "Zyada mat lo"),
    ],
    "Anemia": [
        ("Ferrous Sulfate", "200mg din mein 2 baar", "3 months", "Constipation", "Vitamin C ke saath lo"),
        ("Folic Acid", "5mg din mein 1 baar", "3 months", "Koi khaas nahi", "Mahilaon ke liye zaroori"),
    ],
}

# ── DIET PLANS ────────────────────────────────
diet_plans = {
    "(vertigo) Paroymsal  Positional Vertigo": ("Ginger tea, bananas, water, vitamin D foods", "Alcohol, caffeine, salty foods", "Small frequent meals", "Head movements dhire karo"),
    "AIDS": ("High protein foods, fruits, vegetables, nuts", "Raw/undercooked food, alcohol", "Regular meals din mein 5-6 baar", "Immunity badhane wale foods lo"),
    "Acne": ("Fruits, vegetables, whole grains, water", "Dairy, sugar, fried foods, chocolate", "Din mein 3 baar balanced meals", "8+ glasses paani peo rozana"),
    "Alcoholic hepatitis": ("High protein, fruits, vegetables, low fat", "Alcohol completely, fatty foods", "Small frequent meals", "Alcohol bilkul band karo"),
    "Allergy": ("Fresh fruits, vegetables, omega-3 foods", "Known allergens, processed foods", "Regular meals", "Trigger foods diary mein likho"),
    "Arthritis": ("Fish, nuts, fruits, leafy greens, turmeric", "Red meat, fried foods, sugar, alcohol", "Anti-inflammatory diet follow karo", "Omega-3 rich foods zyada khao"),
    "Bronchial Asthma": ("Apples, ginger, turmeric, leafy greens", "Cold foods, sulfites, artificial colors", "Warm meals preferred", "Breathing exercises karo"),
    "Cervical spondylosis": ("Calcium rich foods, vitamin D, fish", "Fried foods, excess salt, alcohol", "Regular meals", "Posture dhyan rakho khaate waqt"),
    "Chicken pox": ("Soft foods, soups, fruits, lots of water", "Spicy food, salty food, oily food", "Light frequent meals", "Khujli wali jagah saaf rakho"),
    "Chronic cholestasis": ("Low fat diet, fruits, vegetables", "Fatty foods, alcohol, fried items", "Small frequent meals", "Fat soluble vitamins lo"),
    "Common Cold": ("Warm soup, ginger tea, citrus fruits, garlic", "Cold drinks, ice cream, fried food", "Baar baar warm cheezein lo", "8-10 glass warm paani peo"),
    "Dengue": ("Papaya leaf juice, coconut water, orange, kiwi", "Spicy food, oily food, alcohol", "Baar baar liquid lo", "Platelet badhane wale foods lo"),
    "Diabetes": ("Whole grains, leafy vegetables, fish, nuts", "Sugar, white bread, sweets, cold drinks", "Har 3-4 ghante mein thoda thoda", "Portion size control karo"),
    "Dimorphic hemmorhoids(piles)": ("High fiber foods, fruits, vegetables, water", "Spicy food, alcohol, processed food", "Regular meals, zyada fiber", "8+ glasses paani peo"),
    "Drug Reaction": ("Light easily digestible foods, water", "Suspected allergen foods", "Small frequent meals", "Doctor ko sari medicines batao"),
    "Fungal infection": ("Probiotics, garlic, coconut oil, vegetables", "Sugar, refined carbs, alcohol, yeast", "Balanced meals", "Area dry aur saaf rakho"),
    "GERD": ("Oatmeal, ginger, bananas, lean meats", "Spicy food, citrus, tomatoes, coffee", "Small frequent meals, raat ko kam khao", "Khaane ke baad 2-3 ghante let mat jao"),
    "Gastroenteritis": ("ORS, bananas, rice, toast, boiled potatoes", "Dairy, spicy food, fatty food, alcohol", "BRAT diet follow karo", "Dehydration se bacho"),
    "Heart attack": ("Low fat, fruits, vegetables, whole grains, fish", "Saturated fats, salt, processed foods", "Small portions din mein 5-6 baar", "Mediterranean diet follow karo"),
    "Hepatitis B": ("High protein, fruits, vegetables, whole grains", "Alcohol completely, fatty foods, raw seafood", "Regular balanced meals", "Liver friendly foods khao"),
    "Hepatitis C": ("Fruits, vegetables, lean protein, whole grains", "Alcohol completely, iron rich foods excess", "Regular meals", "Healthy weight maintain karo"),
    "Hepatitis D": ("Fruits, vegetables, high protein, low fat", "Alcohol completely, fatty foods", "Regular balanced meals", "Hepatitis B ke saath manage karo"),
    "Hepatitis E": ("Light easily digestible foods, lots of water", "Alcohol, fatty foods, raw food", "Small frequent meals", "Hygiene maintain karo"),
    "Hypertension": ("Banana, oats, leafy greens, low fat dairy", "Namak, processed food, alcohol, caffeine", "Din mein 4-5 baar thoda khao", "DASH diet follow karo"),
    "Hyperthyroidism": ("Calcium rich foods, cruciferous vegetables", "Iodine rich foods, caffeine, alcohol", "Regular balanced meals", "Weight maintain karo"),
    "Hypoglycemia": ("Complex carbs, protein, frequent meals", "Simple sugars alone, alcohol on empty stomach", "Har 3 ghante kuch khao", "Sugar snacks hamesha saath rakho"),
    "Hypothyroidism": ("Iodine rich foods, selenium foods, fruits", "Soy products, cruciferous veggies excess", "Regular meals", "Levothyroxine khali pet lo"),
    "Impetigo": ("Vitamin C rich foods, protein, vegetables", "Sugary foods, processed foods", "Balanced meals", "Haath dhona zaroori"),
    "Jaundice": ("Fruits, vegetables, rice, dal, boiled food", "Alcohol, fatty foods, spicy food, raw food", "Light frequent meals", "Boiled paani peo"),
    "Malaria": ("Chawal, kela, ubli sabziyan, coconut water", "Spicy food, oily food, alcohol", "Din mein 5-6 baar halka khana", "Zyada se zyada fluids lo"),
    "Migraine": ("Ginger, cherries, almonds, salmon, water", "Alcohol, caffeine, aged cheese, MSG", "Regular time pe khao, skip mat karo", "Food diary rakho triggers pehchano"),
    "Osteoarthristis": ("Calcium, vitamin D, fish oil, turmeric", "Nightshade vegetables, sugar, alcohol", "Anti-inflammatory diet", "Weight control karo joints ke liye"),
    "Paralysis (brain hemorrhage)": ("Soft foods, high protein, fruits, vegetables", "Hard foods, alcohol, excess salt", "Small frequent meals, soft texture", "Swallowing difficulty ho to doctor batao"),
    "Peptic ulcer diseae": ("Probiotics, fruits, vegetables, lean protein", "Spicy food, alcohol, caffeine, citrus", "Small frequent meals", "Stress management karo"),
    "Pneumonia": ("Warm soup, honey, turmeric milk, protein", "Cold drinks, alcohol, sugary foods", "Din mein 5-6 baar garam khana", "Zyada se zyada liquids lo"),
    "Psoriasis": ("Fish, fruits, vegetables, olive oil", "Red meat, dairy, alcohol, processed foods", "Anti-inflammatory diet", "Healthy weight maintain karo"),
    "Tuberculosis": ("High calorie, high protein, fruits, vegetables", "Alcohol, tobacco, raw foods", "Regular balanced meals", "Weight gain important hai"),
    "Typhoid": ("Ubla chawal, dal, ubla aloo, kela, dahi", "Kacha khaana, mirch masala, high-fiber food", "Baar baar thoda thoda khao", "Sirf saaf aur fresh khana khao"),
    "Urinary tract infection": ("Water, cranberry juice, probiotics, vitamin C", "Caffeine, alcohol, spicy food, sugar", "Zyada se zyada paani peo", "8-10 glasses paani rozana"),
    "Varicose veins": ("High fiber, fruits, vegetables, flavonoids", "Excess salt, processed foods, alcohol", "Regular balanced meals", "Pair utha ke rakho jab ho sake"),
    "hepatitis A": ("Light easily digestible foods, fruits, water", "Alcohol, fatty foods, raw seafood", "Small frequent meals", "Hygiene bahut zaroori hai"),
}

# ── WORKOUT PLANS ─────────────────────────────
workout_plans = {
    "(vertigo) Paroymsal  Positional Vertigo": ("Brandt-Daroff exercises, gentle walking", "Sudden head movements, intense exercise", 15, "Din mein 2 baar", "Slowly karo, support rakho"),
    "AIDS": ("Light walking, yoga, swimming, stretching", "High intensity during illness", 20, "4-5 din/hafta", "CD4 count ke hisaab se adjust karo"),
    "Acne": ("Regular exercise, outdoor activities", "Sweaty equipment directly face pe", 30, "4-5 din/hafta", "Exercise ke baad face wash karo"),
    "Alcoholic hepatitis": ("Complete rest during acute phase", "All exercise during acute phase", 0, "Recovery ke baad dhire dhire", "Doctor ki permission ke baad"),
    "Allergy": ("Indoor exercises, swimming in clean pool", "Outdoor exercise during high pollen", 30, "4-5 din/hafta", "Antihistamine pehle lo"),
    "Arthritis": ("Swimming, water aerobics, gentle yoga, walking", "High impact exercises, heavy lifting", 20, "4-5 din/hafta", "Warm up zaroori hai"),
    "Bronchial Asthma": ("Swimming, walking, yoga", "Cold air mein exercise, high pollen area", 20, "4 din/hafta", "Inhaler hamesha saath rakho"),
    "Cervical spondylosis": ("Neck stretches, shoulder rolls, walking", "Heavy lifting, contact sports", 20, "Din mein 2 baar", "Posture correct rakho"),
    "Chicken pox": ("Complete rest jab tak daane hain", "Koi bhi exercise active phase mein", 0, "Recovery ke baad", "School/office mat jao"),
    "Chronic cholestasis": ("Light walking, gentle yoga", "Strenuous exercise", 15, "3-4 din/hafta", "Thakaan feel ho to rok lo"),
    "Common Cold": ("Light stretching, gentle yoga", "Gym, running, swimming", 15, "Sirf theek lage tab", "Bukhaar mein bilkul mat karo"),
    "Dengue": ("Complete bed rest", "Koi bhi exercise bimari mein", 0, "Recovery ke baad only", "Platelet normal hone ke baad"),
    "Diabetes": ("Walking, cycling, swimming, yoga", "Khali pet exercise", 30, "5 din/hafta", "Sugar check karo exercise ke baad"),
    "Dimorphic hemmorhoids(piles)": ("Walking, swimming, yoga", "Heavy lifting, cycling", 20, "4-5 din/hafta", "Straining avoid karo"),
    "Drug Reaction": ("Rest during reaction", "All exercise during reaction", 0, "Doctor ki permission ke baad", "Reaction khatam hone ka wait karo"),
    "Fungal infection": ("Regular exercise ok hai", "Wet clothes mein raho mat", 30, "4-5 din/hafta", "Dry clothes pehno exercise ke baad"),
    "GERD": ("Walking, gentle yoga, cycling", "High impact, lying down after eating", 20, "4-5 din/hafta", "Khaane ke 2 ghante baad exercise karo"),
    "Gastroenteritis": ("Complete rest during illness", "All exercise during illness", 0, "Recovery ke baad", "Hydration pehle restore karo"),
    "Heart attack": ("Cardiac rehab program, gentle walking", "Strenuous exercise without clearance", 20, "Doctor ke mutabiq", "Cardiac rehab join karo"),
    "Hepatitis B": ("Light walking, gentle yoga", "Strenuous exercise", 20, "3-4 din/hafta", "Thakaan ho to rok lo"),
    "Hepatitis C": ("Light to moderate exercise, walking, yoga", "Heavy exercise during treatment", 20, "3-4 din/hafta", "Treatment ke dauraan dhyan rakho"),
    "Hepatitis D": ("Light walking, rest preferred", "Strenuous exercise", 15, "3 din/hafta", "Liver pe stress mat dalo"),
    "Hepatitis E": ("Rest during illness", "All exercise during illness", 0, "Recovery ke baad", "4-6 hafta rest karo"),
    "Hypertension": ("Brisk walking, swimming, cycling, yoga", "Heavy lifting, intense sprinting", 30, "5 din/hafta", "BP check karo pehle"),
    "Hyperthyroidism": ("Light to moderate exercise, yoga, walking", "High intensity cardio", 20, "3-4 din/hafta", "Heart rate monitor karo"),
    "Hypoglycemia": ("Regular moderate exercise", "Exercise on empty stomach", 20, "4-5 din/hafta", "Snack lo pehle"),
    "Hypothyroidism": ("Regular aerobic exercise, walking, swimming", "Overexertion", 30, "4-5 din/hafta", "Dhire dhire intensity badhao"),
    "Impetigo": ("Rest during active infection", "Contact sports, swimming", 0, "Infection khatam hone ke baad", "Dusron ko infection mat phailao"),
    "Jaundice": ("Complete rest during illness", "All strenuous exercise", 0, "Recovery ke baad dhire dhire", "Liver ko rest chahiye"),
    "Malaria": ("Complete rest during fever", "Koi bhi exercise bukhaar mein", 10, "Recovery ke baad dhire dhire", "Jab tak doctor na kahe mat karo"),
    "Migraine": ("Gentle yoga, walking, swimming", "High intensity workout", 20, "3-4 din/hafta", "Trigger avoid karo"),
    "Osteoarthristis": ("Swimming, water aerobics, cycling, yoga", "High impact exercise, running", 20, "4-5 din/hafta", "Joint friendly exercises karo"),
    "Paralysis (brain hemorrhage)": ("Physiotherapy exercises, passive movements", "Any exercise without supervision", 30, "Daily supervised", "Specialist ki guidance zaroori"),
    "Peptic ulcer diseae": ("Light walking, yoga, stress reduction", "Heavy lifting, high stress exercise", 20, "4-5 din/hafta", "Stress management important"),
    "Pneumonia": ("Deep breathing, gentle walk recovery mein", "Strenuous exercise during illness", 10, "Recovery ke baad", "Breathing exercises lungs ke liye"),
    "Psoriasis": ("Swimming, walking, yoga, cycling", "Activities jo skin irritate karein", 30, "4-5 din/hafta", "Sunscreen lagao outdoor exercise mein"),
    "Tuberculosis": ("Light walking, breathing exercises", "Strenuous exercise during treatment", 15, "Dhire dhire badhao", "Treatment poora karo pehle"),
    "Typhoid": ("Bed rest, gentle walk after recovery", "Koi bhi strenuous exercise", 10, "Recovery ke baad slowly", "Poori tarah theek hone ke baad"),
    "Urinary tract infection": ("Light walking, yoga", "Swimming during infection", 20, "4-5 din/hafta", "Zyada paani peo exercise ke baad"),
    "Varicose veins": ("Walking, swimming, cycling, leg exercises", "Standing/sitting for long periods", 30, "5 din/hafta", "Compression stockings pehno"),
    "hepatitis A": ("Rest during illness", "All exercise during illness", 0, "Recovery ke baad", "4-8 hafta lagta hai"),
}

# ── INSERT MEDICINES ──────────────────────────
print("\n💊 Medicines insert ho rahi hain...")
for disease, meds in medicines.items():
    did = get_did(disease)
    if did:
        for m in meds:
            cur.execute("""
                INSERT INTO medicines
                (disease_id, medicine_name, dosage, duration, side_effects, notes)
                VALUES (?,?,?,?,?,?)
            """, (did,) + m)
print("✅ Medicines done!")

# ── INSERT DIET PLANS ─────────────────────────
print("🥗 Diet plans insert ho rahe hain...")
for disease, (eat, avoid, timing, tips) in diet_plans.items():
    did = get_did(disease)
    if did:
        cur.execute("""
            INSERT INTO diet_plans
            (disease_id, eat_foods, avoid_foods, meal_timing, diet_tips)
            VALUES (?,?,?,?,?)
        """, (did, eat, avoid, timing, tips))
print("✅ Diet plans done!")

# ── INSERT WORKOUT PLANS ──────────────────────
print("🏃 Workout plans insert ho rahe hain...")
for disease, (ex, avoid_ex, dur, freq, notes) in workout_plans.items():
    did = get_did(disease)
    if did:
        cur.execute("""
            INSERT INTO workout_plans
            (disease_id, exercises, avoid_exercises, duration_mins, frequency, special_notes)
            VALUES (?,?,?,?,?,?)
        """, (did, ex, avoid_ex, dur, freq, notes))
print("✅ Workout plans done!")

conn.commit()
conn.close()

print(f"\n{'='*55}")
print("🎉 SAARA DATA SUCCESSFULLY INSERT HO GAYA!")
print(f"   ✅ 41 Diseases ke liye Medicines")
print(f"   ✅ 41 Diseases ke liye Diet Plans")
print(f"   ✅ 41 Diseases ke liye Workout Plans")
print(f"{'='*55}\n")