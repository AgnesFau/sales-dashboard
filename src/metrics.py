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

def shop_summary(df):
    out = df.groupby("shop").agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
        orders=("status", lambda s: (s != "cancelled").sum()),
    )
    out["margin_%"] = (out["profit"] / out["revenue"] * 100).round(1)
    return out.round(2).sort_values("revenue", ascending=False).reset_index()

def sales_by_hour(df, by="revenue"):
    d = df.assign(hour=df["timestamp"].dt.hour)
    if by == "orders":
        d = d[d["status"] != "cancelled"]
        s = d.groupby(["shop", "hour"]).size()
    else:
        s = d.groupby(["shop", "hour"])[by].sum()
    table = s.unstack("shop").reindex(range(24)).fillna(0)
    table.index.name = "hour"
    return table.round(2)

def make_insights(df):
    insights = []

    shops = shop_summary(df)
    if len(shops) >= 2:
        worst = shops.loc[shops["margin_%"].idxmin()]
        best = shops.loc[shops["margin_%"].idxmax()]
        insights.append(
            f"**{worst['shop'].title()}** keeps only {worst['margin_%']:.0f} cents "
            f"of every dollar it sells. **{best['shop'].title()}** keeps "
            f"{best['margin_%']:.0f} cents."
        )

    total_revenue = df["revenue"].sum()
    total_profit = df["profit"].sum()
    cake = df[df["category"] == "cake"]
    if len(cake) and total_revenue > 0 and total_profit > 0:
        revenue_share = cake["revenue"].sum() / total_revenue * 100
        profit_share = cake["profit"].sum() / total_profit * 100
        insights.append(
            f"Cakes bring in {revenue_share:.0f}% of all sales "
            f"but only {profit_share:.0f}% of the profit."
        )

    hourly = sales_by_hour(df, "orders")
    parts = []
    shop_cols = [c for c in hourly.columns if c != "online"]
    if shop_cols and hourly[shop_cols].to_numpy().sum() > 0:
        parts.append(f"shops are busiest at {hourly[shop_cols].sum(axis=1).idxmax():02d}:00")
    if "online" in hourly.columns and hourly["online"].sum() > 0:
        parts.append(f"online orders peak at {hourly['online'].idxmax():02d}:00")
    if parts:
        insights.append(" while ".join(parts).capitalize() + ".")

    return insights