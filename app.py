import pandas as pd

online_orders = pd.read_csv('data/raw/online_orders.csv')
products = pd.read_csv('data/raw/products.csv')
shop1_sales = pd.read_csv('data/raw/shop1_sales.csv')
shop2_sales = pd.read_csv('data/raw/shop2_sales.csv')
shop3_sales = pd.read_csv('data/raw/shop3_sales.csv')

def audit(df, name='deafult'):
    data = {
        "file": name,
        "rows": len(df),
        "missing_values": int(df.isna().sum().sum()),
        "duplicated": int(df.duplicated().sum()),
        "negative_prices": int((df['price'] < 0).sum()),
        "odd_qty": int((~df['quantity'].between(1,20)).sum()),
        "odd_discounts": int((~df['discount_pct'].between(0,20)).sum()),
        "unique_products": int(df['product'].nunique())
    }
    return data

before = [audit(online_orders, "online")]
tabel_bfr = pd.DataFrame(before)
tabel_bfr.to_csv("data/reports/online_order_report.csv")

def formatting(df):
    for column in df.select_dtypes(include=["object", "string"]).columns:
        df[column] = df[column].str.lower().str.strip()
    return df

online_orders = formatting(online_orders)
products = formatting(products)
shop1_sales = formatting(shop1_sales)
shop2_sales = formatting(shop2_sales)
shop3_sales = formatting(shop3_sales)

def info(df):
    print(df.head())
    print(df.columns.tolist())
    print(df.info())
    print(df.describe())
    for column in df.columns:
        print(f"\nColumn: {column}")
        print(df[column].value_counts(dropna=False))

PRODUCT_CORRECTION = {
    "b-day cake": "birthday cake",
    "birthday  cake": "birthday cake",
    "choc cake": "chocolate cake",
    "cookies": "cookie",
    "blue berry muffin": "blueberry muffin",
    "cheesecake": "cheesecake slice",
    "cinamon roll": "cinnamon roll",
    "late": "latte",
    "rye": "rye bread",
    "baguete": "baguette",
    "sourdough": "sourdough loaf",
    "blueberry muffn": "blueberry muffin",
    "expresso": "espresso",
    "cheese cake slice": "cheesecake slice",
    "sour dough loaf": "sourdough loaf",
    "croisant": "croissant"
}

online_orders["product"] = online_orders["product"].str.strip().str.lower().str.replace(r"\s+", " ", regex=True).replace(PRODUCT_CORRECTION)
online_orders = online_orders.dropna(subset=["product", "quantity", "timestamp"])
online_orders['city'] = online_orders['city'].fillna("unknown")

online_orders['price'] = online_orders['price'].fillna(online_orders['product'].map(products.set_index('product')['list_price']))
online_orders.loc[~online_orders['discount_pct'].between(0,20), "discount_pct"] = 0

online_orders = online_orders.drop_duplicates()

after = pd.DataFrame([audit(online_orders, "online")])
result = tabel_bfr.merge(after, on="file", suffixes=("_before", "_after"))

metrics = ["rows", "missing_values", "duplicated", "negative_prices", "odd_qty", "odd_discounts", "unique_products"]

report = pd.DataFrame({
    "metric": metrics,
    "before": [result[f"{m}_before"].iloc[0] for m in metrics],
    "after":  [result[f"{m}_after"].iloc[0] for m in metrics],
})
report["fixed"] = report["before"] - report["after"]
report.to_csv("data/reports/online_report.csv", index=False)

online_orders.to_csv('data/cleaned/online_cleaned.csv', index=False)