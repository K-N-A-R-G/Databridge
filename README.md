# Databridge — Demo ETL/Analytics Project

## Overview
**Databridge** is a modular demo project showcasing a complete data-processing workflow:
raw sources → normalization → ETL → SQLite storage → analytics (SQL & Pandas) → visualization outputs.

The project is designed to demonstrate:
- structured ETL pipeline design,
- reproducible data normalization using templates,
- SQL and Pandas analytics separation,
- modular architecture with clear responsibilities,
- practical application of Python tooling.

---

## Workflow Summary
1. **Raw data** (`CSV`/`JSON`) is inspected and normalized using interactive templates.
2. **ETL stage** converts files into clean DataFrames according to template rules.
3. **SQLite** becomes the central storage: all normalized DataFrames are persisted as tables.
4. **SQL analytics** operates directly on the SQLite tables.
5. **Pandas analytics** works on the active table, producing analytical DataFrames.
6. **Results** (aggregations, trends, categories) are saved as CSV for visualization.
7. **Maintenance tools** allow managing tables (preview, delete, vacuum).

---

## Current Progress
Modules implemented:

  - [`getdata.py`](./doc/getdata.md): detect format, read raw files, normalize headers and column values.
  - [`template_manager.py`](./doc/template_manager.md): interactive creation and editing of normalization templates.
  - [`etl.py`](./doc/etl.md): build normalized DataFrames using templates; append multiple sources; align schema.
  - [`devtools.py`](./doc/devtools.md): developer utilities for splitting files, adding noise, testing workflows.
  - [`pipeline.py`](./doc/pipeline.md): orchestrates the full ETL process, manages templates, builds DataFrames, writes results to SQLite.
  - [`sqlbridge.py`](./doc/sql_layer.md) / [`sqlfuncs.py`](./doc/sql_layer.md): SQL analytics layer — executes analytical SQL queries on tables stored in `bridge.db`.
  - [`pandasbridge.py`](./doc/pdbridge.md): Pandas analytics layer — runs DataFrame-based analytics on the active table and saves results.
  - [`dbtools.py`](./doc/dbtools.md): database maintenance tools — list, preview, delete, and vacuum SQLite tables.
  - [`config.py`](./doc/config.md): centralized configuration module — manages paths, active table state, and common runtime settings.

Development logs, detailed docs and examples → see [`doc/`](./doc/).

---

## Demonstration Criteria
- Consistent ETL process from multiple heterogeneous sources.
- SQL analytics (aggregations, grouping, joins).
- Pandas analytics (trends, grouping, retention metrics).
- Result files for further visualization (CSV).
- Clear documentation of each module and stage.

---

## Skills Demonstrated
- Python (pandas, sqlite3, pathlib)
- ETL design and template-driven normalization
- SQL (GROUP BY, window functions)
- Data cleaning and schema alignment
- Modular architecture and reproducible workflows

---

## Repository Structure
```
Databridge/
├── Data
│   ├── config.txt
│   ├── customers.csv
│   ├── customers_noisy.csv
│   ├── products.json
│   ├── results
│   │   ├── analytics
│   │   │   ├── Average Order Value (AOV).csv
│   │   │   │   ...
│   │   │   └── Weekly sales trend.csv
│   │   ├── databases
│   │   │   └── bridge.db
│   │   ├── result_retail_sales_dataset_meta.csv
│   │   │   ...
│   │   └── result_sales_meta.xlsx
│   ├── retail_sales_dataset.csv
│   ├   ...
│   ├── sales.csv
│   └── templates
│       ├── retail_sales_dataset_meta.json
│       └── sales_meta.json
├── README.md
├── __init__.py
├── analytics.py
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
├── pipeline.py
├── sqlbridge.py
├── sqlfuncs.py
└── template_manager.py

```

---

## Next Steps
1. Add visualization layer (matplotlib or plotly).
2. Extend SQL and Pandas analytics set.
3. Improve error reporting and diagnostics.
4. Add optional test suite.
5. Expand example datasets.

---
