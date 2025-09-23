from custom_types import DemoError
from datetime import datetime
from pathlib import Path
from typing import Any, List, Tuple, Optional

import csv
import json
import pandas as pd


def detect_format(path: Path) -> str:
    """Detect file format by lightweight content inspection."""
    with path.open("r", encoding="utf-8") as f:
        head = f.read(2048).lstrip()
        if head.startswith(("{", "[")):
            return "json"
        elif sum(x in head for x in ",;\t") == 1:
            return "csv"
        return "unknown"


def read_data(path: Path) -> Tuple[str, List[dict[str, Any]]]:
    """Read data from a CSV or JSON file depending on detected format."""

    fmt = detect_format(path)

    # --- demo limitation: file size ---
    max_size = 10 * 1024 * 1024  # 10 MB
    if path.stat().st_size > max_size:
        raise DemoError(
            f"streaming read for large files (>10 MB) in format '{fmt}'"
        )

    if fmt == "json":
        with path.open("r", encoding="utf-8") as f:
            return fmt, json.load(f)
    elif fmt == "csv":
        with path.open("r", encoding="utf-8") as f:
            return fmt, list(csv.DictReader(f))
    else:
        raise ValueError(f"Unsupported file format: {path}")


# --- helpers ---
def parse_number(val: str) -> Optional[float]:
    """Convert strings with digits, separators, currency symbols to float."""
    if val is None:
        return None
    val = str(val).strip()
    if val.lower() in {"", "null", "nan", "n/a", "-"}:
        return None
    # remove currency symbols and spaces
    val = re.sub(r"[^\d.,-]", "", val)
    # replace comma with dot if comma used as decimal
    if val.count(",") == 1 and val.count(".") == 0:
        val = val.replace(",", ".")
    # remove thousand separators
    val = val.replace(",", "")
    try:
        return float(val)
    except ValueError:
        return None


def parse_date(val: str) -> Optional[str]:
    """Convert various date/time strings to YYYY-MM-DD or YYYY-MM-DD HH:MM:SS"""
    if val is None:
        return None
    val = str(val).strip()
    if val.lower() in {"", "null", "nan", "n/a", "-"}:
        return None
    try:
        dt = pd.to_datetime(val, errors="coerce", dayfirst=True)
        if pd.isna(dt):
            return None
        # If time is 00:00:00, drop time
        if dt.time() == datetime.min.time():
            return dt.strftime("%Y-%m-%d")
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return None


def parse_bool(val: str) -> Optional[bool]:
    """Convert Yes/No, True/False, 1/0 to True/False"""
    if val is None:
        return None
    val = str(val).strip().lower()
    if val in {"true", "yes", "y", "1"}:
        return True
    elif val in {"false", "no", "n", "0"}:
        return False
    else:
        return None


# --- main normalizer ---
def normalize_value(value: Any, column: str) -> Any:
    """Normalize single value based on column name heuristics"""
    col = column.lower()
    if any(x in col for x in ("date", "time")):
        return parse_date(value)
    elif any(x in col for x in ("price", "amount", "total", "quantity")):
        return parse_number(value)
    elif any(x in col for x in ("gender", "yes_no", "active")):
        return parse_bool(value)
    else:
        return normalize_text(value)


def normalize_text(val: str) -> Optional[str]:
    """Clean text: strip, lowercase, replace non-alphanum with _"""
    if val is None:
        return None
    val = str(val).strip()
    if val.lower() in {"", "null", "nan", "n/a", "-"}:
        return None
    val = val.lower()
    # replace non-alphanumeric with "_"
    val = re.sub(r"[^a-z0-9]+", "_", val)
    val = val.strip("_")
    return val


def normalize_column(values: pd.Series, target_name: str, dtype: type,
                     format_spec: str = None, header_case: str = None) -> pd.Series:
    """
    Normalize a pandas Series according to metadata.

    - values: original column values
    - target_name: target header name
    - dtype: target type (str, int, float, date)
    - format_spec: formatting string, e.g. ":.2f" or date format
    - header_case: 'lower', 'capitalize', 'title', 'upper' for column name normalization

    Returns a new Series with normalized values.
    """
    # Normalize header (just for reference, actual header rename handled elsewhere)
    if header_case in ('lower', 'capitalize', 'title', 'upper'):
        normalized_name = getattr(target_name, header_case)()
    else:
        normalized_name = target_name

    # Normalize values
    series = values.copy()

    if dtype == "numeric":
        series = pd.to_numeric(series, errors="coerce")
    elif dtype == int:
        series = pd.to_numeric(series, errors="coerce").astype("Int64")
    elif dtype == float:
        series = pd.to_numeric(series, errors="coerce").astype(float)
        if format_spec:
            series = series.map(
                lambda x: format(x, format_spec) if pd.notnull(x) else x
            )
    elif dtype == str:
        series = series.astype(str)
    elif dtype == "date" or dtype.__name__ == "date":
        # convert to datetime
        series = pd.to_datetime(series, errors="coerce")
        if format_spec:
            series = series.dt.strftime(format_spec)
    else:
        series = series  # fallback, leave as-is

    return series


# --- normalize dataframe ---
def normalize_df(df: pd.DataFrame) -> pd.DataFrame:
    df_norm = df.copy()
    for col in df_norm.columns:
        df_norm[col] = df_norm[col].apply(lambda v: normalize_value(v, col))
    return df_norm
