from custom_types import TemplateDict
from pathlib import Path
from typing import Any
from getdata import read_data, normalize_column, normalize_header, detect_format

import json
import pandas as pd


def create_df_from_file(
    file_path: Path,
    template: TemplateDict,
    drop_duplicates: bool = False
) -> pd.DataFrame:
    """
    Creates a DataFrame from file strictly based on the template:
    - Iterates over template columns.
    - For each column, tries to find a matching file column (via normalize_header).
    - If found and normalization sample has at least one valid value → include column.
    - Otherwise column filled with NaN.
    """
    fmt, raw = read_data(file_path)  # (format, list[dict])
    df_dict = {}

    if not raw:
        return pd.DataFrame()

    # Preload first N rows as sample for validation
    sample_size = min(10, len(raw))
    sample_rows = raw[:sample_size]

    for col_key, col_spec in template.items():
        if not col_spec.get("save", False):
            continue

        target_name = col_spec["target_name"]
        matched_col = None

        # Try to find matching column in file headers
        for file_col in raw[0].keys():
            # Normalize both names (file column and template target)
            norm_file_col = normalize_header(file_col)
            norm_tpl_col = normalize_header(col_spec["target_name"])

            if norm_file_col == norm_tpl_col:
                # Take sample values
                values = [row.get(file_col, None) for row in sample_rows]
                series = pd.Series(values)

                # Try to normalize sample to check viability
                normalized_sample = normalize_column(
                    series,
                    target_name=col_spec["target_name"],
                    dtype=col_spec["type"],
                    format_spec=col_spec.get("format"),
                    header_case=col_spec.get("header_case"),
                )

                # If normalization gives at least one non-empty value — match confirmed
                if normalized_sample.notna().any():
                    matched_col = file_col
                    break

        if matched_col is None:
            # no match → create empty column
            df_dict[target_name] = [pd.NA] * len(raw)
        else:
            # normalize whole column
            series = pd.Series([row.get(matched_col, None) for row in raw])
            normalized = normalize_column(
                series,
                target_name=col_spec["target_name"],
                dtype=col_spec["type"],
                format_spec=col_spec.get("format"),
                header_case=col_spec.get("header_case"),
            )
            df_dict[target_name] = normalized

    df = pd.DataFrame(df_dict)

    if drop_duplicates:
        df = df.drop_duplicates(ignore_index=True)

    return df


def append_df_from_file(
    df: pd.DataFrame,
    file_path: Path,
    template: TemplateDict,
    drop_duplicates: bool = False
) -> pd.DataFrame:
    """
    Appends data from file to existing DataFrame according to template.
    Works strictly from template, not from existing DataFrame structure.

    - All columns defined in template will be present in the result.
    - For each column, tries to match file headers via normalize_header + sample normalization.
    - If match found → normalize and append values.
    - If no match → append NaN values for that column.
    - Empty rows (all NaN) are ignored.
    """
    new_df = create_df_from_file(file_path, template, drop_duplicates=False)
    new_df = new_df.dropna(how="all")  # drop completely empty rows

    # Ensure both DataFrames have same set/order of columns (all from template)
    template_cols = [spec["target_name"] for spec in template.values() if spec.get("save", False)]
    for col in template_cols:
        if col not in df.columns:
            df[col] = pd.NA
        if col not in new_df.columns:
            new_df[col] = pd.NA

    # Reorder both by template definition
    df = df[template_cols]
    new_df = new_df[template_cols]

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
