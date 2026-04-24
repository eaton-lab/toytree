# Command Line

The `toytree` command-line interface is designed for two complementary jobs:

- run one command against a Newick or Nexus file;
- build shell pipelines where several `toytree` commands pass trees through
  stdin and stdout.

Most commands read one tree, write one tree or table, and keep the syntax
close to the corresponding Python API. When you want exact flag details, start
with `toytree <command> -h`. This page focuses on common workflows and the
commands most users reach for first.

Examples that generate random trees use `--seed 123` so the text outputs below
stay reproducible.

## Start with help

At the top level, `toytree -h` shows the available subcommands and their
one-line purpose.

```bash
toytree -h
```

```output
usage: toytree [subcommand] --help

----------------------------------------------------------
|  toytree: phylogenetic tree toolkit                   |
----------------------------------------------------------

options:
  -h, --help                show this help message and exit
  -v, --version             show program's version number and exit

subcommands:
  {get-node-data,set-node-data,io,view,draw,rtree,root,prune,distance,make-ultrametric,anc-state-discrete,consensus,relabel}
    get-node-data           return table of node feature data from a tree
    set-node-data           set node features on a tree and return updated newick
    io                      convert tree data between binary/Newick/Nexus with NHX metadata
    view                    print tree as unicode or ASCII text
    draw                    render styled tree figures in graphic formats
    rtree                   generate random trees from toytree.rtree methods
    root                    root a tree using outgroup, MAD, or DLC optimization
    prune                   return tree connecting only the selected tip names
    distance                compute a distance between two trees
    make-ultrametric        make a tree ultrametric using fast or penalized-likelihood methods
    anc-state-discrete      fit a discrete CTMC model and write ancestral-state metadata to tree output
    consensus               infer a consensus tree from a multi-tree input
    relabel                 relabel node name features for all nodes or selected subsets

Tutorials
---------
https://eaton-lab.org/toytree/
```

## CLI conventions

### Unambiguous command prefixes

Top-level subcommands can be abbreviated to any unambiguous prefix. These all
work:

```bash
toytree get -h
toytree set -h
toytree anc -h
```

The documentation uses canonical command names for clarity, but short prefixes
are convenient in interactive shell use.

### Input usually defaults to stdin when piped

When a tree is already flowing through a pipeline, `-i -` is often optional.
That keeps pipelines short:

```bash
toytree rtree -n 20 | toytree view
toytree root -i TREE.nwk -n OUTGROUP | toytree get-node-data -f name dist
```

### Use binary transport when the tree stays inside `toytree`

For speed improvements, especially on large trees, use `-b` / `--binary-out`
when several `toytree` commands are chained together and the tree does not need
to become human-readable in the middle of the pipeline. Binary transport avoids
repeated Newick parsing and alleviates the need to serialize feature data to text
in between commands.

```bash
toytree rtree -n 20 -b \
  | toytree set-node-data -f group -s r0=A r1=B -d C -b \
  | toytree view -y group=B -Y
```

### Use `toytree io` at text boundaries

Most commands focus on tree operations. `toytree io` is a useful boundary tool for:

- converting between binary, Newick, and Nexus;
- setting NHX-style metadata formatting;
- controlling list pack / unpack tokens;
- writing to single-feature format with `name{value}` labels.

If you need to move from a `toytree` pipeline back to plain text, or vice
versa, `io` is often useful.

## Command map

| Command | When to use it | Typical output |
| --- | --- | --- |
| `view` | Inspect a tree as plain text in the terminal | Unicode or ASCII tree |
| `draw` | Render graphic output for notebooks, files, or a browser | svg, png, pdf, html |
| `rtree` | Generate random example or test trees | Newick text or binary tree |
| `root` | Root by outgroup or infer a root by MAD / DLC | rooted tree |
| `prune` | Keep only selected tips | smaller tree |
| `relabel` | Clean or transform node names | updated tree |
| `get-node-data` | Inspect node features as a table or JSON | text table or JSON |
| `set-node-data` | Add node or edge features from mappings or a file | updated tree |
| `io` | Convert formats and control metadata syntax | Newick, Nexus, or binary |
| `distance` | Compare two trees | scalar result or JSON |
| `make-ultrametric` | Adjust branch lengths to be ultrametric | ultrametric tree |
| `anc-state-discrete` | Fit a discrete CTMC and write reconstructed states | tree with metadata |
| `consensus` | Summarize many trees as one consensus tree | consensus tree |

## `view`: inspect trees in the terminal

`view` prints a text rendering directly to stdout. It is the fastest way to
inspect a tree from the shell, including both topology and relative edge lengths,
and can even display one feature trait at a time.

- Unicode is the default.
- `--ascii` switches to plain ASCII line drawing.
- `--ladderize` reorders clades for display only.
- `--tip-labels` and `--use-edge-lengths` control how much detail is shown.
- `--heavy` and `--heavier` emphasize edges matching a feature query.

### Default Unicode tree

```bash
toytree rtree -n 10 --seed 123 | toytree view
```

```output
             ┌─────────r0
    ┌────────┤
    │        └─────────r1
    │
┌───┤                 ┌─────────r2
│   │        ┌────────┤
│   │        │        └─────────r3
│   └────────┤
│            │        ┌─────────r4
│            └────────┤
│                     └─────────r5
│
│   ┌─────────r6
└───┤
    │        ┌─────────r7
    └────────┤
             │        ┌─────────r8
             └────────┤
                      └─────────r9
```

### ASCII fallback
If unicode cannot be rendered unicode is a safe fallback that should work everywhere.

```bash
toytree rtree -n 10 --seed 123 | toytree view --ascii
```

```output
             /---------r0
    /--------+
    |        \---------r1
    |
/---+                 /---------r2
|   |        /--------+
|   |        |        \---------r3
|   \--------+
|            |        /---------r4
|            \--------+
|                     \---------r5
|
|   /---------r6
\---+
    |        /---------r7
    \--------+
             |        /---------r8
             \--------+
                      \---------r9
```

### Feature trait
A trait value can be shown on a tree by selecting edges matching a query using
``--heavy``. For greater emphasis add ``--heavier``.

```bash
# emphasize edges that match a query (e.g., high support edges)
toytree view -i TREE.nwk --heavy 'support>95'

# heavier emphasis on edges matching a query
toytree rtree -n 10 -m u -s 123 | toytree view --heavy 'dist>0.2' --heavier
```

```output
   ┌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒r0
┌──┤
│  │      ┌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒r1
│  └──────┤
│         └▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒r2
│
│                ┌──────────────r3
│         ┌──────┤
│  ┌──────┤      └──────────────r4
│  │      │
└──┤      └▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒r5
   │
   │      ┌▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒r6
   └──────┤
          │      ┌──────────────r7
          └──────┤
                 │      ┌───────r8
                 └──────┤
                        └───────r9
```

Other useful patterns:

```bash
# show a ladderized display without changing the tree data
toytree view -i TREE.nwk --ladderize

# view topology easier by using equal edge lengths w/ tips aligned
toytree view -i TREE.nwk --use-edge-lengths false
```

## `draw`: render graphic output

`draw` is the more powerful graphics-oriented command. This can generate the fully
styled drawings that are possible from the Python API, and write the results to svg,
png, pdf, or html figures. The ``-v`` option selects the default program to automatically
open the file for viewing, depending on its format.

```bash
toytree draw -i TREE.nwk -o tree.svg
toytree draw -i TREE.nwk -f png --view
toytree rtree -n 20 | toytree draw -v
```

This command supports rich options to style the nodes, edges, tips, layout, and other
formatting options.


## `rtree`: generate example trees

`rtree` exposes the tree generators in `toytree.rtree`. The
`-m/--method` flag accepts full names or unambiguous prefixes such as
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

## `root`, `prune`, and `relabel`: modify trees

These commands change tree structure or labels and then emit another tree.

### `root`

Use `root` to root by outgroup or infer a root using optimization criteria.

- `--mad`: minimal ancestor deviation rooting.
- `--dlc`: minimal deep-coalescence-style rooting criterion.

```bash
toytree root -i TREE.nwk -n A B C > ROOTED.nwk
toytree root -i TREE.nwk --mad > ROOTED.nwk
toytree root -i TREE.nwk --dlc --species-tree SPECIES.nwk > ROOTED.nwk
```

### `prune`

`prune` keeps only selected tips and the minimal connecting topology.

```bash
toytree prune -i TREE.nwk -n A B C D > PRUNED.nwk
toytree prune -i TREE.nwk -n '~^cladeA' '~^cladeB' -o PRUNED.nwk
```
```bash
toytree rtree -n 4 --seed 123 | toytree prune -n r0 r1 r2 | toytree io
```

```output
(r0:1,(r1:1,r2:1):1);
```

### `relabel`

Use `relabel` to clean or rewrite names before plotting, exporting, or joining
against external data.

```bash
toytree relabel -i TREE.nwk --strip '_-'
toytree relabel -i TREE.nwk --delim '|' --delim-idxs 0 2 --delim-join '_'
toytree relabel -i TREE.nwk -n '~^DE' --append '_X'
toytree relabel -i TREE.nwk --italic --bold
```

## `get/set` node data

These two commands are the CLI equivalents of reading and writing node
features.

### `get-node-data`

`get-node-data` returns node features as delimited text, a human-readable
table, or JSON. It is often the easiest way to inspect the tree after a
pipeline step.

```bash
toytree rtree -n 6 --seed 123 | toytree get-node-data -f name dist -H
```

```output
   name  dist
0    r0   1.0
1    r1   1.0
2    r2   1.0
3    r3   1.0
4    r4   1.0
5    r5   1.0
6         1.0
7         1.0
8         0.5
9         0.5
10        0.0
```

Internal nodes appear too unless you add `-t/--tips-only`.

```bash
toytree get-node-data -i TREE.nwk
toytree get-node-data -i TREE.nwk -H
toytree get-node-data -i TREE.nwk -n A B C -f name dist support
toytree get-node-data -i TREE.nwk -f dist -N
toytree get-node-data -i TREE.nwk -f name dist --json
```

`-N/--index-by-name` uses node names as the row index, but falls back to node
idx when names are empty.

### `set-node-data`

`set-node-data` stores values on nodes or edges. Use mapping mode for quick
one-off edits and table mode when values already live in a TSV or CSV file.

```bash
# mapping mode
toytree set-node-data -i TREE.nwk -f group -s a=1 b=2 -d 0 > OUT.nwk
toytree set-node-data -i TREE.nwk -f rate -s 10=0.1 11=0.2 --edge > OUT.nwk

# table mode
toytree set-node-data -i TREE.nwk --table data.tsv --table-sep '\t' > OUT.nwk
toytree set-node-data -i TREE.nwk --table data.tsv --table-query-column id
```

```bash
# pipeline example
toytree rtree -n 4 --seed 123 \
  | toytree set-node-data -f group -s r0=A r1=B -d C \
  | toytree io
```

```output
((r0[&group=A]:1,(r1[&group=B]:1,r2[&group=C]:1)[&group=C]:1)[&group=C]:0.5,r3[&group=C]:0.5)[&group=C];
```

When the goal is metadata syntax rather than metadata values, keep
`set-node-data` focused on annotation and pipe the result into `toytree io` has
more options for how to format the NHX.

## `io`: convert tree formats and metadata syntax

`io` is the dedicated tree I/O command. Use it when you need a format
conversion without changing the tree itself.

```bash
toytree rtree -n 4 --seed 123 | toytree io
```

```output
((r0:1,(r1:1,r2:1):1):0.5,r3:0.5);
```

Common uses:

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

`io` also controls custom list pack and unpack tokens:

```bash
toytree io -i TREE.nhx \
  --in-feature-prefix '&&NHX:' \
  --in-feature-delim ':' \
  --in-feature-assignment '=' \
  --in-feature-unpack '|' \
  > TREE.nwk

toytree io -i TREE.bin --features-pack ';' > TREE.custom.nwk
toytree io -i TREE.custom.nwk --in-feature-unpack ';' > TREE.roundtrip.nwk
```

## `distance`, `make-ultrametric`, `anc-state-discrete`, and `consensus`

These commands are more analysis-oriented but follow the same CLI pattern:
read one tree or tree collection, perform one focused operation, and write the
result to stdout unless `-o/--output` says otherwise.

### `distance`

Compare two trees with Robinson-Foulds, generalized RF, or quartet metrics.

```bash
toytree distance -i TREE1.nwk -j TREE2.nwk -m rf
toytree distance -i TREE1.nwk -j TREE2.nwk -m rfg_mci --normalize
toytree distance -i TREE1.nwk -j TREE2.nwk -m quartet --quartet-metric symmetric_difference
toytree distance -i TREE1.nwk -j TREE2.nwk -m quartet-all --json
```

### `make-ultrametric`

Convert branch lengths to an ultrametric tree using a fast extension method or
one of the penalized-likelihood models.

```bash
toytree make-ultrametric -i TREE.nwk -m extend > UTREE.nwk
toytree make-ultrametric -i TREE.nwk -m relaxed --lam 0.5 > UTREE.nwk
toytree make-ultrametric -i TREE.nwk -m correlated --lam 0.5 --nstarts 8 --ncores 4 --seed 123 > UTREE.nwk
```

### `anc-state-discrete`

Fit a discrete CTMC model (`ER`, `SYM`, or `ARD`) to a feature already stored
on the tree and write reconstructed states back onto the tree.

- `{feature}_anc`: MAP state at each node.
- `{feature}_anc_posterior`: packed posterior probabilities at each node.

```bash
# simulate random tree, add trait X to tips,
toytree rtree -n 10 -s 123 \
  | toytree set -f X -s '~r[0-5]=A' '~r[6-9]=B' \
  | toytree anc -f X -n 2 -m ER \
  > TREE.anc.nwk
```

```output
(((r0[&X_anc=A,X_anc_posterior=1|0,X=A]:1,r1[&X_anc=A,X_anc_posterior=1|0,X=A]:1)[&X_anc=A,X_anc_posterior=0.994583482788|0.0054165172122]:1,((r2[&X_anc=A,X_anc_posterior=1|0,X=A]:1,r3[&X_anc=A,X_anc_posterior=1|0,X=A]:1)[&X_anc=A,X_anc_posterior=0.999179502126|0.000820497874258]:1,(r4[&X_anc=A,X_anc_posterior=1|0,X=A]:1,r5[&X_anc=A,X_anc_posterior=1|0,X=A]:1)[&X_anc=A,X_anc_posterior=0.999179502126|0.000820497874258]:1)[&X_anc=A,X_anc_posterior=0.993821269148|0.00617873085181]:1)[&X_anc=A,X_anc_posterior=0.926420660726|0.0735793392744]:0.5,(r6[&X_anc=B,X_anc_posterior=0|1,X=B]:1,(r7[&X_anc=B,X_anc_posterior=0|1,X=B]:1,(r8[&X_anc=B,X_anc_posterior=0|1,X=B]:1,r9[&X_anc=B,X_anc_posterior=0|1,X=B]:1)[&X_anc=B,X_anc_posterior=0.000767001919383|0.999232998081]:1)[&X_anc=B,X_anc_posterior=0.00539421285013|0.99460578715]:1)[&X_anc=B,X_anc_posterior=0.0681987790081|0.931801220992]:0.5)[&X_anc=B,X_anc_posterior=0.497317024197|0.502682975803];
```

If the input already contains internal-node states for the same feature, those
states are treated as fixed constraints and the command writes a warning to
stderr.

### `consensus`

Read a multi-tree input and return a consensus tree, optionally carrying
selected node or edge features onto the consensus result.

```bash
toytree consensus -i TREES.nwk
toytree consensus -i TREES.nwk -m 0.5
toytree consensus -i TREES.nwk --edge-features dist support
toytree consensus -i TREES.nwk --features height --ultrametric
```

## More pipeline examples

For deeper examples of binary transport, NHX-like metadata conversion, JSON
stderr summaries, and mixed text/binary workflows, see
[CLI pipelines](cli-pipelines.md).
