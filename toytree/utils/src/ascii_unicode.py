#!/usr/bin/env python

"""Render ``ToyTree`` objects as ASCII or Unicode line drawings.

This module contains the newer text renderer used by ``ToyTree.view()``.
It renders complete ``ToyTree`` objects, can scale horizontal branch
lengths from cached node heights, falls back to topology-only spacing
when needed, and can optionally ladderize clades for display without
modifying the underlying tree. Rendered branches can also be emphasized
from simple feature selectors without importing any broader query stack.
"""

from __future__ import annotations

import math
import re
from typing import TYPE_CHECKING, Callable, Literal

from toytree.utils.src.exceptions import TreeNodeError

if TYPE_CHECKING:
    from toytree.core.node import Node
    from toytree.core.tree import ToyTree


_CHARSET_VALUES = ("ascii", "unicode")
_HEAVY_OPS = ("<=", ">=", "!=", "<", ">", "=")
_HEAVY_SELECTOR = re.compile(
    r"^\s*(?P<feature>[^=!<>\s]+)\s*(?P<op><=|>=|!=|=|<|>)\s*(?P<value>.+?)\s*$"
)
_LEFT, _RIGHT, _UP, _DOWN = 1, 2, 4, 8
_MISSING = object()


def _validate_inputs(
    tree: ToyTree,
    width: int | None,
    charset: str,
    use_edge_lengths: bool,
    heavy: str | None,
    heavier: bool,
    ladderize: bool,
) -> None:
    """Validate public rendering arguments before layout work starts."""
    from toytree.core.tree import ToyTree

    if not isinstance(tree, ToyTree):
        raise TreeNodeError("tree must be a ToyTree instance.")
    if width is not None and (
        isinstance(width, bool) or not isinstance(width, int) or width < 2
    ):
        raise TreeNodeError("width must be None or an integer greater than 1.")
    if charset not in _CHARSET_VALUES:
        raise TreeNodeError("charset must be one of 'ascii' or 'unicode'.")
    if not isinstance(use_edge_lengths, bool):
        raise TreeNodeError("use_edge_lengths must be a bool.")
    if heavy is not None and (isinstance(heavy, bool) or not isinstance(heavy, str)):
        raise TreeNodeError(
            "heavy must be None or a selector string like "
            "'support>50', 'sex=M', or 'support=nan'."
        )
    if not isinstance(heavier, bool):
        raise TreeNodeError("heavier must be a bool.")
    if not isinstance(ladderize, bool):
        raise TreeNodeError("ladderize must be a bool.")


def _is_missing_value(value: object) -> bool:
    """Return True when a value should be treated as missing."""
    if value is None:
        return True
    try:
        return math.isnan(value)
    except TypeError:
        return str(value).strip().lower() == "nan"


def _is_empty_label(value: object) -> bool:
    """Return True when a tip label should be rendered as blank."""
    return _is_missing_value(value)


def _stringify_label(value: object) -> str:
    """Return a tip label string with NaN-like values hidden."""
    return "" if _is_empty_label(value) else str(value)


def _coerce_number(value: object) -> float | None:
    """Return a finite float when a value is numeric-like."""
    if value is _MISSING or isinstance(value, bool) or _is_missing_value(value):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not math.isfinite(number):
        return None
    return number


def _compile_heavy_selector(heavy: str | None) -> Callable[[Node], bool]:
    """Compile a branch-highlighting selector into a predicate."""
    if heavy is None:
        return lambda node: False
    if not heavy.strip():
        raise TreeNodeError(
            "heavy must be a selector string like "
            "'support>50', 'sex=M', or 'support=nan'."
        )

    match = _HEAVY_SELECTOR.match(heavy)
    if match is None:
        raise TreeNodeError(
            "heavy must be a selector like " "'support>50', 'sex=M', or 'support=nan'."
        )

    feature = match.group("feature")
    op = match.group("op")
    raw_value = match.group("value").strip()
    if not raw_value:
        raise TreeNodeError("heavy must include a right-hand value, e.g. 'support>50'.")
    if op not in _HEAVY_OPS:
        raise TreeNodeError(f"unsupported heavy operator {op!r}.")

    rhs_is_nan = raw_value.lower() == "nan"
    rhs_num = _coerce_number(raw_value)

    if op in {"<", "<=", ">", ">="}:
        if rhs_is_nan or rhs_num is None:
            raise TreeNodeError(
                "heavy numeric comparisons require a numeric value, "
                "e.g. 'support>50'."
            )
        comparators = {
            "<": lambda left: left < rhs_num,
            "<=": lambda left: left <= rhs_num,
            ">": lambda left: left > rhs_num,
            ">=": lambda left: left >= rhs_num,
        }

        def _numeric_predicate(node: Node) -> bool:
            value = getattr(node, feature, _MISSING)
            lhs_num = _coerce_number(value)
            return lhs_num is not None and comparators[op](lhs_num)

        return _numeric_predicate

    if rhs_is_nan:

        def _missing_predicate(node: Node) -> bool:
            value = getattr(node, feature, _MISSING)
            matched = value is _MISSING or _is_missing_value(value)
            return matched if op == "=" else not matched

        return _missing_predicate

    def _equality_predicate(node: Node) -> bool:
        value = getattr(node, feature, _MISSING)
        if value is _MISSING or _is_missing_value(value):
            return False
        lhs_num = _coerce_number(value)
        if rhs_num is not None and lhs_num is not None:
            matched = lhs_num == rhs_num
        else:
            matched = str(value) == raw_value
        return matched if op == "=" else not matched

    return _equality_predicate


def _resolve_tip_label(
    tip: Node,
    tip_labels: bool | str | tuple,
) -> str:
    """Resolve one tip label using the supported label specifications."""
    if tip_labels in (False, None):
        return ""

    feature = "name"
    formatter = None
    args: tuple[object, ...] = ()

    if tip_labels is True:
        pass
    elif isinstance(tip_labels, str):
        feature = tip_labels
    elif (
        isinstance(tip_labels, tuple) and tip_labels and isinstance(tip_labels[0], str)
    ):
        feature, *formatter_items = tip_labels
        if formatter_items:
            formatter = formatter_items[0]
            args = tuple(formatter_items[1:])
    else:
        raise TreeNodeError(
            "tip_labels must be True, False, None, a feature name, "
            "or a tuple like ('feature', formatter)."
        )

    if not hasattr(tip, feature):
        raise TreeNodeError(
            f"tip_labels requested missing feature {feature!r} on tip {tip!r}."
        )

    value = getattr(tip, feature)
    if formatter is None:
        return _stringify_label(value)
    if _is_empty_label(value):
        return ""
    if isinstance(formatter, str):
        try:
            return _stringify_label(formatter.format(value))
        except Exception as exc:
            raise TreeNodeError(
                f"tip_labels formatter failed for feature {feature!r}."
            ) from exc
    if callable(formatter):
        try:
            return _stringify_label(formatter(value, *args))
        except Exception as exc:
            raise TreeNodeError(
                f"tip_labels formatter failed for feature {feature!r}."
            ) from exc
    raise TreeNodeError(
        "tip_labels tuple must be ('feature', format_string) or "
        "('feature', callable, *args)."
    )


def _get_render_topology(
    tree: ToyTree,
    ladderize: bool,
) -> tuple[list[Node], list[Node], list[Node], dict[Node, tuple[Node, ...]]]:
    """Return nodes and child order in the order used for display."""
    root = tree.treenode

    if not ladderize:
        preorder_nodes = list(root.traverse("preorder"))
        postorder_nodes = list(root.traverse("postorder"))
        leaves = list(root.iter_leaves())
        return (
            leaves,
            preorder_nodes,
            postorder_nodes,
            {node: node.children for node in preorder_nodes},
        )

    descendant_counts: dict[Node, int] = {}
    render_children: dict[Node, tuple[Node, ...]] = {}
    for node in root.traverse("postorder"):
        if node.children:
            # Keep ties stable while sorting smaller clades first, matching
            # the default ladderize direction without mutating the tree.
            ordered_children = tuple(
                sorted(node.children, key=lambda child: descendant_counts[child])
            )
            render_children[node] = ordered_children
            descendant_counts[node] = sum(
                descendant_counts[child] for child in ordered_children
            )
        else:
            render_children[node] = ()
            descendant_counts[node] = 1

    preorder_nodes: list[Node] = []
    leaves: list[Node] = []
    stack = [root]
    while stack:
        node = stack.pop()
        preorder_nodes.append(node)
        children = render_children[node]
        if children:
            stack.extend(reversed(children))
        else:
            leaves.append(node)

    postorder_nodes: list[Node] = []
    stack2 = [(root, False)]
    while stack2:
        node, seen = stack2.pop()
        if seen:
            postorder_nodes.append(node)
            continue
        stack2.append((node, True))
        for child in reversed(render_children[node]):
            stack2.append((child, False))

    return leaves, preorder_nodes, postorder_nodes, render_children


def _resolve_tip_labels(
    leaves: list[Node],
    tip_labels: bool | str | tuple,
) -> dict[Node, str]:
    """Return the final rendered label for each displayed tip."""
    return {tip: _resolve_tip_label(tip, tip_labels) for tip in leaves}


def _estimate_width(leaves: list[Node], labels: dict[Node, str]) -> int:
    """Estimate a stable width from tree size and label lengths."""
    name_budget = max(len(tip.name) for tip in leaves)
    label_budget = max(len(label) for label in labels.values())
    return max(
        24,
        min(
            160,
            int(2.5 * len(leaves)) + max(name_budget, label_budget) + 8,
        ),
    )


def _assign_rows(
    leaves: list[Node],
    postorder_nodes: list[Node],
    render_children: dict[Node, tuple[Node, ...]],
) -> dict[Node, int]:
    """Assign one row per tip and midpoint rows to internal nodes."""
    rows: dict[Node, int] = {tip: 2 * idx for idx, tip in enumerate(leaves)}
    for node in postorder_nodes:
        children = render_children[node]
        if children:
            rows[node] = (rows[children[0]] + rows[children[-1]]) // 2
    return rows


def _get_topology_depths(preorder_nodes: list[Node]) -> dict[Node, int]:
    """Return root-to-node topological depths for the display order."""
    root = preorder_nodes[0]
    topo_depths: dict[Node, int] = {root: 0}
    for node in preorder_nodes[1:]:
        topo_depths[node] = topo_depths[node.up] + 1
    return topo_depths


def _get_scaled_depths(
    tree: ToyTree,
    preorder_nodes: list[Node],
    leaves: list[Node],
    use_edge_lengths: bool,
) -> dict[Node, float | int]:
    """Return horizontal depths for display columns."""
    topo_depths = _get_topology_depths(preorder_nodes)

    if not use_edge_lengths:
        max_tip_depth = max(topo_depths[tip] for tip in leaves)
        # Match the linear-layout topology view: internal edges use unit
        # spacing, then shorter terminal edges extend to the farthest tip.
        return {
            node: max_tip_depth if node.is_leaf() else topo_depths[node]
            for node in preorder_nodes
        }

    root_height = tree.treenode.height
    if not math.isfinite(root_height) or root_height <= 0:
        return topo_depths
    for node in preorder_nodes[1:]:
        if not math.isfinite(node.dist) or node.dist < 0:
            return topo_depths

    # ToyTree caches node heights, so root.height - node.height is the
    # root-to-node branch-length depth without a second cumulative walk.
    return {node: root_height - node.height for node in preorder_nodes}


def _assign_cols(
    preorder_nodes: list[Node],
    scaled_depths: dict[Node, float | int],
    labels: dict[Node, str],
    width: int,
) -> dict[Node, int]:
    """Scale display depths into integer canvas columns."""
    root = preorder_nodes[0]
    max_tip_label_len = max(len(label) for label in labels.values())
    label_space = max_tip_label_len + 1 if max_tip_label_len else 0
    branch_cols = max(2, width - label_space)
    max_depth = max(scaled_depths.values())
    cols: dict[Node, int] = {root: 0}

    # Preserve relative spacing when possible, but force every edge to
    # consume at least one column so deep trees stay visibly connected.
    for node in preorder_nodes[1:]:
        parent = node.up
        base_col = round((scaled_depths[node] / max_depth) * (branch_cols - 1))
        cols[node] = max(base_col, cols[parent] + 1)
    return cols


def _connect_horizontal(
    canvas: list[list[int | str]],
    heavy_horizontal: list[list[bool]],
    row: int,
    start: int,
    stop: int,
    heavy: bool = False,
) -> None:
    """Connect neighboring cells horizontally from start to stop."""
    if start == stop:
        return
    lo, hi = sorted((start, stop))
    for col in range(lo, hi):
        canvas[row][col] |= _RIGHT
        canvas[row][col + 1] |= _LEFT
        if heavy:
            heavy_horizontal[row][col] = True
            heavy_horizontal[row][col + 1] = True


def _connect_vertical(
    canvas: list[list[int | str]],
    col: int,
    start: int,
    stop: int,
) -> None:
    """Connect neighboring cells vertically from start to stop."""
    if start == stop:
        return
    lo, hi = sorted((start, stop))
    for row in range(lo, hi):
        canvas[row][col] |= _DOWN
        canvas[row + 1][col] |= _UP


def _is_heavy_branch(node: Node, heavy_selector: Callable[[Node], bool]) -> bool:
    """Return True when the edge above a displayed child should be heavy."""
    return (not node.is_root()) and heavy_selector(node)


def _build_connection_grids(
    preorder_nodes: list[Node],
    leaves: list[Node],
    labels: dict[Node, str],
    rows: dict[Node, int],
    cols: dict[Node, int],
    heavy_selector: Callable[[Node], bool],
) -> tuple[list[list[int | str]], list[list[bool]]]:
    """Build the connection grid and heavy-edge mask."""
    nrows = max(rows.values()) + 1
    ncols = 1
    for tip in leaves:
        label_end = cols[tip] + (1 + len(labels[tip]) if labels[tip] else 0)
        ncols = max(ncols, label_end + 1)
    ncols = max(ncols, max(cols.values()) + 1)

    canvas: list[list[int | str]] = [[0] * ncols for _ in range(nrows)]
    heavy_horizontal = [[False] * ncols for _ in range(nrows)]

    # Build the topology as directional connections first, then map each
    # occupied cell to one glyph. This avoids overshoot at forks and keeps
    # ASCII and Unicode rendering paths aligned.
    for node in preorder_nodes[1:]:
        _connect_horizontal(
            canvas,
            heavy_horizontal,
            rows[node],
            cols[node.up],
            cols[node],
            heavy=_is_heavy_branch(node, heavy_selector),
        )
        _connect_vertical(canvas, cols[node.up], rows[node.up], rows[node])

    for tip in leaves:
        label = labels[tip]
        if not label:
            continue
        start = cols[tip] + 1
        for offset, char in enumerate(label):
            canvas[rows[tip]][start + offset] = char

    return canvas, heavy_horizontal


def _mask_to_char(
    mask: int,
    heavy: bool,
    charset: Literal["ascii", "unicode"],
    heavier: bool,
) -> str:
    """Map a connection mask to one rendered glyph."""
    if not mask:
        return " "

    if charset == "ascii":
        if mask == (_RIGHT | _DOWN):
            return "/"
        if mask == (_RIGHT | _UP):
            return "\\"
        if mask & (_LEFT | _RIGHT) and mask & (_UP | _DOWN):
            return "+"
        if mask & (_LEFT | _RIGHT):
            # Heavier mode swaps only the horizontal emphasis glyph while
            # leaving connector geometry intact for readability.
            return "#" if heavier and heavy else "=" if heavy else "-"
        return "|"

    horiz = "▒" if heavier and heavy else "━" if heavy else "─"
    vert = "│"
    glyphs = {
        _LEFT: horiz,
        _RIGHT: horiz,
        _LEFT | _RIGHT: horiz,
        _UP: vert,
        _DOWN: vert,
        _UP | _DOWN: vert,
        _RIGHT | _DOWN: "┌",
        _RIGHT | _UP: "└",
        _LEFT | _DOWN: "┐",
        _LEFT | _UP: "┘",
        _RIGHT | _UP | _DOWN: "├",
        _LEFT | _UP | _DOWN: "┤",
        _LEFT | _RIGHT | _DOWN: "┬",
        _LEFT | _RIGHT | _UP: "┴",
        _LEFT | _RIGHT | _UP | _DOWN: "┼",
    }
    return glyphs.get(mask, horiz if mask & (_LEFT | _RIGHT) else vert)


def _render_lines(
    canvas: list[list[int | str]],
    heavy_horizontal: list[list[bool]],
    charset: Literal["ascii", "unicode"],
    heavier: bool,
) -> str:
    """Render the populated connection grid into the final text block."""
    lines = []
    for ridx, row in enumerate(canvas):
        chars = []
        for cidx, cell in enumerate(row):
            if isinstance(cell, str):
                chars.append(cell)
            else:
                chars.append(
                    _mask_to_char(
                        cell,
                        heavy_horizontal[ridx][cidx],
                        charset,
                        heavier,
                    )
                )
        lines.append("".join(chars).rstrip())
    return "\n".join(lines)


def get_ascii_or_unicode(
    tree: ToyTree,
    width: int | None = None,
    tip_labels: bool | str | tuple = True,
    charset: Literal["ascii", "unicode"] = "ascii",
    use_edge_lengths: bool = True,
    heavy: str | None = None,
    heavier: bool = False,
    ladderize: bool = False,
) -> str:
    """Return an ASCII or Unicode rendering of a ``ToyTree``.

    Parameters
    ----------
    tree : ToyTree
        Tree to render as a text block.
    width : int | None, default=None
        Target width for the drawing before label overflow. If ``None``,
        then a heuristic width is estimated from the number of tips and
        rendered label lengths.
    tip_labels : bool | str | tuple, default=True
        Tip-label specification. Use ``True`` for ``tip.name``,
        ``False`` or ``None`` to omit labels, a feature name string to
        display that attribute, or ``("feature", formatter)`` to apply
        a format string or callable.
    charset : Literal["ascii", "unicode"], default="ascii"
        Character set used to draw branches and connectors.
    use_edge_lengths : bool, default=True
        If ``True``, scale horizontal positions from cached node
        heights when valid edge lengths are available. If ``False``,
        render internal edges with equal spacing and extend terminal
        edges so all tips align at the farthest displayed tip.
    heavy : str | None, default=None
        Optional selector used to render matching non-root branches
        with heavy horizontal glyphs. Selectors use the form
        ``feature<op>value`` with operators ``=``, ``!=``, ``>``,
        ``>=``, ``<``, or ``<=``. Examples include ``support>95``,
        ``sex=M``, and ``support=nan``.
    heavier : bool, default=False
        If ``True``, then matching heavy branches use a stronger
        horizontal glyph: ``#`` in ASCII mode or ``▒`` in Unicode mode.
        If ``False``, heavy branches use ``=`` in ASCII mode or ``━``
        in Unicode mode.
    ladderize : bool, default=False
        If ``True``, reorder child clades by ascending descendant tip
        count for display only. The underlying tree is not modified.

    Returns
    -------
    str
        A text block representing ``tree``.

    Raises
    ------
    TreeNodeError
        Raised if rendering options are invalid or a requested tip-label
        feature or formatter cannot be resolved.

    Examples
    --------
    >>> import toytree
    >>> from toytree.utils.src.ascii_unicode import get_ascii_or_unicode
    >>> tree = toytree.tree("((a:1,b:2):3,c:4);")
    >>> print(get_ascii_or_unicode(tree, width=12))

    >>> print(
    ...     get_ascii_or_unicode(
    ...         tree,
    ...         charset="unicode",
    ...         use_edge_lengths=False,
    ...         heavy="support>95",
    ...         heavier=True,
    ...         ladderize=True,
    ...     )
    ... )

    See Also
    --------
    toytree.ToyTree.view
        Print the rendered tree directly to a text stream.
    toytree.Node.draw_ascii
        Legacy PyCogent-style printer retained for backward compatibility.
    """
    _validate_inputs(
        tree,
        width,
        charset,
        use_edge_lengths,
        heavy,
        heavier,
        ladderize,
    )

    leaves, preorder_nodes, postorder_nodes, render_children = _get_render_topology(
        tree,
        ladderize,
    )
    if not leaves:
        return ""
    labels = _resolve_tip_labels(leaves, tip_labels)
    if len(leaves) == 1:
        return labels[leaves[0]]

    render_width = _estimate_width(leaves, labels) if width is None else width
    rows = _assign_rows(leaves, postorder_nodes, render_children)
    scaled_depths = _get_scaled_depths(tree, preorder_nodes, leaves, use_edge_lengths)
    cols = _assign_cols(preorder_nodes, scaled_depths, labels, render_width)
    heavy_selector = _compile_heavy_selector(heavy)
    canvas, heavy_horizontal = _build_connection_grids(
        preorder_nodes,
        leaves,
        labels,
        rows,
        cols,
        heavy_selector,
    )
    return _render_lines(canvas, heavy_horizontal, charset, heavier)
