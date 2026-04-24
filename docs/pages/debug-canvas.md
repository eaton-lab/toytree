---
section: User Guide
---

# Debugging Canvas, Axes, and Data Bounds

`toytree.utils.debug_toyplot_canvas()` adds translucent fills to a Toyplot
canvas and axes so you can see layout regions at a glance. This is useful
when tuning `margin`, `padding`, and label offsets.

## What the layers mean

- **Canvas** (background color): the full canvas area.
- **Padding** (outer band): axes range expanded by `axes.padding`.
- **Axes**: the axes range itself.
- **Data**: the bounds of the marks, computed from mark extents.

## Example

```python
import toytree

# draw a tree and keep the returned mark
tree = toytree.rtree.unittree(10)
c, a, m = tree.draw(layout="r", tip_labels=True)

# show axes so the ranges are visible
a.x.show = True
a.y.show = True

# add debug fills (data bounds computed from mark extents)
toytree.utils.debug_toyplot_canvas(c, a, marks=m)

# display in notebook
c
```

## Custom colors

```python
toytree.utils.debug_toyplot_canvas(
    c,
    a,
    marks=m,
    canvas_style={"background-color": "#fafafa"},
    padding_style={"fill": "#ffb3b3", "opacity": 0.2},
    axes_style={"fill": "#b3d9ff", "opacity": 0.2},
    data_style={"fill": "#b8e3b1", "opacity": 0.35},
)
```

## Multiple axes

If you have multiple axes (e.g., grid layouts), pass a list of axes and
a corresponding list of marks (or a mapping from axes to marks):

```python
toytree.utils.debug_toyplot_canvas(
    c,
    [ax1, ax2],
    marks=[mark1, mark2],
)
```
