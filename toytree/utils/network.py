#!/usr/bin/env python

"""Network parsing utilities.

Currently developed for parsing, analyzing and plotting network
output files in newick-like format produced by the SNAQ program in
PhyloNetworks.

Toytree default is to draw networks in "majortree" mode.

Extended newick network format
------------------------------
Basic network, e.g., used by dendroscope.
>>> ((r3,(r2,(r1, #HX)),(r0)#HX);
This indicates an admix edges from r1 -> r0. The #HX node is the
source, and the #HX node label is the destination. This example shows
only the edge, but not its proportions, or edge lengths indicating
where the admix edge starts or stops at each end.

With admixture magnitudes (termed gamma values under some models).
>>> ((r3,(r2, (r1, #HX:::0.1)),(r0)#HX);

With admixture magnitudes and edge lengths.
>>>

This is what it looks like when more than one admix from a node:
>>> ((A,#H1),B)
>>> (((A,#H1),H2),B)

This is what it looks like when more than one admix to a node:
>>> (A)#H1
>>> (A)#H1#H2  (???)

Examples
---------
>>> NET = "(r1,(r2,(r3,(r4,#H6):10.0):1.949048825686914):10.0,(r0)#H6);""
>>> toytree.utils.network.parse_networks(NET)
"""

from typing import Union, Tuple, List
from pathlib import Path
import re
from loguru import logger
import toytree
from toytree.io.src.utils import replace_whitespace

logger = logger.bind(name="toytree")


class Network:
    """Child class of ToyTree that stores and draws network edges.

    A network object can be used to draw networks, to calculate or
    report statistics on a network, and to extract minor or major
    trees from a network (as ToyTree objects).

    Algorithm to traverse nodes of a network in order... could still
    use the same traversals that trace the major or minor tree to visit
    each node, but another traversal may be available that would also
    visit nodes connected by an admix edge sooner...
    """
    def __init__(self, network: Union[str, Path]):
        self.network = network
        # tree, admix = parse_network(net, disconnect=disconnect)
        # super().__init__(tree, *args, **kwargs)
        # self.admix = admix

    # def ... , disconnect: bool = True, **kwargs):

    def add_edge(self) -> toytree.ToyTree:
        """Return modified Network with a new degree-3 edge added."""

    def remove_edge(self) -> toytree.ToyTree:
        """Return modified Network with a degree-3 edge removed."""

    def get_major_tree(self) -> toytree.ToyTree:
        """Return the major tree..."""

    def get_admixture_edges(self) -> Tuple:
        """Return Tuple with list of admixture edges..."""

    def write(self):
        """Write network in extended format..."""

    def root(self):
        """raise rootMisMatchError if direction doesn't work..."""


class NetworkToMajorTree:
    """Class with functions to parse (ToyTree, admix_edges) from net.

    ...
    """
    def __init__(self, net: Union[str, Path], disconnect=True):
        self.net: str = self._get_network_as_newick_str(net)
        """: Input network as newick string (parsed from str or Path)."""
        self.tree: toytree.ToyTree = None
        """: The major tree."""
        self.admix: List[Tuple] = []
        """: List of admixture edges."""
        self.disconnect: bool = disconnect
        """: ..."""

    def _get_network_as_newick_str(self, net: Union[str, Path]) -> str:
        """Parse network newick from file or '[network];...details' string."""
        # if net is a file then read the first line
        if ";" not in net:
            if not net.exists():
                raise IOError("input type is not a file or newick (no ; ending).")
            with open(net, 'rt', encoding="utf-8") as infile:
                net = infile.readline()
        else:
            # trim off loglik and anything after it (TODO: keep loglik)
            if ";" in net:
                net = net.split(";")[0] + ';'
        # strip whitespace
        net = replace_whitespace(net)
        # net = WHITE_SPACE.sub("", net)
        return net

    def _set_tree_with_admix_as_node_labels(self) -> toytree.ToyTree:
        """Return a ToyTree parsed from network newick with gamma nodes.

        Admix nodes are indicated by #[name]:[dist]::[gamma] where dist
        will be absent for tip nodes but present for internal nodes. We
        modify this to be #[name-with-gamma]:dist so we can still use
        the same tree parser and then modify the tree afterwards to
        extract the major tree and minor admix edges.
        """
        string = self.net
        # tip nodes replace L:::G -> L-G
        re0 = re.compile(r"(#\w+):::([\d.]+)")
        # internal nodes replace L:D::G -> L-G:D
        re1 = re.compile(r"(#\w+):([\d.]+)::([\d.]+)")
        string = re0.sub(r"\1-gamma-\2", string)
        string = re1.sub(r"\1-gamma-\3:\2", string)
        self.tree = toytree.tree(string)

    def _pseudo_unroot(self) -> toytree.ToyTree:
        """Return unrooted tree re-ordered for display purposes.

        Tree is rooted tree on an edge that does not split a ...
        """
        # store a list of all nodes the tree *could* be rooted on.
        opt = self.tree.get_nodes()
        for node in self.tree.traverse("postorder"):
            if node.name.startswith("#H"):
                for desc in node.get_descendants():
                    if desc in opt:
                        opt.remove(desc)
        logger.trace(f"can root on {opt}")
        return self.tree.root(opt[0]).mod.ladderize().mod.unroot()

    def get_major_tree_and_admix_edges(self) -> Tuple:
        """..."""
        self._set_tree_with_admix_as_node_labels()
        self.tree._draw_browser(ts='s', layout='unr', width=700, node_labels="name", node_colors="pink")
        self.tree = self._pseudo_unroot()
        self.tree._draw_browser(ts='s', width=500, node_labels="idx", node_colors="pink", tmpdir="~")

        # restart traversal after each pair of nodes is fixed.
        while 1:
            try:
                hnodes = self.tree.get_nodes("~#H*")
                hnodes = sorted(hnodes, key=lambda x: x.name)
            except ValueError:
                self.tree.mod.remove_unary_nodes(inplace=True)
                logger.debug(f"finished: {self.admix}")
                return self.tree, self.admix

            # order as [dest, src] i.e., [node-label, tip-node] and get gamma
            if hnodes[0].is_leaf():
                hnodes = [hnodes[1], hnodes[0]]
            if "-gamma-" in hnodes[1].name:
                prop = hnodes[1].name.rsplit("-gamma-", 1)[1]
            else:
                prop = 0.5
            logger.trace(f"hnodes: {hnodes}")

            # remove the tip node representing a src
            logger.debug(f"deleting minor node: {hnodes[1].name} {hnodes[1].idx}")
            desc1 = tuple(hnodes[1]._up.get_leaf_names())
            hnodes[1]._delete()
            desc1 = [i for i in desc1 if not i.startswith("#H")]
            logger.trace(f"desc1: {desc1}")

            # remove internal node representing admix destination
            logger.debug(f"deleting major node: {hnodes[0].name} {hnodes[0].idx}")
            desc0 = tuple(hnodes[0].get_leaf_names())
            desc0 = [i for i in desc0 if not i.startswith("#H")]
            hnodes[0]._delete()
            logger.trace(f"desc0: {desc0}")

            self.tree._update()
            self.admix.append((desc0, desc1, 0.5, {}, f"{float(prop):.3g}"))


def parse_network(net: Union[str, Path], disconnect=True):
    """Parse a network file to extract a major topology and admix dict.

    This leaves the hybrid nodes in the tree and labels each with
    .name="H{int}" and .gamma={float}.
    """
    # if net is a file then read the first line
    if ";" not in net:
        if not net.exists():
            raise IOError("input type is not a file or newick (no ; ending).")
        with open(net, 'rt', encoding="utf-8") as infile:
            net = infile.readline()
    else:
        # trim off loglik and anything after it (TODO: keep loglik)
        if ";" in net:
            net = net.split(";")[0] + ';'

    # sub :xxx:: to be ::: b/c I don't care about admix edge bls FOR NOW.
    net = re.sub(r":\d.\w*::", ":::", net)
    print(net)

    # change H nodes to be internal node labels rather than tip nodes.
    while ",#" in net:
        pre, post = net.split(",#", 1)
        npre, npost = post.split(")", 1)
        newpre = npre.split(":")[0] + "-" + npre.split(":")[-1]
        net = pre + ")#" + newpre + npost
    net = net.replace(":::", "-")
    print(net)

    # parse cleaned newick and set empty gamma on all nodes
    net = toytree.tree(net)#, tree_format=1)
    print(net.get_node_data())

    # store admix data
    admix = {}

    # if not rooted choose any non-H root
    if not net.is_rooted():
        net = net.root(
            [i for i in net.get_tip_labels() if not i.startswith("#H")][0]
        )

    # Traverse tree to find hybrid nodes. If a hybrid node is labeled as a
    # distinct branch in the tree then it is dropped from the tree and
    for node in net.traverse("postorder"):

        # find hybrid nodes as internal nchild=1, or external with H in name
        if (len(node.children) == 1) or node.name.startswith("#H"):

            # assign name and gamma to hybrid nodes
            print(node.name)
            aname, aprop = node.name.split("-")
            aname = aname.lstrip("#")
            node.name = aname

            # assign hybrid to closest nodes up and down from edge
            # node.children[0].hybrid = int(aname[1:])
            # node.gamma = round(float(aprop), 3)
            # node.up.hybrid = int(aname[1:])

            # if root is a hybrid edge (ugh)
            if node.up is None:
                small, big = sorted(node.children, key=len)
                root = toytree.Node(name='root')
                node.children = [small]
                small.up = node
                node.up = root
                big.up = root
                root.children = [node, big]
                net.treenode = root

            # disconnect node by connecting children to parent
            if disconnect:

                # if tip is a hybrid
                if not node.children:
                    # get sister node
                    sister = [i for i in node.up.children if i != node][0]

                    # connect sister to gparent
                    sister.up = node.up.up
                    node.up.up._remove_child(node.up)
                    node.up.up._add_child(sister)

                # if hybrid is internal
                else:
                    node.up._remove_child(node)
                    for child in node.children:
                        child._up = node.up
                        node.up._add_child(child)

            # store admix data by descendants but remove hybrid tips
            desc = node.get_leaf_names()
            if aname in desc:
                desc = [i for i in node.up.get_leaf_names() if i != aname]
            desc = [i for i in desc if not i.startswith("#H")]

            # put this node into admix
            if aname not in admix:
                admix[aname] = (desc, aprop)

            # matching edge in admix, no arrange into correct order by minor
            else:
                # this is the minor edge
                if aprop < admix[aname][1]:
                    admix[aname] = (
                        admix[aname][0],
                        desc,
                        0.5,
                        {},
                        str(round(float(aprop), 3)),
                    )

                # this is the major edge
                else:
                    admix[aname] = (
                        desc,
                        admix[aname][0],
                        0.5,
                        {},
                        str(round(float(admix[aname][1]), 3)),
                    )

    # update coords needed if node disconnection is turned back on.
    # net._coords.update()
    net._update()
    net = net.mod.ladderize()
    return net, admix

# def test3A():
#     net = "(((r0,#H1:::0.9),r2),(r3,(r4,#H1:::0.1)));"
#     return parse_network(net)

def test3A():
    """No gamma values."""
    net = "(((r0,#H1),r2),(((r3,r4))#H1));"
    parse = NetworkToMajorTree(net)
    tree, admix = parse.get_major_tree_and_admix_edges()
    return tree, admix

def test3B():
    """Major tree has higher gamma value.
    >>> ((r0,r2),(r3,r4));  [(r0,(r3, r4), 0.5)]
    """
    # net = "(((r0,r1),#HX),(((r2,r3))#HX,r4),r5);"
    # net = "(C,D,((O,(E,#H7:::0.196):0.314):0.664,(((A1,A2))#H7:::0.804,B):10.0):10.0);"
    # net = "(C,D,((O,(E,#H7)),(B,(A)#H7)));"
    # net = "(C,D,((O,(E,#H7:::0.49)),(B,(A)#H7:::0.51)));"
    # net = "(C,D,((O,(E,#H7:::0.51)),(B,(A)#H7:::0.49)));"
    net = "((r5,(r4,(r3,((r2,(r0,r1):4.268188213461936):2.9023407392778653)#H9:10.0::0.7093477022612464):3.2038798063864555):10.0):10.0,r6,(r7,#H9:0.0::0.2906522977387535):10.0);"
    # net = "(C,D,((O,(E,#H7:::0.195):0.313):0.664,(B,(A)#H7:::0.804):10.0):10.0);"
    parse = NetworkToMajorTree(net)
    tree, admix = parse.get_major_tree_and_admix_edges()
    return tree, admix

def test3C():
    """...
    >>> ((r0,r2),(r3,r4));  [((r3, r4),r0, 0.5)]
    """
    NET = "(((r0,#H1:::0.9),r2),(r3,r4)#H1:::0.1);"

def test_am_2():
    net = """(quitensis,caudatus,((hybridus,((cruentus,((((retroflexus,wrightii):3.177882128684601,powellii):1.0960348982483923,acutilobus):1.196100087172878,((((((((tuberculatus,arenicola):0.6109501450803072,pumilus):0.4760189778806285,cannabinus):2.412166114595602,(((albus,blitoides):3.721391761165372,(viridis,(blitum,tricolor):1.0147162921429302):3.1242417846101658):0.8709001073072796,(fimbriatus)#H24:::0.5252749295119973):1.8571548128366557):2.707582965691606,#H24:::0.4747250704880027):1.5826753575568118,(((palmeri,watsonii):0.9398829701307351,spinosus):1.724020571200692)#H26:5.622450726846983::0.7964515993969742):3.198826088104374,(dubius,#H26:0.0005151894132288451::0.20354840060302581):9.999954155584865):0.6322904226943913)#H25:0.49722570736992866::0.7233188613740416):2.5040114155558104):0.47630091121000095,hypochondriacus):0.754444529685924):0.7024345634254702,#H25:2.415867402213081::0.2766811386259585):3.554563433506071);"""
    parse = NetworkToMajorTree(net)
    tree, admix = parse.get_major_tree_and_admix_edges()
    return tree, admix
    # parse = NetworkToMajorTree(NET)
    # return parse
    # return parse_network(NET, disconnect=0)

def test_interactive_3():
    NET = "(r1,(r2,(r3,(r4,#H6):10.0):1.949048825686914):10.0,(r0)#H6);"
    NET = "((r3,(r2,(r1, #HX))),(r0)#HX);"
    parse = NetworkParser(NET)
    # parse_network(NET)


if __name__ == "__main__":

    toytree.set_log_level("TRACE")
    # t0, a0 = test3B()
    NET = "(r1,(r2,(r3,(r4,#H6):10.0):1.949048825686914):10.0,(r0)#H6);"
    # parse_network(NET)
    parser = NetworkToMajorTree(NET)
    tree, edges = parser.get_major_tree_and_admix_edges()
    tree._draw_browser(tmpdir="~", admixture_edges=edges)

    # t0, a0 = test_am_2()
    # # t0 = t0.root("fimbriatus")
    # t0._draw_browser(
    #     ts='s',
    #     width=500, height=800,
    #     node_labels="idx",
    #     use_edge_lengths=True,
    #     admixture_edges=a0,
    # )
