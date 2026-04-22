#!/usr/bin/env python

"""Compute conditional clade probabilities...

Example
-------
gtree = (...)
sptree = (...)

"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from math import comb
from typing import Dict, List, Tuple

import numpy as np
from scipy.signal import convolve2d
from scipy.sparse import csr_matrix
from scipy.sparse.linalg import expm_multiply

import toytree

# ----------------------------
# Bitmask helpers
# ----------------------------


def _all_mask(n: int) -> int:
    return (1 << n) - 1


def _mask_from_names(names: List[str], name_to_bit: Dict[str, int]) -> int:
    m = 0
    for nm in names:
        m |= name_to_bit[nm]
    return m


def _names_from_mask(mask: int, tips: List[str]) -> List[str]:
    out = []
    for i, nm in enumerate(tips):
        if (mask >> i) & 1:
            out.append(nm)
    return out


# ----------------------------
# Tree traversal / descendant masks
# ----------------------------


def _postorder_nodes(tree: toytree.ToyTree):
    return list(tree.treenode.traverse("postorder"))


def _descendant_masks(
    tree: toytree.ToyTree, name_to_bit: Dict[str, int]
) -> Dict[object, int]:
    """Compute descendant bitmask for every Node in tree (postorder DP)."""
    masks: Dict[object, int] = {}
    for n in _postorder_nodes(tree):
        if n.is_leaf():
            masks[n] = name_to_bit[n.name]
        else:
            m = 0
            for ch in n.children:
                m |= masks[ch]
            masks[n] = m
    return masks


def _find_mrca_by_masks(
    B_nodes_post: List[object], B_desc: Dict[object, int], S_mask: int
) -> object:
    """
    MRCA is the smallest (fewest descendants) node whose descendant set contains S.
    Works even if S is not a species-tree clade.
    """
    best = None
    best_size = 10**9
    for n in B_nodes_post:
        dm = B_desc[n]
        if (dm & S_mask) == S_mask:  # contains S
            sz = dm.bit_count()
            if sz < best_size:
                best = n
                best_size = sz
    if best is None:
        raise ValueError("Could not find MRCA (unexpected: S not subset of B tips?).")
    return best


def _ancestor_set_including(node: object) -> set:
    s = {node}
    cur = node
    while cur.up is not None:
        cur = cur.up
        s.add(cur)
    return s


# ----------------------------
# Distribution container
# ----------------------------


@dataclass
class Dist2D:
    # transient distribution over (i,j) lineage counts
    P: np.ndarray  # shape (Imax+1, Jmax+1)
    pS: float  # success absorbing mass (only used on MRCA->root path)
    pF: float  # failure absorbing mass


def _dist_leaf(in_S: bool) -> Dist2D:
    if in_S:
        P = np.zeros((2, 1), dtype=float)  # i in {0,1}, j=0
        P[1, 0] = 1.0
    else:
        P = np.zeros((1, 2), dtype=float)  # i=0, j in {0,1}
        P[0, 1] = 1.0
    return Dist2D(P=P, pS=0.0, pF=0.0)


def _merge_dists(children: List[Dist2D]) -> Dist2D:
    """
    Merge k child populations at a speciation node (backwards in time).
    Transient parts convolve in (i,j). Absorbing masses combine by independence.
    """
    if not children:
        raise ValueError("No children to merge.")

    cur = children[0]
    for nxt in children[1:]:
        # transient convolution
        P = convolve2d(cur.P, nxt.P, mode="full")

        # absorbing failure: if either child is failure
        pF = cur.pF + nxt.pF - cur.pF * nxt.pF

        # absorbing success: if either child is success AND neither is failure
        pS = cur.pS * (1 - nxt.pF) + nxt.pS * (1 - cur.pF) - cur.pS * nxt.pS

        cur = Dist2D(P=P, pS=pS, pF=pF)

    return cur


# ----------------------------
# CTMC generator build + branch propagation
# ----------------------------


@lru_cache(maxsize=None)
def _build_ctmc(
    Imax: int, Jmax: int, success_mode: bool
) -> Tuple[csr_matrix, Dict[Tuple[int, int], int], int, int | None]:
    """
    Build sparse generator Q (row-vector convention dp/dt = p Q).
    States include:
      - all (i,j) with 0<=i<=Imax, 0<=j<=Jmax, excluding (0,0)
      - if success_mode: exclude all i==1 transient states and use absorbing 'S' instead
      - absorbing 'F' always
    Returns:
      Q (csr), idx_map for tuple states, idx_F, idx_S (or None if !success_mode)
    """
    idx_map: Dict[Tuple[int, int], int] = {}
    states: List[Tuple[int, int] | str] = []

    # tuple (i,j) transient states
    for i in range(Imax + 1):
        for j in range(Jmax + 1):
            if i == 0 and j == 0:
                continue
            if success_mode and i == 1:
                continue
            idx_map[(i, j)] = len(states)
            states.append((i, j))

    idx_S = None
    if success_mode:
        idx_S = len(states)
        states.append("S")

    idx_F = len(states)
    states.append("F")

    n = len(states)
    rows = []
    cols = []
    data = []

    def add(src: int, dst: int, rate: float) -> None:
        rows.append(src)
        cols.append(dst)
        data.append(rate)

    # fill transitions
    for (i, j), src in idx_map.items():
        total = 0.0

        # within-S coalescence: (i,j) -> (i-1,j)
        if i >= 2:
            r = comb(i, 2)
            total += r
            if success_mode and (i - 1) == 1:
                add(src, idx_S, r)  # type: ignore[arg-type]
            else:
                add(src, idx_map[(i - 1, j)], r)

        # within-outside coalescence: (i,j) -> (i,j-1)
        if j >= 2:
            r = comb(j, 2)
            total += r
            add(src, idx_map[(i, j - 1)], r)

        # cross coalescence -> failure
        if i > 0 and j > 0:
            r = i * j
            total += r
            add(src, idx_F, r)

        # diagonal
        add(src, src, -total)

    Q = csr_matrix((data, (rows, cols)), shape=(n, n), dtype=float)
    return Q, idx_map, idx_F, idx_S


def _propagate_branch(
    dist: Dist2D, t: float, Imax: int, Jmax: int, success_mode: bool
) -> Dist2D:
    """
    Push distribution through a branch of length t (coalescent units).
    Uses expm_multiply on sparse Q^T for column-vector probabilities.
    """
    if t == 0.0:
        # still need to collapse i==1 into pS in success_mode
        if success_mode:
            P = dist.P.copy()
            pS = dist.pS
            # move all i==1 transient mass into success
            if P.shape[0] > 1:
                pS += float(P[1, :].sum())
                P[1, :] = 0.0
            return Dist2D(P=P, pS=pS, pF=dist.pF)
        return dist

    Q, idx_map, idx_F, idx_S = _build_ctmc(Imax, Jmax, success_mode)

    v = np.zeros((Q.shape[0],), dtype=float)

    # load transient mass
    P = dist.P
    for i in range(P.shape[0]):
        for j in range(P.shape[1]):
            p = P[i, j]
            if p == 0.0:
                continue
            if i == 0 and j == 0:
                continue
            if success_mode and i == 1:
                v[idx_S] += p  # type: ignore[index]
            else:
                v[idx_map[(i, j)]] += p

    # load absorbing mass
    v[idx_F] += dist.pF
    if success_mode:
        v[idx_S] += dist.pS  # type: ignore[index]

    # evolve column vector under Q^T
    v2 = expm_multiply((Q.T) * t, v)

    # unpack
    P2 = np.zeros((Imax + 1, Jmax + 1), dtype=float)
    for (i, j), k in idx_map.items():
        P2[i, j] = float(v2[k])

    pF2 = float(v2[idx_F])
    pS2 = float(v2[idx_S]) if success_mode else 0.0  # type: ignore[arg-type]

    return Dist2D(P=P2, pS=pS2, pF=pF2)


@lru_cache(maxsize=None)
def _eventual_success(i: int, j: int) -> float:
    """
    In an infinite ancestral population: P(hit i=1 before cross event),
    allowing outside-outside coalescences to reduce j.
    """
    if i <= 1 or j == 0:
        return 1.0
    rin = comb(i, 2)
    rout = comb(j, 2)
    rcross = i * j
    tot = rin + rout + rcross
    # cross => immediate failure (0 contribution)
    return (rin / tot) * _eventual_success(i - 1, j) + (rout / tot) * _eventual_success(
        i, j - 1
    )


# ----------------------------
# Main: clade probability for one clade mask S
# ----------------------------


def clade_probability_msc_dp(B: toytree.ToyTree, S_mask: int) -> float:
    """
    Exact P(gene tree contains clade S | MSC on species tree B),
    with one sample per species and matching labels.
    """
    tips = B.get_tip_labels()
    n = len(tips)
    full = _all_mask(n)

    if S_mask == 0 or S_mask == full or S_mask.bit_count() < 2:
        # empty, all-taxa, or singleton "clade" => probability 1 by definition/convention
        return 1.0

    name_to_bit = {nm: (1 << i) for i, nm in enumerate(tips)}
    B_nodes = _postorder_nodes(B)
    B_desc = _descendant_masks(B, name_to_bit)

    mrca = _find_mrca_by_masks(B_nodes, B_desc, S_mask)
    anc = _ancestor_set_including(mrca)

    # DP: for each node, store distribution at *top* of its branch (after propagating its dist)
    dist_top: Dict[object, Dist2D] = {}

    for node in B_nodes:
        dm = B_desc[node]
        Imax = (dm & S_mask).bit_count()
        Jmax = (dm & (full ^ S_mask)).bit_count()

        if node.is_leaf():
            dist0 = _dist_leaf(in_S=bool(dm & S_mask))
        else:
            child_dists = [dist_top[ch] for ch in node.children]
            dist0 = _merge_dists(child_dists)

        # propagate along the branch from this node to its parent
        t = float(node.dist) if (node.dist is not None) else 0.0
        success_mode = node in anc
        dist1 = _propagate_branch(dist0, t, Imax, Jmax, success_mode)

        dist_top[node] = dist1

    root = B.treenode
    dist_root = dist_top[root]

    # Finish: at the (infinite) ancestral population above the root, compute eventual success.
    p = dist_root.pS
    P = dist_root.P
    for i in range(P.shape[0]):
        for j in range(P.shape[1]):
            pij = P[i, j]
            if pij == 0.0:
                continue
            if i == 0 and j == 0:
                continue
            # note: on MRCA->root path we have collapsed i==1 into pS already
            p += pij * _eventual_success(i, j)

    # numerical safety
    return float(min(1.0, max(0.0, p)))


# ----------------------------
# Compute probabilities for all internal clades in gene tree A
# ----------------------------


def gene_tree_clade_probs(
    A: toytree.ToyTree, B: toytree.ToyTree
) -> Dict[Tuple[str, ...], float]:
    """
    Return {clade_taxa_tuple: probability} for each internal clade in A (excluding root).
    """
    tipsB = B.get_tip_labels()
    tipsA = A.get_tip_labels()
    if set(tipsA) != set(tipsB):
        raise ValueError(
            "A and B must have identical tip label sets (one sample per species)."
        )

    # fix a consistent bit order using B's tip ordering
    name_to_bit = {nm: (1 << i) for i, nm in enumerate(tipsB)}

    # clade masks from A
    A_desc = _descendant_masks(A, name_to_bit)
    out: Dict[Tuple[str, ...], float] = {}

    for node in _postorder_nodes(A):
        if node.is_leaf():
            continue
        if node.up is None:
            continue  # skip the root clade (all taxa)
        S_mask = A_desc[node]
        taxa = tuple(sorted(_names_from_mask(S_mask, tipsB)))
        out[taxa] = clade_probability_msc_dp(B, S_mask)

    return out


# ----------------------------
# Example usage
# ----------------------------
if __name__ == "__main__":
    # A = toytree.tree("(((a,b),(c,d)),(e,f));")
    A = toytree.tree("(((a,c),(b,d)),(e,f));")
    B = toytree.tree("((((a,b):0.7,(c,d):0.7):0.4,(e,f):0.2):0.3);")  # coalescent units

    probs = gene_tree_clade_probs(A, B)
    for clade, p in sorted(probs.items(), key=lambda x: (len(x[0]), x[0])):
        print(clade, p)

    # SPTREE = "(Alternanthera_philoxeroides:0.44798409,(Deeringia_amaranthoides:0.19414575,(Amaranthus_tricolor:0.0283318,((Amaranthus_fimbriatus:0.01043586,(Amaranthus_australis:0.01044097,Amaranthus_cannabinus:0.00931709):0.00774284):0.00099556,((Amaranthus_retroflexus:0.00663625,(Amaranthus_spinosus:0.0117843,(Amaranthus_hybridus_cp1:0.00268167,(Amaranthus_hybridus_cp2:0.00026998,(Amaranthus_caudatus:9.1e-07,Amaranthus_cruentus:7.973e-05):0.00019878):0.00184508):0.00406972):0.00163053):0.01313138,(Amaranthus_greggii:0.00890237,(Amaranthus_acanthochiton:0.00843022,((Amaranthus_floridanus:0.00101728,(Amaranthus_arenicola:0.00086006,Amaranthus_tuberculatus:0.00251385):9.1e-07):0.00471167,(Amaranthus_pumilus:0.00668091,(Amaranthus_palmeri:0.00079119,Amaranthus_watsonii:0.00277269):0.00304054):0.00274509):0.00023663):0.00184292):0.00609605):0.01011877):0.00477752):0.31228773):0.10280971);"
    # GTREE = """..."""
