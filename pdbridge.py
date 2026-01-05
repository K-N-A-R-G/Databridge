"""
pandasbridge.py — Pandas analytics execution layer for Databridge
"""
from config import get_active_table, DB_PATH, RESULTS_DIR
from custom_types import DBConnection
from devmenu import DevMenu
from vis.vis_core import execute_pd_in_process, show_table

import multiprocessing as mp
import pdfuncs
import pandas as pd
import threading

from typing import NoReturn




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
    conn = DBConnection().get()
    table = get_active_table()
    if not table:
        print("No active table selected.")
        return

    try:
        print(f"\nActive table: {table}")
        df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 10;", conn)
        print(df)
    except Exception as e:
        print(f"[Preview ERROR] {e}")


def load_active_table_df() -> pd.DataFrame | NoReturn |None:
    """Return full DataFrame of active table, or None if not selected."""
    conn = DBConnection().get()
    table = get_active_table()
    if not table:
        raise FileNotFoundError("No active table selected.")


    try:
        df = pd.read_sql_query(f"SELECT * FROM {table};", conn)
        return df
    except Exception as e:
        print(f"[Load ERROR] {e}")
        return None


# === Core analytics runner ===

def run_action(index: int):
    conn = DBConnection().get()
    table = get_active_table()
    if not table:
        print("No active table selected.")
        return

    # Extract metadata
    keys = list(pdfuncs.__all__.keys())
    func_name = keys[index - 1]
    func = pdfuncs.__all__[func_name]

    light = getattr(func, 'light', True)
    render_mode = getattr(func, 'render', 'table')

    print(f"\n\033[1;36m[PANDAS] {getattr(func, 'display_name', func_name)}\033[0m")
    choice = input("<Enter> = Preview | F = Full: ").strip().lower()
    full_mode = (choice == 'f')

    if not full_mode:
        # --- PREVIEW (Fast loading 5 lines right here) ---
        df_mini = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 5;", conn)
        func(df_mini, manual=True)

    else:
        # --- FULL (Background execution) ---
        if light:
            # tables: in separate thread
            print("[SYSTEM] Loading full table for Pandas...")
            df_full = pd.read_sql_query(f"SELECT * FROM {table};", conn)
            func(df_full, manual=False)

            threading.Thread(target=show_table, daemon=True).start()

        else:
            # graphs: in separate process
            print("[SYSTEM] Spawning isolated Pandas process...")
            p = mp.Process(
                target=execute_pd_in_process,
                args=('pdfuncs', func_name, DB_PATH, table, render_mode),
                daemon=True
            )
            p.start()


# === DevMenu actions ===

def make_actiondict():
    conn = DBConnection().get()
    actions = {}

    # pandas analytic functions
    for i, func_name in enumerate(pdfuncs.__all__.keys(), start=1):
        func = pdfuncs.__all__[func_name]
        actions[str(i)] = (
            func.display_name,
            run_action,
            (i,),
            {}
        )

    # utility: preview active table
    actions["p"] = ("Preview active table", preview_active_table, (), {})

    return actions


# === Entry point ===

def run_pd_engine() -> NoReturn | None:
    """Entry point for Pipeline menu — opens Pandas Analytics DevMenu."""
    conn = DBConnection().get()
    if not DB_PATH.exists():
        raise FileNotFoundError("Database not found. Run ETL first.")


    # Show preview before entering menu (nice UX)
    preview_active_table()

    menu = DevMenu(make_actiondict(), title="Pandas Analytics", dev_mode=True)
    menu.run()
