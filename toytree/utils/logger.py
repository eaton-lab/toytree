#!/usr/bin/env python

"""
logger for development and user warnings.
"""

import sys
from loguru import logger


def set_loglevel(loglevel="DEBUG"):#, logfile=None):
    """
    Config and start the logger
    """
    config = {
        "handlers": [
            {
                "sink": sys.stderr, 
                "colorize": True,
                "format": (
                    "{time:hh:mm:ss.SSS} <level>{level: <7}</level> <white>|</white> "
                    "<magenta>{file: <11}</magenta> <white>|</white> "
                    "<black>{function: <16}</black> <white>|</white> "
                    "<level>{message}</level>"
                ),
                "level": loglevel,
                },
        ]
    }
    logger.configure(**config)
    logger.enable("toytree")
