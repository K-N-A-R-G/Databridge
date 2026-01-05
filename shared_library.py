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

    func(conn, manual=False)
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
