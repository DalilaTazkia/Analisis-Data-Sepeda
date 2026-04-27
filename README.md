# 🚲 Analisis Data Peminjaman Sepeda – Bike Sharing Dataset

## 📋 Deskripsi Proyek
Proyek analisis data ini mengeksplorasi dataset **Capital Bikeshare Washington D.C. (2011–2012)**
untuk menjawab dua pertanyaan bisnis berbasis metode SMART:

1. **Pola peminjaman per jam** – Hari Kerja vs. Hari Libur/Akhir Pekan
2. **Pengaruh cuaca & musim** – terhadap total peminjaman harian

---

## 📁 Struktur File
```
.
├── notebook_analisis_sepeda.ipynb   # Jupyter Notebook – seluruh alur analisis
├── dashboard.py                     # Streamlit Dashboard interaktif
├── requirements.txt                 # Dependensi Python
├── day.csv                          # Dataset harian
├── hour.csv                         # Dataset per jam
└── README.md                        # Dokumentasi proyek
```

---

## 🚀 Cara Menjalankan

### 1. Instalasi Dependensi
```bash
pip install -r requirements.txt
```

### 2. Jalankan Dashboard Streamlit
```bash
streamlit run dashboard.py
```
Pastikan file `day.csv` dan `hour.csv` berada di direktori yang sama dengan `dashboard.py`.

### 3. Buka Notebook
```bash
jupyter notebook notebook_analisis_sepeda.ipynb
```

---

## 📊 Fitur Dashboard
- **Filter Interaktif**: Tahun, Musim, Kondisi Cuaca, Tipe Hari
- **Tab 1 – Pola Per Jam**: Line chart & heatmap jam × hari dalam minggu
- **Tab 2 – Cuaca & Musim**: Barplot cuaca, boxplot musim, heatmap silang
- **Tab 3 – Tren & Clustering**: Tren bulanan 2011 vs 2012, donut chart clustering permintaan
- **Tab 4 – Korelasi**: Scatter plot suhu, heatmap korelasi, bar chart nilai korelasi

---

## 🔑 Kesimpulan Utama
1. **Hari kerja** → pola bimodal (puncak 08:00 & 17:00) → pola commuter
2. **Hari libur** → pola unimodal (puncak 11:00–13:00) → aktivitas rekreasi
3. **Cuaca cerah** → rata-rata 4.876 peminjaman/hari vs. cuaca hujan hanya 1.803 (turun >63%)
4. **Musim Fall (Gugur)** memiliki rata-rata peminjaman tertinggi
5. **Total 2012 tumbuh ~70% YoY** dibanding 2011

---

## 📦 Dataset
- **Sumber**: [UCI Machine Learning Repository – Bike Sharing Dataset](https://archive.ics.uci.edu/ml/datasets/bike+sharing+dataset)
- **Periode**: 1 Januari 2011 – 31 Desember 2012
- **day.csv**: 731 baris × 16 kolom (agregasi harian)
- **hour.csv**: 17.379 baris × 17 kolom (data per jam)

---

## 🛠️ Deploy ke Streamlit Cloud
1. Push semua file ke GitHub repository
2. Login ke [share.streamlit.io](https://share.streamlit.io)
3. Klik **New app** → pilih repo, branch, dan set main file: `dashboard.py`
4. Klik **Deploy**
