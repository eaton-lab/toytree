#!/usr/bin/env python

"""
A replacement for toyplot.html._draw_text() function that allows
for simplifying styles.
"""

from typing import Dict
from xml.etree import ElementTree as xml
import toyplot.style
import toyplot.font
import toyplot.text


POP_STYLES = [
    "font-size",
    "font-weight",
    "font-family",
    "vertical-align",
    "white-space",
    "stroke",
]


def render_text(
    root: xml.SubElement,
    text: str,
    x: float=0,
    y: float=0,
    style: Dict[str,str]=None,
    angle: float=None,
    title: str=None,
    attributes: Dict[str,str]=None,
    ):
    """
    A replacement for toyplot.html._draw_text() function that allows
    for simplifying styles.
    """
    # require helvetica font-family
    style = toyplot.style.combine({"font-family": "helvetica"}, style)
    attributes = attributes if attributes is not None else {}
    fonts = toyplot.font.ReportlabLibrary()
    layout = (
        text if isinstance(text, toyplot.text.Layout) else
        toyplot.text.layout(text, style, fonts)
    )

    # Make a group for the text. e.g., {'class': 'TipLabel'}
    group = xml.SubElement(root, "g", attrib=attributes)

    # apply a transform to the group
    transform = ""
    if x or y:
        transform += "translate(%r,%r)" % (x, y)
    if angle:
        transform += "rotate(%r)" % (-angle) # pylint: disable=invalid-unary-operand-type
    if transform:
        group.set("transform", transform)

    # apply a title to the tip label
    if title is not None:
        xml.SubElement(group, "title").text = str(title)

    hyperlink = []
    for line in layout.children:
        for box in line.children:

            # remove redundant styles
            for sty in POP_STYLES:
                if sty in box.style:
                    box.style.pop(sty)

            # remove fill if set on parent xml (not in style)
            for tsty in ['fill', 'fill-opacity']:
                if tsty not in style:
                    if tsty in box.style:
                        box.style.pop(tsty)

            # draw 
            if isinstance(box, toyplot.text.TextBox):
                xml.SubElement(
                    group, "text",
                    x=str(box.left), 
                    y=str(box.baseline),
                    style=toyplot.style.to_css(box.style),
                    ).text = box.text

            elif isinstance(box, toyplot.text.PushHyperlink):
                hyperlink.append(group)
                group = xml.SubElement(
                    group,
                    "a",
                    style=toyplot.style.to_css(box.style),
                )
                group.set("xlink:href", box.href)
                if box.target is not None:
                    group.set("target", box.target)

            elif isinstance(box, toyplot.text.PopHyperlink):
                group = hyperlink.pop()
