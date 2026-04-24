<div class="nb-md-page-hook" aria-hidden="true"></div>

# Tree Parsing (I/O)

Tree data is typically stored in a serialized (text) format containing the topology and sometimes additional metadata. ``toytree`` can parse serialized tree data from a variety of formats (Newick, Nexus, NHX), accepted as text, local file paths, HTTP(S) URLs, and UTF-8 bytes. Parsed data is returned as a ``ToyTree`` or ``MultiTree`` object. Most users only need `toytree.tree()` for one tree and `toytree.mtree()` for many trees. These methods will auto-detect the input type and format and return a tree object.


```python
import toytree
```


```python
# example newick string
DATA = "((tip1:2,tip2:2):1,tip3:3);"

# parse DATA and return a ToyTree
tree = toytree.tree(DATA)
tree
```




    <toytree.ToyTree at 0x78b1fc16ec90>



<div class="admonition tip">
  <p class="admonition-title">Take Home</p>
  <p>
      Use <code>toytree.tree()</code> for one tree and <code>toytree.mtree()</code> when the input contains multiple trees. Reach for parser options only when metadata comments or internal labels need explicit control.
  </p>
</div>

## Tree data formats

Below are examples of the common Newick, NHX, and Nexus tree data formats. Newick is the base format from which the other two formats are extensions. More details on parsing each format is described below. While a few additional formats (e.g., JSON or XML) are sometimes used to store tree data, these Newick-based formats are most common. Plain Newick format stores topology, labels, and edge lengths. NHX or 'comment' syntax extends Newick with square-bracket metadata. NEXUS wraps one or more Newick or NHX trees inside a `trees` block, often with a `translate` table.


```python
# newick: represents a topology using nested parentheses
NEWICK0 = "((,),);"
```


```python
# newick: name strings are usually present for tips as `(label,)`
NEWICK1 = "((tip1,tip2),tip3);"
```


```python
# newick: names can also be present for internal nodes as `()label`
NEWICK2 = "((tip1,tip2)internal1,tip3)internal2;"
```


```python
# newick: edge lengths (dists) are usually present as `()label:dist`
NEWICK3 = "((tip1:2,tip2:2):1,tip3:3);"
```


```python
# newick: support values can be stored in place of internal names `()support`
NEWICK4 = "((tip1,tip2)100,tip3);"
```


```python
# nhx: additional metadata is stored as key=value pairs as `()[meta]`
NHX1 = "((tip1[&trait=2],tip2[&trait=4])[&trait=3],tip3[&trait=1])[&trait=5];"
```


```python
# nexus: newick/NHX data with other code blocks between (begin... end;)  
NEXUS1 = """
#NEXUS
begin trees;
    translate
        1 apple,
        2 blueberry,
        3 cantaloupe,
        4 durian,
    ;
    tree tree0 = [&U] ((1,2),(3,4));
end;
"""
```

## Choose the entry point

| You have | Use | Returns |
| --- | --- | --- |
| One tree in text, a file path, a URL, or bytes | `toytree.tree()` | `ToyTree` |
| Multiple serialized trees, a NEXUS trees block, or an ordered collection of tree inputs | `toytree.mtree()` | `MultiTree` |
| One serialized Newick string and you want direct parser control | `toytree.io.parse_newick_string()` or `toytree.io.parse_newick_string_custom()` | parsed tree from that string |

For string input, `toytree.tree()` and `toytree.mtree()` use this detection order:

1. `http://` or `https://` -> fetch remote text.
2. Starts with `(` or `#`, or ends with `;` -> parse as serialized tree text.
3. Existing local path -> read the file.
4. Anything else -> raise `ToytreeError`.

If your serialized input contains multiple trees, prefer `toytree.mtree()`. Calling `toytree.tree()` on the same input prints a warning and returns only the first tree.


## Auto-detect formats
Parsing is made especially easy in ``toytree`` through the general purpose ``toytree.tree()`` method, which can auto-detect the input type and format. For example, we can parse all of the above data strings correctly, including their metadata, without the need to specify an additional arguments. Moreover, it can can parse these data regardless of whether they are entered as a string, bytes, file path, or URL. In this way, ``toytree.tree()`` acts as a sort of swiss army knife for tree data parsing. This method will raise `ToyTreeError` on empty or malformed inputs.


```python
# parse all 7 tree data strings from above into ToyTree objects
data = [NEWICK0, NEWICK1, NEWICK2, NEWICK3, NEWICK4, NHX1, NEXUS1]
trees = [toytree.tree(i) for i in data]
trees
```




    [<toytree.ToyTree at 0x78b17583f2f0>,
     <toytree.ToyTree at 0x78b175fd06b0>,
     <toytree.ToyTree at 0x78b17583f6b0>,
     <toytree.ToyTree at 0x78b17583fda0>,
     <toytree.ToyTree at 0x78b175860110>,
     <toytree.ToyTree at 0x78b175860440>,
     <toytree.ToyTree at 0x78b17646eea0>]



## Newick basics

Plain Newick format includes information about topology, tip labels, and edge lengths, but internal labels are ambiguous: the same position can hold a node name, an edge support value, or some other feature. `toytree.tree()` automatically infers names versus support when you do not override it.

### Internal labels inferred as names
Non-numeric internal labels are stored as node `name` values.


```python
# A newick string with internal node names
NEWICK2 = "((tip1,tip2)internal1,tip3)internal2;"

# parse with .tree()
tree = toytree.tree(NEWICK2)

# show the tree data (labels were assigned to 'name' feature)
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
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>tip1</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>tip2</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>tip3</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>internal1</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>internal2</td>
      <td>2.0</td>
      <td>0.0</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



### Internal labels inferred as support
Numeric internal labels are stored as `support`. Note: tip edges and the root edge do not typically have support values, and are stored as NaN.


```python
# newick with str labels for tips and int labels for internal nodes
NEWICK4 = "((tip1,tip2)100,tip3);"

# parse the newick string with .tree()
tree = toytree.tree(NEWICK4)

# show the tree data (labels assigned to 'support' for internal Node)
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
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>tip1</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>tip2</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>tip3</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td></td>
      <td>1.0</td>
      <td>1.0</td>
      <td>100.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td></td>
      <td>2.0</td>
      <td>0.0</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



### Override internal label parsing
If auto-inference is not what you want, pass `internal_labels="name"`, `internal_labels="support"`, or any other feature name. This is rarely needed but allows overriding the auto-detection for non-standard newick data storage. In this example we re-assign the internal label to a new named feature "arbitrary" instead of assigning it to 'name' or 'support'.


```python
# parse the newick string with internal str labels and assign
tre0 = toytree.tree(NEWICK2, internal_labels="arbitrary")

# show the tree data where labels were assigned to "arbitrary"
tre0.get_node_data()
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
      <th>arbitrary</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>tip1</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>tip2</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>tip3</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td></td>
      <td>1.0</td>
      <td>1.0</td>
      <td>NaN</td>
      <td>internal1</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td></td>
      <td>2.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>internal2</td>
    </tr>
  </tbody>
</table>
</div>



## NHX and comment metadata
Square-bracket comments let Newick store extra node and edge features, for example `[&state=1]` or `:1[&posterior=0.95]`. `toytree.tree()` parses these automatically and keeps edge-attached fields in `tree.edge_features`.

When a program uses a different comment style, these parser options control how metadata is read:

- `feature_prefix`: expected prefix. The default `&` accepts both `[&x=1]` and `[x=1]`; use `&&NHX:` for strict NHX input.
- `feature_delim`: separator between items inside one metadata block, often `,` or `:`.
- `feature_assignment`: separator between keys and values, often `=` or `:`.
- `feature_unpack`: separator for packed values such as `0.1|0.9`.
- `internal_labels`: override ambiguous internal labels when a file mixes plain Newick labels with metadata comments.

Malformed input raises `ToytreeError` for missing semicolons, imbalanced parentheses, unterminated metadata blocks, and explicit prefix mismatches. If you need exact control over a single serialized Newick string, use `toytree.io.parse_newick_string()` or `toytree.io.parse_newick_string_custom()` directly.


```python
# only tip Node metadata
NHX1 = "((a[&N=1],b[&N=2]),c[&N=3]);"
# only internal Node metadata
NHX2 = "((a,b)[&N=4],c)[&N=5];"
# both tip and internal Node metadata
NHX3 = "((a[&N=1],b[&N=2])[&N=4],c[&N=3])[&N=5];"
# only edge metadata
NHX4 = "((a:1[&E=1],b:1[&E=2]):1[&E=4],c:1[&E=3]);"
# both node and edge metadata
NHX5 = "((a[&N=1]:1[&E=1],b[&N=2]:1[&E=2])[&N=4]:1[&E=4],c[&N=3]:1[&E=3])[&N=5];"
```


```python
# NHX1 has only tip node data mapped to feature "N"
toytree.tree(NHX1).get_node_data()
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
      <th>N</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>a</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>b</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
      <td>2.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>c</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>NaN</td>
      <td>3.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td></td>
      <td>1.0</td>
      <td>1.0</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td></td>
      <td>2.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>




```python
# NHX5 has all node data mapped to feature "N" and edge data to feature "E"
toytree.tree(NHX5).get_node_data()
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
      <th>E</th>
      <th>N</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>a</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
      <td>1.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>b</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
      <td>2.0</td>
      <td>2.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>c</td>
      <td>1.0</td>
      <td>1.0</td>
      <td>NaN</td>
      <td>3.0</td>
      <td>3.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td></td>
      <td>1.0</td>
      <td>1.0</td>
      <td>NaN</td>
      <td>4.0</td>
      <td>4.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td></td>
      <td>2.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>5.0</td>
    </tr>
  </tbody>
</table>
</div>



## NEXUS format
NEXUS wraps tree strings inside a `trees` block and may include other unrelated blocks that `toytree` ignores. `toytree.tree()` reads the first tree in that block, while `toytree.mtree()` reads them all. If a `translate` table is present, only tip labels are remapped; internal labels keep their usual name or support interpretation. A NEXUS input with no trees raises `ToytreeError`.



```python
# nexus: Newick/NHX data with other code blocks between (begin... end;)  
NEXUS_EXAMPLE = """
#NEXUS
begin data;
    ...
end;

begin mrbayes;
    ...
end;

begin trees;
    translate
        1 apple,
        2 blueberry,
        3 cantaloupe,
        4 durian,
    ;
    tree tree0 = [&U] ((1,2),(3,4));
end;
"""
```


```python
# parse NEXUS file and show tree data
tree = toytree.tree(NEXUS_EXAMPLE)
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
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>apple</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>blueberry</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>cantaloupe</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>durian</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td></td>
      <td>1.0</td>
      <td>1.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td></td>
      <td>1.0</td>
      <td>1.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td></td>
      <td>2.0</td>
      <td>0.0</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



## Parsing MultiTrees
Use `toytree.mtree()` when you want every tree from multiline serialized input, a NEXUS `trees` block, or an ordered collection of tree inputs. Direct inputs follow the same path, URL, text, and bytes detection rules as `toytree.tree()`, and ordered iterables may mix serialized `str`, `Path`, and `bytes` entries.


```python
# a str with Newick data separated by new lines
# multiline serialized input belongs to .mtree(), which loads every tree
MULTILINE_NEWICK = """
(((a:1,b:1):1,(d:1.5,e:1.5):0.5):1,c:3);
(((a:1,d:1):1,(b:1,e:1):1):1,c:3);
(((a:1.5,b:1.5):1,(d:1,e:1):1.5):1,c:3.5);
(((a:1.25,b:1.25):0.75,(d:1,e:1):1):1,c:3);
(((a:1,b:1):1,(d:1.5,e:1.5):0.5):1,c:3);
(((b:1,a:1):1,(d:1.5,e:1.5):0.5):2,c:4);
(((a:1.5,b:1.5):0.5,(d:1,e:1):1):1,c:3);
(((b:1.5,d:1.5):0.5,(a:1,e:1):1):1,c:3);
"""

# parse with .mtree
mtree = toytree.mtree(MULTILINE_NEWICK)
mtree

```




    <toytree.MultiTree ntrees=8>




```python
# a Nexus str with trees in a trees block
MULTI_N5XUS = """
#NEXUS
begin trees;
    translate
        1 a,
        2 b,
        3 c,
        4 d,
        5 e,
    ;
    tree 1 = [&R] (((1:1,2:1):1,(4:1.5,5:1.5):0.5):1,3:3);
    tree 2 = [&R] (((1:1,4:1):1,(2:1,5:1):1):1,3:3);
    tree 3 = [&R] (((1:1.5,2:1.5):1,(4:1,5:1):1.5):1,3:3.5);
    tree 4 = [&R] (((1:1.25,2:1.25):0.75,(4:1,5:1):1):1,3:3);
    tree 5 = [&R] (((1:1,2:1):1,(4:1.5,5:1.5):0.5):1,3:3);
    tree 6 = [&R] (((2:1,1:1):1,(4:1.5,5:1.5):0.5):2,3:4);
    tree 7 = [&R] (((1:1.5,2:1.5):0.5,(4:1,5:1):1):1,3:3);
    tree 8 = [&R] (((2:1.5,4:1.5):0.5,(1:1,5:1):1):1,3:3);
end;
"""

# pars5 with .mtree
mtree = toytree.mtree(MULTI_N5XUS)
mtree
```




    <toytree.MultiTree ntrees=8>



Single-tree input is still valid for `toytree.mtree()` and returns a `MultiTree` containing one `ToyTree`. Ordered lists, tuples, and generators are supported. Collections cannot mix `ToyTree` objects with serialized inputs, and unordered containers or mappings are rejected because tree order would be ambiguous. Calling `toytree.tree()` on multi-tree serialized input prints a warning and returns only the first tree.


```python
# calling .mtree on a single tree input is OK
toytree.mtree(NEWICK1)
```




    <toytree.MultiTree ntrees=1>




```python
# calling .tree on multiple-tree input prints a warning to stderr
# and returns only the first tree from the serialized input
toytree.tree(MULTILINE_NEWICK)
```

    Data contains (8) trees.
    Loading only the first tree using `toytree.tree`. Use `toytree.mtree` to instead load a MultiTree.





    <toytree.ToyTree at 0x78b1758c99a0>



## URLs and common parsing errors
`toytree.tree()` and `toytree.mtree()` can fetch public HTTP(S) URLs directly. The same detection rules also apply to direct UTF-8 bytes input.

Common parsing failures are usually straightforward:

- empty or whitespace-only strings are invalid;
- malformed Newick, NHX, or NEXUS raises `ToytreeError`;
- `toytree.tree()` is single-tree convenience, so use `toytree.mtree()` for multiline or multi-tree input.



```python
toytree.tree("https://eaton-lab.org/data/Cyathophora.tre")
```




    <toytree.ToyTree at 0x78b17583f080>


