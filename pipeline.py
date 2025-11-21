import atexit
import pandas as pd
import sqlite3

from pathlib import Path
from typing import List, Optional

from config import BASE_DIR, RESULTS_DIR, TEMPLATES_DIR, DB_PATH, set_active_table
from custom_types import ActionDict, DBConnection
from dbtools import run_dbtools
from devmenu import DevMenu, select_from_list
from devtools import menu_actions as devtools_actions
from etl import append_df_from_file, load_template, create_df_from_file
from pdbridge import run_pd_engine  #, load_active_table_df
from sqlbridge import run_sql_engine
from template_manager import select_or_create_template
# from vis.api import show_table_window, show_plot


conn = DBConnection()

GREEN = "\033[32m"
RESET = "\033[0m"


def get_all_data_files(suffixes=None) -> List[Path]:
    """Return all files in ./Data optionally filtered by suffixes."""
    files = [f for f in BASE_DIR.iterdir() if f.is_file()]
    if suffixes:
        files = [f for f in files if f.suffix.lower() in suffixes]
    return files


def choose_files(single=False) -> List[Path]:
    """Prompt user to select files from ./Data, with options for all/csv/json or numbered selection."""
    all_files = get_all_data_files(suffixes=[".csv", ".json"])
    if not all_files:
        raise FileNotFoundError("No data files found in ./Data/")

    print("\nAvailable files:")
    for i, f in enumerate(all_files, 1):
        print(f"{i}) {f.name}")

    if single:
        try:
            num = int(input('Type one number of selected file '))
            choice = all_files[num - 1] if 0 <= num <= len(all_files) else None
            return choice.name
        except ValueError:
            return None

    print("\na) All files")
    print("c) All CSV")
    print("j) All JSON")
    choice = input("\nSelect files (numbers separated by space, or 'a', 'c', 'j'): ").strip().lower()

    if choice == "a":
        files = all_files
    elif choice == "c":
        files = [f for f in all_files if f.suffix.lower() == ".csv"]
    elif choice == "j":
        files = [f for f in all_files if f.suffix.lower() == ".json"]
    else:
        indices = [int(x)-1 for x in choice.split() if x.isdigit()]
        files = [all_files[i] for i in indices if 0 <= i < len(all_files)]

    if not files:
        print("No files selected")

    return files


def choose_template() -> Optional[Path]:
    templates = list(TEMPLATES_DIR.glob("*.json"))
    if not templates:
        raise FileNotFoundError("No templates found in ./Data/templates/")

    item = select_from_list([t.name for t in templates], "Available templates")
    if not item:
        return None
    res = Path(
     f'Data/templates/{item}')
    return res


def build_df_interactive():
    """
    Wrapper to first select a template, then build DataFrame.
    """
    template_path = choose_template()  # Using the existing template selection function
    if template_path is None:
        print("No template selected.")
        return None
    if template_path:
        build_dataframe_from_template(template_path)


def build_dataframe_from_template(
    template_path: Optional[Path],
    drop_duplicates: bool = True,
    save_result: bool = True
) -> Optional[pd.DataFrame]:
    """
    Build a DataFrame from multiple files using a MetaEditor template.
    Columns are added if they match the template (normalized headers + successful data normalization).
    """
    path = Path(template_path)
    if not path.exists():
        print(f"Error: template not found → {path}")
        return None
    template = load_template(template_path)
    files = choose_files()
    if not files:
        return

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Start with empty DataFrame; will be filled by first file
    df = pd.DataFrame()

    for f in files:
        if df.empty:
            df = create_df_from_file(f, template, drop_duplicates=False)
        else:
            df = append_df_from_file(df, f, template, drop_duplicates=False)

    if drop_duplicates:
        df = df.drop_duplicates(ignore_index=True)

    if save_result:
        save_dataframe(df, template_path)

    conn = DBConnection.get()
    tables = {template_path.stem: df}
    write_tables_to_db(tables, conn)
    print(f"{GREEN}SQLite cache updated:{RESET} {template_path.stem} → bridge.db")

    return df


def save_dataframe(df: pd.DataFrame, template_path: Path):
    """
    Interactive DataFrame saving using DevMenu.
    """
    out_base = RESULTS_DIR / f"result_{template_path.stem}"

    actions = {
        "c": (
            "Save as CSV",
            df.to_csv,
            (out_base.with_suffix(".csv"),),
            {"index": False}
        ),
        "x": (
            "Save as XLSX",
            df.to_excel,
            (out_base.with_suffix(".xlsx"),),
            {"index": False}
        ),
        "j": (
            "Save as JSON",
            df.to_json,
            (out_base.with_suffix(".json"),),
            {"orient": "records", "indent": 2}
        ),
    }

    menu = DevMenu(actions, title="Choose output format")
    menu.run()

    print(f"\nSaved result to {out_base}")


def write_tables_to_db(tables: dict[str, pd.DataFrame], conn) -> None:
    """
    Write multiple DataFrames into SQLite cache.

    Each key of 'tables' becomes table name; if table exists, it's replaced.
    """
    for name, df in tables.items():
        df.to_sql(name, conn, if_exists="replace", index=False)


def choose_active_table():
    """Interactive selector: fetch tables from SQLite and save selection."""
    if not DB_PATH.exists():
        print("\033[31mDatabase not found. Run pipeline first.\033[0m")
        return

    conn = sqlite3.connect(DB_PATH)
    tables = pd.read_sql_query(
        "SELECT name FROM sqlite_master WHERE type='table';", conn
    )["name"].tolist()
    conn.close()

    if not tables:
        print("\033[31mNo tables found in database.\033[0m")
        return

    choice = select_from_list(tables, title="Select active table")
    if choice:
        set_active_table(choice)
        print(f"\033[32mActive table set to: {choice}\033[0m")
    else:
        print("\033[33mSelection cancelled.\033[0m")


def manage_templates():
    select_or_create_template(choose_files(single=True))


# def visualize_active_table():
    # df = load_active_table_df()
    # if df is None:
        # return
    # show_plot(df, title=f"Plot of {active_table}")


# def preview_active_sql():
    # result = execute_sql("SELECT * FROM ... LIMIT 2000")
    # show_table_window(result)


def main():
    actions: ActionDict = {
        "1": ("Build DataFrame using template", build_df_interactive, (), {}),
        "2": ("Select/edit metadata template", manage_templates, (), {}),
        "3": ("List files in ./Data/", lambda: print("\n".join(f.name for f in get_all_data_files())), (), {}),
        "4": ("SQL analytics", run_sql_engine, (), {}),
        "5": ("Pandas analytics", run_pd_engine, (), {}),
        "6": ("Developer tools", DevMenu(devtools_actions).run, (), {}),
        "7": ("Select active table", choose_active_table, (), {}),
        "8": ("Database maintenance\n", run_dbtools, (), {}),
        # "va": ('View active table', visualize_active_table, (), {}),
        # "an": ("Another vis", preview_active_sql, (), {}),
    }

    menu = DevMenu(actions, title="Pipeline Manager", dev_mode=True)
    menu.run()


if __name__ == "__main__":
    main()
    atexit.register(conn.close)
