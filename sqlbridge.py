"""
sqlbridge.py — minimal analytical SQL layer for Databridge
"""

from config import DB_PATH, get_active_table
from custom_types import DBConnection
from devmenu import DevMenu
from vis.vis_core import show_table, execute_sql_in_process

import multiprocessing as mp
import pandas as pd
import sqlfuncs
import threading


def preview_active_table():
    """Preview the currently active table."""
    conn = DBConnection().get()
    table = get_active_table()
    if not table:
        print("No active table selected.")
        return

    try:
        df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 5;", conn)
        print(df)
    except Exception as e:
        print(f"[Preview ERROR] {e}")



def inspect_structure():
    """Inspect structure of active table."""
    conn = DBConnection().get()
    table = get_active_table()
    if not table:
        print("No active table selected.")
        return

    try:
        df = pd.read_sql_query(f"PRAGMA table_info({table});", conn)
        print(df[["name", "type"]])
    except Exception as e:
        print(f"[Inspect ERROR] {e}")


def run_action(index: int):
    """Run selected SQL analytical function with Threading/Multiprocessing logic."""
    conn = DBConnection().get()
    table = get_active_table()
    if not table:
        print("No active table selected.\nUse main menu → Select active table.")
        return

    # Extract function and metadata
    keys = list(sqlfuncs.__all__.keys())
    func_name = keys[index - 1]
    func = sqlfuncs.__all__[func_name]

    # Metadata from the decorator @register
    light = getattr(func, 'light', True)
    render_mode = getattr(func, 'render', 'table')
    display_name = getattr(func, 'display_name', func_name)

    print(f"\n\033[1;35m{display_name}\033[0m")
    print(f"Table: {table}")

    mode = input("<Enter> = Preview | F = Full: ").strip().lower()
    full_mode = (mode == 'f')

    if not full_mode:
        # PREVIEW MODE (Always on the main thread, console only)
        func(manual=True)

    elif full_mode:
        # --- FULL MODE (Graphics) ---
        if light:
            print("[SYSTEM] Launching table view in Thread...")
            func(manual=False)
            print(render_mode)

            thread = threading.Thread(
                                      target=show_table,
                                      args=(),
                                      kwargs={},
                                      daemon=True
                                      )
            thread.start()

        else:
            print(f"[SYSTEM] Spawning heavy process for {render_mode}...")

            p = mp.Process(
                target=execute_sql_in_process,
                args=('sqlfuncs', func_name, DB_PATH, table, render_mode),
                daemon=True
            )
            p.start()


def make_actiondict() -> dict[str, tuple]:
    """Build ActionDict for DevMenu."""
    conn = DBConnection().get()
    actions = {}
    print(f'{conn = }')

    # SQL analytics functions
    for i, func_name in enumerate(sqlfuncs.__all__, start=1):
        func = getattr(sqlfuncs, func_name)
        actions[str(i)] = [
            func.display_name,
            run_action,
            (i,),
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

    # Show preview before menu
    preview_active_table()

    menu = DevMenu(
        make_actiondict(),
        title="SQL Analytics",
        dev_mode=True
    )
    menu.run()
