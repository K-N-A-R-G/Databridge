def execute_sql_in_process(
                        module_name,
                        func_name,
                        DB_PATH,
                        active_table,
                        render_mode
                        ):
    import importlib
    import sqlite3
    import tkinter as tk
    import threading

    from custom_types import buffer
    from devmenu import DevMenu
    from vis.vis_core import vis_make_actiondict

    lib = importlib.import_module(module_name)
    vis = importlib.import_module('vis.visfuncs')
    func = lib.__all__[func_name]
    conn = sqlite3.connect(DB_PATH)
    # print(conn)
    # LOCAL_VIS_ROOT = tk.Tk()
    # LOCAL_VIS_ROOT.withdraw()
    # local_vis_act = DevMenu(vis_make_actiondict(None), auto=True)
    vis_maker = vis.__all__[render_mode]

    print('\nenv is ready')
    func(conn, manual=False)
    # print(buffer)
    vis_maker(buffer)
    # print(local_vis_act.actions)
    # local_vis_act.do(render_mode)


def execute_pd_in_process(
                        module_name,
                        func_name,
                        DB_PATH,
                        active_table,
                        render_mode
                        ):
    import importlib
    import sqlite3
    import pandas as pd  # Загружаем "тяжеловеса" только здесь
    import tkinter as tk

    from custom_types import buffer

    # 1. Динамический импорт модулей
    lib = importlib.import_module(module_name)
    vis = importlib.import_module('vis.visfuncs')

    # Извлекаем саму функцию и рисовальщик
    func = lib.__all__[func_name]
    vis_maker = vis.__all__[render_mode]

    # 2. Подготовка данных (Pandas заходит в чат)
    print(f'\n[ENV READY] Loading table "{active_table}" into DataFrame...')
    conn = sqlite3.connect(DB_PATH)
    try:
        # Читаем всю таблицу. В отдельном процессе это не вешает основной терминал.
        df = pd.read_sql_query(f"SELECT * FROM {active_table}", conn)
    finally:
        conn.close()

    # 3. Выполнение аналитики
    # Твоя функция (например, customer_retention) наполнит buffer
    func(df, manual=False)

    # 4. Запуск визуализации
    # Откроет окно со своим mainloop, полностью изолированное от терминала
    vis_maker(buffer)
