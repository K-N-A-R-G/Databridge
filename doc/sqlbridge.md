# SQL Analytics Layer (`sqlbridge.py` & `sqlfuncs.py`)

## Overview
The SQL Layer provides a high-performance analytical bridge between the ETL storage and the visualization engine. It executes optimized queries directly on the SQLite backend, enabling complex aggregations and data transformations before passing results to the UI.

## Key Features
- **Zero-Blocking Execution**: Heavy SQL operations and subsequent graphical rendering are offloaded to isolated processes, ensuring the terminal remains responsive.
- **Dynamic Registration**: Analytical functions are defined in `sqlfuncs.py` and automatically mapped to the `DevMenu` using the `@register` decorator.
- **Universal Transport**: Query results are encapsulated in the `DataResult` buffer, decoupling the SQL engine from the specific visualization implementation.

---

## Module Structure

| Module | Responsibility |
|:--- | :--- |
| **`sqlbridge.py`** | **Execution Engine**: Manages database connections, spawns background processes for "Full" analysis, and handles terminal previews. |
| **`sqlfuncs.py`** | **Logic Library**: Contains predefined SQL analytical functions (e.g., Top Products, AOV, Window-based metrics). |

---

## Technical Workflow

### 1. Function Registration
Functions are registered with metadata to define their behavior in the UI:
- `display_name`: The label shown in the analytics menu.
- `render`: The target visualization type (`graph`, `pie`, or `table`).
- `light`: A boolean flag determining if the task runs in a thread (True) or an isolated process (False).

### 2. Multi-Mode Execution
The SQL bridge supports two primary interaction modes:

| Mode | Trigger | Behavior |
| :--- | :--- | :--- |
| **Preview** | `<Enter>` | Fetches a small result subset and prints a formatted table to the console. |
| **Full Mode**| `F` | Spawns a dedicated process that loads the full dataset, fills the `DataResult` buffer, and launches the GUI. |

### 3. Data Integration
1. The engine retrieves the active table name from `config`.
2. The selected SQL function executes a query against `bridge.db`.
3. The result (rows and columns) is passed to `buffer.set()`.
4. The Visualization module (`visfuncs.py`) picks up the data from the buffer for rendering.

---

## Usage Example (`sqlfuncs.py`)

```python
@register("Top Categories by Volume", render="pie", light=True)
def top_categories(conn, manual=True):
    query = "SELECT category, SUM(quantity) FROM data_table GROUP BY category"
    # Logic to handle terminal print vs. DataResult buffer
```

## Maintenance & Inspection

 -  preview_table(): Provides a lightweight glance at table contents without loading them into memory.

 -  list_actions(): Automatically generates the menu based on currently available functions in sqlfuncs.py.

 -  Decoupling: The SQL layer is agnostic of the ETL source; it only requires a valid SQLite table to function.

### Key Changes Implemented:
1.  **Architecture Alignment**: Updated the description to include **Process Isolation** and the **Zero-Blocking UI** concepts we implemented.
2.  **Buffer Integration**: Explicitly mentioned the **`DataResult`** buffer as the transport layer.
3.  **English Standardization**: Fully translated to match the professional tone of the new `README.md`.
4.  **Operational Clarity**: Clarified the difference between the "Bridge" (the runner) and the "Library" (the queries).

Which file is next? We still have `doc/etl.md`, `doc/getdata.md`, and the newly created `doc/vis.md` (which you might want to create based on our `visfuncs.py` work).
