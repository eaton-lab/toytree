#!/usr/bin/env python

"""Return midpoint coordinate of edges given the layout.

"""

import numpy as np


def get_edge_midpoints(
    etable: np.ndarray,
    ntable: np.ndarray,
    layout: str,
    edge_type: str,
) -> np.ndarray:
    """Return mid coords (x,y) on edges for the add_edge_[x] functions.

    Finding midpoints requires information about the layout and edge_type
    """
    nnodes = ntable.shape[0]
    midpoints = np.zeros((nnodes, 2))
    for ridx in range(etable.shape[0]):
        cidx, pidx = etable[ridx]
        cx, cy = ntable[cidx]
        px, py = ntable[pidx]

        # unrooted layout is always edge_type='c'
        if edge_type == "c":
            midx = (px + cx) / 2.
            midy = (py + cy) / 2.
        else:
            if layout in ("u", "d"):
                midx = cx
                midy = (py + cy) / 2.
            elif layout in ("r", "l"):
                midx = (cx + px) / 2.
                midy = cy
            elif layout == "c":
                raise NotImplementedError("TODO. For now, use w/ edge_type='c'.")
            else:  # "unrooted":
                raise NotImplementedError("TODO. For now, use w/ edge_type='c'.")
        midpoints[cidx] = (midx, midy)
    return midpoints


if __name__ == "__main__":

    import toytree
    tree = toytree.rtree.unittree(10, seed=123)
    c, a, m = tree.draw()
    coords = get_edge_midpoints(m.etable, m.ntable, m.layout, m.edge_type)
    print(coords)
