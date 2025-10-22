from pathlib import Path
from typing import List, Optional
import pandas as pd

from custom_types import ActionDict
from devmenu import DevMenu
from etl import append_df_from_file, load_template, create_df_from_file

DATA_DIR = Path("./Data")
RESULTS_DIR = DATA_DIR / "results"
TEMPLATES_DIR = DATA_DIR / "templates"


def get_all_data_files(suffixes=None) -> List[Path]:
    """Return all files in ./Data optionally filtered by suffixes."""
    files = [f for f in DATA_DIR.iterdir() if f.is_file()]
    if suffixes:
        files = [f for f in files if f.suffix.lower() in suffixes]
    return files


def choose_files() -> List[Path]:
    """Prompt user to select files from ./Data, with options for all/csv/json or numbered selection."""
    all_files = get_all_data_files(suffixes=[".csv", ".json"])
    if not all_files:
        raise FileNotFoundError("No data files found in ./Data/")

    print("\nAvailable files:")
    for i, f in enumerate(all_files, 1):
        print(f"{i}) {f.name}")

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
        raise ValueError("No files selected")

    return files


def choose_from_list(items: list[str], title: str = "Select item") -> int | None:
    """Generic selector for DevMenu-like lists."""
    print(f"\n{title}:")
    for i, item in enumerate(items, start=1):
        print(f"{i:>2}) {item}")

    while True:
        choice = input("\nEnter number or 'q' to back: ").strip().lower()
        if choice == "q":
            return None
        try:
            num = int(choice)
            if 1 <= num <= len(items):
                return num - 1
            print("Incorrect number")
        except ValueError:
            print("Incorrect input")


def choose_template() -> Optional[Path]:
    templates = list(TEMPLATES_DIR.glob("*.json"))
    if not templates:
        raise FileNotFoundError("No templates found in ./Data/templates/")

    idx = choose_from_list([t.name for t in templates], "Available templates")
    return templates[idx] if idx is not None else None


def build_df_interactive():
    """
    Wrapper to first select a template, then build DataFrame.
    """
    template_path = choose_template()  # Using the existing template selection function
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
    if template_path is None:
        print("No template selected.")
        return None

    template = load_template(template_path)
    files = choose_files()

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

    print(f"\nSaved result to {out_base}.[csv|xlsx|json]")


def main():
    actions: ActionDict = {
        "1": ("Build DataFrame using template", build_df_interactive, (), {}),
        "2": ("List files in ./Data/", lambda: print("\n".join(f.name for f in get_all_data_files())), (), {}),
    }

    menu = DevMenu(actions, title="Databridge Manager")
    menu.run()


if __name__ == "__main__":
    main()
