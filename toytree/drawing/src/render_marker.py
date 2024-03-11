#!/usr/bin/env python

"""Use toyplot html functions to add markers

"""

from toyplot.html import (_draw_bar, _draw_triangle, _draw_circle, _draw_rect)


def render_marker(marker_xml, marker) -> None:
    """Call the toyplot render function for the selected marker."""
    if marker.shape == "|":
        _draw_bar(marker_xml, marker.size)
    elif marker.shape == "/":
        _draw_bar(marker_xml, marker.size, angle=-45)
    elif marker.shape == "-":
        _draw_bar(marker_xml, marker.size, angle=90)
    elif marker.shape == "\\":
        _draw_bar(marker_xml, marker.size, angle=45)
    elif marker.shape == "+":
        _draw_bar(marker_xml, marker.size)
        _draw_bar(marker_xml, marker.size, angle=90)
    elif marker.shape == "x":
        _draw_bar(marker_xml, marker.size, angle=-45)
        _draw_bar(marker_xml, marker.size, angle=45)
    elif marker.shape == "*":
        _draw_bar(marker_xml, marker.size)
        _draw_bar(marker_xml, marker.size, angle=-60)
        _draw_bar(marker_xml, marker.size, angle=60)
    elif marker.shape == "^":
        _draw_triangle(marker_xml, marker.size)
    elif marker.shape == ">":
        _draw_triangle(marker_xml, marker.size, angle=-90)
    elif marker.shape == "v":
        _draw_triangle(marker_xml, marker.size, angle=180)
    elif marker.shape == "<":
        _draw_triangle(marker_xml, marker.size, angle=90)
    elif marker.shape == "s":
        _draw_rect(marker_xml, marker.size)
    elif marker.shape == "d":
        _draw_rect(marker_xml, marker.size, angle=45)
    elif marker.shape and marker.shape[0] == "r":
        width, height = marker.shape[1:].split("x")
        _draw_rect(
            marker_xml, marker.size,
            width=float(width), height=float(height))
    elif marker.shape == "o":
        _draw_circle(marker_xml, marker.size)
    elif marker.shape == "oo":
        _draw_circle(marker_xml, marker.size)
        _draw_circle(marker_xml, marker.size / 2)
    elif marker.shape == "o|":
        _draw_circle(marker_xml, marker.size)
        _draw_bar(marker_xml, marker.size)
    elif marker.shape == "o/":
        _draw_circle(marker_xml, marker.size)
        _draw_bar(marker_xml, marker.size, -45)
    elif marker.shape == "o-":
        _draw_circle(marker_xml, marker.size)
        _draw_bar(marker_xml, marker.size, 90)
    elif marker.shape == "o\\":
        _draw_circle(marker_xml, marker.size)
        _draw_bar(marker_xml, marker.size, 45)
    elif marker.shape == "o+":
        _draw_circle(marker_xml, marker.size)
        _draw_bar(marker_xml, marker.size)
        _draw_bar(marker_xml, marker.size, 90)
    elif marker.shape == "ox":
        _draw_circle(marker_xml, marker.size)
        _draw_bar(marker_xml, marker.size, -45)
        _draw_bar(marker_xml, marker.size, 45)
    elif marker.shape == "o*":
        _draw_circle(marker_xml, marker.size)
        _draw_bar(marker_xml, marker.size)
        _draw_bar(marker_xml, marker.size, -60)
        _draw_bar(marker_xml, marker.size, 60)
