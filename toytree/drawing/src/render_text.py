#!/usr/bin/env python

"""A replacement for toyplot.html._draw_text() function that allows
for simplifying styles.

This is used in `render_tree` to add tip labels and node labels.
"""

from typing import Dict, Union
from xml.etree import ElementTree as xml
from loguru import logger
import toyplot.style
import toyplot.font
import toyplot.text
from toytree.color.src.concat import concat_style_fix_color

logger = logger.bind(name="toytree")
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
    text: Union[str, toyplot.text.Layout],
    xpos: float = 0,
    ypos: float = 0,
    style: Dict[str , str] = None,
    angle: float = None,
    title: str = None,
    attributes: Dict[str, str] = None,
) -> None:
    """Add xml.SubElements to the DOM for <text> markers.

    A replacement for toyplot.html._draw_text() function that allows
    for simplifying styles.
    """
    # require helvetica font-family
    style = toyplot.style.combine({"font-family": "helvetica"}, style)
    layout = toyplot.text.layout(text, style, toyplot.font.ReportlabLibrary())

    # DEFAULT STYLE OF LAYOUT. These styles can be updated, but all 
    # have already been set on the <g class=toytree-TipLabels> group
    # and so they are discarded after we get the Layout object.
    # {'fill': '#292724',
    #  'font-family': 'helvetica',
    #  'font-size': '12.0px',
    #  'font-weight': 'normal',
    #  'stroke': 'none',
    #  'vertical-align': 'baseline',
    #  'white-space': 'pre'}

    # a layout has left, right, bottom, height, 
    # layout = (
    #     text if isinstance(text, toyplot.text.Layout) else
    #     toyplot.text.layout(text, style, fonts)
    # )

    # Make a group for the text. e.g., {'class': 'TipLabel'}
    attributes = attributes if attributes is not None else {}
    group = xml.SubElement(root, "g", attrib=attributes)

    # apply a transform to the group
    transform = ""
    if xpos or ypos:
        transform += f"translate({xpos:.6g},{ypos:.6g})"  # %r,%r)" % (x, y)
    if angle:
        transform += f"rotate({-angle:.6g})"  # %r)" % (-angle) # pylint: disable=invalid-unary-operand-type
    if transform:
        group.set("transform", transform)

    # optionally apply a title to the text
    if title is not None:
        xml.SubElement(group, "title").text = str(title)

    # only fill and stroke can differ on an individual text element
    sty = {
        i: style.get(i, None) for i in
        ["fill", "fill-opacity", "stroke", "stroke-opacity"]
    }

    # for each child in layout (element with different style) make xml
    hyperlink = []
    for line in layout.children:
        for box in line.children:

            # draw textbox <text ...>
            if isinstance(box, toyplot.text.TextBox):
                xml.SubElement(
                    group, "text",
                    x=str(box.left),
                    y=str(box.baseline),
                    # style=toyplot.style.to_css(box.style),
                    # style=concat_style_to_str2(sty)
                    style=concat_style_fix_color(sty),
                ).text = box.text

            # NOT TESTED
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


if __name__ == "__main__":

    root_ = xml.Element('root')
    group_ = xml.SubElement(root_, "g", attrib={"class": "Labels"})    
    render_text(
        root=group_, text="hello", 
        xpos=0, ypos=0, angle=0, 
        attributes={"class": "Label"},
        style={"font-size": "12px", "fill": "red"},
    )
    print(xml.tostring(group_))
