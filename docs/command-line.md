# Command Line Interface

The `toytree` CLI provides tree generation, manipulation, reporting, model
fitting, and rendering from the shell. It is designed for two modes of use:

- direct single-command work on Newick / Nexus files;
- fast shell pipelines where commands exchange trees through stdin/stdout.

Run top-level help:

```bash
toytree -h
```

## CLI conventions

### Unambiguous command prefixes

Top-level subcommands can be abbreviated to any unambiguous prefix. For
example, the following are valid:

```bash
toytree get -h
toytree set -h
toytree anc -h
```

The canonical command names are still used in help text and section headings
below.

### Input defaults to stdin when piped

When a tree is piped into a command, `-i -` is usually unnecessary. This makes
pipelines shorter:

```bash
toytree rtree -n 20 | toytree draw -v
toytree root -i TREE.nwk -n OUTGROUP | toytree get -f name dist
```

### Binary transport for pipelines

Use `-b` / `--binary-out` when the tree stays inside a `toytree` pipeline.
Binary transport preserves in-memory feature types and avoids repeated text
serialization and parsing.

```bash
toytree rtree -n 200 -b | toytree set -f group -s r0=A r1=B -d C -b | toytree draw -a
```

### Use `toytree io` at text boundaries

Most commands focus on tree operations. Use `toytree io` when you need to:

- convert between binary, Newick, and Nexus;
- change metadata comment formatting;
- parse or emit NHX-like metadata styles;
- write a single node feature as `name{value}` labels.

## Command overview

- `draw`: render trees as ASCII or graphics.
- `rtree`: generate random trees from `toytree.rtree`.
- `root`: root by outgroup query or infer roots by MAD or DLC.
- `prune`: keep selected tips and the minimal connecting structure.
- `relabel`: transform node name features using split / strip / prepend /
  append rules.
- `get-node-data`: return node features as a table or JSON.
- `set-node-data`: store node or edge features from mappings or tables.
- `io`: convert tree I/O formats and control metadata parsing / writing.
- `distance`: compute distances between two trees.
- `make-ultrametric`: transform branch lengths to an ultrametric tree.
- `anc-state-discrete`: fit a discrete CTMC model and reconstruct ancestral
  states.
- `consensus`: infer a consensus tree from a multi-tree input.

## `draw`

`draw` prints an ASCII tree by default. Use `--output` and / or `--view` for
graphic output.

```bash
# ASCII to stdout
toytree draw -i TREE.nwk

# graphic output
toytree draw -i TREE.nwk -o tree.svg
toytree draw -i TREE.nwk -f png --view

# from a pipeline
toytree rtree -n 20 | toytree draw -v
```

## `rtree`

`rtree` exposes several tree generators from `toytree.rtree`. The
`-m/--method` argument accepts full names or unambiguous prefixes such as
`-m u` for `unittree` and `-m bd` for `bdtree`.

```bash
# default random bifurcating topology
toytree rtree -n 10 --seed 123 > TREE.nwk

# ultrametric random tree with target height
toytree rtree --method unittree -n 20 --treeheight 5 --seed 123 > TREE.nwk

# birth-death simulation
toytree rtree --method bdtree -n 25 --b 1.0 --d 0.2 --stop taxa --stats > TREE.nwk

# coalescent simulation
toytree rtree --method coaltree -n 16 --N 500 --seed 7 > TREE.nwk
```

## `root`

`root` can root by named outgroup or infer a root using optimization-based
criteria.

- `--mad`: minimal ancestor deviation rooting.
- `--dlc`: minimal deep-coalescence style rooting criterion.

```bash
# outgroup rooting
toytree root -i TREE.nwk -n A B C > ROOTED.nwk

# optimization-based rooting
toytree root -i TREE.nwk --mad > ROOTED.nwk
toytree root -i TREE.nwk --dlc --species-tree SPECIES.nwk > ROOTED.nwk
```

## `prune`

`prune` keeps only selected tips and the minimal connecting topology.

```bash
toytree prune -i TREE.nwk -n A B C D > PRUNED.nwk
toytree prune -i TREE.nwk -n '~^cladeA' '~^cladeB' -o PRUNED.nwk
```

## `relabel`

`relabel` modifies node name features using text rules. It is useful for
cleaning tip labels before plotting or exporting.

```bash
toytree relabel -i TREE.nwk --strip '_-'
toytree relabel -i TREE.nwk --delim '|' --delim-idxs 0 2 --delim-join '_'
toytree relabel -i TREE.nwk -n '~^DE' --append '_X'
toytree relabel -i TREE.nwk --italic --bold
```

## `get-node-data`

`get-node-data` returns node features as delimited text, a human-readable
table, or JSON.

```bash
toytree get -i TREE.nwk
toytree get -i TREE.nwk -H
toytree get -i TREE.nwk -n A B C -f name dist support
toytree get -i TREE.nwk -f dist -N
toytree get -i TREE.nwk -f name dist --json
```

`-N/--index-by-name` uses node names as the row index, but falls back to node
idx where names are empty.

## `set-node-data`

`set-node-data` stores feature values on nodes or edges. Values can come from
explicit `query=value` mappings or from a tabular file.

```bash
# mapping mode
toytree set -i TREE.nwk -f group -s a=1 b=2 -d 0 > OUT.nwk
toytree set -i TREE.nwk -f rate -s 10=0.1 11=0.2 --edge > OUT.nwk

# table mode
toytree set -i TREE.nwk --table data.tsv --table-sep '\t' > OUT.nwk
toytree set -i TREE.nwk --table data.tsv --table-query-column id
```

For metadata formatting, pipe the result into `toytree io` rather than
changing output syntax here.

## `io`

`io` is the dedicated boundary tool for converting tree text / binary formats
and controlling metadata syntax.

```bash
# text to binary
toytree io -i TREE.nwk -b > TREE.bin

# binary back to Newick
toytree io -i TREE.bin > TREE.nwk

# write Nexus
toytree io -i TREE.bin --nexus -o TREE.nex

# write NHX-like metadata
toytree io -i TREE.bin -fp '&&NHX:' -fd ':' -fa '=' > TREE.nhx

# write one feature as name{value}
toytree io -i TREE.bin --write-single-feature X > TREE.curly.nwk
```

`io` also supports custom list pack / unpack tokens:

```bash
toytree io -i TREE.nhx --in-feature-prefix '&&NHX:' --in-feature-delim ':' \
  --in-feature-assignment '=' --in-feature-unpack '|' > TREE.nwk
```

## `distance`

`distance` compares two trees using Robinson-Foulds, generalized RF, and
quartet-based metrics.

```bash
toytree distance -i TREE1.nwk -j TREE2.nwk -m rf
toytree distance -i TREE1.nwk -j TREE2.nwk -m rfg_mci --normalize
toytree distance -i TREE1.nwk -j TREE2.nwk -m quartet --quartet-metric symmetric_difference
toytree distance -i TREE1.nwk -j TREE2.nwk -m quartet-all --json
```

## `make-ultrametric`

`make-ultrametric` provides fast edge-extension alignment and several
penalized-likelihood models.

```bash
# fast alignment method
toytree make-ultrametric -i TREE.nwk -m extend > UTREE.nwk

# penalized-likelihood methods
toytree make-ultrametric -i TREE.nwk -m relaxed --lam 0.5 > UTREE.nwk
toytree make-ultrametric -i TREE.nwk -m correlated --lam 0.5 --nstarts 8 --ncores 4 --seed 123 > UTREE.nwk
```

## `anc-state-discrete`

`anc-state-discrete` fits a discrete CTMC model (`ER`, `SYM`, or `ARD`) to a
feature already stored on the tree, then writes:

- `{feature}_anc`: MAP state at each node;
- `{feature}_anc_posterior`: packed posterior probabilities for each node.

If the input feature already contains non-missing internal-node states, those
states are treated as fixed constraints and a warning is written to stderr.

```bash
# reconstruct ancestral states
toytree anc -i TREE.nwk -f X -n 3 -m ER > TREE.anc.nwk

# extract a table of reconstructed states
toytree anc -i TREE.nwk -f X -n 3 -m ARD | toytree get -f X_anc X_anc_posterior -s ','

# convert metadata comments to NHX-like output
toytree anc -i TREE.nwk -f X -n 3 -m ER \
  | toytree io -fp '&&NHX:' -fd ':' -fa '=' > TREE.anc.nhx

# binary pipeline
toytree anc -i TREE.nwk -f X -n 3 -b | toytree get -f X_anc

# model-fit summary as JSON on stderr
toytree anc -i TREE.nwk -f X -n 3 --json > TREE.anc.nwk 2> fit.json
```

## `consensus`

`consensus` reads a multi-tree input and returns a consensus tree. It can also
map selected node or edge features from the source trees onto the consensus.

```bash
toytree consensus -i TREES.nwk
toytree consensus -i TREES.nwk -m 0.5
toytree consensus -i TREES.nwk --edge-features dist support
toytree consensus -i TREES.nwk --features height --ultrametric
```

## More pipeline examples

For binary/text transport patterns, metadata conversion, and JSON-oriented
examples, see [CLI pipelines](cli-pipelines.md).
