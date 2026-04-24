<div class="nb-md-page-hook" aria-hidden="true"></div>

# Traversal order/methods
Traversal is the process of visiting each `Node` in a tree exactly once in a defined order. Different traversal orders are useful for efficient calculations, searches, and tree algorithms.

This page introduces the main traversal strategies in `toytree`, then focuses on the cached `idxorder` traversal used by `ToyTree`. Understanding `idxorder` explains node `idx` labels and why selecting nodes by index is fast and intuitive, as also used in the [Node Query/Selection section](core-query).

<div class="admonition tip">
  <p class="admonition-title">Take Home</p>
  <p>
      The main idea on this page is <code>idxorder</code>. It is the cached traversal behind node <code>idx</code> labels, so once you understand it, selecting tips, internal nodes, and slices of nodes becomes much easier.
  </p>
</div>


```python
import toytree
```


```python
# an example tree
tree = toytree.rtree.unittree(8, seed=123)
```

## Why traverse?
A `ToyTree` contains connected `Node` objects arranged hierarchically. Even if you store those nodes in a list or dictionary, you still need some linear order to visit them, and different tasks benefit from different orders.

**A traversal algorithm is a consistent set of rules for visiting each `Node` exactly once.**

Some traversals are useful when parent values depend on children, others when children depend on parents, and others when you want to stop early after finding a target. Many statistics, model-fitting methods, and search algorithms on trees depend on one of these patterns.

`ToyTree.traverse()` is a generator that yields nodes one at a time in the requested order.


```python
# traverse() is a generator function
tree.traverse(strategy="levelorder")
```




    <generator object ToyTree.traverse at 0x7e55cefd18a0>




```python
# unpacking the generator returns every Node visited once
list(tree.traverse("levelorder"))
```




    [<Node(idx=14)>,
     <Node(idx=9)>,
     <Node(idx=13)>,
     <Node(idx=0, name='r0')>,
     <Node(idx=8)>,
     <Node(idx=10)>,
     <Node(idx=12)>,
     <Node(idx=1, name='r1')>,
     <Node(idx=2, name='r2')>,
     <Node(idx=3, name='r3')>,
     <Node(idx=4, name='r4')>,
     <Node(idx=5, name='r5')>,
     <Node(idx=11)>,
     <Node(idx=6, name='r6')>,
     <Node(idx=7, name='r7')>]



## Traversal strategies
Below are the main traversal strategies in `toytree`: `levelorder`, `preorder`, `postorder`, and `idxorder`. The helper function below draws a tree and labels each node by its position in the chosen traversal.


```python
def get_traversal_drawing(tree, strategy):
    """Return a tree drawing canvas showing a traversal strategy"""
    
    # create map of {node: int} in levelorder traversal
    order = {j: i for (i, j) in enumerate(tree.traverse(strategy))}
    
    # set as data to the tree
    tree.set_node_data(feature=strategy, data=order, inplace=True)
    
    # draw the tree showing the 'levelorder' feature on nodes
    c, a, m = tree.draw(layout='d', node_sizes=18, node_labels=strategy, node_mask=False);
    
    # add label
    a.label.text = f'"{strategy}" traversal'
    return c
```

### levelorder (root to tips)
A levelorder traversal, also called breadth-first search (BFS), starts at the root and visits nodes one depth level at a time before moving deeper. Here depth means number of nodes, not branch length. In `toytree`, nodes within a level are visited left to right. Its main advantage is that parents are always visited before children.


```python
get_traversal_drawing(tree, "levelorder")
```




<div class="toyplot" id="t9ccd1a9b030641cf818947d4e79878f5" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t529ffa2f87874d61a97c1cdd1546c933"><g class="toyplot-coordinates-Cartesian" id="t4bf66b6f7dec4d399048d0e5d974e982"><clipPath id="tfa9c3d1f2488453ea1db86a60332e3c5"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#tfa9c3d1f2488453ea1db86a60332e3c5)"><g class="toytree-mark-Toytree" id="tb723292f2741439099fa936f8b724196"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 79.7 83.9 L 60.5 83.9 L 60.5 224.5" id="9,0" style=""></path><path d="M 98.9 130.7 L 86.1 130.7 L 86.1 224.5" id="8,1" style=""></path><path d="M 98.9 130.7 L 111.6 130.7 L 111.6 224.5" id="8,2" style=""></path><path d="M 150.0 130.7 L 137.2 130.7 L 137.2 224.5" id="10,3" style=""></path><path d="M 150.0 130.7 L 162.8 130.7 L 162.8 224.5" id="10,4" style=""></path><path d="M 207.5 130.7 L 188.4 130.7 L 188.4 224.5" id="12,5" style=""></path><path d="M 226.7 177.6 L 213.9 177.6 L 213.9 224.5" id="11,6" style=""></path><path d="M 226.7 177.6 L 239.5 177.6 L 239.5 224.5" id="11,7" style=""></path><path d="M 79.7 83.9 L 98.9 83.9 L 98.9 130.7" id="9,8" style=""></path><path d="M 129.2 60.4 L 79.7 60.4 L 79.7 83.9" id="14,9" style=""></path><path d="M 178.8 83.9 L 150.0 83.9 L 150.0 130.7" id="13,10" style=""></path><path d="M 207.5 130.7 L 226.7 130.7 L 226.7 177.6" id="12,11" style=""></path><path d="M 178.8 83.9 L 207.5 83.9 L 207.5 130.7" id="13,12" style=""></path><path d="M 129.2 60.4 L 178.8 60.4 L 178.8 83.9" id="14,13" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(60.4891,224.456)"><circle r="9.0"></circle></g><g id="Node-1" transform="translate(86.0637,224.456)"><circle r="9.0"></circle></g><g id="Node-2" transform="translate(111.638,224.456)"><circle r="9.0"></circle></g><g id="Node-3" transform="translate(137.213,224.456)"><circle r="9.0"></circle></g><g id="Node-4" transform="translate(162.787,224.456)"><circle r="9.0"></circle></g><g id="Node-5" transform="translate(188.362,224.456)"><circle r="9.0"></circle></g><g id="Node-6" transform="translate(213.936,224.456)"><circle r="9.0"></circle></g><g id="Node-7" transform="translate(239.511,224.456)"><circle r="9.0"></circle></g><g id="Node-8" transform="translate(98.8509,130.738)"><circle r="9.0"></circle></g><g id="Node-9" transform="translate(79.67,83.8787)"><circle r="9.0"></circle></g><g id="Node-10" transform="translate(150,130.738)"><circle r="9.0"></circle></g><g id="Node-11" transform="translate(226.724,177.597)"><circle r="9.0"></circle></g><g id="Node-12" transform="translate(207.543,130.738)"><circle r="9.0"></circle></g><g id="Node-13" transform="translate(178.771,83.8787)"><circle r="9.0"></circle></g><g id="Node-14" transform="translate(129.221,60.4491)"><circle r="9.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(60.4891,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(86.0637,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(111.638,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(137.213,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(162.787,224.456)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(188.362,224.456)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(213.936,224.456)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(239.511,224.456)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g><g class="toytree-NodeLabel" transform="translate(98.8509,130.738)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(79.67,83.8787)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(150,130.738)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(226.724,177.597)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(207.543,130.738)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(178.771,83.8787)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(129.221,60.4491)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(60.4891,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(86.0637,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(111.638,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(137.213,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(162.787,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(188.362,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(213.936,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(239.511,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g></g></g></g><g transform="translate(150.0,42.0)"><text x="-71.22500000000001" y="-4.823" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:14.0px;font-weight:bold;stroke:none;vertical-align:baseline;white-space:pre">"levelorder" traversal</text></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



### preorder (root to tips)
A preorder traversal is a [depth-first search](https://en.wikipedia.org/wiki/Depth-first_search). It starts at the root and follows each subtree as far as possible before backtracking. In `toytree`, the default order is NLR: node, left subtree, right subtree. Like levelorder, it visits each parent before its children, but it explores deep branches sooner, which matters if you may stop once a target node is found.


```python
get_traversal_drawing(tree, "preorder")
```




<div class="toyplot" id="ta40152f46762448ab01be1b8b858f74c" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tf7c7daa9f73044faa642236cb2c89acd"><g class="toyplot-coordinates-Cartesian" id="t83d1024b25bb4b26ab9730747983e83a"><clipPath id="t68118a8f0e5043e8a52cda8c8569edf2"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t68118a8f0e5043e8a52cda8c8569edf2)"><g class="toytree-mark-Toytree" id="t255a50246a184c1aa3c3ffc9b916c2d4"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 79.7 83.9 L 60.5 83.9 L 60.5 224.5" id="9,0" style=""></path><path d="M 98.9 130.7 L 86.1 130.7 L 86.1 224.5" id="8,1" style=""></path><path d="M 98.9 130.7 L 111.6 130.7 L 111.6 224.5" id="8,2" style=""></path><path d="M 150.0 130.7 L 137.2 130.7 L 137.2 224.5" id="10,3" style=""></path><path d="M 150.0 130.7 L 162.8 130.7 L 162.8 224.5" id="10,4" style=""></path><path d="M 207.5 130.7 L 188.4 130.7 L 188.4 224.5" id="12,5" style=""></path><path d="M 226.7 177.6 L 213.9 177.6 L 213.9 224.5" id="11,6" style=""></path><path d="M 226.7 177.6 L 239.5 177.6 L 239.5 224.5" id="11,7" style=""></path><path d="M 79.7 83.9 L 98.9 83.9 L 98.9 130.7" id="9,8" style=""></path><path d="M 129.2 60.4 L 79.7 60.4 L 79.7 83.9" id="14,9" style=""></path><path d="M 178.8 83.9 L 150.0 83.9 L 150.0 130.7" id="13,10" style=""></path><path d="M 207.5 130.7 L 226.7 130.7 L 226.7 177.6" id="12,11" style=""></path><path d="M 178.8 83.9 L 207.5 83.9 L 207.5 130.7" id="13,12" style=""></path><path d="M 129.2 60.4 L 178.8 60.4 L 178.8 83.9" id="14,13" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(60.4891,224.456)"><circle r="9.0"></circle></g><g id="Node-1" transform="translate(86.0637,224.456)"><circle r="9.0"></circle></g><g id="Node-2" transform="translate(111.638,224.456)"><circle r="9.0"></circle></g><g id="Node-3" transform="translate(137.213,224.456)"><circle r="9.0"></circle></g><g id="Node-4" transform="translate(162.787,224.456)"><circle r="9.0"></circle></g><g id="Node-5" transform="translate(188.362,224.456)"><circle r="9.0"></circle></g><g id="Node-6" transform="translate(213.936,224.456)"><circle r="9.0"></circle></g><g id="Node-7" transform="translate(239.511,224.456)"><circle r="9.0"></circle></g><g id="Node-8" transform="translate(98.8509,130.738)"><circle r="9.0"></circle></g><g id="Node-9" transform="translate(79.67,83.8787)"><circle r="9.0"></circle></g><g id="Node-10" transform="translate(150,130.738)"><circle r="9.0"></circle></g><g id="Node-11" transform="translate(226.724,177.597)"><circle r="9.0"></circle></g><g id="Node-12" transform="translate(207.543,130.738)"><circle r="9.0"></circle></g><g id="Node-13" transform="translate(178.771,83.8787)"><circle r="9.0"></circle></g><g id="Node-14" transform="translate(129.221,60.4491)"><circle r="9.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(60.4891,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(86.0637,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(111.638,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(137.213,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(162.787,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(188.362,224.456)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(213.936,224.456)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(239.511,224.456)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g><g class="toytree-NodeLabel" transform="translate(98.8509,130.738)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(79.67,83.8787)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(150,130.738)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(226.724,177.597)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(207.543,130.738)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(178.771,83.8787)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(129.221,60.4491)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(60.4891,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(86.0637,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(111.638,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(137.213,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(162.787,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(188.362,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(213.936,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(239.511,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g></g></g></g><g transform="translate(150.0,42.0)"><text x="-66.54899999999999" y="-4.823" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:14.0px;font-weight:bold;stroke:none;vertical-align:baseline;white-space:pre">"preorder" traversal</text></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



### postorder (tips to root)
A postorder traversal is also depth-first, but it yields nodes after visiting their descendants. In `toytree`, the default order is LRN: left subtree, right subtree, node. This means children are always visited before their parent, which is useful when parent values depend on child values, such as likelihood, parsimony, ancestral-state, or node-height calculations.


```python
get_traversal_drawing(tree, "postorder")
```




<div class="toyplot" id="tc677de3b3b3249f39a6a82cdeb629d8b" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t4661823e00ec45629c0fb9ff83f0aeb7"><g class="toyplot-coordinates-Cartesian" id="t2ccab0d2ce10429ea89d858da730c15c"><clipPath id="t521116f2a2ec4b5bbcfdbb7fdeda3a51"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t521116f2a2ec4b5bbcfdbb7fdeda3a51)"><g class="toytree-mark-Toytree" id="t6abff5c8661d4ba98d81ac61aee208a8"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 79.7 83.9 L 60.5 83.9 L 60.5 224.5" id="9,0" style=""></path><path d="M 98.9 130.7 L 86.1 130.7 L 86.1 224.5" id="8,1" style=""></path><path d="M 98.9 130.7 L 111.6 130.7 L 111.6 224.5" id="8,2" style=""></path><path d="M 150.0 130.7 L 137.2 130.7 L 137.2 224.5" id="10,3" style=""></path><path d="M 150.0 130.7 L 162.8 130.7 L 162.8 224.5" id="10,4" style=""></path><path d="M 207.5 130.7 L 188.4 130.7 L 188.4 224.5" id="12,5" style=""></path><path d="M 226.7 177.6 L 213.9 177.6 L 213.9 224.5" id="11,6" style=""></path><path d="M 226.7 177.6 L 239.5 177.6 L 239.5 224.5" id="11,7" style=""></path><path d="M 79.7 83.9 L 98.9 83.9 L 98.9 130.7" id="9,8" style=""></path><path d="M 129.2 60.4 L 79.7 60.4 L 79.7 83.9" id="14,9" style=""></path><path d="M 178.8 83.9 L 150.0 83.9 L 150.0 130.7" id="13,10" style=""></path><path d="M 207.5 130.7 L 226.7 130.7 L 226.7 177.6" id="12,11" style=""></path><path d="M 178.8 83.9 L 207.5 83.9 L 207.5 130.7" id="13,12" style=""></path><path d="M 129.2 60.4 L 178.8 60.4 L 178.8 83.9" id="14,13" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(60.4891,224.456)"><circle r="9.0"></circle></g><g id="Node-1" transform="translate(86.0637,224.456)"><circle r="9.0"></circle></g><g id="Node-2" transform="translate(111.638,224.456)"><circle r="9.0"></circle></g><g id="Node-3" transform="translate(137.213,224.456)"><circle r="9.0"></circle></g><g id="Node-4" transform="translate(162.787,224.456)"><circle r="9.0"></circle></g><g id="Node-5" transform="translate(188.362,224.456)"><circle r="9.0"></circle></g><g id="Node-6" transform="translate(213.936,224.456)"><circle r="9.0"></circle></g><g id="Node-7" transform="translate(239.511,224.456)"><circle r="9.0"></circle></g><g id="Node-8" transform="translate(98.8509,130.738)"><circle r="9.0"></circle></g><g id="Node-9" transform="translate(79.67,83.8787)"><circle r="9.0"></circle></g><g id="Node-10" transform="translate(150,130.738)"><circle r="9.0"></circle></g><g id="Node-11" transform="translate(226.724,177.597)"><circle r="9.0"></circle></g><g id="Node-12" transform="translate(207.543,130.738)"><circle r="9.0"></circle></g><g id="Node-13" transform="translate(178.771,83.8787)"><circle r="9.0"></circle></g><g id="Node-14" transform="translate(129.221,60.4491)"><circle r="9.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(60.4891,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(86.0637,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(111.638,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(137.213,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(162.787,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(188.362,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(213.936,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(239.511,224.456)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(98.8509,130.738)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(79.67,83.8787)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(150,130.738)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(226.724,177.597)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(207.543,130.738)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(178.771,83.8787)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(129.221,60.4491)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(60.4891,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(86.0637,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(111.638,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(137.213,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(162.787,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(188.362,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(213.936,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(239.511,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g></g></g></g><g transform="translate(150.0,42.0)"><text x="-70.434" y="-4.823" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:14.0px;font-weight:bold;stroke:none;vertical-align:baseline;white-space:pre">"postorder" traversal</text></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



### idxorder (tips to root)
`idxorder` is a custom traversal used by `toytree`. It visits all tip nodes from left to right first, then visits internal nodes in postorder. You can think of it as tips-first-then-postorder. Like postorder, internal nodes are visited only after their children.

This is especially convenient for phylogenetic trees because tips are often the named samples users care about most. It also means the first `ntips` positions are always the tips, which is why tip selection by index is so simple in `ToyTree`.


```python
get_traversal_drawing(tree, "idxorder")
```




<div class="toyplot" id="t4bff410f2b024064b86ddaa70cbc5e98" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t94b2464e42ce49f28ce0ce2025968408"><g class="toyplot-coordinates-Cartesian" id="t2d20f0e419a04eac8350174e211c08ba"><clipPath id="t19b448fa9ffc409cb6f962dc71f70624"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t19b448fa9ffc409cb6f962dc71f70624)"><g class="toytree-mark-Toytree" id="te5fae68a01ca4d53bd2839e76b8882ae"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 79.7 83.9 L 60.5 83.9 L 60.5 224.5" id="9,0" style=""></path><path d="M 98.9 130.7 L 86.1 130.7 L 86.1 224.5" id="8,1" style=""></path><path d="M 98.9 130.7 L 111.6 130.7 L 111.6 224.5" id="8,2" style=""></path><path d="M 150.0 130.7 L 137.2 130.7 L 137.2 224.5" id="10,3" style=""></path><path d="M 150.0 130.7 L 162.8 130.7 L 162.8 224.5" id="10,4" style=""></path><path d="M 207.5 130.7 L 188.4 130.7 L 188.4 224.5" id="12,5" style=""></path><path d="M 226.7 177.6 L 213.9 177.6 L 213.9 224.5" id="11,6" style=""></path><path d="M 226.7 177.6 L 239.5 177.6 L 239.5 224.5" id="11,7" style=""></path><path d="M 79.7 83.9 L 98.9 83.9 L 98.9 130.7" id="9,8" style=""></path><path d="M 129.2 60.4 L 79.7 60.4 L 79.7 83.9" id="14,9" style=""></path><path d="M 178.8 83.9 L 150.0 83.9 L 150.0 130.7" id="13,10" style=""></path><path d="M 207.5 130.7 L 226.7 130.7 L 226.7 177.6" id="12,11" style=""></path><path d="M 178.8 83.9 L 207.5 83.9 L 207.5 130.7" id="13,12" style=""></path><path d="M 129.2 60.4 L 178.8 60.4 L 178.8 83.9" id="14,13" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(60.4891,224.456)"><circle r="9.0"></circle></g><g id="Node-1" transform="translate(86.0637,224.456)"><circle r="9.0"></circle></g><g id="Node-2" transform="translate(111.638,224.456)"><circle r="9.0"></circle></g><g id="Node-3" transform="translate(137.213,224.456)"><circle r="9.0"></circle></g><g id="Node-4" transform="translate(162.787,224.456)"><circle r="9.0"></circle></g><g id="Node-5" transform="translate(188.362,224.456)"><circle r="9.0"></circle></g><g id="Node-6" transform="translate(213.936,224.456)"><circle r="9.0"></circle></g><g id="Node-7" transform="translate(239.511,224.456)"><circle r="9.0"></circle></g><g id="Node-8" transform="translate(98.8509,130.738)"><circle r="9.0"></circle></g><g id="Node-9" transform="translate(79.67,83.8787)"><circle r="9.0"></circle></g><g id="Node-10" transform="translate(150,130.738)"><circle r="9.0"></circle></g><g id="Node-11" transform="translate(226.724,177.597)"><circle r="9.0"></circle></g><g id="Node-12" transform="translate(207.543,130.738)"><circle r="9.0"></circle></g><g id="Node-13" transform="translate(178.771,83.8787)"><circle r="9.0"></circle></g><g id="Node-14" transform="translate(129.221,60.4491)"><circle r="9.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(60.4891,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(86.0637,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(111.638,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(137.213,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(162.787,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(188.362,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(213.936,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(239.511,224.456)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(98.8509,130.738)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(79.67,83.8787)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(150,130.738)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(226.724,177.597)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(207.543,130.738)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(178.771,83.8787)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(129.221,60.4491)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(60.4891,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(86.0637,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(111.638,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(137.213,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(162.787,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(188.362,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(213.936,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(239.511,224.456)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g></g></g></g><g transform="translate(150.0,42.0)"><text x="-65.772" y="-4.823" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:14.0px;font-weight:bold;stroke:none;vertical-align:baseline;white-space:pre">"idxorder" traversal</text></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



## Using a cached traversal
Traversal is useful, but repeated traversals are not always the fastest way to access nodes.

If a tree has not changed, it is often better to cache a traversal-derived view of the structure and reuse it. Looking up nodes from cached data is much faster than walking the whole tree again.

This is a key property of the `ToyTree` class. It stores a cached `idxorder` traversal and updates that cache when the tree structure is modified. **That cache is the source of node `idx` labels.** Because of this, tips, internal nodes, and full-node slices can be accessed quickly without running a fresh traversal each time.


```python
# node idx 0 represents the first node in an idxorder traversal
tree[3]
```




    <Node(idx=3, name='r3')>




```python
# node idx 10 represents the 11th node in an idxorder traversal
tree[10]
```




    <Node(idx=10)>



### Speed Comparison
Here is a simple example: access the names of every leaf node in a large tree. The first approach reads tips directly from the cached `idxorder`; the second performs a new traversal. Both are fast, but the cached approach is about 10X faster. The difference is modest here, but it matters in code that repeats the operation many times.


```python
bigtree = toytree.rtree.rtree(ntips=300)
```


```python
%%timeit
# select tip nodes from the idxorder cache
[i.name for i in bigtree[:bigtree.ntips]]
```

    15.7 μs ± 63.8 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)



```python
%%timeit
# perform a new traversal to visit each node
names = []
for node in bigtree.traverse(strategy="idxorder"):
    if node.is_leaf():
        names.append(node.name)
```

    125 μs ± 576 ns per loop (mean ± std. dev. of 7 runs, 10,000 loops each)


## Common traversals
Below are common snippets for iterating over all nodes or common subsets:

### iterate over all nodes


```python
# trees are iterable and return nodes in idxorder
for node in tree:
    pass

# same as above
for node in tree[:]:
    pass

# nodes can be indexed using their idxorder idx labels
for idx in range(tree.nnodes):
    node = tree[idx]

# to iterate idxorder in reverse (root to tips)
for node in tree[::-1]:
    pass
```

### iterate over leaf nodes
The patterns below iterate over leaf nodes efficiently.


```python
# for tip nodes
for idx in range(tree.ntips):
    pass

# for tip nodes
for node in tree[:tree.ntips]:
    pass

# for tip nodes
for node in tree:
    if not node.is_leaf():
        pass

# tips in reverse order of how they will be plotted
for node in tree[:tree.ntips][::-1]:
    pass

# tips in reverse order of how they will be plotted
for node in tree[:tree.ntips:-1]:
    pass
```

### iterate over internal nodes
The patterns below iterate over internal nodes efficiently.


```python
# for internal nodes
for idx in range(tree.ntips, tree.nnodes):
    pass

# for internal nodes
for node in tree[tree.ntips: tree.nnodes]:
    pass

# for internal nodes
for node in tree[:]:
    if not node.is_leaf():
        pass

# for reverse order: root to last internal
for idx in range(tree.nnodes - 1, tree.ntips - 1, -1):
    node = tree[idx]

# for reverse order: root to last internal
for node in tree[tree.nnodes: tree.ntips:-1]:
    pass
```
