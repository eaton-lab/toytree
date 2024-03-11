#!/usr/bin/env python

"""Parse tree data from flexible inputs to pass to a newick parser.

"""

from typing import Union, TypeVar, List, Tuple, Mapping
import re
from pathlib import Path
from loguru import logger
import requests

from toytree.core import ToyTree
from toytree.core.multitree import MultiTree
from toytree.io.src.newick import parse_newick_string
from toytree.io.src.nexus import get_newicks_and_translation_from_nexus
from toytree.io.src.utils import replace_whitespace

logger = logger.bind(name="toytree")

# for removing white_ space from newicks
# WHITE_SPACE = re.compile(r"[\n\r\t ]+")
ILLEGAL_NEWICK_CHARS = re.compile(r"[:;(),\[\]\t\n\r=]")

# PEP 484 recommend capitalizing alias names
Url = TypeVar("Url")


def parse_generic_to_str(data: Union[str, Url, Path]) -> str:
    """Return str data from input whether it is str, file, or url.

    The returned data string could be any format, it is not yet
    checked at this point. For example, newick or nexus; one tree
    or multiple trees; extended NHX or not.
    """
    # Path: read file and yield string. But if a str path then is
    # found differently further below in str parsing.
    if isinstance(data, Path):
        if data.exists():
            with open(data, 'r', encoding='utf-8') as indata:
                return indata.read()
        raise IOError(f"Path {data} does not exist.")

    # str: check if it is URI, then Path, then newick.
    if isinstance(data, str):
        # is there any scenario (nex?) not to strip by default?...
        data = data.strip()

        # empty string
        if ";" in data:
            return data

        # ...
        if not data:
            return "(0);"

        # newick always starts with "(" whereas a filepath and
        # URI can never start with this, so... easy enough.
        if data[0] in ("(", "#"):
            return data

        # check for URI (hack: doesn't support ftp://, etc.)
        if data.startswith("http"):
            response = requests.get(data)
            response.raise_for_status()
            return response.text

        # check if str is actually Path (fails if filename is large)
        if Path(data).exists():
            with open(data, 'r', encoding="utf-8") as indata:
                return indata.read()
        else:
            raise IOError(
                "Tree input appears to be a file path "
                f"but does not exist: '{data}'")

    # if entered as bytes convert to str and restart
    elif isinstance(data, bytes):
        data = data.decode()
        parse_generic_to_str(data)

    # not str or Path then raise TypeError
    raise TypeError(f"Error parsing unrecognized tree data input: {data}.")


def parse_data_from_str(strdata: str) -> Tuple[List[str], Mapping[int, str]]:
    """Return list of newicks and translation dict.
    """
    # if nexus then parse [nwks] from trees block
    if strdata[:6].upper() == "#NEXUS":
        nwks, tdict = get_newicks_and_translation_from_nexus(strdata)
        tdict = tdict
    # if newick then optionally split into multiple newicks
    else:
        strdata = replace_whitespace(strdata)
        nwks = strdata.split("\n")
        tdict = {}
    return nwks, tdict


def translate_node_names(tree: ToyTree, tdict: Mapping[int, str]) -> ToyTree:
    """Check valid and translate names using nexus translation dictionary."""
    if tdict:
        for node in tree:
            # replace disallowed characters in names with '_'
            if node.name:
                clean_name = ILLEGAL_NEWICK_CHARS.sub("_", tdict[node.name])
                node.name = clean_name
    return tree


def parse_tree(data: Union[str, Url, Path], **kwargs) -> ToyTree:
    """Return a ToyTree parsed from flexible input types.

    """
    strdata = parse_generic_to_str(data)
    nwks, tdict = parse_data_from_str(strdata)
    tree = parse_newick_string(nwks[0], **kwargs)
    if len(nwks) > 1:
        logger.warning(
            f"Data contains ({len(nwks)}) trees.\n"
            "Loading first using `toytree.tree`. Use `toytree.mtree` "
            "to instead load a MultiTree.")
    return translate_node_names(tree, tdict)


def parse_multitree(data: Union[str, Url, Path], **kwargs) -> ToyTree:
    """Return a MultiTree parsed from flexible input types.

    """
    strdata = parse_generic_to_str(data)
    nwks, tdict = parse_data_from_str(strdata)
    mtree = MultiTree([])
    for nwk in nwks:
        tree = parse_newick_string(nwk, **kwargs)
        translate_node_names(tree, tdict)
        mtree.treelist.append(tree)
    return mtree


def parse_tree_object(data: Union[str, Url, Path], **kwargs) -> Union[ToyTree, MultiTree]:
    """Return a ToyTree or MultiTree parsed from flexible input types.

    """
    strdata = parse_generic_to_str(data)
    nwks, tdict = parse_data_from_str(strdata)
    if len(nwks) > 1:
        mtree = MultiTree([])
        for nwk in nwks:
            tree = parse_newick_string(nwk, **kwargs)
            mtree.treelist.append(translate_node_names(tree, tdict))
        return mtree
    tree = parse_newick_string(nwks[0], **kwargs)
    return translate_node_names(tree, tdict)


if __name__ == "__main__":

    TEST = "/home/deren/Downloads/Clustal_Omega_Dec3.txt"
    TEST1 = "((a,b)c);"
    TEST2 = """(
    (a,b)X,c)
    ;
"""

    print(parse_tree_object(TEST))
    print(parse_tree_object(TEST1))
    print(parse_tree_object(TEST2))
    print(parse_tree_object("https://eaton-lab.org/data/Cyathophora.tre"))
    print(parse_tree_object("https://eaton-lab.org/data/densitree.nex"))

    TEST4 = """\
#NEXUS
begin trees;
    translate
           1       apple,
           2       blueberry,
           3       cantaloupe,
           4       durian,
           ;
    tree tree0 = [&U] ((1,2),(3,4));
    tree tree1 = [&U] ((1,2),(3,4));
end;
"""
    print(parse_tree_object(TEST4))

    TEST5 = """\
(((a:1,b:1):1,(d:1.5,e:1.5):0.5):1,c:3);
(((a:1,d:1):1,(b:1,e:1):1):1,c:3);
(((a:1.5,b:1.5):1,(d:1,e:1):1.5):1,c:3.5);
(((a:1.25,b:1.25):0.75,(d:1,e:1):1):1,c:3);
(((a:1,b:1):1,(d:1.5,e:1.5):0.5):1,c:3);
(((b:1,a:1):1,(d:1.5,e:1.5):0.5):2,c:4);
(((a:1.5,b:1.5):0.5,(d:1,e:1):1):1,c:3);
(((b:1.5,d:1.5):0.5,(a:1,e:1):1):1,c:3);
"""
    print(parse_tree_object(TEST5))
#     tool = TreeIOParser(TEST5)
#     trees = tool.parse_multitree_auto()
#     print(trees[0].get_tip_labels())
