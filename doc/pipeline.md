# Pipeline Module (`pipeline.py`)

The `pipeline.py` module provides the interactive workflow manager for building normalized DataFrames from raw data files located in `./Data/`.
It integrates file selection, template management, and ETL routines into a single command menu powered by **DevMenu**.

---

## Features

- Lists available templates from `./Data/templates/`
- Lists available files in `./Data/`
- Flexible file selection:
  - Pick individual files by number
  - Select all files
  - Select only `.csv` or `.json` files
- Builds a unified DataFrame:
  - Uses template rules from **MetaEditor**
  - Normalizes headers and values automatically
  - Ensures deduplication if requested
  - Can append data from multiple sources incrementally
- Saves results automatically to `./Data/results/`

---

## Typical Workflow

1. **Choose a template**
   Select a JSON template describing how columns should be normalized and stored.
   Templates are usually created or edited with **MetaEditor**.

2. **Choose input files**
   Select files interactively from the `./Data/` directory.
   Examples:
   - `1 3 5` → use files number 1, 3 and 5
   - `a` → use all files
   - `c` → use only CSV files
   - `j` → use only JSON files

3. **Build the DataFrame**
   Data from all selected files is merged and normalized according to the template.
   New columns defined in the template are added on the fly if matching data is found.

4. **Save the result**
   The resulting DataFrame is saved as a `.csv` file under `./Data/results/`.
   The filename includes the template name, e.g. `result_sales_meta.csv`.

---

## Example


---

## Internals

- Uses **getdata.py** for raw file parsing and column normalization.
- Uses **etl.py** for template-based DataFrame creation and appending.
- Uses **DevMenu** for the interactive control panel.

---

## Notes

- CSV is the primary output format. If preferred, the DataFrame can also be exported to Excel (`.xlsx`) for better handling of column widths and date formats.
- Results are stored in `./Data/results/` to avoid accidental recursion (mixing inputs with outputs).

## Data Flow Diagram

```mermaid
flowchart TD
    A[Raw Data Files<br>(CSV, JSON in ./Data/)] --> B[File Selection<br>(choose_files)]
    B --> C[Template Selection<br>(choose_template)]
    C --> D[ETL Processing<br>(create/append DataFrame)]
    D --> E[Normalized DataFrame]
    E --> F[Save Result<br>(CSV in ./Data/results/)]
```
