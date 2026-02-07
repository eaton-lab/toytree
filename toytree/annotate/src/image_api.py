#!/usr/bin/env python

"""Helpers for placing and resizing images on a Toyplot canvas."""

from __future__ import annotations

from typing import Tuple

import numpy as np
import toyplot


def generate_example_image(width: int = 96, height: int = 96) -> np.ndarray:
    """Create a small RGB gradient image as a demo placeholder.

    Parameters
    ----------
    width : int
        Image width in pixels.
    height : int
        Image height in pixels.

    Returns
    -------
    numpy.ndarray
        A (height, width, 3) float array in the range [0, 1].
    """
    x = np.linspace(0.0, 1.0, width)
    y = np.linspace(0.0, 1.0, height)
    xv, yv = np.meshgrid(x, y)
    red = xv
    green = yv
    blue = 0.3 * np.ones_like(xv)
    return np.dstack((red, green, blue))


def place_image_on_canvas(
    canvas: toyplot.Canvas,
    image: np.ndarray,
    *,
    x: float = 50,
    y: float = 50,
    width: float = 120,
    height: float = 120,
) -> toyplot.mark.Image:
    """Place an image at a position and size on a Toyplot canvas.

    Parameters
    ----------
    canvas : toyplot.Canvas
        Canvas to receive the image.
    image : numpy.ndarray
        RGB or RGBA image data.
    x, y : float
        Upper-left corner position in canvas coordinates (pixels by default).
    width, height : float
        Image size in canvas units (pixels by default).

    Returns
    -------
    toyplot.mark.Image
        The image mark added to the canvas.
    """
    return canvas.image(data=image, rect=(x, y, width, height))


def minimal_working_example(
    *,
    canvas_size: Tuple[int, int] = (400, 300),
    image_size: Tuple[int, int] = (140, 140),
    image_position: Tuple[int, int] = (40, 60),
) -> Tuple[toyplot.Canvas, toyplot.mark.Image]:
    """Build a minimal canvas with a movable/resizable image.

    Adjust ``image_size`` and ``image_position`` to resize and reposition the
    image on the canvas.
    """
    canvas = toyplot.Canvas(width=canvas_size[0], height=canvas_size[1])
    image = generate_example_image(width=image_size[0], height=image_size[1])
    mark = place_image_on_canvas(
        canvas,
        image,
        x=image_position[0],
        y=image_position[1],
        width=image_size[0],
        height=image_size[1],
    )
    return canvas, mark


# """An API to access phylopic images and position as toyplot image Markers.


# >>> c, a, m = toytree.draw()
# >>>


# canvas, axes, mark = tree.draw(scale_bar=True, width=400, height=500);
# mark2 = tree.annotate.add_tip_markers(axes, marker='o', size=5, xshift=8);
# axes.x.show = True
# axes.y.show = True

# # make it render so we can get pixel coordinates
# toytree.save(canvas, "/tmp/test.html")
# x = axes.project('x', mark.ntable[10, 0])
# y = axes.project('y', mark.ntable[10, 1])

# # add an image to pixel coordinates
# image = Image.open("/home/deren/Pictures/Pedicularis/oliv.jpg")
# width=200
# height=100
# canvas.image(image, bounds=(x, x+width, y, y+height))
# toytree.save(canvas, "/home/deren/tree.html")
# canvas

# """

# """An API to access phylopic images and position as toyplot image Markers.
# """
