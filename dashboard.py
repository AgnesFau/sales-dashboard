import streamlit as st

from src.metrics import load_sales

st.set_page_config(page_title="Mama Rosa's Bakery", layout="wide")


@st.cache_data
def get_data():
    return load_sales()


sales = get_data()

st.title("Mama Rosa's Bakery")
st.caption("Sales dashboard: 3 shops and the online store, Jan 2024 to Jun 2025")

# ---------- KPI row ----------
revenue = sales["revenue"].sum()
profit = sales["profit"].sum()
orders = (sales["status"] != "cancelled").sum()
margin = profit / revenue * 100

col1, col2, col3 = st.columns(3)
col1.metric("Revenue", f"${revenue:,.0f}")
col2.metric("Profit", f"${profit:,.0f}", f"{margin:.0f}% margin", delta_color="off")
col3.metric("Orders", f"{orders:,}")