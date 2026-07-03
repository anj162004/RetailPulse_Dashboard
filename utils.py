import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# ─── Theme Colors ───────────────────────────────────────────────────────────
PRIMARY     = "#4F46E5"   # Indigo
SECONDARY   = "#06B6D4"   # Cyan
ACCENT      = "#F59E0B"   # Amber
SUCCESS     = "#10B981"   # Emerald
DANGER      = "#EF4444"   # Red
BG_CARD     = "#1E1E2E"
TEXT_MAIN   = "#E2E8F0"
TEXT_MUTED  = "#94A3B8"

PALETTE     = [PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER,
               "#8B5CF6", "#EC4899", "#14B8A6", "#F97316", "#84CC16"]

# ─── Page Config ─────────────────────────────────────────────────────────────
def set_page_config(title: str, icon: str):
    st.set_page_config(
        page_title=f"RetailPulse: AI-Powered Retail Analytics | {title}",
        page_icon=icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )

# ─── Global CSS ──────────────────────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* Dark sidebar */
    section[data-testid="stSidebar"] {
        background: #0F0F1A !important;
        border-right: 1px solid #2D2D44;
    }
    section[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
    section[data-testid="stSidebar"] .stSelectbox label,
    section[data-testid="stSidebar"] .stMultiSelect label { color: #94A3B8 !important; font-size: 0.78rem !important; }

   
    /* Main background */
.main {
    background: #0D0D1A;
}

/* Main page spacing */
.block-container {
    max-width: 100%;
    padding-top: 4.5rem !important;
    padding-right: 2.5rem !important;
    padding-left: 2.5rem !important;
    padding-bottom: 2rem !important;
}

    /* Metric cards */
    .metric-card {
        background: linear-gradient(135deg, #1E1E2E 0%, #16213E 100%);
        border: 1px solid #2D2D44;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.5rem;
    }
    .metric-label { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em;
                    text-transform: uppercase; color: #94A3B8; margin-bottom: 0.3rem; }
    .metric-value { font-size: 1.9rem; font-weight: 800; color: #E2E8F0; line-height: 1; }
    .metric-delta { font-size: 0.78rem; margin-top: 0.3rem; }
    .delta-up   { color: #10B981; } 
    .delta-down { color: #EF4444; }

    /* Section headers */
    .section-header {
        font-size: 1.05rem; font-weight: 700; color: #E2E8F0;
        border-left: 3px solid #4F46E5; padding-left: 0.75rem;
        margin: 1.5rem 0 0.8rem 0;
    }

    
    /* Page title */
.page-title {
    font-size: 2rem;
    font-weight: 800;
    color: #E2E8F0;
    line-height: 1.3;
    letter-spacing: -0.02em;
    margin-top: 0.2rem;
    margin-bottom: 0.35rem;
}

.page-subtitle {
    font-size: 0.95rem;
    color: #94A3B8;
    margin-bottom: 1.5rem;
}
    /* Plotly chart backgrounds */
    .js-plotly-plot .plotly { background: transparent !important; }

    /* Tables */
    .stDataFrame { border-radius: 10px; overflow: hidden; }
    .stDataFrame thead tr th { background: #1E1E2E !important; color: #94A3B8 !important; }

    /* Sidebar brand */
    .sidebar-brand {
        font-size: 1.1rem; font-weight: 800; color: #4F46E5;
        letter-spacing: -0.02em; padding: 0.5rem 0 1rem 0;
        border-bottom: 1px solid #2D2D44; margin-bottom: 1rem;
    }

    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1E1E2E 0%, #16213E 100%);
        border: 1px solid #2D2D44; border-radius: 12px;
        padding: 0.8rem 1rem;
    }
    div[data-testid="metric-container"] label { color: #94A3B8 !important; font-size: 0.75rem !important; }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: #E2E8F0 !important; font-weight: 800 !important; }
                /* Hide Streamlit Header */
header[data-testid="stHeader"] {
    background: transparent;
    height: 0;
}

div[data-testid="stToolbar"] {
    display: none;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}
    </style>
    """, unsafe_allow_html=True)

# ─── Data Loader ─────────────────────────────────────────────────────────────
@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv("data/retail_feature_engineered.csv", parse_dates=["InvoiceDate"])
    df["Customer ID"] = df["Customer ID"].astype("Int64")
    return df

def apply_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    """Renders sidebar filters and returns filtered dataframe."""
    st.sidebar.markdown('<div class="sidebar-brand">🛍️ RetailPulse</div>', unsafe_allow_html=True)
    st.sidebar.markdown("### 🎛️ Filters")

    years = sorted(df["Year"].unique())
    sel_years = st.sidebar.multiselect("Year", years, default=years)

    countries = sorted(df["Country"].unique())
    sel_countries = st.sidebar.multiselect("Country", countries, default=countries)

    months = list(range(1, 13))
    month_names = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    sel_months = st.sidebar.multiselect("Month", months,
                                         default=months,
                                         format_func=lambda x: month_names[x-1])

    filtered = df[
        df["Year"].isin(sel_years) &
        df["Country"].isin(sel_countries) &
        df["Month"].isin(sel_months)
    ]

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**{len(filtered):,}** rows matching filters")
    return filtered

# ─── Chart helpers ────────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter", color="#CBD5E1", size=12),
    margin=dict(l=0, r=0, t=30, b=0),
    xaxis=dict(gridcolor="#2D2D44", linecolor="#2D2D44", tickfont=dict(color="#94A3B8")),
    yaxis=dict(gridcolor="#2D2D44", linecolor="#2D2D44", tickfont=dict(color="#94A3B8")),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#CBD5E1")),
)

def styled_chart(fig: go.Figure, height: int = 380) -> go.Figure:
    fig.update_layout(height=height, **CHART_LAYOUT)
    return fig

def metric_card(label: str, value: str, delta: str = "", delta_up: bool = True):
    delta_html = ""
    if delta:
        cls = "delta-up" if delta_up else "delta-down"
        arrow = "▲" if delta_up else "▼"
        delta_html = f'<div class="metric-delta {cls}">{arrow} {delta}</div>'
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)

def section_header(text: str):
    st.markdown(f'<div class="section-header">{text}</div>', unsafe_allow_html=True)

def page_header(title: str, subtitle: str):
    st.markdown(
        """
        <div style="padding-top:18px;"></div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="page-title">
            {title}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="page-subtitle">
            {subtitle}
        </div>
        """,
        unsafe_allow_html=True,
    )