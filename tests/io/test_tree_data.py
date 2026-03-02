#!/usr/bin/env python

"""Example tree string data to test IO.
"""

TESTS = [
    ("only topo", "((),);"),

    ("only tip names", "((a,b),c);"),
    ("only tip dists", "((:2,:1),);"),
    ("only internal dists", "((,):1,);"),
    ("only internal names", "((,)A,);"),
    ("only internal names and dists", "((,)A:3,);"),
    ("only tip anno", "(([&x=a],[&x=b])A:3,);"),

    ("only dists w/ root", "((:2,:1):1,):2;"),
    ("only internal dists w/ root", "((,):1,):2;"),
    ("only internal names w/ root", "((,)A,)R;"),
    ("only internal names and dists w/ root", "((,)A:3,)R:1;"),

    ("all names", "((a,b)A,c)R;"),
    ("all names and dists", "((a:1,b:1)A:1,c:1)R:1;"),
    ("all names and dists and tip anno", "((a[&x=0]:1,b[&x=1]:1)A:1,c[&x=2]:1)R:1;"),
    ("meta containing colon", "((a[&x=0]:1,b[&x=1]:1)A:1,c[&x=2]:1)R:1;"),
    ("meta with no prefix", "((a[x=0]:1,b[x=3,y=1]:1)A:1,c[x=2]:1)R:1;"),
]

import toytree

for key, val in dict(TESTS).items():
    print(key, val)
    tree = toytree.tree(val)
    print(tree.get_node_data())
