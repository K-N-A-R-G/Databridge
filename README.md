# Mini-project “databridge”

## Overview
**Databridge** is a learning/demo project showing the complete workflow:
raw data → ETL/ELT → SQL → visualization → business conclusions.

Main focus:
- Python (data handling, cleaning, ETL).
- SQL (aggregation, joins, window functions).
- Visualization for business analytics.
- Demonstration of development history and modular design.

## Project Goals
1. Demonstrate end-to-end data processing.
2. Practice Python + SQL integration.
3. Show reproducible workflow with modular architecture.
4. Document each stage for clarity and re-use.

## Data Sources (test)
- `sales.csv`: date, product, price, quantity.
- `customers.csv`: customer info, region, segment, age.
- `products.json`: categories, cost, discount.

**Reasons for cleaning/normalization:**
- Missing values.
- Different date formats.
- Duplicate records.
- Inconsistent categories.

## Workflow
1. **Raw sources** → cleaned with `MetaEditor` templates.
2. **ETL/ELT** → normalized DataFrames.
3. **SQL** → queries with aggregation and joins.
4. **Visualization** → charts (bar, line, pie).
5. **Business insights** → criteria and conclusions.

## Current Progress
- Modules implemented:
  - [`getdata.py`](./doc/getdata.md): read, detect format, normalize column/data.
  - [`template_manager.py`](./doc/template_manager.md): interactive template builder.
  - [`etl.py`](./doc/elt.md): helpers for DataFrame creation and merging.
  - [`devtools.py`](./doc/devtools.md): developer utilites for splitting source file, adding "noise", etc.
- Development logs, detailed docs and examples → see [`doc/`](./doc/).

## Demonstration Criteria
- ETL/ELT from multiple sources.
- SQL queries with non-trivial aggregations.
- Charts for business analysis.
- Short report/log (what was cleaned, what conclusions drawn).

## Skills Demonstrated
- Python (pandas, numpy, matplotlib).
- SQL (JOIN, GROUP BY, window functions).
- Data preparation and normalization.
- Visualization and business requirement handling.
- ML critique (basic regression, error analysis).

## Repository Structure
```
databridge/
│
├── getdata.py
├── etl.py
├── metaeditor.py
├── template_manager.py
├── devmenu.py
├── custom_types.py
│
├── Data/            # test data files
├── doc/             # detailed module documentation
│   ├── metaeditor.md
│   ├── etl.md
│   ├── sql_queries.md
│   └── ...
└── README.md        # (this file)
```

## Next Steps
1. Extend ETL/merging.
2. SQL queries + examples.
3. Visualization functions.
4. Documentation split into `doc/`.
5. Add optional tests.

---

📖 **Detailed documentation:** see [`doc/`](./doc/)
