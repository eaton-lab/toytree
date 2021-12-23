#!/usr/bin/env python

"""Parse newick or nexus data to return a ToyTree class instance.

A newick/nexus file/string parser based on the ete3.parser.newick.
Takes as input a string or file that contains one or multiple lines
that contain newick strings. Lines that do not contain newick strings
are ignored, unless the #NEXUS is in the header in which case the
'translate' and 'trees' blocks are parsed.

Support for 'extended' NHX format for additional metadata, and
variants of this, such as mrbayes format.

Classes:
    - FastTreeParse
    - TreeParser
    - Newick2TreeNode
    - NexusParser
    - Matchers
    - FastNewick2TreeNode
"""

from typing import List, Union
import os
import re
import requests
from pathlib import Path
from loguru import logger
from toytree.core.node import Node
from toytree.utils import NewickError
from toytree.utils.src.globals import NW_FORMAT

from toytree.io.src.nexus_io import get_newicks_and_translation_from_nexus

logger = logger.bind(name="toytree")

# Regular expressions used for reading newick format
FLOAT_RE = r"\s*[+-]?\d+\.?\d*(?:[eE][-+]\d+)?\s*"
NAME_RE = r"[^():,;]+?"
NHX_RE = r"\[&&NHX:[^\]]*\]"

# for removing white_ space from newicks
WHITE_SPACE = re.compile(r"[\n\r\t ]+")


class BaseParser:
    """Base class for Parser classes."""
    def __init__(self, data: Union[str, bytes, Path]):
        self.data = data
        self.treenodes: List[Node] = []

class NewickParser(BaseParser):
    """Class for parsing newick input data to Node instances.

    Parsing newick requires a tree_format integer type to indicate
    what type of data is present (e.g., Node support values, names,
    other metadata).

    Note
    ----
    This class parses a single newick to a single TreeNode. See the
    ... class for parsing multi-newick string or file to multiple
    Node instances.

    Examples
    --------
    >>> data = "((a,(b,c));"
    >>> tool = NewickParser(data)
    >>> print(tool.treenodes)
    """
    def __init__(self, data, tree_format: int):
        super().__init__(data)
        self.root = Node()
        self.current_node = self.root
        self.current_parent = None
        self.tree_format = tree_format

        # run the core functions
        self.check_parentheses()
        self.standardize()
        self.run()

    def check_parentheses(self):
        """Check that tree nesting structure is valid."""
        assert self.data.count("(") == self.data.count(")"), (
            "Parentheses do not match. Broken tree data.")

    # TODO: is this necessary?
    def standardize(self):
        """Standardize newick to remove bad characters."""

        # remove white_ spaces and separators
        self.data = WHITE_SPACE.sub("", self.data)

    def run(self):
        """Extract Node and metadata from nesting strings."""

        # split on parentheses open
        for chunk in self.data.split("(")[1:]:

            # add child to make this node a parent
            self.current_node = Node()
            if self.current_parent is None:
                self.current_parent = self.root
            else:
                self.current_parent._add_child(new_node)

            # get all parenth endings from this parenth start
            subchunks = (ch.strip() for ch in chunk.split(","))
            print(subchunks)
            if subchunks[-1] != '' and not subchunks[-1].endswith(';'):
                raise NewickError(
                    'Broken newick structure at: {}'.format(chunk))

class Newick2TreeNode:
    """Parse a newick str to a TreeNode object."""
    def __init__(self, data, fmt=0):
        self.data = data
        self.root = Node()
        self.current_node = self.root
        self.current_parent = None
        self.fmt = fmt
        self.cleanup_data()

    def cleanup_data(self):
        """
        Removes characters from newick that should not be in names or
        attributes, such as curly brackets, parentheses, etc, and
        replaces them with square brackets.
        """
        # check parentheses
        if self.data.count('(') != self.data.count(')'):
            raise NewickError('Parentheses do not match. Broken tree data.')

        # remove white_ spaces and separators
        self.data = WHITE_SPACE.sub("", self.data)

        # mrbayes format terrible formatting hacks--------
        if self.fmt == 10:

            # convert bracket markers to NHX format
            self.data = self.data.replace("[&", "[&&NHX:")

            # replace commas inside feature strings with dashes
            ns = ""
            for chunk in self.data.split("{"):
                if "}" in chunk:
                    pre, post = chunk.split("}", 1)
                    pre = pre.replace(",", "-")
                    ns += "{" + pre + "}" + post
                else:
                    ns += chunk
            self.data = ns

            # replace parentheses inside brackets with curly braces
            ns = ""
            for chunk in self.data.split("["):
                if "]" in chunk:
                    pre, post = chunk.split("]", 1)
                    pre = pre.replace("(", "{")
                    pre = pre.replace(")", "}")
                    pre = pre.replace(",", ":")
                    pre = pre.replace('"', "")
                    pre = pre.replace("'", "")
                    ns += "[" + pre + "]" + post
                else:
                    ns += chunk
            self.data = ns

    def newick_from_string(self):
        """Reads a newick string in the New Hampshire format.

        """
        # split on parentheses to traverse hierarchical tree structure
        for chunk in self.data.split("(")[1:]:
            # add child to make current node a parent.
            self.current_parent = (
                self.root if self.current_parent is None else
                self.current_parent.add_child()
            )

            # get all parenth endings from this parenth start
            subchunks = [ch.strip() for ch in chunk.split(",")]
            if subchunks[-1] != '' and not subchunks[-1].endswith(';'):
                raise NewickError(
                    'Broken newick structure at: {}'.format(chunk))

            # Every closing parenthesis will close a node and go up one level.
            for idx, leaf in enumerate(subchunks):
                if leaf.strip() == '' and idx == len(subchunks) - 1:
                    continue
                closing_nodes = leaf.split(")")

                # parse features and apply to the node object
                self.apply_node_data(closing_nodes[0], "leaf")

                # next contain closing nodes and data about the internal nodes.
                if len(closing_nodes) > 1:
                    for closing_internal in closing_nodes[1:]:
                        closing_internal = closing_internal.rstrip(";")
                        # read internal node data and go up one level
                        self.apply_node_data(closing_internal, "internal")
                        self.current_parent = self.current_parent.up
        return self.root



    def apply_node_data(self, subnw, node_type):
        """Builds a tree of connected Nodes saved as .root.
        """
        if node_type in ("leaf", "single"):
            self.current_node = Node()
            self.current_parent._add_child(self.current_node)
            # self.current_node = self.current_parent.add_child()
        else:
            self.current_node = self.current_parent

        # if no feature data
        subnw = subnw.strip()
        if not subnw:
            return

        # load matcher junk
        c1, c2, cv1, cv2, match = MATCHER[self.fmt].type[node_type]

        # if beast or mb then combine brackets
        if self.fmt == 10:
            if "]:" not in subnw:
                node, edge = subnw.split("]", 1)
                subnw = node + "]:0.0" + edge
            node, edge = subnw.split("]:")
            npre, npost = node.split("[")

            # mrbayes mode: (a[&a:1,b:2]:0.1[&c:10])
            try:
                epre, epost = edge.split("[")
                subnw = "{}:{}[&&NHX:{}".format(
                    npre, epre, ":".join([npost[6:], epost[6:]]))

            # BEAST mode: (a[&a:1,b:2,c:10]:0.1)
            except ValueError:
                subnw = "{}:{}[&&NHX:{}]".format(npre, edge, npost[6:])

        # look for node features
        data = re.match(match, subnw)

        # if there are node features then add them to this node
        if data:
            data = data.groups()

            # data should not be empty
            if all(i is None for i in data):
                raise NewickError(
                    "Unexpected newick format {}".format(subnw))

            # node has a name
            if (data[0] is not None) and (data[0] != ''):
                setattr(self.current_node, c1, cv1(data[0]))
                # self.current_node.add_feature(c1, cv1(data[0]))

            if (data[1] is not None) and (data[1] != ''):
                setattr(self.current_node, c2, cv2[data[1][1:]])
                # self.current_node.add_feature(c2, cv2(data[1][1:]))

            if (data[2] is not None) and data[2].startswith("[&&NHX"):
                fdict = parse_nhx(data[2])
                for fname, fvalue in fdict.items():
                    setattr(self.current_node, fname, fvalue)
                    # self.current_node.add_feature(fname, fvalue)
        else:
            raise NewickError("Unexpected newick format {}".format(subnw))




class FastTreeParser:
    """The simplest and fastest newick parser.

    A less flexible but faster newick parser for performance
    sensitive apps. Only supports newick string input in format 0.
    """
    def __init__(self, newick, tree_format):
        self.data = newick
        extractor = FastNewick2TreeNode(self.data, tree_format)
        self.treenode = extractor.newick_from_string()


class TreeParser:
    """Flexible tree data parsing class.

    """
    def __init__(
        self,
        intree: Union[str,bytes,Path],
        tree_format=0,
        multitree=False,
        debug=False,
        ):
        """Parse data from string or file.

        Reads input as a string or file, figures out format and parses it.
        Formats 0-10 are newick formats supported by ete3.
        Format 11 is nexus format from mrbayes.

        Result in .treenodes contains one or more Nodes, representing
        the root of one or more trees.
        """
        # the input file/stream and the loaded data
        self.intree = intree
        self.data = None
        self.debug = debug

        # the tree_format and parsed tree string from data
        self.fmt = tree_format
        self.multitree = multitree
        self.newick = ""

        # returned result: 1 tree for Toytree multiple trees for MultiTrees
        self.treenodes = []

        # newick translation dictionary
        self.tdict = {}

        # compiled re matchers for this tree format type
        self.matcher = MATCHER[self.fmt]

        # parse intree
        if not self.debug:
            self._run()

    def _run(self):
        # no input data
        if not self.intree:
            self.treenodes = [Node()]
            logger.warning("Empty tree: No data present.")
        # get newick from data and test newick structure
        else:
            # read data input by lines to .data
            self.get_data_from_intree()

            # check for NEXUS wrappings and update .data for newick strings
            self.parse_nexus()

            # raise warnings if tree_format doesn't seem right for data
            self.warn_about_format()

            # parse newick strings to treenodes list
            self.get_treenodes()

            # apply names from tdict
            self.apply_name_translation()

    def warn_about_format(self):
        """Logs a warning if data does not fit the selected format."""
        if "[&&NHX" not in self.data[0]:
            if ("[&" in self.data[0]) & (self.fmt != 10):
                logger.warning(
                    "Warning: data looks like tree_format=10 (mrbayes-like)")

    def get_data_from_intree(self):
        """Parse input and store in .data.

        Load *data* from a file or string and return as a list of
        strings. The data contents could be one newick string; a
        multiline NEXUS format for one tree; multiple newick strings
        on multiple lines; or multiple newick strings in a multiline
        NEXUS format. In any case, we will read in the data as a list
        of lines.
        """
        # load string: filename or data stream
        if isinstance(self.intree, (str, bytes)):

            # strip it
            self.intree = self.intree.strip()

            # is a URL: make a list by splitting a string
            if any(i in self.intree for i in ("http://", "https://")):
                response = requests.get(self.intree)
                response.raise_for_status()
                self.data = response.text.strip().split("\n")

            # is a file: read by lines to a list
            elif os.path.exists(self.intree):
                with open(self.intree, 'rU') as indata:
                    self.data = indata.readlines()

            # is a string: make into a list by splitting
            else:
                self.data = self.intree.split("\n")

        # load iterable: iterable of newick strings
        elif isinstance(self.intree, (list, set, tuple)):
            self.data = list(self.intree)

    def parse_nexus(self):
        """If NEXUS header then use NexusParser class to get data"""
        if self.data[0].strip().upper() == "#NEXUS":
            self.data, self.tdict = get_newicks_and_translation_from_nexus(self.data)

    def get_treenodes(self):
        """Call Newick2TreeNode on data string(s).

        Checks the format of intree nex/nwk for extra features
        """
        if not self.multitree:
            # get TreeNodes from Newick
            extractor = Newick2TreeNode(self.data[0].strip(), fmt=self.fmt)

            # extract one tree
            self.treenodes.append(extractor.newick_from_string())

        else:
            for tre in self.data:
                # get TreeNodes from Newick
                extractor = Newick2TreeNode(tre.strip(), fmt=self.fmt)

                # extract one tree
                self.treenodes.append(extractor.newick_from_string())

    def apply_name_translation(self):
        """If a translation dict was parsed then apply it on names.
        """
        if self.tdict:
            for tree in self.treenodes:
                for node in tree.traverse():
                    if node.name in self.tdict:
                        node.name = self.tdict[node.name]


class Newick2TreeNode:
    """Parse a newick str to a TreeNode object."""
    def __init__(self, data, fmt=0):
        self.data = data
        self.root = Node()
        self.current_node = self.root
        self.current_parent = None
        self.fmt = fmt
        self.cleanup_data()

    def cleanup_data(self):
        """
        Removes characters from newick that should not be in names or
        attributes, such as curly brackets, parentheses, etc, and
        replaces them with square brackets.
        """
        # check parentheses
        if self.data.count('(') != self.data.count(')'):
            raise NewickError('Parentheses do not match. Broken tree data.')

        # remove white_ spaces and separators
        self.data = re.sub(r"[\n\r\t ]+", "", self.data)

        # mrbayes format terrible formatting hacks--------
        if self.fmt == 10:

            # convert bracket markers to NHX format
            self.data = self.data.replace("[&", "[&&NHX:")

            # replace commas inside feature strings with dashes
            ns = ""
            for chunk in self.data.split("{"):
                if "}" in chunk:
                    pre, post = chunk.split("}", 1)
                    pre = pre.replace(",", "-")
                    ns += "{" + pre + "}" + post
                else:
                    ns += chunk
            self.data = ns

            # replace parentheses inside brackets with curly braces
            ns = ""
            for chunk in self.data.split("["):
                if "]" in chunk:
                    pre, post = chunk.split("]", 1)
                    pre = pre.replace("(", "{")
                    pre = pre.replace(")", "}")
                    pre = pre.replace(",", ":")
                    pre = pre.replace('"', "")
                    pre = pre.replace("'", "")
                    ns += "[" + pre + "]" + post
                else:
                    ns += chunk
            self.data = ns

    def newick_from_string(self):
        """Reads a newick string in the New Hampshire format.

        """
        # split on parentheses to traverse hierarchical tree structure
        for chunk in self.data.split("(")[1:]:
            # add child to make this node a parent.
            if self.current_parent is None:
                self.current_parent = self.root 
            else:
                new_node = Node()
                self.current_parent._add_child(new_node)
                self.current_parent = new_node

            # get all parenth endings from this parenth start
            subchunks = [ch.strip() for ch in chunk.split(",")]
            if subchunks[-1] != '' and not subchunks[-1].endswith(';'):
                raise NewickError(
                    'Broken newick structure at: {}'.format(chunk))

            # Every closing parenthesis will close a node and go up one level.
            for idx, leaf in enumerate(subchunks):
                if leaf.strip() == '' and idx == len(subchunks) - 1:
                    continue
                closing_nodes = leaf.split(")")

                # parse features and apply to the node object
                self.apply_node_data(closing_nodes[0], "leaf")

                # next contain closing nodes and data about the internal nodes.
                if len(closing_nodes) > 1:
                    for closing_internal in closing_nodes[1:]:
                        closing_internal = closing_internal.rstrip(";")
                        # read internal node data and go up one level
                        self.apply_node_data(closing_internal, "internal")
                        self.current_parent = self.current_parent.up
        return self.root

    def apply_node_data(self, subnw, node_type):
        """Builds a tree of connected Nodes saved as .root.
        """
        if node_type in ("leaf", "single"):
            self.current_node = Node()
            self.current_parent._add_child(self.current_node)
            # self.current_node = self.current_parent.add_child()
        else:
            self.current_node = self.current_parent

        # if no feature data
        subnw = subnw.strip()
        if not subnw:
            return

        # load matcher junk
        c1, c2, cv1, cv2, match = MATCHER[self.fmt].type[node_type]

        # if beast or mb then combine brackets
        if self.fmt == 10:
            if "]:" not in subnw:
                node, edge = subnw.split("]", 1)
                subnw = node + "]:0.0" + edge
            node, edge = subnw.split("]:")
            npre, npost = node.split("[")

            # mrbayes mode: (a[&a:1,b:2]:0.1[&c:10])
            try:
                epre, epost = edge.split("[")
                subnw = "{}:{}[&&NHX:{}".format(
                    npre, epre, ":".join([npost[6:], epost[6:]]))

            # BEAST mode: (a[&a:1,b:2,c:10]:0.1)
            except ValueError:
                subnw = "{}:{}[&&NHX:{}]".format(npre, edge, npost[6:])

        # look for node features
        data = re.match(match, subnw)

        # if there are node features then add them to this node
        if data:
            data = data.groups()

            # data should not be empty
            if all(i is None for i in data):
                raise NewickError(
                    "Unexpected newick format {}".format(subnw))

            # node has a name
            if (data[0] is not None) and (data[0] != ''):
                setattr(self.current_node, c1, cv1(data[0]))
                # self.current_node.add_feature(c1, cv1(data[0]))

            if (data[1] is not None) and (data[1] != ''):
                if c2 == "dist":
                    c2 = "_dist"
                setattr(self.current_node, c2, cv2(data[1][1:]))
                # self.current_node.add_feature(c2, cv2(data[1][1:]))

            if (data[2] is not None) and data[2].startswith("[&&NHX"):
                fdict = parse_nhx(data[2])
                for fname, fvalue in fdict.items():
                    setattr(self.current_node, fname, fvalue)
                    # self.current_node.add_feature(fname, fvalue)
        else:
            raise NewickError("Unexpected newick format {}".format(subnw))




# re matchers should all be compiled on toytree init
class Matchers:
    """Parse newick format by ete3 numeric format options.
    """
    def __init__(self, formatcode):
        self.type = {}

        for node_type in ["leaf", "single", "internal"]:
            # (node_type == "leaf") or (node_type == "single"):
            if node_type != "internal":
                container1 = NW_FORMAT[formatcode][0][0]
                container2 = NW_FORMAT[formatcode][1][0]
                converterFn1 = NW_FORMAT[formatcode][0][1]
                converterFn2 = NW_FORMAT[formatcode][1][1]
                flexible1 = NW_FORMAT[formatcode][0][2]
                flexible2 = NW_FORMAT[formatcode][1][2]
            else:
                container1 = NW_FORMAT[formatcode][2][0]
                container2 = NW_FORMAT[formatcode][3][0]
                converterFn1 = NW_FORMAT[formatcode][2][1]
                converterFn2 = NW_FORMAT[formatcode][3][1]
                flexible1 = NW_FORMAT[formatcode][2][2]
                flexible2 = NW_FORMAT[formatcode][3][2]

            if converterFn1 == str:
                first_match = "({})".format(NAME_RE)
            elif converterFn1 == float:
                first_match = "({})".format(FLOAT_RE)
            elif converterFn1 is None:
                first_match = '()'

            if converterFn2 == str:
                second_match = "(:{})".format(NAME_RE)
            elif converterFn2 == float:
                second_match = "(:{})".format(FLOAT_RE)
            elif converterFn2 is None:
                second_match = '()'

            if flexible1 and (node_type != 'leaf'):
                first_match += "?"
            if flexible2:
                second_match += "?"

            m0 = r"^\s*{first_match}"
            m1 = r"\s*{second_match}"
            m2 = r"\s*({NHX_RE})"
            m3 = r"?\s*$"
            matcher_str = (m0 + m1 + m2 + m3).format(**{
                "first_match": first_match,
                "second_match": second_match,
                "NHX_RE": NHX_RE,
                })

            # matcher_str = r'^\s*{}\s*{}\s*({})?\s*$'.format(
            # FIRST_MATCH, SECOND_MATCH, NHX_RE)
            compiled_matcher = re.compile(matcher_str)

            # fill matcher for this node
            self.type[node_type] = [
                container1,
                container2,
                converterFn1,
                converterFn2,
                compiled_matcher
            ]


def parse_nhx(NHX_string):
    """
    NHX format:  [&&NHX:prop1=value1:prop2=value2]
    MB format: ((a[&Z=1,Y=2], b[&Z=1,Y=2]):1.0[&L=1,W=0], ...
    """
    # store features
    ndict = {}

    # parse NHX or MB features
    if "[&&NHX:" in NHX_string:
        NHX_string = NHX_string.replace("[&&NHX:", "")
        NHX_string = NHX_string.replace("]", "")

        for field in NHX_string.split(":"):
            try:
                pname, pvalue = field.split("=")
                ndict[pname] = pvalue
            except ValueError as e:
                raise NewickError('Invalid NHX format %s' % field)
    return ndict


# GLOBAL RE COMPILED MATCHERS
MATCHER = {}
for formatcode in range(11):
    MATCHER[formatcode] = Matchers(formatcode)



class FastNewick2TreeNode:
    """Parse newick str to a TreeNode object

    """
    def __init__(self, data, tree_format):
        self.data = data
        self.root = Node()
        self.current_node = self.root
        self.current_parent = None
        self.fmt = tree_format
        self.data = re.sub(r"[\n\r\t ]+", "", self.data)

    def newick_from_string(self):
        """Reads a newick string in the New Hampshire format."""

        # split on parentheses to traverse hierarchical tree structure
        for chunk in self.data.split("(")[1:]:
            # add child to make this node a parent.
            if self.current_parent is None:
                self.current_parent = self.root 
            else:
                new_node = Node()
                self.current_parent._add_child(new_node)
                self.current_parent = new_node            
            # self.current_parent = (
                # self.root if self.current_parent is None else
                # self.current_parent.add_child()
            # )

            # get all parenth endings from this parenth start
            subchunks = [ch.strip() for ch in chunk.split(",")]
            if subchunks[-1] != '' and not subchunks[-1].endswith(';'):
                raise NewickError(
                    'Broken newick structure at: {}'.format(chunk))

            # Every closing parenthesis will close a node and go up one level.
            for idx, leaf in enumerate(subchunks):
                if leaf.strip() == '' and idx == len(subchunks) - 1:
                    continue
                closing_nodes = leaf.split(")")

                # parse features and apply to the node object
                self.apply_node_data(closing_nodes[0], "leaf")

                # next contain closing nodes and data about the internal nodes.
                if len(closing_nodes) > 1:
                    for closing_internal in closing_nodes[1:]:
                        closing_internal = closing_internal.rstrip(";")
                        # read internal node data and go up one level
                        self.apply_node_data(closing_internal, "internal")
                        self.current_parent = self.current_parent.up
        return self.root

    def apply_node_data(self, subnw, node_type):
        """Parse data (edge lengths, support, etc) from node string."""
        if node_type in ("leaf", "single"):
            new_node = Node()
            self.current_parent._add_child(new_node)
            self.current_node = new_node
        else:
            self.current_node = self.current_parent

        # if no feature data
        subnw = subnw.strip()
        if not subnw:
            return

        # load matcher junk
        c1, c2, cv1, cv2, match = MATCHER[self.fmt].type[node_type]

        # look for node features
        data = re.match(match, subnw)

        # if there are node features then add them to this node
        if data:
            data = data.groups()

            # node has a name
            if (data[0] is not None) and (data[0] != ''):
                self.current_node.add_feature(c1, cv1(data[0]))

            if (data[1] is not None) and (data[1] != ''):
                self.current_node.add_feature(c2, cv2(data[1][1:]))

        else:
            raise NewickError("Unexpected newick format {}".format(subnw))


if __name__ == "__main__":

    # get a working example to compare speed with newick.

    pass