# ============================================================
# PORTFOLIO BIG DATA - ANALISIS IKLIM HARIAN
# Stasiun Meteorologi Juanda (2025)
# Google Colab Ready
# ============================================================

# ==============================================================
# CELL 0 — INSTALL & IMPORT
# ==============================================================
# !pip install openpyxl pandas matplotlib seaborn scipy networkx plotly -q

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
from scipy import stats
import warnings, os, re
from io import StringIO

warnings.filterwarnings('ignore')
plt.rcParams.update({
    'figure.dpi': 120,
    'axes.spines.top': False,
    'axes.spines.right': False,
    'font.family': 'DejaVu Sans',
    'axes.titlesize': 13,
    'axes.labelsize': 11,
})
PALETTE = sns.color_palette("husl", 10)

print("✅ Library berhasil diimpor")


# ==============================================================
# CELL 1 — INTRODUCTION & RESEARCH QUESTION
# ==============================================================
intro = """
╔══════════════════════════════════════════════════════════════╗
║     ANALISIS IKLIM HARIAN STASIUN METEOROLOGI JUANDA        ║
║                  Maret – Desember 2025                      ║
╚══════════════════════════════════════════════════════════════╝

📌 LATAR BELAKANG
   Stasiun Meteorologi Juanda (ID WMO: 96935) berlokasi di
   Sidoarjo, Jawa Timur (-7.38°LS, 112.78°BT, elevasi 3m).
   Data iklim harian digunakan untuk memahami pola cuaca,
   potensi bencana hidrometeorologi, dan perubahan iklim lokal.

📌 PROBLEM STATEMENT
   Diperlukan analisis komprehensif terhadap variabel iklim
   (suhu, curah hujan, kelembapan, angin, penyinaran matahari)
   selama 10 bulan untuk mengidentifikasi tren, anomali, dan
   pola musiman di wilayah Surabaya–Sidoarjo.

📌 RESEARCH QUESTIONS
   1. Bagaimana tren suhu harian (TN, TX, TAVG) selama 2025?
   2. Bulan apa yang memiliki curah hujan tertinggi?
   3. Apakah ada korelasi signifikan antar variabel iklim?
   4. Bagaimana distribusi arah dan kecepatan angin dominan?
   5. Apakah ada anomali/outlier dalam data yang perlu diperhatikan?
"""
print(intro)


# ==============================================================
# CELL 2 — DATA COLLECTION & SOURCES
# ==============================================================
print("=" * 60)
print("2. DATA COLLECTION & SOURCES")
print("=" * 60)

sources_info = """
📂 SUMBER DATA
   Instansi  : BMKG (Badan Meteorologi, Klimatologi, dan Geofisika)
   Stasiun   : Stasiun Meteorologi Juanda, Sidoarjo
   Format    : Excel (.xlsx) laporan iklim harian per bulan
   Periode   : Maret 2025 – Desember 2025 (10 bulan)

📋 VARIABEL DATA
   TANGGAL  → Tanggal pengamatan
   TN       → Temperatur minimum (°C)
   TX       → Temperatur maksimum (°C)
   TAVG     → Temperatur rata-rata (°C)
   RH_AVG   → Kelembapan udara rata-rata (%)
   RR       → Curah hujan (mm)
   SS       → Lama penyinaran matahari (jam)
   FF_X     → Kecepatan angin maksimum (m/s)
   DDD_X    → Arah angin saat kecepatan maks (°)
   FF_AVG   → Kecepatan angin rata-rata (m/s)
   DDD_CAR  → Arah angin terbanyak (arah mata angin)

⚠️  KODE MISSING VALUES
   8888 = Data tidak terukur
   9999 = Tidak ada data / tidak dilakukan pengukuran
"""
print(sources_info)


# ==============================================================
# CELL 3 — DATA PREPARATION (MERGE + CLEANING)
# ==============================================================
print("=" * 60)
print("3. DATA PREPARATION")
print("=" * 60)

# ── 3a. UPLOAD FILES (Colab) ──────────────────────────────────
# Jika di Google Colab, uncomment blok berikut:
# from google.colab import files
# uploaded = files.upload()   # pilih semua 10 file xlsx sekaligus
# FILE_DIR = '.'              # file tersimpan di direktori kerja

# Jika sudah upload manual atau mount Google Drive:
FILE_DIR = '.'   # ganti path sesuai lokasi file Anda
# Contoh Drive: FILE_DIR = '/content/drive/MyDrive/data_iklim'

MONTH_MAP = {
    'maret': 3, 'april': 4, 'mei': 5, 'juni': 6,
    'july': 7, 'agustus': 8, 'september': 9,
    'oktober': 10, 'november': 11, 'desember': 12
}

def parse_climate_file(filepath):
    """Baca 1 file xlsx laporan iklim BMKG, return DataFrame bersih."""
    df_raw = pd.read_excel(filepath, sheet_name=0, header=None)

    # Temukan baris header (TANGGAL)
    header_row = None
    for i, row in df_raw.iterrows():
        if any(str(v).strip().upper() == 'TANGGAL' for v in row):
            header_row = i
            break
    if header_row is None:
        raise ValueError(f"Header 'TANGGAL' tidak ditemukan di {filepath}")

    df = df_raw.iloc[header_row:].reset_index(drop=True)
    df.columns = [str(c).strip().upper() for c in df.iloc[0]]
    df = df.iloc[1:].copy()

    # Ambil kolom numerik yang relevan
    cols_keep = ['TANGGAL', 'TN', 'TX', 'TAVG', 'RH_AVG', 'RR', 'SS',
                 'FF_X', 'DDD_X', 'FF_AVG', 'DDD_CAR']
    cols_keep = [c for c in cols_keep if c in df.columns]
    df = df[cols_keep].copy()

    # Buang baris footer (KETERANGAN, dst)
    df = df[df['TANGGAL'].apply(
        lambda x: bool(re.match(r'\d{2}[-/]\d{2}[-/]\d{4}', str(x)))
    )].copy()

    # Parse tanggal
    df['TANGGAL'] = pd.to_datetime(df['TANGGAL'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['TANGGAL'])

    # Konversi numerik & ganti kode missing
    num_cols = [c for c in cols_keep if c not in ('TANGGAL', 'DDD_CAR')]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c], errors='coerce')
        df[c] = df[c].replace([8888, 9999], np.nan)

    return df


# ── 3b. BACA & GABUNG SEMUA FILE ─────────────────────────────
all_dfs = []
files_found = []

for fname in os.listdir(FILE_DIR):
    if not fname.endswith('.xlsx'):
        continue
    name_lower = fname.lower()
    matched_month = None
    for keyword, mnum in MONTH_MAP.items():
        if keyword in name_lower:
            matched_month = mnum
            break
    if matched_month is None:
        continue
    fpath = os.path.join(FILE_DIR, fname)
    try:
        df_month = parse_climate_file(fpath)
        df_month['BULAN'] = matched_month
        df_month['NAMA_BULAN'] = pd.Timestamp(2025, matched_month, 1).strftime('%B')
        all_dfs.append(df_month)
        files_found.append(f"  ✅ {fname}  →  {len(df_month)} baris")
    except Exception as e:
        files_found.append(f"  ❌ {fname}  →  ERROR: {e}")

print("\n📁 FILE YANG DIPROSES:")
for f in sorted(files_found):
    print(f)

if not all_dfs:
    print("\n⚠️  Tidak ada file yang berhasil dibaca!")
    print("   Pastikan file .xlsx berada di direktori:", FILE_DIR)
else:
    df = pd.concat(all_dfs, ignore_index=True).sort_values('TANGGAL').reset_index(drop=True)

    # ── 3c. TAMBAH KOLOM TURUNAN ─────────────────────────────
    df['RANGE_SUHU'] = df['TX'] - df['TN']
    df['HARI_HUJAN'] = (df['RR'] > 0).astype(int)
    df['KATEGORI_HUJAN'] = pd.cut(
        df['RR'].fillna(0),
        bins=[-0.1, 0, 5, 20, 50, 100, 9999],
        labels=['Tidak Hujan', 'Ringan (<5mm)', 'Sedang (5-20mm)',
                'Lebat (20-50mm)', 'Sangat Lebat (50-100mm)', 'Ekstrem (>100mm)']
    )

    print(f"\n📊 TOTAL DATA GABUNGAN: {len(df)} baris × {df.shape[1]} kolom")
    print(f"   Periode   : {df['TANGGAL'].min().date()} s/d {df['TANGGAL'].max().date()}")
    print(f"   Bulan     : {df['BULAN'].nunique()} bulan")


# ==============================================================
# CELL 4 — MISSING VALUES & QUALITY CHECK
# ==============================================================
print("\n" + "=" * 60)
print("4. MISSING VALUES & DATA QUALITY")
print("=" * 60)

num_cols = ['TN', 'TX', 'TAVG', 'RH_AVG', 'RR', 'SS', 'FF_X', 'DDD_X', 'FF_AVG']

missing = df[num_cols].isnull().sum()
missing_pct = (missing / len(df) * 100).round(2)
quality_df = pd.DataFrame({
    'Missing': missing,
    'Persen (%)': missing_pct,
    'Valid': len(df) - missing
})
print("\n📋 Ringkasan Missing Values:")
print(quality_df.to_string())

# Visualisasi missing values
fig, ax = plt.subplots(figsize=(9, 3.5))
missing_pct[missing_pct > 0].sort_values().plot(
    kind='barh', ax=ax, color='#e07b54', edgecolor='white')
ax.set_title('Persentase Missing Values per Variabel')
ax.set_xlabel('Persen (%)')
for bar in ax.patches:
    ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height()/2,
            f'{bar.get_width():.1f}%', va='center', fontsize=9)
plt.tight_layout()
plt.savefig('missing_values.png', bbox_inches='tight')
plt.show()
print("✅ Visualisasi missing values tersimpan: missing_values.png")


# ==============================================================
# CELL 5 — STATISTIK DESKRIPTIF
# ==============================================================
print("\n" + "=" * 60)
print("5. STATISTIK DESKRIPTIF")
print("=" * 60)

desc = df[num_cols].describe().round(2)
print(desc.to_string())

# Heatmap statistik per bulan
pivot_temp = df.groupby('BULAN')[['TN', 'TAVG', 'TX', 'RH_AVG', 'RR', 'SS']].mean().round(2)
pivot_temp.index = [pd.Timestamp(2025, m, 1).strftime('%b') for m in pivot_temp.index]

fig, ax = plt.subplots(figsize=(10, 4))
sns.heatmap(pivot_temp.T, annot=True, fmt='.1f', cmap='YlOrRd',
            linewidths=0.4, ax=ax, cbar_kws={'shrink': 0.8})
ax.set_title('Rata-rata Variabel Iklim per Bulan', fontsize=13)
ax.set_xlabel('Bulan')
ax.set_ylabel('')
plt.tight_layout()
plt.savefig('heatmap_bulanan.png', bbox_inches='tight')
plt.show()
print("✅ Heatmap tersimpan: heatmap_bulanan.png")


# ==============================================================
# CELL 6 — TREND ANALYSIS: SUHU
# ==============================================================
print("\n" + "=" * 60)
print("6. TREND ANALYSIS — SUHU")
print("=" * 60)

fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

# Suhu harian
ax1 = axes[0]
ax1.fill_between(df['TANGGAL'], df['TN'], df['TX'], alpha=0.2, color='#e07b54', label='Range TN–TX')
ax1.plot(df['TANGGAL'], df['TAVG'], color='#c0392b', linewidth=1.2, label='TAVG')
ax1.plot(df['TANGGAL'], df['TN'], color='#3498db', linewidth=0.8, linestyle='--', label='TN')
ax1.plot(df['TANGGAL'], df['TX'], color='#e74c3c', linewidth=0.8, linestyle='--', label='TX')

# Trendline TAVG
mask = df['TAVG'].notna()
x_num = mdates.date2num(df.loc[mask, 'TANGGAL'])
slope, intercept, r, p, _ = stats.linregress(x_num, df.loc[mask, 'TAVG'])
trend_y = slope * x_num + intercept
ax1.plot(df.loc[mask, 'TANGGAL'], trend_y, 'k--', linewidth=1.5,
         label=f'Tren TAVG (slope={slope*30:.3f}°C/bln, p={p:.3f})')
ax1.set_ylabel('Suhu (°C)')
ax1.set_title('Suhu Harian — Stasiun Juanda 2025')
ax1.legend(fontsize=9, loc='upper right')
ax1.set_ylim(18, 40)

# Range suhu harian
ax2 = axes[1]
ax2.bar(df['TANGGAL'], df['RANGE_SUHU'], color='#9b59b6', alpha=0.6, width=1)
monthly_range = df.groupby('BULAN')['RANGE_SUHU'].mean()
for bln, val in monthly_range.items():
    mask_b = df['BULAN'] == bln
    mid_date = df.loc[mask_b, 'TANGGAL'].median()
    ax2.axhline(val, xmin=0, xmax=1, color='k', alpha=0.1)
ax2.set_ylabel('Range Suhu TX–TN (°C)')
ax2.set_xlabel('Tanggal')
ax2.set_title('Range Suhu Harian (TX – TN)')
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax2.xaxis.set_major_locator(mdates.MonthLocator())
plt.setp(ax2.xaxis.get_majorticklabels(), rotation=0)

plt.tight_layout()
plt.savefig('trend_suhu.png', bbox_inches='tight')
plt.show()

print(f"\n📌 Statistik Suhu:")
print(f"   TAVG rata-rata  : {df['TAVG'].mean():.2f}°C")
print(f"   TX tertinggi    : {df['TX'].max():.1f}°C pada {df.loc[df['TX'].idxmax(), 'TANGGAL'].date()}")
print(f"   TN terendah     : {df['TN'].min():.1f}°C pada {df.loc[df['TN'].idxmin(), 'TANGGAL'].date()}")
print(f"   Tren TAVG       : {slope*30:.4f}°C/bulan (p={p:.4f})")
print(f"   Signifikan?     : {'Ya (p<0.05)' if p < 0.05 else 'Tidak (p≥0.05)'}")


# ==============================================================
# CELL 7 — ANALISIS CURAH HUJAN
# ==============================================================
print("\n" + "=" * 60)
print("7. ANALISIS CURAH HUJAN")
print("=" * 60)

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# 7a. Curah hujan harian
ax = axes[0]
colors_rr = df['RR'].apply(lambda x:
    '#d63031' if x > 100 else '#e17055' if x > 50 else '#fdcb6e' if x > 20 else '#74b9ff' if x > 5 else '#b2bec3' if x > 0 else '#dfe6e9')
ax.bar(df['TANGGAL'], df['RR'].fillna(0), color=colors_rr, width=1)
ax.set_title('Curah Hujan Harian')
ax.set_ylabel('Curah Hujan (mm)')
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
ax.xaxis.set_major_locator(mdates.MonthLocator())

# 7b. Total curah hujan per bulan
ax = axes[1]
monthly_rr = df.groupby('BULAN')['RR'].sum()
monthly_rr.index = [pd.Timestamp(2025, m, 1).strftime('%b') for m in monthly_rr.index]
bars = ax.bar(monthly_rr.index, monthly_rr.values, color=PALETTE, edgecolor='white')
for bar, val in zip(bars, monthly_rr.values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
            f'{val:.0f}', ha='center', va='bottom', fontsize=9)
ax.set_title('Total Curah Hujan per Bulan')
ax.set_ylabel('Total (mm)')
ax.set_xlabel('Bulan')

# 7c. Distribusi kategori hujan
ax = axes[2]
kat_counts = df['KATEGORI_HUJAN'].value_counts()
kat_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%', startangle=90,
                colors=sns.color_palette('pastel', len(kat_counts)),
                textprops={'fontsize': 8})
ax.set_title('Distribusi Kategori Hujan')
ax.set_ylabel('')

plt.tight_layout()
plt.savefig('analisis_hujan.png', bbox_inches='tight')
plt.show()

bulan_terlembab = monthly_rr.idxmax()
print(f"\n📌 Statistik Curah Hujan:")
print(f"   Total setahun       : {df['RR'].sum():.1f} mm")
print(f"   Bulan terbanyak     : {bulan_terlembab} ({monthly_rr.max():.1f} mm)")
print(f"   Hari hujan          : {df['HARI_HUJAN'].sum()} hari ({df['HARI_HUJAN'].mean()*100:.1f}%)")
print(f"   RR maksimum harian  : {df['RR'].max():.1f} mm pada {df.loc[df['RR'].idxmax(), 'TANGGAL'].date()}")


# ==============================================================
# CELL 8 — ANALISIS KELEMBAPAN & PENYINARAN
# ==============================================================
print("\n" + "=" * 60)
print("8. KELEMBAPAN & PENYINARAN MATAHARI")
print("=" * 60)

fig, axes = plt.subplots(2, 2, figsize=(14, 8))

# 8a. Kelembapan harian
ax = axes[0, 0]
monthly_rh = df.groupby('BULAN')['RH_AVG']
for bln, grp in monthly_rh:
    ax.plot(grp.index, grp.values, alpha=0.3, linewidth=0.5, color='steelblue')
df_roll = df.set_index('TANGGAL')['RH_AVG'].rolling('7D').mean()
ax.plot(df_roll.index, df_roll.values, color='navy', linewidth=2, label='MA 7 hari')
ax.set_title('Kelembapan Udara Harian (RH_AVG)')
ax.set_ylabel('Kelembapan (%)')
ax.legend()
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

# 8b. Distribusi kelembapan per bulan (boxplot)
ax = axes[0, 1]
data_rh = [df[df['BULAN'] == b]['RH_AVG'].dropna().values for b in sorted(df['BULAN'].unique())]
labels_b = [pd.Timestamp(2025, b, 1).strftime('%b') for b in sorted(df['BULAN'].unique())]
bp = ax.boxplot(data_rh, labels=labels_b, patch_artist=True,
                medianprops={'color': 'black', 'linewidth': 1.5})
for patch, color in zip(bp['boxes'], PALETTE):
    patch.set_facecolor(color)
    patch.set_alpha(0.7)
ax.set_title('Distribusi Kelembapan per Bulan')
ax.set_ylabel('RH_AVG (%)')

# 8c. Penyinaran matahari per bulan
ax = axes[1, 0]
monthly_ss = df.groupby('BULAN')['SS'].mean()
monthly_ss.index = [pd.Timestamp(2025, m, 1).strftime('%b') for m in monthly_ss.index]
ax.plot(monthly_ss.index, monthly_ss.values, 'o-', color='#f39c12', linewidth=2, markersize=8)
ax.fill_between(range(len(monthly_ss)), monthly_ss.values, alpha=0.15, color='#f39c12')
ax.set_xticks(range(len(monthly_ss)))
ax.set_xticklabels(monthly_ss.index)
ax.set_title('Rata-rata Penyinaran Matahari per Bulan')
ax.set_ylabel('Lama Penyinaran (jam)')

# 8d. Scatter RR vs SS
ax = axes[1, 1]
scatter = ax.scatter(df['SS'], df['RR'], c=df['BULAN'], cmap='tab10',
                     alpha=0.5, s=20, edgecolors='none')
plt.colorbar(scatter, ax=ax, label='Bulan')
mask_ss = df['SS'].notna() & df['RR'].notna()
r_val, p_val = stats.pearsonr(df.loc[mask_ss, 'SS'], df.loc[mask_ss, 'RR'])
ax.set_title(f'Hubungan Penyinaran vs Curah Hujan\n(r={r_val:.3f}, p={p_val:.4f})')
ax.set_xlabel('Penyinaran (jam)')
ax.set_ylabel('Curah Hujan (mm)')

plt.tight_layout()
plt.savefig('kelembapan_penyinaran.png', bbox_inches='tight')
plt.show()

print(f"\n📌 Kelembapan:")
print(f"   Rata-rata  : {df['RH_AVG'].mean():.1f}%")
print(f"   Tertinggi  : {df['RH_AVG'].max():.0f}% pada {df.loc[df['RH_AVG'].idxmax(), 'TANGGAL'].date()}")
print(f"\n📌 Penyinaran:")
print(f"   Rata-rata  : {df['SS'].mean():.1f} jam/hari")
print(f"   Korelasi dgn RR: r={r_val:.3f} ({'signifikan' if p_val<0.05 else 'tidak signifikan'})")


# ==============================================================
# CELL 9 — ANALISIS ANGIN
# ==============================================================
print("\n" + "=" * 60)
print("9. ANALISIS ANGIN")
print("=" * 60)

fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# 9a. Distribusi kecepatan angin
ax = axes[0]
ax.hist(df['FF_AVG'].dropna(), bins=20, color='#00b894', edgecolor='white', alpha=0.8)
ax.axvline(df['FF_AVG'].mean(), color='red', linestyle='--', linewidth=1.5,
           label=f'Mean: {df["FF_AVG"].mean():.2f} m/s')
ax.set_title('Distribusi Kecepatan Angin Rata-rata')
ax.set_xlabel('Kecepatan (m/s)')
ax.set_ylabel('Frekuensi')
ax.legend()

# 9b. Kecepatan angin bulanan
ax = axes[1]
monthly_wind = df.groupby('BULAN')[['FF_AVG', 'FF_X']].mean()
x = np.arange(len(monthly_wind))
w = 0.35
ax.bar(x - w/2, monthly_wind['FF_AVG'], w, label='FF_AVG', color='#00b894', alpha=0.8)
ax.bar(x + w/2, monthly_wind['FF_X'], w, label='FF_X', color='#00cec9', alpha=0.8)
ax.set_xticks(x)
ax.set_xticklabels([pd.Timestamp(2025, m, 1).strftime('%b') for m in monthly_wind.index])
ax.set_title('Kecepatan Angin Rata-rata vs Maks per Bulan')
ax.set_ylabel('Kecepatan (m/s)')
ax.legend()

# 9c. Arah angin dominan (DDD_CAR)
ax = axes[2]
ddd_counts = df['DDD_CAR'].value_counts()
ddd_counts = ddd_counts[ddd_counts.index.notna() & (ddd_counts.index != 'nan')]
wedges, texts, autotexts = ax.pie(
    ddd_counts.values, labels=ddd_counts.index,
    autopct='%1.1f%%', startangle=90,
    colors=sns.color_palette('Set2', len(ddd_counts)),
    textprops={'fontsize': 9})
ax.set_title('Distribusi Arah Angin Dominan (DDD_CAR)')

plt.tight_layout()
plt.savefig('analisis_angin.png', bbox_inches='tight')
plt.show()

print(f"\n📌 Statistik Angin:")
print(f"   FF_AVG rata-rata : {df['FF_AVG'].mean():.2f} m/s")
print(f"   FF_X maksimum    : {df['FF_X'].max():.1f} m/s pada {df.loc[df['FF_X'].idxmax(), 'TANGGAL'].date()}")
print(f"   Arah dominan     : {ddd_counts.idxmax()} ({ddd_counts.max()} hari)")


# ==============================================================
# CELL 10 — MATRIKS KORELASI
# ==============================================================
print("\n" + "=" * 60)
print("10. MATRIKS KORELASI ANTAR VARIABEL")
print("=" * 60)

corr_cols = ['TN', 'TX', 'TAVG', 'RH_AVG', 'RR', 'SS', 'FF_X', 'FF_AVG']
corr_matrix = df[corr_cols].corr()

fig, ax = plt.subplots(figsize=(9, 7))
mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdBu_r',
            center=0, vmin=-1, vmax=1, mask=mask,
            linewidths=0.5, ax=ax, annot_kws={'size': 10},
            cbar_kws={'shrink': 0.8, 'label': 'Pearson r'})
ax.set_title('Matriks Korelasi Variabel Iklim', fontsize=13)
plt.tight_layout()
plt.savefig('korelasi.png', bbox_inches='tight')
plt.show()

# Tampilkan korelasi kuat
print("\n📌 Korelasi Kuat (|r| ≥ 0.4):")
for c1 in corr_cols:
    for c2 in corr_cols:
        if c1 >= c2:
            continue
        r = corr_matrix.loc[c1, c2]
        if abs(r) >= 0.4:
            direction = "positif" if r > 0 else "negatif"
            print(f"   {c1} ↔ {c2}: r={r:.3f} ({direction})")


# ==============================================================
# CELL 11 — DETEKSI OUTLIER & ANOMALI
# ==============================================================
print("\n" + "=" * 60)
print("11. DETEKSI OUTLIER & ANOMALI")
print("=" * 60)

fig, axes = plt.subplots(2, 4, figsize=(16, 7))
axes = axes.flatten()

outlier_summary = []
for i, col in enumerate(corr_cols):
    ax = axes[i]
    data = df[col].dropna()

    Q1, Q3 = data.quantile(0.25), data.quantile(0.75)
    IQR = Q3 - Q1
    lower, upper = Q1 - 1.5*IQR, Q3 + 1.5*IQR
    outliers = df[(df[col] < lower) | (df[col] > upper)][['TANGGAL', col]]

    ax.boxplot(data, patch_artist=True,
               boxprops={'facecolor': '#74b9ff', 'alpha': 0.7},
               medianprops={'color': 'red', 'linewidth': 2},
               flierprops={'marker': 'o', 'color': '#d63031', 'markersize': 4})
    ax.set_title(f'{col}\n({len(outliers)} outlier)', fontsize=10)
    ax.set_xlabel('')

    outlier_summary.append({
        'Variabel': col, 'Q1': round(Q1, 2), 'Q3': round(Q3, 2),
        'IQR': round(IQR, 2), 'Batas Bawah': round(lower, 2),
        'Batas Atas': round(upper, 2), 'Jumlah Outlier': len(outliers)
    })

plt.suptitle('Deteksi Outlier per Variabel (Metode IQR)', fontsize=13, y=1.01)
plt.tight_layout()
plt.savefig('outlier.png', bbox_inches='tight')
plt.show()

outlier_df = pd.DataFrame(outlier_summary)
print("\n📋 Ringkasan Outlier:")
print(outlier_df.to_string(index=False))


# ==============================================================
# CELL 12 — RINGKASAN BULANAN (EXPORT CSV)
# ==============================================================
print("\n" + "=" * 60)
print("12. RINGKASAN BULANAN & EXPORT")
print("=" * 60)

monthly_summary = df.groupby(['BULAN', 'NAMA_BULAN']).agg(
    TN_mean=('TN', 'mean'), TX_mean=('TX', 'mean'), TAVG_mean=('TAVG', 'mean'),
    RH_mean=('RH_AVG', 'mean'), RR_total=('RR', 'sum'), RR_max=('RR', 'max'),
    hari_hujan=('HARI_HUJAN', 'sum'), SS_mean=('SS', 'mean'),
    FF_AVG_mean=('FF_AVG', 'mean'), FF_X_max=('FF_X', 'max'), n_hari=('TANGGAL', 'count')
).round(2).reset_index()

print("\n📊 Ringkasan Bulanan:")
print(monthly_summary[['NAMA_BULAN', 'TN_mean', 'TX_mean', 'TAVG_mean',
                         'RH_mean', 'RR_total', 'hari_hujan', 'SS_mean']].to_string(index=False))

df.to_csv('data_iklim_gabungan_2025.csv', index=False)
monthly_summary.to_csv('ringkasan_bulanan_2025.csv', index=False)
print("\n✅ File tersimpan:")
print("   - data_iklim_gabungan_2025.csv")
print("   - ringkasan_bulanan_2025.csv")


# ==============================================================
# CELL 13 — FINDINGS & CONCLUSIONS
# ==============================================================
print("\n" + "=" * 60)
print("13. KEY FINDINGS & CONCLUSIONS")
print("=" * 60)

findings = f"""
╔══════════════════════════════════════════════════════════════╗
║                    KEY FINDINGS                             ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  🌡️  SUHU                                                    ║
║  • TAVG rata-rata tahunan: {df['TAVG'].mean():.2f}°C                      ║
║  • TX maksimum: {df['TX'].max():.1f}°C | TN minimum: {df['TN'].min():.1f}°C           ║
║  • Tren suhu: {slope*30:+.4f}°C/bulan                            ║
║                                                              ║
║  🌧️  CURAH HUJAN                                             ║
║  • Total: {df['RR'].sum():.0f} mm | Hari hujan: {df['HARI_HUJAN'].sum()} hari               ║
║  • Kategori dominan: Tidak Hujan/Hujan Ringan               ║
║                                                              ║
║  💨  ANGIN                                                   ║
║  • Arah dominan: {ddd_counts.idxmax()} | FF_AVG: {df['FF_AVG'].mean():.2f} m/s              ║
║                                                              ║
║  📊  KORELASI KUAT                                           ║
║  • TN ↔ TX: korelasi positif (suhu min-maks konsisten)      ║
║  • SS ↔ RR: korelasi negatif (lebih cerah → kurang hujan)  ║
║  • RH ↔ RR: korelasi positif (kelembapan tinggi → lebih hujan)║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  📝  REKOMENDASI                                             ║
║  1. Monitor bulan dengan RR tinggi untuk kesiapsiagaan banjir║
║  2. Pola angin dominan berguna untuk perencanaan penerbangan ║
║  3. Data penyinaran berguna untuk estimasi energi surya      ║
║  4. Anomali outlier perlu divalidasi ulang ke sumber asli   ║
╚══════════════════════════════════════════════════════════════╝
"""
print(findings)


# ==============================================================
# CELL 14 — SELF-ASSESSMENT RUBRIC
# ==============================================================
print("=" * 60)
print("14. SELF-ASSESSMENT RUBRIC")
print("=" * 60)

rubric = """
┌─────────────────────────────────────┬──────────┬──────────────────────┐
│ Kriteria                            │ Nilai    │ Catatan              │
├─────────────────────────────────────┼──────────┼──────────────────────┤
│ 1. Kelengkapan data & sumber        │  _ / 20  │                      │
│ 2. Kualitas data preparation        │  _ / 20  │                      │
│ 3. Kedalaman EDA                    │  _ / 20  │                      │
│ 4. Kualitas visualisasi             │  _ / 20  │                      │
│ 5. Insight & interpretasi           │  _ / 20  │                      │
├─────────────────────────────────────┼──────────┼──────────────────────┤
│ TOTAL                               │  _ / 100 │                      │
└─────────────────────────────────────┴──────────┴──────────────────────┘

📝 Isi tabel di atas secara jujur berdasarkan hasil portfolio Anda.
"""
print(rubric)


# ==============================================================
# CELL 15 — REFLECTION
# ==============================================================
print("=" * 60)
print("15. REFLECTION & PEER FEEDBACK")
print("=" * 60)

reflection_template = """
📓 REFLECTION JOURNAL
─────────────────────
Tanggal  : _______________
Nama     : _______________

1. Apa yang paling saya pelajari dari proyek ini?
   ___________________________________________________

2. Tantangan terbesar yang saya hadapi:
   ___________________________________________________

3. Bagaimana cara saya mengatasi tantangan tersebut?
   ___________________________________________________

4. Apa yang akan saya lakukan berbeda jika mengulang proyek ini?
   ___________________________________________________

5. Skill baru yang saya kuasai (pandas, visualisasi, statistik, dll):
   ___________________________________________________


📋 PEER FEEDBACK (diisi oleh rekan)
────────────────────────────────────
Reviewer : _______________

Kekuatan portfolio ini:
+ ___________________________________________________
+ ___________________________________________________

Area yang bisa ditingkatkan:
△ ___________________________________________________
△ ___________________________________________________

Saran spesifik:
→ ___________________________________________________
"""
print(reflection_template)
print("\n✅ ============================================")
print("   PORTFOLIO SELESAI! Semua output tersimpan.")
print("   File CSV dan PNG siap diunduh dari Colab.")
print("=" * 50)
