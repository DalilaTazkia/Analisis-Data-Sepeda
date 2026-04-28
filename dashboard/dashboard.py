"""
 Bike Sharing Dashboard

"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import streamlit as st

warnings.filterwarnings("ignore")
sns.set_theme(style="whitegrid")

# ──────────────────────────────────────────────────────────────────────────────
# KONFIGURASI HALAMAN
# ──────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────────────────────
# CSS
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main-header {
    background: linear-gradient(135deg, #0D47A1 0%, #1976D2 60%, #42A5F5 100%);
    padding: 2rem 2.5rem;
    border-radius: 16px;
    color: white;
    margin-bottom: 1.5rem;
    box-shadow: 0 6px 24px rgba(13,71,161,0.25);
}
.main-header h1 {
    margin: 0 0 0.3rem 0;
    font-size: 2rem;
    font-weight: 700;
    letter-spacing: -0.5px;
}
.main-header p {
    margin: 0;
    font-size: 0.95rem;
    opacity: 0.88;
}

.metric-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    border-left: 5px solid #1976D2;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    margin-bottom: 0.6rem;
}
.metric-card .mc-label {
    color: #607D8B;
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.6px;
    margin-bottom: 0.25rem;
}
.metric-card .mc-value {
    color: #0D47A1;
    font-size: 1.75rem;
    font-weight: 700;
    line-height: 1.1;
}
.metric-card .mc-delta        { font-size: 0.78rem; color: #546E7A; margin-top: 0.2rem; }
.metric-card .mc-delta.green  { color: #2E7D32; font-weight: 600; }

.sec-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #0D47A1;
    padding-bottom: 0.35rem;
    border-bottom: 2.5px solid #BBDEFB;
    margin: 1rem 0 0.75rem 0;
}

.ibox {
    border-radius: 0 10px 10px 0;
    padding: 0.75rem 1.1rem;
    margin: 0.6rem 0;
    font-size: 0.88rem;
    line-height: 1.55;
    border-left: 4px solid;
}
.ibox.blue  { background:#E3F2FD; border-color:#1976D2; color:#0D2D6E; }
.ibox.green { background:#E8F5E9; border-color:#388E3C; color:#1B5E20; }
.ibox.amber { background:#FFF8E1; border-color:#F9A825; color:#4E342E; }
.ibox.red   { background:#FFEBEE; border-color:#C62828; color:#7B0000; }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# KONSTANTA
# ──────────────────────────────────────────────────────────────────────────────
SEASON_ORDER   = ["Spring", "Summer", "Fall", "Winter"]
SEASON_COLORS  = ["#81C784", "#FFB74D", "#EF5350", "#64B5F6"]
WEATHER_ORDER  = ["Cerah/Berawan Tipis", "Berkabut/Berawan",
                  "Hujan/Salju Ringan", "Hujan Lebat/Es"]
WEATHER_COLORS = ["#4CAF50", "#FF9800", "#F44336", "#9C27B0"]
WDAY_NAMES     = ["Minggu","Senin","Selasa","Rabu","Kamis","Jumat","Sabtu"]
MONTH_NAMES    = ["Jan","Feb","Mar","Apr","Mei","Jun",
                  "Jul","Agu","Sep","Okt","Nov","Des"]
CORR_COLS      = ["temp_c","atemp_c","hum_pct","wind_kph",
                  "cnt","casual","registered"]


# ──────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ──────────────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    BASE = os.path.dirname(os.path.abspath(__file__))
    day  = pd.read_csv(os.path.join(BASE, "day_clean.csv"))
    hour = pd.read_csv(os.path.join(BASE, "hour_clean.csv"))

    for df in [day, hour]:
        df["dteday"]     = pd.to_datetime(df["dteday"])
        # year_label di CSV berupa int (2011/2012) → konversi ke string
        df["year_label"] = df["year_label"].astype(str)

    # Clustering permintaan harian (binning manual)
    bins   = [0, 1500, 3000, 4500, 6000, 9000]
    labels = ["Sangat Rendah", "Rendah", "Sedang", "Tinggi", "Sangat Tinggi"]
    day["demand_cluster"] = pd.cut(day["cnt"], bins=bins, labels=labels)

    return day, hour


df_day, df_hour = load_data()


# ──────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚲 Bike Sharing")
    st.caption("Dalila Tazkia")
    st.divider()
    st.markdown("### Filter Data")

    sel_years = st.multiselect(
        "Tahun", options=["2011", "2012"], default=["2011", "2012"])

    sel_seasons = st.multiselect(
        "Musim", options=SEASON_ORDER, default=SEASON_ORDER)

    avail_weather = df_day["weather_label"].dropna().unique().tolist()
    sel_weather   = st.multiselect(
        "Kondisi Cuaca", options=avail_weather, default=avail_weather)

    sel_daytype = st.radio(
        "Tipe Hari",
        ["Semua", "Hari Kerja", "Hari Libur/Akhir Pekan"],
        index=0)

    st.divider()
    st.caption("Dataset: UCI Bike Sharing 2011–2012")


# ──────────────────────────────────────────────────────────────────────────────
# FILTER
# ──────────────────────────────────────────────────────────────────────────────
def apply_filter(df):
    m = (
        df["year_label"].isin(sel_years) &
        df["season_label"].isin(sel_seasons) &
        df["weather_label"].isin(sel_weather)
    )
    if sel_daytype != "Semua":
        m &= (df["day_type"] == sel_daytype)
    return df[m].copy()


fd = apply_filter(df_day)
fh = apply_filter(df_hour)

if fd.empty or fh.empty:
    st.warning("⚠️ Tidak ada data untuk kombinasi filter yang dipilih. "
               "Silakan ubah filter di sidebar.")
    st.stop()


# ──────────────────────────────────────────────────────────────────────────────
# HEADER
# ──────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>Bike Sharing Analytics Dashboard</h1>
  <p>Analisis Pola Peminjaman & Faktor Cuaca</p>
</div>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# KPI
# ──────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="sec-title">Key Performance Indicators</div>',
            unsafe_allow_html=True)

total   = int(fd["cnt"].sum())
avg_d   = fd["cnt"].mean()
cas     = int(fd["casual"].sum())
reg     = int(fd["registered"].sum())
peak_v  = int(fd["cnt"].max())
peak_dt = fd.loc[fd["cnt"].idxmax(), "dteday"].strftime("%d %b %Y")
pct_cas = f"{cas/total*100:.1f}% dari total" if total else "–"
pct_reg = f"{reg/total*100:.1f}% dari total" if total else "–"

kpis = [
    ("Total Peminjaman",   f"{total:,}",      "Periode terpilih", ""),
    ("Rata-rata Harian",   f"{avg_d:,.0f}",   "Per hari",         ""),
    ("Pengguna Kasual",    f"{cas:,}",          pct_cas,           "green"),
    ("Pengguna Terdaftar", f"{reg:,}",          pct_reg,           "green"),
    ("Puncak Harian",      f"{peak_v:,}",       peak_dt,           ""),
]

for col, (lbl, val, dlt, cls) in zip(st.columns(5), kpis):
    with col:
        st.markdown(f"""
        <div class="metric-card">
          <div class="mc-label">{lbl}</div>
          <div class="mc-value">{val}</div>
          <div class="mc-delta {cls}">{dlt}</div>
        </div>""", unsafe_allow_html=True)

st.divider()


# ──────────────────────────────────────────────────────────────────────────────
# TABS
# ──────────────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "⏰ Pola Per Jam",
    "🌤️ Cuaca & Musim",
    "📈 Tren & Clustering",
    "🔗 Korelasi",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 – POLA PER JAM
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="sec-title">Pertanyaan 1 – Pola Peminjaman Per Jam</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="ibox blue">
    📌 <b>Pertanyaan Bisnis:</b> Bagaimana pola rata-rata peminjaman per jam
    berdasarkan tipe hari (hari kerja vs. hari libur/akhir pekan) sepanjang
    2011–2012, dan pada jam berapa puncak peminjaman terjadi?
    </div>""", unsafe_allow_html=True)

    # Data
    hourly = (fh.groupby(["hr", "day_type"])["cnt"]
              .mean().reset_index(name="avg_cnt"))
    hourly_piv = (hourly
                  .pivot(index="hr", columns="day_type", values="avg_cnt")
                  .reindex(columns=["Hari Kerja", "Hari Libur/Akhir Pekan"]))

    col_l, col_r = st.columns([3, 2])

    with col_l:
        DT_COLORS = {"Hari Kerja": "#1565C0",
                     "Hari Libur/Akhir Pekan": "#E65100"}
        fig, ax = plt.subplots(figsize=(8, 4.5))

        for dt, color in DT_COLORS.items():
            if dt not in hourly_piv.columns:
                continue
            s = hourly_piv[dt].dropna()
            if s.empty:
                continue
            ax.plot(s.index, s.values,
                    marker="o", ms=4.5, lw=2.5,
                    color=color, label=dt, zorder=3)
            pk_hr  = int(s.idxmax())
            pk_val = s.max()
            off_x  = 1.5 if dt == "Hari Kerja" else -4.5
            ax.annotate(
                f"Puncak\n{pk_hr:02d}:00\n({pk_val:.0f})",
                xy=(pk_hr, pk_val),
                xytext=(pk_hr + off_x, pk_val + 18),
                fontsize=8, color=color,
                arrowprops=dict(arrowstyle="->", color=color, lw=1.2))

        ax.axvspan( 7,  9, alpha=0.07, color="#1565C0", zorder=0)
        ax.axvspan(16, 19, alpha=0.07, color="#1565C0", zorder=0)
        ax.set_xlabel("Jam dalam Sehari", fontsize=11)
        ax.set_ylabel("Rata-rata Peminjaman", fontsize=11)
        ax.set_title("Pola Rata-rata Peminjaman Per Jam",
                     fontsize=12, fontweight="bold")
        ax.set_xticks(range(0, 24))
        ax.set_xlim(-0.5, 23.5)
        ax.legend(fontsize=9, loc="upper left")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col_r:
        st.markdown('<div class="sec-title">Jam Puncak & Terendah</div>',
                    unsafe_allow_html=True)
        for dt, cls in [("Hari Kerja", "green"),
                        ("Hari Libur/Akhir Pekan", "amber")]:
            if dt in hourly_piv.columns:
                s = hourly_piv[dt].dropna()
                if not s.empty:
                    st.markdown(f"""
                    <div class="ibox {cls}">
                    <b>{dt}</b><br>
                    🔺 Puncak  : <b>{int(s.idxmax()):02d}:00</b> →
                    <b>{s.max():.0f}</b> peminjaman<br>
                    🔻 Terendah: <b>{int(s.idxmin()):02d}:00</b> →
                    <b>{s.min():.0f}</b> peminjaman
                    </div>""", unsafe_allow_html=True)

        st.markdown('<div class="sec-title">Rata-rata per Periode</div>',
                    unsafe_allow_html=True)

        def jam_kat(hr):
            if   6 <= hr <= 9:   return "🌅 Pagi (06–09)"
            elif 10 <= hr <= 15: return "☀️ Siang (10–15)"
            elif 16 <= hr <= 20: return "🌆 Sore (16–20)"
            else:                return "🌙 Malam"

        tmp = fh.copy()
        tmp["period"] = tmp["hr"].apply(jam_kat)
        tbl = (tmp.groupby(["period", "day_type"])["cnt"]
               .mean().round(1).unstack().fillna(0).reset_index())
        st.dataframe(tbl, use_container_width=True, hide_index=True)

    # Heatmap
    st.markdown("---")
    st.markdown("#### Heatmap: Rata-rata Peminjaman per Jam × Hari dalam Minggu")

    hm_raw = (fh.groupby(["weekday", "hr"])["cnt"]
              .mean().unstack())
    hm = (hm_raw
          .reindex(index=range(7), columns=range(24))
          .fillna(0))
    hm.index = WDAY_NAMES

    fig2, ax2 = plt.subplots(figsize=(14, 4))
    sns.heatmap(
        hm, ax=ax2,
        cmap="YlOrRd", vmin=0,
        linewidths=0.2, linecolor="white",
        cbar_kws={"label": "Rata-rata Peminjaman", "shrink": 0.9})
    ax2.set_xlabel("Jam", fontsize=11)
    ax2.set_ylabel("")
    ax2.set_title("Heatmap Peminjaman per Jam × Hari dalam Minggu",
                  fontsize=12, fontweight="bold")
    ax2.tick_params(axis="x", labelsize=9, rotation=0)
    ax2.tick_params(axis="y", labelsize=10, rotation=0)
    fig2.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)

    st.markdown("""
    <div class="ibox blue">
    💡 <b>Insight:</b> Hari kerja menunjukkan pola <b>bimodal</b> — puncak
    pagi (08:00) dan sore (17:00–18:00) mencerminkan pola <i>commuter</i>.
    Hari libur/akhir pekan berpola <b>unimodal</b> dengan puncak tengah hari
    (11:00–13:00) mencerminkan aktivitas rekreasi.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 – CUACA & MUSIM
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="sec-title">Pertanyaan 2 – Pengaruh Cuaca & Musim</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="ibox blue">
    📌 <b>Pertanyaan Bisnis:</b> Bagaimana pengaruh kondisi cuaca dan musim
    terhadap total peminjaman harian, dan kondisi mana yang paling signifikan
    menurunkan peminjaman?
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Rata-rata Peminjaman per Kondisi Cuaca")

        w_avg = (fd.groupby("weather_label")["cnt"]
                 .mean()
                 .reindex(WEATHER_ORDER)
                 .dropna()
                 .reset_index(name="avg"))

        fig3, ax3 = plt.subplots(figsize=(7, 4.5))
        bars = ax3.bar(
            range(len(w_avg)), w_avg["avg"],
            color=WEATHER_COLORS[:len(w_avg)],
            edgecolor="white", linewidth=1.2, width=0.6)
        for b, v in zip(bars, w_avg["avg"]):
            ax3.text(b.get_x() + b.get_width() / 2,
                     b.get_height() + 50,
                     f"{v:,.0f}",
                     ha="center", fontsize=10.5, fontweight="bold")
        ax3.set_xticks(range(len(w_avg)))
        ax3.set_xticklabels(w_avg["weather_label"], fontsize=9.5)
        ax3.set_ylabel("Rata-rata Peminjaman / Hari", fontsize=11)
        ax3.set_title("Rata-rata per Kondisi Cuaca",
                      fontsize=12, fontweight="bold")
        ax3.set_ylim(0, w_avg["avg"].max() * 1.22)
        ax3.grid(axis="y", alpha=0.35)
        fig3.tight_layout()
        st.pyplot(fig3)
        plt.close(fig3)

        w_tbl = (fd.groupby("weather_label")["cnt"]
                 .agg(Rata_rata="mean", Median="median", Jumlah_Hari="count")
                 .round(1)
                 .reindex(WEATHER_ORDER)
                 .dropna())
        st.dataframe(w_tbl, use_container_width=True)

    with col2:
        st.markdown("####  Distribusi Peminjaman per Musim")

        avail_s  = [s for s in SEASON_ORDER if s in fd["season_label"].values]
        s_data   = [fd[fd["season_label"] == s]["cnt"].values for s in avail_s]
        s_colors = [SEASON_COLORS[SEASON_ORDER.index(s)] for s in avail_s]

        fig4, ax4 = plt.subplots(figsize=(7, 4.5))
        if s_data and any(len(d) > 0 for d in s_data):
            bp = ax4.boxplot(
                s_data, patch_artist=True,
                medianprops=dict(color="black", linewidth=2.5),
                whiskerprops=dict(linewidth=1.5),
                capprops=dict(linewidth=1.5))
            for patch, color in zip(bp["boxes"], s_colors):
                patch.set_facecolor(color)
                patch.set_alpha(0.75)
            np.random.seed(42)
            for i, (s, color) in enumerate(zip(avail_s, s_colors), start=1):
                y = fd[fd["season_label"] == s]["cnt"]
                x = np.random.normal(i, 0.07, size=len(y))
                ax4.scatter(x, y, alpha=0.22, s=12,
                            color=color, edgecolors="none")
        ax4.set_xticks(range(1, len(avail_s) + 1))
        ax4.set_xticklabels(avail_s, fontsize=11)
        ax4.set_ylabel("Jumlah Peminjaman Harian", fontsize=11)
        ax4.set_title("Distribusi per Musim (Boxplot)",
                      fontsize=12, fontweight="bold")
        ax4.grid(axis="y", alpha=0.35)
        fig4.tight_layout()
        st.pyplot(fig4)
        plt.close(fig4)

        s_tbl = (fd.groupby("season_label")["cnt"]
                 .agg(Rata_rata="mean", Median="median",
                      Min="min", Max="max", Hari="count")
                 .round(1)
                 .reindex(avail_s))
        st.dataframe(s_tbl, use_container_width=True)

    # Heatmap silang
    st.markdown("---")
    st.markdown("#### Heatmap Silang: Musim × Kondisi Cuaca")

    cross = (fd.groupby(["season_label", "weather_label"])["cnt"]
             .mean().unstack()
             .reindex(index=avail_s, columns=WEATHER_ORDER)
             .fillna(0)
             .round(0))

    fig5, ax5 = plt.subplots(figsize=(10, 3.8))
    sns.heatmap(
        cross, ax=ax5,
        annot=True, fmt=".0f",
        cmap="RdYlGn", vmin=0,
        linewidths=0.5, linecolor="white",
        cbar_kws={"label": "Rata-rata Peminjaman", "shrink": 0.85})
    ax5.set_title("Rata-rata Peminjaman Harian (Musim × Cuaca)",
                  fontsize=12, fontweight="bold")
    ax5.set_xlabel("")
    ax5.set_ylabel("")
    ax5.tick_params(axis="x", rotation=15, labelsize=10)
    ax5.tick_params(axis="y", rotation=0,  labelsize=10)
    fig5.tight_layout()
    st.pyplot(fig5)
    plt.close(fig5)

    if len(w_avg) >= 2:
        top  = w_avg.iloc[0]
        bot  = w_avg.iloc[-1]
        drop = (top["avg"] - bot["avg"]) / top["avg"] * 100
        st.markdown(f"""
        <div class="ibox amber">
        ⚠️ <b>Insight:</b> Peminjaman turun <b>{drop:.1f}%</b> dari kondisi
        terbaik (<b>{top.weather_label}</b>: {top.avg:,.0f}/hari) ke kondisi
        terburuk (<b>{bot.weather_label}</b>: {bot.avg:,.0f}/hari).
        Strategi promosi saat cuaca buruk sangat direkomendasikan.
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 – TREN & CLUSTERING
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="sec-title">Tren Bulanan & Clustering Permintaan</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Tren Peminjaman Bulanan per Tahun")
        monthly = (fd.groupby(["year_label", "mnth"])["cnt"]
                   .sum().reset_index())

        fig6, ax6 = plt.subplots(figsize=(7, 4.5))
        for yr, color, marker in [("2011","#5C6BC0","o"), ("2012","#EF5350","s")]:
            sub = monthly[monthly["year_label"] == yr].sort_values("mnth")
            if sub.empty:
                continue
            ax6.plot(sub["mnth"], sub["cnt"],
                     color=color, marker=marker,
                     ms=7, lw=2.5, label=yr, zorder=3)
            ax6.fill_between(sub["mnth"], sub["cnt"],
                             alpha=0.10, color=color)

        ax6.set_xticks(range(1, 13))
        ax6.set_xticklabels(MONTH_NAMES, fontsize=9.5)
        ax6.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}K"))
        ax6.set_ylabel("Total Peminjaman", fontsize=11)
        ax6.set_xlabel("Bulan", fontsize=11)
        ax6.set_title("Tren Bulanan (2011 vs. 2012)",
                      fontsize=12, fontweight="bold")
        ax6.legend(title="Tahun", fontsize=10)
        ax6.grid(alpha=0.35)
        fig6.tight_layout()
        st.pyplot(fig6)
        plt.close(fig6)

        if {"2011","2012"}.issubset(set(sel_years)):
            t11 = fd[fd["year_label"] == "2011"]["cnt"].sum()
            t12 = fd[fd["year_label"] == "2012"]["cnt"].sum()
            if t11 > 0:
                yoy = (t12 - t11) / t11 * 100
                st.markdown(f"""
                <div class="ibox green">
                📈 <b>YoY Growth:</b> Total peminjaman 2012 tumbuh
                <b>{yoy:.1f}%</b> dibanding 2011
                ({t11:,.0f} → {t12:,.0f}).
                </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("#### Clustering Permintaan Harian")
        cc = fd["demand_cluster"].value_counts().sort_index()
        clust_colors = ["#EF9A9A","#FFCC80","#FFF176","#A5D6A7","#80DEEA"]

        fig7, ax7 = plt.subplots(figsize=(6.5, 4.5))
        if not cc.empty:
            wedges, texts, autotexts = ax7.pie(
                cc.values,
                labels=cc.index,
                colors=clust_colors[:len(cc)],
                autopct="%1.1f%%",
                startangle=90,
                pctdistance=0.80,
                wedgeprops=dict(width=0.55, edgecolor="white", lw=2))
            for t  in texts:     t.set_fontsize(9)
            for at in autotexts: at.set_fontsize(8.5)
            ax7.legend(
                wedges,
                [f"{k}: {v} hari" for k, v in zip(cc.index, cc.values)],
                loc="lower center", bbox_to_anchor=(0.5, -0.14),
                ncol=2, fontsize=8.5)
        ax7.set_title("Proporsi Cluster Permintaan Harian",
                      fontsize=12, fontweight="bold")
        fig7.tight_layout()
        st.pyplot(fig7)
        plt.close(fig7)

        c_tbl = (fd.groupby("demand_cluster", observed=True)
                 .agg(Hari=("cnt","count"),
                      Avg_Peminjaman=("cnt","mean"),
                      Avg_Suhu=("temp_c","mean"),
                      Pct_Workday=("workingday","mean"))
                 .round(2))
        c_tbl["Pct_Workday"] = (c_tbl["Pct_Workday"] * 100).round(1)
        c_tbl.columns = ["Hari","Avg Peminjaman","Avg Suhu(°C)","% Hari Kerja"]
        st.dataframe(c_tbl, use_container_width=True)

    # Stacked bar
    st.markdown("---")
    st.markdown("####  Komposisi Kasual vs. Terdaftar per Bulan")
    um = (fd.groupby(["mnth","year_label"])[["casual","registered"]]
          .sum().reset_index())

    fig8, ax8 = plt.subplots(figsize=(13, 4.5))
    w = 0.35
    for yr, cc_, cr, off in [
        ("2011","#90CAF9","#1565C0",-w/2),
        ("2012","#FFCC80","#E65100", w/2),
    ]:
        sub = um[um["year_label"] == yr].sort_values("mnth")
        if sub.empty:
            continue
        x = sub["mnth"].values + off
        ax8.bar(x, sub["casual"],     width=w*0.92, color=cc_,
                label=f"Kasual {yr}")
        ax8.bar(x, sub["registered"], width=w*0.92, color=cr,
                bottom=sub["casual"], label=f"Terdaftar {yr}")

    ax8.set_xticks(range(1, 13))
    ax8.set_xticklabels(MONTH_NAMES, fontsize=10)
    ax8.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x, _: f"{x/1000:.0f}K"))
    ax8.set_ylabel("Total Peminjaman", fontsize=11)
    ax8.set_title("Komposisi Kasual vs. Terdaftar per Bulan",
                  fontsize=12, fontweight="bold")
    ax8.legend(fontsize=9, ncol=4, loc="upper left")
    ax8.grid(axis="y", alpha=0.35)
    fig8.tight_layout()
    st.pyplot(fig8)
    plt.close(fig8)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 – KORELASI
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="sec-title">Analisis Korelasi Faktor Lingkungan</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Suhu vs. Jumlah Peminjaman")
        fig9, ax9 = plt.subplots(figsize=(7, 5))
        for season, color in zip(SEASON_ORDER, SEASON_COLORS):
            sub = fd[fd["season_label"] == season]
            if sub.empty:
                continue
            ax9.scatter(sub["temp_c"], sub["cnt"],
                        c=color, alpha=0.55, s=28,
                        label=season, edgecolors="none")

        if len(fd) > 1:
            z    = np.polyfit(fd["temp_c"], fd["cnt"], 1)
            x_ln = np.linspace(fd["temp_c"].min(), fd["temp_c"].max(), 100)
            ax9.plot(x_ln, np.poly1d(z)(x_ln),
                     "k--", lw=2, label="Tren Linear")
            r = fd[["temp_c","cnt"]].corr().iloc[0, 1]
            ax9.text(0.05, 0.93, f"r = {r:.3f}",
                     transform=ax9.transAxes, fontsize=11,
                     bbox=dict(boxstyle="round,pad=0.35",
                               facecolor="wheat", alpha=0.9))

        ax9.set_xlabel("Suhu Aktual (°C)", fontsize=11)
        ax9.set_ylabel("Peminjaman Harian", fontsize=11)
        ax9.set_title("Suhu vs. Jumlah Peminjaman (per Musim)",
                      fontsize=12, fontweight="bold")
        ax9.legend(fontsize=9, loc="upper left")
        ax9.grid(alpha=0.3)
        fig9.tight_layout()
        st.pyplot(fig9)
        plt.close(fig9)

    with col2:
        st.markdown("#### Heatmap Korelasi")
        corr_df = fd[CORR_COLS].corr()

        fig10, ax10 = plt.subplots(figsize=(7, 5))
        sns.heatmap(
            corr_df, ax=ax10,
            annot=True, fmt=".2f",
            cmap="RdYlGn", center=0, vmin=-1, vmax=1,
            linewidths=0.5, linecolor="white",
            square=True,
            cbar_kws={"label": "Korelasi Pearson", "shrink": 0.82})
        ax10.set_title("Heatmap Korelasi Pearson",
                       fontsize=12, fontweight="bold")
        ax10.tick_params(axis="x", rotation=30, labelsize=9)
        ax10.tick_params(axis="y", rotation=0,  labelsize=9)
        fig10.tight_layout()
        st.pyplot(fig10)
        plt.close(fig10)

    # Bar chart korelasi
    st.markdown("---")
    st.markdown("#### Kekuatan Korelasi dengan Jumlah Peminjaman (cnt)")

    corr_cnt = (fd[CORR_COLS].corr()["cnt"]
                .drop("cnt")
                .sort_values(key=abs, ascending=False))
    bar_colors = ["#4CAF50" if v > 0 else "#F44336" for v in corr_cnt.values]

    fig11, ax11 = plt.subplots(figsize=(10, 3.5))
    bars = ax11.barh(corr_cnt.index, corr_cnt.values,
                     color=bar_colors, edgecolor="white", height=0.55)
    for b, v in zip(bars, corr_cnt.values):
        ax11.text(
            v + (0.01 if v >= 0 else -0.01),
            b.get_y() + b.get_height() / 2,
            f"{v:.3f}", va="center",
            ha="left" if v >= 0 else "right",
            fontsize=10, fontweight="bold")
    ax11.axvline(0, color="black", lw=1.2)
    ax11.set_xlabel("Nilai Korelasi Pearson", fontsize=11)
    ax11.set_title("Korelasi Variabel Lingkungan dengan cnt",
                   fontsize=12, fontweight="bold")
    ax11.set_xlim(-0.6, 1.1)
    ax11.grid(axis="x", alpha=0.3)
    fig11.tight_layout()
    st.pyplot(fig11)
    plt.close(fig11)

    r_temp = float(corr_cnt.get("temp_c", 0))
    r_hum  = float(corr_cnt.get("hum_pct", 0))
    r_wind = float(corr_cnt.get("wind_kph", 0))
    st.markdown(f"""
    <div class="ibox blue">
    🔍 <b>Temuan Korelasi Utama:</b><br>
    • <b>Suhu (r = {r_temp:.3f})</b> – korelasi positif kuat:
      semakin hangat → semakin banyak peminjaman<br>
    • <b>Kelembaban (r = {r_hum:.3f})</b> – korelasi negatif:
      hari lembab cenderung lebih sedikit peminjaman<br>
    • <b>Kecepatan Angin (r = {r_wind:.3f})</b> – korelasi negatif:
      angin kencang mengurangi minat bersepeda
    </div>""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# FOOTER
# ──────────────────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center;color:#90A4AE;font-size:0.82rem;padding:0.8rem 0">
    <b>Bike Sharing Analytics Dashboard</b> &nbsp;·&nbsp;
    Capital Bikeshare Washington D.C. 2011–2012 &nbsp;·&nbsp;
    Built with Streamlit & Matplotlib
</div>
""", unsafe_allow_html=True)