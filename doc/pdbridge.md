## Pandas Analytics Module (`pdbridge.py`)

This module provides an execution layer for Pandas-based analytical functions defined in `analytics.py`.
It loads the active table from SQLite into a DataFrame, executes analytics, previews results, and stores output files.

###Database Maintenance Module (dbtools.py)

This module provides a maintenance interface for managing the SQLite database used by Databridge.
It allows listing, previewing, and deleting tables, as well as performing manual optimization.

Responsibilities

Inspect all tables stored inside the SQLite database.

Preview table contents without loading full data into memory.

Delete individual tables or wipe the entire database schema.

Execute administrative operations (e.g., VACUUM).

Present a dedicated DevMenu for database operations.

Functions
list_tables(conn: sqlite3.Connection) -> list[str]

Returns a list of all table names in the database.

preview_table(conn: sqlite3.Connection, table: str, limit: int = 10)

Displays the first limit rows of a table using Pandas for convenience.

delete_table(conn: sqlite3.Connection, table: str)

Removes a single table from the database.
If the deleted table was active, resets the active table via config.

delete_all_tables(conn: sqlite3.Connection)

Drops all tables from the database.
Resets the active table and leaves the database file empty but valid.

action_list_tables(conn)

Interactive wrapper for listing tables.

action_preview_table(conn)

Interactive wrapper for previewing selected table.

action_delete_table(conn)

Prompts the user to confirm and delete a single table.

action_delete_all(conn)

Full schema reset with confirmation.

action_vacuum(conn)

Runs SQLite VACUUM to compact the database and reclaim disk space.

make_actiondict(conn) -> dict

Builds the DevMenu ActionDict:

1 — List tables

2 — Preview table

3 — Delete table

4 — Delete all tables

5 — VACUUM

run_dbtools()

Entry point for the Database Maintenance menu:

Retrieves an active SQLite connection.

Launches the DevMenu.

Does not close the connection (DB lifecycle is managed by the main pipeline).

Workflow

User selects “Database maintenance” from the main pipeline.

The module retrieves the currently active SQLite connection.

DevMenu presents administrative options.

Actions affect database structure immediately.

Control returns to the pipeline; database remains open.

Notes

Does not close or recreate database connections.

Safe to use during long-running sessions.

VACUUM requires an open connection and may take time on large files.

Useful for cleaning up artifacts created during ETL and experimentation. Responsibilities

Retrieve the active table via `config.get_active_table()`.

Load full table contents using `pandas.read_sql_query`.

Execute analytics functions registered in `analytics.__all__`.

Provide manual preview mode for inspection.

Save analytical outputs (DataFrames) into
`Data/results/analytics/{name}.csv`.

Expose a `DevMenu` of available analytics operations.

### Functions
**`run_action(conn: sqlite3.Connection, index: int)`**

Runs a selected analytics function.

Fetches DataFrame of active table.

Calls the corresponding analytics function:

If it returns a DataFrame → preview + save.

If it returns None → preview was already shown.

If it returns a scalar → printed directly.

Handles missing columns and Pandas parsing errors gracefully.

**`preview_active_table()`**

Displays the first 5 rows of the active table.

make_actiondict(conn) -> dict

Builds the ActionDict for DevMenu:

Each registered analytics function is assigned a numbered action.

Includes an action "p" for table preview.

**`run_pd_engine()`**

Entry point for Pandas analytics:

Opens database connection via SQLite.

Shows initial table preview.

Launches DevMenu.

Returns control to the pipeline without closing the connection.

### Workflow

1. Active table is chosen through the main pipeline menu.

2. User opens "Pandas Analytics".

3. The module:

  - Loads the active table into a DataFrame.

  - Passes it to analytics functions.

  - Previews head rows.

  - Saves final DataFrame output to CSV.

4. Outputs are available for visualizations and dashboards.
---
### Notes

 - Analytics functions must accept a DataFrame and may return `pd.DataFrame,` scalar, or `None`.

 - Errors such as incompatible types or invalid date formats are shown but do not interrupt the menu.

 - Designed for clean, schema-consistent tables (produced via templates and ETL).

 - Does not modify database tables.
