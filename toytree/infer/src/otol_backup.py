#!/usr/bin/env python

"""Open tree of life API calls.

Query information from the open tree of life. This can include:
1. fetching newick strings based on taxon/node labels.
2. fetch an induced (pruned) subtree relating a list of taxa.

Terminology
-----------
OTT_ID: int
    A unique identifier assigned to a taxon in the Open Tree Taxonomy
    (OTT). It represents a named taxon (e.g., a species, genus, family)
    e.g., 770309 for Homo sapiens.
NODE_ID: str
    A unique identifier for an internal node in the Open Tree synthetic
    tree. May or may not correspond to a taxonomic ID (OTT_ID). If so,
    it will have an ID like "ott489154". If not, it is a common 
    ancestor within the synthetic tree and will have an ID like
    "mrcaott770309ott489154".

Example
-------
...
"""

from typing import Sequence, List
from urllib.parse import urljoin
from re import match
import requests
from requests.models import HTTPError
import pandas as pd
from loguru import logger
from toytree import tree
from toytree.core import Node, ToyTree


URI = "https://api.opentreeoflife.org/v3/"
HEADERS_JSON = {"content-type": "application/json", "User-Agent": "toytree"}
NODE_ID_PATTERN = r"^(ott\d+|mrcaott\d+)"
FLEX_QUERY = str | int | Sequence[str] | Sequence[int]
RANKS = ["species", "genus", "family", "order", "class", "phylum", "kingdom"]


# TODO: replace with just one get_node_info api call!
def _query_to_node_ids(query: FLEX_QUERY) -> List[str]:
    """Return a list of str node IDs from a query.

    ottID -> ott{ottID}
    nodeID -> nodeID
    name -> nodeID
    """
    # convert any input type to a str ottid.
    node_ids = []
    if isinstance(query, (str, int)):
        query = [query]
    for q in query:
        if isinstance(q, str):
            if not match(NODE_ID_PATTERN, q):
                try:
                    q = f"ott{get_taxon_id(q)}"
                except Exception:
                    pass
            node_ids.append(q)
        elif isinstance(q, int):
            node_ids.append(f"ott{q}")
    return node_ids


def get_matched_names(query: str | Sequence[str], do_approximate_matching: bool = False, context: str = None) -> dict[str, str]:
    """Return name matching from Open Tree of Life tnrs.

    Performs an API call to the Open Tree of Life taxonomic name
    resolving service (tnrs) and returns the JSON result as a dict.

    Parameters
    ----------
    names: str | List[str]
        One or more taxonomic names as strings.
    do_approximate_matching": bool
        If True then fuzzy name matching is performed. This is slower.
    context: str
        Enter a high-level taxonomic name to limit the search scope.
        [NB: This doesn't seem to work.]

    See Also
    --------
    - get_taxon_table

    Example
    -------
    >>> match_names("Lamiales")
    >>> {..., 'matched_names': ['lamiales'], 'results': [...], unmatched_names: []'}
    """
    if isinstance(query, str):
        query = [query]
    url = urljoin(URI, "tnrs/match_names")
    json = {"names": query}
    json = json if not do_approximate_matching else json | {"do_approximate_matching": True}
    json = json if not context else json | {"context": context}    
    response = requests.post(url=url, headers=HEADERS_JSON, json=json)
    try:
        response.raise_for_status()
    except Exception as exc:
        logger.error(response.text)
        raise exc
    return response.json()


def get_taxon_id_table(query: str | Sequence[str], accept_synonym: bool=False) -> pd.DataFrame:
    """Return DataFrame of taxon name and ID matching by OTOL tnrs.

    This calls the Open Tree of Life Taxonomic Name Resolution Service
    and returns a dataframe with matched names and OTT IDs given one
    or more queried taxon names.

    Returns
    -------
    pd.DataFrame

    Example
    -------
    >>> get_taxon_id_table(["homo sapiens", "Pedicularis"])
    >>> #           query         taxon     rank  is_synonym  ott_id ncbi_id  gbif_id
    >>> # 0  homo sapiens  Homo sapiens  species       False  770315    9606  2436436
    >>> # 1   pedicularis   Pedicularis    genus       False  989660   43174  3171670
    """
    # get dict of unmatched and matched names
    name_dict = get_matched_names(query)

    # report synonymized names
    # for name in name_dict["matched_names"]:
    data = []
    for item in name_dict["results"]:
        if not item.get("matches"):
            logger.warning(f"no match for '{item['name']}'")
            continue

        match = item["matches"][0]
        query = match["search_string"]
        matched_name = match["matched_name"]
        taxon_name = match["taxon"]["name"]
        taxon_rank = match["taxon"]["rank"]
        taxon_ott_id = match["taxon"]["ott_id"]
        synonym = match["is_synonym"]
        # source = match["taxon"]["source"]

        # parse sources, e.g., ["ncbi:1000", "gbif:202933"]
        ids = match["taxon"]["tax_sources"]
        ids = dict(i.split(":") for i in ids)
        ncbi = ids.get("ncbi", "nan")
        gbif = ids.get("gbif", "nan")

        # replace matched name with accepted taxon synonym (default) or not.
        if accept_synonym:
            taxon = taxon_name
        else:
            taxon = matched_name
        data.append([query, taxon, taxon_rank, synonym, taxon_ott_id, ncbi, gbif])

    columns=["query", "taxon", "rank", "is_synonym", "ott_id", "ncbi_id", "gbif_id"]
    return pd.DataFrame(data=data, columns=columns)


def get_taxonomy() -> dict[str,str]:
    """Return dict of metadata about the current version of the 
    open tree of life taxonomy.
    """
    url = urljoin(URI, "taxonomy/about")
    headers = {"content-type": "application/json"}
    response = requests.post(url=url, headers=headers, json={})
    response.raise_for_status()
    json = response.json()
    return json


def get_taxon_info(query: str | int | dict[str, int], include_lineage: bool=False, include_children: bool=False, include_terminal_descendants: bool=False) -> dict[str,str]:
    """Return taxonomy info about a queried ID from open tree or other 
    sources.

    Parameters
    ----------
    query
        An int ott_id, str node_id, or dict mapping a database name to
        its int id type, e.g., {'ncbi': 900}.
    include_lineage: bool
        Whether to include info about all higher-level taxa that 
        include this taxon. Default=False.
    include_children: bool
        Whether to include info about all child taxa. Default=False.
    include_terminal_descendants: bool
        Whether to include a list of terminal OTT ids descended from this taxon.

    Examples
    --------    
    >>> get_taxon_info(900)
    >>> get_taxon_info("ott_900")
    >>> get_taxon_info({'ncbi': 123})
    >>> get_taxon_info(900, include_lineage=True)    
    """
    # parse external database IDs if dict, else otol IDs
    if isinstance(query, dict):
        key = list(query)[0]
        value = query[key]
        json = {"source_id": f"{key}:{value}"}
    elif isinstance(query, int):
        json = {"ott_id": query}
    else:
        node_id = _query_to_node_ids(query)[0]
        json = {"ott_id": int(node_id.lstrip("ott_"))}

    # options
    json.update({
        "include_children": include_children,
        "include_lineage": include_lineage,
        "include_terminal_descendants": include_terminal_descendants,
    })

    # send post
    url = urljoin(URI, "taxonomy/taxon_info")
    response = requests.post(url=url, headers=HEADERS_JSON, json=json)
    try:
        response.raise_for_status()
    except Exception as exc:
        logger.error(response.text)
        raise exc    
    json = response.json()
    return json


def get_taxon_lineage(query: str | int, full_json: bool = False, rank_only: bool = False, max_height: int = None, top: str = None) -> dict[str, str]:
    """Return an ordered list of the taxonomic lineage from this node to root.

    Parameters
    ----------
    query: str | int
        A node ID, taxon ID, or taxon name to get taxon lineage for.
    full_json: bool
        If True the full JSON dict from open tree is returned, else a
        simplified dict is returned with only {rank: name}.
    rank_only: bool
        If True then only 'ranked' taxa are included (e.g., genus, 
        family, order, class, phylum, kingdom, domain)
    max_height: int | None
        An optional max number of ancestor taxa to include.
    top: str
        An optional taxon name to use a top-level stopping criterion.

    Returns
    -------
    dict or list[dict]
        If 'full_json' is False a simple dict is returned mapping ranks
        to names, else a list of dicts is returned where each dict
        contains detailed info on the internal taxon.

    Examples
    --------
    >>> get_taxon_lineage("Boswellia sacra", rank_only=True, max_height=3)
    >>> # {"genus": "Boswellia", "family": "Burseraceae", "order": "Sapindales"}
    """
    lineage = get_taxon_info(query, include_lineage=True)["lineage"]

    # exclude 'no rank' taxa or rename as 'no_rank_1', 'no_rank_2', etc
    if rank_only:
        lineage = [i for i in lineage if i["rank"] != "no rank"]
    else:
        ridx = 1
        # print(lineage)
        for i in lineage:
            if i["rank"] == "no rank":
                i["rank"] = f"no_rank_{ridx}"
                ridx += 1

    # return full json dict or simplified dict (default)
    if not full_json:
        return {i["rank"]: i["unique_name"] for i in lineage[:max_height]}
    return lineage[:max_height]


def get_taxon_parent(query: str | int, full_json: bool = False, rank_only: bool = False) -> dict[str, str]:
    """Returns the nearest taxonomic parent of a query. 
    """
    return get_taxon_lineage(query, full_json, rank_only)[0]


def get_taxon_descendants(query: str | int, min_rank: str="genus", terminal_only: bool = False) -> List[int]:
    """Return list of open tree taxon IDs descended from a query and
    above a min_rank taxonomic minimum.

    Parameters
    ----------
    ...

    Examples
    --------
    >>> get_taxon_path("lamiales", min_rank="family")
    """
    if min_rank:
        min_rank = min_rank.lower()
        assert min_rank in RANKS

    # get the query as a node ID
    assert isinstance(query, (str, int)), "query should be a node ID, taxon ID, or taxon name"
    query = [_query_to_node_ids(query)[0]]

    # traverse down tree stopping when min_rank it encountered
    ott_ids = []
    while query:
        q = query.pop(0)
        info = get_taxon_info(q, include_children=True)
        for node in info["children"]:
            if not node["flags"]:
                ott_id = node["ott_id"]
                if node["rank"] == min_rank:
                    ott_ids.append(ott_id)
                else:
                    query.append(ott_id)
                    if not terminal_only:
                        ott_ids.append(ott_id)
    return ott_ids


def get_taxon_id(query: str) -> int:
    """Return the int ott_id of a str taxon query to the otol tnrs.

    Parameters
    ----------
    query: str
        A taxonomic name to query (e.g., species, genus, family, etc.)

    Example
    -------
    >>> get_taxon_id("Lamiales")
    >>> # 23736
    """
    name_dict = get_matched_names(query)
    for item in name_dict["results"]:
        if not item.get("matches"):
            logger.warning(f"no match for '{item['name']}'")
            return None
        match = item["matches"][0]            
        return int(match["taxon"]["ott_id"])


def get_node_id(query: str | int) -> str:
    """Return the int ott_id of a str taxon query to the otol tnrs.

    Parameters
    ----------
    query: str
        A taxonomic name to query (e.g., species, genus, family, etc.)

    Example
    -------
    >>> get_node_id("Lamiales")
    >>> # 'ott23736'
    """
    return get_node_info(query)[0]["node_id"]


def get_node_info(query: FLEX_QUERY, include_lineage: bool = False) -> List[dict[str,str]]:
    """Return a dict with information about one or more taxon nodes.

    The information lists the studies that include these nodes and
    their tree ids. This output is verbose but a little messy. See
    `get_node_id` and `get_supporting_studies_from_id` for related
    but simpler options.

    Parameters
    ----------
    query: str | int | List
        One or more taxon names or ott ids as ints or strs.

    Example
    -------
    >>> get_node_info(["Pedicularis", "ott815270", 23736])
    >>> # [{...}]
    """
    node_ids = _query_to_node_ids(query)

    # send post
    json = {"node_ids": node_ids, "include_lineage": include_lineage}
    url = urljoin(URI, "tree_of_life/node_info")
    response = requests.post(url=url, headers=HEADERS_JSON, json=json)
    try:
        response.raise_for_status()
    except Exception as exc:
        logger.error(response.text)
        raise exc
    return response.json()


def get_mrca_info(query: FLEX_QUERY) -> dict[str, str]:
    """Return json dict with info about the MRCA of a set of queries.

    Example
    -------
    >>> get_mrca_info(["Canarium", "Bursera", "Boswellia"])
    >>> # {'mrca': {'node_id': ..., 'num_tips': ...'}, ...}
    """
    # build list of str node_ids from input ints or taxon queries.
    node_ids = _query_to_node_ids(query)

    # send post
    url = urljoin(URI, "tree_of_life/mrca")
    json = {"node_ids": node_ids}
    response = requests.post(url=url, headers=HEADERS_JSON, json=json)
    try:
        response.raise_for_status()
    except Exception as exc:
        logger.error(response.text)
        raise exc
    return response.json()


def get_mrca_node_id(query: FLEX_QUERY) -> str:
    """Return the node ID of the MRCA of a set of queries.

    Example
    -------
    >>> get_mrca_node_id(["Canarium", "Bursera", "Boswellia"])
    >>> # mrcaott96ott98
    """
    return get_mrca_info(query)["mrca"]["node_id"]


def get_mrca_taxon_id(query: FLEX_QUERY) -> str:
    """Return the nearest taxon ID to the MRCA node of a set of queries.

    Example
    -------
    >>> get_mrca_taxon_id(["Canarium", "Bursera", "Boswellia"])
    >>> # 350867
    """
    return get_mrca_info(query)["nearest_taxon"]["ott_id"]


def get_synthetic_subtree(query: int | str, full_json: bool = False, **kwargs) -> str:
    """Return a newick str of the subtree below an open tree node.

    Parameters
    ----------
    query: str | int
        An open tree node ID, taxon ID, or taxon name.

    Returns
    -------
    str or dict[str, str]
        A newick string or dict.
    """
    # get top level node and ensure it has <25K tips (max allowed)
    node_id = _query_to_node_ids(query)[0]
    info = get_node_info(node_id)[0]
    if info["num_tips"] >= 25_000:
        msg = "open tree of life does not allow fetching trees with >25K tips. Use `get_synthetic_induced_subtree` instead."
        logger.error(msg)
        raise ValueError(msg)

    # ...
    json = {"node_id": f"{node_id}"}
    json = json | kwargs

    # post to api
    url = urljoin(URI, "tree_of_life/subtree")
    response = requests.post(url=url, headers=HEADERS_JSON, json=json)
    try:
        response.raise_for_status()
    except HTTPError as exc:
        mrca = response.json()["broken"]["mrca"]
        logger.error(
            f"Node is broken (i.e., not in synthetic tree) due to conflicts. Use '{mrca}' instead. See Error:\n{response.text}")
        raise exc
    except Exception as exc:
        logger.error(response.text)
        raise exc
    json = response.json()
    if full_json:
        return json
    return json["newick"]


def get_synthetic_induced_subtree(query: Sequence[int | str], full_json: bool = False, label_format: str = "name_and_id", insert_broken_nodes: bool = False) -> str:
    """Return a newick str of the subtree below an open tree node.

    Parameters
    ----------
    query: Sequence[str | int]
        A list of open tree node IDs, taxon IDs, or taxon names.
    label_format: str
        Option for labels: 'name_and_id', 'name', or 'id'.

    Returns
    -------
    str
        A newick string.
    """
    # get query converted to str node ids
    node_ids = _query_to_node_ids(query)
    json = {"node_ids": node_ids, "label_format": label_format}

    # post to api
    url = urljoin(URI, "tree_of_life/induced_subtree")
    response = requests.post(url=url, headers=HEADERS_JSON, json=json)
    try:
        response.raise_for_status()
    # except HTTPError as exc:
    #     mrca = response.json()["broken"]["mrca"]
    #     logger.error(
    #         f"Node is broken (i.e., not in synthetic tree) due to conflicts. Use '{mrca}' instead. See Error:\n{response.text}")
    #     raise exc
    except Exception as exc:
        logger.error(response.text)
        raise exc
    json = response.json()

    # solve broken nodes
    if insert_broken_nodes:
        tree = toytree.tree(json["newick"])
        for key, val in json["broken"].items():
            node = tree.get_nodes("~" + val)[0]
            name = get_taxon_info(key)["name"]
            child = Node(f"broken_{name}_{node.name}", dist=1.)
            child.broken = True
            node._add_child(child)
        tree._update()
        nwk = tree.write(internal_labels="name", dist_formatter=None)
        json["newick"] = nwk

    # return as json or newick
    if full_json:
        return json
    return json["newick"]


def get_taxonomy_induced_subtree(query: str | int, min_rank: str="genus") -> List[int]:
    """Return a subtree below a taxonomic name or ID composed of 
    descendant taxa that are of a min_rank or above.

    Parameters
    ----------
    ...

    Examples
    --------
    >>> get_taxonomy_induced_subtree("lamiales", min_rank="family")
    """
    if min_rank:
        min_rank = min_rank.lower()
        assert min_rank in RANKS

    # get the mrca node ID even if not a taxon
    mrca = get_mrca_info(query)
    if mrca["mrca"].get("taxon"):
        mrca = mrca["mrca"]["taxon"]
    else:
        mrca = mrca["nearest_taxon"]
    ott_id = mrca["ott_id"]
    root = Node(name=ott_id)
    nodes = {ott_id: root}
    qlist = [ott_id]

    # traverse down tree stopping when min_rank it encountered
    while qlist:
        q = qlist.pop(0)
        info = get_taxon_info(q, include_children=True)
        node = nodes[q]
        node._taxon = info["name"]
        for c in info["children"]:
            if not c["flags"]:
                ott_id = c["ott_id"]
                new_node = Node(name=ott_id, dist=1.)
                new_node._taxon = c["name"]
                node._add_child(new_node)
                nodes[ott_id] = new_node
                # logger.warning(f"p={node._taxon} | c={new_node._taxon} | {ott_id} | {c['rank']}")
                if c["rank"] != min_rank:
                    qlist.append(ott_id)
    tree = ToyTree(root)
    tree.set_node_data("name", [f"{i._taxon}_{i._name}" for i in tree], inplace=True)
    return tree


###############################################################


def get_supporting_studies(query: FLEX_QUERY) -> List[str]:
    """Return a list of studies@trees supporting splits in the synthetic
    tree relating a set of queried node IDs, taxon IDs, or taxon names.

    Parameters
    ----------
    query: str | int | Sequence[str | int]
        One or more node ID, taxon ID, or taxon names. If a single 
        taxon is entered it will search studies for the full clade
        below that node. If a number of queries are entered, the 
        studies are relevant to their induced subtree.

    Returns
    -------
    List[str]
        A list of string identifiers of study@tree.
    """
    if isinstance(query, (str, int)):
        json = get_synthetic_subtree(query, full_json=True)
    else:
        json = get_synthetic_induced_subtree(query, full_json=True)
    return json["supporting_studies"]


# def find_studies(taxon: str, verbose: bool = True, **kwargs) -> list[str]:
#     """Return list of study Ids matching a taxon query.

#     For the query "Orobanchaceae" the result ["pg_2044", "pg_2031",
#     "pg_145"] contains three matched studies. To get details of one of
#     these studies use `get_study()` or to get trees use `get_tree()`.
#     This search looks for matches to the "ot:focalCladeOTTTaxonName"
#     study property (this is the only search option I could get to work.)
#     """
#     url = urljoin(URI, "studies/find_studies")
#     headers = {"content-type": "application/json"}
#     json = {"property": "ot:focalCladeOTTTaxonName", "value": taxon, "verbose": verbose}
#     json = json | kwargs
#     response = requests.post(url=url, headers=headers, json=json)
#     try:
#         response.raise_for_status()
#     except Exception as exc:
#         logger.error(response.text)
#         raise exc
#     json = response.json()
#     return json
    # return [i["ot:studyId"] for i in json["matched_studies"]]


def get_study_or_tree(study_id: str | int, tree_id: str | int = None, label_format: str = None) -> str:
    """Return tree or trees associated with a study or tree id.

    Parameters
    ----------
    study_id: str | int
        ...
    tree_id: str | int | None
        ...
    label_format: str | None
        "originallabel, "ottid", or "otttaxonname"

    API call format
    -----------------
    $ curl https://api.opentreeoflife.org/v3/study/pg_1144
    $ curl https://api.opentreeoflife.org/v3/study/pg_1144.tre/?tip_label=ot:ottid
    $ curl https://api.opentreeoflife.org/v3/study/pg_1144.tre/?tip_label=ot:otttaxonname

    Example
    -------
    >>> get_study_or_tree("pg_1144", tree_id=1, label_format="ottid")
    >>> # (((...)))
    """
    # only support newick currently
    suffix = ".tre"

    # three format options
    if label_format == "otttaxonname":
        label = "?tip_label=ot:otttaxonname"
    elif label_format == "ottid":
        label = "?tip_label=ot:ottid"
    else:
        label = "?tip_label=ot:originallabel"        

    # add tree id if provided
    if tree_id is not None:
        if isinstance(tree_id, str):
            tree_id = int(tree_id.lstrip("tree"))
        url = urljoin(URI, f"study/{study_id}/tree/tree{tree_id}{suffix}/{label}")
    else:
        url = urljoin(URI, f"study/{study_id}{suffix}/{label}")

    # call api
    response = requests.get(url=url)
    try:
        response.raise_for_status()
    except Exception as exc:
        logger.error(response.text)
        raise exc

    # clean data b/c otol puts extra quotes around _some_ names
    return response.text
    nex = response.text    
    nex = nex.replace("'", "")
    return nex



if __name__ == "__main__":

    import toytree
    from json import dumps

    # find Orobanchaceae studies. Select pg_xxx label for one of them.
    # studies = find_studies("Pedicularis")
    # print(dumps(studies, indent=2))

    # nwk = get_tree("pg_2642")
    # nwk = get_tree("ot_2304")
    # toytree.tree(nwk).ladderize()._draw_browser(tmpdir="~", scale_bar=True)

    
    # ott_id = get_node_info("Boswellia")
    # print(ott_id)
    # print(mrca)
    # print(get_newick_from_id("mrcaott96ott98"))
    # info = get_matched_names("Pedicular", do_approximate_matching=True, context="Flowering plants")
    # print(dumps(info, indent=2))
    # print(_query_to_node_ids(["Boswellia", "Canarium", "Bursera"]))

    # print(mrca)
    # tre = get_synthetic_subtree(mrca)
    # print(tre)
    # get_synthetic_subtree(988295)
    # tre = get_synthetic_subtree("mrcaott96ott98")
    # print(tre.ntips)

    # mrca = get_mrca_taxon_id(["Boswellia", "Canarium", "Bursera"])    
    # print(mrca)
    # print(get_taxon_lineage("Boswellia sacra", full_json=False, rank_only=True, max_height=5))    
    # print(get_taxon_lineage("Boswellia sacra", full_json=False, rank_only=False, max_height=5))
    # print(get_taxon_lineage("Boswellia sacra", full_json=True, rank_only=True, max_height=3))
    # print(get_taxon_lineage("Boswellia sacra", full_json=True, rank_only=False, max_height=3))
    # print(get_taxon_path("Lamiales", min_rank="family"))
    # query = ["Lamiaceae", "Bignoniaceae", "Oleaceae", "Acanthaceae"]
    # node = get_taxonomy_induced_subtree(query, min_rank="family")
    # print(node._children)
    # nwk = get_study_or_tree("ot_2116", 1)
    # toytree.tree(nwk)._draw_browser(tmpdir="~")
    # print(nwk)
    # toytree.tree("((a,b),'cat dog');")._draw_browser(tmpdir="~")

    # raise SystemExit(0)

    # 1. fetch taxon info for multiple str search terms.
    # df = get_taxon_table(["homo sapiens", "Pedicularis", "Amaranthus palmeri", "Beta vulgaris"])
    # print(df)

    # 2. query the ott_id of a single taxon.
    ott_id = get_node_info("Boswellia")
    print(ott_id)

    # 3. query the node info of one or more nodes (useful to find study trees)
    info = get_node_info(ott_id)
    print(info)#["num_tips"])
    raise SystemExit(0)
    # 4. get current taxonomy
    # _ = get_taxonomy()

    # 5. get taxon info
    # info = get_taxon_info(ott_id) # include_children=True)
    # info = get_taxon_info("ott_273185")
    # info = get_taxon_info({"gbif": 3171670})

    # 6. get a taxonomy resolved name search
    info = match_names("Pedicularis")

    # 7. 


    mrca = get_mrca_node_id([273185, 1009710])
    print(mrca)

    nwk = get_newick_from_id("mrcaott22343ott59373")
    # nwk = get_newick_from_id(11726)    
    tree = toytree.tree(nwk)
    print(tree.ntips)
    tree._draw_browser(tmpdir="~", ts='s', height=8000)
