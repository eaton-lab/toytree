#!/usr/bin/env python

"""Generic tree input parsing class.


Notes
-----
Compared to the ete newick parser this one is slower, since it splits
nodes by finding unmatched parantheses, versus simply finding the next
open parentheses. This cost comes with the benefit, however, of being
able to parse complex newick strings (e.g., NXH) without having to 
specify ahead of time that the file is NHX.
"""

from typing import Union, List, TypeVar, Dict, Tuple
import re
from pathlib import Path
from loguru import logger
import requests

from toytree.core.node import Node
from toytree.utils import ToytreeError
from toytree.io.src.newick import parse_newick_string
from toytree.io.src.nexus import get_newicks_and_translation_from_nexus

logger = logger.bind(name="toytree")

# for removing white_ space from newicks
WHITE_SPACE = re.compile(r"[\n\r\t ]+")
ILLEGAL_NEWICK_CHARS = r"[:;(),\[\]\t\n\r=]"

# PEP 484 recommend capitalizing alias names
Url = TypeVar("Url")


class TreeIOParser:
    """Return a list of Nodes from various tree input types.

    This is intended for internal use only.
    See `toytree.tree` for the docstring. Use kwargs to enter args
    to the `parse_newick_string` function.

    Parameters
    ----------
    multitree: bool
        If False then only the first tree is read, whereas if True
        one or more trees will be read from each input. The default
        of False leads to faster loading when fetching a single tree
        using `toytree.tree` versus `toytree.mtree` on the same file.
    """
    def __init__(
        self,
        data: Union[str, Url, Path, List],
        multitree: bool = False,
        **kwargs,
        ) -> List[Node]:

        self.data = data
        self.multitree = multitree
        self.kwargs = kwargs
        self.trees: List[Node] = []
        self.run()

    def _iter_data_inputs_as_strings(self) -> str:
        """Return a list of data strings for one or more trees.

        The data strings could be newick or nexus format at this point,
        and a data string could contain a single or multiple trees.
        """
        # get data as a collection of valid input types
        inputs = []
        if isinstance(self.data, list):
            inputs = self.data
        else:
            inputs = [self.data]

        # only do first data item if not allowing multitrees, for speed
        if not self.multitree:
            inputs = inputs[:1]

        # iterate over each input and store newick in self.data list
        for item in inputs:

            # if str data is a URI then parse it to List[str]
            if item.startswith("http"):
                response = requests.get(item)
                response.raise_for_status()
                item = response.text.strip()

            # if item is a Path, or a str filepath then parse newick 
            # List[str] from it. Will raise OSError if name too long 
            # so clearly not a filepath. Skips if not an existing Path.
            else:
                try:
                    if Path(item).exists():
                        with open(item, 'r', encoding="utf-8") as indata:
                            item = indata.read()
                except OSError:
                    pass

            # if str data is now a newick str then save it.
            if isinstance(item, str):
                yield item
            else:
                raise ToytreeError("Error parsing tree data input.")

    def _iter_strings_to_newicks(self) -> Tuple[str, Dict]:
        """Yield (newick str, trans dict) for each tree in each input.
        """
        for strdata in self._iter_data_inputs_as_strings():
            strdata = strdata.strip()

            # extract newick and translation dict from nexus
            if strdata.upper().startswith("#NEXUS"):
                nwks, tdict = get_newicks_and_translation_from_nexus(strdata)
            else:
                nwks, tdict = strdata.split("\n"), {}

            # limit to one tree if not multitree parsing
            if not self.multitree:
                nwks = nwks[:1]

            # yield tree data
            for newick in nwks:
                yield newick, tdict

    def run(self):
        """Parse ToyTrees from newick strings."""
        for nwk, tdict in self._iter_strings_to_newicks():

            # check newick is valid
            assert nwk.count("(") == nwk.count(")"), (
                "Parentheses do not match. Broken tree data.")

            # get ToyTree from newick string
            nwk = WHITE_SPACE.sub("", nwk)
            ttree = parse_newick_string(nwk, **self.kwargs)

            # translate names using nexus translation dictionary
            if tdict:
                for node in ttree.traverse():
                    # remove disallowed characters from names
                    node.name = re.sub(
                        ILLEGAL_NEWICK_CHARS, "_", tdict[node.name])
                    node.name = tdict[node.name]

            # save the tree
            self.trees.append(ttree)


if __name__ == "__main__":
    pass
