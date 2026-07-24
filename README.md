<div align="center">

# 🏥 AI-Powered Healthcare Management System

### Intelligent Disease Prediction & Health Recommendation Platform

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.39-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Scikit-learn](https://img.shields.io/badge/Scikit--learn-ML-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org)
[![Power BI](https://img.shields.io/badge/Power_BI-Dashboard-F2C811?style=for-the-badge&logo=powerbi&logoColor=white)](https://powerbi.microsoft.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

---

An AI-driven healthcare platform that predicts diseases from symptoms using **Random Forest ML**, provides **medicine recommendations**, **diet plans**, **workout routines**, and generates **PDF health reports** — all through a beautiful **Streamlit** web app.

[Features](#-features) | [Demo](#-demo) | [Tech Stack](#-tech-stack) | [Installation](#-installation) | [Project Structure](#-project-structure)

</div>

---

## 📋 Overview

This system is designed as a **Final Year Project** combining **Data Science, Machine Learning, SQL, and Power BI** to deliver a complete healthcare solution. Patients can enter their symptoms and receive an AI-powered diagnosis along with a full health plan.

### Key Highlights

| Metric | Value |
|--------|-------|
| 🎯 Model Accuracy | **99.5%** |
| 🏥 Diseases Covered | **41** |
| 🔬 Symptoms Database | **130+** |
| 💊 Medicines | **25+** |
| 🗄️ Database Tables | **8** |
| 📊 Power BI Reports | **4 Dashboards** |

---

## ✨ Features

### Core Features
- **🔍 AI Symptom Checker** — Select symptoms → Random Forest model predicts disease with confidence %
- **💊 Medicine Recommendations** — Dosage, duration, side effects, and doctor notes for each disease
- **🥗 Diet Plans** — Personalized eat/avoid food lists, meal timing, and health tips
- **🏃 Workout Routines** — Disease-specific exercises with duration, frequency, and precautions

### Additional Features
- **🤖 AI Health Chatbot** — Instant health advice on fever, diet, exercise, sleep, stress, and more
- **📄 PDF Report Generation** — Download complete health reports as professional PDF files
- **📤 Social Sharing** — Share reports on WhatsApp, Twitter, and Email
- **👤 Patient Registration** — User accounts with login system (SHA-256 password hashing)
- **📋 Prediction History** — Track all past predictions with timestamps
- **📊 Analytics Dashboard** — Interactive charts: severity distribution, symptoms per disease, medicine counts
- **⚖️ BMI Calculator** — Calculate Body Mass Index with health score and ideal weight
- **🆚 Disease Comparison** — Compare two diseases side by side
- **🌙 Dark Mode** — Toggle between light and dark themes
- **🎨 Animated UI** — ECG animation, DNA helix, particle effects, 3D card hover effects

---

## 🖥️ Demo

### Application Screens

| Home | Symptom Checker | Disease Result |
|------|----------------|----------------|
| Animated hero with ECG, DNA helix, particle effects | Multi-select symptoms from 130+ options | Top 3 predictions with confidence bars |

| Analytics | Chatbot | PDF Report |
|-----------|---------|------------|
| Severity pie charts, bar graphs | Health tips for fever, diet, exercise | Professional downloadable health report |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Streamlit | Interactive web application with custom CSS animations |
| **Backend** | Python 3.12 | Core logic, API, and data processing |
| **Machine Learning** | Scikit-learn (Random Forest) | Disease prediction with 200 decision trees |
| **Database** | SQLite (SQL) | 8 relational tables for healthcare data |
| **Data Analysis** | Pandas, NumPy | Data processing and numerical computation |
| **Visualization** | Matplotlib, Seaborn | Charts, heatmaps, and analytics graphs |
| **Reporting** | FPDF2 | PDF report generation |
| **BI Dashboard** | Power BI | Interactive analytics dashboards |
| **Version Control** | Git & GitHub | Source code management |

---

## ⚙️ Installation

### Prerequisites
- Python 3.10+
- pip (Python package manager)

### Steps

**1. Clone the repository**
```bash
git clone https://github.com/vermamunish92451-crypto/AI-Powered-Healthcare-Management-System.git
cd AI-Powered-Healthcare-Management-System
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Setup database** (if not already set up)
```bash
python database/schema.py
python database/insert_data.py
python database/add_recommendations.py
```

**4. Train the ML model** (optional — model already included)
```bash
python model/train_model.py
```

**5. Run the application**
```bash
streamlit run app.py
```

**6. Open browser**
```
http://localhost:8501
```

---

## 📁 Project Structure

```
AI-Powered-Healthcare-Management-System/
│
├── app.py                      # Main Streamlit application (1500+ lines)
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
│
├── database/
│   ├── schema.py               # Database schema (8 tables)
│   ├── create_database.py      # Database initialization
│   ├── insert_data.py          # Seed data insertion
│   └── add_recommendations.py  # Medicine, diet, workout data
│
├── model/
│   ├── train_model.py          # ML model training script
│   ├── prediction.py           # Prediction engine
│   └── healthcare_model.pkl    # Trained Random Forest model
│
├── dataset/
│   ├── training_data.csv       # ML training dataset
│   ├── dataset.csv             # Raw disease-symptom data
│   ├── Symptom-severity.csv    # Symptom severity levels
│   ├── symptom_Description.csv # Disease descriptions
│   └── symptom_precaution.csv  # Precautionary measures
│
├── analysis/
│   ├── eda.py                  # Exploratory Data Analysis
│   ├── eda_3d.py               # 3D visualizations
│   └── powerbi_export.py       # Power BI data export
│
├── powerbi_export/             # Exported data for Power BI
├── reports/                    # Generated reports
└── __pycache__/                # Python cache
```

---

## 🗄️ Database Schema

```
┌──────────────┐    ┌──────────────────┐    ┌──────────────┐
│   patients   │    │    diseases      │    │   symptoms   │
│──────────────│    │──────────────────│    │──────────────│
│ patient_id   │    │ disease_id       │    │ symptom_id   │
│ name         │    │ disease_name     │    │ symptom_name │
│ age          │    │ description      │    └──────────────┘
│ gender       │    │ severity         │
│ blood_group  │    │ category         │
└──────────────┘    └──────────────────┘
       │                    │
       │           ┌──────────────────┐
       │           │ disease_symptoms │
       │           │──────────────────│
       │           │ disease_id       │
       │           │ symptom_id       │
       │           └──────────────────┘
       │                    │
┌──────┴────────────────────┴──────────────────────────┐
│                                                       │
│  ┌────────────┐  ┌────────────┐  ┌────────────────┐  │
│  │ medicines  │  │ diet_plans │  │ workout_plans  │  │
│  │────────────│  │────────────│  │────────────────│  │
│  │ medicine_id│  │ diet_id    │  │ workout_id     │  │
│  │ disease_id │  │ disease_id │  │ disease_id     │  │
│  │ name       │  │ eat_foods  │  │ exercises      │  │
│  │ dosage     │  │ avoid_foods│  │ avoid_exercises│  │
│  │ duration   │  │ meal_timing│  │ duration_mins  │  │
│  └────────────┘  │ diet_tips  │  │ frequency      │  │
│                  └────────────┘  └────────────────┘  │
│                                                       │
│  ┌──────────────────────────────────────────────────┐ │
│  │                   predictions                     │ │
│  │──────────────────────────────────────────────────│ │
│  │ pred_id │ patient_id │ symptoms_entered          │ │
│  │ predicted_disease │ confidence_pct │ predicted_at│ │
│  └──────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────┘
```

---

## 🤖 Machine Learning Model

| Parameter | Value |
|-----------|-------|
| **Algorithm** | Random Forest Classifier |
| **Number of Trees** | 200 |
| **Test Size** | 20% |
| **Class Weight** | Balanced |
| **Feature Type** | Binary (symptom present/absent) |
| **Accuracy** | 99.5% |

### How It Works
1. User selects symptoms from 130+ options
2. Binary vector created (1 = symptom present, 0 = absent)
3. Random Forest model predicts disease probabilities
4. Top 3 diseases shown with confidence percentages
5. Full health plan retrieved from SQLite database

---

## 📊 Power BI Dashboards

4 interactive dashboards exported from the database:
- Disease severity distribution
- Symptom frequency analysis
- Medicine usage patterns
- Patient prediction trends

---

## ⚠️ Disclaimer

> This system is for **educational and academic purposes only**. The AI predictions are based on a trained machine learning model and should **not** be used as a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for actual medical concerns.

---

## 👨‍💻 Developer

**Munish Verma**

- 🎓 Sardar Beant Singh State University
- 📧 [vermamunish92451@gmail.com](mailto:vermamunish92451@gmail.com)
- 💻 [GitHub](https://github.com/vermamunish92451-crypto)
- 🔗 [LinkedIn](https://linkedin.com/in/munishverma)

---

<div align="center">

**Final Year Project — Data Science | 2026**

Made with ❤️ using Python, Machine Learning & Streamlit

</div>
