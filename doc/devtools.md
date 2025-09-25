# Developer Utilities (devtools.py)

This module contains developer-focused utilities for splitting datasets, adding noise, and normalizing headers. These functions are intended for demo, testing, and ETL development, not for production usage.

## Purpose
- Split a raw dataset into multiple files in different formats (CSV/JSON).
- Introduce synthetic noise for testing.
- Normalize column headers to snake_case.
- Quick visualization/debug of data subsets.

## Functions

### normalize_header(name: str) -> str
Converts a column name to snake_case.

- Strips whitespace, lowercases, replaces non-alphanumeric characters with "_".
- Returns normalized string.

### split_dataset(input_csv, customers_csv, products_json, sales_csv) -> None
Splits a single CSV file into three parts: customers, products, and sales.

- Reads the CSV.
- Normalizes headers using normalize_header.
- Extracts:
  - customers.csv → customer_id, gender, age (duplicates removed)
  - products.json → product_category, price_per_unit (duplicates removed)
  - sales.csv → transaction_id, date, customer_id, product_category, quantity, total_amount
- Saves each part to the specified path.

### add_noise(input_path: Path, level: float = 0.1, write_file: bool = False) -> List[Any]
Introduces random noise into data for testing.

- Works for CSV or JSON (uses read_data from getdata.py).
- Noise types:
  - Replace some values with None.
  - Replace numeric values with strings or small lists of numbers.
  - Replace strings with random text or numbers.
  - Replace dates with randomly formatted current datetime.
- level determines the probability of corruption per value.
- write_file=True saves the noisy data to a new file alongside original.
- Returns the noisy data as a list of dicts (for JSON) or lists (for CSV).

## Dev Menu
The module integrates with DevMenu for quick interactive execution:

- Option 1 → Run split_dataset.
- Option 2 → Run add_noise on Data/customers.csv.

## Example Usage

```python
from devtools import split_dataset, add_noise
from pathlib import Path

# Split dataset
split_dataset(
    "Data/retail_sales_dataset.csv",
    "Data/customers.csv",
    "Data/products.json",
    "Data/sales.csv"
)

# Add noise to customers.csv
noisy = add_noise(
    input_path=Path("Data/customers.csv"),
    level=0.2,
    write_file=True)
```

## Notes

- Functions are for developer/testing purposes only.

- The noisy data helps test ETL pipelines for robustness.

- Header normalization ensures consistent column naming across modules.
