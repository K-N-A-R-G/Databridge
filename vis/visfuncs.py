# vis/visfuncs.py
import math
import matplotlib.pyplot as plt
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from typing import Callable


__all__ = {}  # ← functions will be added automatically

def vis_register(mode: str):
    def wrapper(func: Callable):
        func.render_mode = mode
        __all__[mode] = func
        return func
    return wrapper


def check_empty(obj):
    if not obj:
        root = tk.Tk()
        root.title("System Notification")
        tk.Label(
            root,
            text="Empty result: Nothing to show",
            padx=20, pady=20, font=("Arial", 12)
        ).pack()
        root.mainloop()
        return True


@vis_register("bar")
def show_diagram(buffer):
    if check_empty(buffer):
        return

    root = tk.Tk()
    root.title("Quick Stats Diagram")

    name, columns, rows = buffer.get()

    labels = [str(r[0])[:10] for r in rows[:10]]
    values = [float(r[1]) if str(r[1]).replace('.','').isdigit() else 0 for r in rows[:10]]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(labels, values, color='skyblue')
    ax.set_xticks(range(len(labels))) # Put dots
    ax.set_xticklabels(labels, rotation=45, ha='right') # Subscribe dots
    ax.set_title(name)
    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()

    tk.Button(root, text="Close", command=root.destroy).pack()
    root.mainloop()



@vis_register("graph")
def show_line_graph(buffer):
    if check_empty(buffer):
        return

    root = tk.Tk()
    root.title("Line Dynamics Chart")

    name, columns, rows = buffer.get()

    # Take a little more data if available (for example, 20)
    limit = 20
    labels = [str(r[0])[:10] for r in rows[:limit]]
    values = [float(r[1]) if str(r[1]).replace('.','').isdigit() else 0 for r in rows[:limit]]

    fig, ax = plt.subplots(figsize=(10, 5))

    # Drawing a line with point markers
    ax.plot(labels, values, color='royalblue', marker='o', linestyle='-', linewidth=2)

    # Adding grid
    ax.grid(True, linestyle='--', alpha=0.6)

    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right')
    ax.set_ylim(bottom=0) # The chart always starts from zero
    ax.set_title(name)

    fig.tight_layout()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    canvas.draw()

    tk.Button(root, text="Close", command=root.destroy).pack()
    root.mainloop()


@vis_register("pie")
def show_pie_chart(buffer):
    if check_empty(buffer):
        return

    root = tk.Tk()
    root.title("Proportional Distribution")

    name, columns, rows = buffer.get()

    # --- GROUPING LOGIC “REST” ---
    limit = 7  # How many sectors to leave (including 'Others')

    # Prepare all data
    all_labels = [str(r[0]) for r in rows]
    all_values = [float(r[1]) if str(r[1]).replace('.','').isdigit() else 0 for r in rows]

    if len(all_values) > limit:
        # Detting TOP-(limit-1)
        final_values = all_values[:limit-1]
        final_labels = all_labels[:limit-1]

        # Sum up everything else
        others_sum = sum(all_values[limit-1:])
        final_values.append(others_sum)
        final_labels.append("Others")
    else:
        final_values = all_values
        final_labels = all_labels

    # --- VISUALIZATION ---
    fig, ax = plt.subplots(figsize=(10, 6), layout='constrained')

    # Draw a pie chart
    # labels=None — disable the labels for the sectors, as there will be a legend
    # autopct — leave the percentages inside the sectors

    wedges, texts, autotexts = ax.pie(
        final_values,
        autopct='%1.1f%%',
        startangle=140,
        pctdistance=0.85 # Shifting the percentages closer to the edge
    )

    # Percentage font setting (white to make it easier to read)
    plt.setp(autotexts, size=9, weight="bold", color="white")

    # --- ADDING A LEGEND ---
    # loc='center left' and bbox_to_anchor move the legend out of the circle

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
