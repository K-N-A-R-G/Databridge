# SQL Layer for Databridge

## Overview
The SQL Layer provides an analytical bridge between the ETL output and the visualization stage.
It stores cleaned data in an SQLite database and allows interactive or automated analytical operations.

---

## Structure

| Module | Purpose |
|---------|----------|
| **sqlbridge.py** | Core of the SQL layer. Creates and manages databases, executes queries, lists saved DBs, previews tables, and integrates with DevMenu. |
| **sqlfuncs.py** | A library of predefined analytical SQL functions (e.g., top products, average daily sales, rolling metrics). Each function is registered automatically for use in DevMenu or pipelines. |

---

## Key Components

### `init_db(tables: dict[str, pd.DataFrame]) -> sqlite3.Connection`
Creates a database from ETL DataFrames. Replaces existing tables if necessary.

### `query(conn, sql, params=None) -> pd.DataFrame`
Executes arbitrary SQL and returns results as a DataFrame.

### `list_databases()`, `inspect_db(path)`, `preview_table(path, table, limit)`
Provide lightweight inspection and preview of saved `.db` files without full loading.

### `list_actions()`, `run_action()`, `make_sql_actiondict(conn)`
Provide dynamic enumeration and invocation of all registered SQL functions, compatible with DevMenu.

---

## Usage
- From `pipeline.py`, call `init_db()` after ETL completion.
- Launch `DevMenu(make_sql_actiondict(conn))` for manual exploration or testing.
- Extend analytical coverage by adding new SQL functions in `sqlfuncs.py` using the `@register` decorator.

---

## Notes
- SQL layer is completely decoupled from ETL and visualization.
- All paths use local `Data/results/databases/` as the storage location.
- Fully compatible with both manual (DevMenu) and automated (pipeline) flows.
