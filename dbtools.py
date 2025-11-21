"""
dbtools.py — administrative SQLite tools for Databridge
Manage tables: list, preview, delete, wipe all.
"""

import sqlite3
import pandas as pd

from config import DB_PATH, get_active_table, set_active_table
from custom_types import DBConnection
from devmenu import DevMenu, select_from_list


# === Low-level utilities ===

def list_tables(conn: sqlite3.Connection) -> list[str]:
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table';"
    ).fetchall()
    return [r[0] for r in rows]


def preview_table(conn: sqlite3.Connection, table: str, limit: int = 10):
    print(f"\n\033[36m=== Preview: {table} ===\033[0m")

    try:
        df = pd.read_sql_query(
            f"SELECT * FROM {table} LIMIT {limit};", conn
        )
        print(df if not df.empty else "(empty table)")
    except Exception as e:
        print(f"\033[31m[ERROR] {e}\033[0m")


def delete_table(conn: sqlite3.Connection, table: str):
    cur = conn.cursor()
    cur.execute(f"DROP TABLE IF EXISTS {table};")
    conn.commit()
    print(f"\033[33mTable deleted: {table}\033[0m")

    # If active table was removed — clear it
    if get_active_table() == table:
        set_active_table("")
        print("\033[35mActive table cleared.\033[0m")


def delete_all_tables(conn: sqlite3.Connection):
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    names = [r[0] for r in cur.fetchall()]

    if not names:
        print("\033[33mNo tables to delete.\033[0m")
        return

    print("\033[33mDeleting ALL tables...\033[0m")
    for name in names:
        cur.execute(f"DROP TABLE IF EXISTS {name};")
    conn.commit()

    set_active_table("")
    print("\033[35mAll tables removed. Active table cleared.\033[0m")


# === Menu actions ===

def action_list_tables(conn):
    tables = list_tables(conn)
    if not tables:
        print("\033[33mNo tables in database.\033[0m")
        return
    print("\n\033[36m=== Tables ===\033[0m")
    for t in tables:
        print(" -", t)


def action_preview_table(conn):
    tables = list_tables(conn)
    if not tables:
        print("\033[33mNo tables available.\033[0m")
        return

    choice = select_from_list(
        tables, title="Choose table to preview"
    )
    if not choice:
        print("\033[33mCancelled.\033[0m")
        return

    preview_table(conn, choice)


def action_delete_table(conn):
    tables = list_tables(conn)
    if not tables:
        print("\033[33mNo tables to delete.\033[0m")
        return

    choice = select_from_list(
        tables, title="Select table to delete"
    )
    if not choice:
        print("\033[33mCancelled.\033[0m")
        return

    confirm = input(f"Delete '{choice}'? (y/N): ").strip().lower()
    if confirm == "y":
        delete_table(conn, choice)
    else:
        print("\033[33mCancelled.\033[0m")


def action_delete_all(conn):
    confirm = input("Delete ALL tables? (y/N): ").strip().lower()
    if confirm == "y":
        delete_all_tables(conn)
    else:
        print("\033[33mCancelled.\033[0m")


def action_vacuum(conn):
    print("\033[36mRunning VACUUM (compressing database)...\033[0m")
    try:
        conn.execute("VACUUM;")
        print("\033[32mDatabase compressed successfully.\033[0m")
    except Exception as e:
        print(f"\033[31mError: {e}\033[0m")


# === ActionDict builder ===

def make_actiondict(conn):
    return {
        "1": ("List tables",         action_list_tables,   (conn,), {}),
        "2": ("Preview table",       action_preview_table, (conn,), {}),
        "3": ("Delete table",        action_delete_table,  (conn,), {}),
        "4": ("Delete ALL tables",   action_delete_all,    (conn,), {}),
        "5": ("VACUUM (compress database)", action_vacuum, (conn,), {}),
    }


def run_dbtools():
    """Entry point for Pipeline: database maintenance tools."""
    if not DB_PATH.exists():
        print("\033[31mDatabase not found. Run ETL first.\033[0m")
        return

    conn = DBConnection.get()
    menu = DevMenu(make_actiondict(conn),
                   title="Database Maintenance",
                   dev_mode=True)
    menu.run()
    conn.close()
