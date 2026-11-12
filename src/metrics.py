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

def product_ranking(sales, by="revenue"):
    return (sales.groupby("product")
                 .agg(revenue=("revenue", "sum"),
                      profit=("profit", "sum"),
                      quantity=("quantity", "sum"))
                 .round(2)
                 .sort_values(by, ascending=False))

def top_products(sales, by="revenue", n=10):
    return product_ranking(sales, by).head(n)

def bottom_products(sales, by="revenue", n=10):
    return product_ranking(sales, by).tail(n).sort_values(by)

ranking = product_ranking(sales)
ranking["margin_%"] = (ranking["profit"] / ranking["revenue"] * 100).round(1)



