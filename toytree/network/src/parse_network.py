#!/usr/bin/env python
"""Parse extended-newick networks into a major tree and admixture events."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple, Union, TypeVar
import re
from pathlib import Path


ToyTree = TypeVar("ToyTree")
Node = TypeVar("Node")
__all__ = ["AdmixtureEvent", "parse_network"]


@dataclass
class AdmixtureEvent:
    """Container describing one hybridization event."""
    src: Tuple[str, ...] | int | Node
    dst: Tuple[str, ...] | int | Node
    src_dist: float | None = None
    dst_dist: float | None = None
    style: Dict[str, object] = field(default_factory=dict)
    meta: Dict[str, object] = field(default_factory=dict)


def _load_network_string(net: Union[str, Path]) -> str:
    """Return the extended-newick network string from a file or string."""
    from toytree.io.src.parse import replace_whitespace

    if ";" not in str(net):
        net = Path(net)
        if not net.exists():
            raise IOError("input type is not a file or newick (no ; ending).")
        with open(net, "rt", encoding="utf-8") as infile:
            net = infile.readline().split(";")[0] + ";"
    else:
        net = str(net).split(";")[0] + ";"
    return replace_whitespace(net)


def _inject_gamma_into_labels(net: str) -> str:
    """Encode gamma values into node labels so ToyTree can parse them."""
    tip_gamma = re.compile(r"(#\w+):::([\d.]+)")
    internal_gamma = re.compile(r"(#\w+):([\d.]+)::([\d.]+)")
    net = tip_gamma.sub(r"\1-gamma-\2", net)
    net = internal_gamma.sub(r"\1-gamma-\3:\2", net)
    return net


def _extract_gamma(label: str) -> Tuple[str, float | None]:
    """Return the base label and parsed gamma if present."""
    if "-gamma-" not in label:
        return label, None
    base, gamma = label.rsplit("-gamma-", 1)
    try:
        return base, float(gamma)
    except ValueError:
        return base, None


def _group_hybrid_nodes(nodes: Iterable[Node]) -> Dict[str, List[Node]]:
    """Return mapping of hybrid id -> nodes with that label."""
    grouped: Dict[str, List[Node]] = {}
    for node in nodes:
        label, gamma = _extract_gamma(node.name)
        node.gamma = gamma if gamma else 0.
        grouped.setdefault(label, []).append(node)
    grouped = {i.lstrip("#"): sorted(j, key=lambda x: len(x.name)) for (i, j) in grouped.items()}
    return grouped


def _get_gamma_value(nodes: Iterable[Node]) -> float:
    """Extract gamma preferring leaf node gamma when available."""
    gamma = None
    for node in nodes:
        _, maybe = _extract_gamma(node.name)
        if maybe is None:
            continue
        if node.is_leaf():
            return maybe
        gamma = maybe
    return 0.5 if gamma is None else gamma


def parse_network(
    newick: Union[str, Path],
    keep_src_edges: bool = True,
    ) -> Tuple[ToyTree, Dict[str, AdmixtureEvent]]:
    """Return the major tree and admixture events parsed from a network."""
    from toytree.io.src.treeio import tree as treeio

    # load nwk from str or file and convert '#HX:DIST::GAMMA' to '#HX-GAMMA:DIST'
    net_string = _load_network_string(newick)
    net_string = _inject_gamma_into_labels(net_string)
    tree = treeio(net_string, internal_labels="name")
    events = []

    # parse #H nodes from tree, keeping major tree and and storing admixture events
    while True:
        try:
            hnodes = tree.get_nodes("~#H*")
        except ValueError:
            hnodes = []
        if not hnodes:
            break

        # pair src,dst nodes
        grouped = _group_hybrid_nodes(hnodes)
        hid, (dst, src) = grouped.popitem()

        # get dst.dist measured from first true (non-unary) descendant node
        dist = 0.
        n = dst.children
        while len(n) == 1:
            dist += n[0].dist
            n = n[0].children


        # store admixture event
        # style = {'stroke': next(colors), 'stroke-width': 10 * src.gamma, 'stroke-dasharray': "3,5"}
        events.append(
            AdmixtureEvent(
                src=src.get_leaf_names(),  #
                dst=dst.get_leaf_names(),  #
                src_dist=0.0,
                dst_dist=dist,  # dst.dist,
                meta={"label": hid, 'gamma': src.gamma},
                # label=f"γ={src.gamma}",
                # label=f"{hid};γ={src.gamma}",
                # hid=hid,
                # gamma=src.gamma,
            )
        )

        # remove dst node, rename src node
        dst._delete()
        src.name = src.name.lstrip("#").split("-gamma-")[0]
        tree._update()

    # relabel hybrid tips in tree and admix events
    for ae in events:
        ae.src = [i if "-gamma-" not in i else i.lstrip("#").split("-gamma-")[0] for i in ae.src]
        ae.dst = [i if "-gamma-" not in i else i.lstrip("#").split("-gamma-")[0] for i in ae.dst]
    return tree, events



if __name__ == "__main__":
    pass

    H0 = "((A:1,B:1)AB:1,(C:1,D:1):1);"
    H1 = "(((A:0.5,#H1:0.1::0.2):0.5,B:1),((C:0.2)#H1:0.8,D:0.1):1)Root;"
    H2 = "(((A:0.5,#H1:0.1::0.2):0.5,(B:0.5,#H2:0.2::0.3):0.5):1,((C:0.2)#H1:0.8,(D:0.1)#H2:0.9):1)Root;"
    H2 = "(((A:0.5,#H1:0.1::0.2):0.5,(B:0.5,#H2:0.2::0.3):0.5):1,((C:0.2)#H1:0.8,(D:0.1)#H2:0.9):1)Root;"
    H3 = "((((A:0.5,#H1:0.1::0.2):0.5,#H3:0.2::0.1),(B:0.5,#H2:0.2::0.3):0.5):1,(((C:0.2)#H1:0.8)#H3:0.8,(D:0.1)#H2:0.9):1)Root;"
    t, a = parse_network(H1)
    print(t.get_ascii())
    for i in a:
        print(i)
