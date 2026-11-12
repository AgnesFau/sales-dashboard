# Bakery Sales Dashboard

A Streamlit dashboard for a made-up bakery owner who wants to know where her money comes from and where it leaks away.

## The problem

Mama Rosa has three shops and an online store, and each one exports its sales a different way.

Shop 1 puts the date and time in two columns. Shop 2 writes dates day first. Shop 3 writes them as text ("Jan 02, 2024 07:16 AM") and glues a dollar sign to the price. The online store adds discounts, refunds and cancelled orders. Across all four, product names have typos, some rows appear twice, and some prices are missing.

The brief was simple: she mostly guesses what sells. Clean the four files into one table, then give her a page she can read without touching code.

The data is not real. I generated it with a Python script and planted the mess on purpose, so I could check my cleaning against a known answer.

## What the dashboard shows

- Revenue, profit and order count at the top
- Sidebar filters for date range, shop and category
- Sales over time, by day, week or month, with an option to split by shop
- Top and bottom products by revenue, profit or units sold
- Revenue, profit and margin for each shop
- The busiest hour of the day
- An insights box that writes three plain sentences from whatever is filtered

## Run it

```bash
git clone <your-repo-url>
cd sales-dashboard
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
streamlit run dashboard.py
```

`python app.py` cleans the raw files and writes `data/cleaned/sales.csv`. The dashboard reads that file, so run it first. To run the checks:

```bash
pytest -v
```

## Cleaning: before and after

This is the online file. The same audit runs on the shop files.

| Check | Before | After |
|---|---|---|
| Rows | 6,065 | 6,000 |
| Missing values | 797 | 0 |
| Duplicate rows | 65 | 0 |
| Discounts outside 0 to 20% | 14 | 0 |
| Product names | 50 spellings | 12 |
| Negative prices | 305 | 303 (refunds, kept on purpose) |

TODO paste the shop 1, 2 and 3 tables from `data/reports/`

## Rules I had to pick

The data does not tell you what to do with a bad row. These are my calls, and anyone reading the numbers should know them.

- A cancelled order counts as zero revenue and zero cost.
- A refund stays in as a negative row, so it lowers revenue. Cost is zero on those rows, otherwise the loss would count twice.
- A quantity of 0, 500 or 999 is a typo, not a real sale. I set it to 1 and kept the row, because dropping it would lose a real sale.
- A discount outside 0 to 20% is an error and becomes 0.
- Missing prices come from the product list. Shop 2 is the exception: it sells cakes cheaper, so it uses its own usual price.
- In the shop files, two rows with the same time, product, quantity and price are one sale, even if the payment method differs.
- "Orders" means every row that is not cancelled. The shops have no order ID, so one row is one order line.

## What the data says

Over 18 months the business made about $278,000 in revenue and $146,000 in profit.

Shop 2 keeps about 39 cents of every dollar it sells. Shop 1 and shop 3 keep about 60, and online keeps about 51. Shop 2 sells its cakes roughly 45% under the list price.

Cakes bring in 55% of all sales but only 39% of the profit. They are the biggest line and the thinnest margin.

TODO add what the busiest-hour chart shows for the shops and for online

## What I learned

- `fillna(x.map(...))` lines up by row index. I mapped the product list instead of the orders, so only the first 12 rows could ever be filled and nothing seemed to change. My product file was also still capitalised while the sales were lowercase, so the lookup matched nothing. Now I print the NaN count before and after every fill.
- Order matters. Fix names first, then fill prices by name, then drop duplicates. Done the other way round, each step quietly fails.
- A negative number is not always an error. Online refunds are negative on purpose, and I almost "fixed" them.
- Duplicates are not always exact. The copies had a different payment method, so `drop_duplicates()` missed 56 of them until I told it which columns to compare.
- My "lowercase every text column" step turned the T in `2024-01-01T12:43:10` into a lowercase t, and the dates stopped parsing. A fix that touches every column can break one you never looked at.
- A CSV does not remember types. Dates come back as text unless I read them with `parse_dates`, and `resample` refuses to work on text.
- I once dropped rows with bad dates just to silence an error. That quietly deleted three whole shops. Now the code stops with an `assert` instead.
- Streamlit runs top to bottom. My filters did nothing until every number read from the filtered table and not the full one.

## Project layout

```
app.py            cleans the raw files and writes data/cleaned/sales.csv
dashboard.py      the Streamlit app
src/metrics.py    revenue, profit, rankings, filters, insights
tests/            pytest checks on the cleaned data
data/raw          the four sales files and products.csv
data/cleaned      output of app.py
data/reports      before and after tables
```

Built with Python, pandas, Streamlit, Plotly and pytest.
