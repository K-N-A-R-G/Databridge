from custom_types import buffer
from typing import Callable, Optional

import sqlite3
import pandas as pd


__all__ = []   # ← functions will be added automatically


def register(name: str):
    """Decorator: assigns user-friendly name and auto-registers the function."""
    def wrapper(func: Callable):
        func.display_name = name
        __all__.append(func.__name__)
        return func
    return wrapper


def query(conn: sqlite3.Connection, sql: str,
          params: Optional[tuple] = None,
          manual: bool = True,
          preview: int = 10) -> None:
    """
    Executes arbitrary SQL and returns result as DataResult or prints preview.
    """
    cur = conn.cursor()
    if manual and "limit" not in sql.lower()[-20:]:
        sql = sql.strip().rstrip(";") + f" LIMIT {preview};"
    cur.execute(sql, params or ())
    rows = cur.fetchall()
    columns = [d[0] for d in cur.description]

    if manual:
        print(f"\nPreview ({len(rows)} rows):")
        print(" | ".join(columns))
        for r in rows:
            print(" | ".join(str(x) for x in r))
        return None
    else:
        buffer.set(
        data=[tuple(r) for r in rows],
        name="SQL Query Result"
        )


@register("Top products by revenue")
def top_products(conn: sqlite3.Connection, limit: int = 5, manual=True) -> pd.DataFrame:
    sql = """
        SELECT p.category, s.product, SUM(s.price * s.quantity) AS revenue
        FROM sales s
        JOIN products p ON s.product = p.name
        GROUP BY p.category, s.product
        ORDER BY revenue DESC
        LIMIT ?;
    """
    return query(conn, sql, (limit,), manual=manual)


@register("Average daily sales by region")
def avg_check_by_region(conn: sqlite3.Connection, manual=True) -> pd.DataFrame:
    sql = """
        SELECT c.region,
               ROUND(SUM(s.price * s.quantity) / COUNT(DISTINCT s.date), 2) AS avg_daily_sales
        FROM sales s
        JOIN customers c ON s.customer_id = c.id
        GROUP BY c.region
        ORDER BY avg_daily_sales DESC;
    """
    return query(conn, sql, manual=manual)


@register("Rolling weekly revenue")
def rolling_weekly_sales(conn: sqlite3.Connection, manual=True) -> pd.DataFrame:
    sql = """
        SELECT date,
               SUM(price * quantity)
                   OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_week
        FROM sales
        ORDER BY date;
    """
    return query(conn, sql, manual=manual)
