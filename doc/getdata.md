# ETL Helper Module (`getdata.py`)

This module provides functions for reading, detecting, and normalizing tabular data from **CSV** and **JSON** sources into **pandas DataFrames**.

---

## Purpose
- Detect the file format (CSV/JSON) with a lightweight check.
- Read file contents into Python structures.
- Normalize column values and entire Series based on heuristics or explicit metadata.
- Provide auxiliary parsers for numbers, dates, booleans, and text.

---

## Functions

### `detect_format(path: Path) -> str`
Detects the format of a file by inspecting its beginning.

- Returns `"csv"`, `"json"`, or `"unknown"`.
- Checks for JSON braces (`{` or `[`) and the presence of a single separator in CSV (`,` `;` `\t`).

---

### `read_data(path: Path) -> Tuple[str, List[dict[str, Any]]]`
Reads a CSV or JSON file.

- Determines the format using `detect_format`.
- Raises `DemoError` if file is larger than 10 MB (demo limitation).
- Returns a tuple `(format, list_of_rows)`.
- Each row is a dictionary mapping column names to values.

---

### Parsers

- `parse_number(val: str) -> Optional[float]`
  Converts strings to floats. Handles thousand separators, decimal commas, and ignores non-numeric symbols.

- `parse_date(val: str) -> Optional[str]`
  Converts date/time strings to `"YYYY-MM-DD"` or `"YYYY-MM-DD HH:MM:SS"`.

- `parse_bool(val: str) -> Optional[bool]`
  Converts "yes/no", "true/false", "1/0" strings to `True`/`False`.

- `normalize_text(val: str) -> Optional[str]`
  Cleans text: trims, lowers, replaces non-alphanumeric with underscores.

- `normalize_value(value: Any, column: str) -> Any`
  Auto-selects the appropriate parser based on column name heuristics.

---

### `normalize_column(values: pd.Series, target_name: str, dtype: type, format_spec: str = None, header_case: str = None) -> pd.Series`
Normalizes a pandas Series according to explicit metadata.

- `dtype`: target type (`int`, `float`, `str`, `"date"`, `"numeric"`).
- `format_spec`: optional formatting string (e.g., `":.2f"` or date format).
- `header_case`: normalizes the header name (`lower`, `capitalize`, `title`, `upper`).
- Returns a new Series with normalized values.

---

### `normalize_df(df: pd.DataFrame) -> pd.DataFrame`
Normalizes all columns of a DataFrame using `normalize_value` heuristics.

- Returns a new DataFrame with normalized values for all columns.

---

## Notes / Limitations
- Handles column-level normalization; does **not** remove duplicates or check cross-row constraints.
- Invalid conversions result in `None`.
- Designed for small-to-medium files (10 MB limit in demo mode).
- Heuristic-based parsing may require adjustment for domain-specific data.

---

## Example

```python
from pathlib import Path
from getdata import read_data, normalize_column, normalize_df

fmt, rows = read_data(Path("sales.csv"))

import pandas as pd
df = pd.DataFrame(rows)

# Normalize a single column
df["price"] = normalize_column(df["price"], target_name="price", dtype=float, format_spec=":.2f")

# Normalize entire DataFrame heuristically
df_norm = normalize_df(df)
