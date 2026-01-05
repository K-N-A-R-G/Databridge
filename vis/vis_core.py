import tkinter as tk

from . visfuncs import check_empty
from custom_types import buffer
from tkinter import ttk, font as tkfont


VIS_ROOT = tk.Tk()
VIS_ROOT.withdraw()


def show_table(buffer=buffer, vis_root=VIS_ROOT):
    """
    Open a Toplevel window showing buffer as a scrollable table (Treeview).
    """
    if check_empty(buffer):
        return

    def tab_win():
        name, columns, rows = buffer.get()

        win = tk.Toplevel(vis_root)
        win.update_idletasks()
        win.update()
        win.title(name or "DataResult Viewer")
        win.rowconfigure(0, weight=1)
        win.columnconfigure(0, weight=1)
        win.geometry("800x210")

        lbl = tk.Label(
            win,
            text=name or "Result",
            font=("Arial", 12, "bold")
        )
        lbl.pack(pady=5)

        # Frame for table
        table_frame = ttk.Frame(win)
        table_frame.pack(fill="both", expand=True, padx=3, pady=10)

        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)

        # Treeview
        tree = ttk.Treeview(table_frame, columns=columns, show="headings")

        # Scrollbars
        vsb = ttk.Scrollbar(
            table_frame, orient="vertical", command=tree.yview
        )
        vsb.grid(row=0, column=1, sticky="ns")

        hsb = ttk.Scrollbar(
            table_frame, orient="horizontal", command=tree.xview
        )
        hsb.grid(row=1, column=0, sticky="ew")

        tree.configure(
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )

        tree.grid(row=0, column=0, sticky="nsew")

        # ------------------------------------------------------------------
        # DEMO auto-fit (one-shot, read-only)
        # ------------------------------------------------------------------

        style = ttk.Style()
        font_name = style.lookup("Treeview", "font")
        font = tkfont.nametofont(font_name)

        base_size = abs(font.actual()["size"])
        padding_px = 20

        column_info = {
            col: {
                "base_max": font.measure(col),  # header width
                "locked": False,
            }
            for col in columns
        }

        for row in rows:
            for col, value in zip(columns, row):
                w = font.measure(str(value))
                if w > column_info[col]["base_max"]:
                    column_info[col]["base_max"] = w

        def apply_column_widths():
            k = abs(font.actual()["size"]) / base_size

            for col in columns:
                info = column_info[col]
                if info["locked"]:
                    continue

                width = math.ceil(info["base_max"] * k) + padding_px
                tree.column(col, width=width)

        # Setup columns
        for col in columns:
            tree.heading(col, text=col, anchor="s")
            tree.column(col, anchor="s")

        # Insert rows
        for row in rows:
            tree.insert("", "end", values=row)

        # Lock column on manual resize
        def on_header_release(event):
            k = abs(font.actual()["size"]) / base_size

            for col in columns:
                if column_info[col]["locked"]:
                    continue

                expected = (
                    math.ceil(column_info[col]["base_max"] * k) + padding_px
                )
                current = tree.column(col, "width")

                if abs(current - expected) > 5:
                    column_info[col]["locked"] = True

        tree.bind("<ButtonRelease-1>", on_header_release)

    vis_root.after(100, tab_win)


def execute_sql_in_process(
                        module_name,
                        func_name,
                        DB_PATH,
                        active_table,
                        render_mode
                        ):
    import importlib
    import sqlite3

    from custom_types import buffer

    lib = importlib.import_module(module_name)
    vis = importlib.import_module('vis.visfuncs')
    func = lib.__all__[func_name]
    conn = sqlite3.connect(DB_PATH)
    vis_maker = vis.__all__[render_mode]

    func(manual=False)
    vis_maker(buffer)


def execute_pd_in_process(
                        module_name,
                        func_name,
                        DB_PATH,
                        active_table,
                        render_mode
                        ):
    import importlib
    import sqlite3
    import pandas as pd

    from custom_types import buffer

    # 1. Dynamic module import
    lib = importlib.import_module(module_name)
    vis = importlib.import_module('vis.visfuncs')

    # Extract the analytic function and the corresponding visualizer
    func = lib.__all__[func_name]
    vis_maker = vis.__all__[render_mode]

    # 2. Data preparation (Pandas enters the chat)
    print(f'\n[ENV READY] Loading table "{active_table}" into DataFrame...')
    conn = sqlite3.connect(DB_PATH)
    try:
        # Read the entire table.
        # In a separate process, this does not slow down the main terminal.
        df = pd.read_sql_query(f"SELECT * FROM {active_table}", conn)
    finally:
        conn.close()

    # 3. Execution of an analytical query, filling the buffer.
    func(df, manual=False)

    # 4. Start the visualization.
    vis_maker(buffer)
