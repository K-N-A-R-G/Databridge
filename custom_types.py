from typing import Optional, Dict, Tuple, Callable, Any, Union

import inspect


ColumnSpec = Dict[str, Optional[Union[str, bool]]]

TemplateDict = Dict[str, ColumnSpec]


ActionDict = Dict[
                  str,
                  Tuple
                       [
                        str,
                        Callable[..., Any],
                        Tuple[Any, ...],
                        Dict[Any, Any]
                       ]
                 ]


class DemoError(Exception):
    """Custom exception for demo features not yet implemented."""

    def __init__(self, ftr: Optional[str] = None) -> None:
        if ftr is None:
            frame = inspect.currentframe()
            caller = frame.f_back if frame is not None else None  # one step back: raise -> __init__
            name = caller.f_code.co_name if caller is not None else ''
            ftr = name if name != '<module>' else 'this feature'

        message = (
            f"Sorry, '{ftr}' is not implemented in the demo version, "
            "but it can be added in the applied version of the project."
        )
        super().__init__(message)

    def __str__(self) -> str:
        return str(self.args[0])
