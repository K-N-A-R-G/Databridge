from pathlib import Path
from typing import Any
from getdata import read_data, normalize_column, detect_format

import json
import pandas as pd


def create_df_from_file(file_path: Path, template: dict, drop_duplicates: bool = False) -> pd.DataFrame:
    """
    Creates a DataFrame from file based on MetaEditor template.

    Args:
        file_path: Path to the input data file.
        template: Template dict from MetaEditor.
        drop_duplicates: If True, duplicate rows will be removed.

    Returns:
        pd.DataFrame
    """
    fmt, raw = read_data(file_path)  # returns (format, list[dict])
    df_dict = {col_spec["target_name"]: [] for col_spec in template.values() if col_spec.get("save", False)}

    for row in raw:
        for col_name, col_spec in template.items():
            if not col_spec.get("save", False):
                continue
            value = row.get(col_name, None)

            try:
                # normalize_column always expects a Series
                series = pd.Series([value])
                normalized = normalize_column(
                    series,
                    target_name=col_spec["target_name"],
                    dtype=col_spec["type"],
                    format_spec=col_spec.get("format"),
                    header_case=col_spec.get("header_case")
                )
                val = normalized.iloc[0] if not normalized.empty else None
            except Exception:
                val = None

            df_dict[col_spec["target_name"]].append(val)

    df = pd.DataFrame(df_dict)

    if drop_duplicates:
        df = df.drop_duplicates(ignore_index=True)

    return df



def append_df_from_file(df: pd.DataFrame, file_path: Path, template: dict, drop_duplicates: bool = False) -> pd.DataFrame:
    """
    Appends data from file to existing DataFrame according to template.
    Rows where all values are None are ignored.

    Args:
        df: Existing DataFrame.
        file_path: Path to the input data file.
        template: Template dict from MetaEditor.
        drop_duplicates: If True, duplicate rows will be removed after concatenation.

    Returns:
        pd.DataFrame
    """
    new_df = create_df_from_file(file_path, template, drop_duplicates=False)
    new_df = new_df.dropna(how="all")  # drop empty rows

    result = pd.concat([df, new_df], ignore_index=True)

    if drop_duplicates:
        result = result.drop_duplicates(ignore_index=True)

    return result


def load_template(template_path: Path) -> dict:
    """
    Loads template JSON as dict.
    """
    with template_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def load_template(template_path: Path) -> dict:
    """
    Loads template JSON as dict.
    """
    with template_path.open("r", encoding="utf-8") as f:
        return json.load(f)
