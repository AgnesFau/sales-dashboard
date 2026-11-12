from pathlib import Path
import pandas as pd
import pytest

SALES_CSV = Path(__file__).parent.parent / "data" / "cleaned" / "sales.csv"
PRODUCTS_CSV = Path(__file__).parent.parent / "data" / "cleaned" / "products_cleaned.csv"

@pytest.fixture(scope="module")
def sales():
    return pd.read_csv(SALES_CSV, parse_dates=["timestamp"])

@pytest.fixture(scope="module")
def products():
    return pd.read_csv(PRODUCTS_CSV)


def test_no_duplicates(sales):
    key = ["timestamp", "shop", "product", "quantity", "price"]
    assert sales.duplicated(subset=key).sum() == 0


def test_product_names_are_valid(sales, products):
    unknown = set(sales["product"]) - set(products["product"])
    assert unknown == set()


def test_no_nulls_in_key_columns(sales):
    key_cols = ["timestamp", "shop", "product", "quantity", "price"]
    assert sales[key_cols].isna().sum().sum() == 0