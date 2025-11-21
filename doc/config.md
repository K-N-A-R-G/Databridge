## Configuration Module (`config.py`)

This module provides a centralized configuration layer for the Databridge project.
It defines core application paths and maintains runtime parameters such as the active database table.
All modules import settings from config.py to ensure consistent behavior across the application.

### Responsibilities

 - Define and manage core directory paths used throughout the project.

 - Store and retrieve the name of the currently active table.

 - Persist active table selection between program runs via Data/config.txt.

 - Provide a stable, module-level API for settings.

### Constants
**`BASE_DIR: Path`**

Root directory for data files:
```shell

Data/
```

**`TEMPLATES_DIR: Path`**

Location of JSON metadata templates:
```shell
Data/templates/
```
**`RESULTS_DIR: Path`**

Directory for ETL and analytics outputs:
```shell
Data/results/
```

**`DB_PATH: Path`**

Location of the SQLite database:
```shell
Data/results/databases/bridge.db
```
**`CONFIG_PATH: Path`**

Path to configuration file storing the active table name:
```shell
Data/config.txt
```
### Runtime State
**`_current_table: Optional[str]`**

Cached name of the currently active table.
Updated by `set_active_table()` and loaded lazily by `get_active_table()`.

This value is:

 - stored in memory, and

 - mirrored on disk (`config.txt`) to preserve selection between sessions.

### Functions
**`set_active_table(name: str) -> None`**

Sets the active table name for the entire application.

**Actions:**

 - Normalize and store the table name.

 - Update the in-memory cached value.

 - Persist the value to Data/config.txt.

**Used by:**

 - Pipeline menu (table selection)

 - SQL/Pandas analytics entry points

 - Database tools (reset or table deletion)

**`get_active_table() -> Optional[str]`**

Retrieves the current active table name.

**Behavior:**

 - If value is cached in `_current_table`, returns it immediately.

 - Otherwise loads it from `Data/config.txt`, if present.

 - Returns `None` if no table is currently selected.

Used by virtually all components that interact with the database.

### Usage Example
```python
from config import get_active_table, set_active_table

print("Before:", get_active_table())
set_active_table("sales_meta")
print("After:", get_active_table())
```
---
### Notes

 - config.py acts as the **single source of truth** for all runtime configuration.

 - All modules must import paths and the active table exclusively from here.

 - The configuration system is intentionally simple:

  - No environment variables

  - No .ini/.yaml files

  - No external dependencies

 - Designed for clarity, portability, and ease of debugging.
