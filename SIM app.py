import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Survei Sistem Absensi Kampus",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .main-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d6a9f 100%);
        padding: 2rem 2.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    .main-header h1 { font-size: 1.8rem; font-weight: 700; margin: 0; }
    .main-header p  { font-size: 0.95rem; opacity: 0.85; margin: 0.4rem 0 0; }

    .metric-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        text-align: center;
        box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    }
    .metric-value { font-size: 2.1rem; font-weight: 700; color: #1e3a5f; }
    .metric-label { font-size: 0.8rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.2rem; }

    .section-title {
        font-size: 1.05rem; font-weight: 600; color: #1e3a5f;
        border-left: 4px solid #2d6a9f;
        padding-left: 0.75rem; margin: 1.5rem 0 1rem;
    }

    .badge {
        display: inline-block; padding: 0.2rem 0.65rem;
        border-radius: 999px; font-size: 0.75rem; font-weight: 600;
    }
    .badge-green  { background: #d1fae5; color: #065f46; }
    .badge-yellow { background: #fef9c3; color: #854d0e; }
    .badge-red    { background: #fee2e2; color: #991b1b; }

    [data-testid="stSidebar"] { background: #f8fafc; }
    .stTabs [data-baseweb="tab-list"] { gap: 6px; }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px 8px 0 0 !important;
        font-weight: 500; font-size: 0.85rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Constants ───────────────────────────────────────────────────────────────
LIKERT_LABELS = {1: "Sangat Tidak Setuju", 2: "Tidak Setuju", 3: "Netral",
                 4: "Setuju", 5: "Sangat Setuju"}
LIKERT_COLORS = {
    "Sangat Tidak Setuju": "#ef4444",
    "Tidak Setuju":        "#f97316",
    "Netral":              "#facc15",
    "Setuju":              "#4ade80",
    "Sangat Setuju":       "#22c55e",
}
Q_SHORT = {
    "Q1 – Kemudahan Pemahaman":    "  Sistem absensi yang digunakan di kampus mudah dipahami  ",
    "Q2 – Kecepatan Proses":       "  Proses absensi dapat dilakukan dengan cepat  ",
    "Q3 – Minimnya Kendala/Error": "  Sistem absensi jarang mengalami kendala atau error  ",
    "Q4 – Kemudahan Pencatatan":   "  Sistem absensi memudahkan mahasiswa dalam mencatat kehadiran  ",
    "Q5 – Akurasi Informasi":      "  Informasi kehadiran yang ditampilkan dalam sistem akurat  ",
}

# ─── Data Loader ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data(file) -> pd.DataFrame:
    raw = pd.read_excel(file if isinstance(file, str) else io.BytesIO(file.read()))

    # Keep only valid survey rows (rows 0–41 have actual responses)
    df = raw.iloc[:42].copy()
    df = df[df["Jenis Kelamin:"].isin(["laki-laki", "Perempuan"])].copy()

    # Rename columns
    rename = {
        "Jenis Kelamin:": "Jenis Kelamin",
        "Umur:":           "Usia",
        "Fakultas:":       "Fakultas",
    }
    rename.update({v: k for k, v in Q_SHORT.items()})
    df.rename(columns=rename, inplace=True)

    # Normalise gender
    df["Jenis Kelamin"] = df["Jenis Kelamin"].str.strip()

    # Cast Likert columns to numeric
    q_cols = list(Q_SHORT.keys())
    for col in q_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["Rata-rata"] = df[q_cols].mean(axis=1)
    return df


def get_sentiment(val):
    if val >= 4.0: return "badge-green",  "Positif"
    if val >= 3.0: return "badge-yellow", "Netral"
    return "badge-red", "Negatif"


# ─── Sidebar ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Pengaturan")
    st.markdown("---")

    uploaded = st.file_uploader("📂 Upload file Excel (.xlsx)", type=["xlsx"])

    st.markdown("---")
    st.markdown("**Filter Responden**")

    # Placeholders — will be filled after data loads
    gender_ph  = st.empty()
    usia_ph    = st.empty()
    fakultas_ph = st.empty()

    st.markdown("---")
    st.caption("Dashboard Survei Kepuasan\nSistem Absensi Kampus\n*Ega Irza Ul Fanani – 142223067*")

# ─── Load Data ────────────────────────────────────────────────────────────────
DEFAULT_PATH = "ega_irza_ul_fanani_142223067___Responses_.xlsx"

try:
    if uploaded:
        df_full = load_data(uploaded)
    else:
        df_full = load_data(DEFAULT_PATH)
except FileNotFoundError:
    st.error("⚠️  File data tidak ditemukan. Silakan upload file Excel lewat sidebar.")
    st.stop()

# ─── Sidebar Filters ─────────────────────────────────────────────────────────
all_genders   = sorted(df_full["Jenis Kelamin"].dropna().unique())
all_usia      = sorted(df_full["Usia"].dropna().unique())
all_fakultas  = sorted(df_full["Fakultas"].dropna().unique())

sel_gender   = gender_ph.multiselect("Jenis Kelamin", all_genders,   default=all_genders)
sel_usia     = usia_ph.multiselect("Usia",           all_usia,       default=all_usia)
sel_fakultas = fakultas_ph.multiselect("Fakultas",    all_fakultas,   default=all_fakultas)

df = df_full[
    df_full["Jenis Kelamin"].isin(sel_gender) &
    df_full["Usia"].isin(sel_usia) &
    df_full["Fakultas"].isin(sel_fakultas)
].copy()

q_cols = list(Q_SHORT.keys())

# ─── Header ──────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>📋 Dashboard Survei Sistem Absensi Kampus</h1>
    <p>Analisis kepuasan mahasiswa terhadap sistem absensi &nbsp;|&nbsp; Ega Irza Ul Fanani – 142223067</p>
</div>
""", unsafe_allow_html=True)

# ─── KPI Row ─────────────────────────────────────────────────────────────────
avg_overall = df[q_cols].values.mean()
badge_cls, badge_lbl = get_sentiment(avg_overall)

c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{len(df)}</div>
        <div class="metric-label">Total Responden</div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{avg_overall:.2f}</div>
        <div class="metric-label">Rata-rata Skor (1–5)</div></div>""", unsafe_allow_html=True)
with c3:
    best_q = df[q_cols].mean().idxmax().split("–")[-1].strip()
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value" style="font-size:1.1rem">{best_q}</div>
        <div class="metric-label">Aspek Tertinggi</div></div>""", unsafe_allow_html=True)
with c4:
    low_q = df[q_cols].mean().idxmin().split("–")[-1].strip()
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value" style="font-size:1.1rem">{low_q}</div>
        <div class="metric-label">Aspek Terendah</div></div>""", unsafe_allow_html=True)
with c5:
    pct_pos = (df[q_cols].values.flatten() >= 4).mean() * 100
    st.markdown(f"""<div class="metric-card">
        <div class="metric-value">{pct_pos:.0f}%</div>
        <div class="metric-label">Respons Positif (≥4)</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ─── Tabs ────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Ringkasan", "👥 Demografi", "📈 Analisis Pertanyaan", "🗂️ Data Mentah"
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 – RINGKASAN
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown('<p class="section-title">Rata-rata Skor per Pertanyaan</p>', unsafe_allow_html=True)
        means = df[q_cols].mean().reset_index()
        means.columns = ["Pertanyaan", "Skor"]
        means["Label"] = means["Pertanyaan"].str.split("–").str[-1].str.strip()
        means["Warna"] = means["Skor"].apply(lambda x: "#22c55e" if x>=4 else ("#facc15" if x>=3 else "#ef4444"))

        fig_bar = go.Figure(go.Bar(
            x=means["Skor"], y=means["Label"],
            orientation="h",
            marker_color=means["Warna"],
            text=means["Skor"].round(2), textposition="outside",
        ))
        fig_bar.update_layout(
            xaxis=dict(range=[0, 5.5], title="Skor (1–5)"),
            yaxis=dict(title=""),
            margin=dict(l=10, r=20, t=10, b=10),
            height=300, plot_bgcolor="white", paper_bgcolor="white",
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.markdown('<p class="section-title">Distribusi Jawaban Keseluruhan</p>', unsafe_allow_html=True)
        all_vals = df[q_cols].values.flatten()
        all_vals = all_vals[~np.isnan(all_vals)].astype(int)
        val_counts = pd.Series(all_vals).value_counts().sort_index()
        val_df = pd.DataFrame({"Skor": val_counts.index,
                               "Jumlah": val_counts.values,
                               "Label": [LIKERT_LABELS[i] for i in val_counts.index]})
        fig_pie = px.pie(val_df, names="Label", values="Jumlah",
                         color="Label", color_discrete_map=LIKERT_COLORS,
                         hole=0.45)
        fig_pie.update_traces(textinfo="percent+label", showlegend=False)
        fig_pie.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=300,
                              paper_bgcolor="white")
        st.plotly_chart(fig_pie, use_container_width=True)

    # Radar Chart
    st.markdown('<p class="section-title">Radar – Profil Kepuasan</p>', unsafe_allow_html=True)
    radar_labels = [q.split("–")[-1].strip() for q in q_cols]
    radar_vals   = df[q_cols].mean().tolist()
    radar_vals  += [radar_vals[0]]
    radar_labels += [radar_labels[0]]

    fig_radar = go.Figure(go.Scatterpolar(
        r=radar_vals, theta=radar_labels,
        fill="toself", fillcolor="rgba(45,106,159,0.2)",
        line=dict(color="#2d6a9f", width=2),
        marker=dict(size=6, color="#1e3a5f"),
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 5])),
        showlegend=False, height=380,
        margin=dict(l=40, r=40, t=30, b=30),
        paper_bgcolor="white",
    )
    st.plotly_chart(fig_radar, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 – DEMOGRAFI
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    d1, d2, d3 = st.columns(3)

    def donut(series, title, colors=None):
        vc = series.value_counts().reset_index()
        vc.columns = ["Kategori", "Jumlah"]
        fig = px.pie(vc, names="Kategori", values="Jumlah",
                     hole=0.5, title=title,
                     color_discrete_sequence=colors or px.colors.qualitative.Set2)
        fig.update_traces(textinfo="percent+label", showlegend=False)
        fig.update_layout(margin=dict(l=0,r=0,t=40,b=0), height=280,
                          paper_bgcolor="white",
                          title_font=dict(size=13, color="#1e3a5f"))
        return fig

    with d1:
        st.plotly_chart(donut(df["Jenis Kelamin"], "Jenis Kelamin",
                              ["#3b82f6","#ec4899"]), use_container_width=True)
    with d2:
        st.plotly_chart(donut(df["Usia"], "Kelompok Usia",
                              ["#8b5cf6","#a78bfa","#c4b5fd"]), use_container_width=True)
    with d3:
        st.plotly_chart(donut(df["Fakultas"], "Fakultas",
                              ["#0ea5e9","#f59e0b","#10b981"]), use_container_width=True)

    st.markdown('<p class="section-title">Rata-rata Skor per Kelompok</p>', unsafe_allow_html=True)

    grp_col = st.radio("Kelompokkan berdasarkan:", ["Jenis Kelamin", "Usia", "Fakultas"], horizontal=True)
    grp_df  = df.groupby(grp_col)[q_cols].mean().reset_index()
    grp_melt = grp_df.melt(id_vars=grp_col, var_name="Pertanyaan", value_name="Skor")
    grp_melt["Pertanyaan"] = grp_melt["Pertanyaan"].str.split("–").str[-1].str.strip()

    fig_grp = px.bar(grp_melt, x="Pertanyaan", y="Skor",
                     color=grp_col, barmode="group",
                     color_discrete_sequence=px.colors.qualitative.Set1)
    fig_grp.update_layout(
        xaxis_title="", yaxis=dict(range=[0, 5], title="Skor"),
        legend_title=grp_col, height=380,
        margin=dict(l=10,r=10,t=10,b=10),
        plot_bgcolor="white", paper_bgcolor="white",
    )
    fig_grp.update_xaxes(tickangle=-20)
    st.plotly_chart(fig_grp, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 – ANALISIS PERTANYAAN
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    selected_q = st.selectbox("Pilih Pertanyaan:", list(Q_SHORT.keys()))

    qa, qb = st.columns([1, 1], gap="large")

    with qa:
        st.markdown('<p class="section-title">Distribusi Jawaban</p>', unsafe_allow_html=True)
        vc = df[selected_q].dropna().astype(int).value_counts().sort_index()
        vc_df = pd.DataFrame({"Skor": vc.index,
                              "Jumlah": vc.values,
                              "Label": [LIKERT_LABELS[i] for i in vc.index]})
        fig_dist = px.bar(vc_df, x="Label", y="Jumlah",
                          color="Label", color_discrete_map=LIKERT_COLORS,
                          text="Jumlah")
        fig_dist.update_traces(textposition="outside", showlegend=False)
        fig_dist.update_layout(xaxis_title="", yaxis_title="Jumlah Responden",
                               height=320, margin=dict(l=0,r=0,t=10,b=0),
                               plot_bgcolor="white", paper_bgcolor="white")
        st.plotly_chart(fig_dist, use_container_width=True)

    with qb:
        st.markdown('<p class="section-title">Statistik Deskriptif</p>', unsafe_allow_html=True)
        s = df[selected_q].dropna()
        stats = {
            "N (valid)": int(s.count()),
            "Rata-rata": round(s.mean(), 3),
            "Median":    round(s.median(), 3),
            "Modus":     int(s.mode()[0]),
            "Std. Dev.": round(s.std(), 3),
            "Min":       int(s.min()),
            "Maks":      int(s.max()),
        }
        st.dataframe(pd.DataFrame(stats, index=["Nilai"]).T, use_container_width=True)

        sentiment_cls, sentiment_lbl = get_sentiment(s.mean())
        st.markdown(f"""
        <p style="margin-top:1rem;font-size:0.9rem;color:#475569;">
        Sentimen: <span class="badge {sentiment_cls}">{sentiment_lbl}</span>
        &nbsp; Positif (≥4): <strong>{(s>=4).mean()*100:.1f}%</strong>
        </p>""", unsafe_allow_html=True)

    # Box plots per group
    st.markdown('<p class="section-title">Box Plot per Kelompok Demografi</p>', unsafe_allow_html=True)
    box_grp = st.radio("Kelompok:", ["Jenis Kelamin", "Usia", "Fakultas"], horizontal=True, key="box_grp")
    fig_box = px.box(df, x=box_grp, y=selected_q, color=box_grp,
                     color_discrete_sequence=px.colors.qualitative.Pastel,
                     points="all")
    fig_box.update_layout(yaxis=dict(range=[0.5, 5.5], title="Skor"),
                          xaxis_title="", showlegend=False,
                          height=350, margin=dict(l=0,r=0,t=10,b=0),
                          plot_bgcolor="white", paper_bgcolor="white")
    st.plotly_chart(fig_box, use_container_width=True)

    # Heatmap correlation
    st.markdown('<p class="section-title">Korelasi antar Pertanyaan</p>', unsafe_allow_html=True)
    corr = df[q_cols].corr()
    short_names = [q.split("–")[-1].strip() for q in q_cols]
    fig_hm = px.imshow(corr.values, x=short_names, y=short_names,
                       color_continuous_scale="Blues", zmin=-1, zmax=1,
                       text_auto=".2f", aspect="auto")
    fig_hm.update_layout(height=400, margin=dict(l=0,r=0,t=10,b=0),
                         paper_bgcolor="white")
    st.plotly_chart(fig_hm, use_container_width=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 – DATA MENTAH
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown('<p class="section-title">Tabel Responden</p>', unsafe_allow_html=True)

    display_cols = ["Jenis Kelamin", "Usia", "Fakultas"] + q_cols + ["Rata-rata"]
    st.dataframe(
        df[display_cols].style.background_gradient(subset=q_cols + ["Rata-rata"],
                                                   cmap="Blues", vmin=1, vmax=5),
        use_container_width=True, height=420,
    )

    # Download button
    out = io.BytesIO()
    df[display_cols].to_excel(out, index=False)
    st.download_button(
        "⬇️ Download Data Terfilter (.xlsx)",
        data=out.getvalue(),
        file_name="survei_absensi_filtered.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    st.markdown('<p class="section-title">Tabel Frekuensi Demografis</p>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)

    def freq_table(series, label):
        vc = series.value_counts().reset_index()
        vc.columns = [label, "Frekuensi"]
        vc["Prosentasi"] = (vc["Frekuensi"] / vc["Frekuensi"].sum()).map("{:.1%}".format)
        vc["Kumulatif"]  = vc["Prosentasi"].str.rstrip("%").astype(float).cumsum().map("{:.1f}%".format)
        return vc

    with fc1:
        st.caption("Jenis Kelamin")
        st.dataframe(freq_table(df["Jenis Kelamin"], "Jenis Kelamin"), hide_index=True, use_container_width=True)
    with fc2:
        st.caption("Usia")
        st.dataframe(freq_table(df["Usia"], "Usia"), hide_index=True, use_container_width=True)
    with fc3:
        st.caption("Fakultas")
        st.dataframe(freq_table(df["Fakultas"], "Fakultas"), hide_index=True, use_container_width=True)
