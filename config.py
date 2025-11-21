"""
config.py — lightweight runtime settings for Databridge
Stores user-selected options like active table or paths.
"""

from pathlib import Path
from typing import Optional


BASE_DIR = Path("Data")
TEMPLATES_DIR = BASE_DIR / "templates"
RESULTS_DIR = BASE_DIR / "results"
DB_PATH = RESULTS_DIR / "databases" / "bridge.db"
CONFIG_PATH = Path("Data/config.txt")

_current_table: Optional[str] = None


def set_active_table(name: str) -> None:
    """Sets and saves active table name."""
    name = name.strip()
    _current_table = name
    CONFIG_PATH.write_text(name)


def get_active_table() -> Optional[str]:
    """Returns currently active table."""
    try:
        val = CONFIG_PATH.read_text().strip()
        _current_table = val
    except Exception as ex:
        raise(ex, 'No active table selected yet')
    print(f'get {_current_table}')
    return _current_table
