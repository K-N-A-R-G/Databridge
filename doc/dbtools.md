## Database Maintenance Module (`dbtools.py`)

This module provides a maintenance interface for managing the SQLite database used by Databridge.
It allows listing, previewing, and deleting tables, as well as performing manual optimization.

Responsibilities

 - Inspect all tables stored inside the SQLite database.

 - Preview table contents without loading full data into memory.

 - Delete individual tables or wipe the entire database schema.

 - Execute administrative operations (e.g., VACUUM).

 - Present a dedicated DevMenu for database operations.

### Functions
**`list_tables(conn: sqlite3.Connection) -> list[str]`**

Returns a list of all table names in the database.

**`preview_table(conn: sqlite3.Connection, table: str, limit: int = 10)`**

Displays the first `limit` rows of a table using Pandas for convenience.

**`delete_table(conn: sqlite3.Connection, table: str)`**

Removes a single table from the database.
If the deleted table was active, resets the active table via config.

**`delete_all_tables(conn: sqlite3.Connection)`**

Drops all tables from the database.
Resets the active table and leaves the database file empty but valid.

**`action_list_tables(conn)`**

Interactive wrapper for listing tables.

**`action_preview_table(conn)`**

Interactive wrapper for previewing selected table.

**`action_delete_table(conn)`**

Prompts the user to confirm and delete a single table.

**`action_delete_all(conn)`**

Full schema reset with confirmation.

**`action_vacuum(conn)`**

Runs SQLite VACUUM to compact the database and reclaim disk space.

**`make_actiondict(conn) -> dict`**

Builds the DevMenu ActionDict:

 - 1 — List tables

 - 2 — Preview table

 - 3 — Delete table

 - 4 — Delete all tables

 - 5 — VACUUM


**`run_dbtools()`**

Entry point for the Database Maintenance menu:

 - Retrieves an active SQLite connection.

 - Launches the DevMenu.

 - Does not close the connection (DB lifecycle is managed by the main pipeline).
---

### Workflow

 1. User selects “Database maintenance” from the main pipeline.

 2. The module retrieves the currently active SQLite connection.

 3. DevMenu presents administrative options.

 4. Actions affect database structure immediately.

 5. Control returns to the pipeline; database remains open.
---

### Notes

 - Does not close or recreate database connections.

 - Safe to use during long-running sessions.

 - VACUUM requires an open connection and may take time on large files.

 - Useful for cleaning up artifacts created during ETL and experimentation.
