#!/usr/bin/env python

__version__ = "2.0.1"
__author__ = "Deren Eaton"

from .Toytree import ToyTree as tree
from .Toytree import RawTree as _rawtree
from .Randomtree import RandomTree as rtree
from .Multitree import MultiTree as mtree
from .Container import Container as container
from .PCM import PCM as pcm

# make a color palette easily accessible and an iter cycling version
from .TreeStyle import COLORS1 as colors
from .TreeStyle import COLORS2 as darkcolors
import itertools as _itertools
icolors1 = _itertools.cycle(colors)
icolors2 = _itertools.cycle(darkcolors)
