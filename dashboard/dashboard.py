"""
Bike Sharing Dashboard – Streamlit
Jalankan: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

# ─── Konfigurasi Halaman ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1565C0 0%, #42A5F5 100%);
        padding: 2rem 2.5rem;
        border-radius: 14px;
        color: white;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p  { margin: 0.4rem 0 0; opacity: 0.90; }

    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        border-left: 5px solid #42A5F5;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
        margin-bottom: 0.5rem;
    }
    .metric-card .label { color: #666; font-size: 0.82rem; font-weight: 600;
                          text-transform: uppercase; }
    .metric-card .value { color: #1565C0; font-size: 1.9rem; font-weight: 700;
                          margin: 0.2rem 0; }
    .metric-card .delta { font-size: 0.82rem; }
    .metric-card .delta.pos { color: #2E7D32; }

    .section-title {
        font-size: 1.2rem; font-weight: 700; color: #1565C0;
        border-bottom: 2px solid #E3F2FD;
        padding-bottom: 0.4rem; margin: 1.2rem 0 0.8rem;
    }
    .insight-box {
        background: #E3F2FD; border-left: 4px solid #1565C0;
        border-radius: 0 8px 8px 0;
        padding: 0.8rem 1.2rem; margin: 0.6rem 0;
        font-size: 0.92rem; color: #1A237E;
    }
    .insight-box.warning  { background: #FFF8E1; border-color: #F57F17; color: #4E342E; }
    .insight-box.success  { background: #E8F5E9; border-color: #2E7D32; color: #1B5E20; }
</style>
""", unsafe_allow_html=True)


# ─── Load & Preprocess Data ───────────────────────────────────────────────────
@st.cache_data
def load_data():
    df_day  = pd.read_csv("day_clean.csv")
    df_hour = pd.read_csv("hour_clean.csv")

    def enrich(df):
        df = df.copy()
        df["dteday"]        = pd.to_datetime(df["dteday"])
        df["season_label"]  = df["season"].map(
            {1:"Spring", 2:"Summer", 3:"Fall", 4:"Winter"})
        df["weather_label"] = df["weathersit"].map(
            {1:"Cerah/Berawan Tipis", 2:"Berkabut/Berawan",
             3:"Hujan/Salju Ringan",  4:"Hujan Lebat/Es"})
        df["year_label"]    = df["yr"].map({0:"2011", 1:"2012"})
        df["day_type"]      = df.apply(
            lambda r: "Hari Libur/Akhir Pekan"
                      if (r["holiday"] == 1 or r["workingday"] == 0)
                      else "Hari Kerja", axis=1)
        df["temp_c"]    = df["temp"]      * 41
        df["atemp_c"]   = df["atemp"]     * 50
        df["hum_pct"]   = df["hum"]       * 100
        df["wind_kph"]  = df["windspeed"] * 67
        return df

    df_day  = enrich(df_day)
    df_hour = enrich(df_hour)

    # Clustering manual
    bins   = [0, 1500, 3000, 4500, 6000, 9000]
    labels = ["Sangat Rendah","Rendah","Sedang","Tinggi","Sangat Tinggi"]
    df_day["demand_cluster"] = pd.cut(df_day["cnt"], bins=bins, labels=labels)

    return df_day, df_hour


df_day, df_hour = load_data()


# ─── Sidebar Filter ───────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🚲 Bike Sharing")
    st.caption("Capital Bikeshare – Washington D.C.")
    st.divider()
    st.subheader("Filter Data")

    selected_years = st.multiselect(
        "Tahun", ["2011","2012"], default=["2011","2012"])

    all_seasons    = ["Spring","Summer","Fall","Winter"]
    selected_seasons = st.multiselect(
        "Musim", all_seasons, default=all_seasons)

    all_weather    = df_day["weather_label"].dropna().unique().tolist()
    selected_weather = st.multiselect(
        "Kondisi Cuaca", all_weather, default=all_weather)

    day_type_opt = st.radio(
        "Tipe Hari",
        ["Semua","Hari Kerja","Hari Libur/Akhir Pekan"],
        index=0)

    st.divider()
    st.caption("Dataset: UCI Bike Sharing (2011–2012)")


# ─── Terapkan Filter ──────────────────────────────────────────────────────────
def apply_filter(df, is_hour=False):
    mask = (
        df["year_label"].isin(selected_years) &
        df["season_label"].isin(selected_seasons) &
        df["weather_label"].isin(selected_weather)
    )
    if day_type_opt != "Semua":
        mask &= (df["day_type"] == day_type_opt)
    return df[mask]

fd  = apply_filter(df_day)
fh  = apply_filter(df_hour)


# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>🚲 Bike Sharing Analytics Dashboard</h1>
  <p>Capital Bikeshare Washington D.C. &nbsp;|&nbsp; 2011–2012 &nbsp;|&nbsp;
     Analisis Pola Peminjaman & Faktor Cuaca</p>
</div>
""", unsafe_allow_html=True)


# ─── KPI Cards ────────────────────────────────────────────────────────────────
st.markdown('<div class="section-title">Key Performance Indicators</div>',
            unsafe_allow_html=True)

total_cnt    = int(fd["cnt"].sum())
avg_daily    = fd["cnt"].mean()
total_casual = int(fd["casual"].sum())
total_reg    = int(fd["registered"].sum())
peak_val     = int(fd["cnt"].max()) if len(fd) else 0
peak_day     = (fd.loc[fd["cnt"].idxmax(), "dteday"].strftime("%d %b %Y")
                if len(fd) else "N/A")

kpi_data = [
    ("Total Peminjaman",   f"{total_cnt:,}",   "Periode terpilih"),
    ("Rata-rata Harian",   f"{avg_daily:,.0f}", "Per hari"),
    ("Pengguna Kasual",    f"{total_casual:,}",
     f"{total_casual/total_cnt*100:.1f}% dari total" if total_cnt else "0%"),
    ("Pengguna Terdaftar", f"{total_reg:,}",
     f"{total_reg/total_cnt*100:.1f}% dari total" if total_cnt else "0%"),
    ("Puncak Harian",      f"{peak_val:,}",    peak_day),
]

cols = st.columns(5)
for col, (label, val, delta) in zip(cols, kpi_data):
    with col:
        st.markdown(f"""
        <div class="metric-card">
          <div class="label">{label}</div>
          <div class="value">{val}</div>
          <div class="delta pos">{delta}</div>
        </div>""", unsafe_allow_html=True)

st.divider()


# ─── Tab Navigation ───────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "⏰ Pola Per Jam",
    "🌤️ Cuaca & Musim",
    "📈 Tren & Clustering",
    "🔗 Korelasi"
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Pola Per Jam
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown('<div class="section-title"> Pola Peminjaman Per Jam</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
    <b>Pertanyaan Bisnis 1:</b> Bagaimana pola rata-rata peminjaman per jam 
    berdasarkan tipe hari (hari kerja vs. hari libur/akhir pekan) sepanjang 2011–2012?
    </div>""", unsafe_allow_html=True)

    col_left, col_right = st.columns([3, 2])

    with col_left:
        # Hitung data
        hourly = (
            fh.groupby(["hr","day_type"])["cnt"]
            .mean().reset_index()
        )
        hourly_piv = hourly.pivot(index="hr", columns="day_type", values="cnt")

        fig, ax = plt.subplots(figsize=(8, 4.5))
        colors  = {"Hari Kerja":"#1565C0",
                   "Hari Libur/Akhir Pekan":"#E65100"}

        for dt, col in colors.items():
            sub = hourly[hourly["day_type"] == dt]
            if len(sub) == 0:
                continue
            ax.plot(sub["hr"], sub["cnt"],
                    marker="o", ms=4.5, lw=2.5,
                    color=col, label=dt)
            peak = sub.loc[sub["cnt"].idxmax()]
            off  = 1.5 if dt == "Hari Kerja" else -4
            ax.annotate(
                f"Puncak\n{int(peak.hr):02d}:00\n({peak.cnt:.0f})",
                xy=(peak.hr, peak.cnt),
                xytext=(peak.hr + off, peak.cnt + 18),
                fontsize=8, color=col,
                arrowprops=dict(arrowstyle="->", color=col, lw=1.2)
            )

        ax.axvspan( 7,  9, alpha=0.07, color="#1565C0")
        ax.axvspan(16, 19, alpha=0.07, color="#1565C0")
        ax.set_xlabel("Jam", fontsize=11)
        ax.set_ylabel("Rata-rata Peminjaman", fontsize=11)
        ax.set_title("Pola Rata-rata Peminjaman Per Jam", fontsize=12,
                     fontweight="bold")
        ax.set_xticks(range(0, 24))
        ax.legend(fontsize=9)
        ax.grid(alpha=0.35)
        plt.tight_layout()
        st.pyplot(fig)
        plt.close()

    with col_right:
        st.markdown('<div class="section-title">Jam Puncak</div>',
                    unsafe_allow_html=True)
        if len(hourly_piv.columns):
            for dt, color_str in [
                ("Hari Kerja", "success"),
                ("Hari Libur/Akhir Pekan", "warning")
            ]:
                if dt in hourly_piv.columns:
                    pk_hr  = hourly_piv[dt].idxmax()
                    pk_val = hourly_piv[dt].max()
                    st.markdown(f"""
                    <div class="insight-box {color_str}">
                    <b>{dt}</b><br>
                    Puncak: Jam <b>{int(pk_hr):02d}:00</b>
                    &nbsp;→&nbsp; rata-rata <b>{pk_val:.0f}</b> peminjaman
                    </div>""", unsafe_allow_html=True)

        # Tabel ringkasan per periode
        def jam_kat(hr):
            if   6 <= hr <= 9:   return "🌅 Pagi (06–09)"
            elif 10 <= hr <= 15: return "☀️ Siang (10–15)"
            elif 16 <= hr <= 20: return "🌆 Sore (16–20)"
            else:                return "🌙 Malam"

        fh2 = fh.copy()
        fh2["period"] = fh2["hr"].apply(jam_kat)
        tbl = (
            fh2.groupby(["period","day_type"])["cnt"]
            .mean().round(1).unstack().fillna(0).reset_index()
        )
        st.dataframe(tbl, use_container_width=True, hide_index=True)

    # Heatmap jam × hari dalam minggu
    st.markdown("---")
    st.markdown("#### Heatmap: Rata-rata Peminjaman per Jam × Hari")
    wday_names = ["Minggu","Senin","Selasa","Rabu","Kamis","Jumat","Sabtu"]
    hm = fh.groupby(["weekday","hr"])["cnt"].mean().unstack()
    hm.index = [wday_names[i] for i in hm.index]

    fig2, ax2 = plt.subplots(figsize=(14, 4))
    sns.heatmap(hm, ax=ax2, cmap="YlOrRd",
                linewidths=0.2, linecolor="white",
                cbar_kws={"label":"Rata-rata Peminjaman"})
    ax2.set_xlabel("Jam", fontsize=11)
    ax2.set_ylabel("Hari", fontsize=11)
    ax2.set_title("Heatmap Peminjaman per Jam × Hari dalam Minggu",
                  fontsize=12, fontweight="bold")
    ax2.tick_params(axis="x", labelsize=9, rotation=0)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close()

    st.markdown("""
    <div class="insight-box">
    <b>Insight:</b> Hari kerja menunjukkan pola <b>bimodal</b> (pagi & sore)
    → pola commuter. Hari libur menunjukkan pola <b>unimodal</b> (tengah hari)
    → aktivitas rekreasi. Slot tertinggi: Rabu–Jumat jam 08:00 & 17:00–18:00.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Cuaca & Musim
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-title"> Pengaruh Cuaca & Musim</div>',
                unsafe_allow_html=True)
    st.markdown("""
    <div class="insight-box">
    <b>Pertanyaan Bisnis 2:</b> Bagaimana pengaruh kondisi cuaca dan musim 
    terhadap total peminjaman harian, dan kondisi mana yang paling menurunkan peminjaman?
    </div>""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### Rata-rata Peminjaman per Kondisi Cuaca")
        w_avg = (
            fd.groupby("weather_label")["cnt"]
            .mean().sort_values(ascending=False).reset_index()
        )
        palette_w = ["#4CAF50","#FF9800","#F44336","#9C27B0"]
        fig3, ax3 = plt.subplots(figsize=(7, 4.5))
        bars = ax3.bar(range(len(w_avg)), w_avg["cnt"],
                       color=palette_w[:len(w_avg)],
                       edgecolor="white", lw=1.2, width=0.6)
        for b, v in zip(bars, w_avg["cnt"]):
            ax3.text(b.get_x() + b.get_width()/2,
                     b.get_height() + 50,
                     f"{v:,.0f}", ha="center",
                     fontsize=10.5, fontweight="bold")
        ax3.set_xticks(range(len(w_avg)))
        ax3.set_xticklabels(w_avg["weather_label"], fontsize=10)
        ax3.set_ylabel("Rata-rata Peminjaman / Hari", fontsize=11)
        ax3.set_title("Rata-rata per Kondisi Cuaca", fontsize=12, fontweight="bold")
        ax3.set_ylim(0, w_avg["cnt"].max() * 1.22)
        ax3.grid(axis="y", alpha=0.35)
        plt.tight_layout()
        st.pyplot(fig3)
        plt.close()

        # Tabel detail
        w_tbl = fd.groupby("weather_label")["cnt"].agg(
            ["mean","median","count"]).round(1)
        w_tbl.columns = ["Rata-rata","Median","Jumlah Hari"]
        st.dataframe(w_tbl.sort_values("Rata-rata", ascending=False),
                     use_container_width=True)

    with col2:
        st.markdown("#### Distribusi Peminjaman per Musim")
        season_order = ["Spring","Summer","Fall","Winter"]
        palette_s    = ["#81C784","#FFB74D","#EF5350","#64B5F6"]
        s_data = [fd[fd["season_label"]==s]["cnt"].values for s in season_order]

        fig4, ax4 = plt.subplots(figsize=(7, 4.5))
        bp = ax4.boxplot(s_data, patch_artist=True,
                         medianprops=dict(color="black", lw=2.5))
        for patch, col in zip(bp["boxes"], palette_s):
            patch.set_facecolor(col); patch.set_alpha(0.75)

        np.random.seed(42)
        for i, (s, col) in enumerate(zip(season_order, palette_s), start=1):
            y = fd[fd["season_label"]==s]["cnt"]
            x = np.random.normal(i, 0.07, len(y))
            ax4.scatter(x, y, alpha=0.22, s=12, color=col, edgecolors="none")

        ax4.set_xticklabels(season_order, fontsize=11)
        ax4.set_ylabel("Jumlah Peminjaman Harian", fontsize=11)
        ax4.set_title("Distribusi Peminjaman per Musim", fontsize=12,
                      fontweight="bold")
        ax4.grid(axis="y", alpha=0.35)
        plt.tight_layout()
        st.pyplot(fig4)
        plt.close()

        # Statistik musim
        s_tbl = (
            fd.groupby("season_label")["cnt"]
            .agg(["mean","median","min","max","count"]).round(1)
            .reindex(season_order)
        )
        s_tbl.columns = ["Rata-rata","Median","Min","Max","Hari"]
        st.dataframe(s_tbl, use_container_width=True)

    # Heatmap silang cuaca × musim
    st.markdown("---")
    st.markdown("#### Heatmap Silang: Musim × Kondisi Cuaca")
    cross = (
        fd.groupby(["season_label","weather_label"])["cnt"]
        .mean().unstack().round(0).reindex(season_order)
    )
    fig5, ax5 = plt.subplots(figsize=(10, 4))
    sns.heatmap(cross, ax=ax5, annot=True, fmt=".0f",
                cmap="RdYlGn", linewidths=0.5,
                cbar_kws={"label":"Rata-rata Peminjaman"})
    ax5.set_title("Rata-rata Peminjaman Harian (Musim × Cuaca)",
                  fontsize=12, fontweight="bold")
    ax5.tick_params(axis="x", rotation=15, labelsize=10)
    ax5.tick_params(axis="y", rotation=0,  labelsize=10)
    plt.tight_layout()
    st.pyplot(fig5)
    plt.close()

    if len(w_avg) >= 2:
        top  = w_avg.iloc[0]
        bot  = w_avg.iloc[-1]
        drop = (top["cnt"] - bot["cnt"]) / top["cnt"] * 100
        st.markdown(f"""
        <div class="insight-box warning">
        <b>Insight:</b> Peminjaman turun <b>{drop:.1f}%</b> dari kondisi terbaik
        (<b>{top.weather_label}</b>: {top.cnt:,.0f}/hari) ke kondisi terburuk
        (<b>{bot.weather_label}</b>: {bot.cnt:,.0f}/hari).
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Tren & Clustering
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title"> Tren Bulanan & Clustering</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    month_names = ["Jan","Feb","Mar","Apr","Mei","Jun",
                   "Jul","Agu","Sep","Okt","Nov","Des"]

    with col1:
        st.markdown("#### Tren Peminjaman Bulanan per Tahun")
        monthly = fd.groupby(["year_label","mnth"])["cnt"].sum().reset_index()

        fig6, ax6 = plt.subplots(figsize=(7, 4.5))
        for yr, col, mk in [("2011","#5C6BC0","o"),("2012","#EF5350","s")]:
            sub = monthly[monthly["year_label"]==yr].sort_values("mnth")
            if len(sub):
                ax6.plot(sub["mnth"], sub["cnt"],
                         color=col, marker=mk, ms=7, lw=2.5, label=yr)
                ax6.fill_between(sub["mnth"], sub["cnt"],
                                 alpha=0.10, color=col)
        ax6.set_xticks(range(1,13))
        ax6.set_xticklabels(month_names, fontsize=9.5)
        ax6.yaxis.set_major_formatter(
            mticker.FuncFormatter(lambda x,_: f"{x/1000:.0f}K"))
        ax6.set_ylabel("Total Peminjaman", fontsize=11)
        ax6.set_xlabel("Bulan", fontsize=11)
        ax6.set_title("Tren Bulanan (2011 vs. 2012)", fontsize=12,
                      fontweight="bold")
        ax6.legend(title="Tahun", fontsize=10)
        ax6.grid(alpha=0.35)
        plt.tight_layout()
        st.pyplot(fig6)
        plt.close()

        # YoY
        if {"2011","2012"}.issubset(set(selected_years)):
            t11 = fd[fd["year_label"]=="2011"]["cnt"].sum()
            t12 = fd[fd["year_label"]=="2012"]["cnt"].sum()
            if t11 > 0:
                yoy = (t12 - t11) / t11 * 100
                st.markdown(f"""
                <div class="insight-box success">
                📈 <b>YoY Growth:</b> Peminjaman 2012 tumbuh <b>{yoy:.1f}%</b>
                dibanding 2011 ({t11:,.0f} → {t12:,.0f}).
                </div>""", unsafe_allow_html=True)

    with col2:
        st.markdown("#### Clustering Permintaan Harian")
        cc = fd["demand_cluster"].value_counts().sort_index()
        cluster_colors = ["#EF9A9A","#FFCC80","#FFF176","#A5D6A7","#80DEEA"]

        fig7, ax7 = plt.subplots(figsize=(6.5, 4.5))
        wedges, texts, autotexts = ax7.pie(
            cc, labels=cc.index,
            colors=cluster_colors[:len(cc)],
            autopct="%1.1f%%", startangle=90,
            pctdistance=0.80,
            wedgeprops=dict(width=0.55, edgecolor="white", lw=2)
        )
        for t  in texts:      t.set_fontsize(9)
        for at in autotexts:  at.set_fontsize(8.5)
        ax7.legend(wedges, [f"{k}: {v} hari" for k,v in cc.items()],
                   loc="lower center", bbox_to_anchor=(0.5,-0.12),
                   ncol=2, fontsize=8.5)
        ax7.set_title("Cluster Permintaan Harian", fontsize=12, fontweight="bold")
        plt.tight_layout()
        st.pyplot(fig7)
        plt.close()

        # Detail tabel cluster
        c_tbl = (
            fd.groupby("demand_cluster", observed=True)
            .agg(hari=("cnt","count"), avg=("cnt","mean"),
                 suhu=("temp_c","mean"), workday=("workingday","mean"))
            .round(2)
        )
        c_tbl["workday"] = (c_tbl["workday"]*100).round(1)
        c_tbl.columns = ["Hari","Avg Peminjaman","Avg Suhu(°C)","% Hari Kerja"]
        st.dataframe(c_tbl, use_container_width=True)

    # Stacked bar komposisi user
    st.markdown("---")
    st.markdown("#### Komposisi Kasual vs. Terdaftar per Bulan")
    um = fd.groupby(["mnth","year_label"])[["casual","registered"]].sum().reset_index()

    fig8, ax8 = plt.subplots(figsize=(13, 4.5))
    w = 0.35
    for yr, cc_, cr, off in [
        ("2011","#90CAF9","#1565C0",-w/2),
        ("2012","#FFCC80","#E65100", w/2)
    ]:
        sub = um[um["year_label"]==yr].sort_values("mnth")
        x   = sub["mnth"].values + off
        ax8.bar(x, sub["casual"],     width=w*0.9, color=cc_, label=f"Kasual {yr}")
        ax8.bar(x, sub["registered"], width=w*0.9, color=cr,
                bottom=sub["casual"],  label=f"Terdaftar {yr}")
    ax8.set_xticks(range(1,13))
    ax8.set_xticklabels(month_names, fontsize=10)
    ax8.yaxis.set_major_formatter(
        mticker.FuncFormatter(lambda x,_: f"{x/1000:.0f}K"))
    ax8.set_ylabel("Total Peminjaman", fontsize=11)
    ax8.set_title("Komposisi Kasual vs. Terdaftar per Bulan",
                  fontsize=12, fontweight="bold")
    ax8.legend(fontsize=9, ncol=4, loc="upper left")
    ax8.grid(axis="y", alpha=0.35)
    plt.tight_layout()
    st.pyplot(fig8)
    plt.close()


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Korelasi
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">🔗 Analisis Korelasi</div>',
                unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    corr_cols  = ["temp_c","atemp_c","hum_pct","wind_kph",
                   "cnt","casual","registered"]

    with col1:
        st.markdown("#### Suhu vs. Jumlah Peminjaman (per Musim)")
        s_colors = {"Spring":"#81C784","Summer":"#FFB74D",
                    "Fall":"#EF5350","Winter":"#64B5F6"}
        fig9, ax9 = plt.subplots(figsize=(7, 5))
        for season, col in s_colors.items():
            sub = fd[fd["season_label"]==season]
            if len(sub):
                ax9.scatter(sub["temp_c"], sub["cnt"],
                            c=col, alpha=0.55, s=25,
                            label=season, edgecolors="none")
        if len(fd) > 1:
            z     = np.polyfit(fd["temp_c"], fd["cnt"], 1)
            p_fn  = np.poly1d(z)
            x_ln  = np.linspace(fd["temp_c"].min(), fd["temp_c"].max(), 100)
            ax9.plot(x_ln, p_fn(x_ln), "k--", lw=2, label="Tren Linear")
            r = fd[["temp_c","cnt"]].corr().iloc[0,1]
            ax9.text(0.05, 0.93, f"r = {r:.3f}",
                     transform=ax9.transAxes, fontsize=11,
                     bbox=dict(boxstyle="round,pad=0.3", facecolor="wheat"))
        ax9.set_xlabel("Suhu Aktual (°C)", fontsize=11)
        ax9.set_ylabel("Peminjaman Harian", fontsize=11)
        ax9.set_title("Suhu vs. Jumlah Peminjaman", fontsize=12, fontweight="bold")
        ax9.legend(fontsize=9)
        ax9.grid(alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig9)
        plt.close()

    with col2:
        st.markdown("#### Heatmap Korelasi Lengkap")
        corr_df = fd[corr_cols].corr()
        fig10, ax10 = plt.subplots(figsize=(7, 5))
        sns.heatmap(corr_df, ax=ax10, annot=True, fmt=".2f",
                    cmap="RdYlGn", center=0, vmin=-1, vmax=1,
                    linewidths=0.5, square=True,
                    cbar_kws={"shrink":0.82})
        ax10.set_title("Heatmap Korelasi Pearson", fontsize=12, fontweight="bold")
        ax10.tick_params(axis="x", rotation=30, labelsize=9)
        ax10.tick_params(axis="y", rotation=0,  labelsize=9)
        plt.tight_layout()
        st.pyplot(fig10)
        plt.close()

    # Bar chart nilai korelasi vs cnt
    st.markdown("---")
    st.markdown("#### Kekuatan Korelasi dengan Jumlah Peminjaman (cnt)")
    if len(fd) > 1:
        corr_cnt = (
            fd[corr_cols].corr()["cnt"]
            .drop("cnt")
            .sort_values(key=abs, ascending=False)
        )
        bar_colors = ["#4CAF50" if v > 0 else "#F44336"
                      for v in corr_cnt]
        fig11, ax11 = plt.subplots(figsize=(10, 3.5))
        bars = ax11.barh(corr_cnt.index, corr_cnt.values,
                         color=bar_colors, edgecolor="white", height=0.55)
        for b, v in zip(bars, corr_cnt.values):
            ax11.text(v + (0.01 if v >= 0 else -0.01),
                      b.get_y() + b.get_height()/2,
                      f"{v:.3f}", va="center",
                      ha="left" if v >= 0 else "right", fontsize=10)
        ax11.axvline(0, color="black", lw=1.2)
        ax11.set_xlabel("Nilai Korelasi Pearson", fontsize=11)
        ax11.set_title("Korelasi Variabel dengan cnt",
                       fontsize=12, fontweight="bold")
        ax11.set_xlim(-0.5, 0.95)
        ax11.grid(axis="x", alpha=0.3)
        plt.tight_layout()
        st.pyplot(fig11)
        plt.close()

        r_temp = corr_cnt.get("temp_c", 0)
        r_hum  = corr_cnt.get("hum_pct", 0)
        r_wind = corr_cnt.get("wind_kph", 0)
        st.markdown(f"""
        <div class="insight-box">
        🔍 <b>Temuan Utama:</b><br>
        • <b>Suhu (r = {r_temp:.3f})</b> – korelasi positif kuat: makin hangat → makin banyak peminjaman<br>
        • <b>Kelembaban (r = {r_hum:.3f})</b> – korelasi negatif: hari lembab = lebih sedikit peminjaman<br>
        • <b>Kecepatan Angin (r = {r_wind:.3f})</b> – korelasi negatif: angin kencang mengurangi minat
        </div>""", unsafe_allow_html=True)


# ─── Footer ───────────────────────────────────────────────────────────────────
st.divider()
st.markdown("""
<div style="text-align:center; color:#888; font-size:0.85rem; padding:1rem 0">
    🚲 <b>Bike Sharing Analytics Dashboard</b> &nbsp;|&nbsp;
    Capital Bikeshare Washington D.C. 2011–2012 &nbsp;|&nbsp;
    Built with Streamlit & Matplotlib
</div>
""", unsafe_allow_html=True)