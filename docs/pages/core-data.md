<div class="nb-md-page-hook" aria-hidden="true"></div>

# Data/Features

By assigning data to nodes in a ``ToyTree`` you can enable many new approaches for data visualization and statistical analyses.

This section focuses on recommended workflows for assigning data to a tree and fetching the data back in tabular format. We recommend using `ToyTree` objects themselves as the primary data storage object. 


```python
import toytree

# an example tree
tree = toytree.rtree.unittree(ntips=5, seed=123)
```

## Simple Example
The methods `set_node_data` and `get_node_data` are broadly useful for assigning data to nodes and fetching data from nodes.

The setter method returns a ``ToyTree`` in which ``data`` is assigned to nodes in the tree by matching node queries, such as names, idx labels, or regular expressions.


```python
# dict mapping node queries to values
data = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h', 8: 'i'}

# store tree with feature "X" set on Nodes 0,1,2
tree = tree.set_node_data(feature="X", data=data)
```


```python
# get the values of "X" for all Nodes in idx traversal order
tree.get_node_data("X")
```




    0    a
    1    b
    2    c
    3    d
    4    e
    5    f
    6    g
    7    h
    8    i
    Name: X, dtype: object



By returning a ``ToyTree`` you can easily chain the setter method with other tree-based methods to set data to a tree and then subsequently perform steps such as drawing a tree that displays those data, or fetching the data for other analyses. Below we chain the 'set' and 'get' methods in one call.


```python
# chain the two functions together to set & get values for a feature
tree.set_node_data("X", data=data).get_node_data("X")
```




    0    a
    1    b
    2    c
    3    d
    4    e
    5    f
    6    g
    7    h
    8    i
    Name: X, dtype: object



## Features
In `toytree` terminology a "feature" is a named trait stored to one or more nodes in a tree. Each `ToyTree` object has several data features by default: ``idx``, ``name``, ``height``, ``dist``, and ``support``. 

You can create and store additional features under almost any name (except for a few disallowed names and characters). When you load a tree from a newick, NHX, or NEXUS formatted data file it will often contain additional metadata that are stored as features. Several examples are shown in the [tree parsing documentation](parse_trees). 

A `ToyTree` contains a dynamic propery `.features` that lists all features currently assigned one or more Nodes in the tree.


```python
# all feature names assigned to at least one Node in this tree
tree.features
```




    ('idx', 'name', 'height', 'dist', 'support', 'X')



### Data as Node attributes

Data stored to a ``ToyTree`` is actually stored to its underlying `Node` objects as [Node attributes](core_node#attributes). 

This is demonstrated below where data is assigned to a feature named "Z" for two Nodes in the tree. Setting and retrieving data directly from Nodes as attributes like this is allowed. However, for general `toytree` usage, we recommend using the helper functions `set_node_data` and `get_node_data` to set and retrieve data as they provide a number of benefits, especially in terms of dealing with missing values, checking data types, and ordering data values.


```python
# set a value for the attribute (feature) named "Z" on two Nodes
tree[0].Z = "A"
tree[1].Z = "B"
```

When the `get_node_data` function is called without any features selected it returns a dataframe showing all features on the current tree. Here, this tree includes the five default features in addition to the new feature "X" for which we assigned a str value to several Nodes above, and it also includes the attribute "Z", for which we manually assigned values to two Nodes. For other Nodes that do not contain a "Z" feature a default missing value of NaN (math.nan) is returned in the dataframe.


```python
# return a dataframe with all feature data
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
      <th>Z</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>r0</td>
      <td>0.0</td>
      <td>0.8</td>
      <td>NaN</td>
      <td>a</td>
      <td>A</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>r1</td>
      <td>0.0</td>
      <td>0.4</td>
      <td>NaN</td>
      <td>b</td>
      <td>B</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>r2</td>
      <td>0.0</td>
      <td>0.4</td>
      <td>NaN</td>
      <td>c</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>r3</td>
      <td>0.0</td>
      <td>0.8</td>
      <td>NaN</td>
      <td>d</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>r4</td>
      <td>0.0</td>
      <td>0.8</td>
      <td>NaN</td>
      <td>e</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td></td>
      <td>0.4</td>
      <td>0.4</td>
      <td>NaN</td>
      <td>f</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td></td>
      <td>0.8</td>
      <td>0.2</td>
      <td>NaN</td>
      <td>g</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td></td>
      <td>0.8</td>
      <td>0.2</td>
      <td>NaN</td>
      <td>h</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>8</th>
      <td>8</td>
      <td></td>
      <td>1.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>i</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



## Set Node data
The `set_node_data` method is used to assign data for one feature at a time.

Data can be entered as a mapping (e.g., dictionary) or sequence of values (e.g., list). A number of options are available to make it easier to assign values to many nodes without having to type each name individually. 

A related function is also available, `set_node_data_from_dataframe`, which allows setting multiple features at the same time from tabular data loaded as a pandas DataFrame. Here, however, we will focus on adding single features at a time.

### data: mapping

Enter data as a mapping (e.g., ``dict``) where the keys are valid [Node Queries](data-query), such as a node name, idx label, or regular expression.

You do not have to assign a value to every node in a tree. You can enter ``data`` as a dict selecting only a subset of Nodes and all others will not have their feature value assigned or modified.


```python
# a mapping of node idx labels to values
data = {0: 10, 1: 10, 2: 10, 3: 20, 8: 50}

# set data to feature "Y" for a set of Nodes
tree = tree.set_node_data("Y", data=data)
tree.get_node_data("Y")
```




    0    10.0
    1    10.0
    2    10.0
    3    20.0
    4     NaN
    5     NaN
    6     NaN
    7     NaN
    8    50.0
    Name: Y, dtype: float64



In this example the data dictionary selects nodes using a variety of Node Queries. The first is a regular expression that matches the first four nodes in the tree, the second matches the node named "r4", and the last matches the node with int index of 8. 


```python
# a mapping with different types of supported node query keys
data = {"~r[0-3]": 10, "r4": 20, 8: 50}

# set data to feature "Y" 
tree = tree.set_node_data(feature="Y", data=data)
tree.get_node_data("Y")
```




    0    10.0
    1    10.0
    2    10.0
    3    10.0
    4    20.0
    5     NaN
    6     NaN
    7     NaN
    8    50.0
    Name: Y, dtype: float64



### data: sequence
You can alternatively set data to all Nodes in a tree by entering the values as a sequence (e.g., list, ndarray) in Node idx order. Note that this requires you to have already properly ordered your input data and to be aware of the Node idx order of your current tree. Thus, this method is more error prone than assigning data by dictionary. Nevertheless, the option is available. 

A ``ToyTreeError`` will be raised if you try to set data to a tree using a sequence that is not ``nnodes`` in length. In that case, you must use a ``mapping`` based input such as a dict to specify the assignment.


```python
# get a list of feature vlaues in idx order
data = tree.get_node_data("Y").tolist()

# set data as a sequence of length nnodes in idx order
tree = tree.set_node_data(feature="Y", data=data)
tree.get_node_data("Y")
```




    0    10.0
    1    10.0
    2    10.0
    3    10.0
    4    20.0
    5     NaN
    6     NaN
    7     NaN
    8    50.0
    Name: Y, dtype: float64



### inplace
Use ``inplace=True`` to store data directly to the input tree rather than returning a copy on which the data has been assigned. 


```python
# set data w/ inplace=False returns a copy of the tree with data assigned
tree.set_node_data(feature="Y", data=data, inplace=True)

# set data w/ inplace=True returns the tree with data assigned
tree.set_node_data(feature="Y", data=data, inplace=True);
```

### default
Use the `default` arg to set a value to all other nodes that do not have assignments in ``data``. 


```python
# set data to feature "Y" using a dict w/ node queries, and the default arg
data = {"~r[0-3]": 10, "r4": 20, 8: 50}
tree.set_node_data(feature="Y", data=data, inplace=True, default=0)
tree.get_node_data("Y")
```




    0    10
    1    10
    2    10
    3    10
    4    20
    5     0
    6     0
    7     0
    8    50
    Name: Y, dtype: int64



Use ``default=float('nan')`` to "clear" the data for a Node that is not listed in ``data``, it will not be overwritten by ``default=None``.

See Also [NaN data](#nan-data).



```python
# set new data to feature "Y" and overwrite previous data at unspecified nodes to NaN
data = {"~r[0-3]": 10, "r4": 20, 8: 50}
tree.set_node_data(feature="Y", data=data, inplace=True, default=float('nan'))
tree.get_node_data("Y")
```




    0    10.0
    1    10.0
    2    10.0
    3    10.0
    4    20.0
    5     NaN
    6     NaN
    7     NaN
    8    50.0
    Name: Y, dtype: float64



### inherit

``inherit`` can be used to assign a value to a node and all of its descendants. 

You can assign values only to the parent node of a clade and use ``inherit=True`` to assign the value to that node and all its descendants. Values are assigned in postorder traversal (roots to tips) so you can enter nested parent node keys.


```python
# set data to feature "Y" for a clade using inherit=True
tree.set_node_data("Y", data={6: 100.0}, inplace=True, inherit=True)
tree.get_node_data("Y")
```




    0    100.0
    1    100.0
    2    100.0
    3     10.0
    4     20.0
    5    100.0
    6    100.0
    7      NaN
    8     50.0
    Name: Y, dtype: float64



## Get Node data

``get_node_data`` extracts feature data from a tree in the correct idx order for plotting. 

Data are returned for a single feature as a pandas ``Series``, or for multiple features as a pandas ``DataFrame``. 

When a feature has not been assigned to all Nodes in a tree ``nan`` will be returned for missing values, but this can be changed by setting a value for the ``missing`` arg.

### Get a single feature
By entering the name of a feature in the tree a pandas Series will be returned with all of the Node values for that feature. Here the Series index contains Node idx labels representing the Nodes in an idxorder traversal of the tree. 


```python
# return values for feature "dist"
tree.get_node_data(feature="dist")
```




    0    0.8
    1    0.4
    2    0.4
    3    0.8
    4    0.8
    5    0.4
    6    0.2
    7    0.2
    8    0.0
    Name: dist, dtype: float64




```python
# return values for feature 'Z' which has data for only 2 Nodes
tree.get_node_data("Z")
```




    0      A
    1      B
    2    NaN
    3    NaN
    4    NaN
    5    NaN
    6    NaN
    7    NaN
    8    NaN
    Name: Z, dtype: object




```python
# return values for feature 'Z' with an imputed missing value
tree.get_node_data("Z", missing="C")
```




    0    A
    1    B
    2    C
    3    C
    4    C
    5    C
    6    C
    7    C
    8    C
    Name: Z, dtype: object



The pandas Series object is convenient for viewing and can be easily converted to other object types, like below.


```python
# convert a single trait Series to a dict
tree.get_node_data("Z", missing="C").to_dict()
```




    {0: 'A', 1: 'B', 2: 'C', 3: 'C', 4: 'C', 5: 'C', 6: 'C', 7: 'C', 8: 'C'}




```python
# convert a single trait Series to a numpy ndarray
tree.get_node_data("Z", missing="C").values
```




    array(['A', 'B', 'C', 'C', 'C', 'C', 'C', 'C', 'C'], dtype=object)



### Get multiple features
By default ``get_node_data`` returns a DataFrame with all features in a tree. 



```python
# return Node values for all features
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
      <th>Y</th>
      <th>Z</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>r0</td>
      <td>0.0</td>
      <td>0.8</td>
      <td>NaN</td>
      <td>a</td>
      <td>100.0</td>
      <td>A</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>r1</td>
      <td>0.0</td>
      <td>0.4</td>
      <td>NaN</td>
      <td>b</td>
      <td>100.0</td>
      <td>B</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>r2</td>
      <td>0.0</td>
      <td>0.4</td>
      <td>NaN</td>
      <td>c</td>
      <td>100.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>r3</td>
      <td>0.0</td>
      <td>0.8</td>
      <td>NaN</td>
      <td>d</td>
      <td>10.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>r4</td>
      <td>0.0</td>
      <td>0.8</td>
      <td>NaN</td>
      <td>e</td>
      <td>20.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td></td>
      <td>0.4</td>
      <td>0.4</td>
      <td>NaN</td>
      <td>f</td>
      <td>100.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td></td>
      <td>0.8</td>
      <td>0.2</td>
      <td>NaN</td>
      <td>g</td>
      <td>100.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td></td>
      <td>0.8</td>
      <td>0.2</td>
      <td>NaN</td>
      <td>h</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>8</th>
      <td>8</td>
      <td></td>
      <td>1.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>i</td>
      <td>50.0</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



You can enter a sequence of feature names and of imputed missing values to construct a table for only a subset of features.


```python
# return values for two features, with different imputed missing values
tree.get_node_data(["support", "Z"], missing=[100, "C"])
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
      <th>support</th>
      <th>Z</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>100</td>
      <td>A</td>
    </tr>
    <tr>
      <th>1</th>
      <td>100</td>
      <td>B</td>
    </tr>
    <tr>
      <th>2</th>
      <td>100</td>
      <td>C</td>
    </tr>
    <tr>
      <th>3</th>
      <td>100</td>
      <td>C</td>
    </tr>
    <tr>
      <th>4</th>
      <td>100</td>
      <td>C</td>
    </tr>
    <tr>
      <th>5</th>
      <td>100</td>
      <td>C</td>
    </tr>
    <tr>
      <th>6</th>
      <td>100</td>
      <td>C</td>
    </tr>
    <tr>
      <th>7</th>
      <td>100</td>
      <td>C</td>
    </tr>
    <tr>
      <th>8</th>
      <td>100</td>
      <td>C</td>
    </tr>
  </tbody>
</table>
</div>



### NaN data
Across all methods in ``toytree`` missing data is specified by any of the following Python types: ``float('nan')``, ``math.nan``, or ``np.nan`` which all return True by ``np.isnan()``. 


```python
# all objects that return True by np.isnan() are valid missing values in toytree
import numpy as np
import math
print([np.isnan(i) for i in [float('nan'), math.nan, np.nan]])
```

    [True, True, True]


## Using features

See ``range_mapping``, ``color_mapping``, ``annotations``, and many ``pcm`` methods, such as ``simulate``, to see many examples of feature data being used for visualizations or statistical analyses.

## Node vs Edge features
Some data stored to a tree are intended to represent information about the edges (splits) in a tree, rather than information about the nodes. This is important as these types of data must be treated differently when doing things like re-rooting a tree, and in some cases, for visualization. (See the [rooting](/toytree/rooting) tutorial for an example of how this is automatically handled in `toytree`.) Any feature can be optionally plotted as a marker and/or label on edges of a tree rather than on nodes. This can be done in a simple way within the `.draw` function by using the argument `node_as_edge_data=True`, or, it can be done with many more options by using functions in the `toytree.annotate` subpackage.

Examples of plotted edge features are shown below. These have a few key features in visualization: (1) values are plotted on the midpoint of edges; (2) No value is shown for the root edge, since it does not represent a true split in the tree; and (3) only one of the two edges descended from the root show a value, since these are actually the same edge, but on which the root node has been placed. As an example of this last point, a value such as a support score, or edge length, is a feature of this entire edge. Thus, the value is the same whether the tree is rooted or unrooted, as shown below.


```python
# draw a feature as EDGE data
tree.draw(
    node_mask=False,
    node_labels="idx",
    node_labels_style={"font-size": 18},
    node_as_edge_data=True,
);
```


<div class="toyplot" id="taa8d83f152f445cd92f5f164c7f0a969" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t619fcf2ecf334ea891306c5b55971696"><g class="toyplot-coordinates-Cartesian" id="t583000831c56486d8dcddafdd0d22d1e"><clipPath id="t59f7eb3bc9064cadb74471cf541312b1"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t59f7eb3bc9064cadb74471cf541312b1)"><g class="toytree-mark-Toytree" id="tf4c9afd9784042cba2ebc6cf0e1906de"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 88.9 185.4 L 88.9 214.2 L 224.4 214.2" id="6,0" style=""></path><path d="M 156.6 156.7 L 156.6 175.9 L 224.4 175.9" id="5,1" style=""></path><path d="M 156.6 156.7 L 156.6 137.5 L 224.4 137.5" id="5,2" style=""></path><path d="M 88.9 80.0 L 88.9 99.1 L 224.4 99.1" id="7,3" style=""></path><path d="M 88.9 80.0 L 88.9 60.8 L 224.4 60.8" id="7,4" style=""></path><path d="M 88.9 185.4 L 88.9 156.7 L 156.6 156.7" id="6,5" style=""></path><path d="M 55.0 132.7 L 55.0 185.4 L 88.9 185.4" id="8,6" style=""></path><path d="M 55.0 132.7 L 55.0 80.0 L 88.9 80.0" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:18px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(156.642,214.218)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(190.526,175.859)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(190.526,137.5)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(156.642,99.1411)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(156.642,60.7822)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(122.757,156.679)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(71.9309,185.449)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.41,214.218)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.41,175.859)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.41,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.41,99.1411)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.41,60.7822)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# draw a feature as EDGE data for the same tree, unrooted.
tree.unroot().draw(
    node_mask=False,
    node_labels="idx",
    node_labels_style={"font-size": 18},
    node_as_edge_data=True,
);
```


<div class="toyplot" id="tb98a3197f5be4d2d9a83f09c57befbcb" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t00dc3e14f1d6489483e6c7bff36c7143"><g class="toyplot-coordinates-Cartesian" id="t3e23af7cb13e4a818bce288dcb3a63b7"><clipPath id="t2f4c8069559d4277a247aa1506d07e13"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t2f4c8069559d4277a247aa1506d07e13)"><g class="toytree-mark-Toytree" id="t1814572fce6a4cc3a25d06e6927f78b6"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 55.0 150.3 L 55.0 214.2 L 167.9 214.2" id="7,0" style=""></path><path d="M 111.5 156.7 L 111.5 175.9 L 167.9 175.9" id="5,1" style=""></path><path d="M 111.5 156.7 L 111.5 137.5 L 167.9 137.5" id="5,2" style=""></path><path d="M 111.5 80.0 L 111.5 99.1 L 224.4 99.1" id="6,3" style=""></path><path d="M 111.5 80.0 L 111.5 60.8 L 224.4 60.8" id="6,4" style=""></path><path d="M 55.0 150.3 L 55.0 156.7 L 111.5 156.7" id="7,5" style=""></path><path d="M 55.0 150.3 L 55.0 80.0 L 111.5 80.0" id="7,6" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:18px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(111.463,214.218)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(139.7,175.859)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(139.7,137.5)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(167.937,99.1411)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(167.937,60.7822)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(83.2257,156.679)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(83.2257,79.9616)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(167.937,214.218)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(167.937,175.859)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(167.937,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.41,99.1411)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.41,60.7822)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


Annotation methods can also be used to plot edge data. See the annotation docs.


```python
# annotate a tree with EDGE data
canvas, axes, mark = tree.draw()
tree.annotate.add_edge_labels(axes=axes, labels="idx", font_size=18, mask=False);
```


<div class="toyplot" id="t1e388a41d0e847c4a359da613a17e33e" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="td2f19578d6fb46b892e6e213116d98c5"><g class="toyplot-coordinates-Cartesian" id="t01e9fd1e27df4185abeb90ac2ef2a68d"><clipPath id="t570c64ef452941469ef8dd2688baaec7"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t570c64ef452941469ef8dd2688baaec7)"><g class="toytree-mark-Toytree" id="t6762d4c74f13424fab62937d501860f2"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 85.7 185.5 L 85.7 214.3 L 224.7 214.3" id="6,0" style=""></path><path d="M 155.2 156.7 L 155.2 175.9 L 224.7 175.9" id="5,1" style=""></path><path d="M 155.2 156.7 L 155.2 137.5 L 224.7 137.5" id="5,2" style=""></path><path d="M 85.7 79.9 L 85.7 99.1 L 224.7 99.1" id="7,3" style=""></path><path d="M 85.7 79.9 L 85.7 60.7 L 224.7 60.7" id="7,4" style=""></path><path d="M 85.7 185.5 L 85.7 156.7 L 155.2 156.7" id="6,5" style=""></path><path d="M 51.0 132.7 L 51.0 185.5 L 85.7 185.5" id="8,6" style=""></path><path d="M 51.0 132.7 L 51.0 79.9 L 85.7 79.9" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.728,214.344)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.728,175.922)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.728,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.728,99.0778)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.728,60.6555)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g></g></g><g class="toyplot-mark-Text" id="t9dec9c457b79415e8e85454e7ad33a1b"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(155.2308940550154,214.34449734970275)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:18.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g class="toyplot-Datum" transform="translate(189.9796738888796,175.92224867485137)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:18.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g class="toyplot-Datum" transform="translate(189.9796738888796,137.5)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:18.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g class="toyplot-Datum" transform="translate(155.2308940550154,99.07775132514863)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:18.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g class="toyplot-Datum" transform="translate(155.2308940550154,60.655502650297265)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:18.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g class="toyplot-Datum" transform="translate(120.48211422115119,156.7111243374257)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:18.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">5</text></g><g class="toyplot-Datum" transform="translate(68.35894447035491,185.5278108435642)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:18.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">6</text></g><g class="toyplot-Datum" transform="translate(68.35894447035491,79.86662698772295)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:18.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">7</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>

