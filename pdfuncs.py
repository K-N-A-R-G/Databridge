import pandas as pd

from getdata import normalize_header
from custom_types import buffer
from typing import Callable


__all__ = {}

def register(name: str, light=True, render='table'):
    """Decorator: assigns user-friendly name and auto-registers the function."""
    def wrapper(func: Callable):
        func.display_name = name
        func.light = light
        func.render = render
        __all__[func.__name__] = func
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


# === 3) CUSTOMER RETENTION ===
@register("Customer retention ratio", render="graph", light=False)
def customer_retention(df: pd.DataFrame, manual=True):
    df = normalize_df_columns(df)
    df = ensure_date(df)

    # 1. Логика расчетов
    df["first_purchase"] = df.groupby("customer_id")["date"].transform("min")
    df["is_repeat"] = df["date"] > df["first_purchase"]

    df['month'] = df['date'].dt.to_period('M')

    # Считаем долю repeat-клиентов
    grouped = df.groupby("month")["is_repeat"].mean().reset_index()

    # Для графиков Matplotlib лучше иметь Timestamp, а не Period
    grouped['month'] = grouped['month'].dt.to_timestamp()

    if manual:
        # В режиме превью возвращаем DataFrame (его напечатает run_action)
        return grouped

    # 2. ПРАВИЛЬНЫЙ ВЫЗОВ BUFFER
    # Просто передаем DataFrame целиком.
    # Buffer сам вытащит колонки и превратит строки в кортежи через itertuples.
    name = "Customer Retention Trend"
    buffer.set(grouped, name=name)


# === 4) AVG ORDER VALUE (AOV) ===
@register("Average Order Value (AOV)", light=True, render='value')
def aov_total(df: pd.DataFrame, manual: bool = True):
    df = normalize_df_columns(df)
    df = ensure_revenue(df)

    # Считаем одно число
    value = df["revenue"].mean().round(2)

    if manual:
        print(f"Total AOV: {value}")
        return value

    # Кладём в буфер как одно значение
    buffer.set(value, name="aov_total")


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
        print(grouped)
        return grouped
    buffer.set(grouped, "top_customers")


# === 6) MOUNYHLY REVENUE ===
@register("Monthly revenue trend", light=False, render='graph')
def monthly_revenue_trend(df: pd.DataFrame, manual: bool = True):
    df = normalize_df_columns(df)
    df = ensure_date(df)
    df = ensure_revenue(df)

    # Агрегация
    grouped = (
        df.assign(period=df["date"].dt.to_period("M"))
        .groupby("period", sort=True)["revenue"]
        .sum()
        .reset_index()
    )

    # Для графика нам нужны объекты Timestamp, а не периоды
    grouped["period"] = grouped["period"].dt.to_timestamp()

    if manual:
        print(grouped)
        return grouped

    # В буфер улетает чистый DataFrame.
    # Визуализатор сам поймет: X = 'period', Y = 'revenue'
    buffer.set(grouped, name="monthly_revenue")


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
