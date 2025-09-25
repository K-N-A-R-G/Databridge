# Template Manager Module (`template_manager.py`)

This module provides tools for managing **metadata templates** for tabular data files (CSV/JSON). Templates define column types, formats, header case, and which columns should be saved. Templates are primarily used by **MetaEditor** and ETL functions.

---

## Classes

### `MetaEditor(file_path: Path)`

Interactive editor for a single data file.

**Responsibilities:**
- Load a sample of the data (CSV/JSON) for inspection.
- Initialize or load existing template from `Data/templates/{file}_meta.json`.
- Display column headers and current metadata.
- Allow interactive editing of:
  - Header case (`lower`, `capitalize`, `title`, `upper`)
  - Column type (`str`, `int`, `float`, `date`)
  - Optional format string
  - Save flag
- Preview normalized values for each column.
- Save template to JSON.

**Example:**

```python
from template_manager import MetaEditor
from pathlib import Path

editor = MetaEditor(Path("Data/sales.csv"))
editor.edit_header()
editor.save_meta(Path("Data/templates/sales_meta.json"))
```

---

## Functions

### `run_metaeditor(filename: str)`

- Launches interactive editor for a file in `Data/`.
- Prompts user to save template after editing.
- Saves to `Data/templates/{filename}_meta.json`.

### `select_or_create_template(filename: str) -> Path | None`

Manages template selection or creation for a file:

- Checks if template exists (`Data/templates/{file}_meta.json`).
  - If yes, shows current template and allows:
    - Confirm
    - Edit via `MetaEditor`
    - Exit
  - If no template exists, offers:
    - Create new template
    - Use existing template as base
    - Exit
- Returns the path to the selected or newly created template, or `None` if cancelled.

**Notes:**
- User decides which columns to save.
- All templates stored in `Data/templates/`.
- Base templates can be copied/edited to create new ones.

---

## Reasons for Using Templates

- Ensure **consistent column types and formats** across files.
- Standardize **header case** and naming.
- Select **only relevant columns** for ETL.
- Facilitate **data normalization and aggregation** downstream.
- Provides **repeatable workflow** for multiple files with similar structure.

---

## Example Usage

```python
from template_manager import select_or_create_template

template_path = select_or_create_template("sales.csv")
if template_path:
    print(f"Template ready for ETL: {template_path}")
else:
    print("No template selected. Processing cancelled.")
```

---

## Notes

- Designed to work with `etl.py` for normalized DataFrame creation.
- Works with CSV and JSON sources.
- Templates are **reusable** and **editable**.
- Interactive prompts ensure user awareness of colum