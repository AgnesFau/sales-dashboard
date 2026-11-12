import pandas as pd

# Load Data
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

def info(df):
    print(df.head())
    print(df.columns.tolist())
    print(df.info())
    print(df.describe())
    for column in df.columns:
        print(f"\nColumn: {column}")
        print(df[column].value_counts(dropna=False))

def formatting(df):
    for column in df.select_dtypes(include=["object", "string"]).columns:
        df[column] = df[column].str.lower().str.strip()
    return df

# Online Orders Data Cleaning
before = [audit(online_orders, "online")]
tabel_bfr = pd.DataFrame(before)

online_orders = formatting(online_orders)
products = formatting(products)
shop1_sales = formatting(shop1_sales)
shop2_sales = formatting(shop2_sales)
shop3_sales = formatting(shop3_sales)

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

# Products Data Cleaning
products.to_csv('data/cleaned/products_cleaned.csv', index=False)

# Shop 1 Sales Data Cleaning
shop1_sales = shop1_sales.rename(columns={
    "qty": "quantity",
    "unit_price": "price"
})
shop1_sales["product"] = shop1_sales["product"].str.strip().str.lower().str.replace(r"\s+", " ", regex=True).replace(PRODUCT_CORRECTION)
shop1_sales["timestamp"] = pd.to_datetime(
    shop1_sales["date"] + " " + shop1_sales["time"],
    format="%Y-%m-%d %H:%M",
    errors="coerce",
)
shop1_sales = shop1_sales.drop(columns=["date", "time"])
shop1_sales.loc[shop1_sales["price"] < 0, "price"] = pd.NA
shop1_sales['price'] = shop1_sales['price'].fillna(shop1_sales['product'].map(products.set_index('product')['list_price']))

shop1_sales.loc[~shop1_sales["quantity"].between(1, 20), "quantity"] = 1
shop1_sales = shop1_sales.drop_duplicates(subset=["timestamp", "product", "quantity", "price"])

shop1_sales.to_csv('data/cleaned/shop1_sales_cleaned.csv', index=False)

# Shop 2 Sales Data Cleaning
shop2_sales = shop2_sales.rename(columns={
    "Sale Date": "timestamp",
    "Item": "product",
    "Quantity": "quantity",
    "Price Each": "price",
    "Paid By": "payment"
})
shop2_sales["product"] = shop2_sales["product"].str.strip().str.lower().str.replace(r"\s+", " ", regex=True).replace(PRODUCT_CORRECTION)
shop2_sales["timestamp"] = pd.to_datetime(
    shop2_sales["timestamp"],
    format="%d/%m/%Y %H:%M",
    errors="coerce",
)

shop2_sales.loc[shop2_sales["price"] < 0, "price"] = pd.NA
shop2_sales['price'] = shop2_sales['price'].fillna(shop2_sales['product'].map(products.set_index('product')['list_price']))

shop2_sales.loc[~shop2_sales["quantity"].between(1, 20), "quantity"] = 1
shop2_sales = shop2_sales.drop_duplicates(subset=["timestamp", "product", "quantity", "price"])

shop2_sales.to_csv('data/cleaned/shop2_sales_cleaned.csv', index=False)

# Shop 3 Sales Data Cleaning
shop3_sales = shop3_sales.rename(columns={
    "sold_at": "timestamp",
    "product_name": "product",
    "units": "quantity",
    "pay_type": "payment"
})
shop3_sales["product"] = shop3_sales["product"].str.strip().str.lower().str.replace(r"\s+", " ", regex=True).replace(PRODUCT_CORRECTION)
shop3_sales["timestamp"] = pd.to_datetime(
    shop3_sales["timestamp"],
    format="%b %d, %Y %I:%M %p",
    errors="coerce",
)

shop3_sales["price"] = pd.to_numeric(shop3_sales["price"].str.replace("$", "", regex=False), errors="coerce")
shop3_sales.loc[shop3_sales["price"] < 0, "price"] = pd.NA
shop3_sales['price'] = shop3_sales['price'].fillna(shop3_sales['product'].map(products.set_index('product')['list_price']))

shop3_sales.loc[~shop3_sales["quantity"].between(1, 20), "quantity"] = 1
shop3_sales = shop3_sales.drop_duplicates(subset=["timestamp", "product", "quantity", "price"])

shop3_sales.to_csv("data/cleaned/shop3_sales_cleaned.csv", index=False)