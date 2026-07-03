import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils import (set_page_config, inject_css, load_data, apply_sidebar_filters,
                   styled_chart, section_header, page_header,
                   PALETTE, PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER)

set_page_config("Profit & Revenue Analysis", "💰")
inject_css()
df_all = load_data()
df     = apply_sidebar_filters(df_all)

page_header("💰 Profit & Revenue Analysis", "Revenue breakdown, margins, and growth analysis by segment")

# Build metrics
total_rev  = df["Sales"].sum()
total_qty  = df["Quantity"].sum()
avg_price  = df["Price"].mean()
total_ord  = df["Invoice"].nunique()
revenue_pp = total_rev / total_qty if total_qty > 0 else 0

# KPIs
k1,k2,k3,k4,k5 = st.columns(5)
with k1: st.metric("Total Revenue",      f"£{total_rev:,.0f}")
with k2: st.metric("Total Units Sold",   f"{total_qty:,}")
with k3: st.metric("Avg Unit Price",     f"£{avg_price:.2f}")
with k4: st.metric("Revenue per Unit",   f"£{revenue_pp:.2f}")
with k5: st.metric("Revenue per Order",  f"£{total_rev/total_ord:,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# Cumulative revenue over time
section_header("📈 Cumulative Revenue Growth")
daily = df.groupby("InvoiceDate")["Sales"].sum().reset_index().sort_values("InvoiceDate")
daily["Cumulative"] = daily["Sales"].cumsum()
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=daily["InvoiceDate"], y=daily["Cumulative"],
    mode="lines", name="Cumulative Revenue",
    line=dict(color=SUCCESS, width=2.5),
    fill="tozeroy", fillcolor="rgba(16,185,129,0.1)",
))
fig = styled_chart(fig, 340)
st.plotly_chart(fig, use_container_width=True)

# Revenue by year + monthly breakdown
c1, c2 = st.columns(2)
with c1:
    section_header("📊 Annual Revenue")
    ann = df.groupby("Year")["Sales"].sum().reset_index()
    fig2 = go.Figure(go.Bar(
        x=ann["Year"].astype(str), y=ann["Sales"],
        marker=dict(color=[PRIMARY, SECONDARY, ACCENT]),
        text=ann["Sales"].map("£{:,.0f}".format),
        textposition="outside",
        textfont=dict(color="#CBD5E1"),
    ))
    fig2 = styled_chart(fig2, 300)
    st.plotly_chart(fig2, use_container_width=True)

with c2:
    section_header("🌍 Revenue Split: UK vs International")
    df["Region"] = df["Country"].apply(lambda x: "United Kingdom" if x == "United Kingdom" else "International")
    region_rev = df.groupby("Region")["Sales"].sum().reset_index()
    fig3 = go.Figure(go.Pie(
        labels=region_rev["Region"], values=region_rev["Sales"],
        marker=dict(colors=[PRIMARY, ACCENT]),
        hole=0.5,
    ))
    fig3 = styled_chart(fig3, 300)
    st.plotly_chart(fig3, use_container_width=True)

# Price band analysis
section_header("💷 Revenue by Price Band")
bins   = [0, 1, 5, 10, 25, 50, 100, 1000]
labels = ["<£1","£1–5","£5–10","£10–25","£25–50","£50–100",">£100"]
df["PriceBand"] = pd.cut(df["Price"], bins=bins, labels=labels)
pband = df.groupby("PriceBand", observed=True).agg(Revenue=("Sales","sum"), Units=("Quantity","sum")).reset_index()
c3, c4 = st.columns(2)
with c3:
    fig4 = go.Figure(go.Bar(
        x=pband["PriceBand"].astype(str), y=pband["Revenue"],
        marker=dict(color=PALETTE[:len(pband)]),
    ))
    fig4 = styled_chart(fig4, 300)
    fig4.update_layout(xaxis_title="Price Band", yaxis_title="Revenue (£)")
    st.plotly_chart(fig4, use_container_width=True)

with c4:
    fig5 = go.Figure(go.Bar(
        x=pband["PriceBand"].astype(str), y=pband["Units"],
        marker=dict(color=SECONDARY),
    ))
    fig5 = styled_chart(fig5, 300)
    fig5.update_layout(xaxis_title="Price Band", yaxis_title="Units Sold")
    st.plotly_chart(fig5, use_container_width=True)

# Revenue waterfall by year
section_header("🌊 Revenue Waterfall Year-over-Year")
ann_sorted = ann.sort_values("Year").reset_index(drop=True)
changes = [ann_sorted["Sales"].iloc[0]]
for i in range(1, len(ann_sorted)):
    changes.append(ann_sorted["Sales"].iloc[i] - ann_sorted["Sales"].iloc[i-1])
measure = ["absolute"] + ["relative"] * (len(changes) - 1)
text    = [f"£{v:,.0f}" for v in changes]
fig6 = go.Figure(go.Waterfall(
    x=ann_sorted["Year"].astype(str),
    y=changes,
    measure=measure,
    text=text,
    connector=dict(line=dict(color="#2D2D44")),
    increasing=dict(marker=dict(color=SUCCESS)),
    decreasing=dict(marker=dict(color=DANGER)),
    totals=dict(marker=dict(color=PRIMARY)),
))
fig6 = styled_chart(fig6, 320)
st.plotly_chart(fig6, use_container_width=True)
