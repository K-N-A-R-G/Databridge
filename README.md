# Mini-project “databridge” – updated plan

## 1. Project Goals
- Demonstrate working with data from raw sources to visualization and business analysis.
- Show skills in Python, SQL, data cleaning and normalization.
- Interact with business requirements through analytical queries and visualization.

## 2. Data Sources (test)
- **sales.csv**: date, product, price, quantity.
- **customers.csv**: customer info, region, segment, age.
- **products.json**: categories, cost, discount.

Reasons for cleaning/normalization:
- Missing values.
- Different date formats.
- Duplicate records.
- Inconsistent categories.

## 3. ETL / ELT

### Implemented

**Module: getdata.py**
- `read_data(path: str) -> list[Any]`
  - Reads CSV or JSON (auto-detects format).
  - Demo mode: raises `DemoError` if file >10 MB.
  - Returns data as a list of rows/structures.

- `detect_format(path: str) -> str`
  - Detects format from first lines.
  - JSON → starts with `[` or `{`.
  - CSV → only one separator from (`,`, `;`, `\t`).

- `normalize_column(values: pd.Series, target_name: str, dtype: type, format_spec: str = None, header_case: str = None) -> pd.Series`
  - Universal function for converting one column to target type/format (str, int, float, numeric, date).
  - Applies numeric/float formatting (e.g. `:.3f`) and date formatting.
  - Used both for MetaEditor preview and full DataFrame normalization.

- Extra parsers: `parse_number`, `parse_date`, `parse_bool`, `normalize_text` (experimental).

- `normalize_data(data: list[Any], original_format: str) -> pd.DataFrame`
  - Converts to numeric where possible.
  - Tries to detect dates.
  - Other columns → strings.
  - Always returns a DataFrame.

**Module: noise.py**
- `add_noise(input_path: Path, level: float = 0.1, write_file: bool = False) -> Tuple[List[Any]]`
  - Adds “noise” into data: `None`, wrong types, corrupted strings/dates.
  - Demo mode: only in memory, `write_file` is a placeholder.

**Module: metaeditor.py**
- `MetaEditor` — interactive tool for creating JSON normalization templates:
  - Allows setting header case, column type, format.
  - Saves only manually selected columns (avoids JSON clutter).
  - Uses `normalize_column` for preview (shows real transformed values).
  - Template can be reused for any file with matching column names.

**Intermediate result:**
- Any CSV/JSON → normalized DataFrame ready for SQL and visualization.

## 4. SQL / Queries
Planned:
- SQLite/PostgreSQL for storage and queries.
- Examples with JOIN, GROUP BY, window functions.
- Functions like:
  - `aggregate_sales(df: pd.DataFrame) -> pd.DataFrame`
  - `top_products_by_region(df: pd.DataFrame, start_date, end_date) -> pd.DataFrame`

## 5. Visualization
Planned:
- `matplotlib` + `Tkinter` for parallel windows.
- Charts:
  - **Bar**: top categories by revenue.
  - **Line**: sales trend.
  - **Pie**: customer segment distribution.
- API functions:
  - `plot_top_categories(df: pd.DataFrame, n=5)`
  - `plot_sales_trend(df: pd.DataFrame)`
  - `plot_customer_segments(df: pd.DataFrame)`

## 6. Project Demonstration Criteria
- Sources → ETL/ELT → normalization.
- SQL queries showing aggregation and advanced selection.
- Visualization for business analysis.
- Short log/report: what was cleaned, what conclusions were made.

## 7. Skills Demonstrated
- Data preparation, cleaning, normalization.
- Python (pandas, numpy, matplotlib/seaborn).
- SQL (JOIN, GROUP BY, window functions).
- Business requirement interpretation.
- Data visualization and interactive windows.
- ML critique (simple regression, error analysis).

## 8. Modules Implemented

| Module         | Functions / Classes | Description |
|----------------|----------------------|-------------|
| custom_types.py | DemoError | “Demo version” exception. |
| devmenu.py     | DevMenu | CLI menu for launching functions. |
| metaeditor.py  | MetaEditor | Interactive tool for normalization template (headers, types, format). Uses `normalize_column` for preview. |
| getdata.py     | detect_format | Detects CSV/JSON format. |
| getdata.py     | read_data | Reads file, returns `(format, list of dicts)`. |
| getdata.py     | normalize_column | Normalizes one column (type, format, header case). |
| getdata.py     | normalize_data | Converts raw list into DataFrame. |
| noise.py       | add_noise | Adds artificial noise into data. |

## 9. Next Steps
1. ETL / merging sources.
2. SQL / aggregated queries.
3. Visualization.
4. ML critique.
5. Documentation & polishing.
[Optional] — test coverage.
