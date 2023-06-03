#!/usr/bin/env python

import re


def replace_whitespace(nwk: str, sub: str = "") -> str:
    """Replace whitespace with sub unless preceded by a semicolon.

    This gets rid of whitespace within newick strings while retaining
    newlines separating newick strings for parsing multitrees.
    """
    pattern = r'(?<!;)\s'
    modified_nwk = re.sub(pattern, sub, nwk)
    return modified_nwk.strip()
