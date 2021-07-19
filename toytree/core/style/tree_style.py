#!/usr/bin/env python

"""
NOT YET IMPLEMENTED

Tree Styles with type checking and serialization.

1. Attribute of ToyTree (downside is it slows initialization...)


Usage
-----

> toytree.tree(...)                   # DefaultTreeStyle() init
> tree.draw(**kwargs)                 # dict or user args
> style = DefaultTreeStyle(**kwargs)  # DefaultTreeStyle(**dict, **tree.style)

# style is then expanded in tree-context to List len args


"""

# pylint: disable=no-name-in-module, no-self-argument, no-self-use

from enum import Enum
from typing import List, Tuple, Optional, Union
import toyplot
import numpy as np
from pydantic import BaseModel, Field, validator
from pydantic.color import Color


COLORS1 = list(
    map(toyplot.color.to_css, toyplot.color.brewer.palette("Set2")))
COLORS2 = list(
    map(toyplot.color.to_css, toyplot.color.brewer.palette("Dark2")))
BLACK = toyplot.color.black



class TreeStyles(str, Enum):
    normal = 'n'
    dark = 'd'
    umlaut = 'o'
    coalescent = 'c'

class EdgeTypes(str, Enum):
    cladogram = 'c'
    phylogram = 'p'
    bezier = 'b'

class LayoutTypes(str, Enum):
    right = 'right'
    left = 'left'
    down = 'down'
    up = 'up'
    circle = 'circular'
    unrooted = 'unrooted'


class Array:
    """
    Arrays are always converted to lists... still figuring out how to
    best allow np.arrays into pydantic model...
    """

class DefaultEdgeStyle(BaseModel):
    stroke: Optional[Color] = Field("#262626")
    stroke_width: float = Field(2, min=0, description="see edge_widths") 
    stroke_linecap: str = Field("round", alias="stroke-linecap")
    stroke_opacity: float = Field(1, min=0.0, max=1.0)

class DefaultNodeStyle(BaseModel):
    fill: Optional[Color] = Field(COLORS1[0])
    stroke: Optional[Color] = Field(None)
    stroke_width: float = Field(1, min=0)

class DefaultTreeStyle(BaseModel):
    height: Optional[int] = None
    width: Optional[int] = None
    edge_type: EdgeTypes = 'p'
    layout: LayoutTypes = 'r'

    node_labels: Union[bool,List[str]] = Field(..., help="...")
    node_colors: List[Tuple[float,float,float,float]] = Field(..., help="")

    edge_colors: Optional[List[Color]] = None
    edge_widths: Optional[List[float]] = None
    node_sizes: Optional[Union[int, List[int]]] = None
    node_colors: Optional[Union[str,Color,List[str],List[Color]]] = COLORS1[0]
    node_markers: List[str]=Field(None)
    node_hover: bool=Field(False)
    use_edge_lengths: bool=Field(False)
    tip_labels: bool=Field(True)
    tip_labels_colors: Optional[List[Color]] = None
    tip_labels_align: bool = False
    scale_bar: bool = False
    padding: int = Field(20, help="applied to Cartesian axes")
    xbaseline: int = 0
    ybaseline: int = 0
    admixture_edges: List[Tuple[int, int]] = Field(None, help="(src, dest, prop, ...)")
    shrink: int = 0
    fixed_order: Optional[List[str]] = None

    node_style: DefaultNodeStyle=Field(default_factory=DefaultNodeStyle)
    edge_style: DefaultEdgeStyle=Field(default_factory=DefaultEdgeStyle)

    class Config:
        validate_assignment = True

    @validator('node_colors')
    def check_node_colors(cls, value) -> List[str]:
        """
        Converts input type to a tuple of rgba floats
          str       | 'teal'                    | [(0.4, 0.7, 0.5, 1.0), ...
          ndarray   | (0.4, 0.7, 0.6, 1.0)      | [(0.4, 0.7, 0.5, 1.0), ...
          List[str] | ['teal', 'orange', ...]   | [(0.4, 0.7, 0.5, 1.0), ...
          List[ndarray] | ['teal', 'orange', ...]   | [(0.4, 0.7, 0.5, 1.0), ...          
        """
        # it may be a color 
        if isinstance(value, np.ndarray):  # it is a color array
            value = list(value)
        if isinstance(value, np.ndarray):  # it is an array of color str
            value = list(value)
        if isinstance(value, np.ndarray):  # it is an array of color arrays
            value = list(value)
        if isinstance(value, np.ndarray):  # it is a str
            value = list(value)
        if isinstance(value, np.ndarray):  # it is an Iterable of str
            value = list(value)
        else:
            raise TypeError(f"node_labels type is invalid: {value}")
        return value

    @validator('node_labels')
    def check_node_labels(cls, value, values) -> List[str]:
        """
        Converts input type to a list of strings. 
          bool -> [' ', ' ', ' ', ...] or ['', '', '', ...]
          List[str] -> ['a', 'b', 'c']
        """
        if isinstance(value, list):
            return value
        if isinstance(value, np.ndarray):
            return list(value)
        if value is True:
            return [" "] * values['_nnodes']
        if value is False:
            return [""] * values['_nnodes']
        raise TypeError(f"node_labels type is invalid: {value}")


    # @classmethod
    # def validate(cls, val):
    #     if isinstance(val, np.ndarray):
    #         try:
    #             val = map(toyplot.color.to_css, val)
    #         except Exception:
    #             print("EXCEPTION", val)
    #         return list(val)
    #     return val




if __name__ == "__main__":

    # print(DefaultEdgeStyle(stroke='red').json(indent=4))
    # print(DefaultNodeStyle(stroke=None).json(indent=4))
    import toytree
    TREE = toytree.rtree.unittree(10)
    print(COLORS1)

    tstyle = DefaultTreeStyle(
        ntips=TREE.ntips,
        nnodes=TREE.nnodes,
        node_labels=False,#TREE.get_node_labels("idx"),
        #node_sizes=list(np.arange(10)),
        #node_colors=[i for i in toyplot.color.Palette()],
    )

    print(tstyle.json(indent=4))
