---
section: Getting Started
---

The changelog will be updated on each packaged release beginning with 
`toytree` v.3.0. Please see the GitHub repo for more detailed commit 
messages and the history prior to v.3.0.


### 2023/6/5 (v.3.0.0)
- new unittest framework for testing methods on GitHub CI.
- new subpackage structure to organize growing code base.
- new functools wrap to keep API and module-level methods synced.
- `cli` New CLI for fast tree drawings in browser `toytree --ts p --width X --height Y`
- `color` New ToyColor module for easier color type validation and conversion.
- `io` Improved inference of internal label type in `toytree.tree`
- `io` Support defaults to np.nan if not present in parsed tree.
- `io` Completely new newick parser function. More flexible parsing.
- `io` Nexus parser can handle more types of nexus formatting.
- `io` Show informative message on NHX parsing errors/formatting. 
- `io` Write Node and Edge features separately to NHX format.
- `distance` separated tree and node distance methods in submodules.
- `distance` new faster node distance functions for path, up or down.
- `distance` much faster algorithm for computing node distances.
- `distance` bipartition based tree distance functions developed and tested.
- `distance` quartet based tree distance functions developed and tested.
- `mod` new rooting functions including minimal ancestor deviation (MAD).
- `mod` added unittests for root and mod methods across wide variety of cases.
- `core` set default Node.dist to 0, including for root on random trees.
- `core` implemented new generic Node query method. Replace regex arg w/ "~name".
- `core` simplified Node object, exposed iter functions, made edit funcs private.
- `core` ToyTree now has `.edge_features` set to store default and additional features
that should be treated as edge data. Edge data in NHX is stored as such.
- `enum` created enum subpackage to group partition iterators and counters.
- `data` replaced `get_node_values` with `get_node_data`.
- `data` missing values in Node data default to np.nan on `get_node_data()`
- `data` new expand_node_mapping for faster expansion of Node queries w/ regex.
- `drawing` renamed ToytreeMark to ToyTreeMark
- `drawing` Use text extents when auto-building canvas size.
- `drawing` Store tip coords in layout/ToyTreeMark for extents, tip angles, etc.
- `drawing` used aspect='fit-range' on circular layouts.
- `drawing` bugfix for circular trees 'p' edge type SVG paths.
- `drawing` bugfix to allow ts='p' with new validators when no Ne feature.
- `drawing` unrooted layout EA or ED algorithms with improved tip angles.
- `style` New TreeStyle serialization and validation is faster and easier to debug.
- `style` general color_mapping approach developed as (feature, ...).
- `style` general value_mapping approach developed as (feature, ...). Replace `normalize_values`.
- `style` create a 'b' builtin style for showing support values easily.
- `style` use same validation method for tip and node data w/ `size` arg.
- `annotate` New annotation subpackage created for extensible add-on plots.
- `annotate` Basic Node/Edge annotation drawing methods developed.
- `annotate` Pie charts and general rectangle/bar methods developed.
- `annotate` Custom Marks to allow for shift in px units, not just data units.
- `annotate` moved `add_scale_bar` and `axes_styling` methods to annotate.
- `pcm` continuous and discrete brownian sim funcs w/ similar syntax.
- `network` network parsing module.

------------------------------------------------------------

