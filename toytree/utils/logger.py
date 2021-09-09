#!/usr/bin/env python

"""
logger for development and user warnings.
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
    """Set the log level for loguru logger.

    This removes default loguru handler, but leaves any others, 
    and adds a new one that will filter to only print logs from 
    toytree modules, which should use `logger.bind(name='toytree')`.
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
        format="{level.icon} toytree: {message}",
        filter=lambda x: x['extra'].get("name") == "toytree",
    )
    LOGGERS.append(idx)
    logger.enable("toytree")
    logger.bind(name="toytree").debug(
        f"toytree v.{toytree.__version__} logging enabled"
    )
