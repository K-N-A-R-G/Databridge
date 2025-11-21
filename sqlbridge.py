"""
sqlbridge.py — minimal analytical SQL layer for Databridge
"""

from config import DB_PATH, get_active_table
from devmenu import DevMenu

import sqlfuncs
import sqlite3
import pandas as pd


def preview_active_table():
    """Preview the currently active table."""
    table = get_active_table()
    if not table:
        print("No active table selected.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 5;", conn)
        print(df)
    except Exception as e:
        print(f"[Preview ERROR] {e}")
    finally:
        conn.close()


def inspect_structure():
    """Inspect structure of active table."""
    table = get_active_table()
    if not table:
        print("No active table selected.")
        return

    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql_query(f"PRAGMA table_info({table});", conn)
        print(df[["name", "type"]])
    except Exception as e:
        print(f"[Inspect ERROR] {e}")
    finally:
        conn.close()


def run_action(conn: sqlite3.Connection, index: int):
    """Run selected SQL analytical function."""
    table = get_active_table()
    if not table:
        print("No active table selected.")
        print("Use main menu → Select active table.")
        return

    func_name = sqlfuncs.__all__[index - 1]
    func = getattr(sqlfuncs, func_name)

    print(f"\n\033[1;35m{func.display_name}\033[0m")
    print(f"Table: {table}")

    mode = input("<Enter> = Preview | F = Full: ").strip().lower()
    manual = not (mode == 'f')

    try:
        func(conn, manual=manual)
    except Exception as e:
        print(f"[SQL ERROR] {e}")


def make_actiondict(conn: sqlite3.Connection) -> dict[str, tuple]:
    """Build ActionDict for DevMenu."""
    actions = {}
    i = ''

    # SQL analytics functions
    for i, func_name in enumerate(sqlfuncs.__all__, start=1):
        func = getattr(sqlfuncs, func_name)
        actions[str(i)] = [
            func.display_name,
            run_action,
            (conn, i),
            {}
        ]
    else:
        actions[str(i)][0] += '\n'
    # Service actions
    actions["i"] = ("Inspect active table structure", inspect_structure, (), {})
    actions["p"] = ("Preview active table", preview_active_table, (), {})

    return actions


def run_sql_engine():
    """Entry point for SQL analytics."""
    if not DB_PATH.exists():
        print("Database not found. Run ETL first.")
        return

    conn = sqlite3.connect(DB_PATH)

    # Show preview before menu
    preview_active_table()

    menu = DevMenu(
        make_actiondict(conn),
        title="SQL Analytics",
        dev_mode=True
    )
    menu.run()

    conn.close()
