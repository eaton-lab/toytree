#!/usr/bin/env python

"""The base TreeStyle object from which other TreeStyles are modified
child classes.

This base class defines the attrs and a set of core functions for 
serializing and expanding user args into a set of full and valid
style arguments.

Proposed Internal usage
-----------------------
The validate argument returns the style objects used in draw with 
values expanded for all nodes/edges in the tree. 
>>> tstyle = tree.style.validate(**kwargs)

This allows for users to enter lazy arguments for some args which will
be stored in several allowable formats, and only converted into the 
required format when .validate() is called at the time of drawing:
>>> tree.draw(node_colors=(1, 0.5, 0.5, 0.5))
>>> tree.draw(node_colors=("idx", "BlueRed")).
>>> tree.draw(node_sizes=tree.get_node_data("idx"))

Set/Get attributes
------------------
>>> tree.style.edge_widths = 'hello'  # raise TypeError 
>>> tree.style.node_labels_style = 3  # raise TypeError
>>> tree.style.node_labels_style = {'font-size': 9}  # does not erase other styles.
>>> ...
"""

from typing import Union, Sequence, TypeVar, Tuple, Dict, Any
import json
from copy import deepcopy
from loguru import logger
import numpy as np
from toytree.color import ToyColor
from toytree.utils import ToytreeError
from toytree.style.src.sub_styles import (
    NodeStyle, NodeLabelStyle, EdgeStyle, EdgeAlignStyle, TipLabelsStyle
)

logger = logger.bind(name="toytree")
Color = TypeVar("Color")
ToyTree = TypeVar("ToyTree")
SUBSTYLES = [
    "node_style", "node_labels_style", "tip_labels_style",
    "edge_style", "edge_align_style",
]

class TreeStyle:
    def __init__(self):
        self.tree_style: str = None
        self.height: float = None
        self.width: float = None
        self.layout: str = "r"

        self.edge_type: str = "p"
        self.edge_colors: Union[Color, Sequence[Color]] = None
        self.edge_widths: Union[float, Sequence[float]] = None
        self.edge_style: EdgeStyle = EdgeStyle()
        self.edge_align_style: EdgeAlignStyle = EdgeAlignStyle()

        self.node_mask: Union[bool, Sequence[bool], None] = None  # None = auto
        self.node_colors: Union[Color, Sequence[Color], None] = None  # override by fill
        self.node_sizes: Union[float, Sequence[float]] = 0.0
        self.node_markers: Union[str, Sequence[str]] = "o"
        self.node_hover: Union[bool, str, Sequence[str]] = None  # None = auto
        self.node_style: NodeStyle = NodeStyle()

        self.node_labels: Union[bool, str, Sequence[str]] = False
        self.node_labels_style: NodeLabelStyle = NodeLabelStyle()

        self.tip_labels: Union[bool, Sequence[str]] = True
        self.tip_labels_colors: Union[str, Sequence[str], None] = None
        self.tip_labels_align: bool = None
        self.tip_labels_style: TipLabelsStyle = TipLabelsStyle()
        self.tip_labels_angles: Union[float, Sequence[float], None] = None

        # self.show_root_edge: bool = None
        self.use_edge_lengths: bool = True
        self.scale_bar: Union[bool, float] = False
        self.padding: float = 15.0
        self.xbaseline: float = 0.0
        self.ybaseline: float = 0.0
        self.admixture_edges: Sequence[Tuple] = None
        self.shrink: float = 0.0


    def dict(self, serialize: bool = True) -> Dict[str, Any]:
        """Return current style arguments as a SERIALIZED dict."""
        sdict = deepcopy(self.__dict__)
        sdict.pop("tree", None)

        # convert substyles into dicts also
        for skey in SUBSTYLES:
            sdict[skey] = sdict[skey].__dict__

        # serialize for printing, but not during drawing prep.
        if serialize:
            for key, value in sdict.items():
                if key in SUBSTYLES:
                    for skey, sval in value.items():
                        sdict[key][skey] = serialize_style(skey, sval)
                else:
                    # logger.warning([key, value])
                    sdict[key] = serialize_style(key, value)

            if sdict['admixture_edges'] is not None:
                for idx, atup in enumerate(sdict['admixture_edges']):
                    _, _, *args = atup
                    if len(args) > 1:
                        sty = args[1]
                        for key, val in sty.items():
                            sdict['admixture_edges'][idx][3][key] = serialize_style(key, val)

        # when dumping after validation change - _ keys
        else:
            for key in SUBSTYLES:
                for skey in list(sdict[key]):
                    value = sdict[key].pop(skey)
                    newkey = skey.replace("_", "-")
                    sdict[key][newkey] = value
        return sdict


    def json(self) -> str:
        """Return a string with tree style serialized as JSON."""
        return json.dumps(self.dict(serialize=True), indent=4)

    def __repr__(self):
        """Return a serialized JSON formatted style dict."""
        return self.json()

    def copy(self) -> "TreeStyle":
        """Return a deepcopy."""
        return deepcopy(self)


def serialize_style(key: str, value: Any) -> Any:
    """Used to make TreeStyle format nicely into JSON."""
    if value is None:
        return value

    # allow numerics
    if isinstance(value, (float, int, np.integer)):
        return value

    # convert colors to serialized form for ...
    if ("color" in key) or (key in ['fill', 'stroke']):
        try:
            col = ToyColor.color_expander(value)
        # exception to allow (feat, colormap) tuple shortcut
        except ToytreeError as inst:
            try:
                if not (isinstance(value, tuple) and len(value) == 2):
                    raise inst
                # NOTE: THIS IS ONLY SERIALIZED TO THE OBJECT REPR
                return (value[0], str(value[1])) # return (feat, colormap)
            except TypeError:
                raise inst

        if isinstance(col, ToyColor):
            value = col.css
        else:
            value = [i.css for i in col[:3]] + ['...']
        return value

    # allow strings now that colors have been set
    if isinstance(value, str):
        return value

    # try to convert anything else (collections) into a list.
    try:
        value = value.tolist()
    except Exception:
        value = list(value)
    return value[:3] + (['...'] if len(value) > 3 else [])


if __name__ == "__main__":

    import toytree
    ts = TreeStyle()
    ts.node_colors = ["red", "blue"]
    ts.tip_labels_colors = toytree.color.COLORS1[0]
    ts.node_markers = ["s", "o"]
    ts.edge_widths = np.arange(10)
    ts.admixture_edges = [('a', 'b', (0.5, 0.1), {'stroke': toytree.color.COLORS1[0]})]
    print(ts)
