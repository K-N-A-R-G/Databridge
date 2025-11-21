import pandas as pd

from getdata import normalize_header
from custom_types import buffer
from typing import Callable


__all__ = []

def register(name: str):
    def wrapper(func: Callable):
        func.display_name = name
        __all__.append(func.__name__)
        return func
    return wrapper


def normalize_df_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [normalize_header(c) for c in df.columns]
    return df


# === 1) WEEKLY SALES TREND ===
@register("Weekly sales trend")
def weekly_sales_trend(df: pd.DataFrame, manual=True):
    df = normalize_df_columns(df)
    df = ensure_date(df)
    df = ensure_revenue(df)

    df["week"] = df["date"].dt.to_period("W")
    grouped = df.groupby("week")["revenue"].sum().reset_index()

    grouped["pct_change"] = grouped["revenue"].pct_change().round(3)
    if manual:
        print(grouped.head())
        return grouped
    buffer.set(grouped, "weekly_sales_trend")
    return grouped


# === 2) CATEGORY CONTRIBUTION ===
@register("Category revenue contribution")
def category_contribution(df: pd.DataFrame, manual=True):
    df = normalize_df_columns(df)
    df = ensure_revenue(df)

    grouped = (
        df.groupby("product_category")["revenue"]
          .sum()
          .sort_values(ascending=False)
          .reset_index()
    )

    grouped["share_pct"] = (grouped["revenue"] /
                            grouped["revenue"].sum() * 100).round(2)

    if manual:
        print(grouped)
        return grouped
    buffer.set(grouped, "category_contribution")
    return grouped


# === 3) CUSTOMER RETENTION ===
@register("Customer retention ratio")
def customer_retention(df: pd.DataFrame, manual=True):
    df = normalize_df_columns(df)
    df = ensure_date(df)

    df["first_purchase"] = df.groupby("customer_id")["date"].transform("min")
    df["is_repeat"] = df["date"] > df["first_purchase"]

    ratio = df["is_repeat"].mean()

    result = pd.DataFrame({"retention_ratio": [ratio]})

    if manual:
        print(result)
        return result
    buffer.set(result, "customer_retention")
    return result


# === 4) AVG ORDER VALUE (AOV) ===
@register("Average Order Value (AOV)")
def aov(df: pd.DataFrame, manual=True):
    df = normalize_df_columns(df)
    df = ensure_revenue(df)

    # every row = one purcharge, just average
    value = df["revenue"].mean()
    result = pd.DataFrame({"avg_order_value": [value]})

    if manual:
        print(result)
        return result
    buffer.set(result, "aov")
    return result


# === 5) SALES BY WEEKDAY ===
@register("Sales by weekday")
def sales_by_weekday(df: pd.DataFrame, manual=True):
    df = normalize_df_columns(df)
    df = ensure_date(df)
    df = ensure_revenue(df)

    df["weekday"] = df["date"].dt.day_name()

    grouped = df.groupby("weekday")["revenue"].sum().reset_index()

    # human-friendly weekday sorting
    ordered = ["Monday", "Tuesday", "Wednesday", "Thursday",
               "Friday", "Saturday", "Sunday"]

    grouped["weekday"] = pd.Categorical(grouped["weekday"], ordered)
    grouped = grouped.sort_values("weekday")

    if manual:
        print(grouped)
        return grouped
    buffer.set(grouped, "sales_by_weekday")
    return grouped


# === 6) TOP CUSTOMERS ===
@register("Top customers by revenue")
def top_customers(df: pd.DataFrame, manual=True, limit=10):
    df = normalize_df_columns(df)
    df = ensure_revenue(df)

    grouped = (
        df.groupby("customer_id")["revenue"]
          .sum()
          .sort_values(ascending=False)
          .reset_index()
          .head(limit)
    )

    if manual:
        # print(grouped)
        return grouped
    buffer.set(grouped, "top_customers")
    return grouped


# === BASE NORMALIZATION ===

def ensure_date(df, col="date"):
    """Safe datetime normalization for any 'date' column."""
    if col not in df.columns:
        raise KeyError(f"Column '{col}' not found in DataFrame")

    df = df.copy()

    # try fast path
    try:
        df[col] = pd.to_datetime(df[col], errors="raise")
        return df
    except Exception:
        pass

    # fallback for weird formats like "2023/11/24_Friday"
    cleaned = df[col].astype(str).str.extract(r"(\d{4}[-/]\d{2}[-/]\d{2})")[0]

    df[col] = pd.to_datetime(cleaned, errors="coerce")

    if df[col].isna().all():
        raise ValueError(f"Could not normalize '{col}' column")

    return df


def ensure_revenue(df):
    """Compute revenue column if it doesn't exist."""
    df = df.copy()

    if "revenue" in df.columns:
        return df

    required = ["quantity", "price_per_unit"]
    for col in required:
        if col not in df.columns:
            raise KeyError(f"Column '{col}' missing — cannot compute revenue")

    df["revenue"] = (
        df["quantity"].astype(float) * df["price_per_unit"].astype(float)
    )

    return df


def ensure_numeric(df, col):
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df
