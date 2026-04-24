<div class="nb-md-page-hook" aria-hidden="true"></div>

# ToyTree
The `toytree.ToyTree` object is the main class in the `toytree` package. It contains a number of useful functions for interacting with the underlying `Node` structure (e.g., rooting, dropping tips), for storing and retrieving data (e.g., trait or support values), performing comparative or statistical analyses (e.g., tree distance metrics), and creating visualizations.

Note: this section of the documentation is relatively short since many of the other sections of the documentation are about properties or methods of `ToyTree` objects.


```python
import toytree
```

## Generating ToyTrees
A `ToyTree` is loaded in one of three ways: (1) by parsing tree data using `toytree.tree()` ([see tree/io](/parse_trees)); (2) by generating a fixed or random tree with `toytree.rtree` ([see rtree](/rtree/)); or (3) by wrapping one or more `toytree.Node` objects in a `ToyTree` ([see Building-trees-from-nodes](/node/#building-trees-from-nodes)). Follow the links for more details on each. We will use the random birth 8-tip unit tree generated below for this tutorial. 


```python
# generate a random uniform tree
tree = toytree.rtree.unittree(8, seed=123)
```

## Trees are indexable and iterable
`Node` objects can be selected from `ToyTrees` in a variety of ways. See [Node Query/selection](/query/) for details.


```python
tree[0]
```




    <Node(idx=0, name='r0')>




```python
tree[1:3]
```




    [<Node(idx=1, name='r1')>, <Node(idx=2, name='r2')>]




```python
for node in tree:
    print(node)
```

    <Node(idx=0, name='r0')>
    <Node(idx=1, name='r1')>
    <Node(idx=2, name='r2')>
    <Node(idx=3, name='r3')>
    <Node(idx=4, name='r4')>
    <Node(idx=5, name='r5')>
    <Node(idx=6, name='r6')>
    <Node(idx=7, name='r7')>
    <Node(idx=8)>
    <Node(idx=9)>
    <Node(idx=10)>
    <Node(idx=11)>
    <Node(idx=12)>
    <Node(idx=13)>
    <Node(idx=14)>


## Cached Traversal
A `ToyTree` stores a cached traversal of all Nodes in the tree in idxorder (see [Traversal order/methods](/traversal/)). Briefly, a traversal involves visiting each node in a tree exactly once. This is used to assign a unique integer label to every node. The idx labels `0-ntips` are the tips, and from `ntips-nnodes-1` are the internal nodes. The `nnodes-1` idx label corresponds to the root.


```python
# show node idx labels of cached idxorder traversal
tree.draw('p');
```


<div class="toyplot" id="t5517a832e29c431b8194d13472527c6b" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tf9b0b7bc6ea94922b8afbb24d739c498"><g class="toyplot-coordinates-Cartesian" id="t7d467f65a8f04ef8a7fd0a501943d230"><clipPath id="t9384667ea26645c1ab635849850646f7"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t9384667ea26645c1ab635849850646f7)"></g><g class="toyplot-coordinates-Axis" id="t8ca80237981249ecb0ae32928ed70a4b" transform="translate(50.0,250.0)rotate(-90.0)translate(0,-15.0)"><line x1="25.56178908041747" y1="0" x2="191.53517191898283" y2="0" style=""></line><g><line x1="25.56178908041747" y1="0" x2="25.56178908041747" y2="5" style=""></line><line x1="108.54848049970013" y1="0" x2="108.54848049970013" y2="5" style=""></line><line x1="191.53517191898283" y1="0" x2="191.53517191898283" y2="5" style=""></line></g><g><g transform="translate(25.56178908041747,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(108.54848049970013,-6)"><text x="-6.95" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.5</text></g><g transform="translate(191.53517191898283,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="t2bde8ff731e74a66a64860a694d6d33e"><clipPath id="t0815025074f940f6859a294ee81bbe21"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t0815025074f940f6859a294ee81bbe21)"><g class="toytree-mark-Toytree" id="te33a2fb7f4c74478b2e4a35d880065b2"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 78.1 82.2 L 58.5 224.4" id="9,0" style=""></path><path d="M 97.7 129.6 L 84.6 224.4" id="8,1" style=""></path><path d="M 97.7 129.6 L 110.8 224.4" id="8,2" style=""></path><path d="M 150.0 129.6 L 136.9 224.4" id="10,3" style=""></path><path d="M 150.0 129.6 L 163.1 224.4" id="10,4" style=""></path><path d="M 208.8 129.6 L 189.2 224.4" id="12,5" style=""></path><path d="M 228.4 177.0 L 215.4 224.4" id="11,6" style=""></path><path d="M 228.4 177.0 L 241.5 224.4" id="11,7" style=""></path><path d="M 78.1 82.2 L 97.7 129.6" id="9,8" style=""></path><path d="M 128.8 58.5 L 78.1 82.2" id="14,9" style=""></path><path d="M 179.4 82.2 L 150.0 129.6" id="13,10" style=""></path><path d="M 208.8 129.6 L 228.4 177.0" id="12,11" style=""></path><path d="M 179.4 82.2 L 208.8 129.6" id="13,12" style=""></path><path d="M 128.8 58.5 L 179.4 82.2" id="14,13" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.0"><g id="Node-0" transform="translate(58.4952,224.438)"><circle r="7.5"></circle></g><g id="Node-1" transform="translate(84.6394,224.438)"><circle r="7.5"></circle></g><g id="Node-2" transform="translate(110.784,224.438)"><circle r="7.5"></circle></g><g id="Node-3" transform="translate(136.928,224.438)"><circle r="7.5"></circle></g><g id="Node-4" transform="translate(163.072,224.438)"><circle r="7.5"></circle></g><g id="Node-5" transform="translate(189.216,224.438)"><circle r="7.5"></circle></g><g id="Node-6" transform="translate(215.361,224.438)"><circle r="7.5"></circle></g><g id="Node-7" transform="translate(241.505,224.438)"><circle r="7.5"></circle></g><g id="Node-8" transform="translate(97.7116,129.596)"><circle r="7.5"></circle></g><g id="Node-9" transform="translate(78.1034,82.1753)"><circle r="7.5"></circle></g><g id="Node-10" transform="translate(150,129.596)"><circle r="7.5"></circle></g><g id="Node-11" transform="translate(228.433,177.017)"><circle r="7.5"></circle></g><g id="Node-12" transform="translate(208.824,129.596)"><circle r="7.5"></circle></g><g id="Node-13" transform="translate(179.412,82.1753)"><circle r="7.5"></circle></g><g id="Node-14" transform="translate(128.758,58.4648)"><circle r="7.5"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(58.4952,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(84.6394,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(110.784,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(136.928,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(163.072,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(189.216,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(215.361,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(241.505,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(97.7116,129.596)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(78.1034,82.1753)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(150,129.596)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(228.433,177.017)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(208.824,129.596)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(179.412,82.1753)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(128.758,58.4648)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(58.4952,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(84.6394,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(110.784,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(136.928,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(163.072,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(189.216,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(215.361,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(241.505,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "tf9b0b7bc6ea94922b8afbb24d739c498";
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
        })(modules["toyplot.coordinates.Axis"],"t8ca80237981249ecb0ae32928ed70a4b",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 1.051001117988, "min": -0.15401137606070392}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


## The tree root (treenode)
A `ToyTree` acts as a wrapper around a collection of connected `Node` objects. Of these nodes, one has a special designation as the **root** of the tree, whether or not the tree structure is rooted or unrooted. This node merely represents the top of the hierarchical structure of stored nodes. This node can be accessed like any other node by indexing or by name, and can also be accessed as the `.treenode` attribute of a `ToyTree`.


```python
# the root node
tree.treenode
```




    <Node(idx=14)>




```python
# also the root node
tree[-1]
```




    <Node(idx=14)>




```python
# the root has no parent Node (.up returns None)
tree.treenode.up
```

A rooted bifurcating tree has `nnodes = (ntips * 2) - 1`, whereas an unrooted bifurcating tree has `nnodes = (ntips * 2) - 2`. In other words converting from rooted to unrooted, or vice-versa, involves adding or removing a node from the tree. In an unrooted tree the root node is always a polytomy. (See the [Tree rooting](/rooting/) tutorial for further details.) This can be seen more clearly by plotting trees in an unrooted layout. The splits in the tree are the same regardless of the root node's placement. In the rooted tree (left) it is on a branch, and has two connected edges (a degree of 2). On the unrooted tree (right) it is on a node of the tree and connected to three edges (of degree 3). 


```python
toytree.mtree([tree, tree.unroot()]).draw(
    layout='unr',
    node_sizes=16, 
    node_labels="idx",
    node_mask=(0,0,1),
);
```


<div class="toyplot" id="t78814be18b074791b5d60c2e79d384cb" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="1400.0px" height="350.0px" viewBox="0 0 1400.0 350.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t12b019b9f16f46b8a55f27f9feccaebe"><g class="toyplot-coordinates-Cartesian" id="t3fafb0ab58534ec7ac4858f3d1eec60c"><clipPath id="t9f536e82757e48029004f19d749703a4"><rect x="20.0" y="40.0" width="330.0" height="270.0"></rect></clipPath><g clip-path="url(#t9f536e82757e48029004f19d749703a4)"></g></g><g class="toyplot-coordinates-Cartesian" id="t19f8155e168b45fbb113097c5926ea7b"><clipPath id="tc0ccf17faac64c61b8a5acece435d299"><rect x="20.0" y="40.0" width="330.0" height="270.0"></rect></clipPath><g clip-path="url(#tc0ccf17faac64c61b8a5acece435d299)"><g class="toytree-mark-Toytree" id="t54cdf2fe9b384451bf3edaa58e7ee622"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 203.1 166.0 L 320.5 203.6" id="9,0" style=""></path><path d="M 220.9 135.5 L 294.7 103.0" id="8,1" style=""></path><path d="M 220.9 135.5 L 209.0 68.8" id="8,2" style=""></path><path d="M 132.5 168.0 L 86.3 111.6" id="10,3" style=""></path><path d="M 132.5 168.0 L 49.0 177.5" id="10,4" style=""></path><path d="M 166.4 219.0 L 98.0 258.3" id="12,5" style=""></path><path d="M 185.9 248.9 L 173.4 281.0" id="11,6" style=""></path><path d="M 185.9 248.9 L 217.1 271.5" id="11,7" style=""></path><path d="M 203.1 166.0 L 220.9 135.5" id="9,8" style=""></path><path d="M 185.5 175.3 L 203.1 166.0" id="14,9" style=""></path><path d="M 168.6 185.3 L 132.5 168.0" id="13,10" style=""></path><path d="M 166.4 219.0 L 185.9 248.9" id="12,11" style=""></path><path d="M 168.6 185.3 L 166.4 219.0" id="13,12" style=""></path><path d="M 185.5 175.3 L 168.6 185.3" id="14,13" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-14" transform="translate(185.512,175.322)"><circle r="8.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(185.512,175.322)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(320.482,203.563)rotate(14.6618)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(294.741,103.038)rotate(-40.6866)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(209.015,68.7732)rotate(-87.216)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(86.2566,111.59)rotate(48.2465)"><text x="-18.89" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(49.0455,177.546)rotate(4.65544)"><text x="-18.89" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(97.9697,258.275)rotate(127.738)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(173.372,281.041)rotate(84.8951)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(217.105,271.523)rotate(52.3597)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="tfb1e597794d947bfb66d58a2f2c2d394"><clipPath id="ta977f680da5d429585e534262a16e953"><rect x="370.0" y="40.0" width="330.0" height="270.0"></rect></clipPath><g clip-path="url(#ta977f680da5d429585e534262a16e953)"></g></g><g class="toyplot-coordinates-Cartesian" id="td5139a8d66094f7297a9447740a0f19a"><clipPath id="tfdec8010f37244d6be5137ebf5843546"><rect x="370.0" y="40.0" width="330.0" height="270.0"></rect></clipPath><g clip-path="url(#tfdec8010f37244d6be5137ebf5843546)"><g class="toytree-mark-Toytree" id="tfb102ed375744d8ba6628393f7cf8e32"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 554.6 166.7 L 670.6 208.0" id="13,0" style=""></path><path d="M 573.9 136.5 L 649.5 106.0" id="8,1" style=""></path><path d="M 573.9 136.5 L 565.1 68.9" id="8,2" style=""></path><path d="M 483.3 166.2 L 439.8 107.9" id="9,3" style=""></path><path d="M 483.3 166.2 L 399.2 173.2" id="9,4" style=""></path><path d="M 514.9 218.5 L 444.3 255.9" id="11,5" style=""></path><path d="M 532.9 249.2 L 518.8 281.2" id="10,6" style=""></path><path d="M 532.9 249.2 L 563.1 273.1" id="10,7" style=""></path><path d="M 554.6 166.7 L 573.9 136.5" id="13,8" style=""></path><path d="M 518.8 184.7 L 483.3 166.2" id="12,9" style=""></path><path d="M 514.9 218.5 L 532.9 249.2" id="11,10" style=""></path><path d="M 518.8 184.7 L 514.9 218.5" id="12,11" style=""></path><path d="M 554.6 166.7 L 518.8 184.7" id="13,12" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-13" transform="translate(554.606,166.704)"><circle r="8.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(554.606,166.704)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(670.576,208.023)rotate(23.9336)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(649.479,106.032)rotate(-38.5425)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(565.104,68.9462)rotate(-85.0729)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(439.842,107.946)rotate(50.473)"><text x="-18.89" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(399.2,173.173)rotate(6.86409)"><text x="-18.89" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(444.288,255.929)rotate(130.019)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(518.754,281.223)rotate(87.1689)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(563.07,273.066)rotate(54.6544)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t94d81a865f764dff99c955152712cd24"><clipPath id="te0bbe7b67ae944e4bd5b54b72a3aa539"><rect x="720.0" y="40.0" width="330.0" height="270.0"></rect></clipPath><g clip-path="url(#te0bbe7b67ae944e4bd5b54b72a3aa539)"></g></g><g class="toyplot-coordinates-Cartesian" id="tfe9e6ae0baee40c883de3e23551e37d4"><clipPath id="t438676ac0ad8462898a6b8cdbbc1aea6"><rect x="1070.0" y="40.0" width="330.0" height="270.0"></rect></clipPath><g clip-path="url(#t438676ac0ad8462898a6b8cdbbc1aea6)"></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Attributes
`ToyTree` attributes store information about the size of the tree, and are automatically updated by the `mod` functions when a tree structure is modified. The `features` and `edge_features` describe data stored to nodes of a tree and are further described in [Data/Features](/data/). 


```python
tree.ntips
```




    8




```python
tree.nnodes
```




    15




```python
tree.treenode
```




    <Node(idx=14)>




```python
tree.features
```




    ('idx', 'name', 'height', 'dist', 'support')




```python
tree.edge_features
```




    {'dist', 'support'}



## Methods
The `ToyTree` object has a number of methods available directly from object, as well as many additional methods organized into subpackages that are also accessible from a tree. 


```python
# does the tree not contain any polytomies
tree.is_bifurcating()
```




    True




```python
# is the tree rooted
tree.is_rooted()
```




    True




```python
# query if set of tip nodes is monophyletic
tree.is_monophyletic("r3", "r2", "r1"), tree.is_monophyletic("r3", "r2", "r1", "r0")
```




    (False, False)




```python
# return a copy of the tree
tree.copy()
```




    <toytree.ToyTree at 0x76c60bef2ae0>




```python
# return a tree drawing as a (Canvas, Cartesian, Mark)
tree.draw(ts='c')
```




    (<toyplot.canvas.Canvas at 0x76c60c08aba0>,
     <toyplot.coordinates.Cartesian at 0x76c60ceccfb0>,
     <toytree.drawing.src.mark_toytree.ToyTreeMark at 0x76c60c09e4e0>)




<div class="toyplot" id="t0919f7f1e9e94fbeab39a09a6ca8b609" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="te485189109784b17a6513581de3e7175"><g class="toyplot-coordinates-Cartesian" id="td60e592309ee4afdb09745a1f73f1635"><clipPath id="t90f043c1447242cdb28878ce20797a4b"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t90f043c1447242cdb28878ce20797a4b)"></g><g class="toyplot-coordinates-Axis" id="tfe2bf8cc3fd04a58bd92f19d628f795f" transform="translate(50.0,250.0)rotate(-90.0)translate(0,-15.0)"><line x1="22.293203075840932" y1="0" x2="195.0826709290981" y2="0" style=""></line><g><line x1="22.293203075840932" y1="0" x2="22.293203075840932" y2="5" style=""></line><line x1="108.68793700246951" y1="0" x2="108.68793700246951" y2="5" style=""></line><line x1="195.0826709290981" y1="0" x2="195.0826709290981" y2="5" style=""></line></g><g><g transform="translate(22.293203075840932,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(108.68793700246951,-6)"><text x="-6.95" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.5</text></g><g transform="translate(195.0826709290981,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="t85d60fc611f2434a948839674490f3a6"><clipPath id="t87bb4b9472b148deb076642eb5ac6f16"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t87bb4b9472b148deb076642eb5ac6f16)"><g class="toytree-mark-Toytree" id="t9dd1de40cd6142f7b6a7d0b8aaa29ea4"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 77.1 79.6 L 57.2 227.7" id="9,0" style=""></path><path d="M 97.0 129.0 L 83.7 227.7" id="8,1" style=""></path><path d="M 97.0 129.0 L 110.2 227.7" id="8,2" style=""></path><path d="M 150.0 129.0 L 136.7 227.7" id="10,3" style=""></path><path d="M 150.0 129.0 L 163.3 227.7" id="10,4" style=""></path><path d="M 209.7 129.0 L 189.8 227.7" id="12,5" style=""></path><path d="M 229.6 178.3 L 216.3 227.7" id="11,6" style=""></path><path d="M 229.6 178.3 L 242.8 227.7" id="11,7" style=""></path><path d="M 77.1 79.6 L 97.0 129.0" id="9,8" style=""></path><path d="M 128.4 54.9 L 77.1 79.6" id="14,9" style=""></path><path d="M 179.8 79.6 L 150.0 129.0" id="13,10" style=""></path><path d="M 209.7 129.0 L 229.6 178.3" id="12,11" style=""></path><path d="M 179.8 79.6 L 209.7 129.0" id="13,12" style=""></path><path d="M 128.4 54.9 L 179.8 79.6" id="14,13" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(57.1653,227.707)"><circle r="3.5"></circle></g><g id="Node-1" transform="translate(83.6895,227.707)"><circle r="3.5"></circle></g><g id="Node-2" transform="translate(110.214,227.707)"><circle r="3.5"></circle></g><g id="Node-3" transform="translate(136.738,227.707)"><circle r="3.5"></circle></g><g id="Node-4" transform="translate(163.262,227.707)"><circle r="3.5"></circle></g><g id="Node-5" transform="translate(189.786,227.707)"><circle r="3.5"></circle></g><g id="Node-6" transform="translate(216.31,227.707)"><circle r="3.5"></circle></g><g id="Node-7" transform="translate(242.835,227.707)"><circle r="3.5"></circle></g><g id="Node-8" transform="translate(96.9516,128.97)"><circle r="3.5"></circle></g><g id="Node-9" transform="translate(77.0585,79.6015)"><circle r="3.5"></circle></g><g id="Node-10" transform="translate(150,128.97)"><circle r="3.5"></circle></g><g id="Node-11" transform="translate(229.573,178.338)"><circle r="3.5"></circle></g><g id="Node-12" transform="translate(209.679,128.97)"><circle r="3.5"></circle></g><g id="Node-13" transform="translate(179.84,79.6015)"><circle r="3.5"></circle></g><g id="Node-14" transform="translate(128.449,54.9173)"><circle r="3.5"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(57.1653,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(83.6895,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(110.214,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(136.738,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(163.262,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(189.786,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(216.31,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(242.835,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "te485189109784b17a6513581de3e7175";
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
        })(modules["toyplot.coordinates.Axis"],"tfe2bf8cc3fd04a58bd92f19d628f795f",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 1.0284585, "min": -0.12901945559999994}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>



```python
# return all ancestors of query nodes
tree.get_ancestors("r4", "r5")
```




    {<Node(idx=4, name='r4')>,
     <Node(idx=5, name='r5')>,
     <Node(idx=10)>,
     <Node(idx=12)>,
     <Node(idx=13)>,
     <Node(idx=14)>}




```python
# get dict mapping one feature to another
tree.get_feature_dict('idx', 'name')
```




    {0: 'r0',
     1: 'r1',
     2: 'r2',
     3: 'r3',
     4: 'r4',
     5: 'r5',
     6: 'r6',
     7: 'r7',
     8: '',
     9: '',
     10: '',
     11: '',
     12: '',
     13: '',
     14: ''}




```python
# get edges as a table
tree.get_edges(feature="idx", df=True)
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
      <td>9</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>8</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>8</td>
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




```python
# get mrca of a queried set of nodes
tree.get_mrca_node("r4", "r5")
```




    <Node(idx=13)>




```python
# get a DataFrame or Series of data from all nodes w/ formatting options
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
      <td>r0</td>
      <td>0.000000</td>
      <td>0.857143</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>r1</td>
      <td>0.000000</td>
      <td>0.571429</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>r2</td>
      <td>0.000000</td>
      <td>0.571429</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>r3</td>
      <td>0.000000</td>
      <td>0.571429</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>r4</td>
      <td>0.000000</td>
      <td>0.571429</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td>r5</td>
      <td>0.000000</td>
      <td>0.571429</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td>r6</td>
      <td>0.000000</td>
      <td>0.285714</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td>r7</td>
      <td>0.000000</td>
      <td>0.285714</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>8</th>
      <td>8</td>
      <td></td>
      <td>0.571429</td>
      <td>0.285714</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>9</th>
      <td>9</td>
      <td></td>
      <td>0.857143</td>
      <td>0.142857</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>10</th>
      <td>10</td>
      <td></td>
      <td>0.571429</td>
      <td>0.285714</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>11</th>
      <td>11</td>
      <td></td>
      <td>0.285714</td>
      <td>0.285714</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>12</th>
      <td>12</td>
      <td></td>
      <td>0.571429</td>
      <td>0.285714</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>13</th>
      <td>13</td>
      <td></td>
      <td>0.857143</td>
      <td>0.142857</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>14</th>
      <td>14</td>
      <td></td>
      <td>1.000000</td>
      <td>0.000000</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>




```python
# get mask that is True for selected nodes and False for others
tree.get_node_mask(0, 1, 2)
```




    array([ True,  True,  True, False, False, False, False, False, False,
           False, False, False, False, False, False])




```python
# get nodes matching a query
tree.get_nodes("~r[0-3]$")
```




    [<Node(idx=2, name='r2')>,
     <Node(idx=3, name='r3')>,
     <Node(idx=0, name='r0')>,
     <Node(idx=1, name='r1')>]




```python
# like get_node_data but only for tip (leaf) nodes
tree.get_tip_data()
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
      <td>r0</td>
      <td>0.0</td>
      <td>0.857143</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>r1</td>
      <td>0.0</td>
      <td>0.571429</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>r2</td>
      <td>0.0</td>
      <td>0.571429</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>r3</td>
      <td>0.0</td>
      <td>0.571429</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>r4</td>
      <td>0.0</td>
      <td>0.571429</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td>r5</td>
      <td>0.0</td>
      <td>0.571429</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td>r6</td>
      <td>0.0</td>
      <td>0.285714</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td>r7</td>
      <td>0.0</td>
      <td>0.285714</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>




```python
# return the names for nodes idx 0-ntips in order
tree.get_tip_labels()
```




    ['r0', 'r1', 'r2', 'r3', 'r4', 'r5', 'r6', 'r7']




```python
# return a hash str unique to this topology
tree.get_topology_id()
```




    '4a3e7d6e3eba2d098b675b30e5d9f8f6'



## Modifying trees
See the `mod` documentation section for details on tree modification methods. Many methods are available for modifying the topology, branch lengths, or other data on trees. These include common options like `.ladderize`, `.prune`, `.root`, `.collapse_nodes`, `edges_set_node_heights`, and many more. These functions are written to be very efficient, requiring the minimum number of tree traversals or modifications, and ensure the returned tree has proper node idx, height, and other node features updated.


```python
# extract a subtree connecting tips r0, r1, r2, r3 and draw it
toytree.mod.extract_subtree(tree, "~r[0-3]").draw();
```


<div class="toyplot" id="t396cf2afeb6b42bab132d6afe19632c3" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="ta29395159bf74e2494ffd5be93d923da"><g class="toyplot-coordinates-Cartesian" id="t687f06607a554b38a00767d18d7173ce"><clipPath id="tfd7a9bd72b9646d6b6d48984e42d95d4"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tfd7a9bd72b9646d6b6d48984e42d95d4)"></g></g><g class="toyplot-coordinates-Cartesian" id="t22c2cf7e74e64253942a9926767624d9"><clipPath id="t5e0f4d809f284ca792cea2efa3d43fbf"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t5e0f4d809f284ca792cea2efa3d43fbf)"><g class="toytree-mark-Toytree" id="t69ac606e101f408180120ebb2cd9e8ed"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 75.8 200.6 L 75.8 217.8 L 224.7 217.8" id="9,0" style=""></path><path d="M 125.4 183.4 L 125.4 194.9 L 224.7 194.9" id="8,1" style=""></path><path d="M 125.4 183.4 L 125.4 171.9 L 224.7 171.9" id="8,2" style=""></path><path d="M 125.4 137.5 L 125.4 149.0 L 224.7 149.0" id="10,3" style=""></path><path d="M 125.4 137.5 L 125.4 126.0 L 224.7 126.0" id="10,4" style=""></path><path d="M 125.4 85.8 L 125.4 103.1 L 224.7 103.1" id="12,5" style=""></path><path d="M 175.1 68.6 L 175.1 80.1 L 224.7 80.1" id="11,6" style=""></path><path d="M 175.1 68.6 L 175.1 57.2 L 224.7 57.2" id="11,7" style=""></path><path d="M 75.8 200.6 L 75.8 183.4 L 125.4 183.4" id="9,8" style=""></path><path d="M 51.0 156.2 L 51.0 200.6 L 75.8 200.6" id="14,9" style=""></path><path d="M 75.8 111.7 L 75.8 137.5 L 125.4 137.5" id="13,10" style=""></path><path d="M 125.4 85.8 L 125.4 68.6 L 175.1 68.6" id="12,11" style=""></path><path d="M 75.8 111.7 L 75.8 85.8 L 125.4 85.8" id="13,12" style=""></path><path d="M 51.0 156.2 L 51.0 111.7 L 75.8 111.7" id="14,13" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.728,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.728,194.889)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.728,171.933)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.728,148.978)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.728,126.022)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.728,103.067)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.728,80.1109)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.728,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Chaining methods
Many methods of a `ToyTree` return a copy of the tree which are intended to make it easy to chain together multiple function calls to accomplish complex operations. For example, below the tree is re-rooted, scaled to a new crown height, ladderized, adds an internal node name, and then calls draw with many styling options including showing the new node name.


```python
# example of complex chained function calls
canvas, axes, mark = (tree
    .root("r6")
    .mod.edges_scale_to_root_height(10)
    .ladderize(True)
    .set_node_data("name", {-1: 'root'})
    .draw(
        node_labels="name", node_mask=(0, 0, 1), node_sizes=18,
        node_markers="r2x1", node_colors="lightgrey",
        scale_bar=True, tip_labels_align=True,
    )
);
```


<div class="toyplot" id="t84d68629d7f545649e4576829db7c818" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="293.2px" viewBox="0 0 300.0 293.2" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t8f859fe5ff874386bf0158cbfca13c49"><g class="toyplot-coordinates-Cartesian" id="t753336326d5a465380c7d740fdc084db"><clipPath id="te55dede9233842ebb4d2339c99c0859c"><rect x="35.0" y="35.0" width="230.0" height="223.2"></rect></clipPath><g clip-path="url(#te55dede9233842ebb4d2339c99c0859c)"></g><g class="toyplot-coordinates-Axis" id="t8b9e87abab0046cc80c1ab0aaeb1f5e5" transform="translate(50.0,243.2)translate(0,15.0)"><line x1="19.325659145226954" y1="0" x2="174.56148620822125" y2="0" style=""></line><g><line x1="19.325659145226954" y1="0" x2="19.325659145226954" y2="-5" style=""></line><line x1="96.9435726767241" y1="0" x2="96.9435726767241" y2="-5" style=""></line><line x1="174.56148620822125" y1="0" x2="174.56148620822125" y2="-5" style=""></line></g><g><g transform="translate(19.325659145226954,6)"><text x="-5.56" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">10</text></g><g transform="translate(96.9435726767241,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">5</text></g><g transform="translate(174.56148620822125,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="t55d4afdd58734d5c9aef49c1b52845ca"><clipPath id="t4ab37ac995774f74965d9e732882a09f"><rect x="35.0" y="35.0" width="230.0" height="223.2"></rect></clipPath><g clip-path="url(#t4ab37ac995774f74965d9e732882a09f)"><g class="toytree-mark-Toytree" id="tedd7185e6c8441cd99bfa4bb5925da28"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 176.8 220.4 L 176.8 232.7 L 224.6 232.7" id="8,0" style=""></path><path d="M 176.8 220.4 L 176.8 208.1 L 224.6 208.1" id="8,1" style=""></path><path d="M 152.9 202.0 L 152.9 183.5 L 224.6 183.5" id="9,2" style=""></path><path d="M 152.9 146.6 L 152.9 158.9 L 200.7 158.9" id="10,3" style=""></path><path d="M 152.9 146.6 L 152.9 134.3 L 200.7 134.3" id="10,4" style=""></path><path d="M 105.1 142.0 L 105.1 109.7 L 152.9 109.7" id="12,5" style=""></path><path d="M 81.3 113.5 L 81.3 85.1 L 105.1 85.1" id="13,6" style=""></path><path d="M 69.3 87.0 L 69.3 60.5 L 81.3 60.5" id="14,7" style=""></path><path d="M 152.9 202.0 L 152.9 220.4 L 176.8 220.4" id="9,8" style=""></path><path d="M 129.0 174.3 L 129.0 202.0 L 152.9 202.0" id="11,9" style=""></path><path d="M 129.0 174.3 L 129.0 146.6 L 152.9 146.6" id="11,10" style=""></path><path d="M 105.1 142.0 L 105.1 174.3 L 129.0 174.3" id="12,11" style=""></path><path d="M 81.3 113.5 L 81.3 142.0 L 105.1 142.0" id="13,12" style=""></path><path d="M 69.3 87.0 L 69.3 113.5 L 81.3 113.5" id="14,13" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 224.6 232.7 L 224.6 232.7"></path><path d="M 224.6 208.1 L 224.6 208.1"></path><path d="M 224.6 183.5 L 224.6 183.5"></path><path d="M 224.6 158.9 L 200.7 158.9"></path><path d="M 224.6 134.3 L 200.7 134.3"></path><path d="M 224.6 109.7 L 152.9 109.7"></path><path d="M 224.6 85.1 L 105.1 85.1"></path><path d="M 224.6 60.5 L 81.3 60.5"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-14" transform="translate(69.3257,87.0136)"><rect x="-18.0" y="-9.0" width="36.0" height="18.0"></rect></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(69.3257,87.0136)"><text x="-7.7535" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">root</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.561,232.712)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.561,208.109)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.561,183.505)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.561,158.902)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.561,134.298)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.561,109.695)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.561,85.0914)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.561,60.488)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t8f859fe5ff874386bf0158cbfca13c49";
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
        })(modules["toyplot.coordinates.Axis"],"t8b9e87abab0046cc80c1ab0aaeb1f5e5",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 1.6387012117670408, "min": -11.24492261296}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


## Subpackage API
Many functions for working with trees are organized in subpackages. See their documentation sections for more details. Any of these methods which accept a toytree as their first argument are also accessible from a `ToyTree` object as a convenience. For example, `toytree.mod.func(tree)` is equivalent to `tree.mod.func()`. We refer to this as using the *module-level API* versus the *object-level API*.


```python
# call drop_tips from the module-level
toytree.mod.drop_tips(tree, "~r[4-6]").draw();
```


<div class="toyplot" id="t6d71eddd79dc4ce58e689510bdf9b96f" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tcd18e3ccaaf642aab48ef4f488dc160c"><g class="toyplot-coordinates-Cartesian" id="tb624fc1728ed4309841717d520087c11"><clipPath id="ta39ef2bf610f44fca87142c360c16cc9"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#ta39ef2bf610f44fca87142c360c16cc9)"></g></g><g class="toyplot-coordinates-Cartesian" id="tf592f9e64b604da783719d8390a7381f"><clipPath id="tc938df1d2aa4483782a53527d4857b4f"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tc938df1d2aa4483782a53527d4857b4f)"><g class="toytree-mark-Toytree" id="tef8012f8b05c4d3d869ab944de8fb5f9"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 75.8 187.7 L 75.8 217.8 L 224.7 217.8" id="6,0" style=""></path><path d="M 125.4 157.6 L 125.4 177.7 L 224.7 177.7" id="5,1" style=""></path><path d="M 125.4 157.6 L 125.4 137.5 L 224.7 137.5" id="5,2" style=""></path><path d="M 75.8 77.2 L 75.8 97.3 L 224.7 97.3" id="7,3" style=""></path><path d="M 75.8 77.2 L 75.8 57.2 L 224.7 57.2" id="7,4" style=""></path><path d="M 75.8 187.7 L 75.8 157.6 L 125.4 157.6" id="6,5" style=""></path><path d="M 51.0 132.5 L 51.0 187.7 L 75.8 187.7" id="8,6" style=""></path><path d="M 51.0 132.5 L 51.0 77.2 L 75.8 77.2" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.728,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.728,177.672)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.728,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.728,97.3276)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.728,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# call drop_tips from the object-level
tree.mod.drop_tips("~r[4-6]").draw();
```


<div class="toyplot" id="t7cc2b4859a394af4a6a7f425baca567e" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t5e51191334df429eae1a3769a383df61"><g class="toyplot-coordinates-Cartesian" id="t3262f8a94f144edbb05456f0d7083212"><clipPath id="td1060429f8e84b43837e3bbb827e6845"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#td1060429f8e84b43837e3bbb827e6845)"></g></g><g class="toyplot-coordinates-Cartesian" id="tac2a4d74545d404e9bf043f67ac58203"><clipPath id="t944e08e054b3425b9a47097021eb8d30"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t944e08e054b3425b9a47097021eb8d30)"><g class="toytree-mark-Toytree" id="tf6178a662c614914907ffa5e21f11357"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 75.8 187.7 L 75.8 217.8 L 224.7 217.8" id="6,0" style=""></path><path d="M 125.4 157.6 L 125.4 177.7 L 224.7 177.7" id="5,1" style=""></path><path d="M 125.4 157.6 L 125.4 137.5 L 224.7 137.5" id="5,2" style=""></path><path d="M 75.8 77.2 L 75.8 97.3 L 224.7 97.3" id="7,3" style=""></path><path d="M 75.8 77.2 L 75.8 57.2 L 224.7 57.2" id="7,4" style=""></path><path d="M 75.8 187.7 L 75.8 157.6 L 125.4 157.6" id="6,5" style=""></path><path d="M 51.0 132.5 L 51.0 187.7 L 75.8 187.7" id="8,6" style=""></path><path d="M 51.0 132.5 L 51.0 77.2 L 75.8 77.2" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.728,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.728,177.672)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.728,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.728,97.3276)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.728,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Writing trees
See the [Writing tree data](/write_trees/) documentation section. The function `write()` is used to write a tree to a newick or other format of serialized tree data, and to return it as a string or write to a file from a `ToyTree`, with options to also include metadata. 


```python
tree.write()
```




    '((r0:0.857142857143,(r1:0.571428571429,r2:0.571428571429):0.285714285714):0.142857142857,((r3:0.571428571429,r4:0.571428571429):0.285714285714,(r5:0.571428571429,(r6:0.285714285714,r7:0.285714285714):0.285714285714):0.285714285714):0.142857142857);'



## Drawing ToyTrees
See the [Tree Drawing](/drawing-basics/) documentation section for a detailed description of drawing options using the `.draw()` function.

## Style dict
`ToyTree` objects have a `.style` dict-like object that can be used to view all options for styling tree drawings, and to modify their default drawing style. This is an optional convenience, it is often simpler to provide arguments directly to the `.draw()` function. 


```python
# create a copy that we will modify the .style of
tre = tree.copy()

# set several style options on the tree
tre.style.node_style.fill = "black"
tre.style.node_style.stroke = "white"
tre.style.node_style.stroke_width = 3
tre.style.node_sizes = 12
tre.style.node_mask = False
tre.style.node_markers = "v"
tre.style.edge_style.stroke = "darkcyan"
tre.style.edge_style.stroke_width = 3
tre.style.layout = 'd'

# call draw and the .style will form the default tree style
tre.draw(tree_style=None);
```


<div class="toyplot" id="t5fe446a0baa74ae6b314e95d8f4d16f2" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tcf9ad9deb1194438a43746c823421e78"><g class="toyplot-coordinates-Cartesian" id="t2b2ef46e48b145138fafed5f94eb9d7d"><clipPath id="t1c56ae2577064389b73314013f822335"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t1c56ae2577064389b73314013f822335)"></g></g><g class="toyplot-coordinates-Cartesian" id="td692231547d245f38d59d025b2407d8b"><clipPath id="t0e922ac7af0e4963ab4bec7016d09c1d"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t0e922ac7af0e4963ab4bec7016d09c1d)"><g class="toytree-mark-Toytree" id="t4d70a6242eb24edd860e97460c066a90"><g class="toytree-Edges" style="stroke:rgb(0.0%,54.5%,54.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:3;fill:none"><path d="M 78.5 82.6 L 59.0 82.6 L 59.0 224.4" id="9,0" style=""></path><path d="M 98.0 129.9 L 85.0 129.9 L 85.0 224.4" id="8,1" style=""></path><path d="M 98.0 129.9 L 111.0 129.9 L 111.0 224.4" id="8,2" style=""></path><path d="M 150.0 129.9 L 137.0 129.9 L 137.0 224.4" id="10,3" style=""></path><path d="M 150.0 129.9 L 163.0 129.9 L 163.0 224.4" id="10,4" style=""></path><path d="M 208.5 129.9 L 189.0 129.9 L 189.0 224.4" id="12,5" style=""></path><path d="M 228.0 177.2 L 215.0 177.2 L 215.0 224.4" id="11,6" style=""></path><path d="M 228.0 177.2 L 241.0 177.2 L 241.0 224.4" id="11,7" style=""></path><path d="M 78.5 82.6 L 98.0 82.6 L 98.0 129.9" id="9,8" style=""></path><path d="M 128.9 59.0 L 78.5 59.0 L 78.5 82.6" id="14,9" style=""></path><path d="M 179.3 82.6 L 150.0 82.6 L 150.0 129.9" id="13,10" style=""></path><path d="M 208.5 129.9 L 228.0 129.9 L 228.0 177.2" id="12,11" style=""></path><path d="M 179.3 82.6 L 208.5 82.6 L 208.5 129.9" id="13,12" style=""></path><path d="M 128.9 59.0 L 179.3 59.0 L 179.3 82.6" id="14,13" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:3"><g id="Node-0" transform="translate(58.994,224.443)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(-180)"></polygon></g><g id="Node-1" transform="translate(84.9957,224.443)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(-180)"></polygon></g><g id="Node-2" transform="translate(110.997,224.443)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(-180)"></polygon></g><g id="Node-3" transform="translate(136.999,224.443)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(-180)"></polygon></g><g id="Node-4" transform="translate(163.001,224.443)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(-180)"></polygon></g><g id="Node-5" transform="translate(189.003,224.443)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(-180)"></polygon></g><g id="Node-6" transform="translate(215.004,224.443)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(-180)"></polygon></g><g id="Node-7" transform="translate(241.006,224.443)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(-180)"></polygon></g><g id="Node-8" transform="translate(97.9966,129.882)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(-180)"></polygon></g><g id="Node-9" transform="translate(78.4953,82.6014)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(-180)"></polygon></g><g id="Node-10" transform="translate(150,129.882)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(-180)"></polygon></g><g id="Node-11" transform="translate(228.005,177.162)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(-180)"></polygon></g><g id="Node-12" transform="translate(208.504,129.882)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(-180)"></polygon></g><g id="Node-13" transform="translate(179.252,82.6014)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(-180)"></polygon></g><g id="Node-14" transform="translate(128.874,58.9612)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(-180)"></polygon></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(58.994,224.443)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(84.9957,224.443)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(110.997,224.443)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(136.999,224.443)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(163.001,224.443)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(189.003,224.443)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(215.004,224.443)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(241.006,224.443)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>

