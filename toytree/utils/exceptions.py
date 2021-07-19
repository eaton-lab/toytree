#!/usr/bin/env python

"""
Custom exception classes
"""


class ToytreeError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class TreeNodeError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class NewickError(Exception):
    def __init__(self, value):
        Exception.__init__(self, value)


class NexusError(Exception):
    def __init__(self, value):
        Exception.__init__(self, value)
