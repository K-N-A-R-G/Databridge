# Databridge — High-Performance ETL & Analytics Platform (Demo)

## Overview
**Databridge** is a modular data analytics platform demonstrating a complete data-processing lifecycle: from raw heterogeneous sources to interactive graphical visualization.

The project is engineered with a focus on **architectural integrity** and **Zero-Blocking UI**. Heavy analytical computations and GUI rendering are offloaded to isolated system processes, ensuring the terminal interface remains responsive and "unfrozen" during complex data visualization.

### Key Technical Highlights:
- **Multiprocessing Engine**: Offloads Matplotlib and Tkinter to child processes to prevent main-loop blocking.
- **Universal Data Bridge**: Uses `DataResult` as a standardized transport layer between SQL, Pandas, and the visualization engine.
- **Hybrid Analytics**: Seamlessly switches between raw SQL aggregations (SQLite) and advanced DataFrame-based metrics (Pandas).
- **Template-Driven ETL**: Reproducible data normalization via interactive JSON-based templates.

---

## Workflow Summary
1. **Raw Data Inspection**: Raw `CSV`/`JSON` files are analyzed and normalized using interactive terminal-based templates.
2. **ETL Pipeline**: Data is converted into clean DataFrames, aligned with schemas, and persisted into a central SQLite database.
3. **Hybrid Analytics Engine**:
    - **SQL Layer**: Performs direct database-side aggregations (Window functions, complex grouping).
    - **Pandas Layer**: Calculates high-level business metrics (Retention, Time-series trends).
4. **Universal Data Transport**: Results are encapsulated into `DataResult` buffers, decoupling data origin from the display logic.
5. **Isolated Visualization**: Spawns an independent process to render GUI windows (Tkinter + Matplotlib) for charts and tables without UI lag.
6. **Maintenance & DevTools**: Utilities for schema management, database vacuuming, and synthetic noise generation for testing.

---

## Current Progress
Modules implemented:

- [`getdata.py`](./doc/getdata.md): Format detection, raw reading, and initial column cleaning.
- [`template_manager.py`](./doc/template_manager.md): Interactive manager for JSON normalization templates.
- [`etl.py`](./doc/etl.md): Core ETL logic, schema alignment, and multi-source appending.
- [`pipeline.py`](./doc/pipeline.md): Full ETL orchestration and SQLite persistence.
- [`sqlbridge.py`](./doc/sql_layer.md) / [`sqlfuncs.py`](./doc/sql_layer.md): SQL analytics layer with registered query libraries.
- [`pdbridge.py`](./doc/pdbridge.md): Pandas analytics layer supporting `Preview` and `Full` execution modes.
- [`vis/`](./doc/vis.md): Visualization engine (Bar, Line, Pie charts) running in isolated processes.
- [`dbtools.py`](./doc/dbtools.md): Database maintenance tools (Preview, Delete, Vacuum).
- [`config.py`](./doc/config.md): Centralized configuration for paths and system state.
- [`devtools.py`](./doc/devtools.md): Developer utilities for dataset splitting and stress testing.

Development logs and detailed documentation → see [`doc/`](./doc/).

---

## Skills Demonstrated
- **Advanced Python**: Multiprocessing, Threading, Decorators, Dynamic imports.
- **Data Engineering**: Template-driven ETL, Schema alignment, Data cleaning.
- **Analysis**: SQL (Complex aggregations), Pandas (Retention metrics, Time-series).
- **Architecture**: Modular design, Separation of Concerns, Inter-process Communication (IPC).

---

## Repository Structure
Databridge/
├── Data
│   ├── config.txt
│   ├── customers.csv
│   ├── customers_noisy.csv
│   ├── products.json
│   ├── results
│   │   ├── analytics
│   │   │   ├── Average Order Value (AOV).csv
│   │   │   ├── Category revenue contribution.csv
│   │   │   ├── Customer retention ratio.csv
│   │   │   ├── Monthly retention.csv
│   │   │   ├── Sales by weekday.csv
│   │   │   ├── Top customers by revenue.csv
│   │   │   └── Weekly sales trend.csv
│   │   ├── databases
│   │   │   └── bridge.db
│   │   ├── result_retail_sales_dataset_meta.csv
│   │   ├── result_retail_sales_dataset_meta.json
│   │   ├── result_retail_sales_dataset_meta.xlsx
│   │   ├── result_sales_meta.csv
│   │   ├── result_sales_meta.json
│   │   └── result_sales_meta.xlsx
│   ├── retail_sales_dataset.csv
│   ├── retail_store_sales.csv
│   ├── sales.csv
│   └── templates
│       ├── retail_sales_dataset_meta.json
│       └── sales_meta.json
├── README.md
├── __init__.py
├── config.py
├── custom_types.py
├── dbtools.py
├── devmenu.py
├── devtools.py
├── doc
│   ├── config.md
│   ├── dbtools.md
│   ├── devtools.md
│   ├── etl.md
│   ├── getdata.md
│   ├── images
│   ├── pdbridge.md
│   ├── pipeline.md
│   ├── sql_layer.md
│   └── template_manager.md
├── etl.py
├── getdata.py
├── pdbridge.py
├── pdfuncs.py
├── pipeline.py
├── shared_library.py
├── sqlbridge.py
├── sqlfuncs.py
├── temp
├── template_manager.py
└── vis
    ├── __init__.py
    ├── vis_core.py
    └── visfuncs.py

---

## Next Steps
1. **Automated Testing**: Implementing a `pytest` suite for core ETL and buffer logic.
2. **Extended Analytics**: Adding forecasting models and A/B testing statistical modules.
3. **Demo Constraints**: Integrating `DemoError` exceptions for premium-tier feature placeholders.
4. **Big Data Optimization**: Implementing data downsampling for ultra-large dataset visualization.

---
