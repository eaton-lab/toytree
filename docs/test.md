---
section: User Guide
---

# Tree I/O

Tree data in its simplest form is very simple.
Metadata can be very rich.
Formats for storing trees has evolved over time.
tldr; the `toytree.tree` function can flexibly parse most formats.
newick, nexus, and NHX format.

``` py
import toytree
```

## Parsing <i>tldr;</i>


``` py
# a simple newick string
NEWICK = "(((a,b),c),d);"

# load newick as a ToyTree object
tree = toytree.tree(NEWICK)
print(tree)
```

```yaml
...
```

## From a string



## From a file



## From a URL