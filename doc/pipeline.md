# Pipeline Module (`pipeline.py`)

The `pipeline.py` module is the **Batch Processing Engine** of Databridge. It orchestrates the transformation of heterogeneous raw data into a structured, analysis-ready SQLite database.

## Role in Architecture
Previously a command center, the current version acts as a **Service Layer**. It provides high-level ETL functions that are called by the `main.py` entry point but can also be executed in standalone mode for testing.

---

## Core Features

- **Automated Discovery**: Scans `./Data/` for raw files and `./Data/templates/` for metadata blueprints.
- **Unified Ingestion**: Merges multiple sources (CSV/JSON) into a single, schema-aligned DataFrame.
- **State Persistence**:
    - Automatically updates the **SQLite cache** (`bridge.db`).
    - Ensures the database remains the "Single Source of Truth" for analytics.
- **Efficient Deduplication**:
    - The engine performs a **Single-Pass De-duplication**.
    - Instead of cleaning each file individually (which is CPU-intensive), it aggregates all sources first and performs a final `drop_duplicates` operation before saving to SQLite.
- **Optional Export**: Provides routines to save normalized results back to disk (`CSV`, `XLSX`, `JSON`) for external use.

---

## ETL Logic Workflow

1. **Mapping Phase**: Loads a JSON template (created via `template_manager.py`).
2. **Batching Phase**: Iteratively processes selected files. For each file:
    - Normalizes headers and data types.
    - Aligns columns with the master template schema.
3. **Persistance Phase**:
    - Replaces or appends data in the shared SQLite database.
    - Synchronizes the "Active Table" state via `config.py`.

---

## Technical Internals

- **Engine**: Uses `etl.py` and `getdata.py` for low-level data manipulation.
- **Database**: Interacts with the `DBConnection` singleton to manage table storage.
- **Scalability**: Designed to handle multiple files in a single pass through vectorized Pandas operations.

## Data Flow Diagram

```mermaid
graph TD
    A["Raw Files (CSV/JSON)"] --> B["Header Normalization"]
    B --> C["Template-Based Extraction"]
    C --> D["Unified DataFrame"]
    D --> E[("SQLite Storage (bridge.db)")]
    D -.-> F["External Export (CSV/XLSX)"]

    style E fill:#f9f,stroke:#333,stroke-width:2px
