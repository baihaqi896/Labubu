# Labubu
Tugas Kelompok Labubu Scrapping web Tokopedia OffICIAL Store Samsung
# Climate Data Analysis using BMKG Dataset
# Project Overview
Proyek ini berfokus pada analisis data iklim harian dengan pendekatan Big Data, khususnya menggunakan konsep 5V untuk mengevaluasi karakteristik dataset.

Data yang digunakan mencakup berbagai parameter atmosfer seperti suhu, kelembapan, curah hujan, penyinaran matahari, serta kecepatan dan arah angin. Melalui analisis ini, diharapkan dapat diperoleh pemahaman mengenai pola cuaca, tren musiman, serta indikasi kejadian cuaca ekstrem.

# Sumber Data
Dataset berasal dari BMKG (Badan Meteorologi, Klimatologi, dan Geofisika).

Data diambil dari:
- Stasiun Meteorologi Juanda, Surabaya
- Periode: Maret 2025 – Maret 2026
- Format: File Microsoft Excel (.xlsx) bulanan

Dataset ini merupakan data resmi yang digunakan untuk pemantauan kondisi cuaca dan iklim di Indonesia.

# Objectives
- Menganalisis karakteristik data iklim menggunakan konsep 5V Big Data
- Mengidentifikasi pola distribusi parameter iklim
- Mendeteksi anomali cuaca ekstrem
- Memahami hubungan antar parameter iklim
- Menghasilkan insight berbasis data untuk berbagai sektor

# Tujuan Analisis
Tujuan analisis adalah untuk membuktikan bahwa dataset iklim harian memenuhi karakteristik Big Data serta menghasilkan insight yang bermanfaat.

Analisis difokuskan pada:
- Distribusi data (EDA)
- Pola time series (tren waktu)
- Hubungan antar parameter (cuaca & iklim)
Tidak hanya eksplorasi data, tetapi juga interpretasi terhadap kondisi iklim yang terjadi.

# Dataset
Dataset yang digunakan adalah data iklim harian BMKG dengan karakteristik:
- 365+ data harian
- 13 file bulanan
- 11 parameter iklim

Parameter meliputi:
- Suhu (TN, TX, TAVG)
- Kelembapan (RH_AVG)
- Curah hujan (RR)
- Penyinaran matahari (SS)
- Kecepatan & arah angin

# Big Data Characteristics (5V + 3V)
1. Volume

Jumlah data yang digunakan mencakup ratusan observasi dengan berbagai parameter iklim yang cukup kompleks.

2. Velocity

Data dikumpulkan secara rutin setiap hari melalui sensor otomatis.

Dalam konteks nyata:
- Data terus bertambah seiring waktu
- Berpotensi digunakan dalam sistem pemantauan cuaca secara real-time

3. Variety

Dataset menunjukkan keberagaman dalam jenis data:
- Data numerik untuk parameter fisik
- Data kategorikal untuk arah angin
- Data waktu dalam format datetime

4. Veracity

Beberapa tantangan kualitas data ditemukan, seperti:
- Nilai kosong akibat error sensor
- Ketidaklengkapan pada beberapa parameter

Untuk mengatasinya dilakukan:
- Pengisian data berdasarkan nilai sebelumnya dan sesudahnya
- Pendekatan statistik seperti median

5. Value

Data memiliki manfaat yang signifikan dalam berbagai bidang, antara lain:
- Analisis kondisi cuaca
- Antisipasi bencana hidrometeorologi
- Perencanaan sektor pertanian
- Dukungan operasional transportasi udara

6. Variability

Perubahan nilai yang cukup dinamis terlihat pada beberapa parameter, khususnya:
- Curah hujan yang sangat fluktuatif
- Intensitas penyinaran matahari
- Perubahan kelembapan antar musim

7. Visualization

Berbagai teknik visualisasi digunakan untuk memahami data, seperti:
- Histogram untuk melihat distribusi
- Grafik time series untuk tren waktu
- Perbandingan antar variabel

Visualisasi ini membantu dalam mengidentifikasi pola serta anomali pada data.
  
8. Validity

Karena bersumber dari lembaga resmi, data memiliki tingkat kredibilitas yang tinggi.

Namun demikian, tetap diperlukan:
- Proses pembersihan data
- Evaluasi hasil analisis
- Interpretasi yang sesuai dengan kondisi nyata
# BIG-DATA
