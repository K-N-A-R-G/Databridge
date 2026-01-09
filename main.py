import threading
from custom_types import DBConnection, ActionDict
from devmenu import DevMenu
from pipeline import (
    build_df_interactive, manage_templates, get_all_data_files,
    choose_active_table, run_dbtools
)
from pdbridge import run_pd_engine
from sqlbridge import run_sql_engine
from devtools import menu_actions as devtools_actions
from vis.vis_core import VIS_ROOT

def run_main():
    conn = DBConnection.get()

    actions: ActionDict = {
        "1": ("Build DataFrame using template", build_df_interactive, (), {}),
        "2": ("Select/edit metadata template", manage_templates, (), {}),
        "3": ("List files in ./Data/", lambda: print("\n".join(f.name for f in get_all_data_files())), (), {}),
        "4": ("SQL analytics", run_sql_engine, (), {}),
        "5": ("Pandas analytics", run_pd_engine, (), {}),
        "6": ("Developer tools", lambda: DevMenu(devtools_actions).run(), (), {}), # Обертка в lambda для чистоты
        "7": ("Select active table", choose_active_table, (), {}),
        "8": ("Database maintenance\n", run_dbtools, (), {}),
    }

    menu = DevMenu(actions, title="Databridge Central Command", dev_mode=True)
    menu.run()

    VIS_ROOT.after(0, VIS_ROOT.quit)

if __name__ == "__main__":
    threading.Thread(target=run_main, daemon=True).start()

    if VIS_ROOT:
        VIS_ROOT.withdraw()
        VIS_ROOT.mainloop()
