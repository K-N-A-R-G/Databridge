from custom_types import buffer, DBConnection
from typing import Callable, Optional

import pandas as pd


__all__ = {}   # ← functions will be added automatically


def register(name: str, light=True, render='table'):
    """Decorator: assigns user-friendly name and auto-registers the function."""
    def wrapper(func: Callable):
        func.display_name = name
        func.light = light
        func.render = render
        __all__[func.__name__] = func
        return func
    return wrapper


def query(conn, sql: str,
          params: Optional[tuple] = None,
          manual: bool = True,
          preview: int = 10,
          name: str = "SQL Query Result") -> None:
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
        name=name
        )


@register("Top products by revenue", light=True, render='table')
def top_products(conn, limit: int = 5, manual: bool=True) -> pd.DataFrame:
    sql = """
        SELECT p.category, s.product, SUM(s.price * s.quantity) AS revenue
        FROM sales s
        JOIN products p ON s.product = p.name
        GROUP BY p.category, s.product
        ORDER BY revenue DESC
        LIMIT ?;
    """
    query(conn, sql, (limit,), manual=manual, name=top_products.display_name)


@register("Average daily sales by region", light=False, render='bar')
def avg_check_by_region(conn, manual=True) -> pd.DataFrame:
    sql = """
        SELECT c.region,
               ROUND(SUM(s.price * s.quantity) / COUNT(DISTINCT s.date), 2) AS avg_daily_sales
        FROM sales s
        JOIN customers c ON s.customer_id = c.id
        GROUP BY c.region
        ORDER BY avg_daily_sales DESC;
    """
    query(conn, sql, manual=manual, name=avg_check_by_region.display_name)


@register("Rolling weekly revenue", light=False, render='graph')
def rolling_weekly_sales(conn, manual=True) -> pd.DataFrame:
    sql = """
        SELECT date,
               SUM(price * quantity)
                   OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_week
        FROM sales
        ORDER BY date;
    """
    query(conn, sql, manual=manual, name=rolling_weekly_sales.display_name)
