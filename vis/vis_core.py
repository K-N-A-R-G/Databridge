import tkinter as tk

from . import visfuncs
from custom_types import ActionDict, buffer
from devmenu import DevMenu


VIS_ROOT = tk.Tk()
VIS_ROOT.withdraw()

def vis_make_actiondict(vis_root=VIS_ROOT) -> ActionDict:
    """Build ActionDict for DevMenu."""
    actions = {}

    # visualization functions
    for render_mode in visfuncs.__all__:
        func = visfuncs.__all__[render_mode]
        actions[render_mode] = [
            render_mode,
            func,
            (buffer, vis_root),
            {},
        ]

    return actions


def run_vis_action(target_func, buffer, VIS_ROOT):
    """
    Движок визуализации.
    """

    target_func(buffer, VIS_ROOT)



vis_act = DevMenu(vis_make_actiondict(), auto=True)
