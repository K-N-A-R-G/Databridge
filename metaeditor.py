from datetime import datetime
from devmenu import DevMenu
from getdata import normalize_column, detect_format
from pathlib import Path

import json
import pandas as pd
import re

class MetaEditor:
    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.data = pd.DataFrame()
        self.headers: List[str] = []
        self.meta: dict[str, dict[str, Any]] = {}  # target_name, type, format, header_case, save_flag

        self.load_file()

    def load_file(self):
        fmt = detect_format(self.file_path)
        sample = self.file_path.read_text(encoding="utf-8")[:2048]

        if fmt == "json":
            try:
                data_obj = json.loads(sample)
                if isinstance(data_obj, list) and data_obj:
                    self.data = pd.DataFrame(data_obj)
                elif isinstance(data_obj, dict):
                    self.data = pd.DataFrame([data_obj])
                else:
                    self.data = pd.DataFrame()
            except Exception:
                self.data = pd.DataFrame()
        elif fmt == "csv":
            self.data = pd.read_csv(self.file_path)
        else:
            self.data = pd.DataFrame()

        self.headers = list(self.data.columns)
        for h in self.headers:
            self.meta[h] = {
                "target_name": h,
                "type": str,
                "format": None,
                "header_case": None,
                "save": False
            }

    def show_headers(self):
        print("Current headers and metadata:")
        for h, m in self.meta.items():
            print(f"{h} → {m}\n")

    def edit_header(self):
        while True:
            self.show_headers()
            name = input("Header to edit (or blank to exit): ").strip()
            if not name:
                break
            if name not in self.meta:
                print("Unknown header.")
                continue

            col_meta = self.meta[name]
            print(f"Editing {name}: {col_meta}")

            # --- Header normalization choice ---
            print("Normalization options:")
            print("  1) lower")
            print("  2) capitalize")
            print("  3) title")
            print("  4) upper")
            choice = input(f"Choose normalization [default={col_meta['header_case']}]: ").strip()
            header_case_map = {"1": "lower", "2": "capitalize", "3": "title", "4": "upper"}
            col_meta["header_case"] = header_case_map.get(choice, col_meta["header_case"])

            # --- Type and format ---
            dtype_input = input(f"Type (str,int,float,date) [{col_meta['type'].__name__}]: ").strip()
            col_meta["type"] = {
                "str": str,
                "int": int,
                "float": float,
                "date": "date"
            }.get(dtype_input, col_meta["type"])

            fmt = input(f"Format (optional) [{col_meta['format']}]: ").strip()
            col_meta["format"] = fmt if fmt else col_meta["format"]

            # --- Preview using normalize_column ---
            preview = normalize_column(
                self.data[name].head(5),
                target_name=col_meta["target_name"],
                dtype=col_meta["type"],
                format_spec=col_meta["format"],
                header_case=col_meta["header_case"]
            )
            print(f"\nPreview of '{name}' column:\n{preview}\n")

            # --- Save flag ---
            save_flag = input("Select column for saving? [y/N]: ").strip().lower()
            col_meta["save"] = save_flag == "y"

    def save_meta(self, path: Path):
        # Save only manually selected columns
        save_meta = {h: m for h, m in self.meta.items() if m.get("save")}
        # Convert types to string to make JSON serializable
        for m in save_meta.values():
            if isinstance(m.get("type"), type):
                m["type"] = m["type"].__name__
        with path.open("w", encoding="utf-8") as f:
            json.dump(save_meta, f, ensure_ascii=False, indent=2)



# --- Helper to run editor --------------------------------------------------
def run_metaeditor(path: Path):
    editor = MetaEditor(path)
    editor.edit_header()
    save = input("Save metadata to file? [y/N]: ").strip().lower()
    if save == "y":
        if save == "y":
            out = path.with_suffix("")  # remove ext
            out = out.with_name(out.name + "_meta.json")
        editor.save_meta(out)
        print(f"Metadata saved to {out}")


menu_actions = {
    "1": ("Edit metadata", run_metaeditor, (Path("Data/sales.csv"),), {})
}

if __name__ == "__main__":
    DevMenu(menu_actions, title="MetaEditor Menu").run()
