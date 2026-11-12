import pandas as pd

sales = pd.read_csv("data/cleaned/sales.csv")
sales["revenue"] = sales["quantity"] * sales ["price"] * (1 - sales["discount_pct"]/100)

sales.loc[sales["status"] == "cancelled", "revenue"] = 0

sales["cost"] = sales["quantity"] * sales["unit_cost"]
sales.loc[sales["status"].isin(["cancelled", "refunded"]), "cost"] = 0
sales["profit"] = sales["revenue"] - sales["cost"]

sales.to_csv("data/sales_report.csv", index=False)

sales["timestamp"] = pd.to_datetime(sales["timestamp"].str.upper(), errors="coerce")

def sales_by(freq):
    return (sales.set_index("timestamp").resample(freq).agg(revenue=("revenue", "sum"), profit=("profit", "sum"), orders=("revenue", "count")).round(2))

daily = sales_by("D")
weekly = sales_by("W")
monthly = sales_by("MS")