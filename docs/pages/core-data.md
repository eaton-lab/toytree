<div class="nb-md-page-hook" aria-hidden="true"></div>

# Data/Features

A common mistake that users make when working with tree data arises from incorrectly assigning trait values to nodes of the tree. This is most prevalent when trait data are stored in a matrix or dataframe separate from the tree object itself, and operations such as re-rooting or ladderizing are applied to the tree. It is important that trees and trait data are kept in sync. To avoid this problem, we recommend using `ToyTree` objects themselves as the primary data storage object in your analyses. It is very simple to assign data to nodes of a tree, and to fetch data back from a tree as a dataframe, or in various alternative formats. A recommended workflow for working with data on trees is demonstrated in this section. 


```python
import toytree
import toyplot
import numpy as np
```

## Simple Example
The functions `set_node_data` and `get_node_data` provide a broad suite of functionality for setting data to one or more nodes on a tree and subsequently fetching the data back in a variety of formats, and in the correct order for plotting. By default the data setting function returns a modified copy of the tree with new data assigned, however, you can optionally use the argument `inplace=True` to set data on the tree object inplace. In either case, a tree is returned by the function, which allows for optionally chaining it with the data getter function to subsequently return the data for one or more node features.


```python
# an example tree
tree = toytree.rtree.unittree(ntips=5, seed=123)
```


```python
# set the feature "X" to a value of 10 on all Nodes in a tree
tree.set_node_data(feature="X", default=10, inplace=True);
```


```python
# get the values of "X" for all Nodes in idx traversal order
tree.get_node_data("X")
```




    0    10
    1    10
    2    10
    3    10
    4    10
    5    10
    6    10
    7    10
    8    10
    dtype: int64




```python
# chain the two functions together to set & get values for a feature
tree.set_node_data("X", default=10).get_node_data("X")
```




    0    10
    1    10
    2    10
    3    10
    4    10
    5    10
    6    10
    7    10
    8    10
    dtype: int64



## Features
In `toytree` terminology a "feature" refers the name of trait for which data is stored to nodes in a tree. For example, each `ToyTree` has several data features by default, such as `name`, `dist`, and `support`. You can create and store data under any arbitrary feature name (except for a few disallowed names and characters), and, in fact when you load a tree from a newick, NHX, or NEXUS formatted data file created by a phylogenetic tree inference program, it will often contain additional metadata that will be loaded as features. Several examples of this are shown in [tree parsing documentation](/toytree/parse_trees/#nhx-format). A `ToyTree` contains a dynamic propery `.features` containing all feature names currently assigned to that tree. (This includes any feature that is assigned to at least one Node in the tree, but it does not need to be assigned to every Node in the tree.)


```python
# all feature names assigned to at least one Node in this tree
tree.features
```




    ('idx', 'name', 'height', 'dist', 'support', 'X')



### Data as Node attributes
When storing data to a `ToyTree` it is actually stored to individual `Node` objects as [Node attributes](/toytree/node/#attributes). This is demonstrated below where data is assigned to a feature named "Z" for two Nodes in the tree. Setting and retrieving data directly from Nodes as attributes like this is the fastest way to set/get data, and is thus especially useful for developers. However, for general `toytree` usage, we recommend using the helper functions `set_node_data` and `get_node_data` to set and retrieve data as they provide a number of benefits, especially in terms of dealing with missing values, checking data types, and ordering data values.


```python
# set a value for the attribute (feature) named "Z" on two Nodes
tree[0].Z = "A"
tree[1].Z = "B"
```

When the `get_node_data` function is called without any features selected it returns a dataframe showing all features on the current tree. Here, this tree includes the five default features in addition to the new feature "X" for which we assigned a value of 10 to all Nodes above, and it also includes the attribute "Z", which has been assigned to only two Nodes in the tree. For other Nodes that do not contain a "Z" feature a default missing value of NaN (numpy.nan) is returned in the dataframe (but note, NaN is not assigned to the "Z" attribute of the other Nodes by this function).


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
      <td>10</td>
      <td>A</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>r1</td>
      <td>0.0</td>
      <td>0.4</td>
      <td>NaN</td>
      <td>10</td>
      <td>B</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>r2</td>
      <td>0.0</td>
      <td>0.4</td>
      <td>NaN</td>
      <td>10</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>r3</td>
      <td>0.0</td>
      <td>0.8</td>
      <td>NaN</td>
      <td>10</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>r4</td>
      <td>0.0</td>
      <td>0.8</td>
      <td>NaN</td>
      <td>10</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td></td>
      <td>0.4</td>
      <td>0.4</td>
      <td>NaN</td>
      <td>10</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td></td>
      <td>0.8</td>
      <td>0.2</td>
      <td>NaN</td>
      <td>10</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td></td>
      <td>0.8</td>
      <td>0.2</td>
      <td>NaN</td>
      <td>10</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>8</th>
      <td>8</td>
      <td></td>
      <td>1.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>10</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



## Set Node data
The `set_node_data` function is the general recommended way to assign data to nodes on a tree. Data can be entered using either a dictionary or sequence of values, and a number of options are available to make it easier to assign values to many nodes without having to type each out individually. A related function is also available, `set_node_data_from_dataframe`, which allows setting multiple features at the same time from tabular data loaded as a pandas DataFrame. Here, however, we will focus on adding single features at a time.

### Setting data by dict
The simplest way to enter specific data values is by using a dictionary. The keys of the dictionary can correspond to any valid [Node Query](/toytree/query) to select one or more Nodes, and the corresponding value will be assigned to these Nodes. Notably, you can enter a dict selecting only a few Nodes and a feature will be assigned to those Nodes, and not to any of the other Nodes not entered in the dict. If you want to assign a default value to all other nodes you can do so using  `default` argument. Finally, the argument `inherit` can be used to also assign a value to all descendants of a selected Node. Examples of each of these is shown below.


```python
# set data to feature "Y" for two Nodes 
data = {0: 10, 1: 20, 2: 30}
tree.set_node_data("Y", data=data).get_node_data("Y")
```




    0    10.0
    1    20.0
    2    30.0
    3     NaN
    4     NaN
    5     NaN
    6     NaN
    7     NaN
    8     NaN
    dtype: float64



In this example the data dictionary selects nodes using a variety of Node Queries. The first is a regular expression that matches the first four nodes in the tree, the second matches the node named "r4", and the last matches the node with int index of 8. Finally, we use the `default` arg to set a value of 0 to all other Nodes not selected in the data dict. In this way, we easily assigned to all 9 nodes in the tree without having to write a value for each.


```python
# set data to feature "Y" using a dict w/ node queries, and the default arg
data = {"~r[0-3]": 10, "r4": 20, 8: 50}
tree.set_node_data(feature="Y", data=data, default=0).get_node_data("Y")
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
    dtype: int64



The `inherit` arg provides another convenient way to assign data to Nodes in a tree based on their hierarchical relationships. For example, to assign a trait value that is inherited by all descendants of a particular node in a tree you need only to assign the value to one or more internal nodes while using the `inherit=True` argument. The inherited values are assigned to nodes in order from root to tips so that you can enter values for nested clades using this argument.


```python
# set data to feature "Y" for a clade using inherit=True
tree.set_node_data("Y", data={6: True}, inherit=True).get_node_data("Y")
```




    0    True
    1    True
    2    True
    3     NaN
    4     NaN
    5    True
    6    True
    7     NaN
    8     NaN
    dtype: object



### Setting data by array
You can alternatively set data to all Nodes in a tree by entering the values as a sequence (e.g., list, ndarray, Series) in Node idx order. Note that this requires you to have already properly ordered your input data and to be aware of the Node idx order of your current tree. Thus, this method is more error prone than assigning data by dictionary. Nevertheless, the option is available. Here we use it to assign random integer values to all Nodes by using the `numpy.random` library to generate an array of random ints. 


```python
# set data using an array of random int values
data = np.random.randint(10, 20, size=tree.nnodes)
tree.set_node_data(feature="Y", data=data).get_node_data("Y")
```




    0    10
    1    16
    2    10
    3    17
    4    16
    5    18
    6    17
    7    16
    8    14
    dtype: int64



## Get Node data
The `get_node_data` function is used to retrieve feature data that has been assigned to Nodes in a tree, and to return them in the correct idx order for plotting. Data can be returned for a single feature as a pandas Series, or for multiple features as a pandas DataFrame. When a feature has not been assigned to all Nodes in a tree a default value of `np.nan` will be returned for missing values, but this can be changed to any arbitrary alternative value by entering an argument for the option `missing`.

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
    dtype: float64




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
    dtype: object




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
    dtype: object



The pandas Series object is convenient to work with since it is accepted by many other `toytree` functions as input, and can can be easily converted to other object types, as demonstrated below.


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
By default the `get_node_data` function returns a DataFrame with data for all features in a tree. In addition to the option to subselect a single feature from the tree, as shown above, you can also select a subset of features to return a DataFrame containing just those features. Finally, an important feature of this function is its application for dealing with missing data. The `missing` argument can accept either a single value to assign to all missing values in the DataFrame, or a list of values to apply separately to each column.


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
      <td>10</td>
      <td>A</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>r1</td>
      <td>0.0</td>
      <td>0.4</td>
      <td>NaN</td>
      <td>10</td>
      <td>B</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>r2</td>
      <td>0.0</td>
      <td>0.4</td>
      <td>NaN</td>
      <td>10</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>r3</td>
      <td>0.0</td>
      <td>0.8</td>
      <td>NaN</td>
      <td>10</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>r4</td>
      <td>0.0</td>
      <td>0.8</td>
      <td>NaN</td>
      <td>10</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td></td>
      <td>0.4</td>
      <td>0.4</td>
      <td>NaN</td>
      <td>10</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td></td>
      <td>0.8</td>
      <td>0.2</td>
      <td>NaN</td>
      <td>10</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td></td>
      <td>0.8</td>
      <td>0.2</td>
      <td>NaN</td>
      <td>10</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>8</th>
      <td>8</td>
      <td></td>
      <td>1.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>10</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>




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



## Using features
One of the primary uses for assigning data to nodes on a tree is to visualize the data. Many arguments to the tree drawing functions accept values to designate the size, color, width, etc. of nodes or edges. These can be entered in three main ways: (1) by extracting the data as a Series using `get_node_data`; (2) by entering the feature name directly as an argument; and (3) by using range or color mapping. The latter to cases simply provide a shorthand syntax for plotting a feature which use `get_node_data` under the hood. Examples are shown below for the two features, "C" and "D", representing a discrete and continuous data set. 


```python
# set a color name as 'red' or 'blue' to all nodes for feature "C"
tree.set_node_data("C", {6: "red"}, inherit=True, default="blue", inplace=True).get_node_data("C")
```




    0     red
    1     red
    2     red
    3    blue
    4    blue
    5     red
    6     red
    7    blue
    8    blue
    dtype: object




```python
# set random float values in (0-1) to all nodes for feature "D"
tree.set_node_data("D", np.random.random(tree.nnodes), inplace=True).get_node_data("D")
```




    0    0.865487
    1    0.270223
    2    0.753520
    3    0.575131
    4    0.563372
    5    0.463798
    6    0.988708
    7    0.822768
    8    0.884204
    dtype: float64



**(1)** The first method for extracting data from a tree to use for plotting makes use of the `get_node_data` function call. Here we call the function from the same tree object that is being plotted, and select the feature "C" of discrete data values. This returns a Series object with the values in the correct order (idxorder) for plotting on the nodes, which are then parsed as a `node_colors` argument.


```python
# draw with node colors entered from the "C" discrete data feature
tree.draw(node_sizes=15, node_mask=False, node_colors=tree.get_node_data("C"));
```


<div class="toyplot" id="t503b9b3774db41e6969ba06a168b5da1" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tcb447aa56caa4aba877a2ec25025838c"><g class="toyplot-coordinates-Cartesian" id="te4a9eead217d4ce1b11e061a5c048c84"><clipPath id="ta6605606787b43cdaf0199f07b05c4a6"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#ta6605606787b43cdaf0199f07b05c4a6)"></g></g><g class="toyplot-coordinates-Cartesian" id="te5b4820561b9476b99f5be92325c2216"><clipPath id="t0c30892541c145329824d184f08f1613"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t0c30892541c145329824d184f08f1613)"><g class="toytree-mark-Toytree" id="t49f4fbf63ddf47ad91290ebf4db44d62"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 92.1 186.6 L 92.1 216.0 L 224.4 216.0" id="6,0" style=""></path><path d="M 158.3 157.1 L 158.3 176.8 L 224.4 176.8" id="5,1" style=""></path><path d="M 158.3 157.1 L 158.3 137.5 L 224.4 137.5" id="5,2" style=""></path><path d="M 92.1 78.6 L 92.1 98.2 L 224.4 98.2" id="7,3" style=""></path><path d="M 92.1 78.6 L 92.1 59.0 L 224.4 59.0" id="7,4" style=""></path><path d="M 92.1 186.6 L 92.1 157.1 L 158.3 157.1" id="6,5" style=""></path><path d="M 59.0 132.6 L 59.0 186.6 L 92.1 186.6" id="8,6" style=""></path><path d="M 59.0 132.6 L 59.0 78.6 L 92.1 78.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(100.0%,0.0%,0.0%)" transform="translate(224.443,216.009)"><circle r="7.5"></circle></g><g id="Node-1" style="fill:rgb(100.0%,0.0%,0.0%)" transform="translate(224.443,176.754)"><circle r="7.5"></circle></g><g id="Node-2" style="fill:rgb(100.0%,0.0%,0.0%)" transform="translate(224.443,137.5)"><circle r="7.5"></circle></g><g id="Node-3" style="fill:rgb(0.0%,0.0%,100.0%)" transform="translate(224.443,98.2456)"><circle r="7.5"></circle></g><g id="Node-4" style="fill:rgb(0.0%,0.0%,100.0%)" transform="translate(224.443,58.9912)"><circle r="7.5"></circle></g><g id="Node-5" style="fill:rgb(100.0%,0.0%,0.0%)" transform="translate(158.25,157.127)"><circle r="7.5"></circle></g><g id="Node-6" style="fill:rgb(100.0%,0.0%,0.0%)" transform="translate(92.0575,186.568)"><circle r="7.5"></circle></g><g id="Node-7" style="fill:rgb(0.0%,0.0%,100.0%)" transform="translate(92.0575,78.6184)"><circle r="7.5"></circle></g><g id="Node-8" style="fill:rgb(0.0%,0.0%,100.0%)" transform="translate(58.9612,132.593)"><circle r="7.5"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.443,216.009)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.443,176.754)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.443,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.443,98.2456)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.443,58.9912)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


**(2)** The second method for extracting data from a tree uses a simpler syntax, entering only the feature name as a string to the `node_colors` argument. Here, the `draw` function will identify that "C" is a valid feature of this tree object, and it will extract the "C" feature data from the tree. Compared to the syntax above, this looks cleaner, but has the downside that you cannot enter additional options to fill a value for missing data. 


```python
# draw with node colors automatically extracted from the "C" feature
tree.draw(node_sizes=15, node_mask=False, node_colors="C");
```


<div class="toyplot" id="tdae0bc4d91874d588b945770339c44a8" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t17a7e99c6c2d459cba7960a37f6baa44"><g class="toyplot-coordinates-Cartesian" id="tcb161410098f4cdd9ab7881377ee59ba"><clipPath id="tad97633064f34fb5bdd9c807d7a9f58e"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tad97633064f34fb5bdd9c807d7a9f58e)"></g></g><g class="toyplot-coordinates-Cartesian" id="tf7666dda7408440cb436bdc4722b47c9"><clipPath id="t8d91841b6a5e47c9bda53cdbcdbdd336"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t8d91841b6a5e47c9bda53cdbcdbdd336)"><g class="toytree-mark-Toytree" id="t4fe73879190d48adaf0bbdbdc29187a7"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 92.1 186.6 L 92.1 216.0 L 224.4 216.0" id="6,0" style=""></path><path d="M 158.3 157.1 L 158.3 176.8 L 224.4 176.8" id="5,1" style=""></path><path d="M 158.3 157.1 L 158.3 137.5 L 224.4 137.5" id="5,2" style=""></path><path d="M 92.1 78.6 L 92.1 98.2 L 224.4 98.2" id="7,3" style=""></path><path d="M 92.1 78.6 L 92.1 59.0 L 224.4 59.0" id="7,4" style=""></path><path d="M 92.1 186.6 L 92.1 157.1 L 158.3 157.1" id="6,5" style=""></path><path d="M 59.0 132.6 L 59.0 186.6 L 92.1 186.6" id="8,6" style=""></path><path d="M 59.0 132.6 L 59.0 78.6 L 92.1 78.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(100.0%,0.0%,0.0%)" transform="translate(224.443,216.009)"><circle r="7.5"></circle></g><g id="Node-1" style="fill:rgb(100.0%,0.0%,0.0%)" transform="translate(224.443,176.754)"><circle r="7.5"></circle></g><g id="Node-2" style="fill:rgb(100.0%,0.0%,0.0%)" transform="translate(224.443,137.5)"><circle r="7.5"></circle></g><g id="Node-3" style="fill:rgb(0.0%,0.0%,100.0%)" transform="translate(224.443,98.2456)"><circle r="7.5"></circle></g><g id="Node-4" style="fill:rgb(0.0%,0.0%,100.0%)" transform="translate(224.443,58.9912)"><circle r="7.5"></circle></g><g id="Node-5" style="fill:rgb(100.0%,0.0%,0.0%)" transform="translate(158.25,157.127)"><circle r="7.5"></circle></g><g id="Node-6" style="fill:rgb(100.0%,0.0%,0.0%)" transform="translate(92.0575,186.568)"><circle r="7.5"></circle></g><g id="Node-7" style="fill:rgb(0.0%,0.0%,100.0%)" transform="translate(92.0575,78.6184)"><circle r="7.5"></circle></g><g id="Node-8" style="fill:rgb(0.0%,0.0%,100.0%)" transform="translate(58.9612,132.593)"><circle r="7.5"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.443,216.009)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.443,176.754)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.443,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.443,98.2456)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.443,58.9912)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


**(3)** The third method uses toytree's "tuple syntax" that is used for range and color mapping (See [*range-mapping*](/toytree/range-mapping) and [*color-mapping*](/toytree/color-mapping)). For colors, you can enter (feature name, colormap, min-value, max-value, nan-value), to map any feature to any range of colors in a colormap. Only the first argument is required, with additional args providing style options, as shown below.


```python
# draw with node colors extracted and colormapped from the "C" feature
tree.draw(node_sizes=15, node_mask=False, node_colors=("C",));
```


<div class="toyplot" id="ta3398ec51a934102900ddd1487ee473b" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t41230b0ce0ab47a2b6ea9fdc53801a37"><g class="toyplot-coordinates-Cartesian" id="tb8223956cecf4a78a424a83eec0f36bf"><clipPath id="t1f35c458ae814cff8347d3daff8f8fd3"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t1f35c458ae814cff8347d3daff8f8fd3)"></g></g><g class="toyplot-coordinates-Cartesian" id="tce2bff63a8e24837906d3c0f0a74e17b"><clipPath id="t1be07ca075b14bdaa577fd332c28c8de"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t1be07ca075b14bdaa577fd332c28c8de)"><g class="toytree-mark-Toytree" id="tf8ea689d1fa04845a0c900270911cc9b"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 92.1 186.6 L 92.1 216.0 L 224.4 216.0" id="6,0" style=""></path><path d="M 158.3 157.1 L 158.3 176.8 L 224.4 176.8" id="5,1" style=""></path><path d="M 158.3 157.1 L 158.3 137.5 L 224.4 137.5" id="5,2" style=""></path><path d="M 92.1 78.6 L 92.1 98.2 L 224.4 98.2" id="7,3" style=""></path><path d="M 92.1 78.6 L 92.1 59.0 L 224.4 59.0" id="7,4" style=""></path><path d="M 92.1 186.6 L 92.1 157.1 L 158.3 157.1" id="6,5" style=""></path><path d="M 59.0 132.6 L 59.0 186.6 L 92.1 186.6" id="8,6" style=""></path><path d="M 59.0 132.6 L 59.0 78.6 L 92.1 78.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(98.8%,55.3%,34.9%)" transform="translate(224.443,216.009)"><circle r="7.5"></circle></g><g id="Node-1" style="fill:rgb(98.8%,55.3%,34.9%)" transform="translate(224.443,176.754)"><circle r="7.5"></circle></g><g id="Node-2" style="fill:rgb(98.8%,55.3%,34.9%)" transform="translate(224.443,137.5)"><circle r="7.5"></circle></g><g id="Node-3" style="fill:rgb(60.0%,83.5%,58.0%)" transform="translate(224.443,98.2456)"><circle r="7.5"></circle></g><g id="Node-4" style="fill:rgb(60.0%,83.5%,58.0%)" transform="translate(224.443,58.9912)"><circle r="7.5"></circle></g><g id="Node-5" style="fill:rgb(98.8%,55.3%,34.9%)" transform="translate(158.25,157.127)"><circle r="7.5"></circle></g><g id="Node-6" style="fill:rgb(98.8%,55.3%,34.9%)" transform="translate(92.0575,186.568)"><circle r="7.5"></circle></g><g id="Node-7" style="fill:rgb(60.0%,83.5%,58.0%)" transform="translate(92.0575,78.6184)"><circle r="7.5"></circle></g><g id="Node-8" style="fill:rgb(60.0%,83.5%,58.0%)" transform="translate(58.9612,132.593)"><circle r="7.5"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.443,216.009)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.443,176.754)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.443,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.443,98.2456)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.443,58.9912)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# draw with node colors extracted and colormapped to BlueRed from "C"
tree.draw(node_sizes=15, node_mask=False, node_colors=("C", "BlueRed"));
```


<div class="toyplot" id="td7896d615dff4a0ebcb59e865c6cb775" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t758c1c7d4dbf46898d066076f2e5e0ea"><g class="toyplot-coordinates-Cartesian" id="t2ae705ccd60e4a2a9a31808e0585a172"><clipPath id="td90021c51dd343ee98924f0557475424"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#td90021c51dd343ee98924f0557475424)"></g></g><g class="toyplot-coordinates-Cartesian" id="t947f7f0b8c244aacb6d604c0c2c2c64e"><clipPath id="tdf8e3a6234ed40d98d0d214381071fb1"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tdf8e3a6234ed40d98d0d214381071fb1)"><g class="toytree-mark-Toytree" id="t2f081957de0c4536918c11d2e7529dd6"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 92.1 186.6 L 92.1 216.0 L 224.4 216.0" id="6,0" style=""></path><path d="M 158.3 157.1 L 158.3 176.8 L 224.4 176.8" id="5,1" style=""></path><path d="M 158.3 157.1 L 158.3 137.5 L 224.4 137.5" id="5,2" style=""></path><path d="M 92.1 78.6 L 92.1 98.2 L 224.4 98.2" id="7,3" style=""></path><path d="M 92.1 78.6 L 92.1 59.0 L 224.4 59.0" id="7,4" style=""></path><path d="M 92.1 186.6 L 92.1 157.1 L 158.3 157.1" id="6,5" style=""></path><path d="M 59.0 132.6 L 59.0 186.6 L 92.1 186.6" id="8,6" style=""></path><path d="M 59.0 132.6 L 59.0 78.6 L 92.1 78.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(93.7%,54.1%,38.4%)" transform="translate(224.443,216.009)"><circle r="7.5"></circle></g><g id="Node-1" style="fill:rgb(93.7%,54.1%,38.4%)" transform="translate(224.443,176.754)"><circle r="7.5"></circle></g><g id="Node-2" style="fill:rgb(93.7%,54.1%,38.4%)" transform="translate(224.443,137.5)"><circle r="7.5"></circle></g><g id="Node-3" style="fill:rgb(40.4%,66.3%,81.2%)" transform="translate(224.443,98.2456)"><circle r="7.5"></circle></g><g id="Node-4" style="fill:rgb(40.4%,66.3%,81.2%)" transform="translate(224.443,58.9912)"><circle r="7.5"></circle></g><g id="Node-5" style="fill:rgb(93.7%,54.1%,38.4%)" transform="translate(158.25,157.127)"><circle r="7.5"></circle></g><g id="Node-6" style="fill:rgb(93.7%,54.1%,38.4%)" transform="translate(92.0575,186.568)"><circle r="7.5"></circle></g><g id="Node-7" style="fill:rgb(40.4%,66.3%,81.2%)" transform="translate(92.0575,78.6184)"><circle r="7.5"></circle></g><g id="Node-8" style="fill:rgb(40.4%,66.3%,81.2%)" transform="translate(58.9612,132.593)"><circle r="7.5"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.443,216.009)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.443,176.754)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.443,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.443,98.2456)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.443,58.9912)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# draw with node colors extracted and colormapped to BlueRed from "D"
tree.draw(node_sizes=15, node_mask=False, node_colors=("D", "BlueRed"));
```


<div class="toyplot" id="t82f2bd9f549c477388815aa59d2070c9" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t812a25327e714474b62c15945680cf16"><g class="toyplot-coordinates-Cartesian" id="ta5b07720e0b74fd29d927241a6d86918"><clipPath id="t4a8b01052e944965ac9c8b9420aa786d"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t4a8b01052e944965ac9c8b9420aa786d)"></g></g><g class="toyplot-coordinates-Cartesian" id="tc4693ce5ddd24f69bd62592ef9d571bc"><clipPath id="te93f1b11e52043dfb855cc7acfbd978e"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#te93f1b11e52043dfb855cc7acfbd978e)"><g class="toytree-mark-Toytree" id="tfd047d13bb974ff690289ba44501fe2a"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 92.1 186.6 L 92.1 216.0 L 224.4 216.0" id="6,0" style=""></path><path d="M 158.3 157.1 L 158.3 176.8 L 224.4 176.8" id="5,1" style=""></path><path d="M 158.3 157.1 L 158.3 137.5 L 224.4 137.5" id="5,2" style=""></path><path d="M 92.1 78.6 L 92.1 98.2 L 224.4 98.2" id="7,3" style=""></path><path d="M 92.1 78.6 L 92.1 59.0 L 224.4 59.0" id="7,4" style=""></path><path d="M 92.1 186.6 L 92.1 157.1 L 158.3 157.1" id="6,5" style=""></path><path d="M 59.0 132.6 L 59.0 186.6 L 92.1 186.6" id="8,6" style=""></path><path d="M 59.0 132.6 L 59.0 78.6 L 92.1 78.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(79.9%,29.6%,26.4%)" transform="translate(224.443,216.009)"><circle r="7.5"></circle></g><g id="Node-1" style="fill:rgb(2.0%,18.8%,38.0%)" transform="translate(224.443,176.754)"><circle r="7.5"></circle></g><g id="Node-2" style="fill:rgb(96.7%,70.5%,58.4%)" transform="translate(224.443,137.5)"><circle r="7.5"></circle></g><g id="Node-3" style="fill:rgb(85.6%,91.5%,94.8%)" transform="translate(224.443,98.2456)"><circle r="7.5"></circle></g><g id="Node-4" style="fill:rgb(83.2%,90.4%,94.3%)" transform="translate(224.443,58.9912)"><circle r="7.5"></circle></g><g id="Node-5" style="fill:rgb(47.8%,71.3%,83.8%)" transform="translate(158.25,157.127)"><circle r="7.5"></circle></g><g id="Node-6" style="fill:rgb(40.4%,0.0%,12.2%)" transform="translate(92.0575,186.568)"><circle r="7.5"></circle></g><g id="Node-7" style="fill:rgb(87.6%,46.0%,36.6%)" transform="translate(92.0575,78.6184)"><circle r="7.5"></circle></g><g id="Node-8" style="fill:rgb(76.2%,22.2%,22.9%)" transform="translate(58.9612,132.593)"><circle r="7.5"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.443,216.009)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.443,176.754)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.443,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.443,98.2456)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.443,58.9912)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Node vs Edge features
Some data stored to a tree are intended to represent information about the edges (splits) in a tree, rather than information about the nodes. This is important as these types of data must be treated differently when doing things like re-rooting a tree, and in some cases, for visualization. (See the [rooting](/toytree/rooting) tutorial for an example of how this is automatically handled in `toytree`.) Any feature can be optionally plotted as a marker and/or label on edges of a tree rather than on nodes. This can be done in a simple way within the `.draw` function by using the argument `node_as_edge_data=True`, or, it can be done with many more options by using functions in the `toytree.annotate` subpackage.

Examples of plotted edge features are shown below. These have a few key features in visualization: (1) values are plotted on the midpoint of edges; (2) No value is shown for the root edge, since it does not represent a true split in the tree; and (3) only one of the two edges descended from the root show a value, since these are actually the same edge, but on which the root node has been placed. As an example of this last point, a value such as a support score, or edge length, is a feature of this entire edge. Thus, the value is the same whether the tree is rooted or unrooted, as shown below.


```python
# draw a feature as EDGE data 
tree.draw(
    node_mask=False, 
    node_labels="idx", 
    node_labels_style={'font-size': 18},
    node_as_edge_data=True,
);
```


<div class="toyplot" id="t05c6c20fc44e49069f84080f408a291c" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tebd96b6cfb13452f8d8ceee1d75ce0fc"><g class="toyplot-coordinates-Cartesian" id="t95ffc427a1544da5be244593c3ee3365"><clipPath id="te8e7ed3b06cc498ba4b51fc0da7a1b37"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#te8e7ed3b06cc498ba4b51fc0da7a1b37)"></g></g><g class="toyplot-coordinates-Cartesian" id="t5a574a5dafcd4e3798bb9bb555301ac3"><clipPath id="t5dd341b0316d419c9b1280d5436e885a"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t5dd341b0316d419c9b1280d5436e885a)"><g class="toytree-mark-Toytree" id="tf1a7183882cf47259ca8a1ae4fd23cdf"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 88.9 185.4 L 88.9 214.2 L 224.4 214.2" id="6,0" style=""></path><path d="M 156.6 156.7 L 156.6 175.9 L 224.4 175.9" id="5,1" style=""></path><path d="M 156.6 156.7 L 156.6 137.5 L 224.4 137.5" id="5,2" style=""></path><path d="M 88.9 80.0 L 88.9 99.1 L 224.4 99.1" id="7,3" style=""></path><path d="M 88.9 80.0 L 88.9 60.8 L 224.4 60.8" id="7,4" style=""></path><path d="M 88.9 185.4 L 88.9 156.7 L 156.6 156.7" id="6,5" style=""></path><path d="M 55.0 132.7 L 55.0 185.4 L 88.9 185.4" id="8,6" style=""></path><path d="M 55.0 132.7 L 55.0 80.0 L 88.9 80.0" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:18px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(156.642,214.218)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(190.526,175.859)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(190.526,137.5)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(156.642,99.1411)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(156.642,60.7822)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(122.757,156.679)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(71.9309,185.449)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.41,214.218)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.41,175.859)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.41,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.41,99.1411)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.41,60.7822)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# draw a feature as EDGE data for the same tree, unrooted.
tree.unroot().draw(
    node_mask=False, 
    node_labels="idx", 
    node_labels_style={'font-size': 18},
    node_as_edge_data=True,
);
```


<div class="toyplot" id="t623e0aa8ee7a44329adc2f8516561cc6" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t1a5f0b4e672040ec8ace44924704a5d2"><g class="toyplot-coordinates-Cartesian" id="t5c1f585a427b468c8de7c90e4745d81c"><clipPath id="t11675f914f4740b9b6cac8a632bb9f4a"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t11675f914f4740b9b6cac8a632bb9f4a)"></g></g><g class="toyplot-coordinates-Cartesian" id="t8b3c2d4e6def49d68a5a4697de9b21eb"><clipPath id="tde5c68a7b78946f69612a7295919401e"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tde5c68a7b78946f69612a7295919401e)"><g class="toytree-mark-Toytree" id="t9d92d34812ac416da0dd027c1fa4b25a"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 55.0 150.3 L 55.0 214.2 L 167.9 214.2" id="7,0" style=""></path><path d="M 111.5 156.7 L 111.5 175.9 L 167.9 175.9" id="5,1" style=""></path><path d="M 111.5 156.7 L 111.5 137.5 L 167.9 137.5" id="5,2" style=""></path><path d="M 111.5 80.0 L 111.5 99.1 L 224.4 99.1" id="6,3" style=""></path><path d="M 111.5 80.0 L 111.5 60.8 L 224.4 60.8" id="6,4" style=""></path><path d="M 55.0 150.3 L 55.0 156.7 L 111.5 156.7" id="7,5" style=""></path><path d="M 55.0 150.3 L 55.0 80.0 L 111.5 80.0" id="7,6" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:18px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(111.463,214.218)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(139.7,175.859)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(139.7,137.5)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(167.937,99.1411)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(167.937,60.7822)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(83.2257,156.679)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(83.2257,79.9616)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:18.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(167.937,214.218)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(167.937,175.859)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(167.937,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.41,99.1411)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.41,60.7822)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


Annotation methods can also be used to plot edge data. See the annotation docs.


```python
# annotate a tree with EDGE data
canvas, axes, mark = tree.draw();
tree.annotate.add_edge_labels(axes=axes, labels="idx", font_size=18, mask=False);
```


<div class="toyplot" id="t405b2e334b8c4fab8321150c11c9fdcf" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="ta88b6ed0c1c442ad871409469715fe44"><g class="toyplot-coordinates-Cartesian" id="t3a9b2ff8ec824a70906572bfbe09f07f"><clipPath id="t62dd784e6aa84642ae7e1e6b94924f7e"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t62dd784e6aa84642ae7e1e6b94924f7e)"></g></g><g class="toyplot-coordinates-Cartesian" id="t51472cb9a35d4de196a76f7d987ec2f0"><clipPath id="t3bc7c71b670f4d3d8ec1603fb79eeabe"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t3bc7c71b670f4d3d8ec1603fb79eeabe)"><g class="toytree-mark-Toytree" id="t7409b59088b34787beb2e8c01a25d009"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 85.7 185.5 L 85.7 214.3 L 224.7 214.3" id="6,0" style=""></path><path d="M 155.2 156.7 L 155.2 175.9 L 224.7 175.9" id="5,1" style=""></path><path d="M 155.2 156.7 L 155.2 137.5 L 224.7 137.5" id="5,2" style=""></path><path d="M 85.7 79.9 L 85.7 99.1 L 224.7 99.1" id="7,3" style=""></path><path d="M 85.7 79.9 L 85.7 60.7 L 224.7 60.7" id="7,4" style=""></path><path d="M 85.7 185.5 L 85.7 156.7 L 155.2 156.7" id="6,5" style=""></path><path d="M 51.0 132.7 L 51.0 185.5 L 85.7 185.5" id="8,6" style=""></path><path d="M 51.0 132.7 L 51.0 79.9 L 85.7 79.9" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.728,214.344)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.728,175.922)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.728,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.728,99.0778)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.728,60.6555)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g></g></g><g class="toyplot-mark-Text" id="t08b0e872a2d144058e6221774fdf4b40"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(155.2308940550154,214.34449734970275)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:18.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g class="toyplot-Datum" transform="translate(189.9796738888796,175.92224867485137)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:18.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g class="toyplot-Datum" transform="translate(189.9796738888796,137.5)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:18.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g class="toyplot-Datum" transform="translate(155.2308940550154,99.07775132514863)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:18.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g class="toyplot-Datum" transform="translate(155.2308940550154,60.655502650297265)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:18.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g class="toyplot-Datum" transform="translate(120.48211422115119,156.7111243374257)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:18.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">5</text></g><g class="toyplot-Datum" transform="translate(68.35894447035491,185.5278108435642)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:18.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">8</text></g><g class="toyplot-Datum" transform="translate(68.35894447035491,79.86662698772295)"><text x="-5.0040000000000004" y="4.599" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:18.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">8</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>

