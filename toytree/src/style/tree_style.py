#!/usr/bin/env python

"""
Tree Styles with type checking and serialization.
"""

# pylint: disable=no-name-in-module

from enum import Enum
from typing import List, Tuple
from pydantic import BaseModel, Field


class EdgeTypes(Enum):
    normal: 'n'
    dark: 'd'
    umlaut: 'o'
    coalescent: 'c'

class LayoutTypes(Enum):
    right: 'right'
    left: 'left'
    down: 'down'
    up: 'up'
    circle: "circle"

class DefaultEdgeStyle(BaseModel):
    stroke: str=Field("#262626")
    stroke_width: int=Field(2, description="see edge_widths") 
    stroke_linecap: str=Field("round", alias="stroke-linecap") # TODO: enum options.
    stroke_opacity: int=Field(1)

class DefaultNodeStyle(BaseModel):
    fill: str=Field(COLORS1[0])
    stroke: int=Field(None)
    stroke_width: int=Field(1)

class DefaultTreestyle(BaseModel):
    edge_type: EdgeTypes=Field('n')
    edge_colors: List[str]=Field(default_factory=list)
    edge_widths: List[int]=Field(default_factory=list)
    height: int=Field(None)
    width: int=Field(None)
    node_labels: bool=Field(False)
    node_sizes: List[int]=Field(None)
    node_colors: List[str]=Field(None)
    node_markers: List[str]=Field(None)
    node_hover: bool=Field(False)
    use_edge_lengths: bool=Field(False)
    tip_labels: bool=Field(True)
    tip_labels_colors: List[str]=Field(None)
    tip_labels_align: bool=Field(False)
    scale_bar: bool=True
    padding: int=Field(20)
    xbaseline: int=Field(0)
    ybaseline: int=Field(0)
    layout: LayoutTypes=Field('r')
    admixture_edges: List[Tuple]=Field(None)
    shrink: int=Field(0)
    fixed_order: List[str]=Field(None)

    node_style: DefaultNodeStyle=Field(...)
    edge_style: DefaultEdgeStyle=Field(...)
