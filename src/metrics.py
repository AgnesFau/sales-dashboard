import pandas as pd

sales = pd.read_csv("data/cleaned/sales.csv")
sales["revenue"] = sales["quantity"] * sales ["price"] * (1 - sales["discount_pct"]/100)

sales.loc[sales["status"] == "cancelled", "revenue"] = 0

sales["cost"] = sales["quantity"] * sales["unit_cost"]
sales.loc[sales["status"].isin(["cancelled", "refunded"]), "cost"] = 0
sales["profit"] = sales["revenue"] - sales["cost"]

sales.to_csv("data/sales_report.csv", index=False)

print(f"Revenue: {sales['revenue'].sum():,.2f}")
print(f"Profit: {sales['profit'].sum():,.2f}")

print(sales.groupby("shop")[["revenue", "profit"]].sum().round(2))
print(sales.groupby("category")[["revenue", "profit"]].sum().round(2))
