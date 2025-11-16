"""
sqlbridge.py — minimal analytical SQL layer for Databridge
"""
from config import get_active_table, DB_PATH
from devmenu import DevMenu, select_from_list
from pathlib import Path

import inspect
import numpy as np
import sqlfuncs
import sqlite3
import pandas as pd


DB_DIR = Path("Data/results/databases")


# ---------- Core ----------

def init_db(tables: dict[str, pd.DataFrame],
            db_path: Path = DB_PATH) -> sqlite3.Connection:
    """
    Creates SQLite DB from provided DataFrames.
    Replaces existing tables if any.
    """
    conn = sqlite3.connect(db_path)
    for name, df in tables.items():
        df.to_sql(name, conn, if_exists="replace", index=False)
    return conn


def inspect_db(db_path: Path) -> dict[str, list[str]]:
    """
    Returns dictionary {table_name: [columns]} without loading data.
    """
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    tables = {}
    for (table_name,) in cur.execute("SELECT name FROM sqlite_master WHERE type='table';"):
        cur.execute(f"PRAGMA table_info({table_name});")
        columns = [row[1] for row in cur.fetchall()]
        tables[table_name] = columns

    conn.close()
    print(tables)


def preview_table(db_path: Path, table: str, limit: int = 5) -> pd.DataFrame:
    """Returns small preview of table content."""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT {limit};", conn)
    conn.close()
    print(df)


def list_actions() -> list[tuple[int, str]]:
    """
    Returns numbered list of available analytical actions.
    """
    actions = []
    for i, func_name in enumerate(sqlfuncs.__all__, start=1):
        func = getattr(sqlfuncs, func_name)
        actions.append((i, func.display_name))
    return actions


def run_action(conn: sqlite3.Connection, index: int):
    """
    Runs selected analytical function by its numeric index.
    """
    table = get_active_table()
    func_name = sqlfuncs.__all__[index - 1]
    func = getattr(sqlfuncs, func_name)
    print(f'\n\033[1;35m{func.display_name}\033[0m\n')
    print('\n<Enter> - Preview  |  F - Full processing')
    mode = input('Select mode: ').strip().lower()
    manual = False if mode == 'f' else True
    return func(conn, manual=manual)



def make_actiondict(conn) -> dict[str, tuple]:
    """
    Builds ActionDict for DevMenu to interact with SQLBridge.
    Keys are string numbers, values = (description, func, args, kwargs)
    """
    actions = {}

    # --- Basic analytical functions ---
    for i, label in list_actions():
        actions[str(i)] = (
            label,          # description
            run_action,     # called function
            (conn, i),      # positional arguments
            {},             # kwargs
        )

    # --- Additional service actions ---
    offset = len(actions)
    actions[str(offset + 1)] = ("Inspect database structure", inspect_db, (DB_PATH,), {})
    actions[str(offset + 2)] = ("Preview table content", preview_table, (DB_PATH, "sales", 5), {})

    return actions


def run_sql_engine():
    """Entry point for Pipeline menu — opens SQL Analytics DevMenu."""
    if not DB_PATH.exists():
        print("\033[31mDatabase not found. Run pipeline first.\033[0m")
        return

    conn = sqlite3.connect(DB_PATH)
    sql_actions = make_actiondict(conn)
    menu = DevMenu(sql_actions, title="SQL Analytics", dev_mode=True)
    menu.run()
    conn.close()


# ---------- Demo ----------

def demo(tables: dict[str, pd.DataFrame]) -> None:
    """
    Simple self-test: creates DB, runs example query.
    """
    conn = init_db(tables)


# ---------- CLI / Direct Run ----------

if __name__ == "__main__":
    # Example usage for manual testing

    sales = pd.DataFrame({
        "date": pd.date_range("2024-01-01", periods=10, freq="D"),
        "product": [f"P{i%3}" for i in range(10)],
        "price": np.random.randint(10, 50, 10),
        "quantity": np.random.randint(1, 5, 10),
        "customer_id": np.random.randint(1, 4, 10)
    })

    customers = pd.DataFrame({
        "id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "region": ["North", "South", "West"],
        "segment": ["Retail", "Wholesale", "Retail"],
        "age": [29, 41, 35]
    })

    products = pd.DataFrame({
        "name": ["P0", "P1", "P2"],
        "category": ["A", "B", "A"],
        "cost": [5, 8, 7],
        "discount": [0.1, 0.2, 0.0]
    })


    demo({"sales": sales, "customers": customers, "products": products})

    tables = {
        "sales": sales,
        "customers": customers,
        "products": products
    }
    conn = init_db(tables)
    sql_actions = make_sql_actiondict(conn)
    menu = DevMenu(sql_actions, title="SQL Actions")

    menu.run()
