import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from utils import (set_page_config, inject_css, load_data, apply_sidebar_filters,
                   styled_chart, section_header, page_header,
                   PALETTE, PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER)

set_page_config("Inventory Risk", "⚠️")
inject_css()
df_all = load_data()
df     = apply_sidebar_filters(df_all)

page_header("⚠️ Inventory Risk Dashboard", "Slow movers, high-value risk items, and stock concentration")

prod = (df.groupby(["StockCode","Description"])
          .agg(TotalQty=("Quantity","sum"),
               TotalSales=("Sales","sum"),
               AvgPrice=("Price","mean"),
               OrderCount=("Invoice","nunique"),
               Months=("Month","nunique"))
          .reset_index())

# Risk classification
p75_qty   = prod["TotalQty"].quantile(0.75)
p75_price = prod["AvgPrice"].quantile(0.75)

def classify_risk(row):
    if row["TotalQty"] < prod["TotalQty"].quantile(0.25) and row["AvgPrice"] > p75_price:
        return "🔴 High Risk"
    elif row["TotalQty"] < prod["TotalQty"].quantile(0.25):
        return "🟠 Slow Mover"
    elif row["OrderCount"] <= 1:
        return "🟡 One-off"
    elif row["TotalQty"] >= p75_qty and row["AvgPrice"] >= p75_price:
        return "🟢 Star Product"
    else:
        return "⚪ Normal"

prod["RiskCategory"] = prod.apply(classify_risk, axis=1)

# KPIs
high_risk  = prod[prod["RiskCategory"] == "🔴 High Risk"]
slow_mover = prod[prod["RiskCategory"] == "🟠 Slow Mover"]
one_off    = prod[prod["RiskCategory"] == "🟡 One-off"]
stars      = prod[prod["RiskCategory"] == "🟢 Star Product"]
k1,k2,k3,k4 = st.columns(4)
with k1: st.metric("🔴 High Risk Products", f"{len(high_risk):,}", f"£{high_risk['TotalSales'].sum():,.0f} tied")
with k2: st.metric("🟠 Slow Movers",        f"{len(slow_mover):,}")
with k3: st.metric("🟡 One-off Products",    f"{len(one_off):,}")
with k4: st.metric("🟢 Star Products",       f"{len(stars):,}")

st.markdown("<br>", unsafe_allow_html=True)

# Risk distribution
c1, c2 = st.columns(2)
with c1:
    section_header("🥧 Product Risk Distribution")
    risk_counts = prod["RiskCategory"].value_counts().reset_index()
    risk_counts.columns = ["Category","Count"]
    fig = go.Figure(go.Pie(
        labels=risk_counts["Category"], values=risk_counts["Count"],
        marker=dict(colors=[DANGER, ACCENT, "#F59E0B", SUCCESS, "#6B7280"]),
        hole=0.5,
    ))
    fig = styled_chart(fig, 320)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    section_header("📦 Revenue by Risk Category")
    risk_rev = prod.groupby("RiskCategory")["TotalSales"].sum().reset_index().sort_values("TotalSales", ascending=False)
    fig2 = go.Figure(go.Bar(
        x=risk_rev["TotalSales"], y=risk_rev["RiskCategory"],
        orientation="h",
        marker=dict(color=[DANGER, SUCCESS, "#F59E0B", ACCENT, "#6B7280"][:len(risk_rev)]),
    ))
    fig2 = styled_chart(fig2, 320)
    fig2.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig2, use_container_width=True)

# Scatter: Qty vs Price coloured by risk
section_header("🔍 Qty vs Price Risk Matrix")
plot_prod = prod[prod["AvgPrice"] <= prod["AvgPrice"].quantile(0.98)].copy()
plot_prod["Desc"] = plot_prod["Description"].str[:30]
risk_color_map = {
    "🔴 High Risk": DANGER,
    "🟠 Slow Mover": ACCENT,
    "🟡 One-off": "#F59E0B",
    "🟢 Star Product": SUCCESS,
    "⚪ Normal": "#6B7280",
}
fig3 = px.scatter(
    plot_prod, x="AvgPrice", y="TotalQty",
    color="RiskCategory",
    color_discrete_map=risk_color_map,
    size="TotalSales",
    hover_name="Desc",
    labels={"AvgPrice":"Avg Price (£)","TotalQty":"Total Qty","RiskCategory":"Risk"},
    size_max=30, opacity=0.75,
)
fig3 = styled_chart(fig3, 400)
st.plotly_chart(fig3, use_container_width=True)

# High risk table
section_header("🔴 High Risk Products — Detail Table")
hr_display = high_risk.sort_values("AvgPrice", ascending=False).head(30).copy()
hr_display["Description"] = hr_display["Description"].str[:45]
hr_display["TotalSales"]  = hr_display["TotalSales"].map("£{:,.2f}".format)
hr_display["AvgPrice"]    = hr_display["AvgPrice"].map("£{:,.2f}".format)
hr_display["TotalQty"]    = hr_display["TotalQty"].map("{:,}".format)
hr_display = hr_display[["StockCode","Description","TotalQty","AvgPrice","TotalSales","OrderCount"]]
hr_display.columns = ["StockCode","Description","Qty","Avg Price","Revenue","Orders"]
st.dataframe(hr_display.reset_index(drop=True), use_container_width=True, height=350)

# Pareto / concentration
section_header("📊 Revenue Concentration (Pareto)")
prod_sorted = prod.sort_values("TotalSales", ascending=False).reset_index(drop=True)
prod_sorted["CumSales"] = prod_sorted["TotalSales"].cumsum()
prod_sorted["CumPct"]   = prod_sorted["CumSales"] / prod_sorted["TotalSales"].sum() * 100
prod_sorted["ProdPct"]  = (prod_sorted.index + 1) / len(prod_sorted) * 100

fig4 = go.Figure()
fig4.add_trace(go.Scatter(
    x=prod_sorted["ProdPct"], y=prod_sorted["CumPct"],
    mode="lines", name="Cumulative Revenue %",
    line=dict(color=PRIMARY, width=2.5),
    fill="tozeroy", fillcolor="rgba(79,70,229,0.12)",
))
fig4.add_vline(x=20, line_color=ACCENT, line_dash="dot", annotation_text="20% of products",
               annotation_font=dict(color=ACCENT))
fig4.add_hline(y=80, line_color=DANGER, line_dash="dot", annotation_text="80% revenue",
               annotation_font=dict(color=DANGER))
fig4 = styled_chart(fig4, 330)
fig4.update_layout(xaxis_title="% of Products", yaxis_title="% of Revenue")
st.plotly_chart(fig4, use_container_width=True)
