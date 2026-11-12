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

cakes = sales[sales["category"] == "cake"]
by_shop = cakes.groupby("shop").agg(revenue=("revenue", "sum"), profit=("profit", "sum"))
by_shop["margin_%"] = (by_shop["profit"] / by_shop["revenue"] * 100).round(1)

online = sales[sales["shop"] == "online"]

refunded = (online["status"] == "refunded").sum()
refund_rate = refunded / len(online) * 100
paid = online[online["status"].isin(["delivered", "refunded"])]
rate = (paid["status"] == "refunded").mean() * 100

refund_value = -online.loc[online["status"] == "refunded", "revenue"].sum()
gross_value = online.loc[online["status"] == "delivered", "revenue"].sum()

by_product = (paid.assign(refunded=paid["status"] == "refunded").groupby("product")["refunded"].mean().mul(100).round(1).sort_values(ascending=False))
monthly = (paid.assign(refunded=paid["status"] == "refunded").set_index("timestamp")["refunded"].resample("MS").mean().mul(100).round(1))

def add_revenue(df):
    df = df.copy()
    df["revenue"] = df["quantity"] * df["price"] * (1 - df["discount_pct"] / 100)
    df.loc[df["status"] == "cancelled", "revenue"] = 0
    return df

if __name__ == "__main__":
    sales = pd.read_csv("data/cleaned/sales.csv", parse_dates=["timestamp"])
    sales = add_revenue(sales)

def load_sales(path="data/cleaned/sales.csv"):
    sales = pd.read_csv(path)
    sales["timestamp"] = pd.to_datetime(sales["timestamp"].str.upper(), format="mixed", errors="coerce")
    sales = add_revenue(sales)
    sales["cost"] = sales["quantity"] * sales["unit_cost"]
    sales.loc[sales["status"].isin(["cancelled", "refunded"]), "cost"] = 0
    sales["profit"] = sales["revenue"] - sales["cost"]
    return sales

def filter_sales(sales, start, end, shops, categories):
    end_exclusive = pd.Timestamp(end) + pd.Timedelta(days=1)   # include whole end day
    mask = (
        (sales["timestamp"] >= pd.Timestamp(start))
        & (sales["timestamp"] < end_exclusive)
        & sales["shop"].isin(shops)
        & sales["category"].isin(categories)
    )
    return sales[mask]

def sales_by(df, freq):
    return (df.set_index("timestamp")
              .resample(freq)
              .agg(revenue=("revenue", "sum"),
                   profit=("profit", "sum"),
                   orders=("revenue", "count"))
              .round(2))


def sales_by_shop(df, freq):
    return (df.groupby(["shop", pd.Grouper(key="timestamp", freq=freq)])
              [["revenue", "profit"]]
              .sum()
              .round(2)
              .reset_index())

def product_ranking(df, by="revenue"):
    return (df.groupby("product")
              .agg(revenue=("revenue", "sum"),
                   profit=("profit", "sum"),
                   quantity=("quantity", "sum"))
              .round(2)
              .sort_values(by, ascending=False))


def top_products(df, by="revenue", n=5):
    return product_ranking(df, by).head(n)


def bottom_products(df, by="revenue", n=5):
    return product_ranking(df, by).tail(n).sort_values(by)

