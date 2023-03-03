#!/usr/bin/env python

"""Unit tests for toytree

Tests for parsing newick, nexus, and other tree inputs correctly,
and at sufficient speeds.
"""

# pylint: disable=missing-function-docstring

import pytest
import toytree

# @pytest.fixture


NEWICK_1 = "((,),(,,));"
NEWICK_2 = "((a:2,b:2)A:2,c:2)B:2;"
NEWICK_3 = "((a[&NHX:label=3],b[&NHX:label=4]),c[&NHX:label=5]);"
NEWICK_4 = "((a:3[&NHX:name=3],b:4[&NHX:name=4]),c:5[&NHX:name=5]);"
NEWICKS = [NEWICK_1, NEWICK_2]

def test_parse_newick():
    tree = toytree.tree(NEWICK_2)
    assert tree.nnodes == 5
    assert tree.ntips == 3
    assert all(tree.get_node_data("dist") == 2.)
    assert list(tree.get_node_data("name")[-2:]) == ['A', 'B']

def test_no_names_newick():
    tree = toytree.tree(NEWICK_1)
    assert tree.nnodes == 8
    assert tree.ntips == 5

def test_parse_newick_nhx():
    tree = toytree.tree(NEWICK_3)
    assert tree.nnodes == 5
    assert tree.ntips == 3

def test_parse_newick_2():
    tree = toytree.io.parse_newick_string(
        NEWICK_3, 
        feature_prefix="&NHX", 
        feature_delim=",",
    )
    assert tree.nnodes == 5
    assert tree.ntips == 3

def test_parse_url():
    tree = toytree.tree("https://eaton-lab.org/data/Cyathophora.tre")
    assert tree.ntips == 13

def test_parse_nexus():
    pass
