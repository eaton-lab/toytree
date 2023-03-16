#!/usr/bin/env python

"""Parse a single ToyTree from multiple input types.

The single input can be in newick, NHX, or nexus format, and contained
in a string, file or URL.

Example
-------
>>> parser = TreeIOParse(data)
>>> parser.parse_node_auto()           # auto
>>> parser.parse_node_from_str()       # faster, reads from str.
>>> parser.parse_node_from_file()      # faster, reads from file.
>>> parser.parse_node_from_url()       # faster, reads from url.
"""

from typing import Union, TypeVar, Dict, List, Optional
import re
from pathlib import Path
from loguru import logger
import requests

from toytree.core.tree import ToyTree
from toytree.io.src.newick import parse_newick_string
from toytree.io.src.nexus import get_newicks_and_translation_from_nexus

logger = logger.bind(name="toytree")

# for removing white_ space from newicks
WHITE_SPACE = re.compile(r"[\n\r\t ]+")
ILLEGAL_NEWICK_CHARS = re.compile(r"[:;(),\[\]\t\n\r=]")

# PEP 484 recommend capitalizing alias names
Url = TypeVar("Url")


class TreeIOParser:
    """Class with functions to return a Node parsed from many inputs.

    This is intended for internal use only. See `toytree.io` module
    for functions that use this class. Supports kwargs for parsing
    newick strings as in `parse_newick_string` function.

    Parameters
    ----------
    data: str, Path, or URL
        One or more tree data inputs, where an input can be a newick
        or nexus str, or a file or URL containing newick or nexus
        strings.
    """
    def __init__(self, data: Union[str, Url, Path], tdict: Optional[Dict[str, str]] = None, **kwargs):
        self.data = data
        """: The input data object."""
        self.tdict: Dict[str, str] = tdict if tdict else {}
        """: Optional translation dict parsed from nexus data."""
        self.kwargs: Dict[str, str] = kwargs
        """: Optional kwargs for parse_newick_string function."""

    def _auto_parse_data_to_str(self) -> str:
        """Return str data parsed from str, file, or url.

        The returned data string could be any format, it is not yet
        checked at this point.
        """
        # Path: read file and yield string. But if a str path then is
        # found differently further below in str parsing.
        if isinstance(self.data, Path):
            if self.data.exists():
                with open(self.data, 'r', encoding='utf-8') as indata:
                    return indata.read()
            raise IOError(f"Path {self.data} does not exist.")

        # str: check if it is URI, then Path, then newick.
        if isinstance(self.data, str):
            # is there any scenario (nex?) not to strip by default?...
            # self.data = self.data.strip()

            # empty string
            if ";" in self.data:
                return self.data

            if not self.data:
                return "(0);"

            # newick always starts with "(" whereas a filepath and
            # URI can never start with this, so... easy enough.
            if self.data[0] in ("(", "#"):
                return self.data

            # check for URI (hack: doesn't support ftp://, etc.)
            if self.data.startswith("http"):
                response = requests.get(self.data)
                response.raise_for_status()
                return response.text

            # check if str is actually Path (fails if filename is large)
            if Path(self.data).exists():
                with open(self.data, 'r', encoding="utf-8") as indata:
                    return indata.read()
            else:
                raise IOError(
                    "Tree input appears to be a file path "
                    f"but does not exist: '{self.data}'")

        # if entered as bytes convert to str and restart
        elif isinstance(self.data, bytes):
            self.data = self.data.decode()
            self._auto_parse_data_to_str()

        # not str or Path then raise TypeError
        raise TypeError(f"Error parsing unrecognized tree data input type: {self.data}.")

    def _convert_nwk_or_nex_to_tree(self, data: str, multi: bool = False) -> str:
        """Return a Node given unknown string data format. """
        if data[:6].upper() == "#NEXUS":
            # splits into: List[str], Dict[str,str]
            data, tdict = get_newicks_and_translation_from_nexus(data)
            self.tdict = tdict
        else:
            if multi:
                data = data.split("\n")
        return data

    def _translate_node_names(self, tree: ToyTree) -> None:
        """Check valid and translate names using nexus translation dictionary."""
        for node in tree.traverse():
            # replace disallowed characters in names with '_'
            if node.name:
                clean_name = ILLEGAL_NEWICK_CHARS.sub("_", self.tdict[node.name])
                node.name = clean_name

    def parse_tree_from_str(self) -> ToyTree:
        """Return a Node parsed from a nwk, nex, or NHX data."""
        data = WHITE_SPACE.sub("", self.data)
        nwk = self._convert_nwk_or_nex_to_tree(data)
        assert nwk.count("(") == nwk.count(")"), (
            "Parentheses do not match. Broken tree data.")
        tre = parse_newick_string(nwk, **self.kwargs)
        if self.tdict:
            self._translate_node_names(tre)
        return tre

    def parse_tree_from_url(self) -> ToyTree:
        """Return a Node parsed from URL containing nwk, nex, or NHX data."""
        response = requests.get(self.data)
        response.raise_for_status()
        self.data = response.text
        return self.parse_tree_from_str()

    def parse_tree_from_file(self) -> ToyTree:
        """Return a Node parsed from URL containing nwk, nex, or NHX data."""
        path = Path(self.data)
        with open(path, 'r', encoding='utf-8') as indata:
            self.data = WHITE_SPACE.sub("", indata.read())
        return self.parse_tree_from_str()

    def parse_tree_auto(self) -> ToyTree:
        """Return a Node parsed from URL containing nwk, nex, or NHX data."""
        self.data = self._auto_parse_data_to_str()
        return self.parse_tree_from_str()

    def parse_multitree_auto(self) -> List[ToyTree]:
        """Parse a multitree input and return as a list of Nodes.
        """
        # convert input type into a nex or newick string.
        data = self._auto_parse_data_to_str().strip()
        # convert to multi-line newick string with tdict separate
        data = self._convert_nwk_or_nex_to_tree(data, multi=True)
        # apply single tree parser to each line and use tdict to translate
        return [TreeIOParser(i, tdict=self.tdict).parse_tree_from_str() for i in data]


if __name__ == "__main__":

    TEST = "/home/deren/Downloads/Clustal_Omega_Dec3.txt"
    TEST1 = "((a,b)c);"
    TEST2 = """(
    (a,b)c)
    ;
"""

    tool = TreeIOParser(TEST1)
    print(tool.parse_tree_auto())

    tool = TreeIOParser(TEST2)
    print(tool.parse_tree_from_str())

    tool = TreeIOParser("https://eaton-lab.org/data/Cyathophora.tre")
    print(tool.parse_tree_from_url())


    TEST3 = "https://eaton-lab.org/data/densitree.nex"
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

    tool = TreeIOParser(TEST5)
    trees = tool.parse_multitree_auto()
    print(trees[0].get_tip_labels())
