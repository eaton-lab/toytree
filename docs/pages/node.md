<div class="nb-md-page-hook" aria-hidden="true"></div>

# toytree.Node

The `toytree.Node` class is primarily used for data storage. Minimally, it contains attributes storing a `.name`, `.dist` (edge length), and `.support` values, as well as attributes `.up` and `.children` which point to other `Node` objects to represent connections between them.

A single `Node` instance is generally of little use, it is only when nodes form connections that they have emergent properties in the form  a network/tree structure. Thus, most methods in the `toytree` library are associated with `ToyTree` objects which are a container around a collection of `Nodes`. However, `Node` objects themselves are important to understand as the underlying object storing data within trees. This section describes the structure of `Node` objects and the design behind their intended use.


```python
import toytree
```


```python
# create an example tree
tree = toytree.rtree.rtree(ntips=8, seed=321)
tree.draw('c');
```


<div class="toyplot" id="tbed292d06ffc44cf90f6434dbb51d278" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t36502208a4634521a62d427658744335"><g class="toyplot-coordinates-Cartesian" id="tebade6fa0d534fa4848984942d00a0fd"><clipPath id="t35a0c41bfc324ed686b659f5efb86654"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t35a0c41bfc324ed686b659f5efb86654)"></g><g class="toyplot-coordinates-Axis" id="t122ff39ede1b41298d5e8c269b06e4a4" transform="translate(50.0,250.0)rotate(-90.0)translate(0,-15.0)"><line x1="22.29320307584091" y1="0" x2="195.0826709290981" y2="0" style=""></line><g><line x1="22.29320307584091" y1="0" x2="22.29320307584091" y2="5" style=""></line><line x1="71.66162246248582" y1="0" x2="71.66162246248582" y2="5" style=""></line><line x1="121.03004184913073" y1="0" x2="121.03004184913073" y2="5" style=""></line><line x1="170.39846123577564" y1="0" x2="170.39846123577564" y2="5" style=""></line></g><g><g transform="translate(22.29320307584091,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(71.66162246248582,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(121.03004184913073,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(170.39846123577564,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="tac60fc65f7f74b428a3d6fd9abb0385b"><clipPath id="t7efe3ebb1bf145acb36cf3fcf2214b7c"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t7efe3ebb1bf145acb36cf3fcf2214b7c)"><g class="toytree-mark-Toytree" id="tcf23000127ec4010ad418a419388fead"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 70.4 129.0 L 57.2 178.3" id="8,0" style=""></path><path d="M 70.4 129.0 L 83.7 178.3" id="8,1" style=""></path><path d="M 90.3 79.6 L 110.2 129.0" id="9,2" style=""></path><path d="M 150.0 129.0 L 136.7 178.3" id="10,3" style=""></path><path d="M 150.0 129.0 L 163.3 178.3" id="10,4" style=""></path><path d="M 209.7 129.0 L 189.8 178.3" id="12,5" style=""></path><path d="M 229.6 178.3 L 216.3 227.7" id="11,6" style=""></path><path d="M 229.6 178.3 L 242.8 227.7" id="11,7" style=""></path><path d="M 90.3 79.6 L 70.4 129.0" id="9,8" style=""></path><path d="M 135.1 54.9 L 90.3 79.6" id="14,9" style=""></path><path d="M 179.8 79.6 L 150.0 129.0" id="13,10" style=""></path><path d="M 209.7 129.0 L 229.6 178.3" id="12,11" style=""></path><path d="M 179.8 79.6 L 209.7 129.0" id="13,12" style=""></path><path d="M 135.1 54.9 L 179.8 79.6" id="14,13" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(57.1653,178.338)"><circle r="3.5"></circle></g><g id="Node-1" transform="translate(83.6895,178.338)"><circle r="3.5"></circle></g><g id="Node-2" transform="translate(110.214,128.97)"><circle r="3.5"></circle></g><g id="Node-3" transform="translate(136.738,178.338)"><circle r="3.5"></circle></g><g id="Node-4" transform="translate(163.262,178.338)"><circle r="3.5"></circle></g><g id="Node-5" transform="translate(189.786,178.338)"><circle r="3.5"></circle></g><g id="Node-6" transform="translate(216.31,227.707)"><circle r="3.5"></circle></g><g id="Node-7" transform="translate(242.835,227.707)"><circle r="3.5"></circle></g><g id="Node-8" transform="translate(70.4274,128.97)"><circle r="3.5"></circle></g><g id="Node-9" transform="translate(90.3206,79.6015)"><circle r="3.5"></circle></g><g id="Node-10" transform="translate(150,128.97)"><circle r="3.5"></circle></g><g id="Node-11" transform="translate(229.573,178.338)"><circle r="3.5"></circle></g><g id="Node-12" transform="translate(209.679,128.97)"><circle r="3.5"></circle></g><g id="Node-13" transform="translate(179.84,79.6015)"><circle r="3.5"></circle></g><g id="Node-14" transform="translate(135.08,54.9173)"><circle r="3.5"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(57.1653,178.338)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(83.6895,178.338)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(110.214,128.97)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(136.738,178.338)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(163.262,178.338)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(189.786,178.338)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(216.31,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(242.835,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t36502208a4634521a62d427658744335";
modules["toyplot/canvas"] = (function(canvas_id)
    {
        return document.querySelector("#" + canvas_id);
    })(modules["toyplot/canvas/id"]);
modules["toyplot.coordinates.Axis"] = (
        function(canvas)
        {
            function sign(x)
            {
                return x < 0 ? -1 : x > 0 ? 1 : 0;
            }

            function mix(a, b, amount)
            {
                return ((1.0 - amount) * a) + (amount * b);
            }

            function log(x, base)
            {
                return Math.log(Math.abs(x)) / Math.log(base);
            }

            function in_range(a, x, b)
            {
                var left = Math.min(a, b);
                var right = Math.max(a, b);
                return left <= x && x <= right;
            }

            function inside(range, projection)
            {
                for(var i = 0; i != projection.length; ++i)
                {
                    var segment = projection[i];
                    if(in_range(segment.range.min, range, segment.range.max))
                        return true;
                }
                return false;
            }

            function to_domain(range, projection)
            {
                for(var i = 0; i != projection.length; ++i)
                {
                    var segment = projection[i];
                    if(in_range(segment.range.bounds.min, range, segment.range.bounds.max))
                    {
                        if(segment.scale == "linear")
                        {
                            var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                            return mix(segment.domain.min, segment.domain.max, amount)
                        }
                        else if(segment.scale[0] == "log")
                        {
                            var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                            var base = segment.scale[1];
                            return sign(segment.domain.min) * Math.pow(base, mix(log(segment.domain.min, base), log(segment.domain.max, base), amount));
                        }
                    }
                }
            }

            var axes = {};

            function display_coordinates(e)
            {
                var current = canvas.createSVGPoint();
                current.x = e.clientX;
                current.y = e.clientY;

                for(var axis_id in axes)
                {
                    var axis = document.querySelector("#" + axis_id);
                    var coordinates = axis.querySelector(".toyplot-coordinates-Axis-coordinates");
                    if(coordinates)
                    {
                        var projection = axes[axis_id];
                        var local = current.matrixTransform(axis.getScreenCTM().inverse());
                        if(inside(local.x, projection))
                        {
                            var domain = to_domain(local.x, projection);
                            coordinates.style.visibility = "visible";
                            coordinates.setAttribute("transform", "translate(" + local.x + ")");
                            var text = coordinates.querySelector("text");
                            text.textContent = domain.toFixed(2);
                        }
                        else
                        {
                            coordinates.style.visibility= "hidden";
                        }
                    }
                }
            }

            canvas.addEventListener("click", display_coordinates);

            var module = {};
            module.show_coordinates = function(axis_id, projection)
            {
                axes[axis_id] = projection;
            }

            return module;
        })(modules["toyplot/canvas"]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"t122ff39ede1b41298d5e8c269b06e4a4",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 3.5996047499999997, "min": -0.45156809459999936}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


## The Node class
The `Node` class is accessible from `toytree.Node` and can be used to create new instances or to check or validate the type of a `Node` instance. Unless you are a developer you are not likely to create new `Node` objects often, but instead will most often interact them by selecting them from within `ToyTrees`.


```python
# create a new Node
single_node = toytree.Node(name="single")
single_node
```




    <Node(name='single')>




```python
# select a Node from a ToyTree
node3 = tree[3]
node3
```




    <Node(idx=3, name='r3')>




```python
# check that an object's type is a Node 
isinstance(node3, toytree.Node)
```




    True



## Attributes
### name: <span style="color:gray">str</span>
The default `name` attribute is an empty string. Leaf nodes usually have names associated with them whereas internal nodes usually do not. This will depend on the data that a tree is parsed or constructed from, and whether additional names are added. Some characters are not allowed in node names (`[:;(),\[\]\t\n\r=]`) as they would interfere with Newick string parsing when written to a file. Names can be accessed from a `Node`'s `.name` attribute, and can be used to query nodes from a `ToyTree`.


```python
# a name can be accessed from a Node
single_node.name
```




    'single'




```python
# a name can be accessed from a Node in a ToyTree
tree[3].name
```




    'r3'




```python
# returns .name from Nodes in the order they will be plotted (idxorder)
tree.get_tip_labels()
```




    ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7']



### idx: <span style="color:gray">int</span>
The default `idx` attribute is an int value of -1, which means that the node is not part of a `ToyTree`. If a node is in a `ToyTree` then it will be assigned a unique idx integer between 0 and nnodes-1. The leaf nodes in a tree have idx values between 0 and ntips - 1, and all internal nodes are labeled by increasing numbers in a post-order left-then-right traversal. This is termed an idxorder traversal. When a tree structure changes (e.g. during re-rooting) the idx values of nodes are updated and can change (see [Traversal](/toytree/traversal/)). A node's idx value can be checked from its `.idx` attribute, or if it is in a `ToyTree` then by calling `.get_node_data()` or plotting the tree to visualize idx values.  


```python
# a Node that is not part of a ToyTree has idx=-1
single_node.idx
```




    -1




```python
# Nodes in a ToyTree have unique idx values between 0 and nnodes - 1
node3.idx
```




    3



### dist: <span style="color:gray">float</span>
The default `dist` attribute is a float of 0. The value represents the distance from a node **to its parent**. In other words, it is the length of an edge connecting them. The dist attribute is thus not actually a feature of a node, but of an edge between nodes, but is nevertheless stored to a `Node` object. We call this an `edge_feature` of a `Node`, since it will change if the tree is re-rooted, changing which Node is parent to another. The value of a dist can range from very small to very large values, such as when representing the expected number of substitutions per site on a phylogeny, or divergence times in millions of years. 


```python
# default Node dist
single_node.dist
```




    0.0




```python
# the dist from node 3 to its parent
node3.dist
```




    1.0



### support: <span style="color:gray">float</span>
The default `support` value is `numpy.nan`, which represents the absence of support information. Tip (leaf) nodes are not expected to have support information, since they do not represent a split in a tree. Similarly, the root node support is `nan` since it does not represent a true split. 


```python
# the default support value
single_node.support
```




    nan



### up: <span style="color:gray">Node</span>
The `.up` attribute references a node's parent. The default value is `None`. This is also the value of the `.up` attribute of the root `Node` in a `ToyTree`, since it has no parent. A `Node` can only have one parent. If a tree is re-rooted the relationship between nodes can change such that a `Node` that was previously a child can become a parent, and thus the `Node` attributes are automatically updated during this process.


```python
# the default .up is None (no value is returned here)
single_node.up
```


```python
# node3's parent is Node 10
node3.up
```




    <Node(idx=10)>




```python
# the parent of node3's parent is Node 11
node3.up.up
```




    <Node(idx=13)>



### children: <span style="color:gray">tuple</span>
The `.children` attribute is a tuple of zero or more `Node` objects that are descended from a node. The default is an empty tuple. If a tree is re-rooted the relationship between nodes can change such that a `Node` that was previously a child can become a parent, and thus the `Node` attributes are automatically updated during this process.


```python
# this single Node has no children
single_node.children
```




    ()




```python
# internal Node 8 in the tree has two children
tree[8].children
```




    (<Node(idx=0, name='r0')>, <Node(idx=1, name='r1')>)



### height: <span style="color:gray">float</span>
The default `height` value is a float of 0. The height of a `Node` is an emergent property of a tree of connected nodes. It is the height above the node that is the farthest distance from the root. This value is automatically updated for every node in a `ToyTree` when a tree is modified during the cached traversal.


```python
# single node has not height
single_node.height
```




    0.0




```python
# leaf node 3 height
node3.height
```




    1.0




```python
# internal node 8 height
tree[8].height
```




    2.0



## Methods
The `Node` object provides a number of functions for fetching information about a node's position relative to other connected nodes. Some of this information is also accessible from a `ToyTree` object, but is sometimes easier to access it from a Node object directly.


```python
node3.is_leaf()
```




    True




```python
node3.is_root()
```




    False




```python
node3.get_ancestors()
```




    (<Node(idx=10)>, <Node(idx=13)>, <Node(idx=14)>)




```python
node3.get_descendants()
```




    (<Node(idx=3, name='r3')>,)




```python
node3.get_leaves()
```




    [<Node(idx=3, name='r3')>]




```python
node3.get_sisters()
```




    (<Node(idx=4, name='r4')>,)




```python
node3.get_leaf_names()
```




    ['r3']



Each of the `get_[x]` functions above is also available as a generator function named `iter_[x]`, which is more efficient for fetching such data over very large trees, or for terminating a traversal over part of the tree once a condition has been met. The `traverse()` function is also a generator function.


```python
node3.iter_ancestors()
```




    <generator object Node.iter_ancestors at 0x7592b80eb060>




```python
node3.traverse("idxorder")
```




    <generator object Node._traverse_idxorder at 0x759230b96a40>



## Nodes vs 'Edges'
Notably, `toytree` does not implement a separate "Edge" class to represent edges in a tree. Instead, edges are simply represented by the connections between `Node` objects -- by their `.up` and `.children` attributes. (This can be important when storing new data types to a tree; see [Edge features](/toytree/data/#node-vs-edge-features)). Thus you can think of edges as pairs of nodes. You can fetch the edge information from a `ToyTree` in a variety of ways. Below we use the function `get_edges` which has options for returning this information in a number of tabular formats.


```python
# edges are simply pairs of Nodes with a child,parent relationship
tree.get_edges(feature='idx', df=True)
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
      <th>child</th>
      <th>parent</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>8</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>8</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>9</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>10</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>10</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td>12</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td>11</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td>11</td>
    </tr>
    <tr>
      <th>8</th>
      <td>8</td>
      <td>9</td>
    </tr>
    <tr>
      <th>9</th>
      <td>9</td>
      <td>14</td>
    </tr>
    <tr>
      <th>10</th>
      <td>10</td>
      <td>13</td>
    </tr>
    <tr>
      <th>11</th>
      <td>11</td>
      <td>12</td>
    </tr>
    <tr>
      <th>12</th>
      <td>12</td>
      <td>13</td>
    </tr>
    <tr>
      <th>13</th>
      <td>13</td>
      <td>14</td>
    </tr>
  </tbody>
</table>
</div>



## Mutability of Nodes
The data assigned to nodes may represent a feature of the node itself, or it may represent a feature of the edge connecting that node to its parent. In the latter case, it is important that the data be treated appropriately if the tree is modified, such as when a node is pruned from the tree, or the tree is re-rooted. In these cases, the edge features, such as the `.dist`, `.support`, and the connection information `.up` and `.children`, need to be automatically updated. Similarly, emergent properties of nodes in a tree, such as the `.height` of a node relative to the farthest leaf must be re-computed.

The automatic updating of these attributes is done at the level of a `ToyTree`, not within individual `Nodes`, and thus we have intentionally designed these elements of `Node` objects to be immutable (you cannot modify them directly). Thus, users cannot call `node.idx = 3`  or `node.height = 100` to set these atrributes to a new value, since these attributes are properties of the node's placement with respect to other nodes in the tree, which need to also be updated. If you try to set one of these values a `ToyTreeError` exception will be raised like in the example below where we catch the exception and print it. For developers there is a simple workaround for this described further below.


```python
# catch 'ToyTreeError' exception raised when trying to modify a Node attribute
try:
    single_node.idx = 10
except toytree.utils.ToytreeError as exc:
    print("ToyTreeError:", exc)
```

    ToyTreeError: Cannot set .idx attribute of a Node. If you are an advanced user then you can do so by setting ._idx. See the docs section on Modifying Nodes and Tree Topology.


### Calling mod functions
Instead of modifying a node's attributes directly you should instead call one of the tree modification functions from the `toytree.mod` subpackage that will ensure that the rest of the tree data is automatically updated along with the modified node data. Examples include the `.root`, `.drop_tips`, `prune`, `ladderize`, `rotate_nodes`, `edges_set_node_heights`, and many others which modify one or more `.up`, `.children`, `.idx`, `.dist`, or `.height` attributes of nodes in unison.


```python
# an example toytree.mod function that modifies node attributes
rtree = tree.mod.root("r4")

# the new tree has different idx values b/c the traversal order changed
toytree.mtree([tree, rtree]).draw(ts='p');
```


<div class="toyplot" id="t8fccba9cbf4e43d1a22f4edf012ae3da" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="900.0px" height="250.0px" viewBox="0 0 900.0 250.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t800c2c585577407ba679b31bed155252"><g class="toyplot-coordinates-Cartesian" id="t7d13775212fe47afa180bf1449dc02f3"><clipPath id="t9fef7f00dade46c78fdb155ec97376cf"><rect x="20.0" y="40.0" width="205.0" height="170.0"></rect></clipPath><g clip-path="url(#t9fef7f00dade46c78fdb155ec97376cf)"></g><g class="toyplot-coordinates-Axis" id="tb7746f5be564471a91ac2853af56af87" transform="translate(30.0,200.0)rotate(-90.0)translate(0,-10.0)"><line x1="18.795886483288783" y1="0" x2="141.54234859142642" y2="0" style=""></line><g><line x1="18.795886483288783" y1="0" x2="18.795886483288783" y2="5" style=""></line><line x1="53.86630422847096" y1="0" x2="53.86630422847096" y2="5" style=""></line><line x1="88.93672197365315" y1="0" x2="88.93672197365315" y2="5" style=""></line><line x1="124.00713971883533" y1="0" x2="124.00713971883533" y2="5" style=""></line></g><g><g transform="translate(18.795886483288783,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(53.86630422847096,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(88.93672197365315,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(124.00713971883533,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="tb28bf9eb696842b591d553f308bfe6e5"><clipPath id="t3dea7a0ad9cd4eaca6da64c9c1071bc0"><rect x="20.0" y="40.0" width="205.0" height="170.0"></rect></clipPath><g clip-path="url(#t3dea7a0ad9cd4eaca6da64c9c1071bc0)"><g class="toytree-mark-Toytree" id="ta9573f5b12e44989ad8fc4d8e9976f79"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 50.5 111.1 L 38.5 146.1" id="8,0" style=""></path><path d="M 50.5 111.1 L 62.5 146.1" id="8,1" style=""></path><path d="M 68.5 76.0 L 86.5 111.1" id="9,2" style=""></path><path d="M 122.5 111.1 L 110.5 146.1" id="10,3" style=""></path><path d="M 122.5 111.1 L 134.5 146.1" id="10,4" style=""></path><path d="M 176.5 111.1 L 158.5 146.1" id="12,5" style=""></path><path d="M 194.5 146.1 L 182.5 181.2" id="11,6" style=""></path><path d="M 194.5 146.1 L 206.5 181.2" id="11,7" style=""></path><path d="M 68.5 76.0 L 50.5 111.1" id="9,8" style=""></path><path d="M 109.0 58.5 L 68.5 76.0" id="14,9" style=""></path><path d="M 149.5 76.0 L 122.5 111.1" id="13,10" style=""></path><path d="M 176.5 111.1 L 194.5 146.1" id="12,11" style=""></path><path d="M 149.5 76.0 L 176.5 111.1" id="13,12" style=""></path><path d="M 109.0 58.5 L 149.5 76.0" id="14,13" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.0"><g id="Node-0" transform="translate(38.494,146.134)"><circle r="7.5"></circle></g><g id="Node-1" transform="translate(62.4957,146.134)"><circle r="7.5"></circle></g><g id="Node-2" transform="translate(86.4974,111.063)"><circle r="7.5"></circle></g><g id="Node-3" transform="translate(110.499,146.134)"><circle r="7.5"></circle></g><g id="Node-4" transform="translate(134.501,146.134)"><circle r="7.5"></circle></g><g id="Node-5" transform="translate(158.503,146.134)"><circle r="7.5"></circle></g><g id="Node-6" transform="translate(182.504,181.204)"><circle r="7.5"></circle></g><g id="Node-7" transform="translate(206.506,181.204)"><circle r="7.5"></circle></g><g id="Node-8" transform="translate(50.4949,111.063)"><circle r="7.5"></circle></g><g id="Node-9" transform="translate(68.4961,75.9929)"><circle r="7.5"></circle></g><g id="Node-10" transform="translate(122.5,111.063)"><circle r="7.5"></circle></g><g id="Node-11" transform="translate(194.505,146.134)"><circle r="7.5"></circle></g><g id="Node-12" transform="translate(176.504,111.063)"><circle r="7.5"></circle></g><g id="Node-13" transform="translate(149.502,75.9929)"><circle r="7.5"></circle></g><g id="Node-14" transform="translate(108.999,58.4577)"><circle r="7.5"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(38.494,146.134)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(62.4957,146.134)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(86.4974,111.063)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(110.499,146.134)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(134.501,146.134)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(158.503,146.134)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(182.504,181.204)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(206.506,181.204)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(50.4949,111.063)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(68.4961,75.9929)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(122.5,111.063)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(194.505,146.134)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(176.504,111.063)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(149.502,75.9929)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(108.999,58.4577)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(38.494,146.134)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(62.4957,146.134)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(86.4974,111.063)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(110.499,146.134)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(134.501,146.134)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(158.503,146.134)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(182.504,181.204)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(206.506,181.204)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t9dcb9abd7e5a4542b565ae2cabdcd010"><clipPath id="tada183ad0bdb43a1b11d83a034af5ed8"><rect x="245.0" y="40.0" width="205.0" height="170.0"></rect></clipPath><g clip-path="url(#tada183ad0bdb43a1b11d83a034af5ed8)"></g><g class="toyplot-coordinates-Axis" id="td1f5353fd3d44325b5f3bf654d3a02b5" transform="translate(255.0,200.0)rotate(-90.0)translate(0,-10.0)"><line x1="18.795886483288783" y1="0" x2="141.54234859142645" y2="0" style=""></line><g><line x1="18.795886483288783" y1="0" x2="18.795886483288783" y2="5" style=""></line><line x1="46.07287806287493" y1="0" x2="46.07287806287493" y2="5" style=""></line><line x1="73.34986964246107" y1="0" x2="73.34986964246107" y2="5" style=""></line><line x1="100.62686122204722" y1="0" x2="100.62686122204722" y2="5" style=""></line><line x1="127.90385280163336" y1="0" x2="127.90385280163336" y2="5" style=""></line></g><g><g transform="translate(18.795886483288783,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(46.07287806287493,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(73.34986964246107,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(100.62686122204722,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(127.90385280163336,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="t1deca7e2d7674b888bf9107cf6a41e6a"><clipPath id="te256f7865a78427882dd59e2be1fef00"><rect x="245.0" y="40.0" width="205.0" height="170.0"></rect></clipPath><g clip-path="url(#te256f7865a78427882dd59e2be1fef00)"><g class="toytree-mark-Toytree" id="t613556fafd6845269c9224eb6e68cac5"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 296.5 58.5 L 263.5 72.1" id="14,0" style=""></path><path d="M 329.5 72.1 L 287.5 99.4" id="13,1" style=""></path><path d="M 329.5 126.7 L 311.5 153.9" id="9,2" style=""></path><path d="M 347.5 153.9 L 335.5 181.2" id="8,3" style=""></path><path d="M 347.5 153.9 L 359.5 181.2" id="8,4" style=""></path><path d="M 395.5 153.9 L 383.5 181.2" id="10,5" style=""></path><path d="M 395.5 153.9 L 407.5 181.2" id="10,6" style=""></path><path d="M 413.5 126.7 L 431.5 153.9" id="11,7" style=""></path><path d="M 329.5 126.7 L 347.5 153.9" id="9,8" style=""></path><path d="M 371.5 99.4 L 329.5 126.7" id="12,9" style=""></path><path d="M 413.5 126.7 L 395.5 153.9" id="11,10" style=""></path><path d="M 371.5 99.4 L 413.5 126.7" id="12,11" style=""></path><path d="M 329.5 72.1 L 371.5 99.4" id="13,12" style=""></path><path d="M 296.5 58.5 L 329.5 72.1" id="14,13" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.0"><g id="Node-0" transform="translate(263.494,72.0961)"><circle r="7.5"></circle></g><g id="Node-1" transform="translate(287.496,99.3731)"><circle r="7.5"></circle></g><g id="Node-2" transform="translate(311.497,153.927)"><circle r="7.5"></circle></g><g id="Node-3" transform="translate(335.499,181.204)"><circle r="7.5"></circle></g><g id="Node-4" transform="translate(359.501,181.204)"><circle r="7.5"></circle></g><g id="Node-5" transform="translate(383.503,181.204)"><circle r="7.5"></circle></g><g id="Node-6" transform="translate(407.504,181.204)"><circle r="7.5"></circle></g><g id="Node-7" transform="translate(431.506,153.927)"><circle r="7.5"></circle></g><g id="Node-8" transform="translate(347.5,153.927)"><circle r="7.5"></circle></g><g id="Node-9" transform="translate(329.499,126.65)"><circle r="7.5"></circle></g><g id="Node-10" transform="translate(395.503,153.927)"><circle r="7.5"></circle></g><g id="Node-11" transform="translate(413.505,126.65)"><circle r="7.5"></circle></g><g id="Node-12" transform="translate(371.502,99.3731)"><circle r="7.5"></circle></g><g id="Node-13" transform="translate(329.499,72.0961)"><circle r="7.5"></circle></g><g id="Node-14" transform="translate(296.496,58.4577)"><circle r="7.5"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(263.494,72.0961)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(287.496,99.3731)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(311.497,153.927)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(335.499,181.204)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(359.501,181.204)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(383.503,181.204)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(407.504,181.204)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(431.506,153.927)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(347.5,153.927)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(329.499,126.65)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(395.503,153.927)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(413.505,126.65)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(371.502,99.3731)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(329.499,72.0961)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(296.496,58.4577)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(263.494,72.0961)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(287.496,99.3731)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(311.497,153.927)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(335.499,181.204)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(359.501,181.204)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(383.503,181.204)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(407.504,181.204)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(431.506,153.927)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t1d49ef42d1c142fb9fc5c0ab15ce461b"><clipPath id="ta2a9766b8bfd4fbdb18dd38a459d6425"><rect x="470.0" y="40.0" width="205.0" height="170.0"></rect></clipPath><g clip-path="url(#ta2a9766b8bfd4fbdb18dd38a459d6425)"></g></g><g class="toyplot-coordinates-Cartesian" id="tfcc82fd8baca4cd7a00c2c42c8b2cc39"><clipPath id="tbf7a302024d740a9a49e4dcb8489e732"><rect x="695.0" y="40.0" width="205.0" height="170.0"></rect></clipPath><g clip-path="url(#tbf7a302024d740a9a49e4dcb8489e732)"></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t800c2c585577407ba679b31bed155252";
modules["toyplot/canvas"] = (function(canvas_id)
    {
        return document.querySelector("#" + canvas_id);
    })(modules["toyplot/canvas/id"]);
modules["toyplot.coordinates.Axis"] = (
        function(canvas)
        {
            function sign(x)
            {
                return x < 0 ? -1 : x > 0 ? 1 : 0;
            }

            function mix(a, b, amount)
            {
                return ((1.0 - amount) * a) + (amount * b);
            }

            function log(x, base)
            {
                return Math.log(Math.abs(x)) / Math.log(base);
            }

            function in_range(a, x, b)
            {
                var left = Math.min(a, b);
                var right = Math.max(a, b);
                return left <= x && x <= right;
            }

            function inside(range, projection)
            {
                for(var i = 0; i != projection.length; ++i)
                {
                    var segment = projection[i];
                    if(in_range(segment.range.min, range, segment.range.max))
                        return true;
                }
                return false;
            }

            function to_domain(range, projection)
            {
                for(var i = 0; i != projection.length; ++i)
                {
                    var segment = projection[i];
                    if(in_range(segment.range.bounds.min, range, segment.range.bounds.max))
                    {
                        if(segment.scale == "linear")
                        {
                            var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                            return mix(segment.domain.min, segment.domain.max, amount)
                        }
                        else if(segment.scale[0] == "log")
                        {
                            var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                            var base = segment.scale[1];
                            return sign(segment.domain.min) * Math.pow(base, mix(log(segment.domain.min, base), log(segment.domain.max, base), amount));
                        }
                    }
                }
            }

            var axes = {};

            function display_coordinates(e)
            {
                var current = canvas.createSVGPoint();
                current.x = e.clientX;
                current.y = e.clientY;

                for(var axis_id in axes)
                {
                    var axis = document.querySelector("#" + axis_id);
                    var coordinates = axis.querySelector(".toyplot-coordinates-Axis-coordinates");
                    if(coordinates)
                    {
                        var projection = axes[axis_id];
                        var local = current.matrixTransform(axis.getScreenCTM().inverse());
                        if(inside(local.x, projection))
                        {
                            var domain = to_domain(local.x, projection);
                            coordinates.style.visibility = "visible";
                            coordinates.setAttribute("transform", "translate(" + local.x + ")");
                            var text = coordinates.querySelector("text");
                            text.textContent = domain.toFixed(2);
                        }
                        else
                        {
                            coordinates.style.visibility= "hidden";
                        }
                    }
                }
            }

            canvas.addEventListener("click", display_coordinates);

            var module = {};
            module.show_coordinates = function(axis_id, projection)
            {
                axes[axis_id] = projection;
            }

            return module;
        })(modules["toyplot/canvas"]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"tb7746f5be564471a91ac2853af56af87",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 3.7411619807333336, "min": -0.535947037182666}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 150.0, "min": 0.0}, "scale": "linear"}]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"td1f5353fd3d44325b5f3bf654d3a02b5",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 4.8100654037999995, "min": -0.689074762091999}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 150.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


### Developing mod functions
Sometimes, however, you may really want to directly modify one or more core features of a `Node`, in which case it is possible, we just want to make sure that you are well aware of the necessary considerations to avoid errors in your code. You can examine the source code of the many `.mod` subpackage functions above for examples. Each of these core attributes is available as a private attribute (e.g., `._dist`, `._idx`) which *can* be modified without raising an exception. The key, however, is that after one or more private node attributes have been modified, the `ToyTree` traversal caching function named `._update()` must be called at the end to ensure that all of the linked attributes of nodes are updated.


```python
# create a new tree copy
modtree = tree.copy()

# modify one or more private node attributes
modtree[0]._dist += 2
modtree[1]._dist += 3

# call update to update idxs, heights, etc.
modtree._update()

# show the old and new tree with longer .dists for nodes 0,1 and .heights for all nodes
toytree.mtree([tree, modtree]).draw(ts='p', scale_bar=True);
```


<div class="toyplot" id="t9c1315dd05c946d6b2e0177de919c043" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="900.0px" height="250.0px" viewBox="0 0 900.0 250.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t9dc60106bff04b5fbe02a01f7bcc9d4b"><g class="toyplot-coordinates-Cartesian" id="tde41b1695ce0459499c06f0de9ea103c"><clipPath id="t49038b80f432461ea36ba6562a132474"><rect x="40.0" y="40.0" width="185.0" height="170.0"></rect></clipPath><g clip-path="url(#t49038b80f432461ea36ba6562a132474)"></g><g class="toyplot-coordinates-Axis" id="t63346b076ef2430d862a36da23a64090" transform="translate(50.0,200.0)rotate(-90.0)translate(0,-10.0)"><line x1="18.795886483288783" y1="0" x2="141.54234859142642" y2="0" style=""></line><g><line x1="18.795886483288783" y1="0" x2="18.795886483288783" y2="5" style=""></line><line x1="53.86630422847096" y1="0" x2="53.86630422847096" y2="5" style=""></line><line x1="88.93672197365315" y1="0" x2="88.93672197365315" y2="5" style=""></line><line x1="124.00713971883533" y1="0" x2="124.00713971883533" y2="5" style=""></line></g><g><g transform="translate(18.795886483288783,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(53.86630422847096,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(88.93672197365315,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(124.00713971883533,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="tef720ad3fbfb4068bb8f5e80838de86b"><clipPath id="t300a9bea53324cb2a7158338f03fce48"><rect x="40.0" y="40.0" width="185.0" height="170.0"></rect></clipPath><g clip-path="url(#t300a9bea53324cb2a7158338f03fce48)"><g class="toytree-mark-Toytree" id="tcad9e715bf9141ae8c0dfb605498f779"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 69.1 111.1 L 58.5 146.1" id="8,0" style=""></path><path d="M 69.1 111.1 L 79.6 146.1" id="8,1" style=""></path><path d="M 84.9 76.0 L 100.8 111.1" id="9,2" style=""></path><path d="M 132.5 111.1 L 121.9 146.1" id="10,3" style=""></path><path d="M 132.5 111.1 L 143.1 146.1" id="10,4" style=""></path><path d="M 180.1 111.1 L 164.2 146.1" id="12,5" style=""></path><path d="M 195.9 146.1 L 185.4 181.2" id="11,6" style=""></path><path d="M 195.9 146.1 L 206.5 181.2" id="11,7" style=""></path><path d="M 84.9 76.0 L 69.1 111.1" id="9,8" style=""></path><path d="M 120.6 58.5 L 84.9 76.0" id="14,9" style=""></path><path d="M 156.3 76.0 L 132.5 111.1" id="13,10" style=""></path><path d="M 180.1 111.1 L 195.9 146.1" id="12,11" style=""></path><path d="M 156.3 76.0 L 180.1 111.1" id="13,12" style=""></path><path d="M 120.6 58.5 L 156.3 76.0" id="14,13" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.0"><g id="Node-0" transform="translate(58.4917,146.134)"><circle r="7.5"></circle></g><g id="Node-1" transform="translate(79.6369,146.134)"><circle r="7.5"></circle></g><g id="Node-2" transform="translate(100.782,111.063)"><circle r="7.5"></circle></g><g id="Node-3" transform="translate(121.927,146.134)"><circle r="7.5"></circle></g><g id="Node-4" transform="translate(143.073,146.134)"><circle r="7.5"></circle></g><g id="Node-5" transform="translate(164.218,146.134)"><circle r="7.5"></circle></g><g id="Node-6" transform="translate(185.363,181.204)"><circle r="7.5"></circle></g><g id="Node-7" transform="translate(206.508,181.204)"><circle r="7.5"></circle></g><g id="Node-8" transform="translate(69.0643,111.063)"><circle r="7.5"></circle></g><g id="Node-9" transform="translate(84.9232,75.9929)"><circle r="7.5"></circle></g><g id="Node-10" transform="translate(132.5,111.063)"><circle r="7.5"></circle></g><g id="Node-11" transform="translate(195.936,146.134)"><circle r="7.5"></circle></g><g id="Node-12" transform="translate(180.077,111.063)"><circle r="7.5"></circle></g><g id="Node-13" transform="translate(156.288,75.9929)"><circle r="7.5"></circle></g><g id="Node-14" transform="translate(120.606,58.4577)"><circle r="7.5"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(58.4917,146.134)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(79.6369,146.134)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(100.782,111.063)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(121.927,146.134)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(143.073,146.134)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(164.218,146.134)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(185.363,181.204)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(206.508,181.204)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(69.0643,111.063)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(84.9232,75.9929)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(132.5,111.063)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(195.936,146.134)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(180.077,111.063)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(156.288,75.9929)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(120.606,58.4577)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(58.4917,146.134)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(79.6369,146.134)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(100.782,111.063)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(121.927,146.134)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(143.073,146.134)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(164.218,146.134)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(185.363,181.204)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(206.508,181.204)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t18074a0bbc63468787e64c92c0f3f48b"><clipPath id="tadb34932422f423598980736d2e86d5f"><rect x="265.0" y="40.0" width="185.0" height="170.0"></rect></clipPath><g clip-path="url(#tadb34932422f423598980736d2e86d5f)"></g><g class="toyplot-coordinates-Axis" id="t2c6bf20060d64036bd4f3a94b5434be4" transform="translate(275.0,200.0)rotate(-90.0)translate(0,-10.0)"><line x1="18.795886483288786" y1="0" x2="141.54234859142645" y2="0" style=""></line><g><line x1="18.795886483288786" y1="0" x2="18.795886483288786" y2="5" style=""></line><line x1="74.58973289607863" y1="0" x2="74.58973289607863" y2="5" style=""></line><line x1="130.38357930886846" y1="0" x2="130.38357930886846" y2="5" style=""></line></g><g><g transform="translate(18.795886483288786,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(74.58973289607863,-6)"><text x="-6.95" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2.5</text></g><g transform="translate(130.38357930886846,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">5</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="tce495e6d072e4ef08594f376f23c0f38"><clipPath id="t0a9e4465d7424f518ad7a300a92dc191"><rect x="265.0" y="40.0" width="185.0" height="170.0"></rect></clipPath><g clip-path="url(#t0a9e4465d7424f518ad7a300a92dc191)"><g class="toytree-mark-Toytree" id="t16027e80c0854e19a614b41897c646e2"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 294.1 91.9 L 283.5 158.9" id="8,0" style=""></path><path d="M 294.1 91.9 L 304.6 181.2" id="8,1" style=""></path><path d="M 309.9 69.6 L 325.8 91.9" id="9,2" style=""></path><path d="M 357.5 91.9 L 346.9 114.3" id="10,3" style=""></path><path d="M 357.5 91.9 L 368.1 114.3" id="10,4" style=""></path><path d="M 405.1 91.9 L 389.2 114.3" id="12,5" style=""></path><path d="M 420.9 114.3 L 410.4 136.6" id="11,6" style=""></path><path d="M 420.9 114.3 L 431.5 136.6" id="11,7" style=""></path><path d="M 309.9 69.6 L 294.1 91.9" id="9,8" style=""></path><path d="M 345.6 58.5 L 309.9 69.6" id="14,9" style=""></path><path d="M 381.3 69.6 L 357.5 91.9" id="13,10" style=""></path><path d="M 405.1 91.9 L 420.9 114.3" id="12,11" style=""></path><path d="M 381.3 69.6 L 405.1 91.9" id="13,12" style=""></path><path d="M 345.6 58.5 L 381.3 69.6" id="14,13" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.0"><g id="Node-0" transform="translate(283.492,158.887)"><circle r="7.5"></circle></g><g id="Node-1" transform="translate(304.637,181.204)"><circle r="7.5"></circle></g><g id="Node-2" transform="translate(325.782,91.934)"><circle r="7.5"></circle></g><g id="Node-3" transform="translate(346.927,114.251)"><circle r="7.5"></circle></g><g id="Node-4" transform="translate(368.073,114.251)"><circle r="7.5"></circle></g><g id="Node-5" transform="translate(389.218,114.251)"><circle r="7.5"></circle></g><g id="Node-6" transform="translate(410.363,136.569)"><circle r="7.5"></circle></g><g id="Node-7" transform="translate(431.508,136.569)"><circle r="7.5"></circle></g><g id="Node-8" transform="translate(294.064,91.934)"><circle r="7.5"></circle></g><g id="Node-9" transform="translate(309.923,69.6164)"><circle r="7.5"></circle></g><g id="Node-10" transform="translate(357.5,91.934)"><circle r="7.5"></circle></g><g id="Node-11" transform="translate(420.936,114.251)"><circle r="7.5"></circle></g><g id="Node-12" transform="translate(405.077,91.934)"><circle r="7.5"></circle></g><g id="Node-13" transform="translate(381.288,69.6164)"><circle r="7.5"></circle></g><g id="Node-14" transform="translate(345.606,58.4577)"><circle r="7.5"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(283.492,158.887)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(304.637,181.204)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(325.782,91.934)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(346.927,114.251)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(368.073,114.251)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(389.218,114.251)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(410.363,136.569)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(431.508,136.569)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(294.064,91.934)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(309.923,69.6164)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(357.5,91.934)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(420.936,114.251)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(405.077,91.934)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(381.288,69.6164)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(345.606,58.4577)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(283.492,158.887)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(304.637,181.204)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(325.782,91.934)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(346.927,114.251)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(368.073,114.251)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(389.218,114.251)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(410.363,136.569)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(431.508,136.569)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t81d17bac0a6f4a0ba28e50fa0c84ba6f"><clipPath id="t8f605498d1754ef7a4228e551c1a93f2"><rect x="490.0" y="40.0" width="185.0" height="170.0"></rect></clipPath><g clip-path="url(#t8f605498d1754ef7a4228e551c1a93f2)"></g></g><g class="toyplot-coordinates-Cartesian" id="t2fb1e18d3c4744c78d922c1d035797aa"><clipPath id="teef9b524421348c19bab394c2165ea0c"><rect x="715.0" y="40.0" width="185.0" height="170.0"></rect></clipPath><g clip-path="url(#teef9b524421348c19bab394c2165ea0c)"></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t9dc60106bff04b5fbe02a01f7bcc9d4b";
modules["toyplot/canvas"] = (function(canvas_id)
    {
        return document.querySelector("#" + canvas_id);
    })(modules["toyplot/canvas/id"]);
modules["toyplot.coordinates.Axis"] = (
        function(canvas)
        {
            function sign(x)
            {
                return x < 0 ? -1 : x > 0 ? 1 : 0;
            }

            function mix(a, b, amount)
            {
                return ((1.0 - amount) * a) + (amount * b);
            }

            function log(x, base)
            {
                return Math.log(Math.abs(x)) / Math.log(base);
            }

            function in_range(a, x, b)
            {
                var left = Math.min(a, b);
                var right = Math.max(a, b);
                return left <= x && x <= right;
            }

            function inside(range, projection)
            {
                for(var i = 0; i != projection.length; ++i)
                {
                    var segment = projection[i];
                    if(in_range(segment.range.min, range, segment.range.max))
                        return true;
                }
                return false;
            }

            function to_domain(range, projection)
            {
                for(var i = 0; i != projection.length; ++i)
                {
                    var segment = projection[i];
                    if(in_range(segment.range.bounds.min, range, segment.range.bounds.max))
                    {
                        if(segment.scale == "linear")
                        {
                            var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                            return mix(segment.domain.min, segment.domain.max, amount)
                        }
                        else if(segment.scale[0] == "log")
                        {
                            var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                            var base = segment.scale[1];
                            return sign(segment.domain.min) * Math.pow(base, mix(log(segment.domain.min, base), log(segment.domain.max, base), amount));
                        }
                    }
                }
            }

            var axes = {};

            function display_coordinates(e)
            {
                var current = canvas.createSVGPoint();
                current.x = e.clientX;
                current.y = e.clientY;

                for(var axis_id in axes)
                {
                    var axis = document.querySelector("#" + axis_id);
                    var coordinates = axis.querySelector(".toyplot-coordinates-Axis-coordinates");
                    if(coordinates)
                    {
                        var projection = axes[axis_id];
                        var local = current.matrixTransform(axis.getScreenCTM().inverse());
                        if(inside(local.x, projection))
                        {
                            var domain = to_domain(local.x, projection);
                            coordinates.style.visibility = "visible";
                            coordinates.setAttribute("transform", "translate(" + local.x + ")");
                            var text = coordinates.querySelector("text");
                            text.textContent = domain.toFixed(2);
                        }
                        else
                        {
                            coordinates.style.visibility= "hidden";
                        }
                    }
                }
            }

            canvas.addEventListener("click", display_coordinates);

            var module = {};
            module.show_coordinates = function(axis_id, projection)
            {
                axes[axis_id] = projection;
            }

            return module;
        })(modules["toyplot/canvas"]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"t63346b076ef2430d862a36da23a64090",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 3.7411619807333336, "min": -0.535947037182666}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 150.0, "min": 0.0}, "scale": "linear"}]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"t2c6bf20060d64036bd4f3a94b5434be4",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 5.878968826866666, "min": -0.8422024870013323}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 150.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


## Building trees from Nodes
There are several ways of constructing trees in `toytree` from scratch. This most simple is to use one of the random tree generation functions from the `toytree.rtree` subpackage. A second method is to write a Newick string and parse it using the `toytree.tree` function. A third is to build or modify a tree using one or more functions from `toytree.mod` such as `.add_child_node`. And finally, the fourth method is to link together `Node` objects manually. The last is the most low-level method, which requires eventually calling `ToyTree._update()` to cache the traversal order and store idx values. Each of these is demonstrated below.

1. Generate random or fixed trees. See the `rtree` documentation section for more details. This includes options to generate trees under a variety of algorithms and of different sizes.


```python
# generate a 6-tip balanced tree with crown height of 1M units
toytree.rtree.baltree(6, treeheight=1e6).draw(scale_bar=True);
```


<div class="toyplot" id="tdb11a8a5711742e4a05da5408946043b" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t2b9e2f7fa5b84a5ba4616d8fd96906e5"><g class="toyplot-coordinates-Cartesian" id="t516f11fc79d14a6a9fd95d980a6ad45d"><clipPath id="t93ad6efba92646709308b2e6ac7facd4"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t93ad6efba92646709308b2e6ac7facd4)"></g><g class="toyplot-coordinates-Axis" id="t9d9af2bdd40f494292662aa627123af8" transform="translate(50.0,225.0)translate(0,15.0)"><line x1="0.9845545534227831" y1="0" x2="174.72845372274378" y2="0" style=""></line><g><line x1="0.9845545534227831" y1="0" x2="0.9845545534227831" y2="-5" style=""></line><line x1="87.85650413808328" y1="0" x2="87.85650413808328" y2="-5" style=""></line><line x1="174.72845372274378" y1="0" x2="174.72845372274378" y2="-5" style=""></line></g><g><g transform="translate(0.9845545534227831,6)"><text x="-19.459999999999997" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1000000</text></g><g transform="translate(87.85650413808328,6)"><text x="-16.68" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">500000</text></g><g transform="translate(174.72845372274378,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="ta6ab8123129d49909b51b23744c8cb63"><clipPath id="td09014f8052c4ce68b6e4fa7077a70e9"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#td09014f8052c4ce68b6e4fa7077a70e9)"><g class="toytree-mark-Toytree" id="t06cf07a338834eb594257633152bdcb3"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 108.9 193.7 L 108.9 217.8 L 224.7 217.8" id="7,0" style=""></path><path d="M 166.8 169.6 L 166.8 185.7 L 224.7 185.7" id="6,1" style=""></path><path d="M 166.8 169.6 L 166.8 153.6 L 224.7 153.6" id="6,2" style=""></path><path d="M 108.9 97.3 L 108.9 121.4 L 224.7 121.4" id="9,3" style=""></path><path d="M 166.8 73.2 L 166.8 89.3 L 224.7 89.3" id="8,4" style=""></path><path d="M 166.8 73.2 L 166.8 57.2 L 224.7 57.2" id="8,5" style=""></path><path d="M 108.9 193.7 L 108.9 169.6 L 166.8 169.6" id="7,6" style=""></path><path d="M 51.0 145.5 L 51.0 193.7 L 108.9 193.7" id="10,7" style=""></path><path d="M 108.9 97.3 L 108.9 73.2 L 166.8 73.2" id="9,8" style=""></path><path d="M 51.0 145.5 L 51.0 97.3 L 108.9 97.3" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.728,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.728,185.707)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.728,153.569)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.728,121.431)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.728,89.2931)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.728,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t2b9e2f7fa5b84a5ba4616d8fd96906e5";
modules["toyplot/canvas"] = (function(canvas_id)
    {
        return document.querySelector("#" + canvas_id);
    })(modules["toyplot/canvas/id"]);
modules["toyplot.coordinates.Axis"] = (
        function(canvas)
        {
            function sign(x)
            {
                return x < 0 ? -1 : x > 0 ? 1 : 0;
            }

            function mix(a, b, amount)
            {
                return ((1.0 - amount) * a) + (amount * b);
            }

            function log(x, base)
            {
                return Math.log(Math.abs(x)) / Math.log(base);
            }

            function in_range(a, x, b)
            {
                var left = Math.min(a, b);
                var right = Math.max(a, b);
                return left <= x && x <= right;
            }

            function inside(range, projection)
            {
                for(var i = 0; i != projection.length; ++i)
                {
                    var segment = projection[i];
                    if(in_range(segment.range.min, range, segment.range.max))
                        return true;
                }
                return false;
            }

            function to_domain(range, projection)
            {
                for(var i = 0; i != projection.length; ++i)
                {
                    var segment = projection[i];
                    if(in_range(segment.range.bounds.min, range, segment.range.bounds.max))
                    {
                        if(segment.scale == "linear")
                        {
                            var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                            return mix(segment.domain.min, segment.domain.max, amount)
                        }
                        else if(segment.scale[0] == "log")
                        {
                            var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                            var base = segment.scale[1];
                            return sign(segment.domain.min) * Math.pow(base, mix(log(segment.domain.min, base), log(segment.domain.max, base), amount));
                        }
                    }
                }
            }

            var axes = {};

            function display_coordinates(e)
            {
                var current = canvas.createSVGPoint();
                current.x = e.clientX;
                current.y = e.clientY;

                for(var axis_id in axes)
                {
                    var axis = document.querySelector("#" + axis_id);
                    var coordinates = axis.querySelector(".toyplot-coordinates-Axis-coordinates");
                    if(coordinates)
                    {
                        var projection = axes[axis_id];
                        var local = current.matrixTransform(axis.getScreenCTM().inverse());
                        if(inside(local.x, projection))
                        {
                            var domain = to_domain(local.x, projection);
                            coordinates.style.visibility = "visible";
                            coordinates.setAttribute("transform", "translate(" + local.x + ")");
                            var text = coordinates.querySelector("text");
                            text.textContent = domain.toFixed(2);
                        }
                        else
                        {
                            coordinates.style.visibility= "hidden";
                        }
                    }
                }
            }

            canvas.addEventListener("click", display_coordinates);

            var module = {};
            module.show_coordinates = function(axis_id, projection)
            {
                axes[axis_id] = projection;
            }

            return module;
        })(modules["toyplot/canvas"]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"t9d9af2bdd40f494292662aa627123af8",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 145452.85560000016, "min": -1005666.7}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


2. Parse a Newick string to generate a tree from scratch with desired characteristics.


```python
# generate a ToyTree with this specific data
toytree.tree("(((a:3,b:2):1),(c:3,d:2):5);").draw(scale_bar=True);
```


<div class="toyplot" id="tac80aa2f76c148f29ad2d2e07f7989b9" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t5afa2ae0e965415cb09e80aedc51fdd2"><g class="toyplot-coordinates-Cartesian" id="t2f42da9a2f584e2f888465cc1af7db2b"><clipPath id="t1ba15b1f561d4a3fa7cee2c91c57b6f9"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t1ba15b1f561d4a3fa7cee2c91c57b6f9)"></g><g class="toyplot-coordinates-Axis" id="t867f3ee2b19247d2ac5d32c630f5cc12" transform="translate(50.0,225.0)translate(0,15.0)"><line x1="0.9892166473576229" y1="0" x2="179.2264504054897" y2="0" style=""></line><g><line x1="12.129043757240876" y1="0" x2="12.129043757240876" y2="-5" style=""></line><line x1="67.82817930665715" y1="0" x2="67.82817930665715" y2="-5" style=""></line><line x1="123.52731485607342" y1="0" x2="123.52731485607342" y2="-5" style=""></line><line x1="179.2264504054897" y1="0" x2="179.2264504054897" y2="-5" style=""></line></g><g><g transform="translate(12.129043757240876,6)"><text x="-6.95" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">7.5</text></g><g transform="translate(67.82817930665715,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">5</text></g><g transform="translate(123.52731485607342,6)"><text x="-6.95" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2.5</text></g><g transform="translate(179.2264504054897,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="t5b5fdd0903ec4486b965de879c8fa938"><clipPath id="tba6edc2a51bb4572931aa58f0975dedb"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tba6edc2a51bb4572931aa58f0975dedb)"><g class="toytree-mark-Toytree" id="tdf167db8acba492e9919fc82c8a1e92c"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 95.5 191.1 L 95.5 217.8 L 162.4 217.8" id="4,0" style=""></path><path d="M 95.5 191.1 L 95.5 164.3 L 140.1 164.3" id="4,1" style=""></path><path d="M 162.4 83.9 L 162.4 110.7 L 229.2 110.7" id="6,2" style=""></path><path d="M 162.4 83.9 L 162.4 57.2 L 206.9 57.2" id="6,3" style=""></path><path d="M 73.3 191.1 L 73.3 191.1 L 95.5 191.1" id="5,4" style=""></path><path d="M 51.0 137.5 L 51.0 191.1 L 73.3 191.1" id="7,5" style=""></path><path d="M 51.0 137.5 L 51.0 83.9 L 162.4 83.9" id="7,6" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(162.387,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(140.108,164.282)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(229.226,110.718)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(206.947,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t5afa2ae0e965415cb09e80aedc51fdd2";
modules["toyplot/canvas"] = (function(canvas_id)
    {
        return document.querySelector("#" + canvas_id);
    })(modules["toyplot/canvas/id"]);
modules["toyplot.coordinates.Axis"] = (
        function(canvas)
        {
            function sign(x)
            {
                return x < 0 ? -1 : x > 0 ? 1 : 0;
            }

            function mix(a, b, amount)
            {
                return ((1.0 - amount) * a) + (amount * b);
            }

            function log(x, base)
            {
                return Math.log(Math.abs(x)) / Math.log(base);
            }

            function in_range(a, x, b)
            {
                var left = Math.min(a, b);
                var right = Math.max(a, b);
                return left <= x && x <= right;
            }

            function inside(range, projection)
            {
                for(var i = 0; i != projection.length; ++i)
                {
                    var segment = projection[i];
                    if(in_range(segment.range.min, range, segment.range.max))
                        return true;
                }
                return false;
            }

            function to_domain(range, projection)
            {
                for(var i = 0; i != projection.length; ++i)
                {
                    var segment = projection[i];
                    if(in_range(segment.range.bounds.min, range, segment.range.bounds.max))
                    {
                        if(segment.scale == "linear")
                        {
                            var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                            return mix(segment.domain.min, segment.domain.max, amount)
                        }
                        else if(segment.scale[0] == "log")
                        {
                            var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                            var base = segment.scale[1];
                            return sign(segment.domain.min) * Math.pow(base, mix(log(segment.domain.min, base), log(segment.domain.max, base), amount));
                        }
                    }
                }
            }

            var axes = {};

            function display_coordinates(e)
            {
                var current = canvas.createSVGPoint();
                current.x = e.clientX;
                current.y = e.clientY;

                for(var axis_id in axes)
                {
                    var axis = document.querySelector("#" + axis_id);
                    var coordinates = axis.querySelector(".toyplot-coordinates-Axis-coordinates");
                    if(coordinates)
                    {
                        var projection = axes[axis_id];
                        var local = current.matrixTransform(axis.getScreenCTM().inverse());
                        if(inside(local.x, projection))
                        {
                            var domain = to_domain(local.x, projection);
                            coordinates.style.visibility = "visible";
                            coordinates.setAttribute("transform", "translate(" + local.x + ")");
                            var text = coordinates.querySelector("text");
                            text.textContent = domain.toFixed(2);
                        }
                        else
                        {
                            coordinates.style.visibility= "hidden";
                        }
                    }
                }
            }

            canvas.addEventListener("click", display_coordinates);

            var module = {};
            module.show_coordinates = function(axis_id, projection)
            {
                axes[axis_id] = projection;
            }

            return module;
        })(modules["toyplot/canvas"]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"t867f3ee2b19247d2ac5d32c630f5cc12",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.9324000000000005, "min": -8.0444}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


3. Modify a tree using one or more `toytree.mod` functions:


```python
# get a 4-tip balanced tree
tree4 = toytree.rtree.baltree(4)

# add a new sister (internal and tip node) to tip node 'r1'
modtree4 = toytree.mod.add_internal_node_and_child(tree4, 'r1', name="child", parent_name="parent")

# draw to highlight new parent and child nodes
modtree4.draw('r', node_mask=modtree4.get_node_mask(5), node_colors="lightgrey");
```


<div class="toyplot" id="t18842a2e910e4c82becc6f305ced04ba" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="te4d25ed7837e4b52a77e1be263ce0cc0"><g class="toyplot-coordinates-Cartesian" id="te942fa19ff044da49d11df13be85233a"><clipPath id="te0c92aaf35f2443397686638bf7970b3"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#te0c92aaf35f2443397686638bf7970b3)"></g></g><g class="toyplot-coordinates-Cartesian" id="t55943929370c41bbaec411ec6345b255"><clipPath id="te05fffa7865348e8b1cce2b0da748c9f"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#te05fffa7865348e8b1cce2b0da748c9f)"><g class="toytree-mark-Toytree" id="t5f6bf5a6299e4b98a7ba96c6190ad031"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 136.9 186.3 L 136.9 215.5 L 206.5 215.5" id="6,0" style=""></path><path d="M 171.7 157.0 L 171.7 176.5 L 206.5 176.5" id="5,1" style=""></path><path d="M 171.7 157.0 L 171.7 137.5 L 206.5 137.5" id="5,2" style=""></path><path d="M 136.9 79.0 L 136.9 98.5 L 206.5 98.5" id="7,3" style=""></path><path d="M 136.9 79.0 L 136.9 59.5 L 206.5 59.5" id="7,4" style=""></path><path d="M 136.9 186.3 L 136.9 157.0 L 171.7 157.0" id="6,5" style=""></path><path d="M 67.4 132.6 L 67.4 186.3 L 136.9 186.3" id="8,6" style=""></path><path d="M 67.4 132.6 L 67.4 79.0 L 136.9 79.0" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(171.712,157)"><rect x="-16.0" y="-8.0" width="32.0" height="16.0"></rect></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(171.712,157)"><text x="-12.7575" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">parent</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:14px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(206.484,215.501)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(206.484,176.501)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(206.484,137.5)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">child</text></g><g class="toytree-TipLabel" transform="translate(206.484,98.4994)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(206.484,59.4988)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


4. Create connections among `Node` objects and create a `ToyTree` from them. You can do this by setting `._up`, `._children`, and `._dist` values on a set of nodes.


```python
# create several tips nodes
nodeA = toytree.Node("A", dist=1)
nodeB = toytree.Node("B", dist=1)
nodeC = toytree.Node("C", dist=1)

# create several internal Nodes
nodeAB = toytree.Node("AB", dist=1)
nodeABC = toytree.Node("ABC", dist=1)

# connect the nodes
nodeA._up = nodeAB
nodeB._up = nodeAB
nodeC._up = nodeABC
nodeAB._up = nodeABC
nodeAB._children = (nodeA, nodeB)
nodeABC._children = (nodeAB, nodeC)

# draw the tree (the tree traversal data is cached at this step)
toytree.tree(nodeABC).draw(ts='r', node_colors="lightgrey");
```


<div class="toyplot" id="t65ba65f15c12456aa975754dc867c4a8" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t33098e2cde5245f9bca5d2122feb2855"><g class="toyplot-coordinates-Cartesian" id="t6c44f04d1d9b46219dccc9299a44717f"><clipPath id="t20c973f0ec194d6d91e42c979086806a"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t20c973f0ec194d6d91e42c979086806a)"></g></g><g class="toyplot-coordinates-Cartesian" id="t5114ed50909c4f59a714c5f8e472c8d3"><clipPath id="tce7e24b6bdaa48e884483c5d6d6d5745"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tce7e24b6bdaa48e884483c5d6d6d5745)"><g class="toytree-mark-Toytree" id="t002a027718f64b2eaba90a50ca534172"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 146.6 176.5 L 146.6 215.5 L 225.8 215.5" id="3,0" style=""></path><path d="M 146.6 176.5 L 146.6 137.5 L 225.8 137.5" id="3,1" style=""></path><path d="M 67.4 118.0 L 67.4 59.5 L 146.6 59.5" id="4,2" style=""></path><path d="M 67.4 118.0 L 67.4 176.5 L 146.6 176.5" id="4,3" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-3" transform="translate(146.606,176.505)"><rect x="-16.0" y="-8.0" width="32.0" height="16.0"></rect></g><g id="Node-4" transform="translate(67.3731,117.997)"><rect x="-16.0" y="-8.0" width="32.0" height="16.0"></rect></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(146.606,176.505)"><text x="-6.003" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">AB</text></g><g class="toytree-NodeLabel" transform="translate(67.3731,117.997)"><text x="-9.252" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">ABC</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:14px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(225.839,215.511)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">A</text></g><g class="toytree-TipLabel" transform="translate(225.839,137.5)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">B</text></g><g class="toytree-TipLabel" transform="translate(146.606,59.4892)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">C</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


Similarly, this process could be applied to an existing tree to add or remove connections by changing the same types of node attributes. The important thing is that the `ToyTree._update()` function is called at the end to update values across connected nodes. The `Node` object includes convenience functions `_add_child` and `_remove_child` which change the `._up` and `._children` attributes together, but setting them manually may be more clear. 


```python
# get a 4-tip balanced tree
tree4 = toytree.rtree.baltree(4, treeheight=2)

# add a new sister (internal and tip node) to tip node 0
tree4[0]._add_child(toytree.Node("child0", dist=1))
tree4[0]._add_child(toytree.Node("child1", dist=1))

# connects node data across three
tree4._update()

# draw to highlight new nodes. Note former node (idx=0, name='r0') is now node idx=5
tree4.draw('r', node_mask=tree4.get_node_mask(5), node_colors="lightgrey");
```


<div class="toyplot" id="t8a75a85e91ef437e9ebfb0b781daaa95" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="te3ff9d0c578c49f5a7446f9fddf6e94f"><g class="toyplot-coordinates-Cartesian" id="t18b6e32964e443ed9a1fd8b10a9a632d"><clipPath id="tbb2fd8cd18c5465cb3975cb5f29a9a0f"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tbb2fd8cd18c5465cb3975cb5f29a9a0f)"></g></g><g class="toyplot-coordinates-Cartesian" id="t1ea79dcc4c024088aaab184aeedd443d"><clipPath id="t8a9f90d734014f46bf390f79ae657ab0"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t8a9f90d734014f46bf390f79ae657ab0)"><g class="toytree-mark-Toytree" id="t10a4d09283c7479dbc7efe80e380f08a"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 155.1 196.0 L 155.1 215.5 L 198.9 215.5" id="5,0" style=""></path><path d="M 155.1 196.0 L 155.1 176.5 L 198.9 176.5" id="5,1" style=""></path><path d="M 111.2 166.8 L 111.2 137.5 L 155.1 137.5" id="6,2" style=""></path><path d="M 111.2 79.0 L 111.2 98.5 L 155.1 98.5" id="7,3" style=""></path><path d="M 111.2 79.0 L 111.2 59.5 L 155.1 59.5" id="7,4" style=""></path><path d="M 111.2 166.8 L 111.2 196.0 L 155.1 196.0" id="6,5" style=""></path><path d="M 67.3 122.9 L 67.3 166.8 L 111.2 166.8" id="8,6" style=""></path><path d="M 67.3 122.9 L 67.3 79.0 L 111.2 79.0" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(155.055,196.001)"><rect x="-16.0" y="-8.0" width="32.0" height="16.0"></rect></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(155.055,196.001)"><text x="-4.0005" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:14px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(198.915,215.501)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">child0</text></g><g class="toytree-TipLabel" transform="translate(198.915,176.501)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">child1</text></g><g class="toytree-TipLabel" transform="translate(155.055,137.5)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(155.055,98.4994)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(155.055,59.4988)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>

