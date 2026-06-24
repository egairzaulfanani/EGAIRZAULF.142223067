import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import io

# ─── Page Config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Survei Sistem Absensi Kampus",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
        padding: 2rem 2.5rem; border-radius: 12px;
        color: white; margin-bottom: 2rem;
    }
    .main-header h1 { font-size: 1.8rem; font-weight: 700; margin: 0; }
    .main-header p  { font-size: 0.95rem; opacity: 0.85; margin: 0.4rem 0 0; }
    .metric-card {
        background: white; border: 1px solid #e2e8f0;
        border-radius: 10px; padding: 1.2rem 1.5rem;
        text-align: center; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .metric-value { font-size: 2.1rem; font-weight: 700; color: #1e3a5f; }
    .metric-label { font-size: 0.8rem; color: #64748b; text-transform: uppercase;
                    letter-spacing: 0.05em; margin-top: 0.2rem; }
    .section-title {
        font-size: 1.05rem; font-weight: 600; color: #1e3a5f;
        border-left: 4px solid #2d6a9f; padding-left: 0.75rem;
        margin: 1.5rem 0 1rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Constants ────────────────────────────────────────────────────────────────
LIKERT_LABELS = {1: "Sangat Tidak Setuju", 2: "Tidak Setuju", 3: "Netral",
                 4: "Setuju", 5: "Sangat Setuju"}
LIKERT_COLORS = ["#ef4444", "#f97316", "#facc15", "#4ade80", "#22c55e"]

COLOR_PALETTE = ["#2d6a9f", "#22c55e", "#f59e0b", "#ef4444", "#8b5cf6",
                 "#06b6d4", "#ec4899", "#10b981"]

Q_COLS = [
    "Q1 – Kemudahan Pemahaman",
    "Q2 – Kecepatan Proses",
    "Q3 – Minimnya Kendala/Error",
    "Q4 – Kemudahan Pencatatan",
    "Q5 – Akurasi Informasi",
]

# ─── Data Hardcoded ───────────────────────────────────────────────────────────
RAW_DATA = [
    ["laki-laki", "26-35 tahun", "Teknik",  2, 2, 4, 1, 2],
    ["laki-laki", "18-25 tahun", "Teknik",  2, 2, 4, 2, 1],
    ["Perempuan", "18-25 tahun", "Fikes",   1, 2, 2, 2, 2],
    ["laki-laki", "26-35 tahun", "Ekonomi", 1, 2, 4, 2, 2],
    ["laki-laki", "18-25 tahun", "Ekonomi", 3, 3, 2, 3, 2],
    ["Perempuan", "18-25 tahun", "Ekonomi", 2, 3, 3, 2, 2],
    ["laki-laki", "26-35 tahun", "Teknik",  2, 3, 2, 3, 3],
    ["Perempuan", "18-25 tahun", "Teknik",  2, 3, 3, 2, 2],
    ["Perempuan", "18-25 tahun", "Fikes",   2, 2, 2, 3, 3],
    ["laki-laki", "18-25 tahun", "Teknik",  5, 5, 3, 4, 5],
    ["laki-laki", "18-25 tahun", "Ekonomi", 4, 4, 4, 3, 5],
    ["Perempuan", "26-35 tahun", "Ekonomi", 4, 4, 3, 3, 4],
    ["laki-laki", "18-25 tahun", "Ekonomi", 3, 3, 3, 4, 4],
    ["laki-laki", "18-25 tahun", "Teknik",  3, 3, 4, 4, 4],
    ["Perempuan", "18-25 tahun", "Teknik",  4, 3, 3, 4, 4],
    ["Perempuan", "18-25 tahun", "Fikes",   4, 4, 4, 4, 4],
    ["laki-laki", "26-35 tahun", "Teknik",  3, 3, 3, 3, 3],
    ["laki-laki", "18-25 tahun", "Teknik",  3, 3, 4, 4, 3],
    ["laki-laki", "26-35 tahun", "Ekonomi", 3, 3, 4, 3, 2],
    ["laki-laki", "26-35 tahun", "Ekonomi", 3, 4, 4, 5, 4],
    ["laki-laki", "18-25 tahun", "Ekonomi", 5, 5, 4, 4, 5],
    ["Perempuan", "18-25 tahun", "Fikes",   3, 3, 2, 4, 4],
    ["Perempuan", "26-35 tahun", "Ekonomi", 3, 3, 4, 3, 4],
    ["Perempuan", "18-25 tahun", "Fikes",   3, 4, 4, 3, 3],
    ["laki-laki", "18-25 tahun", "Ekonomi", 3, 3, 4, 3, 5],
    ["laki-laki", "18-25 tahun", "Ekonomi", 3, 3, 4, 3, 4],
    ["laki-laki", "18-25 tahun", "Teknik",  4, 4, 4, 4, 4],
    ["laki-laki", "26-35 tahun", "Fikes",   3, 4, 3, 4, 4],
    ["Perempuan", "18-25 tahun", "Fikes",   3, 4, 3, 4, 4],
    ["Perempuan", "18-25 tahun", "Fikes",   3, 4, 3, 3, 4],
    ["Perempuan", "26-35 tahun", "Fikes",   3, 4, 3, 3, 4],
    ["Perempuan", "18-25 tahun", "Ekonomi", 3, 3, 4, 4, 5],
    ["laki-laki", "18-25 tahun", "Teknik",  3, 4, 5, 5, 4],
    ["laki-laki", "18-25 tahun", "Teknik",  3, 3, 4, 4, 4],
    ["laki-laki", "18-25 tahun", "Fikes",   3, 4, 4, 4, 4],
    ["laki-laki", "26-35 tahun", "Teknik",  3, 4, 3, 4, 5],
    ["laki-laki", "26-35 tahun", "Teknik",  3, 4, 3, 4, 5],
    ["laki-laki", "26-35 tahun", "Teknik",  3, 4, 5, 5, 5],
    ["laki-laki", "18-25 tahun", "Fikes",   3, 5, 4, 5, 5],
    ["Perempuan", "18-25 tahun", "Ekonomi", 3, 3, 4, 4, 5],
    ["Perempuan", "18-25 tahun", "Ekonomi", 5, 5, 4, 4, 5],
    ["Perempuan", "18-25 tahun", "Fikes",   4, 5, 5, 5, 5],
]

@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.DataFrame(RAW_DATA,
                      columns=["Jenis Kelamin", "Usia", "Fakultas"] + Q_COLS)
    df["Jenis Kelamin"] = df["Jenis Kelamin"].str.strip()
    for col in Q_COLS:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Rata-rata"] = df[Q_COLS].mean(axis=1)
    return df


def bar_color(val):
    if val >= 4.0: return "#22c55e"
    if val >= 3.0: return "#facc15"
    return "#ef4444"


# ─── Load Data ────────────────────────────────────────────────────────────────
df_full = load_data()

# ─── Sidebar – Info saja ─────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📋 Informasi")
    st.markdown("---")
    st.markdown("**Judul Survei**")
    st.info("Kepuasan Mahasiswa terhadap Sistem Absensi Kampus")
    st.markdown("**Peneliti**")
    st.info("Ega Irza Ul Fanani\nNIM: 142223067")
    st.markdown("**Total Responden**")
    st.info(f"{len(df_full)} mahasiswa")
    st.markdown("---")
    st.caption("Dashboard Survei Kepuasan\nSistem Absensi Kampus")

# ─── Gunakan seluruh data ─────────────────────────────────────────────────────
df = df_full.copy()

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>📋 Dashboard Survei Sistem Absensi Kampus</h1>
    <p>Analisis kepuasan mahasiswa terhadap sistem absensi &nbsp;|&nbsp; Ega Irza Ul Fanani – 142223067</p>
</div>
""", unsafe_allow_html=True)

# ─── KPI ──────────────────────────────────────────────────────────────────────
avg_overall = df[Q_COLS].values.mean()
pct_pos     = (df[Q_COLS].values.flatten() >= 4).mean() * 100
best_q      = df[Q_COLS].mean().idxmax().split("–")[-1].strip()
low_q       = df[Q_COLS].mean().idxmin().split("–")[-1].strip()

c1, c2, c3, c4, c5 = st.columns(5)
for col, val, lbl in [
    (c1, len(df),              "Total Responden"),
    (c2, f"{avg_overall:.2f}", "Rata-rata Skor (1–5)"),
    (c3, best_q,               "Aspek Tertinggi"),
    (c4, low_q,                "Aspek Terendah"),
    (c5, f"{pct_pos:.0f}%",    "Respons Positif (≥4)"),
]:
    with col:
        st.markdown(f"""<div class="metric-card">
            <div class="metric-value" style="font-size:{'2.1rem' if len(str(val))<=5 else '1rem'}">{val}</div>
            <div class="metric-label">{lbl}</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Ringkasan", "👥 Demografi", "📈 Analisis Pertanyaan", "🗂️ Data Mentah"
])

# ════════════════════════════════════════════════════════
# TAB 1 – RINGKASAN
# ════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns(2, gap="large")

    with col_left:
        st.markdown('<p class="section-title">Rata-rata Skor per Pertanyaan</p>', unsafe_allow_html=True)
        means  = df[Q_COLS].mean()
        labels = [q.split("–")[-1].strip() for q in Q_COLS]
        colors = [bar_color(v) for v in means.values]

        fig, ax = plt.subplots(figsize=(6, 3.5))
        bars = ax.barh(labels, means.values, color=colors, edgecolor="white")
        ax.set_xlim(0, 5.5)
        ax.set_xlabel("Skor (1–5)", fontsize=9)
        for bar, val in zip(bars, means.values):
            ax.text(val + 0.05, bar.get_y() + bar.get_height()/2,
                    f"{val:.2f}", va="center", fontsize=8)
        ax.spines[["top","right"]].set_visible(False)
        ax.tick_params(labelsize=8)
        fig.tight_layout()
        st.pyplot(fig)
        plt.close(fig)

    with col_right:
        st.markdown('<p class="section-title">Distribusi Jawaban Keseluruhan</p>', unsafe_allow_html=True)
        all_vals   = df[Q_COLS].values.flatten()
        all_vals   = all_vals[~np.isnan(all_vals)].astype(int)
        val_counts = pd.Series(all_vals).value_counts().sort_index()

        fig2, ax2 = plt.subplots(figsize=(5, 3.5))
        wedges, texts, autotexts = ax2.pie(
            val_counts.values,
            labels=[LIKERT_LABELS[i] for i in val_counts.index],
            colors=LIKERT_COLORS, autopct="%1.1f%%",
            startangle=140, pctdistance=0.75,
            wedgeprops=dict(width=0.55)
        )
        for t in texts: t.set_fontsize(7)
        for a in autotexts: a.set_fontsize(7)
        ax2.set_title("Distribusi Skala Likert", fontsize=10)
        fig2.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)

    # Radar Chart
    st.markdown('<p class="section-title">Radar – Profil Kepuasan</p>', unsafe_allow_html=True)
    radar_vals   = df[Q_COLS].mean().tolist()
    radar_labels = [q.split("–")[-1].strip() for q in Q_COLS]
    N      = len(radar_labels)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    radar_vals += radar_vals[:1]

    fig3, ax3 = plt.subplots(figsize=(5, 5), subplot_kw=dict(polar=True))
    ax3.set_theta_offset(np.pi / 2)
    ax3.set_theta_direction(-1)
    ax3.set_xticks(angles[:-1])
    ax3.set_xticklabels(radar_labels, size=8)
    ax3.set_ylim(0, 5)
    ax3.set_yticks([1, 2, 3, 4, 5])
    ax3.set_yticklabels(["1","2","3","4","5"], size=7)
    ax3.plot(angles, radar_vals, color="#2d6a9f", linewidth=2)
    ax3.fill(angles, radar_vals, color="#2d6a9f", alpha=0.2)
    fig3.tight_layout()
    _, rc3, _ = st.columns([1, 2, 1])
    with rc3: st.pyplot(fig3)
    plt.close(fig3)


# ════════════════════════════════════════════════════════
# TAB 2 – DEMOGRAFI
# ════════════════════════════════════════════════════════
with tab2:
    def plot_donut(ax, series, title):
        vc = series.value_counts()
        wedges, texts, autotexts = ax.pie(
            vc.values, labels=vc.index,
            colors=COLOR_PALETTE[:len(vc)],
            autopct="%1.1f%%", startangle=140,
            wedgeprops=dict(width=0.55), pctdistance=0.78
        )
        for t in texts: t.set_fontsize(8)
        for a in autotexts: a.set_fontsize(8)
        ax.set_title(title, fontsize=10, fontweight="bold", pad=10)

    fig_d, axes = plt.subplots(1, 3, figsize=(12, 4))
    plot_donut(axes[0], df["Jenis Kelamin"], "Jenis Kelamin")
    plot_donut(axes[1], df["Usia"],          "Kelompok Usia")
    plot_donut(axes[2], df["Fakultas"],      "Fakultas")
    fig_d.tight_layout()
    st.pyplot(fig_d)
    plt.close(fig_d)

    st.markdown('<p class="section-title">Rata-rata Skor per Kelompok</p>', unsafe_allow_html=True)
    grp_col = st.radio("Kelompokkan berdasarkan:",
                       ["Jenis Kelamin", "Usia", "Fakultas"], horizontal=True)

    grp_df         = df.groupby(grp_col)[Q_COLS].mean()
    short_qs       = [q.split("–")[-1].strip() for q in Q_COLS]
    grp_df.columns = short_qs

    fig_g, ax_g = plt.subplots(figsize=(10, 4))
    x = np.arange(len(short_qs))
    n = len(grp_df)
    w = 0.7 / n
    for i, (grp, row) in enumerate(grp_df.iterrows()):
        ax_g.bar(x + i * w - (n-1)*w/2, row.values, width=w,
                 label=str(grp), color=COLOR_PALETTE[i % len(COLOR_PALETTE)])
    ax_g.set_xticks(x)
    ax_g.set_xticklabels(short_qs, rotation=15, ha="right", fontsize=9)
    ax_g.set_ylim(0, 5.5)
    ax_g.set_ylabel("Skor")
    ax_g.legend(title=grp_col, fontsize=8)
    ax_g.spines[["top","right"]].set_visible(False)
    fig_g.tight_layout()
    st.pyplot(fig_g)
    plt.close(fig_g)


# ════════════════════════════════════════════════════════
# TAB 3 – ANALISIS PERTANYAAN
# ════════════════════════════════════════════════════════
with tab3:
    selected_q = st.selectbox("Pilih Pertanyaan:", Q_COLS)

    qa, qb = st.columns([1, 1], gap="large")

    with qa:
        st.markdown('<p class="section-title">Distribusi Jawaban</p>', unsafe_allow_html=True)
        vc        = df[selected_q].dropna().astype(int).value_counts().sort_index()
        vc_labels = [LIKERT_LABELS[i] for i in vc.index]
        bar_cols  = [LIKERT_COLORS[i-1] for i in vc.index]

        fig_dist, ax_dist = plt.subplots(figsize=(6, 3.5))
        bars = ax_dist.bar(vc_labels, vc.values, color=bar_cols, edgecolor="white")
        for bar, val in zip(bars, vc.values):
            ax_dist.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.2,
                         str(val), ha="center", fontsize=9)
        ax_dist.set_ylabel("Jumlah Responden")
        ax_dist.set_xticklabels(vc_labels, rotation=15, ha="right", fontsize=8)
        ax_dist.spines[["top","right"]].set_visible(False)
        fig_dist.tight_layout()
        st.pyplot(fig_dist)
        plt.close(fig_dist)

    with qb:
        st.markdown('<p class="section-title">Statistik Deskriptif</p>', unsafe_allow_html=True)
        s     = df[selected_q].dropna()
        stats = pd.DataFrame({
            "Statistik": ["N (valid)", "Rata-rata", "Median", "Modus", "Std. Dev.", "Min", "Maks"],
            "Nilai":     [int(s.count()), round(s.mean(),3), round(s.median(),3),
                          int(s.mode()[0]), round(s.std(),3), int(s.min()), int(s.max())]
        })
        st.dataframe(stats, hide_index=True, use_container_width=True)
        pct  = (s >= 4).mean() * 100
        sent = "✅ Positif" if s.mean() >= 4 else ("⚠️ Netral" if s.mean() >= 3 else "❌ Negatif")
        st.info(f"**Sentimen:** {sent} &nbsp;&nbsp; **Positif (≥4):** {pct:.1f}%")

    # Box plot
    st.markdown('<p class="section-title">Box Plot per Kelompok Demografi</p>', unsafe_allow_html=True)
    box_grp  = st.radio("Kelompok:", ["Jenis Kelamin", "Usia", "Fakultas"],
                        horizontal=True, key="box_grp")
    groups   = df[box_grp].dropna().unique()
    box_data = [df[df[box_grp] == g][selected_q].dropna().values for g in groups]

    fig_box, ax_box = plt.subplots(figsize=(8, 4))
    bp = ax_box.boxplot(box_data, tick_labels=list(groups), patch_artist=True)
    for patch, color in zip(bp["boxes"], COLOR_PALETTE):
        patch.set_facecolor(color); patch.set_alpha(0.6)
    ax_box.set_ylim(0.5, 5.5)
    ax_box.set_ylabel("Skor")
    ax_box.spines[["top","right"]].set_visible(False)
    fig_box.tight_layout()
    st.pyplot(fig_box)
    plt.close(fig_box)

    # Heatmap korelasi
    st.markdown('<p class="section-title">Korelasi antar Pertanyaan</p>', unsafe_allow_html=True)
    corr         = df[Q_COLS].corr()
    corr.index   = [q.split("–")[-1].strip() for q in Q_COLS]
    corr.columns = corr.index

    fig_hm, ax_hm = plt.subplots(figsize=(7, 5))
    sns.heatmap(corr, annot=True, fmt=".2f", cmap="Blues",
                vmin=-1, vmax=1, ax=ax_hm,
                linewidths=0.5, annot_kws={"size": 9})
    ax_hm.tick_params(labelsize=8)
    fig_hm.tight_layout()
    st.pyplot(fig_hm)
    plt.close(fig_hm)


# ════════════════════════════════════════════════════════
# TAB 4 – DATA MENTAH
# ════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-title">Tabel Responden</p>', unsafe_allow_html=True)
    display_cols = ["Jenis Kelamin", "Usia", "Fakultas"] + Q_COLS + ["Rata-rata"]
    st.dataframe(
        df[display_cols].style.background_gradient(
            subset=Q_COLS + ["Rata-rata"], cmap="Blues", vmin=1, vmax=5),
        use_container_width=True, height=420,
    )

    out = io.BytesIO()
    df[display_cols].to_excel(out, index=False)
    st.download_button(
        "⬇️ Download Data (.xlsx)",
        data=out.getvalue(),
        file_name="survei_absensi.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.markdown('<p class="section-title">Tabel Frekuensi Demografis</p>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)

    def freq_table(series, label):
        vc = series.value_counts().reset_index()
        vc.columns = [label, "Frekuensi"]
        vc["Persen"] = (vc["Frekuensi"] / vc["Frekuensi"].sum()).map("{:.1%}".format)
        return vc

    with fc1:
        st.caption("Jenis Kelamin")
        st.dataframe(freq_table(df["Jenis Kelamin"], "Jenis Kelamin"),
                     hide_index=True, use_container_width=True)
    with fc2:
        st.caption("Usia")
        st.dataframe(freq_table(df["Usia"], "Usia"),
                     hide_index=True, use_container_width=True)
    with fc3:
        st.caption("Fakultas")
        st.dataframe(freq_table(df["Fakultas"], "Fakultas"),
                     hide_index=True, use_container_width=True)
