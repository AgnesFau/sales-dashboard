import streamlit as st
import plotly.express as px
from src.metrics import filter_sales, load_sales, sales_by, sales_by_shop

st.set_page_config(page_title="Mama Rosa's Bakery", layout="wide")

@st.cache_data
def get_data():
    return load_sales()

sales = get_data()

st.title("Mama Rosa's Bakery")
st.caption("Sales dashboard: 3 shops and the online store, Jan 2024 to Jun 2025")

st.sidebar.header("Filters")

min_date = sales["timestamp"].min().date()
max_date = sales["timestamp"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

all_shops = sorted(sales["shop"].unique())
shops = st.sidebar.multiselect("Shop", all_shops, default=all_shops)

all_categories = sorted(sales["category"].unique())
categories = st.sidebar.multiselect(
    "Category", all_categories, default=all_categories, format_func=str.title
)

if len(date_range) != 2:
    st.info("Pick an end date.")
    st.stop()

start, end = date_range

filtered = filter_sales(sales, start, end, shops, categories)

if filtered.empty:
    st.warning("No sales for these filters.")
    st.stop()

st.sidebar.write(f"Rows after filter: {len(filtered):,} of {len(sales):,}")

revenue = filtered["revenue"].sum()
profit = filtered["profit"].sum()
orders = (filtered["status"] != "cancelled").sum()
margin = profit / revenue * 100

col1, col2, col3 = st.columns(3)
col1.metric("Revenue", f"${revenue:,.0f}")
col2.metric("Profit", f"${profit:,.0f}", f"{margin:.0f}% margin", delta_color="off")
col3.metric("Orders", f"{orders:,}")

st.subheader("Sales over time")

left, right = st.columns(2)
group = left.radio("Group by", ["Day", "Week", "Month"], horizontal=True, index=2)
split = right.checkbox("Split by shop")

freq = {"Day": "D", "Week": "W", "Month": "MS"}[group]

if split:
    data = sales_by_shop(filtered, freq)
    fig = px.line(data, x="timestamp", y="revenue", color="shop")
else:
    data = sales_by(filtered, freq).reset_index()
    fig = px.line(data, x="timestamp", y="revenue")

fig.update_layout(
    xaxis_title=None,
    yaxis_title="Revenue ($)",
    hovermode="x unified",
    margin=dict(l=0, r=0, t=10, b=0),
)
st.plotly_chart(fig, width="stretch")