#!/usr/bin/env python

"""Apply styling to toyplot Cartesian axes objects.

Set margin to 60.
"""

import toyplot


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
