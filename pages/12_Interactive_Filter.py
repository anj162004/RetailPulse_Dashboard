import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils import (set_page_config, inject_css, load_data,
                   styled_chart, section_header, page_header,
                   PALETTE, PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER)

set_page_config("Interactive Filter Dashboard", "🎛️")
inject_css()

# ── Custom sidebar for this page only ────────────────────────────────────────
df_all = load_data()

st.sidebar.markdown('<div class="sidebar-brand">🛍️ RetailPulse</div>', unsafe_allow_html=True)
st.sidebar.markdown("## 🎛️ Custom Explorer")

# Advanced filters
years    = sorted(df_all["Year"].unique())
sel_year = st.sidebar.multiselect("Year", years, default=years)

countries    = sorted(df_all["Country"].unique())
sel_country  = st.sidebar.multiselect("Country", countries, default=countries[:5], help="Select countries to compare")

months    = list(range(1, 13))
mn_labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
sel_month = st.sidebar.multiselect("Month", months, default=months, format_func=lambda x: mn_labels[x-1])

weekdays    = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
sel_weekday = st.sidebar.multiselect("Weekday", weekdays, default=weekdays)

price_min, price_max = float(df_all["Price"].min()), float(df_all["Price"].quantile(0.99))
sel_price = st.sidebar.slider("Unit Price Range (£)", price_min, price_max,
                               (price_min, min(50.0, price_max)), step=0.5)

qty_min, qty_max = int(df_all["Quantity"].quantile(0.01)), int(df_all["Quantity"].quantile(0.99))
sel_qty = st.sidebar.slider("Quantity Range (per line)", qty_min, qty_max, (qty_min, qty_max))

# X and Y axis selector
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Chart Explorer")
dimensions = ["Sales","Quantity","Price"]
x_axis = st.sidebar.selectbox("X Axis",  ["MonthName","Country","Weekday","Year","Hour"], index=0)
y_axis = st.sidebar.selectbox("Y Axis",  dimensions, index=0)
agg_fn = st.sidebar.selectbox("Aggregation", ["sum","mean","median","count"], index=0)
chart_type = st.sidebar.radio("Chart Type", ["Bar","Line","Scatter"], horizontal=True)

# Apply all filters
df = df_all[
    df_all["Year"].isin(sel_year) &
    df_all["Country"].isin(sel_country) &
    df_all["Month"].isin(sel_month) &
    df_all["Weekday"].isin(sel_weekday) &
    df_all["Price"].between(sel_price[0], sel_price[1]) &
    df_all["Quantity"].between(sel_qty[0], sel_qty[1])
]

st.sidebar.markdown("---")
st.sidebar.markdown(f"**{len(df):,}** rows · **{df['Invoice'].nunique():,}** orders")

# ── Page ─────────────────────────────────────────────────────────────────────
page_header("🎛️ Interactive Filter Dashboard",
            "Slice and dice the data your way — adjust every filter in the sidebar")

if df.empty:
    st.warning("⚠️ No data matches your current filters. Please adjust the sidebar selections.")
    st.stop()

# ── Live KPIs ─────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5 = st.columns(5)
with k1: st.metric("Revenue",       f"£{df['Sales'].sum():,.0f}")
with k2: st.metric("Orders",        f"{df['Invoice'].nunique():,}")
with k3: st.metric("Customers",     f"{df['Customer ID'].nunique():,}")
with k4: st.metric("Unique Products",f"{df['StockCode'].nunique():,}")
with k5: st.metric("Avg Order £",   f"£{df.groupby('Invoice')['Sales'].sum().mean():,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Custom Chart Builder ──────────────────────────────────────────────────────
section_header(f"📊 {y_axis} by {x_axis} ({agg_fn}) — {chart_type} Chart")

grouped = getattr(df.groupby(x_axis)[y_axis], agg_fn)().reset_index()
grouped.columns = [x_axis, y_axis]

# Smart sort
month_order = ["January","February","March","April","May","June","July","August","September","October","November","December"]
day_order   = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
if x_axis == "MonthName":
    grouped[x_axis] = pd.Categorical(grouped[x_axis], categories=month_order, ordered=True)
    grouped = grouped.sort_values(x_axis)
elif x_axis == "Weekday":
    grouped[x_axis] = pd.Categorical(grouped[x_axis], categories=day_order, ordered=True)
    grouped = grouped.sort_values(x_axis)
else:
    grouped = grouped.sort_values(y_axis, ascending=False)

if chart_type == "Bar":
    fig = go.Figure(go.Bar(
        x=grouped[x_axis].astype(str), y=grouped[y_axis],
        marker=dict(color=PALETTE[:len(grouped)] if len(grouped) <= 10 else PRIMARY),
        hovertemplate=f"<b>%{{x}}</b><br>{y_axis}: %{{y:,.2f}}<extra></extra>"
    ))
elif chart_type == "Line":
    fig = go.Figure(go.Scatter(
        x=grouped[x_axis].astype(str), y=grouped[y_axis],
        mode="lines+markers",
        line=dict(color=PRIMARY, width=2.5),
        marker=dict(size=7, color=PRIMARY),
        fill="tozeroy", fillcolor="rgba(79,70,229,0.1)",
    ))
else:  # Scatter
    fig = go.Figure(go.Scatter(
        x=grouped[x_axis].astype(str), y=grouped[y_axis],
        mode="markers",
        marker=dict(size=12, color=grouped[y_axis],
                    colorscale="Viridis", showscale=True),
    ))

fig = styled_chart(fig, 400)
fig.update_xaxes(tickangle=-30)
st.plotly_chart(fig, use_container_width=True)

# ── Country comparison ────────────────────────────────────────────────────────
section_header("🌍 Country-by-Country Comparison")
monthly_country = (df.groupby(["Country","MonthName","Month"])["Sales"]
                     .sum().reset_index().sort_values("Month"))
fig2 = go.Figure()
for i, country in enumerate(sel_country[:8]):
    d = monthly_country[monthly_country["Country"] == country]
    fig2.add_trace(go.Scatter(
        x=d["MonthName"], y=d["Sales"],
        mode="lines+markers",
        name=country,
        line=dict(color=PALETTE[i % len(PALETTE)], width=2),
        marker=dict(size=5),
    ))
fig2 = styled_chart(fig2, 360)
st.plotly_chart(fig2, use_container_width=True)

# ── Raw data table ────────────────────────────────────────────────────────────
with st.expander("📋 View Filtered Raw Data (first 500 rows)"):
    display = df.head(500).copy()
    display["Sales"] = display["Sales"].map("£{:,.2f}".format)
    display["Price"] = display["Price"].map("£{:,.2f}".format)
    st.dataframe(display, use_container_width=True, height=400)

# ── Download ──────────────────────────────────────────────────────────────────
st.markdown("---")
col1, col2 = st.columns([1, 4])
with col1:
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="⬇️ Download Filtered Data",
        data=csv,
        file_name="retail_pulse_filtered.csv",
        mime="text/csv",
    )
with col2:
    st.markdown(f'<p style="color:#64748B;font-size:0.82rem;padding-top:0.6rem;">Exporting {len(df):,} rows based on current filter selection.</p>',
                unsafe_allow_html=True)
