from typing import Callable, Tuple, Optional
import sqlite3, pandas as pd


__all__ = []   # ← functions will be added automatically


def register(name: str):
    """Decorator: assigns user-friendly name and auto-registers the function."""
    def wrapper(func: Callable):
        func.display_name = name
        __all__.append(func.__name__)
        return func
    return wrapper


def query(conn: sqlite3.Connection, sql: str,
          params: Optional[Tuple]=None, manual: bool=True) -> pd.DataFrame:
    """
    Executes arbitrary SQL and returns result as DataFrame.
    """
    if manual:
        print(pd.read_sql_query(sql, conn, params=params))
    else:
        return pd.read_sql_query(sql, conn, params=params)


@register("Top products by revenue")
def top_products(conn: sqlite3.Connection, limit: int = 5) -> pd.DataFrame:
    sql = """
        SELECT p.category, s.product, SUM(s.price * s.quantity) AS revenue
        FROM sales s
        JOIN products p ON s.product = p.name
        GROUP BY p.category, s.product
        ORDER BY revenue DESC
        LIMIT ?;
    """
    return query(conn, sql, (limit,))


@register("Average daily sales by region")
def avg_check_by_region(conn: sqlite3.Connection) -> pd.DataFrame:
    sql = """
        SELECT c.region,
               ROUND(SUM(s.price * s.quantity) / COUNT(DISTINCT s.date), 2) AS avg_daily_sales
        FROM sales s
        JOIN customers c ON s.customer_id = c.id
        GROUP BY c.region
        ORDER BY avg_daily_sales DESC;
    """
    return query(conn, sql)


@register("Rolling weekly revenue")
def rolling_weekly_sales(conn: sqlite3.Connection) -> pd.DataFrame:
    sql = """
        SELECT date,
               SUM(price * quantity)
                   OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS rolling_week
        FROM sales
        ORDER BY date;
    """
    return query(conn, sql)
