import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
import os

DB_PATH  = "database/healthcare.db"
SAVE_DIR = "reports"
os.makedirs(SAVE_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

print("="*55)
print("   📊 3D GRAPHS BAN RAHE HAIN...")
print("="*55)

COLORS = ['#2196F3','#4CAF50','#FF5722','#9C27B0',
          '#00BCD4','#FFC107','#E91E63','#3F51B5',
          '#8BC34A','#FF9800']

# ══════════════════════════════════════════════
# GRAPH 1 — 3D Bar: Symptoms per Disease
# ══════════════════════════════════════════════
print("\n📈 Graph 1: 3D Symptoms per Disease...")
df_sym = pd.read_sql("""
    SELECT d.disease_name, COUNT(ds.symptom_id) as count
    FROM diseases d
    JOIN disease_symptoms ds ON d.disease_id = ds.disease_id
    GROUP BY d.disease_name
    ORDER BY count DESC
""", conn)

fig = plt.figure(figsize=(14, 8))
ax  = fig.add_subplot(111, projection='3d')

x     = np.arange(len(df_sym))
y     = np.zeros(len(df_sym))
z     = np.zeros(len(df_sym))
dx    = np.ones(len(df_sym)) * 0.6
dy    = np.ones(len(df_sym)) * 0.6
dz    = df_sym['count'].values

ax.bar3d(x, y, z, dx, dy, dz,
         color=COLORS[:len(df_sym)],
         alpha=0.85,
         shade=True)

ax.set_xticks(x + 0.3)
ax.set_xticklabels(df_sym['disease_name'],
                   rotation=35, ha='right', fontsize=8)
ax.set_ylabel('', fontsize=10)
ax.set_zlabel('Symptom Count', fontsize=11)
ax.set_title('3D View: Symptoms per Disease',
             fontsize=15, fontweight='bold', pad=20)

ax.set_facecolor('#F0F4F8')
fig.patch.set_facecolor('#F8F9FA')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/3d_01_symptoms_per_disease.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 3d_01_symptoms_per_disease.png")

# ══════════════════════════════════════════════
# GRAPH 2 — 3D Bar: Medicines per Disease
# ══════════════════════════════════════════════
print("\n📈 Graph 2: 3D Medicines per Disease...")
df_med = pd.read_sql("""
    SELECT d.disease_name, COUNT(m.medicine_id) as count
    FROM diseases d
    JOIN medicines m ON d.disease_id = m.disease_id
    GROUP BY d.disease_name
    ORDER BY count DESC
""", conn)

fig = plt.figure(figsize=(14, 8))
ax  = fig.add_subplot(111, projection='3d')

x  = np.arange(len(df_med))
z  = np.zeros(len(df_med))
dz = df_med['count'].values

ax.bar3d(x, np.zeros(len(df_med)), z,
         0.6, 0.6, dz,
         color=COLORS[:len(df_med)],
         alpha=0.85, shade=True)

ax.set_xticks(x + 0.3)
ax.set_xticklabels(df_med['disease_name'],
                   rotation=35, ha='right', fontsize=8)
ax.set_zlabel('Medicine Count', fontsize=11)
ax.set_title('3D View: Medicines per Disease',
             fontsize=15, fontweight='bold', pad=20)
ax.set_facecolor('#F0F4F8')
fig.patch.set_facecolor('#F8F9FA')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/3d_02_medicines_per_disease.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 3d_02_medicines_per_disease.png")

# ══════════════════════════════════════════════
# GRAPH 3 — 3D Bar: Workout Duration
# ══════════════════════════════════════════════
print("\n📈 Graph 3: 3D Workout Duration...")
df_work = pd.read_sql("""
    SELECT d.disease_name, w.duration_mins
    FROM diseases d
    JOIN workout_plans w ON d.disease_id = w.disease_id
    ORDER BY w.duration_mins DESC
""", conn)

fig = plt.figure(figsize=(14, 8))
ax  = fig.add_subplot(111, projection='3d')

x     = np.arange(len(df_work))
dz    = df_work['duration_mins'].values
clrs  = ['#4CAF50' if v > 0 else '#F44336' for v in dz]

ax.bar3d(x, np.zeros(len(df_work)), np.zeros(len(df_work)),
         0.6, 0.6, dz,
         color=clrs, alpha=0.85, shade=True)

ax.set_xticks(x + 0.3)
ax.set_xticklabels(df_work['disease_name'],
                   rotation=35, ha='right', fontsize=8)
ax.set_zlabel('Duration (minutes)', fontsize=11)
ax.set_title('3D View: Workout Duration per Disease',
             fontsize=15, fontweight='bold', pad=20)
ax.set_facecolor('#F0F4F8')
fig.patch.set_facecolor('#F8F9FA')

green = mpatches.Patch(color='#4CAF50', label='Exercise recommended')
red   = mpatches.Patch(color='#F44336', label='Rest recommended')
ax.legend(handles=[green, red], fontsize=10)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/3d_03_workout_duration.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 3d_03_workout_duration.png")

# ══════════════════════════════════════════════
# GRAPH 4 — 3D Scatter: Disease Severity Map
# ══════════════════════════════════════════════
print("\n📈 Graph 4: 3D Severity Scatter...")
df_all = pd.read_sql("""
    SELECT d.disease_name, d.severity, d.category,
           COUNT(DISTINCT ds.symptom_id) as sym_count,
           COUNT(DISTINCT m.medicine_id) as med_count
    FROM diseases d
    LEFT JOIN disease_symptoms ds ON d.disease_id = ds.disease_id
    LEFT JOIN medicines m         ON d.disease_id = m.disease_id
    GROUP BY d.disease_name
""", conn)

sev_map  = {'Mild': 1, 'Moderate': 2, 'Severe': 3}
sev_clr  = {'Mild': '#4CAF50', 'Moderate': '#FFC107', 'Severe': '#F44336'}
df_all['sev_num'] = df_all['severity'].map(sev_map)
df_all['color']   = df_all['severity'].map(sev_clr)

fig = plt.figure(figsize=(13, 9))
ax  = fig.add_subplot(111, projection='3d')

scatter = ax.scatter(
    df_all['sym_count'],
    df_all['med_count'],
    df_all['sev_num'],
    c    = df_all['color'],
    s    = 300,
    alpha= 0.85,
    edgecolors='white',
    linewidth=1.5,
    depthshade=True
)

for _, row in df_all.iterrows():
    ax.text(row['sym_count'] + 0.1,
            row['med_count'] + 0.1,
            row['sev_num']   + 0.05,
            row['disease_name'],
            fontsize=8, fontweight='bold')

ax.set_xlabel('Symptom Count', fontsize=11, labelpad=10)
ax.set_ylabel('Medicine Count', fontsize=11, labelpad=10)
ax.set_zlabel('Severity Level', fontsize=11, labelpad=10)
ax.set_zticks([1, 2, 3])
ax.set_zticklabels(['Mild', 'Moderate', 'Severe'])
ax.set_title('3D Scatter: Disease Severity Map',
             fontsize=15, fontweight='bold', pad=20)
ax.set_facecolor('#F0F4F8')
fig.patch.set_facecolor('#F8F9FA')

patches = [mpatches.Patch(color=c, label=s)
           for s, c in sev_clr.items()]
ax.legend(handles=patches, fontsize=10, loc='upper left')

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/3d_04_severity_scatter.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 3d_04_severity_scatter.png")

# ══════════════════════════════════════════════
# GRAPH 5 — 3D Surface: Symptom Heatmap
# ══════════════════════════════════════════════
print("\n📈 Graph 5: 3D Surface Symptom Heatmap...")
diseases_df = pd.read_sql("SELECT disease_id, disease_name FROM diseases", conn)
symptoms_df = pd.read_sql("SELECT symptom_id, symptom_name FROM symptoms", conn)
mapping_df  = pd.read_sql("SELECT disease_id, symptom_id FROM disease_symptoms", conn)

matrix = pd.DataFrame(0,
    index  = diseases_df['disease_name'],
    columns= symptoms_df['symptom_name']
)
for _, row in mapping_df.iterrows():
    dn = diseases_df.loc[diseases_df['disease_id']==row['disease_id'], 'disease_name'].values
    sn = symptoms_df.loc[symptoms_df['symptom_id']==row['symptom_id'], 'symptom_name'].values
    if len(dn) and len(sn):
        matrix.loc[dn[0], sn[0]] = 1

matrix = matrix.loc[:, matrix.sum() > 0]

Z = matrix.values.astype(float)
X = np.arange(Z.shape[1])
Y = np.arange(Z.shape[0])
X, Y = np.meshgrid(X, Y)

fig = plt.figure(figsize=(16, 9))
ax  = fig.add_subplot(111, projection='3d')

surf = ax.plot_surface(X, Y, Z,
                        cmap='YlOrRd',
                        alpha=0.85,
                        edgecolor='none',
                        linewidth=0)

ax.set_yticks(range(len(matrix.index)))
ax.set_yticklabels(matrix.index, fontsize=7)
ax.set_xticks([])
ax.set_zlabel('Symptom Present', fontsize=11)
ax.set_title('3D Surface: Disease-Symptom Matrix',
             fontsize=15, fontweight='bold', pad=20)
ax.set_facecolor('#F0F4F8')
fig.patch.set_facecolor('#F8F9FA')
fig.colorbar(surf, ax=ax, shrink=0.4, label='Present (1) / Absent (0)')

plt.tight_layout()
plt.savefig(f"{SAVE_DIR}/3d_05_symptom_surface.png",
            dpi=150, bbox_inches='tight')
plt.close()
print("   ✅ Saved: 3d_05_symptom_surface.png")

conn.close()

print(f"\n{'='*55}")
print("   🎉 SAARE 5 3D GRAPHS BAN GAYE!")
print(f"   📁 Dekho: reports/ folder mein")
print(f"{'='*55}\n")