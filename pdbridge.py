"""
pandasbridge.py — Pandas analytics execution layer for Databridge
"""
from config import get_active_table, DB_PATH, RESULTS_DIR
from devmenu import DevMenu
from custom_types import buffer, DBConnection

import pandas as pd
import sqlite3
import analytics


# === Setup results directory ===
RESULTS_DIR = RESULTS_DIR / "analytics"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# === Helpers ===

def _preview(df: pd.DataFrame, name: str) -> None:
    """Print short preview of analytic result."""
    print(f"\nPreview of {name} ({len(df)} rows):")
    print(df.head(10).to_string(index=False))


def save_result(df: pd.DataFrame, name: str) -> None:
    """Save analytic result to CSV."""
    out = RESULTS_DIR / f"{name}.csv"
    df.to_csv(out, index=False)
    print(f"Saved: {out}")


def preview_active_table() -> None:
    """Show first rows of currently active table."""
    table = get_active_table()
    if not table:
        print("No active table selected.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        print(f"\nActive table: {table}")
        df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 10;", conn)
        print(df)
    except Exception as e:
        print(f"[Preview ERROR] {e}")
    # finally:
        # conn.close()


def load_active_table_df() -> pd.DataFrame | None:
    """Return full DataFrame of active table, or None if not selected."""
    table = get_active_table()
    if not table:
        print("No active table selected.")
        return None

    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(f"SELECT * FROM {table};", conn)
        return df
    except Exception as e:
        print(f"[Load ERROR] {e}")
        return None
    # finally:
        # conn.close()

# === Core analytics runner ===

def run_action(conn: sqlite3.Connection, index: int):
    """Run a single pandas analytics function by menu index."""
    func_name = analytics.__all__[index - 1]
    func = getattr(analytics, func_name)

    table = get_active_table()
    if not table:
        print("No active table selected. Use: Select active table.")
        return

    print(f"\n\033[1;35m{func.display_name}\033[0m")
    print(f"Table: {table}")

    # Load table into DataFrame
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table};", conn)
    except Exception as e:
        print(f"[Load ERROR] {e}")
        return

    # Run analytic function: df -> df_out
    try:
        result = func(df)
    except Exception as e:
        print(f"[Analytics ERROR] {e}")
        return

    # result is DataFrame or scalar
    if isinstance(result, pd.DataFrame):
        _preview(result, func.display_name)
        save_result(result, func.display_name)

        # write to shared buffer
        buffer.set(result, name=func.display_name)

    elif isinstance(result, (int, float)):
        print(f"Result: {result}")
        buffer.set(result, name=func.display_name)

    elif isinstance(result, dict):
        # demo() returns multiple values
        print("Demo results:")
        for key, val in result.items():
            if isinstance(val, pd.DataFrame):
                _preview(val, key)
                save_result(val, key)
            else:
                print(f"{key}: {val}")
        buffer.set(result, name=func.display_name)

    else:
        print("No data returned.")


# === DevMenu actions ===

def make_actiondict(conn):
    actions = {}

    # pandas analytic functions
    for i, func_name in enumerate(analytics.__all__, start=1):
        func = getattr(analytics, func_name)
        actions[str(i)] = (
            func.display_name,
            run_action,
            (conn, i),
            {}
        )

    # utility: preview active table
    actions["p"] = ("Preview active table", preview_active_table, (), {})

    return actions


# === Entry point ===

def run_pd_engine():
    """Entry point for Pipeline menu — opens Pandas Analytics DevMenu."""
    if not DB_PATH.exists():
        print("Database not found. Run ETL first.")
        return

    # Show preview before entering menu (nice UX)
    preview_active_table()

    conn = DBConnection.get()

    menu = DevMenu(make_actiondict(conn), title="Pandas Analytics", dev_mode=True)
    menu.run()

    # conn.close()
