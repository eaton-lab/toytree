<div class="nb-md-page-hook" aria-hidden="true"></div>

# Writing tree data

`tree.write()` turns a `ToyTree` back into plain text, such as Newick formatted tree data. That text can be saved to a file, copied into another program, or inspected directly as text when you want to see exactly what will be exported.

In most cases you will either call `tree.write()` to get a string or `tree.write(path=...)` to save a file. The same method can also include branch lengths, internal labels, extra metadata, or a NEXUS wrapper when you need them.


```python
import numpy as np
import toytree
```


```python
# get a balanced 4-tip tree
tree = toytree.rtree.baltree(ntips=4)

# write the tree to serialized newick format
tree.write()
```




    '((r0:0.5,r1:0.5):0.5,(r2:0.5,r3:0.5):0.5);'



<div class="admonition tip">
  <p class="admonition-title">Take Home</p>
  <p>
      Start with <code>tree.write()</code> when you want a text version of a tree. Add <code>path=...</code> to save it, <code>features=[...]</code> to include metadata, or <code>nexus=True</code> when another tool expects NEXUS.
  </p>
</div>

## Example tree
The examples below all use one small tree with a few extra values already stored on it. That makes it easier to see what changes when we write plain Newick, include internal labels, or add metadata.

Here the tips already have names, the internal nodes have names like `A` and `B`, support values are stored on internal edges, and there is one extra numeric feature named `X`. You do not need all of that data in normal use, but it gives us something concrete to work with.


```python
# add internal node names as "A"
tree.set_node_data("name", {4: "A", 5: "B", 6: "C"}, inplace=True)

# add internal node support values as 100
tree.set_node_data("support", {4: 100, 5: 90}, inplace=True)

# add X as node feature with random float values
tree.set_node_data("X", np.random.normal(0, 2, tree.nnodes), inplace=True)

# show the tree data
tree.get_node_data()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>idx</th>
      <th>name</th>
      <th>height</th>
      <th>dist</th>
      <th>support</th>
      <th>X</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>r0</td>
      <td>0.0</td>
      <td>0.5</td>
      <td>NaN</td>
      <td>-3.351227</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>r1</td>
      <td>0.0</td>
      <td>0.5</td>
      <td>NaN</td>
      <td>2.830278</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>r2</td>
      <td>0.0</td>
      <td>0.5</td>
      <td>NaN</td>
      <td>1.277740</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>r3</td>
      <td>0.0</td>
      <td>0.5</td>
      <td>NaN</td>
      <td>1.365754</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>A</td>
      <td>0.5</td>
      <td>0.5</td>
      <td>100.0</td>
      <td>-0.719738</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td>B</td>
      <td>0.5</td>
      <td>0.5</td>
      <td>90.0</td>
      <td>1.806481</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td>C</td>
      <td>1.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>-0.279087</td>
    </tr>
  </tbody>
</table>
</div>



## Defaults
If you call `tree.write()` with no extra arguments, `toytree` gives you a Newick string. That output usually includes branch lengths, and if the tree has support values they are written in the internal-label position.

The default internal-label setting is `internal_labels="support"`, which is why support values appear in the examples below when they are available on the tree.

This default is a good place to start because it matches what many other phylogenetics tools expect. From there, you can simplify the output or make it more detailed depending on what you need.


```python
# Newick str from using default arguments to write()
tree.write()
```




    '((r0:0.5,r1:0.5)100:0.5,(r2:0.5,r3:0.5)90:0.5);'



## Save a file
By default, `tree.write()` returns a string. If you want to create a file instead, pass `path=...`.

That gives you two very common workflows:

- use `tree.write()` when you want the text in Python;
- use `tree.write(path="example.nwk")` when you want a file on disk.

The `path` argument accepts a normal string path, a `pathlib.Path`, or `None`. When a file is written successfully the method returns `None`. If the destination cannot be written, `toytree` raises `ToytreeError`.


```python
# write to a file path
tree.write(path="/tmp/example.nwk")
```

## Plain Newick
Newick is the simplest and most widely used tree text format. If you only need topology, tip names, branch lengths, and maybe internal labels, this is usually the right output format.

To demonstrate formatting options we will start simple and then add detail back in. We will start by writing just the topology to check the structure of the tree, then add branch lengths and/or internal labels. 

The shorter positional form shown below works for this, but keyword arguments are usually clearer and are the better choice in scripts and shared examples.


```python
# write topology only set these args to None
tree.write(path=None, dist_formatter=None, internal_labels=None)
```




    '((r0,r1),(r2,r3));'




```python
# short-hand for simplest tree serialization
tree.write(None, None, None)
```




    '((r0,r1),(r2,r3));'



### Branch lengths
Branch lengths are often useful, but they can also make the text harder to scan when you only care about topology. Set `dist_formatter=None` to hide them.

If you do want branch lengths, `dist_formatter` lets you decide how they should look. This is useful when the raw values are longer than you want to show in a file or in an example. `toytree` accepts normal Python format strings such as `"%.2f"` or `"{:.4g}"`. Invalid format strings raise `ToytreeError`.

In the examples below, `internal_labels=None` is only there to keep the comparison focused on the branch lengths.


```python
# hide edge lengths
tree.write(dist_formatter=None, internal_labels=None)
```




    '((r0,r1),(r2,r3));'




```python
# format edge lengths to show two fixed floating points
tree.write(dist_formatter="%.2f", internal_labels=None)
```




    '((r0:0.50,r1:0.50):0.50,(r2:0.50,r3:0.50):0.50);'




```python
# format edge lengths to show max 4 floating points
tree.write(dist_formatter="%.4g", internal_labels=None)
```




    '((r0:0.5,r1:0.5):0.5,(r2:0.5,r3:0.5):0.5);'




```python
# format edge lengths as integers
tree.write(dist_formatter="%d", internal_labels=None)
```




    '((r0:0,r1:0):0,(r2:0,r3:0):0);'



### Internal labels
The `internal_labels` argument answers a simple question: if something should be written at internal nodes, which stored feature should be used?

By default, `toytree` uses `internal_labels="support"`.

Two common choices are:

- `internal_labels="support"` to write support values;
- `internal_labels="name"` to write internal node names.

You can also set any another feature to be stored on internal nodes, but it is generally better use the metadata assignment option described below, and keep the internal label position only for 'name' or 'support'.

If the selected feature is missing from every internal node, `toytree` raises `ToytreeError` instead of quietly writing something incomplete.

Here `dist_formatter=None` is only used to keep the examples visually simple.


```python
# None excludes internal labels
tree.write(dist_formatter=None, internal_labels=None)
```




    '((r0,r1),(r2,r3));'




```python
# use support floats as internal labels
tree.write(dist_formatter=None, internal_labels="support")
```




    '((r0,r1)100,(r2,r3)90);'




```python
# use name str as internal labels
tree.write(dist_formatter=None, internal_labels="name")
```




    '((r0,r1)A,(r2,r3)B)C;'




```python
# use other existing feature in tree as internal labels
tree.write(dist_formatter=None, internal_labels="X")
```




    '((r0,r1)-0.719738299649,(r2,r3)1.80648078256)-0.2790872575;'



### Format labels
If your internal labels are numeric, such as 'support' values, you can format how they are stored.

String labels are written as strings, so this option mainly matters for numeric values. The default ("%.12g") write 12 floating points. Setting `internal_labels_formatter=None` hides numeric internal labels while still allowing string labels to be written if you selected a string-valued feature.


```python
# None applies no string formatting
tree.write(internal_labels_formatter=None)
```




    '((r0:0.5,r1:0.5):0.5,(r2:0.5,r3:0.5):0.5);'




```python
# float format the 'support' values as max 12 floating points
tree.write(internal_labels="support", internal_labels_formatter="%.12g")
```




    '((r0:0.5,r1:0.5)100:0.5,(r2:0.5,r3:0.5)90:0.5);'




```python
# float format the 'support' values w/ 2 fixed floating points
tree.write(internal_labels="support", internal_labels_formatter="{:.2f}")
```




    '((r0:0.5,r1:0.5)100.00:0.5,(r2:0.5,r3:0.5)90.00:0.5);'




```python
# float format the 'support' values as ints
tree.write(internal_labels="support", internal_labels_formatter="%d")
```




    '((r0:0.5,r1:0.5)100:0.5,(r2:0.5,r3:0.5)90:0.5);'



## NHX metadata
Sometimes plain Newick is not enough because you want to keep extra information attached to the tree. In that case, `toytree` can write NHX-style metadata inside square brackets.

The main idea is simple: pass feature names with `features=[...]`, and `toytree` will include those stored values in the output. Node features are written next to nodes, and edge features are written on edges.

Most users only need two checks before writing NHX:

- `tree.features` shows which features exist on the tree;
- `tree.edge_features` shows which of those are edge data.

Python lists, tuples, and arrays are also sometimes stored on a tree. A common example is a vector of ancestral-state probabilities at an internal node. When those list-like values are written to NHX metadata, `features_pack` joins them into one string value. The common convention is `val1|val2`, such as `0.1|0.9`.

When that tree is parsed again with `toytree.tree()`, the matching `feature_unpack` setting splits the serialized value back into a Python list. Item types are inferred on read, so numeric-looking values become numbers and everything else remains strings.

String metadata are written directly, so `toytree` rejects values that would make the output ambiguous, such as values containing the active metadata delimiters or square brackets.

### Select features
Start by checking what data are stored on the tree, then choose only the features you actually want to export. Keeping that list short usually makes the output easier to read and easier for other programs to parse.


```python
# see the features of a tree
tree.features
```




    ('idx', 'name', 'height', 'dist', 'support', 'X')




```python
# see which features are edge (not node) data
tree.edge_features
```




    {'dist', 'support'}




```python
# write NHX w/ "X" as node feature
tree.write(features=["X"])
```




    '((r0[&X=-3.35122656592]:0.5,r1[&X=2.83027759993]:0.5)100[&X=-0.719738299649]:0.5,(r2[&X=1.27774016632]:0.5,r3[&X=1.36575371172]:0.5)90[&X=1.80648078256]:0.5)[&X=-0.2790872575];'




```python
# write NHX w/ "support" also stored as metadata
tree.write(features=["support"])
```




    '((r0:0.5,r1:0.5)100:0.5[&support=100],(r2:0.5,r3:0.5)90:0.5[&support=90]);'



### Format features
If a feature contains numeric values, `features_formatter` lets you shorten or tidy those values before writing them. This is especially helpful when NHX metadata would otherwise carry long floating-point strings.


```python
# write NHX string with one node metadata feature  
tree.write(features=["X"], features_formatter="%.3f")
```




    '((r0[&X=-3.351]:0.5,r1[&X=2.830]:0.5)100[&X=-0.720]:0.5,(r2[&X=1.278]:0.5,r3[&X=1.366]:0.5)90[&X=1.806]:0.5)[&X=-0.279];'



### Features pack
List-like values use `features_pack` instead. For example, a probability vector such as `[0.1, 0.9]` is written by default as `0.1|0.9`, and parsing that same tree with `toytree.tree()` turns it back into a Python list like `[0.1, 0.9]`. If you need a different separator, you can change `features_pack` when writing and `feature_unpack` when parsing.


```python
# assign a [0, 1] list data to every Node
tree.set_node_data(feature="Y", default=[0.1, 0.9], inplace=True)

# write 'packed' list using default 'features_pack' value '|'
tree.write(features="Y", features_pack="|")
```




    '((r0[&Y=0.1|0.9]:0.5,r1[&Y=0.1|0.9]:0.5)100[&Y=0.1|0.9]:0.5,(r2[&Y=0.1|0.9]:0.5,r3[&Y=0.1|0.9]:0.5)90[&Y=0.1|0.9]:0.5)[&Y=0.1|0.9];'



## NEXUS
NEXUS is useful when you want a tree file in a more explicit container format. Instead of writing just one Newick line, `toytree` wraps the tree inside a `trees` block and adds the `#NEXUS` header.

You will also see a translation table with integer tip tokens. That table is normal for NEXUS output and helps keep the embedded tree string compact while preserving the original tip names. You can still use the same formatting options from the Newick and NHX examples above, because NEXUS output simply wraps that underlying tree text.


```python
# write tree in Newick format wrapped in Nexus
nexus = tree.write(nexus=True)
print(nexus)
```

    #NEXUS
    begin trees;
        translate
            0 r0,
            1 r1,
            2 r2,
            3 r3,
        ;
        tree 0 = [&R] ((0:0.5,1:0.5)100:0.5,(2:0.5,3:0.5)90:0.5);
    end;



```python
# write tree in NHX format wrapped in Nexus
nexus = tree.write(features=["support", "name", "X"], nexus=True, features_formatter="%.2f")
print(nexus)
```

    #NEXUS
    begin trees;
        translate
            0 r0,
            1 r1,
            2 r2,
            3 r3,
        ;
        tree 0 = [&R] ((0[&name=r0,X=-3.35]:0.5,1[&name=r1,X=2.83]:0.5)100[&name=A,X=-0.72]:0.5[&support=100.00],(2[&name=r2,X=1.28]:0.5,3[&name=r3,X=1.37]:0.5)90[&name=B,X=1.81]:0.5[&support=90.00])[&name=C,X=-0.28];
    end;



```python
# write tree to file as Nexus
tree.write(path="/tmp/test.nex", nexus=True)
```

## MultiTree output
A `MultiTree` can also be written back to text. The idea is the same as `ToyTree.write()`, but the process is repeated for every tree in order.

For multi-Newick output, each tree is written on its own line. For multi-NEXUS output, the trees appear together inside one `trees` block. If you already understand `ToyTree.write()`, this section should feel familiar.


```python
# create a MultiTree
mtree = toytree.mtree([tree, tree, tree])
```


```python
# write multi-Newick
print(mtree.write())
```

    ((r0:0.5,r1:0.5)100:0.5,(r2:0.5,r3:0.5)90:0.5);
    ((r0:0.5,r1:0.5)100:0.5,(r2:0.5,r3:0.5)90:0.5);
    ((r0:0.5,r1:0.5)100:0.5,(r2:0.5,r3:0.5)90:0.5);


## Single-feature labels

`write_single_feature` is a compact alternative to NHX metadata. Instead of writing a full metadata block such as `[&trait=Test]`, it appends one feature value to each node label as a `{value}` suffix. This style is used by some phylogenetics tools, including HyPhy and RAxML-NG, when they expect one categorical label per node.

This option is helpful when you want one simple annotation on every node and you need the output to stay easy to read. The selected feature must exist on every node, and its values cannot be empty or NaN. This mode is only for plain tree text, so it is not available together with `nexus=True`.


```python
labels = {
    0: "Test",
    1: "Test",
    2: "Reference",
    3: "Reference",
    4: "Test",
    5: "Reference",
    6: "Reference",
}

# set data to each node as feature 'trait'
tree = tree.set_node_data("trait", labels)

# write to single-feature newick and print
text = tree.write(write_single_feature="trait")
print(text)
```

    ((r0{Test}:0.5,r1{Test}:0.5)100{Test}:0.5,(r2{Reference}:0.5,r3{Reference}:0.5)90{Reference}:0.5){Reference};


If you parse that tree again with `toytree.tree()`, the curly-brace suffix is read back into a feature named `trait`.


```python
toytree.tree(text).get_node_data()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>idx</th>
      <th>name</th>
      <th>height</th>
      <th>dist</th>
      <th>support</th>
      <th>trait</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>r0</td>
      <td>0.0</td>
      <td>0.5</td>
      <td>NaN</td>
      <td>Test</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>r1</td>
      <td>0.0</td>
      <td>0.5</td>
      <td>NaN</td>
      <td>Test</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>r2</td>
      <td>0.0</td>
      <td>0.5</td>
      <td>NaN</td>
      <td>Reference</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>r3</td>
      <td>0.0</td>
      <td>0.5</td>
      <td>NaN</td>
      <td>Reference</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td></td>
      <td>0.5</td>
      <td>0.5</td>
      <td>100.0</td>
      <td>Test</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td></td>
      <td>0.5</td>
      <td>0.5</td>
      <td>90.0</td>
      <td>Reference</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td></td>
      <td>1.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>Reference</td>
    </tr>
  </tbody>
</table>
</div>


