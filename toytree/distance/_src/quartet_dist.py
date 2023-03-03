#!/usr/bin/env python

"""
Computation of similarity metrics based on quartet-based methods.
Reference: Martin Smith, `Tree Similarity Metrics`.

"""

from typing import Iterator, Tuple, TypeVar, Set
import itertools
import pandas as pd
import numpy as np
import toytree


ToyTree = TypeVar("ToyTree")


################################################################
    # Enumerating all quartets - resolved and unresolved
################################################################

def get_all_quartets(tree: ToyTree) -> Iterator[Tuple[str]]:
    """..."""
    for qrt in itertools.combinations(sorted(tree.get_tip_labels()), 4):
        yield qrt

def get_n_quartets(tree: ToyTree) -> int:
    """..."""
    return sum(1 for i in get_all_quartets(tree))

# To get all resolved quartets, see toytree.enumeration
# e.g. tree = toytree.rtree.unittree(7, seed=123)
#      qrt_resolved = tree.iter_quartets(collapse=True)

def get_n_resolved_quartets(tree: ToyTree) -> int:
    """..."""
    return sum(1 for i in list(sorted(toytree.enumeration.iter_quartets(tree, collapse=True))))


################################################################
    # Computing Tree Similarity Metrics based on Quartets

    # Distinguishing between resolved vs. unresolved quartets
    # Using sorting order to determine whether quartets are
    # resolved in the same way.

    # All Tree Similarity Metrics based on Quartets revolve
    # around the following terms:

    # N = 2*Q
    # Q = Total possible quartets
    # S = Resolved in the same way between the two trees
    # D = Resolved differently between the two trees
    # R1 = Unresolved in tree 1, resolved in tree 2
    # R2 = Unresolved in tree 2, resolved in tree1
    # U = unresolved in both trees

    # Note: Computing differences = 1 - similarity
################################################################

def get_sorting_order(qrt: Iterator[Set[str]]) -> int:
    """
    Determine sorting order for each quartet by finding min value of quartet
    and then finding its respective pair's index number and tip name in the set.
    """
    # use min to deal with alphanumeric values
    amin = min(qrt)
    qqq = list(qrt)
    order = qqq.index(amin)

    if order == 0:
        out_order = 1
    elif order == 1:
        out_order = 0
    elif order == 2:
        out_order = 3
    elif order == 3:
        out_order = 2
    out_val = qqq[out_order]
    return out_order, out_val

def iter_quartet_resolutions(tree: ToyTree) -> Iterator[Tuple]:
    """
    Get all resolved quartets, determine sorting order,
    then internally sort each resolved quartet to match
    order of the all possible quartets generated via
    itertools combinations.
    """
    # get all resolved quartets
    for qrt in tree.iter_quartets(collapse=True):
        # record sorting order of resolved quartet
        res = get_sorting_order(qrt)
        # internally sort resolved quartet to match itertools combinations (loses sorting order)
        sorted_qrt = tuple(sorted(qrt))
        # return tuple with sorted qrt and sorting order
        yield sorted_qrt, res

def get_iter_quartet_df(tree: ToyTree) -> pd.DataFrame:
    """
    Create data frame to record:
    1) Quartet set - four taxon subtrees stored as a set
    2) Resolution - boolean (True or False)
    3) Sorting order - 0, 1, 2, or 3
    """
    # get all possible resolved qrts with resolution
    all_qrt_with_res = sorted(iter_quartet_resolutions(tree))

    # get all possible quartets
    qrt1 = list(sorted(get_all_quartets(tree)))

    # define output data frame
    # create empty data frame with default values, fill later
    similarity_quartet_df = pd.DataFrame(data= np.zeros(shape=(len(qrt1), 3)),
                                         columns=['quartet_set', 'resolved', 'sorting_order'])
    similarity_quartet_df['resolved'] = False
    similarity_quartet_df['sorting_order'] = None


    # fill quartet_set column with all possible quartets
    similarity_quartet_df['quartet_set'] = qrt1

    # iterate over each quartet
    # all possible quartets
    iq1 = iter(qrt1)
    # all resolved quartets with sorting order
    iq2 = iter(all_qrt_with_res)

    counter = 0
    qrt_l1 = next(iq1)
    qrt_l2 = next(iq2)

    while 1:
        try:
            # check if quartet is among resolved quartets
            if qrt_l1 == qrt_l2[0]:
                # if True, then record resolved = True and sorting order
                similarity_quartet_df.loc[counter, 'resolved'] = True
                similarity_quartet_df.loc[counter, 'sorting_order'] = str(qrt_l2[1])
                qrt_l1 = next(iq1)
                qrt_l2 = next(iq2)
            else:
                # if False, then advance to the next quartet
                qrt_l1 = next(iq1)
        except StopIteration:
            break
        # advance counter each time
        counter += 1

    return similarity_quartet_df

def get_iter_quartet_metrics(
    tree1_df: pd.DataFrame,
    tree2_df: pd.DataFrame,
    metric: str) -> int:
    """
    Different ways to compute similarity metrics based on
    Quartet Methods according to Martin Smith's 'Quartets' (2020) package
    """

    intersection_resolved_qrt_s = 0
    resolved_diff_qrt1_qrt2_d = 0
    resolved_qrt1_not_qrt2_r1 = 0
    resolved_qrt2_not_qrt1_r2 = 0
    intersection_unresolved_qrt_u = 0

    # compute Q = total possible number of quartets
    total_possible_qrt_q = tree1_df.shape[0]

    # iterate through each row of the two data frames
    for idx in range(0, tree1_df.shape[0]):
        df1_status = tree1_df.iloc[idx, 1]
        df1_res = tree1_df.iloc[idx, 2]
        df2_status = tree2_df.iloc[idx, 1]
        df2_res = tree2_df.iloc[idx, 2]

        # compute S = total number of quartets resolved in the same way in both trees
        # Resolved = True, same sorting order
        # df1 status = df2 status = True AND df1_res = df2_res sorting order is the same
        if df1_status == True and df2_status == True and df1_res == df2_res:
            intersection_resolved_qrt_s += 1

        # compute U = number of quartets unresolved in both trees
        # Resolved = False for both
        # df2 status = False and df1 status = False
        if df1_status == False and df2_status == False:
            intersection_unresolved_qrt_u += 1

        # compute R1 = number of quartets unresolved in tree1, but resolved in tree2
        # df1 status = False, df2 status = True
        if df1_status == False and df2_status == True:
            resolved_qrt2_not_qrt1_r2 += 1

        # compute R2 = number of quartets unresolved in tree2, but resolved in tree1
        # df2 status= False, df1 status = True
        if df1_status == True and df2_status == False:
            resolved_qrt1_not_qrt2_r1 += 1

        # compute D = symmetric difference of resolved quartets
        # Resolved in both trees, but resolved differently
        # df1 status = True, df2 status = True AND sorting order diff, df1_res[2] != df1_res[2]
        if df1_status == True and df2_status == True and df1_res != df2_res:
            resolved_diff_qrt1_qrt2_d += 1

    # compute N = S + D + R1 + R2 + U
    total_qrts_n = (intersection_resolved_qrt_s + resolved_diff_qrt1_qrt2_d +
        resolved_qrt1_not_qrt2_r1 + resolved_qrt2_not_qrt1_r2 + intersection_unresolved_qrt_u)


        # output stat
    if metric == "general":
        print("N: {}  2*Q".format(2*total_possible_qrt_q))
        print("Q: {}  Total possible quartets".format(total_possible_qrt_q))
        print("S: {}  Resolved in the same way between the two trees".format(
            intersection_resolved_qrt_s))
        print("D: {}   Resolved differently between the two trees".format(
            resolved_diff_qrt1_qrt2_d))
        print("R1: {}  Unresolved in tree 1, resolved in tree 2".format(resolved_qrt2_not_qrt1_r2))
        print("R2: {}  Unresolved in tree 2, resolved in tree 1".format(resolved_qrt1_not_qrt2_r1))
        print("U: {}   Unresolved in both trees".format(intersection_unresolved_qrt_u))
        stat = " "
        metric = " "
    elif metric == "do_not_conflict":
        stat = (intersection_resolved_qrt_s + resolved_qrt1_not_qrt2_r1 +
            resolved_qrt2_not_qrt1_r2 + intersection_unresolved_qrt_u)/(total_qrts_n)
    elif metric == "explicitly_agree":
        stat = intersection_resolved_qrt_s/(total_qrts_n)
    elif metric == "strict_joint_assertions":
        stat = intersection_resolved_qrt_s/(intersection_resolved_qrt_s+resolved_diff_qrt1_qrt2_d)
    elif metric == "semistrict_joint_assertions":
        stat = intersection_resolved_qrt_s/(intersection_resolved_qrt_s+resolved_diff_qrt1_qrt2_d
            +intersection_unresolved_qrt_u)
    elif metric == "steel_and_penny":
        stat = (intersection_resolved_qrt_s+intersection_unresolved_qrt_u)/(total_qrts_n)
    elif metric == "symmetric_difference":
        stat = 1 - (((2*resolved_diff_qrt1_qrt2_d)+resolved_qrt1_not_qrt2_r1+
            resolved_qrt2_not_qrt1_r2)/ ((2*resolved_diff_qrt1_qrt2_d)+
            (2*intersection_resolved_qrt_s)+resolved_qrt1_not_qrt2_r1+resolved_qrt2_not_qrt1_r2))
    elif metric == "symmetric_divergence":
        stat = 1 - ((resolved_diff_qrt1_qrt2_d+resolved_diff_qrt1_qrt2_d+resolved_qrt1_not_qrt2_r1+
            resolved_qrt2_not_qrt1_r2)/ (2*total_possible_qrt_q))
    elif metric == "similarity_to_reference":
        stat = (intersection_resolved_qrt_s + (resolved_qrt1_not_qrt2_r1 +
            resolved_qrt2_not_qrt1_r2 + intersection_unresolved_qrt_u)/3)/ total_possible_qrt_q
    elif metric == "marczewski_steinhaus":
        stat = 1 - ((2*resolved_diff_qrt1_qrt2_d) + resolved_qrt1_not_qrt2_r1 +
            resolved_qrt2_not_qrt1_r2)/((2*resolved_diff_qrt1_qrt2_d) +
            intersection_resolved_qrt_s + resolved_qrt1_not_qrt2_r1 +
            resolved_qrt2_not_qrt1_r2)
    else:
        print("Metric not recognized")
    
    return stat




if __name__ == "__main__":

    TREE1 = toytree.rtree.unittree(7, seed=123)
    TREE2 = toytree.rtree.unittree(7, seed=321)
    TREE2 = TREE2.mod.collapse_nodes(3, 7, 6)

    #TREE1 = toytree.rtree.unittree(20, seed=123)
    #TREE2 = toytree.rtree.unittree(20, seed=321)
    #TREE2 = TREE2.mod.collapse_nodes(13, 17, 16)

    treedf1 = get_iter_quartet_df(TREE1)
    treedf2 = get_iter_quartet_df(TREE2)

    print(treedf1)
    print(treedf2)

    get_iter_quartet_metrics(treedf1, treedf2, "general")
    get_iter_quartet_metrics(treedf1, treedf2, "do_not_conflict")
    get_iter_quartet_metrics(treedf1, treedf2, "explicitly_agree")
    get_iter_quartet_metrics(treedf1, treedf2, "strict_joint_assertions")
    get_iter_quartet_metrics(treedf1, treedf2, "semistrict_joint_assertions")
    get_iter_quartet_metrics(treedf1, treedf2, "symmetric_difference")
    get_iter_quartet_metrics(treedf1, treedf2, "marczewski_steinhaus")
    get_iter_quartet_metrics(treedf1, treedf2, "steel_and_penny")
    get_iter_quartet_metrics(treedf1, treedf2, "symmetric_divergence")
    get_iter_quartet_metrics(treedf1, treedf2, "similarity_to_reference")
