"""
Developer utilities for demo and testing.
"""

__all__ = ["split_dataset", "add_noise"]

from devmenu import DevMenu
from datetime import datetime
from getdata import read_data
from pathlib import Path
from typing import Any, List, Tuple, Union, Optional
import json
import pandas as pd
import random
import re
import string as st


def normalize_header(name: str) -> str:
    """Convert column names to snake_case."""
    name = name.strip().lower()
    name = re.sub(r"[^0-9a-z.]+", "_", name)
    return name.strip("_")


def split_dataset(input_csv: Union[str, Path],
                  customers_csv: Union[str, Path],
                  products_json: Union[str, Path],
                  sales_csv: Union[str, Path]) -> None:
    """
    Split dataset into customers, products, and sales.
    """
    df = pd.read_csv(input_csv)

    # normalize headers
    print("\n--- DEBUG split_dataset ---")
    print("Raw columns:", list(df.columns))
    df.columns = [normalize_header(c) for c in df.columns]
    print("Normalized columns:", list(df.columns))
    print(df.head(3))
    print("--- END DEBUG ---\n")

    # customers
    customers = df[["customer_id", "gender", "age"]].drop_duplicates()
    customers.to_csv(customers_csv, index=False)

    # products
    products = df[["product_category", "price_per_unit"]].drop_duplicates()
    with open(products_json, "w", encoding="utf-8") as f:
        json.dump(products.to_dict(orient="records"), f,
                  ensure_ascii=False, indent=2)

    # sales
    sales = df[["transaction_id", "date", "customer_id",
                "product_category", "quantity", "total_amount"]]
    sales.to_csv(sales_csv, index=False)

    print("Split done:")
    print(f"  {customers_csv}")
    print(f"  {products_json}")
    print(f"  {sales_csv}")


def add_noise(
    input_path: Path,
    level: float = 0.1,
    write_file: bool = False
) -> List[Any]:
    """
    Corrupt data with random noise (demo).
    """
    fmt, records = read_data(input_path)

    noisy_data: List[Any] = []
    date_formats = ["%Y-%m-%d", "%d/%m/%Y", "%m-%d-%Y"]

    for record in records:
        if isinstance(record, dict):
            new_rec = record.copy()
            for k, val in new_rec.items():
                if random.random() < level:
                    if random.random() < 0.3:
                        new_rec[k] = None
                    elif isinstance(val, (int, float)):
                        new_rec[k] = str(val) if random.random() < 0.5 else \
                                     [random.randint(0, 10) for _ in range(random.randint(1,3))]
                    elif isinstance(val, str):
                        choice = random.random()
                        if choice < 0.33:
                            new_rec[k] = random.random() * 100
                        elif choice < 0.66:
                            new_rec[k] = "".join(random.choices(st.ascii_lowercase, k=5))
                        else:
                            new_rec[k] = datetime.now().strftime(random.choice(date_formats))
            noisy_data.append(new_rec)
        else:
            new_row = []
            for val in record:
                if random.random() < level:
                    if isinstance(val, (int, float)):
                        new_row.append(str(val))
                    elif isinstance(val, str):
                        new_row.append(random.random() * 100)
                    else:
                        new_row.append(None)
                else:
                    new_row.append(val)
            noisy_data.append(new_row)

    if write_file and input_path and fmt:
        out_path = Path(input_path).with_stem(Path(input_path).stem + "_noisy")
        if fmt == "json":
            with out_path.open("w", encoding="utf-8") as f:
                json.dump(noisy_data, f, ensure_ascii=False, indent=2)
        elif fmt == "csv":
            pd.DataFrame(noisy_data).to_csv(out_path, index=False)
        print(f"Noisy data written to {out_path}")

    return noisy_data


# --- Dev Menu ---------------------------------------------------------

menu_actions = {
    "1": ("",
        split_dataset, (
        "Data/retail_sales_dataset.csv",
        "Data/customers.csv",
        "Data/products.json",
        "Data/sales.csv"),
        {}),
    "2": ("",
        add_noise,
        (),
        {
         "input_path": Path("Data/customers.csv"),
         "level": 0.2,
         "write_file": True
        }),
}


DevMenu(menu_actions, title="DevTools Menu").run()  # type: ignore

