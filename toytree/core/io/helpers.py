#!/usr/bin/env python

"""helper functions for tree parsing odd file formats.
"""

import re

def bpp2newick(bppnewick):
    """Converts bpp outfile format to normal newick."""
    regex1 = re.compile(r" #[-+]?[0-9]*\.?[0-9]*[:]")
    regex2 = re.compile(r" #[-+]?[0-9]*\.?[0-9]*[;]")
    regex3 = re.compile(r": ")
    new = regex1.sub(":", bppnewick)
    new = regex2.sub(";", new)
    new = regex3.sub(":", new)
    return new.strip()
