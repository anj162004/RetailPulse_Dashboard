import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from utils import (set_page_config, inject_css, load_data,
                   apply_sidebar_filters, styled_chart, section_header,
                   page_header, PALETTE, PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER)

set_page_config("Executive Summary", "🛍️")
inject_css()

df_all = load_data()
df     = apply_sidebar_filters(df_all)

# ── Header ──────────────────────────────────────────────────────────────────
page_header("📊 Executive Summary Dashboard",
            "High-level performance overview · Online Retail II · 2009 – 2011")

# ── KPI Row ─────────────────────────────────────────────────────────────────
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric("Total Revenue", f"£{df['Sales'].sum():,.0f}")
with k2:
    st.metric("Total Orders", f"{df['Invoice'].nunique():,}")
with k3:
    st.metric("Customers", f"{df['Customer ID'].nunique():,}")
with k4:
    st.metric("Products", f"{df['StockCode'].nunique():,}")
with k5:
    aov = df.groupby("Invoice")["Sales"].sum().mean()
    st.metric("Avg Order Value", f"£{aov:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# ── Row 1: Revenue Trend + Revenue by Country ────────────────────────────────
c1, c2 = st.columns([3, 2])

with c1:
    section_header("📈 Monthly Revenue Trend")
    monthly = (df.groupby(["Year", "Month"])["Sales"].sum()
                 .reset_index()
                 .sort_values(["Year", "Month"]))
    monthly["Period"] = monthly["Year"].astype(str) + "-" + monthly["Month"].astype(str).str.zfill(2)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=monthly["Period"], y=monthly["Sales"],
        mode="lines+markers",
        line=dict(color=PRIMARY, width=2.5),
        marker=dict(size=5, color=PRIMARY),
        fill="tozeroy",
        fillcolor="rgba(79,70,229,0.12)",
        name="Revenue"
    ))
    fig = styled_chart(fig, 320)
    fig.update_xaxes(tickangle=-45, tickfont=dict(size=10))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    section_header("🌍 Revenue by Country (Top 10)")
    country = df.groupby("Country")["Sales"].sum().sort_values(ascending=False).head(10).reset_index()
    fig2 = go.Figure(go.Bar(
        x=country["Sales"], y=country["Country"],
        orientation="h",
        marker=dict(color=PALETTE[:10]),
    ))
    fig2 = styled_chart(fig2, 320)
    fig2.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Weekday + Hour heatmap ───────────────────────────────────────────
c3, c4 = st.columns(2)

with c3:
    section_header("📅 Revenue by Day of Week")
    day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
    weekday = df.groupby("Weekday")["Sales"].sum().reindex(day_order).reset_index()
    fig3 = go.Figure(go.Bar(
        x=weekday["Weekday"], y=weekday["Sales"],
        marker=dict(color=SECONDARY),
    ))
    fig3 = styled_chart(fig3, 300)
    st.plotly_chart(fig3, use_container_width=True)

with c4:
    section_header("⏰ Revenue by Hour of Day")
    hourly = df.groupby("Hour")["Sales"].sum().reset_index().sort_values("Hour")
    fig4 = go.Figure(go.Bar(
        x=hourly["Hour"].astype(str) + ":00",
        y=hourly["Sales"],
        marker=dict(color=ACCENT),
    ))
    fig4 = styled_chart(fig4, 300)
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3: Top products + YoY comparison ─────────────────────────────────────
c5, c6 = st.columns([2, 3])

with c5:
    section_header("🏆 Top 10 Products by Revenue")
    top_prod = (df.groupby("Description")["Sales"].sum()
                  .sort_values(ascending=False).head(10).reset_index())
    top_prod["Description"] = top_prod["Description"].str[:30]
    fig5 = go.Figure(go.Bar(
        x=top_prod["Sales"], y=top_prod["Description"],
        orientation="h",
        marker=dict(color=SUCCESS),
    ))
    fig5 = styled_chart(fig5, 350)
    fig5.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig5, use_container_width=True)

with c6:
    section_header("📊 Year-over-Year Revenue Comparison")
    yoy = df.groupby(["Year", "MonthName", "Month"])["Sales"].sum().reset_index().sort_values("Month")
    fig6 = go.Figure()
    colors_yoy = [PRIMARY, SECONDARY, ACCENT]
    for i, year in enumerate(sorted(yoy["Year"].unique())):
        d = yoy[yoy["Year"] == year]
        fig6.add_trace(go.Scatter(
            x=d["MonthName"], y=d["Sales"],
            mode="lines+markers",
            name=str(year),
            line=dict(color=colors_yoy[i], width=2),
            marker=dict(size=6),
        ))
    fig6 = styled_chart(fig6, 350)
    st.plotly_chart(fig6, use_container_width=True)

# ── Footer note ──────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<p style="color:#475569;font-size:0.75rem;text-align:center;">'
    'RetailPulse Dashboard · Built with Streamlit & Plotly · Data: Online Retail II (UCI ML Repository)'
    '</p>', unsafe_allow_html=True
)
