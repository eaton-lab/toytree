#!/usr/bin/env python

"""
Custom exception classes
"""


class ToytreeError(Exception):
    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args, **kwargs)


class TreeNodeError(ToytreeError):
    def __init__(self, *args, **kwargs):
        ToytreeError.__init__(self, *args, **kwargs)


class NewickError(ToytreeError):
    def __init__(self, value):
        ToytreeError.__init__(self, value)


class NexusError(ToytreeError):
    def __init__(self, value):
        ToytreeError.__init__(self, value)
