from typing import Optional, Dict, Tuple, Callable, Any, Union

import inspect
import pandas as pd
from pathlib import Path
import sqlite3


ColumnSpec = Dict[str, Optional[Union[str, bool]]]
TemplateDict = Dict[str, ColumnSpec]

MenuNode = Tuple[str, Callable[..., Any], Tuple[Any, ...], Dict[Any, Any]]
ActionDict = Dict[str, MenuNode]


class DemoError(Exception):
    """Custom exception for demo features not yet implemented."""

    def __init__(self, ftr: Optional[str] = None) -> None:
        if ftr is None:
            frame = inspect.currentframe()
            caller = frame.f_back if frame is not None else None  # one step back: raise -> __init__
            name = caller.f_code.co_name if caller is not None else ''
            ftr = name if name != '<module>' else 'this feature'

        message = (
            f"Sorry, '{ftr}' is not implemented in the demo version, "
            "but it can be added in the applied version of the project."
        )
        super().__init__(message)

    def __str__(self) -> str:
        return str(self.args[0])


class DBConnection:
    _conn: sqlite3.Connection | None = None
    _path: Path | None = None

    @classmethod
    def get(cls, path: Path | None = None) -> sqlite3.Connection:
        """Return existing connection or open new one at given path."""
        if cls._conn is None:
            db_path = path or cls._path or Path("Data/results/databases/bridge.db")
            cls._path = db_path
            cls._conn = sqlite3.connect(db_path)
        return cls._conn

    @classmethod
    def close(cls):
        if cls._conn:
            cls._conn.close()
            cls._conn = None
            print("Database closed")
            input()


class DataResult:
    """
    Unified container for analytical results (SQL, Pandas, JSON, or list-based sources).

    The class acts as a lightweight universal data buffer shared between all modules
    of the Databridge project. It provides a consistent interface for reading,
    updating, appending, and converting tabular data — regardless of its origin.

    DataResult is intentionally minimal: it is not a full-featured DataFrame,
    but rather a stable transport format for analytical and visualization layers.

    ----------------------------------------------------------------------
    Structure
    ----------------------------------------------------------------------
    - columns : list[str]
        List of column names.
    - rows : list[tuple]
        List of row values (each row is a tuple).
    - name : str
        Optional label or identifier for the dataset (e.g. "top_products").

    ----------------------------------------------------------------------
    Core Behavior
    ----------------------------------------------------------------------
    *DataResult* can accept various input types:
        - pandas.DataFrame
        - pandas.Series
        - list[tuple] or list[list]
        - list[dict] (e.g. JSON array of objects)
        - single tuple (interpreted as one row)

    The data is stored internally as (columns, rows), ensuring uniform access
    from any analytical or visualization module.

    ----------------------------------------------------------------------
    Methods
    ----------------------------------------------------------------------

    set(data, name="")
        Replace the current contents of the buffer with new data.
        Automatically detects the data type and extracts columns/rows.

        Parameters
        ----------
        data : DataFrame | Series | list[tuple] | list[dict] | tuple
            The data to store.
        name : str, optional
            Dataset name to assign.

        Example
        -------
        >>> df = pd.DataFrame({"A": [1, 2], "B": [3, 4]})
        >>> buffer.set(df, name="simple_table")

    append_rows(data)
        Append new rows to the existing buffer, keeping current columns.
        If the buffer is empty, columns are inferred from the new data.

        Parameters
        ----------
        data : same as in `set`
            Data to append.

        Example
        -------
        >>> buffer.append_rows([("extra", 123)])

    head(n=5)
        Return the first N rows (as list of tuples).

        Example
        -------
        >>> buffer.head(3)
        [('A', 'B'), (1, 3), (2, 4)]

    as_dicts()
        Convert the stored data into list[dict] format.
        Useful for JSON serialization or dictionary-based inspection.

        Example
        -------
        >>> buffer.as_dicts()
        [{'A': 1, 'B': 3}, {'A': 2, 'B': 4}]

    __len__()
        Return the number of rows stored in the buffer.

    __repr__()
        Text preview with up to five rows, used for quick inspection in console.

        Example
        -------
        >>> print(buffer)
        <DataResult simple_table: 2 rows>
        1 | 3
        2 | 4

    ----------------------------------------------------------------------
    Typical Workflow
    ----------------------------------------------------------------------
    1) Analytical module (SQL or Pandas) loads or computes data:
        >>> buffer.set(df, name="sales_summary")

    2) Visualization module reads from the shared buffer:
        >>> df = pd.DataFrame(buffer.rows, columns=buffer.columns)

    3) Developer utilities can inspect results in terminal:
        >>> print(buffer.head())

    The same single instance (e.g. `buffer = DataResult()`) is imported
    across all Databridge modules and acts as a shared communication bridge
    between analysis, persistence, and visualization layers.
    """
    def __init__(self, columns: list[str] = None, rows: list[tuple] = None, name: str = ""):
        self.columns = columns or []
        self.rows = rows or []
        self.name = name

   # === universal write / update ===
    def set(self, data, name: str = "") -> None:
        """Accepts DataFrame, Series, list[tuple], list[dict], or JSON-like list."""
        import pandas as pd
        self.rows.clear()
        self.columns.clear()
        self._ingest(data)
        if name:
            self.name = name

    def append_rows(self, data) -> None:
        """Append data of any supported type to current rows."""
        new_rows = []
        new_columns = []

        if isinstance(data, pd.DataFrame):
            new_columns = list(data.columns)
            new_rows = [tuple(r) for r in data.itertuples(index=False, name=None)]

        elif isinstance(data, pd.Series):
            new_columns = ["index", "value"]
            new_rows = list(zip(data.index.tolist(), data.tolist()))

        elif isinstance(data, list) and data and isinstance(data[0], dict):
            new_columns = list(data[0].keys())
            new_rows = [tuple(d[c] for c in new_columns) for d in data]

        elif isinstance(data, list) and data and isinstance(data[0], (tuple, list)):
            new_rows = [tuple(r) for r in data]

        elif isinstance(data, tuple):
            new_rows = [data]

        else:
            raise TypeError(f"Unsupported type for DataResult.append_rows(): {type(data)}")

        # if no columns exist yet, inherit them from appended data
        if not self.columns and new_columns:
            self.columns = new_columns
        self.rows.extend(new_rows)

    # === internal reader ===
    def _ingest(self, data) -> None:
        """Internal helper for set(): shared type detection logic."""
        import pandas as pd
        if isinstance(data, pd.DataFrame):
            self.columns = list(data.columns)
            self.rows = [tuple(r) for r in data.itertuples(index=False, name=None)]
        elif isinstance(data, pd.Series):
            self.columns = ["index", "value"]
            self.rows = list(zip(data.index.tolist(), data.tolist()))
        elif isinstance(data, list) and data and isinstance(data[0], dict):
            self.columns = list(data[0].keys())
            self.rows = [tuple(d[c] for c in self.columns) for d in data]
        elif isinstance(data, list) and data and isinstance(data[0], (tuple, list)):
            self.columns = [f"col{i}" for i in range(len(data[0]))]
            self.rows = [tuple(r) for r in data]
        elif isinstance(data, tuple):
            self.columns = [f"col{i}" for i in range(len(data))]
            self.rows = [data]
        else:
            raise TypeError(f"Unsupported type for DataResult.set(): {type(data)}")

    # === read / representation ===
    def head(self, n=5): return self.rows[:n]
    def as_dicts(self): return [dict(zip(self.columns, r)) for r in self.rows]
    def __len__(self): return len(self.rows)
    def __repr__(self):
        lines = [" | ".join(map(str, row)) for row in self.head(5)]
        return f"<DataResult {self.name or ''}: {len(self.rows)} rows>\n" + "\n".join(lines)


buffer = DataResult()
