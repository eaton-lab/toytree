#!/usr/bin/env python

"""SubStyle dict-like objects to store styles nested within TreeStyle.

"""

from typing import Optional, Union
from enum import Enum
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

    # TOO SLOW TO CHECK EVERY STYLE AS IT IS SET. CHECKED ONLY ON VALIDATION.
    # def __setattr__(self, key: str, value) -> None:
    #     """ColorTypes are always converted to XXX"""
    #     if key in ["fill", "stroke"]:
    #         self.__dict__[key] = ColorType(value).css
    #     else:
    #         self.__dict__[key] = value


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


class TipLabelsStyle(SubStyle):
    def __init__(self):
        self.fill: ColorType = "rgba(16.1%,15.3%,14.1%,1.000)"
        self.fill_opacity: Optional[float] = None
        self.font_size: Union[str, float] = 11
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
    print(ns.__dict__)
