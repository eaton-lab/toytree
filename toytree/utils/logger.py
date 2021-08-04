#!/usr/bin/env python

"""
logger for development and user warnings.
"""

import sys
from loguru import logger
import toytree


LOGFORMAT = (
    "<level>{level: <7}</level> | "
    "<b><magenta>{function: <10}:{line}</magenta></b> | "
    "{message}"
)

def colorize():
    """
    colorize the logger if stderr is IPython/Jupyter or a terminal (TTY)
    """
    try:
        import IPython
        tty1 = bool(IPython.get_ipython())
    except ImportError:
        tty1 = False
    tty2 = sys.stderr.isatty()
    if tty1 or tty2:
        return True
    return False


def set_loglevel(loglevel="INFO"):
    """
    Set the loglevel for loguru logger. Using 'enable' here as 
    described in the loguru docs for logging inside of a library.
    This sets the level at which logger calls will be displayed 
    throughout the rest of the code.
    """
    logger.add(sys.stderr, level=loglevel)
    config = {}
    config["handlers"] = [{
        "sink": sys.stderr,
        "format": LOGFORMAT,
        "level": loglevel,
        "colorize": colorize(),
    }]
    logger.configure(**config)
    logger.enable("toytree")
    logger.debug(f"toytree v.{toytree.__version__} logging enabled")
