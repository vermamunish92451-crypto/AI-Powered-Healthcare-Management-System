import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os

DB_PATH  = "database/healthcare.db"
SAVE_DIR = "reports"
os.makedirs(SAVE_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

print("="*55)
print("   📊 EDA - GRAPHS BAN RAHE HAIN...")
print("="*55)

# Style set karo
plt.rcParams['figure.facecolor'] = '#F8F9FA'
plt.rcParams['axes.facecolor']   = '#FFFFFF'
plt.rcParams['font.family']      = 'DejaVu Sans'

COLORS = ['#2196F3','#4CAF50','#FF5722','#9C27B0',
          '#00BCD4','#FFC107','#E91E63','#3F51B5',
          '#8BC34A','#FF9800']

# ══════════════════════════════════════════════
# GRAPH 1 — Disease Severity Distribution
# ══════════════════════════════════════════════
print("\n📈 Graph 1: Disease Severity...")
df_sev = pd.read_sql("""
    SELECT severity, COUNT(*) as count
    FROM diseases GROUP BY severity
""", conn)

fig, ax = plt.subplots(figsize=(8, 6))
severity_colors = {
    'Mild'    : '#4CAF50',
    'Moderate': '#FFC107',
    'Severe'  : '#F44336'
}
clrs = [severity_colors.get(s, '#9E9E9E') for s in df_sev['severity']]
wedges, texts, autotexts = ax.pie(
    df_sev['count'],
    labels    = df_sev['severity'],
    colors    = clrs,
    autopct   = '%1.0f%%',
    startangle= 90,
    wedgeprops= dict(width=0.6, edgecolor='white', linewidth=3),
    textprops = {'fontsize': 13}
)
for at in autotexts:
    at.set_fontsize(14)
    at.set_fontweight('bold')
    at.set_color('white')

ax.set_title('Disease Severity Distribution',
             fontsize=16, fontweight='bold', pad=20)

# Legend
patches = [mpatches.Patch(color=c, label=s)
           for s, c in severity_colors.items()]
ax.legend(handles=patches, loc='lower right', fontsize=11)

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/01_severity_distribution.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 01_severity_distribution.png")

# ══════════════════════════════════════════════
# GRAPH 2 — Symptoms per Disease
# ══════════════════════════════════════════════
print("\n📈 Graph 2: Symptoms per Disease...")
df_sym = pd.read_sql("""
    SELECT d.disease_name, COUNT(ds.symptom_id) as count
    FROM diseases d
    JOIN disease_symptoms ds ON d.disease_id = ds.disease_id
    GROUP BY d.disease_name
    ORDER BY count DESC
""", conn)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(df_sym['disease_name'], df_sym['count'],
              color=COLORS, edgecolor='white', linewidth=1.5)
ax.set_title('Number of Symptoms per Disease',
             fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Disease', fontsize=13)
ax.set_ylabel('Symptom Count', fontsize=13)
ax.set_ylim(0, df_sym['count'].max() + 2)
plt.xticks(rotation=40, ha='right', fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3)

for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 0.1,
            str(int(h)), ha='center', va='bottom',
            fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/02_symptoms_per_disease.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 02_symptoms_per_disease.png")

# ══════════════════════════════════════════════
# GRAPH 3 — Disease Category Bar Chart
# ══════════════════════════════════════════════
print("\n📈 Graph 3: Disease Categories...")
df_cat = pd.read_sql("""
    SELECT category, COUNT(*) as count
    FROM diseases GROUP BY category
    ORDER BY count DESC
""", conn)

fig, ax = plt.subplots(figsize=(10, 6))
cat_colors = ['#2196F3','#4CAF50','#FF5722','#9C27B0','#FFC107']
bars = ax.barh(df_cat['category'], df_cat['count'],
               color=cat_colors[:len(df_cat)],
               edgecolor='white', linewidth=1.5)
ax.set_title('Diseases by Medical Category',
             fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Number of Diseases', fontsize=13)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='x', alpha=0.3)

for bar in bars:
    w = bar.get_width()
    ax.text(w + 0.05, bar.get_y() + bar.get_height()/2,
            str(int(w)), va='center', fontsize=13, fontweight='bold')

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/03_disease_categories.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 03_disease_categories.png")

# ══════════════════════════════════════════════
# GRAPH 4 — Disease Symptom Heatmap
# ══════════════════════════════════════════════
print("\n📈 Graph 4: Disease-Symptom Heatmap...")
diseases_df = pd.read_sql("SELECT disease_id, disease_name FROM diseases", conn)
symptoms_df = pd.read_sql("SELECT symptom_id, symptom_name FROM symptoms", conn)
mapping_df  = pd.read_sql("SELECT disease_id, symptom_id FROM disease_symptoms", conn)

matrix = pd.DataFrame(0,
    index  = diseases_df['disease_name'],
    columns= symptoms_df['symptom_name']
)
for _, row in mapping_df.iterrows():
    dname = diseases_df.loc[diseases_df['disease_id']==row['disease_id'], 'disease_name'].values
    sname = symptoms_df.loc[symptoms_df['symptom_id']==row['symptom_id'], 'symptom_name'].values
    if len(dname) and len(sname):
        matrix.loc[dname[0], sname[0]] = 1

matrix = matrix.loc[:, matrix.sum() > 0]

fig, ax = plt.subplots(figsize=(20, 7))
sns.heatmap(matrix, cmap='YlOrRd',
            linewidths=0.5, linecolor='#eeeeee',
            cbar_kws={'shrink': 0.6, 'label': 'Symptom Present'},
            ax=ax, vmin=0, vmax=1)
ax.set_title('Disease vs Symptom Matrix',
             fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Symptoms', fontsize=12)
ax.set_ylabel('Diseases', fontsize=12)
plt.xticks(rotation=50, ha='right', fontsize=9)
plt.yticks(rotation=0, fontsize=10)
plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/04_disease_symptom_heatmap.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 04_disease_symptom_heatmap.png")

# ══════════════════════════════════════════════
# GRAPH 5 — Workout Duration per Disease
# ══════════════════════════════════════════════
print("\n📈 Graph 5: Workout Duration...")
df_work = pd.read_sql("""
    SELECT d.disease_name, w.duration_mins
    FROM diseases d
    JOIN workout_plans w ON d.disease_id = w.disease_id
    ORDER BY w.duration_mins DESC
""", conn)

fig, ax = plt.subplots(figsize=(12, 6))
clrs = ['#4CAF50' if x > 0 else '#F44336' for x in df_work['duration_mins']]
bars = ax.bar(df_work['disease_name'], df_work['duration_mins'],
              color=clrs, edgecolor='white', linewidth=1.5)
ax.set_title('Recommended Workout Duration per Disease',
             fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Disease', fontsize=13)
ax.set_ylabel('Duration (minutes)', fontsize=13)
plt.xticks(rotation=40, ha='right', fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3)

green_patch = mpatches.Patch(color='#4CAF50', label='Exercise recommended')
red_patch   = mpatches.Patch(color='#F44336', label='Rest recommended')
ax.legend(handles=[green_patch, red_patch], fontsize=11)

for bar in bars:
    h = bar.get_height()
    label = f"{int(h)} min" if h > 0 else "Rest"
    ax.text(bar.get_x() + bar.get_width()/2, h + 0.3,
            label, ha='center', va='bottom',
            fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/05_workout_duration.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 05_workout_duration.png")

# ══════════════════════════════════════════════
# GRAPH 6 — Medicine Count per Disease
# ══════════════════════════════════════════════
print("\n📈 Graph 6: Medicines per Disease...")
df_med = pd.read_sql("""
    SELECT d.disease_name, COUNT(m.medicine_id) as count
    FROM diseases d
    JOIN medicines m ON d.disease_id = m.disease_id
    GROUP BY d.disease_name
    ORDER BY count DESC
""", conn)

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.bar(df_med['disease_name'], df_med['count'],
              color=COLORS, edgecolor='white', linewidth=1.5)
ax.set_title('Number of Medicines per Disease',
             fontsize=16, fontweight='bold', pad=15)
ax.set_xlabel('Disease', fontsize=13)
ax.set_ylabel('Medicine Count', fontsize=13)
plt.xticks(rotation=40, ha='right', fontsize=10)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.grid(axis='y', alpha=0.3)

for bar in bars:
    h = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, h + 0.05,
            str(int(h)), ha='center', va='bottom',
            fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/06_medicines_per_disease.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 06_medicines_per_disease.png")

conn.close()

print(f"\n{'='*55}")
print("   🎉 SAARE 6 GRAPHS BAN GAYE!")
print(f"   📁 Dekho: reports/ folder mein")
print(f"{'='*55}\n")