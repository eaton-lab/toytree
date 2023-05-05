#!/usr/bin/env python

"""SubStyle dict-like objects to store styles nested within TreeStyle.

"""

from __future__ import annotations
from typing import Optional, Union
from enum import Enum
import json
from copy import deepcopy
from toytree.color import ColorType
from toytree.utils import ToytreeError


class EdgeType(str, Enum):
    CLADOGRAM = "c"
    PHYLOGRAM = "p"
    BEZIER = "b"


class LayoutType(str, Enum):
    RIGHT = "right"
    LEFT = "left"
    DOWN = "down"
    UP = "up"
    CIRCLE = "circular"
    UNROOTED = "unrooted"


class SubStyle:
    """A subclass of Style for CSS on markers."""

    def __delattr__(self, key) -> None:
        raise ToytreeError("TreeStyle dict keys cannot be deleted.")

    # def json(self) -> str:
    #     """Return a string with tree style serialized as JSON."""
    #     return json.dumps(self.__dict__, indent=4)

    def __repr__(self):
        """Return a serialized JSON formatted style dict."""
        block = ["{"]
        for key, val in self.__dict__.items():
            block.append(f"    {key}: {val!r},")
        block.append("}")
        return "\n".join(block)

    def copy(self) -> SubStyle:
        """Return a deepcopy."""
        return deepcopy(self)

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        return setattr(self, key, value)


class NodeStyle(SubStyle):
    def __init__(self):
        self.fill: ColorType = "rgba(40.0%,76.1%,64.7%,1.000)"
        self.fill_opacity: float = None
        self.stroke: ColorType = "#262626"
        self.stroke_width: float = 1.5
        self.stroke_opacity: float = None


class NodeLabelStyle(SubStyle):
    def __init__(self):
        self.fill: ColorType = "rgba(16.1%,15.3%,14.1%,1.000)"
        self.fill_opacity: float = 1.0
        self.font_size: Union[int, str] = 9
        self.font_weight: int = 300
        self.font_family: str = "Helvetica"
        self._toyplot_anchor_shift: Union[str, int] = 0
        # self.anchor_shift: Union[str, int] = 0 # TODO: this would be nice...
        self.baseline_shift: Union[str, int] = 0
        self.text_anchor: str = "middle"


class EdgeStyle(SubStyle):
    def __init__(self):
        self.stroke: ColorType = "rgba(16.1%,15.3%,14.1%,1.000)"
        self.stroke_width: float = 2.0
        self.stroke_opacity: Optional[float] = None
        self.stroke_linecap: str = "round"
        self.stroke_dasharray: Optional[str] = None


class EdgeAlignStyle(SubStyle):
    def __init__(self):
        self.stroke: ColorType = "rgba(66.3%,66.3%,66.3%,1.000)"
        self.stroke_width: int = 2
        self.stroke_opacity: Optional[float] = 0.75
        self.stroke_linecap: str = "round"
        self.stroke_dasharray: str = "2,4"


class TipLabelStyle(SubStyle):
    def __init__(self):
        self.fill: ColorType = "rgba(16.1%,15.3%,14.1%,1.000)"
        self.fill_opacity: Optional[float] = None
        self.font_size: Union[str, float] = 12
        self._toyplot_anchor_shift: Union[str, float] = 15
        self.baseline_shift: Union[str, int] = 0
        self.text_anchor: str = "start"
        # TODO: remove these but allow them to be modified if needed?
        self.font_weight: int = 300
        self.font_family: str = "Helvetica"


if __name__ == "__main__":

    ns = NodeStyle()
    ns.fill = (0.3, 0.3, 0.3, 0.5)
    ns.stroke = "blue"
    ns.fill_opacity = 1.5
    print(ns)
