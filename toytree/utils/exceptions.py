#!/usr/bin/env python

"""
Custom exception classes
"""


class ToytreeError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class TreeError(Exception):
    "A problem occurred during a TreeNode operation"
    def __init__(self, value=''):
        self.value = value

    def __str__(self):
        return repr(self.value)


class NewickError(Exception):
    """Exception class designed for NewickIO errors."""
    def __init__(self, value):
        Exception.__init__(self, value)


class NexusError(Exception):
    """Exception class designed for NewickIO errors."""
    def __init__(self, value):
        Exception.__init__(self, value)


