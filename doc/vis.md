## Visualization Core (`vis_core.py`)

The vis_core module acts as the graphical engine of the Databridge platform. It manages data rendering and window lifecycle management within a multi-threaded environment.
### Key Features
1. **Interactive Data Tables (show_table)**
Renders the contents of the DataResult buffer into a structured, scrollable table using Tkinter's Treeview.
  - **Intelligent Auto-fit:** The system automatically calculates optimal column widths based on both header text and cell content.
  - **Dynamic Header Locking:** If a user manually resizes a column, the automatic scaling for that specific column is disabled to respect user intent.
  - **Thread-Safe Rendering:** Windows are spawned via the .after() method, allowing the CLI to trigger GUI elements from background threads without crashing the main event loop.
2. **Isolated Analytical Processes (execute_in_process)**
To handle heavy computations (Pandas/SQL) and advanced charting (Matplotlib), the core spawns independent OS processes.
  - **Zero-Blocking Architecture:** The main terminal remains fully responsive while complex calculations and rendering take place in the background.
  - **Dynamic Module Loading:** Uses importlib to load analytical and visualization functions on-the-fly, providing high extensibility.
  - **Context Isolation:** Each process maintains its own database connection and memory space, preventing resource contention and ensuring stability.

### Window Management Architecture
The system utilizes a hybrid UI synchronization scheme:

  - **The Anchor:** A hidden VIS_ROOT (instance of `tk.Tk`) is initialized in the application's Main Thread.
  - **Sub-windows:** All data tables are opened as Toplevel windows anchored to this root.
  - **Analytics Sub-processes:** Heavy visualization tasks are completely decoupled from the parent process, running in their own dedicated memory space.

### Developer Technical Specs

  - **Data Transport Protocol:** Data transfer between the analytical engine and the visualizer within a process is handled via the universal buffer object (from `custom_types`).
  - **Reflective Routing:** Both `execute_sql_in_process` and `execute_pd_in_process` resolve module and function names dynamically through the `__all__` export dicts of the target libraries.
