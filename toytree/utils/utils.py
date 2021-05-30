#!/usr/bin/env python

"""
Helper objects of general use, or a landing space for experimental
code until it finds a more permanent home.
"""

import re
from exceptions import ToytreeError


def bpp2newick(bppnewick):
    """
    converts bpp newick format to normal newick. ugh.
    """
    regex1 = re.compile(r" #[-+]?[0-9]*\.?[0-9]*[:]")
    regex2 = re.compile(r" #[-+]?[0-9]*\.?[0-9]*[;]")
    regex3 = re.compile(r": ")
    new = regex1.sub(":", bppnewick)
    new = regex2.sub(";", new)
    new = regex3.sub(":", new)
    return new.strip()

