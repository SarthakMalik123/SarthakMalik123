from __future__ import annotations
import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px


def kpi_card(title: str, value: str | float, col):
    with col:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">{title}</div>
                <div class="kpi-value">{value}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def risk_distribution_chart(df: pd.DataFrame, title: str):
    counts = df["risk_level"].value_counts().reset_index()
    counts.columns = ["risk_level", "count"]
    chart = alt.Chart(counts).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
        x=alt.X("risk_level:N", sort=["Low", "Medium", "High"], title=None),
        y=alt.Y("count:Q", title=None),
        color=alt.Color("risk_level:N", scale=alt.Scale(domain=["Low", "Medium", "High"], range=["#10B981", "#F59E0B", "#EF4444"]), legend=None),
        tooltip=["risk_level", "count"],
    ).properties(height=260, title=title)
    st.altair_chart(chart, use_container_width=True)


def products_by_risk_pie(df: pd.DataFrame, title: str):
    data = df.groupby("product")["risk_level"].apply(lambda s: (s=="High").mean()).reset_index(name="high_risk_ratio")
    fig = px.pie(data, names="product", values="high_risk_ratio", title=title, color_discrete_sequence=px.colors.sequential.Blues)
    st.plotly_chart(fig, use_container_width=True)