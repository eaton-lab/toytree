#!/usr/bin/env python

"""Canvas setup functions for single or grids of trees."""

from __future__ import annotations

from dataclasses import dataclass, field

from toyplot.canvas import Canvas
from toyplot.coordinates import Cartesian

AUTO_GRID_MAX_WIDTH = 1600.0
AUTO_GRID_MAX_HEIGHT = 1200.0


@dataclass(frozen=True)
class GridSizeSpec:
    """Store per-cell sizing bounds for a multitree layout family.

    Parameters
    ----------
    base_cell_width : float
        Minimum per-cell width in px used for compact grid defaults.
    base_cell_height : float
        Minimum per-cell height in px used for compact grid defaults.
    ref_mark_width : float
        Single-tree preferred width treated as the compact baseline for
        extent-aware auto-sizing.
    ref_mark_height : float
        Single-tree preferred height treated as the compact baseline for
        extent-aware auto-sizing.
    max_cell_width : float
        Soft per-cell width cap applied during auto-sizing.
    max_cell_height : float
        Soft per-cell height cap applied during auto-sizing.
    """

    base_cell_width: float
    base_cell_height: float
    ref_mark_width: float
    ref_mark_height: float
    max_cell_width: float
    max_cell_height: float


def get_grid_size_spec(layout: str) -> GridSizeSpec:
    """Return per-cell sizing bounds for a multitree layout family.

    Parameters
    ----------
    layout : str
        Layout token used for the grid.

    Returns
    -------
    GridSizeSpec
        Layout-family sizing constants for compact defaults and
        extent-aware auto-sizing.
    """
    if layout in ("r", "l"):
        return GridSizeSpec(
            base_cell_width=225.0,
            base_cell_height=250.0,
            ref_mark_width=300.0,
            ref_mark_height=275.0,
            max_cell_width=400.0,
            max_cell_height=325.0,
        )
    if layout in ("u", "d"):
        return GridSizeSpec(
            base_cell_width=225.0,
            base_cell_height=250.0,
            ref_mark_width=300.0,
            ref_mark_height=300.0,
            max_cell_width=325.0,
            max_cell_height=400.0,
        )
    return GridSizeSpec(
        base_cell_width=250.0,
        base_cell_height=250.0,
        ref_mark_width=280.0,
        ref_mark_height=280.0,
        max_cell_width=350.0,
        max_cell_height=350.0,
    )


def _scale_total_extent(
    total: float,
    nslots: int,
    base_cell: float,
    soft_cap: float,
) -> float:
    """Return a soft-capped grid extent without shrinking below base cells."""
    if total <= soft_cap:
        return total
    return max(base_cell, soft_cap / nslots) * nslots


def get_fallback_grid_canvas_size(
    nrows: int,
    ncols: int,
    layout: str,
) -> tuple[float, float]:
    """Return compact fallback canvas size for a tree grid.

    Parameters
    ----------
    nrows : int
        Number of grid rows.
    ncols : int
        Number of grid columns.
    layout : str
        Layout token used for the grid.

    Returns
    -------
    tuple[float, float]
        Canvas ``(width, height)`` in px derived from base cell sizes
        and the multitree soft canvas caps.
    """
    spec = get_grid_size_spec(layout)
    width = _scale_total_extent(
        spec.base_cell_width * ncols,
        ncols,
        spec.base_cell_width,
        AUTO_GRID_MAX_WIDTH,
    )
    height = _scale_total_extent(
        spec.base_cell_height * nrows,
        nrows,
        spec.base_cell_height,
        AUTO_GRID_MAX_HEIGHT,
    )
    return width, height


@dataclass
class Grid:
    """Store canvas and subplot axes for a tree grid.

    Parameters
    ----------
    nrows : int
        Number of grid rows.
    ncols : int
        Number of grid columns.
    width : float or int or None
        Canvas width in px, or None to infer it from layout defaults.
    height : float or int or None
        Canvas height in px, or None to infer it from layout defaults.
    layout : str
        Layout code used to infer default canvas geometry.
    margin : float or tuple[float, float, float, float] or None
        Subplot margin in px, either as a scalar or
        ``(top, right, bottom, left)``.
    padding : float
        Toyplot padding passed to each subplot Cartesian.
    scale_bar : bool or float or int
        Scale-bar setting used only to reserve subplot margin space.
    """

    nrows: int
    ncols: int
    width: float | int | None
    height: float | int | None
    layout: str
    margin: float | tuple[float, float, float, float] | None
    padding: float
    scale_bar: bool | float | int

    # attrs to be filled
    canvas: Canvas | None = field(default=None, init=False)
    axes: list[Cartesian] = field(init=False, default_factory=list)

    def __post_init__(self):
        """Initialize the canvas and populate subplot axes."""
        self.get_canvas()
        self.get_axes()

    def get_axes(self) -> None:
        """Populate per-cell Cartesian axes with grid-aware margins."""
        nplots = self.nrows * self.ncols

        # create a separate Cartesian for each tree subplot
        for idx in range(nplots):
            # get the margin setting depending on axes on edge or mid
            if self.margin is not None:
                margin = self.margin
            else:
                if self.nrows == 1:
                    margin = [50, 10, 50, 30]
                else:
                    margin = [30, 30, 30, 30]
                    row, _ = divmod(idx, self.ncols)
                    if row == 0:
                        margin[0] += 10
                        margin[2] -= 10
                    if row == self.nrows - 1:
                        margin[2] += 10
                        margin[0] -= 10

                # ensure room for the scale bar
                if self.scale_bar:
                    if self.layout in "du":
                        margin[3] += 20
                    elif self.layout in "lr":
                        margin[2] += 20
                margin = tuple(margin)

            # create Cartesian and append to list
            axes = self.canvas.cartesian(
                grid=(self.nrows, self.ncols, idx),
                padding=self.padding,
                margin=margin,
            )
            axes.margin = margin
            self.axes.append(axes)

    def get_canvas(self) -> None:
        """Set canvas dimensions from user input or layout heuristics."""
        fallback_width, fallback_height = get_fallback_grid_canvas_size(
            self.nrows,
            self.ncols,
            self.layout,
        )
        if self.width is None:
            self.width = fallback_width
        if self.height is None:
            self.height = fallback_height
        self.canvas = Canvas(
            height=self.height,
            width=self.width,
        )


if __name__ == "__main__":
    # get_multitree_grid()

    grid = Grid(2, 1, None, None, "r", None, 10, False)
    print(grid)
