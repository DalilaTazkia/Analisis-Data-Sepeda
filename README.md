# Analisis Data Peminjaman Sepeda – Bike Sharing Dataset

**Nama:** Dalila Tazkia

**Dataset:** Bike Sharing Dataset

**Sumber:** [https://www.kaggle.com/datasets/lakshmi25npathi/bike-sharing-dataset](https://www.kaggle.com/datasets/lakshmi25npathi/bike-sharing-dataset)

---

## Deskripsi Proyek

Proyek analisis data ini mengeksplorasi dataset Capital Bikeshare Washington D.C. (2011–2012) untuk menjawab dua pertanyaan bisnis berbasis metode SMART:

1. Pola peminjaman per jam – Bagaimana pola rata-rata peminjaman per jam berdasarkan tipe hari (hari kerja vs. hari libur/akhir pekan) sepanjang 2011–2012?
2. Pengaruh cuaca dan musim – Bagaimana pengaruh kondisi cuaca dan musim terhadap total peminjaman harian, serta kondisi mana yang paling menurunkan peminjaman?

---

## Struktur Repositori

```
Analisis-Data-Sepeda/
│
├── dashboard/
│   ├── dashboard.py
│   ├── day_clean.csv
│   └── hour_clean.csv
│
├── data/
│   ├── day.csv
│   └── hour.csv
│
├── notebook_Analisis_Data_DalilaTazkia.ipynb
├── requirements.txt
└── README.md
```

---

## Cara Menjalankan

### 1. Clone Repositori

```bash
git clone https://github.com/DalilaTazkia/Analisis-Data-Sepeda.git
cd Analisis-Data-Sepeda
```

### 2. Install Dependensi

```bash
pip install -r requirements.txt
```

### 3. Jalankan Dashboard

```bash
cd dashboard
streamlit run dashboard.py
```

Pastikan file `day_clean.csv` dan `hour_clean.csv` berada di dalam folder `dashboard/`.

### 4. Buka Notebook

```bash
jupyter notebook notebook_Analisis_Data_DalilaTazkia.ipynb
```

---

## Fitur Dashboard

Dashboard dibangun menggunakan Streamlit dan terdiri dari empat bagian utama:

* Pola Per Jam: Visualisasi pola peminjaman per jam dalam bentuk line chart dan heatmap jam terhadap hari dalam minggu
* Cuaca dan Musim: Analisis pengaruh kondisi cuaca dan musim menggunakan bar chart, boxplot, dan heatmap
* Tren dan Clustering: Perbandingan tren bulanan tahun 2011 dan 2012, serta segmentasi permintaan
* Korelasi: Analisis hubungan antar variabel menggunakan scatter plot dan korelasi Pearson

Dashboard juga menyediakan filter interaktif berdasarkan tahun, musim, kondisi cuaca, dan tipe hari.

---

## Kesimpulan Utama

1. Hari kerja menunjukkan pola bimodal dengan puncak pada pukul 08.00 dan 17.00, yang mencerminkan pola pengguna komuter
2. Hari libur dan akhir pekan menunjukkan pola unimodal dengan puncak pada pukul 11.00 hingga 13.00, yang cenderung bersifat rekreasi
3. Cuaca cerah menghasilkan rata-rata sekitar 4.877 peminjaman per hari, sedangkan kondisi hujan menurunkan hingga sekitar 1.803 peminjaman per hari
4. Musim gugur memiliki rata-rata peminjaman tertinggi dibandingkan musim lainnya
5. Terjadi peningkatan total peminjaman sekitar 70 persen pada tahun 2012 dibandingkan tahun 2011

---

## Dataset

Dataset yang digunakan berasal dari Kaggle dan merupakan data Capital Bikeshare Washington D.C. untuk periode 2011–2012.

| File                       | Deskripsi            | Baris  | Kolom |
| -------------------------- | -------------------- | ------ | ----- |
| `data/day.csv`             | Data harian (raw)    | 731    | 16    |
| `data/hour.csv`            | Data per jam (raw)   | 17.379 | 17    |
| `dashboard/day_clean.csv`  | Data harian (clean)  | 731    | 24    |
| `dashboard/hour_clean.csv` | Data per jam (clean) | 17.379 | 25    |

---

## Deploy Streamlit Cloud

Dashboard dapat dijalankan secara online melalui Streamlit Cloud:

1. Login ke [https://share.streamlit.io](https://share.streamlit.io)
2. Klik New app dan pilih repository DalilaTazkia/Analisis-Data-Sepeda
3. Atur Main file path ke `dashboard/dashboard.py`
4. Klik Deploy

---
