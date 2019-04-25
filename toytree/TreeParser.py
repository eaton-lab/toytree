#!/usr/bin/env python

"""
A newick/nexus file/string parser based on the ete3.parser.newick. Takes as 
input a string or file that contains one or multiple lines that contain 
newick strings. Lines that do not contain newick strings are ignored, unless
the #NEXUS is in the header in which case the 'translate' and 'trees' blocks
are parsed. 
"""

import os
import re
import requests
from .etemini import TreeNode


# Regular expressions used for reading newick format
FLOAT_RE = r"\s*[+-]?\d+\.?\d*(?:[eE][-+]\d+)?\s*"
NAME_RE = r"[^():,;]+?"
NHX_RE = r"\[&&NHX:[^\]]*\]"
NW_FORMAT = {
    # flexible with support
    # Format 0 = (A:0.35,(B:0.72,(D:0.60,G:0.12)1.00:0.64)1.00:0.56);
    0: [
        ('name', str, True),
        ('dist', float, True),
        ('support', float, True),
        ('dist', float, True),
    ],

    # flexible with internal node names
    # Format 1 = (A:0.35,(B:0.72,(D:0.60,G:0.12)E:0.64)C:0.56);
    1: [
        ('name', str, True),
        ('dist', float, True),
        ('name', str, True),
        ('dist', float, True),      
    ],

    # strict with support values
    # Format 2 = (A:0.35,(B:0.72,(D:0.60,G:0.12)1.00:0.64)1.00:0.56);
    2: [
        ('name', str, False),
        ('dist', float, False),
        ('support', str, False),
        ('dist', float, False),      
    ],

    # strict with internal node names
    # Format 3 = (A:0.35,(B:0.72,(D:0.60,G:0.12)E:0.64)C:0.56);
    3: [
        ('name', str, False),
        ('dist', float, False),
        ('name', str, False),
        ('dist', float, False),      
    ],

    # strict with internal node names
    # Format 4 = (A:0.35,(B:0.72,(D:0.60,G:0.12)));
    4: [
        ('name', str, False),
        ('dist', float, False),
        (None, None, False),
        (None, None, False),      
    ],

    # Format 5 = (A:0.35,(B:0.72,(D:0.60,G:0.12):0.64):0.56);
    5: [
        ('name', str, False),
        ('dist', float, False),
        (None, None, False),
        ('dist', float, False),      
    ],

    # Format 6 = (A:0.35,(B:0.72,(D:0.60,G:0.12)E)C);
    6: [
        ('name', str, False),
        (None, None, False),
        (None, None, False),        
        ('dist', float, False),      
    ],

    # Format 7 = (A,(B,(D,G)E)C);
    7: [
        ('name', str, False),
        ('dist', float, False),
        ('name', str, False),        
        (None, None, False),        
    ],    


    # Format 8 = (A,(B,(D,G)));
    8: [
        ('name', str, False),
        (None, None, False),
        ('name', str, False),        
        (None, None, False),
    ],

    # Format 9 = (,(,(,)));
    9: [
        ('name', str, False),
        (None, None, False),
        (None, None, False),
        (None, None, False),
    ],    

    # Format 10 = ((a[&Z=1,Y=2]:1.0[&X=3], b[&Z=1,Y=2]:3.0[&X=2]):1.0[&L=1,W=0], ...
    # NHX Like mrbayes NEXUS common
    10: [
        ('name', str, True),
        ('dist', str, True),
        ('name', str, True),
        ('dist', str, True),
    ]
}



class NewickError(Exception):
    """Exception class designed for NewickIO errors."""
    def __init__(self, value):
        Exception.__init__(self, value)

class NexusError(Exception):
    """Exception class designed for NewickIO errors."""
    def __init__(self, value):
        Exception.__init__(self, value)



class TreeParser(object):
    def __init__(self, intree, tree_format=0, multitree=False, debug=False):
        """
        Reads input as a string or file, figures out format and parses it.
        Formats 0-10 are newick formats supported by ete3. 
        Format 11 is nexus format from mrbayes.

        Returns either a Toytree or MultiTree object, depending if input has
        one or more trees. 
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
        # get newick from data and test newick structure
        if self.intree:
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

        # no input data
        else:
            self.treenodes = [TreeNode()]


    def warn_about_format(self):
        # warning about formats
        if "[&&NHX" not in self.data[0]:
            if ("[&" in self.data[0]) & (self.fmt != 10):
                print("Warning: data looks like tree_format=10 (mrbayes-like)")          


    def get_data_from_intree(self):
        """
        Load *data* from a file or string and return as a list of strings.
        The data contents could be one newick string; a multiline NEXUS format
        for one tree; multiple newick strings on multiple lines; or multiple
        newick strings in a multiline NEXUS format. In any case, we will read
        in the data as a list on lines. 
        """

        # load string: filename or data stream
        if isinstance(self.intree, (str, bytes)):
            
            # strip it
            self.intree = self.intree.strip()

            # is a URL: make a list by splitting a string
            if any([i in self.intree for i in ("http://", "https://")]):
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
        "get newick data from NEXUS"
        if self.data[0].strip().upper() == "#NEXUS":
            nex = NexusParser(self.data)
            self.data = nex.newicks
            self.tdict = nex.tdict


    def get_treenodes(self):
        "test format of intree nex/nwk, extra features"

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
        if self.tdict:
            for tree in self.treenodes:
                for node in tree.traverse():
                    if node.name in self.tdict:
                        node.name = self.tdict[node.name]



class Newick2TreeNode:
    "Parse newick str to a TreeNode object"    
    def __init__(self, data, fmt=0):
        self.data = data
        self.root = TreeNode()
        self.current_node = self.root
        self.current_parent = None
        self.fmt = fmt
        self.cleanup_data()


    def cleanup_data(self):
        # check parentheses
        if self.data.count('(') != self.data.count(')'):
            raise NewickError('Parentheses do not match. Broken tree data.')

        # remove white spaces and separators 
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
        "Reads a newick string in the New Hampshire format."

        # split on parentheses to traverse hierarchical tree structure
        for chunk in self.data.split("(")[1:]:
            # add child to make this node a parent.
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

        if node_type in ("leaf", "single"):
            self.current_node = self.current_parent.add_child()
        else:
            self.current_node = self.current_parent
        
        # if no feature data
        subnw = subnw.strip()
        if not subnw:
            return 

        # load matcher junk
        c1, c2, cv1, cv2, match = MATCHER[self.fmt].type[node_type]

        # if mrbayes then combine brackets
        if self.fmt == 10:
            if "]:" not in subnw:
                node, edge = subnw.split("]", 1)
                subnw = node + "]:0.0" + edge                       
            node, edge = subnw.split("]:")
            npre, npost = node.split("[")
            epre, epost = edge.split("[")
            subnw = "{}:{}[&&NHX:{}".format(
                npre, epre, ":".join([npost[6:], epost[6:]]))

        # look for node features
        data = re.match(match, subnw)

        # if there are node features then add them to this node
        if data:
            data = data.groups()

            # data should not be empty
            if all([i is None for i in data]):
                raise NewickError(
                    "Unexpected newick format {}".format(subnw))

            # node has a name
            if (data[0] is not None) and (data[0] != ''):
                self.current_node.add_feature(c1, cv1(data[0]))

            if (data[1] is not None) and (data[1] != ''):
                self.current_node.add_feature(c2, cv2(data[1][1:]))

            if (data[2] is not None) and data[2].startswith("[&&NHX"):
                fdict = parse_nhx(data[2])
                for fname, fvalue in fdict.items():
                    self.current_node.add_feature(fname, fvalue)
        else:
            raise NewickError("Unexpected newick format {}".format(subnw))



class NexusParser:
    """
    Parse nexus file/str formatted data to extract tree data and features.
    Expects '#NEXUS', 'begin trees', 'tree', and 'end;'.
    """
    def __init__(self, data):

        self.data = data
        self.newicks = []
        self.tdict = {}
        self.extract_tree_block()


    def extract_tree_block(self):
        "iterate through data file to extract trees"        

        lines = iter(self.data)
        while 1:
            try:
                line = next(lines).strip()
            except StopIteration:
                break
    
            # enter trees block
            if line.lower() == "begin trees;":
                while 1:
                    # iter through trees block
                    sub = next(lines).strip().split()
                    
                    # skip if a blank line
                    if not sub:
                        continue

                    # look for translation
                    if sub[0].lower() == "translate":
                        while sub[0] != ";":
                            sub = next(lines).strip().split()
                            self.tdict[sub[0]] = sub[-1].strip(",")

                    # parse tree blocks
                    if sub[0].lower().startswith("tree"):
                        self.newicks.append(sub[-1])
        
                    # end of trees block
                    if sub[0].lower() == "end;":
                        break



# re matchers should all be compiled on toytree init
class Matchers:
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



# class NewickWriter(object):
#     """
#     Write TreeNode data to a newick string.
#     """
#     def __init__(self, treenode, format, format_root_node, features):
#         self.treenode = treenode
#         self.format = format
#         self.format_root_node = format_root_node
#         self.features = features
#         self.newick = ""
#         self.write_newick()


#     def write_newick(self):

#         # what is this doing...?
#         for post, node in self.treenode.iter_prepostorder(is_leaf_fn=is_leaf):
#             if post:
#                 self.newick.append(")")
#                 if node.up is not None or self.format_root_node:
#                     self.newick.append(
#                         format_node(
#                             node, 
#                             "internal", 
#                             format,
#                             dist_formatter=dist_formatter,
#                             support_formatter=support_formatter,
#                             name_formatter=name_formatter),
#                         )
#                     self.newick.append(_get_features_string(node, features))

#             else:
#                 if node is not rootnode and node != node.up.children[0]:
#                     newick.append(",")

#                 if leaf(node):
#                     safe_name = re.sub("["+_ILEGAL_NEWICK_CHARS+"]", "_", \
#                                    str(getattr(node, "name")))
#                     newick.append(format_node(node, "leaf", format,
#                                   dist_formatter=dist_formatter,
#                                   support_formatter=support_formatter,
#                                   name_formatter=name_formatter))
#                     newick.append(_get_features_string(node, features))
#                 else:
#                     newick.append("(")

#     newick.append(";")
#     return ''.join(newick)    


def is_leaf(node):
    return not bool(node.children)


def parse_messy_nexus(nexus):
    """
    Approaches: 
    1: Parse the format to match NHX and then parse like normal NHX. 
    2. New parser to store all features and values as strings. 
    """


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
