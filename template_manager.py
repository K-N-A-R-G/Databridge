from devmenu import DevMenu
from getdata import normalize_column, detect_format
from pathlib import Path

import json
import pandas as pd
from typing import Any, List


class MetaEditor:
    TYPES = {
        "str": str,
        "int": int,
        "float": float,
        "date": "date",
    }

    def __init__(self, file_path: Path):
        self.file_path = file_path
        self.data = pd.DataFrame()
        self.headers: List[str] = []
        self.meta: dict[str, dict[str, Any]] = {}
        self.template_path = self.file_path.parent / "templates" / (self.file_path.stem + "_meta.json")
        self.load_file()
        self.load_template()

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
            if h not in self.meta:
                self.meta[h] = {
                    "target_name": h,
                    "type": "str",
                    "format": None,
                    "header_case": None,
                    "save": False,
                }

    def load_template(self):
        if self.template_path.exists():
            try:
                template_data = json.loads(self.template_path.read_text(encoding="utf-8"))
                for h, m in template_data.items():
                    if h in self.meta:
                        self.meta[h].update(m)
            except Exception:
                print(f"Warning: could not load template {self.template_path}")

    def show_headers(self):
        print(f"\nEditing file: {self.file_path}\n")
        print("Current headers and metadata:")
        for h, m in self.meta.items():
            save_mark = "\033[92m[S]\033[0m" if m.get("save") else "[ ]"  # зеленый [S] или пустой [ ]
            print(f"{h} {save_mark} → type={m['type']}, format={m['format']}, header_case={m['header_case']}")
        print()

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

            # --- Header normalization choice ---
            print("Normalization options:")
            print("  1) lower")
            print("  2) capitalize")
            print("  3) title")
            print("  4) upper")
            default_case = col_meta['header_case'] or 'None'
            choice = input(f"Choose normalization [default={default_case}]: ").strip()
            header_case_map = {"1": "lower", "2": "capitalize", "3": "title", "4": "upper"}
            col_meta["header_case"] = header_case_map.get(choice, col_meta["header_case"])

            # --- Type and format ---
            default_type = col_meta["type"]
            dtype_input = input(f"Type (str,int,float,date) [default={default_type}]: ").strip()
            if dtype_input in self.TYPES:
                col_meta["type"] = dtype_input

            default_fmt = col_meta["format"]
            fmt = input(f"Format (optional) [default={default_fmt}]: ").strip()
            col_meta["format"] = fmt if fmt else col_meta["format"]

            # --- Preview using normalize_column ---
            dtype_for_preview = self.TYPES[col_meta["type"]]
            preview = normalize_column(
                self.data[name].head(5),
                target_name=col_meta["target_name"],
                dtype=dtype_for_preview,
                format_spec=col_meta["format"],
                header_case=col_meta["header_case"],
            )
            print(f"\nPreview of '{name}' column:\n{preview}\n")

            # --- Save flag ---
            default_save = 'y' if col_meta['save'] else 'n'
            save_flag = input(f"Select column for saving? [y/N] [default={default_save}]: ").strip().lower()
            if save_flag == '':
                save_flag = default_save
            col_meta["save"] = save_flag == "y"

    def save_meta(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        save_meta = {h: m for h, m in self.meta.items() if m.get("save")}
        with path.open("w", encoding="utf-8") as f:
            json.dump(save_meta, f, ensure_ascii=False, indent=2)


# --- Helper to run editor --------------------------------------------------
def run_metaeditor(filename: str):
    # всегда внутри Data/
    path = Path("Data") / filename
    editor = MetaEditor(path)
    editor.edit_header()
    save = input("Save metadata to file? [y/N]: ").strip().lower()
    if save == "y":
        out = path.parent / "templates" / (path.stem + "_meta.json")
        out.parent.mkdir(parents=True, exist_ok=True)
        editor.save_meta(out)
        print(f"Metadata saved to {out}")


def select_or_create_template(filename: str) -> Path | None:
    """
    Проверяет наличие шаблона для данного файла.
    Если нет — предлагает создать новый или использовать существующий как основу.
    Возвращает путь к выбранному/новому шаблону или None при отмене.
    """
    data_path = Path("Data")
    templates_path = data_path / "templates"
    templates_path.mkdir(parents=True, exist_ok=True)

    file_template = templates_path / f"{Path(filename).stem}_meta.json"

    if file_template.exists():
        try:
            with file_template.open("r", encoding="utf-8") as f:
                tmpl_data = json.load(f)
            print(f"\nTemplate found for '{filename}': {file_template.name}")
            for h, m in tmpl_data.items():
                save_mark = "[S]" if m.get("save") else "[ ]"
                print(f"{h} → type={m.get('type')}, format={m.get('format')}, header_case={m.get('header_case')}")
        except Exception:
            print("Failed to load template. Will need to create a new one.")
            tmpl_data = {}

        while True:
            print("\nOptions:")
            print("1) Confirm template")
            print("2) Edit template")
            print("3) Exit")
            choice = input("> ").strip()
            if choice == "1":
                return file_template
            elif choice == "2":
                editor = MetaEditor(Path("Data") / filename)
                # инициализируем meta из загруженного шаблона
                for h, m in tmpl_data.items():
                    if h in editor.meta:
                        editor.meta[h].update(m)
                editor.edit_header()
                save_new = input(f"Save edited template for '{filename}'? [y/N]: ").strip().lower()
                if save_new == "y":
                    editor.save_meta(file_template)
                    print(f"Template saved: {file_template}")
                return file_template
            elif choice == "3":
                return None

    # Нет шаблона — предложим варианты
    print(f"No template found for '{filename}'.")
    while True:
        print("\nOptions:")
        print("1) Create new template")
        print("2) Use existing template as base")
        print("3) Exit")
        choice = input("> ").strip()
        if choice == "1":
            editor = MetaEditor(data_path / filename)
            editor.edit_header()
            save = input(f"Save new template for '{filename}'? [y/N]: ").strip().lower()
            if save == "y":
                file_template.parent.mkdir(parents=True, exist_ok=True)
                editor.save_meta(file_template)
                print(f"Template saved: {file_template}")
                return file_template
            else:
                print("Cancelled. Returning to options.")
        elif choice == "2":
            # Список всех шаблонов в templates
            available = sorted([p for p in templates_path.glob("*_meta.json")])
            if not available:
                print("No existing templates available.")
                continue
            while True:
                print("\nAvailable templates:")
                for i, p in enumerate(available, 1):
                    print(f"{i}) {p.name}")
                print("0) Back")
                sel = input("Select template to view/edit: ").strip()
                if sel == "0":
                    break
                if not sel.isdigit() or not (1 <= int(sel) <= len(available)):
                    print("Invalid selection.")
                    continue
                base_template = available[int(sel) - 1]
                # Загрузить и показать
                try:
                    with base_template.open("r", encoding="utf-8") as f:
                        tmpl_data = json.load(f)
                    print(f"\nTemplate: {base_template.name}")
                    for h, m in tmpl_data.items():
                        save_mark = "[S]" if m.get("save") else "[ ]"
                        print(f"{h} {save_mark} → type={m.get('type')}, format={m.get('format')}, header_case={m.get('header_case')}")
                except Exception:
                    print("Failed to load template.")
                    continue

                # Опции просмотра/редактирования
                print("\nOptions:")
                print("1) Edit this template as new template")
                print("2) Back to template list")
                action = input("> ").strip()
                if action == "1":
                    editor = MetaEditor(data_path / filename)
                    # Инициализируем meta из выбранного шаблона
                    for h, m in tmpl_data.items():
                        if h in editor.meta:
                            editor.meta[h].update(m)
                    editor.edit_header()
                    save_new = input(f"Save as new template for '{filename}'? [y/N]: ").strip().lower()
                    if save_new == "y":
                        editor.save_meta(file_template)
                        print(f"New template saved: {file_template}")
                        return file_template
                    else:
                        print("Cancelled. Returning to template list.")
                elif action == "2":
                    continue
        elif choice == "3":
            return None



menu_actions = {
    "1": ("Select/edit metadata", select_or_create_template, ("sales.csv",), {})
}

if __name__ == "__main__":
    filename = 'sales.csv'
    DevMenu(menu_actions, title="MetaEditor Menu").run()
