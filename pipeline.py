from pathlib import Path
from typing import List
import pandas as pd
import json
import re

from devmenu import DevMenu
from getdata import read_data, normalize_column, detect_format, normalize_header
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


def choose_template() -> Path:
    """Prompt user to select a template JSON file."""
    templates = list(TEMPLATES_DIR.glob("*.json"))
    if not templates:
        raise FileNotFoundError("No templates found in ./Data/templates/")

    print("\nAvailable templates:")
    for i, t in enumerate(templates, 1):
        print(f"{i}) {t.name}")

    try:
        num = int(input("\nChoose template number: "))
        tpl_path = templates[num - 1]
        return tpl_path
    except ValueError:
        print("Incorrect input")
    except IndexError:
        print("Incorrect number")


def build_df_interactive():
    """
    Wrapper to first select a template, then build DataFrame.
    """
    template_path = choose_template()  # Using the existing template selection function
    if template_path:
        build_dataframe_from_template(template_path)


def build_dataframe_from_template(
    template_path: Path,
    drop_duplicates: bool = True,
    save_result: bool = True
) -> pd.DataFrame:
    """
    Build a DataFrame from multiple files using a MetaEditor template.
    Columns are added if they match the template (normalized headers + successful data normalization).
    """
    template = load_template(template_path)
    files = choose_files()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize empty DataFrame with template columns
    df_dict = {col_spec["target_name"]: [] for col_spec in template.values() if col_spec.get("save", False)}
    df = pd.DataFrame(df_dict)

    for f in files:
        fmt, raw = read_data(f)
        for col_name, col_spec in template.items():
            if not col_spec.get("save", False):
                continue

            # Extract column values from raw, normalize header
            matched_values = []
            for row in raw:
                for k, v in row.items():
                    if normalize_header(k) == normalize_header(col_name):
                        try:
                            series = pd.Series([v])
                            normalized = normalize_column(
                                series,
                                target_name=col_spec["target_name"],
                                dtype=col_spec["type"],
                                format_spec=col_spec.get("format"),
                                header_case=col_spec.get("header_case")
                            )
                            val = normalized.iloc[0] if not normalized.empty else None
                            if val is not None:
                                matched_values.append(val)
                        except Exception:
                            continue
            # Add column to df if at least one value matched
            if matched_values:
                if col_spec["target_name"] not in df.columns:
                    df[col_spec["target_name"]] = pd.Series([None]*len(df))
                # Align lengths
                max_len = max(len(df), len(matched_values))
                if len(df) < max_len:
                    for c in df.columns:
                        df[c] = df[c].reindex(range(max_len))
                df.loc[len(df) - len(matched_values):, col_spec["target_name"]] = pd.to_datetime(
                matched_values, format=col_spec.get("format"), errors="coerce"
                )

    if drop_duplicates:
        df = df.drop_duplicates(ignore_index=True)

    if save_result:
        out_file = RESULTS_DIR / f"result_{template_path.stem}.csv"
        df.to_csv(out_file, index=False)
        print(f"\nSaved result to {out_file}")

    return df


def main():
    actions = {
        "1": ("Build DataFrame using template", build_df_interactive, (), {}),
        "2": ("List files in ./Data/", lambda: print("\n".join(f.name for f in get_all_data_files())), (), {}),
    }

    menu = DevMenu(actions, title="Databridge Manager")
    menu.run()


if __name__ == "__main__":
    main()
