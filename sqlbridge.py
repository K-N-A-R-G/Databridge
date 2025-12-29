"""
sqlbridge.py — minimal analytical SQL layer for Databridge
"""

from config import DB_PATH, get_active_table
from custom_types import DBConnection
from devmenu import DevMenu
from shared_library import execute_sql_in_process
from vis.vis_core import vis_act

import multiprocessing as mp
import pandas as pd
import sqlfuncs
import sqlite3
import sys
import threading


if __name__ == '__main__':
    mp.set_start_method('spawn')


def preview_active_table(conn):
    """Preview the currently active table."""
    table = get_active_table()
    if not table:
        print("No active table selected.")
        return

    try:
        df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 5;", conn)
        print(df)
    except Exception as e:
        print(f"[Preview ERROR] {e}")



def inspect_structure(conn):
    """Inspect structure of active table."""
    table = get_active_table()
    if not table:
        print("No active table selected.")
        return

    try:
        df = pd.read_sql_query(f"PRAGMA table_info({table});", conn)
        print(df[["name", "type"]])
    except Exception as e:
        print(f"[Inspect ERROR] {e}")


def run_action(conn, index: int):
    """Run selected SQL analytical function with Threading/Multiprocessing logic."""
    table = get_active_table()
    if not table:
        print("No active table selected.\nUse main menu → Select active table.")
        return

    # Извлекаем функцию и метаданные
    keys = list(sqlfuncs.__all__.keys())
    func_name = keys[index - 1]
    func = sqlfuncs.__all__[func_name]

    # Метаданные из декоратора @register
    light = getattr(func, 'light', True)
    render_mode = getattr(func, 'render', 'table')
    display_name = getattr(func, 'display_name', func_name)

    print(f"\n\033[1;35m{display_name}\033[0m")
    print(f"Table: {table}")

    # Выбор режима
    mode = input("<Enter> = Preview | F = Full: ").strip().lower()
    full_mode = (mode == 'f')

    if not full_mode:
        # --- РЕЖИМ PREVIEW (Всегда в основном потоке, только консоль) ---
        func(conn, manual=True)

    elif full_mode:
        # --- РЕЖИМ FULL (Графика) ---
        if light:
            # Легкие задачи (Таблицы): запускаем в ПОТОКЕ
            # Чтобы не блокировать консоль, но иметь доступ к памяти
            print(f"[SYSTEM] Launching table view in Thread...")

            func(conn, manual=False)
            print(render_mode)

            thread = threading.Thread(
                                      target=vis_act.do,
                                      args=(render_mode,),
                                      kwargs={},
                                      daemon=True
                                      )
            thread.start()

        else:
            # Тяжелые задачи (Графики): запускаем в ПРОЦЕССЕ
            # Полная изоляция для Matplotlib и своего Tk-root
            print(f"[SYSTEM] Spawning heavy process for {render_mode}...")

            p = mp.Process(
                target=execute_sql_in_process,
                args=('sqlfuncs', func_name, DB_PATH, table, render_mode),
                daemon=True
            )
            p.start()


def make_actiondict(conn: DBConnection) -> dict[str, tuple]:
    """Build ActionDict for DevMenu."""
    actions = {}
    print(f'{conn = }')

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
    actions["i"] = ("Inspect active table structure", inspect_structure, (conn,), {})
    actions["p"] = ("Preview active table", preview_active_table, (conn,), {})

    return actions


def run_sql_engine(conn):
    """Entry point for SQL analytics."""
    if not DB_PATH.exists():
        print("Database not found. Run ETL first.")
        return

    # Show preview before menu
    preview_active_table(conn)

    menu = DevMenu(
        make_actiondict(conn),
        title="SQL Analytics",
        dev_mode=True
    )
    menu.run()
