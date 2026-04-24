# CLI Pipeline Cookbook

This page focuses on shell pipelines that pass trees between `toytree` CLI
commands. The key decision is whether the pipeline should exchange tree data as
text or in binary transport form.

## Pipeline rules of thumb

- Use text when you want human-readable Newick / Nexus or need to interoperate
  with non-`toytree` tools.
- Use binary transport (`-b`) when the tree stays inside a `toytree` pipeline.
  This preserves feature types and avoids repeated metadata parsing.
- When a tree is piped into a command, input usually defaults to stdin. In most
  pipelines you do not need `-i -`.
- Use `toytree io` at the start or end of a pipeline when you need to control
  metadata syntax, convert binary to text, or emit Nexus.

## Text pipelines

Text pipelines are easiest to inspect and debug.

```bash
toytree root -i TREE.nwk -n OUTGROUP | toytree view --ladderize

toytree prune -i TREE.nwk -n A B C | toytree get -f name dist

toytree anc -i TREE.nwk -f X -n 3 -m ER | toytree get -f X_anc X_anc_posterior -s ','
```

## Binary pipelines

Binary transport is best when multiple `toytree` commands are chained and the
tree should keep in-memory feature types throughout the pipeline.

```bash
toytree rtree -n 500 -b \
  | toytree set -f group -s r0=A r1=B -d C -b \
  | toytree view --ascii
```

Another common pattern is to use binary in the middle of a longer workflow:

```bash
toytree io -i TREE.nwk -b \
  | toytree prune -n a b c -b \
  | toytree relabel --prepend 'X_' -b \
  | toytree io > OUT.nwk
```

## `toytree io` at pipeline boundaries

`toytree io` is the boundary tool for tree serialization. Use it when you need
to change output format without changing the tree itself.

```bash
# text -> binary
toytree io -i TREE.nwk -b > TREE.bin

# binary -> text
toytree io -i TREE.bin > TREE.nwk

# binary -> Nexus
toytree io -i TREE.bin --nexus -o TREE.nex
```

When converting back to text, the output is ordinary serialized tree data, for
example:

```output
((r0:1,r1:1):1,r2:2);
```

## NHX-like metadata workflows

Use `toytree io` to convert standard extended Newick comments to an NHX-like
style, or to parse NHX-like input using custom delimiters.

```bash
# write NHX-like output
toytree anc -i TREE.nwk -f X -n 3 -m ER \
  | toytree io -fp '&&NHX:' -fd ':' -fa '=' > TREE.anc.nhx

# parse NHX-like input
toytree io -i TREE.anc.nhx \
  --in-feature-prefix '&&NHX:' \
  --in-feature-delim ':' \
  --in-feature-assignment '=' \
  --in-feature-unpack '|' \
  > TREE.roundtrip.nwk
```

If a metadata feature stores list-like values, `toytree io` can control how
they are packed and unpacked in text comments:

```bash
# custom pack token on output
toytree io -i TREE.bin --features-pack ';' > TREE.custom.nwk

# matching unpack token on input
toytree io -i TREE.custom.nwk --in-feature-unpack ';' > TREE.roundtrip.nwk
```

## Single-feature `name{value}` output

`toytree io --write-single-feature` writes one feature on every node in a
curly-brace label form, `name{value}`.

```bash
toytree set -i TREE.nwk -f trait -s a=1 b=2 -d 0 -b \
  | toytree io --write-single-feature trait > TREE.curly.nwk
```

This format is useful for compact export when a single feature should travel
with the node label itself rather than with comment metadata.

## Ancestral-state reconstruction pipelines

`anc-state-discrete` writes reconstructed states back onto the tree as
metadata, so there are two common downstream patterns:

```bash
# keep the tree and inspect reconstruction later
toytree anc -i TREE.nwk -f X -n 3 -m ER > TREE.anc.nwk

# emit a node table directly
toytree anc -i TREE.nwk -f X -n 3 -m ER \
  | toytree get -f X_anc X_anc_posterior -H

# keep binary transport and extract only the MAP states
toytree anc -i TREE.nwk -f X -n 3 -b | toytree get -f X_anc
```

If the input feature already includes internal-node states, those states are
treated as fixed constraints and the command writes a warning to stderr.

## JSON outputs for scripting

Several commands support `--json` for structured downstream use.

### `get-node-data --json`

```bash
toytree get -i TREE.nwk -f name dist --json
```

This returns a JSON object in pandas `orient="index"` form, keyed by the
dataframe row index.

### `distance --json`

```bash
toytree distance -i T1.nwk -j T2.nwk -m rf --json
toytree distance -i T1.nwk -j T2.nwk -m quartet-all --json
```

### Model summaries on stderr

Some model-fitting commands keep tree output on stdout and write JSON summaries
to stderr.

```bash
toytree anc -i TREE.nwk -f X -n 3 --json > TREE.anc.nwk 2> fit.json

toytree make-ultrametric -i TREE.nwk -m correlated --lam 0.5 --json \
  > UTREE.nwk 2> ultrametric-fit.json
```

## Inspecting intermediate results

`tee` is useful when you want to keep a binary intermediate without breaking
the pipeline.

```bash
toytree rtree -n 200 -b \
  | tee /tmp/tree.bin \
  | toytree prune -n r0 r1 r2 -b \
  | toytree io > PRUNED.nwk

toytree io -i /tmp/tree.bin > INTERMEDIATE.nwk
```
