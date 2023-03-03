#!/usr/bin/env python

"""Custom exception classes.

We catch most errors that are of the ToytreeError BaseClass and try
to handle them more nicely than other random errors. This includes
adding a logging.error message.
"""

# from loguru import logger
# logger = logger.bind(name="toytree")


class ToytreeError(Exception):
    """BaseClass for many custom exceptions or common user errors."""
    pass


class ToytreeRegexError(Exception):
    """Exceptions for data getting/setting on Nodes."""
    pass


class NodeDataError(Exception):
    """Exceptions for data getting/setting on Nodes."""
    pass


class ToyColorError(ToytreeError):
    """Exceptions for parsing color inputs."""
    pass


class StyleSizeMismatchError(ToytreeError):
    pass


class StyleTypeMismatchError(ToytreeError):
    pass


class StyleColorMappingTupleError(ToytreeError):
    pass


class TreeNodeError(ToytreeError):
    """Exceptions for operating on immutable attributes."""
    pass


class NewickError(ToytreeError):
    pass


class NexusError(ToytreeError):
    pass


if __name__ == "__main__":

    # raise ValueError("HELLO WORLD")
    # raise ToytreeError("HELLO WORLD")
    import toytree
    tree = toytree.rtree.unittree(10)
    tree.draw(node_colors=['red', 'blue'])
