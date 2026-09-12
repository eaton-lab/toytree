<div class="nb-md-page-hook" aria-hidden="true"></div>

# OpenTree and TimeTree

The `toytree.otol` module connects taxon-name resolution, OpenTree topology, and TimeTree divergence-age retrieval. Network results depend on external services and their current taxonomies, so analyses should retain the returned identifiers and provenance columns.


```python
import toytree
```

## Resolve names once

Resolve names before constructing a tree. The table preserves input order and reports unmatched or ambiguous rows explicitly. For reproducible tree construction, require every row to resolve and choose how duplicate OTT identifiers should be handled.


```python
resolved = toytree.otol.resolve_taxonomic_names(
    ["Homo sapiens", "Pan troglodytes", "Gorilla gorilla"],
    on_unresolved="raise",
    on_ambiguous="first",
    on_duplicate="raise",
)
resolved
```

## Construct ToyTree objects

`fetch_tree_from_taxonomy` merges OpenTree ancestor identities directly. It does not convert ranks into distances. Its unit edge lengths are topological placeholders, not divergence times.

`fetch_tree_from_synthesis` uses the OpenTree synthetic induced tree. With `constrain_by_taxonomy=True`, taxonomy clades are hard constraints and compatible synthesis relationships refine polytomies. With `force_as_tips=True`, a queried ancestor is represented by a terminal child so every query remains a tip. Both functions return `ToyTree` and attach `ott_id` and `ncbi_id` features.


```python
taxonomy_tree = toytree.otol.fetch_tree_from_taxonomy(resolved)
synthesis_tree = toytree.otol.fetch_tree_from_synthesis(
    resolved,
    constrain_by_taxonomy=True,
    force_as_tips=True,
)
```

The older `fetch_newick_subtree_from_taxonomy` and `fetch_newick_induced_tree_otol` names remain as deprecated compatibility wrappers. They return Newick strings. New code should use the ToyTree-returning functions and call `tree.write(...)` explicitly when serialization is needed.

## Retrieve TimeTree ages safely

TimeTree queries use NCBI identifiers stored on the tree. Adjusted ages are preferred because TimeTree computes them to reconcile chronology across its global tree; the output retains adjusted and precomputed values, confidence limits, study counts, query pairs, and the selected source.

By default, independently queried parent-child conflicts are warned about but preserved, and unsupported nodes remain missing. This avoids silently turning separate estimates into a seemingly coherent chronogram. Use `on_conflict="adjust"` only when deterministic clipping is appropriate for the analysis, or `on_conflict="raise"` for strict validation. Optional imputation only interpolates between observed time anchors and never extrapolates a missing root.


```python
ages = toytree.otol.get_timetree_node_ages(
    synthesis_tree,
    endpoint="pairwise",
    max_pairs=3,
    age_source="adjusted",
    on_conflict="warn",
    impute_missing=False,
    on_error="warn",
)
ages
```

Pairwise representatives are sampled across different child clades, including balanced coverage of multifurcations. Set `on_error="raise"` when a failed remote request must stop the analysis rather than appear as an error row. The returned DataFrame is indexed in the input tree's internal-node order and the input tree is not mutated.

## Transport and cache configuration

OpenTree and TimeTree share retry and cache behavior. Selected JSON responses are cached atomically for seven days by default. Cache keys include the base URL, HTTP method, endpoint, and request payload; corrupt or expired files are treated as misses. A caller-provided `requests.Session` remains owned by the caller.


```python
toytree.otol.configure_client(timeout=30, cache=True, cache_ttl=7 * 24 * 3600)
toytree.otol.configure_timetree_client(
    timeout=30,
    cache=True,
    cache_ttl=7 * 24 * 3600,
)
```

## Raw JSON methods

Methods prefixed with `fetch_json_` expose validated raw endpoint payloads for specialized workflows. Their return structures are controlled by the remote service and may evolve; prefer the tree builders for ordinary topology construction.

## Citation and data use

Cite [OpenTree](https://tree.opentreeoflife.org/about/open-tree-of-life) for topology or taxonomy data and the [TimeTree resource paper](https://pmc.ncbi.nlm.nih.gov/articles/PMC9400175/) for divergence estimates. TimeTree's [current site and terms](https://timetree-api.temple.edu/about) permit personal research and teaching use, request contact for other uses, and restrict redistribution of its data and transformations. Review the current service terms before publishing or redistributing derived datasets. TimeTree estimates are provided as-is and should retain their provenance in downstream analyses.
