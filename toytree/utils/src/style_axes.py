#!/usr/bin/env python

"""Apply styling to toyplot Cartesian axes objects.

Set margin to 60.
"""

from typing import Optional, Sequence, Tuple, Union, Mapping, Any

import toyplot
import numpy as np
from toyplot.canvas import Canvas
from toyplot.coordinates import Cartesian


def set_axes_ticks_external(axes: toyplot.coordinates.Cartesian) -> toyplot.coordinates.Cartesian:
    """Add custom generic style to plot axes.

    Sets tick marks to extend 5px outside of spine, tick mark labels
    to 10px outside of spine, and text labels to 30px outside of spine.
    To make sure that labels can still fit, the margin is also increased
    by 10px, so that it is 60px on top, bottom, left and right.
    """
    axes.x.ticks.show = True
    axes.x.domain.show = False
    axes.y.domain.show = False
    axes.y.ticks.show = True
    axes.x.ticks.near = 5
    axes.x.ticks.far = 0
    axes.y.ticks.near = 5
    axes.y.ticks.far = 0
    axes.x.ticks.labels.offset = 10
    axes.y.ticks.labels.offset = 10
    axes.y.label.offset = 30
    axes.x.label.offset = 30
    axes.label.offset = 20

    # this is equivalent to increasing margin from default=50 to 60.
    axes._xmin_range += 10
    axes._xmax_range -= 10
    axes._ymin_range += 10
    axes._ymax_range -= 10
    return axes


def set_axes_box_outline(axes: toyplot.coordinates.Cartesian) -> toyplot.coordinates.Cartesian:
    """Adds a box outline to plots.

    This is achieved by creating new axes objects that ignore the data
    domain and extend their spines all the way to the extent of the
    axes padding.

    Note
    ----
    To easily set the stroke-width of ALL spines, ticks, etc you can
    use the canvas.style['stroke-width'] setting. Also, note that if
    the axes.padding is changed AFTER this function is called then the
    axes can be separated from the box outline (i.e., this func uses
    the curretn padding value to align the two).
    """
    # opposite of original y
    newy = axes.share("x", xlabel=axes.x.label.text)
    # newy.y.spine.style['stroke'] = stroke
    newy.y.ticks.show = False
    newy.y.ticks.labels.show = False
    newy._ymin_range -= axes.padding
    newy._ymax_range += axes.padding

    # on top of original y, inherits the ymin,max range from newy
    newy = newy.share("x", xlabel=axes.x.label.text)
    # newy.y.spine.style['stroke'] = stroke
    newy.y.spine.position = "low"
    newy.y.ticks.show = False
    newy.y.ticks.labels.show = False

    # opposite of original x
    newx = axes.share("y", ylabel=axes.y.label.text)
    # newx.x.spine.style['stroke'] = stroke
    newx.x.ticks.show = False
    newx.x.ticks.labels.show = False
    newx._xmin_range -= axes.padding
    newx._xmax_range += axes.padding

    # on top of original x
    newx = newx.share("y", ylabel=axes.y.label.text)
    # newx.x.spine.style['stroke'] = stroke
    newx.x.spine.position = "low"
    newx.x.ticks.show = False
    newx.x.ticks.labels.show = False
    return axes


def debug_toyplot_canvas(
    canvas: Canvas,
    axes: Union[Cartesian, Sequence[Cartesian]],
    marks: Optional[Union[Any, Sequence[Any], Mapping[Cartesian, Any]]] = None,
    canvas_style: Optional[dict] = None,
    axes_style: Optional[dict] = None,
    padding_style: Optional[dict] = None,
    data_style: Optional[dict] = None,
) -> Tuple[Canvas, Union[Cartesian, Sequence[Cartesian]]]:
    """Visualize toyplot canvas / axes / padding regions for debugging.

    Parameters
    ----------
    canvas
        Existing toyplot canvas.
    axes
        A single Cartesian axes or a sequence of axes to highlight.
    marks
        Optional marks used to compute a data-region bounds rectangle.
        If a mapping is provided, it should map axes -> marks.
    canvas_style, axes_style, padding_style, data_style
        Style dictionaries applied to canvas background and debug fills.
        The style may include an "opacity" key, which will be applied
        using the mark opacity argument.
    """
    default_canvas_style = {"background-color": "#f2f2f2"}
    default_padding_style = {"fill": "#f7b0b0", "stroke": "none", "opacity": 0.25}
    default_axes_style = {"fill": "#b3d5f2", "stroke": "none", "opacity": 0.25}
    default_data_style = {"fill": "#b8e3b1", "stroke": "none", "opacity": 0.25}

    if canvas_style:
        default_canvas_style.update(canvas_style)
    if padding_style:
        default_padding_style.update(padding_style)
    if axes_style:
        default_axes_style.update(axes_style)
    if data_style:
        default_data_style.update(data_style)

    canvas.style.update(default_canvas_style)

    # normalize axes input
    axes_in = axes
    if isinstance(axes, Cartesian):
        axes = [axes]
    else:
        axes = list(axes)

    # draw debug shapes in canvas coordinate space
    overlay = canvas.cartesian(
        margin=0,
        padding=0,
        show=False,
        xshow=False,
        yshow=False,
        xmin=0,
        xmax=canvas.width,
        ymin=canvas.height,
        ymax=0,
    )

    def _rect(x0, x1, y0, y1, style):
        style = dict(style) if style is not None else {}
        opacity = style.pop("opacity", 1.0)
        overlay.fill(
            a=[x0, x1],
            b=[y0, y0],
            c=[y1, y1],
            along="x",
            opacity=opacity,
            style=style,
            annotation=True,
        )

    def _normalize_marks(marks_in, axes_list):
        if marks_in is None:
            return [None] * len(axes_list)
        if isinstance(marks_in, Mapping):
            return [marks_in.get(ax) for ax in axes_list]
        if isinstance(marks_in, (list, tuple)) and len(axes_list) > 1:
            if len(marks_in) == len(axes_list):
                return list(marks_in)
        return [marks_in] * len(axes_list)

    def _iter_marks(marks_in):
        if marks_in is None:
            return []
        if isinstance(marks_in, (list, tuple)):
            return list(marks_in)
        return [marks_in]

    def _bounds_from_marks(ax, marks_in):
        marks_list = _iter_marks(marks_in)
        if not marks_list:
            return None
        ax._finalize()
        xproj = ax._x_projection
        yproj = ax._y_projection
        lefts = []
        rights = []
        tops = []
        bottoms = []
        for mk in marks_list:
            coords, extents = mk.extents(["x", "y"])
            xs, ys = coords
            left, right, top, bottom = extents
            xr = xproj(xs)
            yr = yproj(ys)
            lefts.append(xr + left)
            rights.append(xr + right)
            tops.append(yr + top)
            bottoms.append(yr + bottom)
        lefts = np.ma.concatenate(lefts)
        rights = np.ma.concatenate(rights)
        tops = np.ma.concatenate(tops)
        bottoms = np.ma.concatenate(bottoms)
        return (
            float(np.ma.min(lefts)),
            float(np.ma.max(rights)),
            float(np.ma.min(tops)),
            float(np.ma.max(bottoms)),
        )

    marks_per_axes = _normalize_marks(marks, axes)

    for ax, ax_marks in zip(axes, marks_per_axes):
        x0 = ax._xmin_range
        x1 = ax._xmax_range
        y0 = ax._ymin_range
        y1 = ax._ymax_range
        pad = ax.padding
        _rect(x0 - pad, x1 + pad, y0 - pad, y1 + pad, default_padding_style)
        bounds = _bounds_from_marks(ax, ax_marks)
        if bounds is None:
            _rect(x0 + pad, x1 - pad, y0 + pad, y1 - pad, default_data_style)
        else:
            dx0, dx1, dy0, dy1 = bounds
            _rect(dx0, dx1, dy0, dy1, default_data_style)
        _rect(x0, x1, y0, y1, default_axes_style)

    return canvas, axes_in


if __name__ == "__main__":

    import toytree
    import numpy as np

    # ...
    tree = toytree.rtree.bdtree(50, b=5, d=2.5)
    c1, a, m = tree.draw(scale_bar=True, width=300, height=225, tip_labels=False, padding=10)
    a.x.label.text = "hello world"
    a.y.label.text = "hello world"
    set_axes_ticks_external(a)
    set_axes_box_outline(a)
    c1.style['stroke-width'] = 1.5

    # ...
    heights = np.array(sorted([-i.height for i in tree.traverse() if not i.is_leaf()]))
    loglineages = np.log(np.arange(2, tree.ntips + 1))
    c2, a, m = toyplot.plot(
        heights, loglineages,
        width=300,
        height=225,
        stroke_width=3,
        xlabel="time",
        ylabel="log n lineages",
    )
    set_axes_ticks_external(a)
    set_axes_box_outline(a)
    c2.style['stroke'] = 'grey'
    c2.style['stroke-width'] = 1.5
    toytree.utils.show([c1, c2])
