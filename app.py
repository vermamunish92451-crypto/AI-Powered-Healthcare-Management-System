import streamlit as st
import sqlite3
import pickle
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from fpdf import FPDF
import hashlib
import datetime
import time

# ── Page Config ──────────────────────────────
st.set_page_config(
    page_title="Healthcare Management System",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Session State Init ───────────────────────
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_email' not in st.session_state:
    st.session_state.user_email = ""
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

# ── Hash Password ────────────────────────────
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ── Database Path ────────────────────────────
DB_PATH = "database/healthcare.db"

# ── Dark Mode CSS ────────────────────────────
dark_mode_css = """
<style>
body, .stApp {
    background-color: #0e1117;
    color: #fafafa;
}
.sidebar .sidebar-content {
    background-color: #1a1a2e;
}
</style>
"""

light_mode_css = """
<style>
body, .stApp {
    background-color: #ffffff;
    color: #000000;
}
</style>
"""

if st.session_state.dark_mode:
    st.markdown(dark_mode_css, unsafe_allow_html=True)
else:
    st.markdown(light_mode_css, unsafe_allow_html=True)

# ── CSS + Animations ─────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap');

* { font-family: 'Poppins', sans-serif; }

.main-title {
    text-align: center;
    color: white;
    font-size: 42px;
    font-weight: 700;
    padding: 30px;
    background: linear-gradient(135deg, #1a237e, #1565C0, #0288d1);
    background-size: 200% 200%;
    animation: gradientShift 4s ease infinite;
    border-radius: 20px;
    margin-bottom: 10px;
    box-shadow: 0 8px 32px rgba(21,101,192,0.3);
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

.chatbot-container {
    background: linear-gradient(135deg, #1a237e, #0288d1);
    border-radius: 20px;
    padding: 20px;
    margin: 10px 0;
}

.chat-message {
    background: rgba(255,255,255,0.1);
    border-radius: 12px;
    padding: 12px 16px;
    margin: 8px 0;
    color: white;
}

.user-message {
    background: rgba(100,255,218,0.2);
    border-left: 4px solid #64FFDA;
}

.bot-message {
    background: rgba(255,255,255,0.1);
    border-left: 4px solid #40C4FF;
}

.login-box {
    background: linear-gradient(135deg, #1a237e, #1565C0);
    border-radius: 20px;
    padding: 40px;
    text-align: center;
    color: white;
    max-width: 400px;
    margin: 0 auto;
}

.social-links {
    text-align: center;
    padding: 20px;
    background: linear-gradient(135deg, #1a237e, #0288d1);
    border-radius: 12px;
    margin-top: 20px;
}

.social-links a {
    color: white;
    margin: 0 15px;
    text-decoration: none;
    font-size: 14px;
}

.social-links a:hover {
    color: #64FFDA;
}

.footer {
    text-align: center;
    padding: 15px;
    color: #666;
    font-size: 12px;
    border-top: 1px solid #eee;
    margin-top: 30px;
}
</style>
""", unsafe_allow_html=True)

DB_PATH    = "database/healthcare.db"
MODEL_PATH = "model/healthcare_model.pkl"

# ── Helper Functions ─────────────────────────
@st.cache_resource
def load_model():
    with open(MODEL_PATH, 'rb') as f:
        data = pickle.load(f)
    return data['model'], data['symptoms'], data['accuracy']

@st.cache_data
def get_symptoms():
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql(
        "SELECT symptom_name FROM symptoms ORDER BY symptom_name", conn)
    conn.close()
    return df['symptom_name'].tolist()

@st.cache_data
def get_diseases():
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql(
        "SELECT disease_name FROM diseases ORDER BY disease_name", conn)
    conn.close()
    return df['disease_name'].tolist()

def get_recommendations(disease_name):
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute(
        "SELECT disease_id, description, severity, category FROM diseases WHERE disease_name=?",
        (disease_name,))
    info = cur.fetchone()
    if not info:
        conn.close()
        return None
    did, desc, severity, category = info
    cur.execute(
        "SELECT medicine_name, dosage, duration, side_effects, notes FROM medicines WHERE disease_id=?",
        (did,))
    medicines = cur.fetchall()
    cur.execute(
        "SELECT eat_foods, avoid_foods, meal_timing, diet_tips FROM diet_plans WHERE disease_id=?",
        (did,))
    diet = cur.fetchone()
    cur.execute(
        "SELECT exercises, avoid_exercises, duration_mins, frequency, special_notes FROM workout_plans WHERE disease_id=?",
        (did,))
    workout = cur.fetchone()
    conn.close()
    return {
        'disease'    : disease_name,
        'description': desc,
        'severity'   : severity,
        'category'   : category,
        'medicines'  : medicines,
        'diet'       : diet,
        'workout'    : workout
    }

def predict(model, symptom_list, selected):
    vec     = [1 if s in selected else 0 for s in symptom_list]
    vec     = np.array(vec).reshape(1, -1)
    proba   = model.predict_proba(vec)[0]
    classes = model.classes_
    top3    = [(classes[i], round(proba[i]*100, 1))
                for i in np.argsort(proba)[::-1][:3]]
    return classes[np.argmax(proba)], proba[np.argmax(proba)], top3

def log_pred(symptoms, disease, confidence):
    conn = sqlite3.connect(DB_PATH)
    cur  = conn.cursor()
    cur.execute("""
        INSERT INTO predictions
        (patient_id, symptoms_entered, predicted_disease, confidence_pct)
        VALUES (?,?,?,?)
    """, (1, ", ".join(symptoms), disease, round(confidence*100, 2)))
    conn.commit()
    conn.close()

def sev_icon(s):
    return {'Mild':'🟢','Moderate':'🟡','Severe':'🔴'}.get(s,'⚪')

# ── PDF Generation Function ──────────────────
def generate_pdf(disease, confidence, rec, symptoms):
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font('Arial', 'B', 24)
    pdf.cell(0, 20, 'Healthcare Management System', 0, 1, 'C')
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, 'Health Report', 0, 1, 'C')
    pdf.ln(10)
    
    # Date
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f'Generated on: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}', 0, 1, 'R')
    pdf.ln(5)
    
    # Patient Symptoms
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Symptoms:', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 8, ', '.join(symptoms))
    pdf.ln(5)
    
    # Predicted Disease
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Predicted Disease:', 0, 1)
    pdf.set_font('Arial', 'B', 16)
    pdf.set_text_color(21, 101, 192)
    pdf.cell(0, 12, f'{disease.upper()}', 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f'Confidence: {confidence*100:.1f}%', 0, 1)
    pdf.cell(0, 8, f'Severity: {rec["severity"]}', 0, 1)
    pdf.cell(0, 8, f'Category: {rec["category"]}', 0, 1)
    pdf.ln(5)
    
    # Description
    pdf.set_font('Arial', 'B', 14)
    pdf.cell(0, 10, 'Description:', 0, 1)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 8, rec['description'])
    pdf.ln(5)
    
    # Medicines
    if rec['medicines']:
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Prescribed Medicines:', 0, 1)
        pdf.set_font('Arial', '', 11)
        for i, med in enumerate(rec['medicines'], 1):
            pdf.cell(0, 8, f'{i}. {med[0]} - {med[1]} (Duration: {med[2]})', 0, 1)
        pdf.ln(5)
    
    # Diet Plan
    if rec['diet']:
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Diet Plan:', 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, f'Eat: {rec["diet"][0]}', 0, 1)
        pdf.cell(0, 8, f'Avoid: {rec["diet"][1]}', 0, 1)
        pdf.cell(0, 8, f'Timing: {rec["diet"][2]}', 0, 1)
        pdf.ln(5)
    
    # Workout
    if rec['workout']:
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Workout Plan:', 0, 1)
        pdf.set_font('Arial', '', 11)
        pdf.cell(0, 8, f'Exercises: {rec["workout"][0]}', 0, 1)
        pdf.cell(0, 8, f'Duration: {rec["workout"][2]} mins', 0, 1)
        pdf.cell(0, 8, f'Frequency: {rec["workout"][3]}', 0, 1)
        pdf.ln(5)
    
    # Disclaimer
    pdf.set_font('Arial', 'I', 9)
    pdf.set_text_color(150, 0, 0)
    pdf.multi_cell(0, 6, 'Disclaimer: This is an AI-based prediction. Please consult a qualified doctor for actual diagnosis and treatment.')
    
    return pdf.output(dest='S').encode('latin-1')

# ── Chatbot Response Function ────────────────
def chatbot_response(user_input):
    user_input = user_input.lower()
    
    # Health tips
    tips = {
        "fever": "For fever: Rest well, drink plenty of fluids, and take paracetamol if needed. If fever persists for more than 3 days, consult a doctor.",
        "headache": "For headache: Stay hydrated, rest in a dark room, and apply cold compress. Avoid screen time.",
        "cold": "For cold: Drink warm liquids, take steam inhalation, and get plenty of rest. Vitamin C rich foods help.",
        "cough": "For cough: Honey with warm water helps. Avoid cold drinks. If cough persists for more than a week, see a doctor.",
        "diabetes": "For diabetes: Monitor blood sugar regularly, follow a low-sugar diet, exercise daily, and take medications on time.",
        "bp": "For blood pressure: Reduce salt intake, exercise regularly, manage stress, and take prescribed medications.",
        "diet": "A balanced diet includes: Fruits, vegetables, whole grains, lean proteins, and healthy fats. Drink 8 glasses of water daily.",
        "exercise": "Recommended: 30 minutes of moderate exercise 5 days a week. Walking, swimming, or cycling are great options.",
        "sleep": "Adults need 7-9 hours of sleep. Maintain a regular sleep schedule, avoid screens before bed, and keep room dark.",
        "stress": "Manage stress: Practice deep breathing, meditation, yoga, or spend time in nature. Talk to someone you trust.",
        "hello": "Hello! I'm your health assistant. How can I help you today? You can ask about symptoms, diseases, diet, or exercise.",
        "hi": "Hi there! I'm here to help with your health questions. What would you like to know?",
        "help": "I can help you with:\n- Symptom information\n- Disease details\n- Diet recommendations\n- Exercise tips\n- General health advice\n\nWhat would you like to know?",
        "thank": "You're welcome! Take care of your health. Remember to consult a doctor for serious concerns.",
        "bye": "Goodbye! Stay healthy and take care!"
    }
    
    # Check for keywords
    for key, response in tips.items():
        if key in user_input:
            return response
    
    # Default response
    return "I'm a health assistant. You can ask me about:\n- Symptoms (fever, headache, cold)\n- Diseases (diabetes, bp)\n- Diet and exercise tips\n- General health advice\n\nWhat would you like to know?"

# ── Create Users Table ───────────────────────
def create_users_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()

create_users_table()

# ── Register User ────────────────────────────
def register_user(name, email, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hash_password(password))
        )
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except sqlite3.IntegrityError:
        conn.close()
        return False, "Email already registered!"

# ── Login User ───────────────────────────────
def login_user(email, password):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT name, email FROM users WHERE email=? AND password=?",
        (email, hash_password(password))
    )
    user = cur.fetchone()
    conn.close()
    if user:
        return True, user[0], user[1]
    return False, None, None

model, symptom_list, acc = load_model()

# ── Sidebar ──────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding:15px;
                background:linear-gradient(135deg,#1a237e,#1565C0);
                border-radius:15px; color:white;
                font-size:22px; font-weight:700;'>
        🏥 Healthcare Management System
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    
    # Dark Mode Toggle
    st.session_state.dark_mode = st.toggle("🌙 Dark Mode", value=st.session_state.dark_mode)
    
    page = st.radio("📌 Navigation", [
        "🏠 Home",
        "🤖 Health Chatbot",
        "👤 Patient Registration",
        "🔍 Symptom Checker",
        "⚖️ BMI Calculator",
        "🆚 Disease Comparison",
        "🌡️ Symptom Severity",
        "📊 Analytics",
        "💊 Medicines",
        "🥗 Diet Plans",
        "🏃 Workout Plans",
        "📋 History"
    ])
    st.markdown("---")
    st.markdown(f"""
    <div class='sidebar-info'>✅ Model Ready</div>
    <div class='sidebar-info'>🎯 Accuracy: {acc*100:.1f}%</div>
    <div class='sidebar-info'>🏥 Diseases: 41</div>
    <div class='sidebar-info'>🔬 Symptoms: 130+</div>
    <div class='sidebar-info'>💊 Medicines: 25+</div>
    """, unsafe_allow_html=True)
    COLORS = ['#2196F3','#4CAF50','#FF5722','#9C27B0',
          '#00BCD4','#FFC107','#E91E63','#3F51B5',
          '#8BC34A','#FF9800']

# ══════════════════════════
# PAGE 1 — HOME
# ══════════════════════════
if page == "🏠 Home":
    # ── Animated Hero Section ──────────────────
    st.markdown("""
    <style>
    @keyframes float {
        0%   { transform: translateY(0px); }
        50%  { transform: translateY(-10px); }
        100% { transform: translateY(0px); }
    }
    @keyframes glow {
        0%   { box-shadow: 0 0 20px rgba(33,150,243,0.3); }
        50%  { box-shadow: 0 0 60px rgba(33,150,243,0.8); }
        100% { box-shadow: 0 0 20px rgba(33,150,243,0.3); }
    }
    @keyframes rotate3d {
        0%   { transform: perspective(1000px) rotateY(0deg); }
        100% { transform: perspective(1000px) rotateY(360deg); }
    }
    @keyframes shimmer {
        0%   { background-position: -1000px 0; }
        100% { background-position: 1000px 0; }
    }
    @keyframes countUp {
        from { opacity: 0; transform: translateY(30px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    .hero-container {
        background: linear-gradient(135deg, #0a0a2e 0%, #0d1b4b 30%,
                    #1a237e 60%, #0288d1 100%);
        border-radius: 25px;
        padding: 0;
        margin-bottom: 25px;
        overflow: hidden;
        position: relative;
    }
    .hero-canvas-wrap {
        width: 100%;
        border-radius: 25px;
        overflow: hidden;
    }
    .stat-3d {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 25px 15px;
        text-align: center;
        animation: float 3s ease-in-out infinite, glow 3s ease-in-out infinite;
        transition: transform 0.3s ease;
        margin: 5px;
    }
    .stat-3d:hover {
        transform: translateY(-15px) scale(1.05);
        background: rgba(33,150,243,0.2);
    }
    .stat-num-3d {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(135deg, #64FFDA, #40C4FF, #E040FB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: countUp 1s ease;
    }
    .stat-lbl-3d {
        color: rgba(255,255,255,0.8);
        font-size: 14px;
        margin-top: 8px;
        font-weight: 500;
    }
    .feature-3d {
        background: linear-gradient(145deg, #1a1a3e, #0d2060);
        border: 1px solid rgba(100,255,218,0.2);
        border-radius: 20px;
        padding: 30px 20px;
        text-align: center;
        transition: all 0.4s ease;
        animation: float 4s ease-in-out infinite;
        cursor: pointer;
        position: relative;
        overflow: hidden;
    }
    .feature-3d::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent,
                    rgba(100,255,218,0.05), transparent);
        animation: shimmer 3s infinite;
    }
    .feature-3d:hover {
        transform: translateY(-12px) rotateX(5deg);
        border-color: rgba(100,255,218,0.6);
        box-shadow: 0 20px 60px rgba(100,255,218,0.2);
    }
    .feature-icon-3d {
        font-size: 52px;
        margin-bottom: 15px;
        display: block;
        animation: float 2s ease-in-out infinite;
    }
    .feature-title-3d {
        color: #64FFDA;
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 12px;
    }
    .feature-text-3d {
        color: rgba(255,255,255,0.7);
        font-size: 13px;
        line-height: 1.8;
    }
    .section-header {
        text-align: center;
        padding: 15px;
        margin: 20px 0;
        background: linear-gradient(135deg, #1a237e, #0288d1);
        border-radius: 12px;
        color: white;
        font-size: 22px;
        font-weight: 700;
    }
    .disease-row {
        background: linear-gradient(145deg, #0d1b4b, #1a237e);
        border: 1px solid rgba(100,255,218,0.15);
        border-radius: 12px;
        padding: 12px 20px;
        margin: 6px 0;
        color: white;
        transition: all 0.3s ease;
    }
    .disease-row:hover {
        border-color: #64FFDA;
        transform: translateX(8px);
        background: linear-gradient(145deg, #1a237e, #0288d1);
    }
    .shimmer-btn {
        background: linear-gradient(135deg, #1565C0, #0288d1, #64FFDA);
        background-size: 200% 200%;
        animation: gradientShift 3s ease infinite;
        color: white !important;
        border: none;
        border-radius: 50px;
        padding: 15px 50px;
        font-size: 18px;
        font-weight: 700;
        cursor: pointer;
        width: 100%;
        transition: transform 0.3s ease;
    }
    </style>

    <!-- Hero Canvas -->
    <div class='hero-container'>
        <canvas id='heroCanvas' width='1200' height='280'
                style='width:100%; display:block;'></canvas>
    </div>

    <script>
    (function() {
        const canvas = document.getElementById('heroCanvas');
        if (!canvas) return;
        const ctx = canvas.getContext('2d');
        let t = 0;

        // Particles
        const particles = Array.from({length: 80}, () => ({
            x: Math.random() * 1200,
            y: Math.random() * 280,
            r: Math.random() * 2.5 + 0.5,
            sx: (Math.random() - 0.5) * 0.8,
            sy: (Math.random() - 0.5) * 0.8,
            c: `hsl(${Math.floor(Math.random()*60+190)},100%,${Math.floor(Math.random()*30+60)}%)`
        }));

        // Stars
        const stars = Array.from({length: 60}, () => ({
            x: Math.random() * 1200,
            y: Math.random() * 280,
            r: Math.random() * 1.5,
            twinkle: Math.random() * Math.PI * 2
        }));

        function draw() {
            // Background
            const bg = ctx.createLinearGradient(0, 0, 1200, 280);
            bg.addColorStop(0, '#0a0a2e');
            bg.addColorStop(0.4, '#0d1b4b');
            bg.addColorStop(0.7, '#1a237e');
            bg.addColorStop(1, '#01579b');
            ctx.fillStyle = bg;
            ctx.fillRect(0, 0, 1200, 280);

            // Stars
            stars.forEach(s => {
                s.twinkle += 0.05;
                const alpha = 0.4 + Math.sin(s.twinkle) * 0.4;
                ctx.beginPath();
                ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(255,255,255,${alpha})`;
                ctx.fill();
            });

            // Grid Lines
            ctx.strokeStyle = 'rgba(100,255,218,0.05)';
            ctx.lineWidth = 1;
            for (let x = 0; x < 1200; x += 60) {
                ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, 280); ctx.stroke();
            }
            for (let y = 0; y < 280; y += 60) {
                ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(1200, y); ctx.stroke();
            }

            // Particles
            particles.forEach(p => {
                p.x += p.sx; p.y += p.sy;
                if (p.x < 0 || p.x > 1200) p.sx *= -1;
                if (p.y < 0 || p.y > 280)  p.sy *= -1;
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = p.c;
                ctx.shadowBlur = 8;
                ctx.shadowColor = p.c;
                ctx.fill();
                ctx.shadowBlur = 0;
            });

            // ECG Line
            ctx.beginPath();
            ctx.strokeStyle = '#00E5FF';
            ctx.lineWidth = 2.5;
            ctx.shadowBlur = 20;
            ctx.shadowColor = '#00E5FF';
            ctx.moveTo(0, 160);
            for (let x = 0; x <= 900; x += 4) {
                let y = 160;
                const seg = ((x + t * 80) % 200);
                if      (seg < 60)  y = 160;
                else if (seg < 70)  y = 160 - 70 * Math.sin((seg-60)/10*Math.PI);
                else if (seg < 80)  y = 160 + 35 * Math.sin((seg-70)/10*Math.PI);
                else if (seg < 100) y = 160 - 110 * Math.sin((seg-80)/20*Math.PI);
                else if (seg < 120) y = 160 + 25 * Math.sin((seg-100)/20*Math.PI);
                else                y = 160;
                ctx.lineTo(x, y);
            }
            ctx.stroke();
            ctx.shadowBlur = 0;

            // DNA Helix (right side)
            for (let i = 0; i < 22; i++) {
                const x1 = 970 + Math.sin(i * 0.45 + t * 1.5) * 35;
                const y1 = i * 13;
                const x2 = 1020 + Math.cos(i * 0.45 + t * 1.5) * 35;
                const y2 = i * 13;

                ctx.beginPath();
                ctx.arc(x1, y1, 4, 0, Math.PI * 2);
                ctx.fillStyle = '#64FFDA';
                ctx.shadowBlur = 10; ctx.shadowColor = '#64FFDA';
                ctx.fill(); ctx.shadowBlur = 0;

                ctx.beginPath();
                ctx.arc(x2, y2, 4, 0, Math.PI * 2);
                ctx.fillStyle = '#E040FB';
                ctx.shadowBlur = 10; ctx.shadowColor = '#E040FB';
                ctx.fill(); ctx.shadowBlur = 0;

                if (i % 2 === 0) {
                    ctx.beginPath();
                    ctx.moveTo(x1, y1); ctx.lineTo(x2, y2);
                    ctx.strokeStyle = 'rgba(255,255,255,0.25)';
                    ctx.lineWidth = 1.5; ctx.stroke();
                }
            }

            // 3D Rotating Circles
            for (let i = 0; i < 4; i++) {
                const cx = 1100, cy = 140;
                const rx = 55 * Math.cos(t * 0.8 + i * Math.PI / 2);
                const ry = 30;
                ctx.beginPath();
                ctx.ellipse(cx, cy, Math.abs(rx), ry, 0, 0, Math.PI * 2);
                ctx.strokeStyle = `hsla(${i*90+180},100%,70%,0.4)`;
                ctx.lineWidth = 1.5; ctx.stroke();
            }

            // Title Text
            ctx.font = 'bold 38px Arial';
            const grad = ctx.createLinearGradient(50, 0, 600, 0);
            grad.addColorStop(0, '#64FFDA');
            grad.addColorStop(0.5, '#40C4FF');
            grad.addColorStop(1, '#E040FB');
            ctx.fillStyle = grad;
            ctx.shadowBlur = 20; ctx.shadowColor = '#40C4FF';
            ctx.fillText('🏥 Healthcare Management System', 50, 100);
            ctx.shadowBlur = 0;

            ctx.font = '18px Arial';
            ctx.fillStyle = 'rgba(255,255,255,0.8)';
            ctx.fillText('AI-Powered Disease Prediction & Health Recommendation', 50, 140);

            // Badge pills
            const badges = ['🤖 Machine Learning', '💊 41 Diseases', '🔬 130+ Symptoms', '📊 100% Accuracy'];
            badges.forEach((b, i) => {
                const bx = 50 + i * 220;
                ctx.fillStyle = 'rgba(100,255,218,0.15)';
                ctx.beginPath();
                ctx.roundRect(bx, 165, 200, 32, 16);
                ctx.fill();
                ctx.strokeStyle = 'rgba(100,255,218,0.4)';
                ctx.lineWidth = 1;
                ctx.stroke();
                ctx.font = '13px Arial';
                ctx.fillStyle = '#64FFDA';
                ctx.fillText(b, bx + 12, 185);
            });

            // Bottom text
            ctx.font = '13px Arial';
            ctx.fillStyle = 'rgba(255,255,255,0.5)';
            ctx.fillText('Final Year Project | Data Science | Python + SQL + ML + Power BI', 50, 255);

            t += 0.015;
            requestAnimationFrame(draw);
        }
        draw();
    })();
    </script>
    """, unsafe_allow_html=True)

    # ── 3D Stats Row ───────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3, c4, c5 = st.columns(5)

    stats = [
        ("100%", "🎯 Accuracy"),
        ("41",   "🏥 Diseases"),
        ("130+", "🔬 Symptoms"),
        ("25+",  "💊 Medicines"),
        ("8",    "🗄️ DB Tables"),
    ]
    for col, (num, label) in zip([c1,c2,c3,c4,c5], stats):
        with col:
            st.markdown(f"""
            <div class='stat-3d'>
                <div class='stat-num-3d'>{num}</div>
                <div class='stat-lbl-3d'>{label}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Feature Cards 3D ───────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>✨ System Features</div>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    features = [
        ("🔍", "Disease Prediction",
         "40+ symptoms analyse\nRandom Forest ML\n100% Accuracy\nTop 3 predictions"),
        ("💊", "Prescription",
         "41 diseases covered\nMedicines + Dosage\nSide effects info\nDoctor notes"),
        ("🥗", "Diet Plan",
         "What to eat\nWhat to avoid\nMeal timing\nHealth tips"),
        ("🏃", "Workout Routine",
         "Disease-specific\nExercise duration\nFrequency guide\nSpecial notes"),
    ]
    delays = ["0s", "0.2s", "0.4s", "0.6s"]
    for col, (icon, title, text), delay in zip([c1,c2,c3,c4], features, delays):
        with col:
            st.markdown(f"""
            <div class='feature-3d'
                 style='animation-delay:{delay};'>
                <span class='feature-icon-3d'>{icon}</span>
                <div class='feature-title-3d'>{title}</div>
                <div class='feature-text-3d'>
                    {text.replace(chr(10), '<br>')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Extra Features Row ─────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    extra = [
        ("👤", "Patient Registration", "Register yourself\nView history"),
        ("⚖️", "BMI Calculator", "Health score\nIdeal weight"),
        ("🆚", "Disease Compare", "2 diseases\nSide by side"),
    ]
    for col, (icon, title, text) in zip([c1,c2,c3], extra):
        with col:
            st.markdown(f"""
            <div class='feature-3d'>
                <span class='feature-icon-3d'>{icon}</span>
                <div class='feature-title-3d'>{title}</div>
                <div class='feature-text-3d'>
                    {text.replace(chr(10), '<br>')}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Diseases Table ─────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>🏥 Covered Diseases (41)</div>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql("""
        SELECT disease_name as Disease,
               category     as Category,
               severity     as Severity,
               description  as Description
        FROM diseases ORDER BY disease_name
    """, conn)
    conn.close()
    st.dataframe(df, use_container_width=True, hide_index=True)

    # ── How it Works ───────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='section-header'>⚡ How It Works?</div>",
                unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    steps = [
        ("1️⃣", "#64FFDA", "Select Your Symptoms",
         "Choose from 130+ symptoms you are experiencing"),
        ("2️⃣", "#40C4FF", "AI Analyses",
         "Random Forest ML model with 200 trees predicts the disease"),
        ("3️⃣", "#E040FB", "Disease Predicted",
         "Top 3 possible diseases shown with confidence percentage"),
        ("4️⃣", "#FFD740", "Get Your Report",
         "Medicine, Diet Plan and Workout Routine provided instantly"),
    ]
    for col, (num, color, title, text) in zip([c1,c2,c3,c4], steps):
        with col:
            st.markdown(f"""
            <div style='background:linear-gradient(145deg,#0d1b4b,#1a237e);
                        border:1px solid {color}40;
                        border-radius:16px; padding:20px;
                        text-align:center; margin:5px;
                        transition: all 0.3s ease;'>
                <div style='font-size:36px;'>{num}</div>
                <div style='color:{color}; font-weight:700;
                            font-size:15px; margin:10px 0;'>
                    {title}
                </div>
                <div style='color:rgba(255,255,255,0.7);
                            font-size:12px; line-height:1.6;'>
                    {text}
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── Disclaimer ─────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
    <div class='warning-box'>
        ⚠️ <b>Disclaimer:</b> This system is for educational purposes only.
        Please consult a qualified doctor for actual diagnosis.
    </div>
    """, unsafe_allow_html=True)

    # ── Social Media Footer ──────────────────────
    st.markdown("""
    <div class='social-links'>
        <h4 style='color:white; margin-bottom:15px;'>Connect With Us</h4>
        <a href='https://github.com/munishverma' target='_blank'>GitHub</a>
        <a href='https://linkedin.com/in/munishverma' target='_blank'>LinkedIn</a>
        <a href='mailto:vermamunish92451@gmail.com' target='_blank'>Email</a>
    </div>
    <div class='footer'>
        <p>Designed & Developed by Munish Verma | Final Year Project 2026</p>
        <p>Healthcare Management System v2.0</p>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════
# PAGE: HEALTH CHATBOT
# ══════════════════════════
elif page == "🤖 Health Chatbot":
    st.markdown("<div class='main-title'>🤖 AI Health Assistant</div>",
                unsafe_allow_html=True)

    st.markdown("""
    <div class='chatbot-container'>
        <p style='color:white; font-size:16px; text-align:center;'>
            👋 Hello! I'm your AI Health Assistant. Ask me about symptoms, diseases, diet, or exercise tips.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Display chat history
    for message in st.session_state.chat_history:
        if message['role'] == 'user':
            st.markdown(f"""
            <div class='chat-message user-message'>
                <b>You:</b> {message['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class='chat-message bot-message'>
                <b>🤖 HealthBot:</b> {message['content'].replace(chr(10), '<br>')}
            </div>
            """, unsafe_allow_html=True)

    # Chat input
    user_input = st.text_input("💬 Ask your health question:", placeholder="Type your question here...")
    
    col1, col2 = st.columns([1, 5])
    with col1:
        send_btn = st.button("📤 Send")
    with col2:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

    if send_btn and user_input:
        # Add user message to history
        st.session_state.chat_history.append({'role': 'user', 'content': user_input})
        
        # Get bot response
        response = chatbot_response(user_input)
        st.session_state.chat_history.append({'role': 'bot', 'content': response})
        
        st.rerun()

    # Quick suggestions
    st.markdown("---")
    st.markdown("### 💡 Quick Questions:")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("🤒 Fever Tips"):
            st.session_state.chat_history.append({'role': 'user', 'content': 'fever'})
            st.session_state.chat_history.append({'role': 'bot', 'content': chatbot_response('fever')})
            st.rerun()
    with c2:
        if st.button("🍎 Diet Advice"):
            st.session_state.chat_history.append({'role': 'user', 'content': 'diet'})
            st.session_state.chat_history.append({'role': 'bot', 'content': chatbot_response('diet')})
            st.rerun()
    with c3:
        if st.button("🏃 Exercise Tips"):
            st.session_state.chat_history.append({'role': 'user', 'content': 'exercise'})
            st.session_state.chat_history.append({'role': 'bot', 'content': chatbot_response('exercise')})
            st.rerun()
    with c4:
        if st.button("😴 Sleep Advice"):
            st.session_state.chat_history.append({'role': 'user', 'content': 'sleep'})
            st.session_state.chat_history.append({'role': 'bot', 'content': chatbot_response('sleep')})
            st.rerun()

# ══════════════════════════
# PAGE 2 — SYMPTOM CHECKER
# ══════════════════════════
elif page == "🔍 Symptom Checker":
    st.markdown("<div class='main-title'>🔍 AI Symptom Checker</div>",
                unsafe_allow_html=True)

    all_symptoms = get_symptoms()

    st.markdown("### 📝 Select Your Symptoms:")
    selected = st.multiselect(
        "Choose symptoms from the list:",
        options=all_symptoms
    )

    if selected:
        st.info(f"✅ **{len(selected)} symptoms selected:** {', '.join(selected)}")

    st.markdown("---")

    if st.button("🔍 Predict Disease"):
        if not selected:
            st.warning("⚠️ Please select at least one symptom!")
        else:
            with st.spinner("🤖 AI is analysing your symptoms..."):
                disease, confidence, top3 = predict(
                    model, symptom_list, selected)
                rec = get_recommendations(disease)
                log_pred(selected, disease, confidence)

            st.markdown(f"""
            <div class='disease-box'>
                <div style='font-size:34px; font-weight:700;'>
                    {sev_icon(rec['severity'])} {disease.upper()}
                </div>
                <div style='font-size:18px; margin-top:10px;'>
                    Confidence: {confidence*100:.1f}% &nbsp;|&nbsp;
                    Severity: {rec['severity']} &nbsp;|&nbsp;
                    Category: {rec['category']}
                </div>
                <div style='margin-top:10px; font-size:15px;
                            color:rgba(255,255,255,0.9);'>
                    {rec['description']}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("### 🔍 Top 3 Predictions:")
            for i, (d, pct) in enumerate(top3, 1):
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.progress(int(pct))
                with c2:
                    st.write(f"**{i}. {d}** {pct}%")

            st.markdown("---")
            st.markdown("<div class='section-title'>💊 Prescription / Medicines</div>",
                        unsafe_allow_html=True)
            for i, med in enumerate(rec['medicines'], 1):
                name, dose, dur, side, notes = med
                st.markdown(f"""
                <div class='medicine-card'>
                    <b style='color:#2E7D32; font-size:17px;'>
                        💊 {i}. {name}
                    </b><br><br>
                    📌 <b>Dosage:</b> {dose}<br>
                    ⏳ <b>Duration:</b> {dur}<br>
                    ⚠️ <b>Side Effects:</b> {side}<br>
                    💡 <b>Notes:</b> {notes}
                </div>
                """, unsafe_allow_html=True)

            if rec['diet']:
                eat, avoid, timing, tips = rec['diet']
                st.markdown("---")
                st.markdown("<div class='section-title'>🥗 Diet Plan</div>",
                            unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"""
                    <div class='diet-card'>
                        <b style='color:#1B5E20; font-size:16px;'>
                            ✅ Ye Khao:
                        </b><br><br>{eat}
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div class='diet-card'>
                        <b style='color:#B71C1C; font-size:16px;'>
                            ❌ Ye Avoid Karo:
                        </b><br><br>{avoid}
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown(f"""
                <div class='diet-card'>
                    🕐 <b>Meal Timing:</b> {timing}<br><br>
                    💡 <b>Tips:</b> {tips}
                </div>
                """, unsafe_allow_html=True)

            if rec['workout']:
                ex, avoid_ex, dur_min, freq, notes = rec['workout']
                st.markdown("---")
                st.markdown("<div class='section-title'>🏃 Workout Routine</div>",
                            unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f"""
                    <div class='workout-card'>
                        <b style='color:#0D47A1; font-size:16px;'>
                            ✅ Ye Exercises Karo:
                        </b><br><br>
                        {ex}<br><br>
                        ⏱️ <b>Duration:</b> {dur_min} minutes<br>
                        📅 <b>Frequency:</b> {freq}
                    </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.markdown(f"""
                    <div class='workout-card'>
                        <b style='color:#B71C1C; font-size:16px;'>
                            ❌ Ye Avoid Karo:
                        </b><br><br>
                        {avoid_ex}<br><br>
                        💡 <b>Special Notes:</b><br>{notes}
                    </div>
                    """, unsafe_allow_html=True)

            # ── PDF Download Button ────────────────
            st.markdown("---")
            pdf_data = generate_pdf(disease, confidence, rec, selected)
            st.download_button(
                label="📥 Download Health Report (PDF)",
                data=pdf_data,
                file_name=f"health_report_{disease.lower().replace(' ', '_')}.pdf",
                mime="application/pdf"
            )

            # ── Share Report Button ────────────────
            st.markdown("### 📤 Share Your Report:")
            share_text = f"I used Healthcare AI and got predicted: {disease} ({confidence*100:.1f}% confidence). Check out this Health Management System!"
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"[📱 Share on WhatsApp](https://wa.me/?text={share_text})", unsafe_allow_html=True)
            with c2:
                st.markdown(f"[🐦 Share on Twitter](https://twitter.com/intent/tweet?text={share_text})", unsafe_allow_html=True)
            with c3:
                st.markdown(f"[📧 Share via Email](mailto:?subject=Health Report&body={share_text})", unsafe_allow_html=True)

            st.markdown("""
            <div class='warning-box'>
                ⚠️ <b>Disclaimer:</b> This is an AI-based prediction.
                Please consult a qualified doctor for actual diagnosis and treatment.
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════
# PAGE 3 — ANALYTICS
# ══════════════════════════
elif page == "📊 Analytics":
    st.markdown("<div class='main-title'>📊 Analytics Dashboard</div>",
                unsafe_allow_html=True)

    conn = sqlite3.connect(DB_PATH)
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 🔵 Disease Severity")
        df = pd.read_sql(
            "SELECT severity, COUNT(*) as cnt FROM diseases GROUP BY severity",
            conn)
        fig, ax = plt.subplots(figsize=(5, 4))
        clrs = [{'Mild':'#4CAF50','Moderate':'#FFC107',
                  'Severe':'#F44336'}.get(s,'#9E9E9E')
                 for s in df['severity']]
        ax.pie(df['cnt'], labels=df['severity'], colors=clrs,
               autopct='%1.0f%%',
               wedgeprops=dict(width=0.6,edgecolor='white',linewidth=2))
        ax.set_title('Severity Distribution', fontweight='bold')
        st.pyplot(fig)
        plt.close()

    with c2:
        st.markdown("#### 📊 Symptoms per Disease")
        df = pd.read_sql("""
            SELECT d.disease_name, COUNT(ds.symptom_id) as cnt
            FROM diseases d
            JOIN disease_symptoms ds ON d.disease_id=ds.disease_id
            GROUP BY d.disease_name ORDER BY cnt DESC
        """, conn)
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.barh(df['disease_name'], df['cnt'],
                color=COLORS[:len(df)], edgecolor='white')
        ax.set_xlabel('Symptom Count')
        ax.set_title('Symptoms per Disease', fontweight='bold')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        st.pyplot(fig)
        plt.close()

    st.markdown("---")
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### 💊 Medicines per Disease")
        df = pd.read_sql("""
            SELECT d.disease_name, COUNT(m.medicine_id) as cnt
            FROM diseases d
            JOIN medicines m ON d.disease_id=m.disease_id
            GROUP BY d.disease_name ORDER BY cnt DESC
        """, conn)
        fig, ax = plt.subplots(figsize=(5, 4))
        ax.bar(df['disease_name'], df['cnt'],
               color=COLORS[:len(df)], edgecolor='white')
        ax.set_ylabel('Medicine Count')
        ax.set_title('Medicines per Disease', fontweight='bold')
        plt.xticks(rotation=40, ha='right', fontsize=8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        st.pyplot(fig)
        plt.close()

    with c2:
        st.markdown("#### 🏃 Workout Duration")
        df = pd.read_sql("""
            SELECT d.disease_name, w.duration_mins
            FROM diseases d
            JOIN workout_plans w ON d.disease_id=w.disease_id
            ORDER BY w.duration_mins DESC
        """, conn)
        fig, ax = plt.subplots(figsize=(5, 4))
        clrs = ['#4CAF50' if v > 0 else '#F44336'
                for v in df['duration_mins']]
        ax.bar(df['disease_name'], df['duration_mins'],
               color=clrs, edgecolor='white')
        ax.set_ylabel('Minutes')
        ax.set_title('Workout Duration', fontweight='bold')
        plt.xticks(rotation=40, ha='right', fontsize=8)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        st.pyplot(fig)
        plt.close()

    conn.close()

# ══════════════════════════
# PAGE 4 — MEDICINES
# ══════════════════════════
elif page == "💊 Medicines":
    st.markdown("<div class='main-title'>💊 Medicines Database</div>",
                unsafe_allow_html=True)

    disease = st.selectbox("Select Disease:", get_diseases())
    conn    = sqlite3.connect(DB_PATH)
    df      = pd.read_sql(f"""
        SELECT m.medicine_name, m.dosage, m.duration,
               m.side_effects, m.notes
        FROM medicines m
        JOIN diseases d ON m.disease_id=d.disease_id
        WHERE d.disease_name='{disease}'
    """, conn)
    conn.close()

    st.markdown(f"### 💊 Medicines for {disease}:")
    for _, row in df.iterrows():
        st.markdown(f"""
        <div class='medicine-card'>
            <b style='color:#2E7D32; font-size:17px;'>
                💊 {row['medicine_name']}
            </b><br><br>
            📌 <b>Dosage:</b> {row['dosage']}<br>
            ⏳ <b>Duration:</b> {row['duration']}<br>
            ⚠️ <b>Side Effects:</b> {row['side_effects']}<br>
            💡 <b>Notes:</b> {row['notes']}
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════
# PAGE 5 — DIET PLANS
# ══════════════════════════
elif page == "🥗 Diet Plans":
    st.markdown("<div class='main-title'>🥗 Diet Plans</div>",
                unsafe_allow_html=True)

    disease = st.selectbox("Select Disease:", get_diseases())
    conn    = sqlite3.connect(DB_PATH)
    df      = pd.read_sql(f"""
        SELECT dp.eat_foods, dp.avoid_foods,
               dp.meal_timing, dp.diet_tips
        FROM diet_plans dp
        JOIN diseases d ON dp.disease_id=d.disease_id
        WHERE d.disease_name='{disease}'
    """, conn)
    conn.close()

    if not df.empty:
        row = df.iloc[0]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class='diet-card'>
                <b style='color:#1B5E20; font-size:16px;'>
                    ✅ Ye Khao:
                </b><br><br>{row['eat_foods']}
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class='diet-card'>
                <b style='color:#B71C1C; font-size:16px;'>
                    ❌ Ye Avoid Karo:
                </b><br><br>{row['avoid_foods']}
            </div>
            """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class='diet-card'>
            🕐 <b>Meal Timing:</b> {row['meal_timing']}<br><br>
            💡 <b>Tips:</b> {row['diet_tips']}
        </div>
        """, unsafe_allow_html=True)

# ══════════════════════════
# PAGE 6 — WORKOUT PLANS
# ══════════════════════════
elif page == "🏃 Workout Plans":
    st.markdown("<div class='main-title'>🏃 Workout Plans</div>",
                unsafe_allow_html=True)

    disease = st.selectbox("Select Disease:", get_diseases())
    conn    = sqlite3.connect(DB_PATH)
    df      = pd.read_sql(f"""
        SELECT wp.exercises, wp.avoid_exercises,
               wp.duration_mins, wp.frequency, wp.special_notes
        FROM workout_plans wp
        JOIN diseases d ON wp.disease_id=d.disease_id
        WHERE d.disease_name='{disease}'
    """, conn)
    conn.close()

    if not df.empty:
        row = df.iloc[0]
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f"""
            <div class='workout-card'>
                <b style='color:#0D47A1; font-size:16px;'>
                    ✅ Ye Exercises Karo:
                </b><br><br>
                {row['exercises']}<br><br>
                ⏱️ <b>Duration:</b> {row['duration_mins']} minutes<br>
                📅 <b>Frequency:</b> {row['frequency']}
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class='workout-card'>
                <b style='color:#B71C1C; font-size:16px;'>
                    ❌ Ye Avoid Karo:
                </b><br><br>
                {row['avoid_exercises']}<br><br>
                💡 <b>Special Notes:</b><br>{row['special_notes']}
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════
# PAGE 7 — HISTORY
# ══════════════════════════
elif page == "📋 History":
    st.markdown("<div class='main-title'>📋 Prediction History</div>",
                unsafe_allow_html=True)

    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql("""
        SELECT pred_id           as ID,
               symptoms_entered  as Symptoms,
               predicted_disease as Disease,
               confidence_pct    as 'Confidence %',
               predicted_at      as 'Date & Time'
        FROM predictions
        ORDER BY predicted_at DESC
    """, conn)
    conn.close()

    if df.empty:
        st.info("📋 No predictions made yet!")
    else:
        st.markdown(f"### 📊 Total Predictions: {len(df)}")
        st.dataframe(df, use_container_width=True, hide_index=True)
        # ══════════════════════════
# PAGE: PATIENT LOGIN
# ══════════════════════════
elif page == "👤 Patient Registration":
    st.markdown("<div class='main-title'>👤 Patient Registration</div>",
                unsafe_allow_html=True)

    st.markdown("### 📝 Enter Your Details:")

    with st.form("patient_form"):
        c1, c2 = st.columns(2)
        with c1:
            name   = st.text_input("👤 Full Name")
            age    = st.number_input("🎂 Age", min_value=1, max_value=120, value=25)
            gender = st.selectbox("⚧ Gender", ["Male", "Female", "Other"])
        with c2:
            blood  = st.selectbox("🩸 Blood Group",
                                  ["A+","A-","B+","B-","AB+","AB-","O+","O-"])
            city   = st.text_input("🏙️ City")
            contact= st.text_input("📱 Mobile Number")

        submitted = st.form_submit_button("✅ Register")

        if submitted:
            if not name:
                st.warning("⚠️ Name is required!")
            else:
                conn = sqlite3.connect(DB_PATH)
                cur  = conn.cursor()
                cur.execute("""
                    INSERT INTO patients
                    (name, age, gender, blood_group, city, contact)
                    VALUES (?,?,?,?,?,?)
                """, (name, age, gender, blood, city, contact))
                conn.commit()
                pid = cur.lastrowid
                conn.close()

                st.success(f"🎉 {name} has been registered successfully!")
                st.markdown(f"""
                <div class='disease-box'>
                    <div style='font-size:24px; font-weight:700;'>
                        ✅ Patient ID: {pid}
                    </div>
                    <div style='font-size:16px; margin-top:10px;'>
                        Name: {name} | Age: {age} | Gender: {gender}<br>
                        Blood Group: {blood} | City: {city}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📋 Registered Patients:")
    conn = sqlite3.connect(DB_PATH)
    df   = pd.read_sql("""
        SELECT patient_id as ID, name as Name,
               age as Age, gender as Gender,
               blood_group as Blood, city as City,
               created_at as 'Register Date'
        FROM patients ORDER BY created_at DESC
    """, conn)
    conn.close()
    if df.empty:
        st.info("No patients registered yet!")
    else:
        st.markdown(f"**Total Patients: {len(df)}**")
        st.dataframe(df, use_container_width=True, hide_index=True)

# ══════════════════════════
# PAGE: BMI CALCULATOR
# ══════════════════════════
elif page == "⚖️ BMI Calculator":
    st.markdown("<div class='main-title'>⚖️ BMI Calculator & Health Score</div>",
                unsafe_allow_html=True)

    st.markdown("### 📏 Enter Your Details:")

    c1, c2, c3 = st.columns(3)
    with c1:
        weight = st.number_input("⚖️ Weight (kg)", min_value=1.0,
                                  max_value=300.0, value=70.0)
    with c2:
        height = st.number_input("📏 Height (cm)", min_value=50.0,
                                  max_value=250.0, value=170.0)
    with c3:
        age_bmi = st.number_input("🎂 Age", min_value=1,
                                   max_value=120, value=25)

    gender_bmi = st.radio("⚧ Gender", ["Male", "Female"], horizontal=True)

    if st.button("🔍 Calculate"):
        height_m = height / 100
        bmi      = weight / (height_m ** 2)

        # BMI Category
        if bmi < 18.5:
            cat   = "Underweight 😟"
            color = "#2196F3"
            advice= "Your weight is below normal — eat more nutritious food!"
        elif bmi < 25:
            cat   = "Normal Weight 😊"
            color = "#4CAF50"
            advice= "Great! Your weight is perfectly healthy!"
        elif bmi < 30:
            cat   = "Overweight ⚠️"
            color = "#FFC107"
            advice= "Lose some weight — focus on exercise and diet!"
        else:
            cat   = "Obese 🚨"
            color = "#F44336"
            advice= "Consult a doctor immediately — serious health risks!"

        # Health Score (0-100)
        if 18.5 <= bmi <= 24.9:
            bmi_score = 100
        elif 17 <= bmi < 18.5 or 25 <= bmi < 27:
            bmi_score = 75
        elif 15 <= bmi < 17 or 27 <= bmi < 30:
            bmi_score = 50
        else:
            bmi_score = 25

        st.markdown(f"""
        <div class='disease-box'>
            <div style='font-size:48px; font-weight:700;'>
                BMI: {bmi:.1f}
            </div>
            <div style='font-size:22px; margin-top:10px;
                        color:white;'>
                {cat}
            </div>
            <div style='font-size:16px; margin-top:8px;
                        color:rgba(255,255,255,0.9);'>
                {advice}
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🏥 Health Score:")
        st.progress(bmi_score)
        st.markdown(f"**Health Score: {bmi_score}/100**")

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("⚖️ BMI", f"{bmi:.1f}")
        with c2:
            st.metric("📊 Category", cat.split()[0])
        with c3:
            st.metric("🏥 Health Score", f"{bmi_score}/100")

        st.markdown("---")
        st.markdown("### 📊 BMI Chart:")
        st.markdown("""
        | Category | BMI Range | Status |
        |----------|-----------|--------|
        | Underweight | < 18.5 | 😟 Kam weight |
        | Normal | 18.5 - 24.9 | 😊 Theek hai |
        | Overweight | 25 - 29.9 | ⚠️ Zyada hai |
        | Obese | ≥ 30 | 🚨 Khatarnak |
        """)

        ideal_min = 18.5 * (height_m ** 2)
        ideal_max = 24.9 * (height_m ** 2)
        st.info(f"💡 Aapki height ke liye ideal weight: "
                f"**{ideal_min:.1f} kg - {ideal_max:.1f} kg**")

# ══════════════════════════
# PAGE: DISEASE COMPARISON
# ══════════════════════════
elif page == "🆚 Disease Comparison":
    st.markdown("<div class='main-title'>🆚 Disease Comparison</div>",
                unsafe_allow_html=True)

    st.markdown("### Compare Two Diseases:")

    all_diseases = get_diseases()
    c1, c2 = st.columns(2)
    with c1:
        d1 = st.selectbox("🔵 First Disease:", all_diseases, index=0)
    with c2:
        d2 = st.selectbox("🔴 Second Disease:", all_diseases, index=1)

    if st.button("🆚 Compare"):
        rec1 = get_recommendations(d1)
        rec2 = get_recommendations(d2)

        if rec1 and rec2:
            # Header
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div class='disease-box'>
                    <div style='font-size:26px; font-weight:700;'>
                        🔵 {d1.upper()}
                    </div>
                    <div style='font-size:15px; margin-top:8px;'>
                        Severity: {rec1['severity']} |
                        Category: {rec1['category']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div style='background:linear-gradient(135deg,#b71c1c,#c62828);
                            color:white; padding:30px; border-radius:15px;
                            text-align:center; margin:10px 0;'>
                    <div style='font-size:26px; font-weight:700;'>
                        🔴 {d2.upper()}
                    </div>
                    <div style='font-size:15px; margin-top:8px;'>
                        Severity: {rec2['severity']} |
                        Category: {rec2['category']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("---")

            # Description
            c1, c2 = st.columns(2)
            with c1:
                st.markdown(f"""
                <div class='medicine-card'>
                    <b style='color:#1565C0;'>📋 Description:</b><br><br>
                    {rec1['description']}
                </div>
                """, unsafe_allow_html=True)
            with c2:
                st.markdown(f"""
                <div class='medicine-card'>
                    <b style='color:#b71c1c;'>📋 Description:</b><br><br>
                    {rec2['description']}
                </div>
                """, unsafe_allow_html=True)

            # Medicines
            st.markdown("### 💊 Medicines Comparison:")
            c1, c2 = st.columns(2)
            with c1:
                for med in rec1['medicines']:
                    st.markdown(f"""
                    <div class='medicine-card'>
                        <b style='color:#2E7D32;'>💊 {med[0]}</b><br>
                        📌 {med[1]} | ⏳ {med[2]}
                    </div>
                    """, unsafe_allow_html=True)
            with c2:
                for med in rec2['medicines']:
                    st.markdown(f"""
                    <div class='medicine-card'>
                        <b style='color:#2E7D32;'>💊 {med[0]}</b><br>
                        📌 {med[1]} | ⏳ {med[2]}
                    </div>
                    """, unsafe_allow_html=True)

            # Diet
            st.markdown("### 🥗 Diet Comparison:")
            c1, c2 = st.columns(2)
            with c1:
                if rec1['diet']:
                    st.markdown(f"""
                    <div class='diet-card'>
                        <b style='color:#1B5E20;'>✅ Khao:</b><br>
                        {rec1['diet'][0]}<br><br>
                        <b style='color:#B71C1C;'>❌ Avoid:</b><br>
                        {rec1['diet'][1]}
                    </div>
                    """, unsafe_allow_html=True)
            with c2:
                if rec2['diet']:
                    st.markdown(f"""
                    <div class='diet-card'>
                        <b style='color:#1B5E20;'>✅ Khao:</b><br>
                        {rec2['diet'][0]}<br><br>
                        <b style='color:#B71C1C;'>❌ Avoid:</b><br>
                        {rec2['diet'][1]}
                    </div>
                    """, unsafe_allow_html=True)

            # Workout
            st.markdown("### 🏃 Workout Comparison:")
            c1, c2 = st.columns(2)
            with c1:
                if rec1['workout']:
                    st.markdown(f"""
                    <div class='workout-card'>
                        <b style='color:#0D47A1;'>✅ Exercises:</b><br>
                        {rec1['workout'][0]}<br><br>
                        ⏱️ <b>{rec1['workout'][2]} min</b> |
                        📅 {rec1['workout'][3]}
                    </div>
                    """, unsafe_allow_html=True)
            with c2:
                if rec2['workout']:
                    st.markdown(f"""
                    <div class='workout-card'>
                        <b style='color:#0D47A1;'>✅ Exercises:</b><br>
                        {rec2['workout'][0]}<br><br>
                        ⏱️ <b>{rec2['workout'][2]} min</b> |
                        📅 {rec2['workout'][3]}
                    </div>
                    """, unsafe_allow_html=True)

# ══════════════════════════
# PAGE: SYMPTOM SEVERITY
# ══════════════════════════
elif page == "🌡️ Symptom Severity":
    st.markdown("<div class='main-title'>🌡️ Symptom Severity Checker</div>",
                unsafe_allow_html=True)

    st.markdown("### Select Your Symptoms:")

    all_symptoms = get_symptoms()
    selected = st.multiselect(
        "Choose symptoms:",
        options=all_symptoms
    )

    if selected:
        st.markdown("### 🌡️ Rate Severity for Each Symptom:")

        severity_scores = {}
        for sym in selected:
            c1, c2 = st.columns([2, 3])
            with c1:
                st.markdown(f"**{sym.replace('_',' ').title()}**")
            with c2:
                sev = st.select_slider(
                    f"",
                    options=["Mild 🟢", "Moderate 🟡", "Severe 🔴"],
                    key=f"sev_{sym}"
                )
                severity_scores[sym] = sev

        st.markdown("---")

        if st.button("📊 Generate Health Report"):
            mild_count     = sum(1 for v in severity_scores.values() if "Mild" in v)
            moderate_count = sum(1 for v in severity_scores.values() if "Moderate" in v)
            severe_count   = sum(1 for v in severity_scores.values() if "Severe" in v)

            total   = len(selected)
            score   = int(((mild_count*1 + moderate_count*2 + severe_count*3) / (total*3)) * 100)
            urgency = "🟢 Low" if score < 40 else "🟡 Medium" if score < 70 else "🔴 HIGH"

            st.markdown(f"""
            <div class='disease-box'>
                <div style='font-size:28px; font-weight:700;'>
                    Health Risk Score: {score}/100
                </div>
                <div style='font-size:20px; margin-top:10px;'>
                    Urgency Level: {urgency}
                </div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("---")
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("🟢 Mild Symptoms",     mild_count)
            with c2:
                st.metric("🟡 Moderate Symptoms", moderate_count)
            with c3:
                st.metric("🔴 Severe Symptoms",   severe_count)

            st.progress(score)

            if severe_count > 0:
                st.error("🚨 Some of your symptoms are severe — Consult a doctor immediately!")
            elif moderate_count > 2:
                st.warning("⚠️ You have moderate symptoms — Should see a doctor soon!")
            else:
                st.success("✅ Symptoms are mild — Rest and stay hydrated!")

            # Predict disease bhi karo
            st.markdown("---")
            st.markdown("### 🔍 Possible Disease:")
            disease, confidence, top3 = predict(
                model, symptom_list, selected)
            rec = get_recommendations(disease)
            if rec:
                st.markdown(f"""
                <div class='disease-box'>
                    <div style='font-size:24px; font-weight:700;'>
                        {sev_icon(rec['severity'])} {disease.upper()}
                    </div>
                    <div style='font-size:16px; margin-top:8px;'>
                        Confidence: {confidence*100:.1f}%
                    </div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("""
            <div class='warning-box'>
                ⚠️ <b>Disclaimer:</b> This is an AI-based prediction.
                Please consult a qualified doctor for actual diagnosis and treatment.
            </div>
            """, unsafe_allow_html=True)