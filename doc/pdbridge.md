# Pandas Analytics & Database Maintenance

## 1. Pandas Analytics Module (`pdbridge.py` & `pdfuncs.py`)

### Overview
This module serves as the execution engine for DataFrame-based analytics. Unlike standard scripts, it implements a **Zero-Blocking UI** strategy by offloading heavy computations and GUI rendering to isolated system processes.

### Key Features
- **Process Isolation**: Spawns independent processes for data visualization (Matplotlib/Tkinter) to keep the main menu responsive.
- **Hybrid Execution Modes**:
    - **Preview Mode**: Fast, low-memory execution using a `LIMIT 5` subset for instant terminal feedback.
    - **Full Mode**: Comprehensive analysis on the entire dataset with optional graphical output.
- **Universal Data Transport**: Results are wrapped in the `DataResult` buffer, ensuring compatibility between the analytical engine and the visualization layer.

### Core Functions
- **`run_pd_engine(conn)`**: The main entry point for executing analytics. It detects whether to run a lightweight preview or a full background process based on user input.
- **`execute_pd_in_process(...)`**: A specialized worker function that handles heavy imports (like Pandas/Matplotlib) and data loading inside a child process to maintain main-process agility.
- **`@register` (Decorator)**: Located in `pdfuncs.py`, it manages function metadata such as display names, rendering modes (`graph`, `pie`, `table`, `bar`), and execution weight.

### Analytical Workflow
1. **User Selection**: An analytical function is chosen from the `DevMenu`.
2. **Mode Selection**: User chooses between a terminal **Preview** or **Full** analysis.
3. **Execution**:
    - **Preview**: Loads a micro-subset of the active table and prints the result.
    - **Full**: Offloads the task to a background process.
4. **Output**: Results are stored in the `DataResult` buffer and passed to `visfuncs.py` for rendering.

---
