import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from utils import (set_page_config, inject_css, load_data, apply_sidebar_filters,
                   styled_chart, section_header, page_header,
                   PALETTE, PRIMARY, SECONDARY, ACCENT, SUCCESS, DANGER)

set_page_config("Product Performance", "🛒")
inject_css()
df_all = load_data()
df     = apply_sidebar_filters(df_all)

page_header("🛒 Product Performance Dashboard", "Revenue, quantity and order frequency by product")

prod = (df.groupby("Description")
          .agg(TotalSales=("Sales","sum"),
               TotalQty=("Quantity","sum"),
               AvgPrice=("Price","mean"),
               OrderCount=("Invoice","nunique"))
          .reset_index()
          .sort_values("TotalSales", ascending=False))

# KPIs
k1,k2,k3,k4 = st.columns(4)
with k1: st.metric("Total Products", f"{len(prod):,}")
with k2: st.metric("Top Product Revenue", f"£{prod['TotalSales'].iloc[0]:,.0f}")
with k3: st.metric("Avg Product Revenue", f"£{prod['TotalSales'].mean():,.0f}")
with k4: st.metric("Avg Price", f"£{prod['AvgPrice'].mean():,.2f}")

st.markdown("<br>", unsafe_allow_html=True)

# Top 15 by revenue + qty
c1, c2 = st.columns(2)
with c1:
    section_header("🏆 Top 15 Products by Revenue")
    top15 = prod.head(15).copy()
    top15["Desc"] = top15["Description"].str[:35]
    fig = go.Figure(go.Bar(
        x=top15["TotalSales"], y=top15["Desc"],
        orientation="h",
        marker=dict(color=PALETTE[:15]),
        hovertemplate="<b>%{y}</b><br>Revenue: £%{x:,.0f}<extra></extra>"
    ))
    fig = styled_chart(fig, 450)
    fig.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig, use_container_width=True)

with c2:
    section_header("📦 Top 15 Products by Quantity Sold")
    top15q = prod.sort_values("TotalQty", ascending=False).head(15).copy()
    top15q["Desc"] = top15q["Description"].str[:35]
    fig2 = go.Figure(go.Bar(
        x=top15q["TotalQty"], y=top15q["Desc"],
        orientation="h",
        marker=dict(color=SECONDARY),
        hovertemplate="<b>%{y}</b><br>Qty: %{x:,}<extra></extra>"
    ))
    fig2 = styled_chart(fig2, 450)
    fig2.update_layout(yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig2, use_container_width=True)

# Scatter: price vs quantity
section_header("🔍 Price vs Quantity — Product Scatter (Top 200)")
top200 = prod.head(200).copy()
top200["Desc"] = top200["Description"].str[:30]
fig3 = px.scatter(
    top200, x="AvgPrice", y="TotalQty",
    size="TotalSales", color="TotalSales",
    color_continuous_scale="Plasma",
    hover_name="Desc",
    labels={"AvgPrice":"Avg Price (£)","TotalQty":"Total Qty Sold","TotalSales":"Revenue"},
    size_max=40
)
fig3 = styled_chart(fig3, 380)
fig3.update_layout(coloraxis_colorbar=dict(tickfont=dict(color="#94A3B8"), title=dict(text="Revenue", font=dict(color="#94A3B8"))))
st.plotly_chart(fig3, use_container_width=True)

# Revenue share: top 20 vs rest
section_header("🥧 Revenue Concentration (Top 20 vs Others)")
top20_rev = prod.head(20)["TotalSales"].sum()
rest_rev  = prod.iloc[20:]["TotalSales"].sum()
fig4 = go.Figure(go.Pie(
    labels=["Top 20 Products", "Remaining Products"],
    values=[top20_rev, rest_rev],
    marker=dict(colors=[PRIMARY, "#2D2D44"]),
    hole=0.55,
))
fig4 = styled_chart(fig4, 300)
st.plotly_chart(fig4, use_container_width=True)

# Table
section_header("📋 Product Performance Table (Top 50)")
display = prod.head(50).copy()
display["Description"] = display["Description"].str[:45]
display["TotalSales"]  = display["TotalSales"].map("£{:,.2f}".format)
display["AvgPrice"]    = display["AvgPrice"].map("£{:,.2f}".format)
display["TotalQty"]    = display["TotalQty"].map("{:,}".format)
display["OrderCount"]  = display["OrderCount"].map("{:,}".format)
display.columns        = ["Description","Revenue","Qty Sold","Avg Price","Orders"]
st.dataframe(display.reset_index(drop=True), use_container_width=True, height=350)
