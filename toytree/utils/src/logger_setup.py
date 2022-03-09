#!/usr/bin/env python

"""Logger for development and user warnings.

All toytree modules that use logging use a 'bound' logger that will
be filtered here to only show for toytree and not for other Python
packages.
"""

import sys
from loguru import logger
import toytree


def colorize():
    """colorize the logger if stderr is IPython/Jupyter or a terminal (TTY)"""
    try:
        import IPython        
        tty1 = bool(IPython.get_ipython())
    except ImportError:
        tty1 = False
    tty2 = sys.stderr.isatty()
    if tty1 or tty2:
        return True
    return False


LOGGERS = [0]
def set_log_level(log_level="INFO"):
    """Set the log level for loguru logger bound to toytree.

    This removes default loguru handler, but leaves any others in place, 
    and adds a new one that will filter to only print logs from 
    toytree modules, which should use `logger.bind(name='toytree')`.

    Examples
    --------
    >>> # suppress toytree logs below INFO level
    >>> toytree.set_log_level("INFO") 
    >>>
    >>> # write a log message from the toytree logger
    >>> from loguru import logger
    >>> logger.bind(name="toytree").info("logged message from toytree")
    """
    for idx in LOGGERS:
        try:
            logger.remove(idx)
        except ValueError:
            pass
    idx = logger.add(
        sink=sys.stderr,
        level=log_level,
        colorize=colorize(),
        format="{level.icon} {name}: {message}",
        filter=lambda x: x['extra'].get("name") == "toytree",
    )
    LOGGERS.append(idx)
    logger.enable("toytree")
    logger.bind(name="toytree").debug(
        f"toytree v.{toytree.__version__} logging enabled"
    )
