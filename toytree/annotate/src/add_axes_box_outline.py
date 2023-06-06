#!/usr/bin/env python

"""Apply styling to toyplot Cartesian axes objects.

Set margin to 60.
"""

from typing import Union, Sequence
from toytree import ToyTree
from toytree.core import Cartesian
from toytree.core.apis import add_subpackage_method, AnnotationAPI
# from toytree.annotate.src.annotation_mark import (
#     get_last_toytree_mark_from_cartesian,
#     assert_tree_matches_mark,
# )

__all__ = ["add_axes_box_outline"]


@add_subpackage_method(AnnotationAPI)
def add_axes_box_outline(
    tree: ToyTree,
    axes: Cartesian,
    margin: Union[int, Sequence[int]] = 60,
    padding: Union[int, Sequence[int]] = None,
    **kwargs,
) -> Cartesian:
    """Adds a box outline to plots.

    This is achieved by creating new axes objects that ignore the data
    domain and extend their spines all the way to the extent of the
    axes padding.

    Parameters
    ----------
    ...

    Note
    ----
    To easily set the stroke-width of ALL spines, ticks, etc you can
    use the canvas.style['stroke-width'] setting. Also, note that if
    the axes.padding is changed AFTER this function is called then the
    axes can be separated from the box outline (i.e., this func uses
    the current padding value to align the two).
    """
    # mark = get_last_toytree_mark_from_cartesian(axes)
    # assert_tree_matches_mark(tree, mark)

    # get padding and margin from axes, or override with new values
    padding = padding if padding is not None else axes._padding
    margin = margin if margin is not None else axes._xmin_range

    # set data domain [margin][pad][ data ][pad][margin] of Cartesian
    #                  label | ax | data  | ax  | label
    x_width = axes._xmax_range - axes._xmin_range
    axes._set_xmin_range(margin)
    axes._set_xmax_range(margin + x_width)
    axes._padding = padding

    # create new axis opposite of original y
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


@add_subpackage_method(AnnotationAPI)
def set_axes_ticks_external(
    tree: ToyTree,
    axes: Cartesian,
    show_domain: bool = True,
) -> Cartesian:
    """Add custom generic style to plot axes.

    Sets tick marks to extend 5px outside of spine, tick mark labels
    to 10px outside of spine, and text labels to 30px outside of spine.
    To make sure that labels can still fit, the margin is also increased
    by 10px, so that it is 60px on top, bottom, left and right.
    """
    axes.x.ticks.show = True
    axes.x.domain.show = show_domain
    axes.y.domain.show = show_domain
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


if __name__ == "__main__":
    pass
