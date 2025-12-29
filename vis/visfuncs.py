# vis/visfuncs.py
import io
import math
import matplotlib.pyplot as plt
import tkinter as tk
import threading
import time

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from multiprocessing import Process, Queue
from PIL import Image, ImageTk
from tkinter import ttk, TclError, font as tkfont
from typing import Callable


__all__ = {}  # ← functions will be added automatically

def vis_register(mode: str):
    def wrapper(func: Callable):
        func.render_mode = mode
        __all__[mode] = func
        return func
    return wrapper


@vis_register("table")
def show_table(buffer, vis_root=None):
    """
    Open a Toplevel window showing buffer as a scrollable table (Treeview).
    """

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

        # ------------------------------------------------------------------
        # Setup columns
        # ------------------------------------------------------------------

        for col in columns:
            tree.heading(col, text=col, anchor="s")
            tree.column(col, anchor="s")

        # apply_column_widths()

        # ------------------------------------------------------------------
        # Insert rows
        # ------------------------------------------------------------------

        for row in rows:
            tree.insert("", "end", values=row)

        # ------------------------------------------------------------------
        # Lock column on manual resize
        # ------------------------------------------------------------------

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


@vis_register("bar")
def show_diagram(buffer):
    root = tk.Tk()
    root.title("Quick Stats Diagram")

    name, columns, rows = buffer.get()

    labels = [str(r[0])[:10] for r in rows[:10]]
    values = [float(r[1]) if str(r[1]).replace('.','').isdigit() else 0 for r in rows[:10]]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(labels, values, color='skyblue')
    ax.set_xticks(range(len(labels))) # Сначала ставим точки
    ax.set_xticklabels(labels, rotation=45, ha='right') # Потом подписываем
    ax.set_title(name)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()

    tk.Button(root, text="Close", command=root.destroy).pack()
    root.mainloop()



@vis_register("graph")
def show_line_graph(buffer):
    root = tk.Tk()
    root.title("Line Dynamics Chart")

    name, columns, rows = buffer.get()

    # Берем чуть больше данных, если они есть (например, 20)
    limit = 20
    labels = [str(r[0])[:10] for r in rows[:limit]]
    values = [float(r[1]) if str(r[1]).replace('.','').isdigit() else 0 for r in rows[:limit]]

    fig, ax = plt.subplots(figsize=(10, 5))

    # Рисуем линию с маркерами-точками
    ax.plot(labels, values, color='royalblue', marker='o', linestyle='-', linewidth=2)

    # Добавляем сетку, чтобы график не висел в пустоте
    ax.grid(True, linestyle='--', alpha=0.6)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_ylim(bottom=0) # Чтобы график всегда начинался от нуля
    ax.set_title(name)

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()

    tk.Button(root, text="Close", command=root.destroy).pack()
    root.mainloop()


@vis_register("pie")
def show_pie_chart(buffer):
    root = tk.Tk()
    root.title("Proportional Distribution")

    name, columns, rows = buffer.get()

    # --- ЛОГИКА ГРУППИРОВКИ «ОСТАЛЬНОЕ» ---
    limit = 7  # Сколько секторов оставить (включая "Others")

    # Подготовка всех данных
    all_labels = [str(r[0]) for r in rows]
    all_values = [float(r[1]) if str(r[1]).replace('.','').isdigit() else 0 for r in rows]

    if len(all_values) > limit:
        # Берем ТОП-(limit-1)
        final_values = all_values[:limit-1]
        final_labels = all_labels[:limit-1]

        # Суммируем всё остальное
        others_sum = sum(all_values[limit-1:])
        final_values.append(others_sum)
        final_labels.append("Others")
    else:
        final_values = all_values
        final_labels = all_labels

    # --- ВИЗУАЛИЗАЦИЯ ---
    fig, ax = plt.subplots(figsize=(10, 6), layout='constrained')

    # Рисуем круговую диаграмму
    # labels=None — отключаем подписи у секторов, так как будет легенда
    # autopct — оставляем проценты внутри секторов
    wedges, texts, autotexts = ax.pie(
        final_values,
        autopct='%1.1f%%',
        startangle=140,
        pctdistance=0.85 # Смещаем проценты ближе к краю
    )

    # Настройка шрифта процентов (белый, чтобы лучше читался)
    plt.setp(autotexts, size=9, weight="bold", color="white")

    # --- ДОБАВЛЕНИЕ ЛЕГЕНДЫ ---
    # loc="center left" и bbox_to_anchor выносят легенду за пределы круга
    ax.legend(
        wedges,
        final_labels,
        title="Categories",
        loc="center left",
        bbox_to_anchor=(1, 0, 0.5, 1)
    )

    ax.set_title(name, pad=20)

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()

    tk.Button(root, text="Close", command=root.destroy).pack()
    root.mainloop()
