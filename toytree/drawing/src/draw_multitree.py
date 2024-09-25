#!/usr/bin/env python

"""Default function for drawing MultiTrees as a grid of trees.

"""

from typing import Tuple, Optional, Sequence, Union, List, TypeVar
from toytree.core import Canvas, Cartesian, Mark
from toytree.drawing.src.setup_grid import Grid
from toytree.style import get_base_tree_style_by_name
from toytree.annotate import add_axes_scale_bar
import toytree
from loguru import logger

MultiTree = TypeVar("MultiTree")
logger = logger.bind(name="toytree")


def draw_multitree(
    mtree: MultiTree,
    shape: Tuple[int, int] = (1, 4),
    shared_axes: bool = False,
    idxs: Optional[Sequence[int]] = None,
    width: Optional[int] = None,
    height: Optional[int] = None,
    margin: Union[float, Tuple[int, int, int, int]] = None,
    **kwargs,
    ) -> Tuple[Canvas, Cartesian, List[Mark]]:
    """Return a toyplot drawing of a grid of ToyTrees.

    The grid spacing can be controlled with shape and margin
    options, and trees can each be on their own axis or on a
    set of shared axes (same max height dimension), which can be
    better for highlighting differences in heights.

    Parameters
    ----------
    shape: Tuple[int,int]
        A tuple of (nrows, ncolumns) for a tree grid drawing. The
        dimension of this matrix determines the number of trees
        that will be plotted.
    shared_axes (bool):
        If True then the 'height' dimension will be shared among
        all trees, otherwise each tree is scaled to fill the
        space in its grid cell.
    idxs (int):
        The indices of trees in treelist that you want to draw. By
        default the first ncols*nrows trees are drawn, but you can
        select the 10-14th tree by entering idxs=[10,11,12,13].
        The selected trees will be displayed in the grid.
    width (int):
        Width of the canvas
    height (int):
        Height of the canvas
    margin: Tuple[int,int,int,int]
        Spacing between subplots in the grid in pixel units. A
        single value or a tuple for top, right, bottom, left.
    **kwargs (dict):
        Any style arguments supported by .draw() in toytrees.

    Examples
    --------
    >>> trees = [toytree.rtree.unittree(10) for i in range(10)]
    >>> mtre = toytree.mtree(trees)
    >>> mtre.draw(shape=(2, 3), width=800, edge_widths=4)
    """
    # legacy support: warn user of old deprecated args.
    if kwargs.get("nrows") or kwargs.get("ncols"):
        raise DeprecationWarning(
            "nrows and ncols args deprecated. Use shape=(nrows, ncols)")

    # get indices of trees that will be drawn
    nrows = max(1, shape[0])
    ncols = max(1, shape[1])
    if idxs is None:
        tidx = range(0, min(nrows * ncols, len(mtree.treelist)))
    else:
        tidx = [idxs] if isinstance(idxs, int) else list(idxs)

    # get all or subset of ToyTrees within the idxs range
    try:
        treelist = [mtree.treelist[i] for i in tidx]
    except IndexError as err:
        logger.error(f"bad idxs argument: {err}")
        raise err

    # if fixed_order=True get the ladderized consensus tree tip order
    # as a List[str] and set that as the fixed_order arg.
    if kwargs.get("fixed_order") is True:
        fixed_order = (
            toytree.MultiTree(treelist)
            .get_consensus_tree()
            .get_tip_labels()
        )
        kwargs["fixed_order"] = fixed_order

    # if less than 4 trees reshape ncols,rows to use ntrees
    if len(treelist) < 4:
        if nrows > ncols:
            nrows = len(treelist)
            ncols = 1
        else:
            nrows = 1
            ncols = len(treelist)

    # get layout first from direct arg then from treestyle
    if "ts" in kwargs:
        layout = get_base_tree_style_by_name(kwargs.get("ts")).layout
    elif "tree_style" in kwargs:
        layout = get_base_tree_style_by_name(kwargs.get("ts")).layout
    else:
        layout = kwargs.get("layout", 'r')

    # get the canvas and axes that can fit the requested trees.
    padding = kwargs.get("padding", 10)
    scale_bar = kwargs.get("scale_bar", False)
    grid = Grid(nrows, ncols, width, height, layout, margin, padding, scale_bar)
    canvas = grid.canvas
    axes = grid.axes

    # default style
    if "tip_labels_style" in kwargs:
        if "-toyplot-anchor-shift" not in kwargs["tip_labels_style"]:
            kwargs["tip_labels_style"]["-toyplot-anchor-shift"] = "10px"
        if "font-size" not in kwargs["tip_labels_style"]:
            kwargs["font-size"] = "10px"
    else:
        kwargs["tip_labels_style"] = {
            "-toyplot-anchor-shift": "10px",
            "font-size": "10px",
        }

    # add toytree-Grid mark to the axes
    marks = []
    tmpargs = kwargs.copy()

    # get max tree height for shared_axes top
    ymax = max(abs(i.treenode.height) for i in treelist)

    # add ToyTree marks
    ncells = grid.nrows * grid.ncols
    for idx in range(ncells):

        # get the axis
        axes = grid.axes[idx]

        # check if an input arg that should be singular was entered as a
        # list of ncells, in which case it should be applied individually
        # to each tree as a sequence.
        # ...

        # add the mark
        if idx < len(treelist):
            _, _, mark = treelist[idx].draw(axes=axes, **tmpargs)

        # store the mark
        marks.append(mark)

    # mod style axes
    for idx in range(grid.nrows * grid.ncols):

        # HACK \/\/\/\/\/\/\/\/\/\/\/\
        if shared_axes:
            # grid.axes[idx].y.domain.max = ymax
            mark.width = canvas.width / ncols
            mark.height = canvas.height / nrows
            mark.scale_bar = kwargs.get("scale_bar", False)
            add_axes_scale_bar(treelist[idx], grid.axes[idx], ymax=ymax)
            # set_axes_ticks_style(ymax, grid.axes[idx], mark, only_inside=True)

            # add an invisible spacer point. This does a much
            # better job than setting ticks alone.
            if mark.layout == 'd':
                grid.axes[idx].scatterplot(
                    mark.xbaseline + treelist[idx].ntips / 2,
                    mark.ybaseline + ymax,
                    color="transparent",
                )
            elif mark.layout == 'u':
                grid.axes[idx].scatterplot(
                    mark.xbaseline + treelist[idx].ntips / 2,
                    mark.ybaseline - ymax,
                    color="transparent",
                )
            elif mark.layout == 'l':
                grid.axes[idx].scatterplot(
                    mark.xbaseline + ymax,
                    mark.ybaseline + treelist[idx].ntips / 2,
                    color="transparent",
                )
            elif mark.layout == 'r':
                grid.axes[idx].scatterplot(
                    mark.xbaseline - ymax,
                    mark.ybaseline + treelist[idx].ntips / 2,
                    color="transparent",
                )

        # axes off if not scale_bar
        if kwargs.get("scale_bar", False) is False:
            if mark.layout in 'du':
                grid.axes[idx].y.show = False
                grid.axes[idx].x.show = False
            else:
                grid.axes[idx].y.show = False
                grid.axes[idx].x.show = False

        if kwargs.get("label"):
            label = kwargs.get("label")
            if not isinstance(label, str):
                label = label[idx]
            grid.axes[idx].label.text = label

    # add mark to axes
    return canvas, grid.axes, marks    


if __name__ == "__main__":

    import toytree    
    trees = [toytree.rtree.unittree(5) for i in range(10)]
    mtree = toytree.mtree(trees)
    c, a, m = draw_multitree(mtree, shape=(2, 8))
    toytree.utils.show([c], tmpdir="~")
