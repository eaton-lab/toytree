<div class="nb-md-page-hook" aria-hidden="true"></div>

# Quick Guide

This page is a practical overview of the main things people do with `toytree`: parse trees, inspect their data, select nodes, modify topology, draw figures, and save results. Use it to get oriented quickly, then follow the links to the more focused guides when you want more detail.

Useful next stops: [parsing tree data](parse_trees.md), [drawing basics](drawing-basics.md), [writing tree data](write_trees.md), and [command line usage](command-line.md).

## The `toytree` package
`toytree` is a Python library for working with trees as data structures. Most workflows start with a `ToyTree` object: you load tree data, inspect or store features on nodes, modify the tree, and then draw or export the result.

`toytree` works especially well in Jupyter notebooks because tree drawings display inline and remain easy to style in code. This guide is notebook-based, so you can follow it from top to bottom in your own session if you want to try the examples interactively.

To begin, let's import the package.


```python
import toytree
toytree.__version__
```




    '3.1.0.dev0'



## A simple example
This short example shows a common `toytree` workflow: parse a tree, reroot it, and draw it. The tree is loaded with `toytree.tree()`; for a broader overview of accepted input types and formats, see [parsing tree data](parse_trees.md).

The example below reads from a public URL, so it requires internet access. The call to `.root("~prz")` uses a regular-expression query to choose an edge based on matching names, which is covered in more detail in [node query and selection](core-query.md).

Finally, `.draw()` renders the tree in the notebook output. Here the tip labels are aligned and node hover tooltips are enabled, but the same method can also be used for simpler static drawings or more customized figures. See [drawing basics](drawing-basics.md) for the main drawing workflow.


```python
# load a toytree from a newick string at a URL
utree = toytree.tree("https://eaton-lab.org/data/Cyathophora.tre")

# re-root on internal edge selected using a regex string
rtree = utree.root("~prz")

# draw the rooted tree
rtree.draw(node_hover=True, node_sizes=8, tip_labels_align=True);
```


<div class="toyplot" id="t985e56cf831c4b97abe2fd64bf675646" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="349.23600000000005px" height="315.28px" viewBox="0 0 349.23600000000005 315.28" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t4d298db3cb534ce884317764a20bf12b"><g class="toyplot-coordinates-Cartesian" id="te19130e684b9414c9e2b9a813045102f"><clipPath id="t7ec1f77b4f9e44a785e2c2e7843536d4"><rect x="35.0" y="35.0" width="279.23600000000005" height="245.27999999999997"></rect></clipPath><g clip-path="url(#t7ec1f77b4f9e44a785e2c2e7843536d4)"></g></g><g class="toyplot-coordinates-Cartesian" id="t13f7ff13197c4e3e95700c98ce744cff"><clipPath id="tbc63562dbf9d47f1a427b251fc5a3c1c"><rect x="35.0" y="35.0" width="279.23600000000005" height="245.27999999999997"></rect></clipPath><g clip-path="url(#tbc63562dbf9d47f1a427b251fc5a3c1c)"><g class="toytree-mark-Toytree" id="tf596acaa5200473b8bb63e59bde59c3f"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 111.0 249.7 L 111.0 258.1 L 119.1 258.1" id="13,0" style=""></path><path d="M 111.0 249.7 L 111.0 241.3 L 118.7 241.3" id="13,1" style=""></path><path d="M 127.8 205.2 L 127.8 224.6 L 145.3 224.6" id="19,2" style=""></path><path d="M 131.0 185.9 L 131.0 207.9 L 151.2 207.9" id="18,3" style=""></path><path d="M 140.3 182.8 L 140.3 191.1 L 150.7 191.1" id="14,4" style=""></path><path d="M 140.3 182.8 L 140.3 174.4 L 150.9 174.4" id="14,5" style=""></path><path d="M 135.7 145.1 L 135.7 157.6 L 153.7 157.6" id="16,6" style=""></path><path d="M 154.8 132.5 L 154.8 140.9 L 157.8 140.9" id="15,7" style=""></path><path d="M 154.8 132.5 L 154.8 124.2 L 158.2 124.2" id="15,8" style=""></path><path d="M 127.7 99.0 L 127.7 107.4 L 147.3 107.4" id="20,9" style=""></path><path d="M 127.7 99.0 L 127.7 90.7 L 148.4 90.7" id="20,10" style=""></path><path d="M 149.5 65.6 L 149.5 73.9 L 149.7 73.9" id="21,11" style=""></path><path d="M 149.5 65.6 L 149.5 57.2 L 149.6 57.2" id="21,12" style=""></path><path d="M 55.4 196.7 L 55.4 249.7 L 111.0 249.7" id="24,13" style=""></path><path d="M 133.4 163.9 L 133.4 182.8 L 140.3 182.8" id="17,14" style=""></path><path d="M 135.7 145.1 L 135.7 132.5 L 154.8 132.5" id="16,15" style=""></path><path d="M 133.4 163.9 L 133.4 145.1 L 135.7 145.1" id="17,16" style=""></path><path d="M 131.0 185.9 L 131.0 163.9 L 133.4 163.9" id="18,17" style=""></path><path d="M 127.8 205.2 L 127.8 185.9 L 131.0 185.9" id="19,18" style=""></path><path d="M 111.0 143.8 L 111.0 205.2 L 127.8 205.2" id="23,19" style=""></path><path d="M 120.3 82.3 L 120.3 99.0 L 127.7 99.0" id="22,20" style=""></path><path d="M 120.3 82.3 L 120.3 65.6 L 149.5 65.6" id="22,21" style=""></path><path d="M 111.0 143.8 L 111.0 82.3 L 120.3 82.3" id="23,22" style=""></path><path d="M 55.4 196.7 L 55.4 143.8 L 111.0 143.8" id="24,23" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 158.2 258.1 L 119.1 258.1"></path><path d="M 158.2 241.3 L 118.7 241.3"></path><path d="M 158.2 224.6 L 145.3 224.6"></path><path d="M 158.2 207.9 L 151.2 207.9"></path><path d="M 158.2 191.1 L 150.7 191.1"></path><path d="M 158.2 174.4 L 150.9 174.4"></path><path d="M 158.2 157.6 L 153.7 157.6"></path><path d="M 158.2 140.9 L 157.8 140.9"></path><path d="M 158.2 124.2 L 158.2 124.2"></path><path d="M 158.2 107.4 L 147.3 107.4"></path><path d="M 158.2 90.7 L 148.4 90.7"></path><path d="M 158.2 73.9 L 149.7 73.9"></path><path d="M 158.2 57.2 L 149.6 57.2"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-13" transform="translate(111.043,249.71)"><title>idx: 13
dist: 0.0179371130487
support: 100
height: 0.0152107514239
name: </title><circle r="4.0"></circle></g><g id="Node-14" transform="translate(140.313,182.75)"><title>idx: 14
dist: 0.00222999650239
support: 100
height: 0.00577636172318
name: </title><circle r="4.0"></circle></g><g id="Node-15" transform="translate(154.845,132.53)"><title>idx: 15
dist: 0.00617527349892
support: 100
height: 0.00109218434613
name: </title><circle r="4.0"></circle></g><g id="Node-16" transform="translate(135.687,145.085)"><title>idx: 16
dist: 0.000738900380519
support: 96
height: 0.00726745784506
name: </title><circle r="4.0"></circle></g><g id="Node-17" transform="translate(133.394,163.918)"><title>idx: 17
dist: 0.000783365499905
support: 99
height: 0.00800635822557
name: </title><circle r="4.0"></circle></g><g id="Node-18" transform="translate(130.964,185.889)"><title>idx: 18
dist: 0.00103379657491
support: 100
height: 0.00878972372548
name: </title><circle r="4.0"></circle></g><g id="Node-19" transform="translate(127.757,205.244)"><title>idx: 19
dist: 0.00538723112355
support: 100
height: 0.00982352030039
name: </title><circle r="4.0"></circle></g><g id="Node-20" transform="translate(127.661,99.05)"><title>idx: 20
dist: 0.00237994755604
support: 100
height: 0.00985454237589
name: </title><circle r="4.0"></circle></g><g id="Node-21" transform="translate(149.471,65.57)"><title>idx: 21
dist: 0.00941020878048
support: 100
height: 0.00282428115145
name: </title><circle r="4.0"></circle></g><g id="Node-22" transform="translate(120.277,82.31)"><title>idx: 22
dist: 0.00297626149201
support: 100
height: 0.0122344899319
name: </title><circle r="4.0"></circle></g><g id="Node-23" transform="translate(111.043,143.777)"><title>idx: 23
dist: 0.0179371130487
support: 100
height: 0.0152107514239
name: </title><circle r="4.0"></circle></g><g id="Node-24" transform="translate(55.3954,196.744)"><title>idx: 24
dist: 0
support: nan
height: 0.0331478644727
name: root</title><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(158.233,258.08)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">32082_przewalskii</text></g><g class="toytree-TipLabel" transform="translate(158.233,241.34)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">33588_przewalskii</text></g><g class="toytree-TipLabel" transform="translate(158.233,224.6)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">33413_thamno</text></g><g class="toytree-TipLabel" transform="translate(158.233,207.86)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">30556_thamno</text></g><g class="toytree-TipLabel" transform="translate(158.233,191.12)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">40578_rex</text></g><g class="toytree-TipLabel" transform="translate(158.233,174.38)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">35855_rex</text></g><g class="toytree-TipLabel" transform="translate(158.233,157.64)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">35236_rex</text></g><g class="toytree-TipLabel" transform="translate(158.233,140.9)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">39618_rex</text></g><g class="toytree-TipLabel" transform="translate(158.233,124.16)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">38362_rex</text></g><g class="toytree-TipLabel" transform="translate(158.233,107.42)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">29154_superba</text></g><g class="toytree-TipLabel" transform="translate(158.233,90.68)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">30686_cyathophylla</text></g><g class="toytree-TipLabel" transform="translate(158.233,73.94)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">41954_cyathophylloides</text></g><g class="toytree-TipLabel" transform="translate(158.233,57.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">41478_cyathophylloides</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Parsing tree data
`toytree.tree()` is the main entry point for loading one tree. It accepts tree text, file paths, URLs, and bytes, and it can parse Newick, NHX-style metadata, and NEXUS containers. The dedicated guide in [parsing tree data](parse_trees.md) covers those formats in more detail.

In the example below, a Newick string is parsed into a `ToyTree`, and `get_node_data()` is used to inspect what was stored on each node. This is often the quickest way to confirm how tip names, branch lengths, and internal support values were interpreted.


```python
# newick str with edge-lengths & support values
newick = "((a:1,b:1)90:3,(c:3,(d:1,e:1)100:2)100:1);"

# load as ToyTree
tree = toytree.tree(newick)

# show tree data parsed from Newick str
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
      <td>a</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>b</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>c</td>
      <td>0.0</td>
      <td>3.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>d</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>e</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td></td>
      <td>1.0</td>
      <td>3.0</td>
      <td>90.0</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td></td>
      <td>1.0</td>
      <td>2.0</td>
      <td>100.0</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td></td>
      <td>3.0</td>
      <td>1.0</td>
      <td>100.0</td>
    </tr>
    <tr>
      <th>8</th>
      <td>8</td>
      <td></td>
      <td>4.0</td>
      <td>0.0</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



Once a tree is parsed, its stored features can be used directly in a drawing. In the example below, `node_labels="idx"` writes each node's cached index, and `edge_colors="dist"` maps branch lengths to colors automatically. This is usually safer and clearer than trying to keep separate style lists in the correct node order. See [data and features](core-data.md) for more detail.


```python
# tree drawing showing Node idx labels and edges colored by dist
tree.draw(
    layout='d', 
    node_labels="idx", node_sizes=15, node_mask=False, node_colors="lightgrey",
    edge_colors="dist", edge_widths=3,
    tip_labels_style={"font-size": 20, "anchor-shift": 20},
    scale_bar=True,
);
```


<div class="toyplot" id="t1da27039833a4ea3aa311f0bb0c12aad" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="ta6902383ef084b3092b2db851d45ccce"><g class="toyplot-coordinates-Cartesian" id="t12ebc1d105f94466a023f93eb2918470"><clipPath id="t5e381fd77b1949348214b9464cf114bc"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t5e381fd77b1949348214b9464cf114bc)"></g><g class="toyplot-coordinates-Axis" id="t739b100638f04c5fb844a40437f21b1b" transform="translate(50.0,250.0)rotate(-90.0)translate(0,-15.0)"><line x1="30.91885912478918" y1="0" x2="191.0581705615969" y2="0" style=""></line><g><line x1="30.91885912478918" y1="0" x2="30.91885912478918" y2="5" style=""></line><line x1="70.95368698399112" y1="0" x2="70.95368698399112" y2="5" style=""></line><line x1="110.98851484319306" y1="0" x2="110.98851484319306" y2="5" style=""></line><line x1="151.02334270239498" y1="0" x2="151.02334270239498" y2="5" style=""></line><line x1="191.0581705615969" y1="0" x2="191.0581705615969" y2="5" style=""></line></g><g><g transform="translate(30.91885912478918,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(70.95368698399112,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(110.98851484319306,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(151.02334270239498,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(191.0581705615969,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="t4eb4aa40d9b24fcf89deb52e8089c5e0"><clipPath id="ta683549262984754b142d93d8ed35667"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#ta683549262984754b142d93d8ed35667)"><g class="toytree-mark-Toytree" id="t45432b04c13a41fb87aa4012de6cd7e1"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 84.0 179.0 L 62.0 179.0 L 62.0 219.1" id="5,0" style="stroke:rgb(74.8%,89.8%,62.7%);stroke-opacity:1.0;stroke-width:3"></path><path d="M 84.0 179.0 L 106.0 179.0 L 106.0 219.1" id="5,1" style="stroke:rgb(74.8%,89.8%,62.7%);stroke-opacity:1.0;stroke-width:3"></path><path d="M 183.0 99.0 L 150.0 99.0 L 150.0 219.1" id="7,2" style="stroke:rgb(62.0%,0.4%,25.9%);stroke-opacity:1.0;stroke-width:3"></path><path d="M 216.0 179.0 L 194.0 179.0 L 194.0 219.1" id="6,3" style="stroke:rgb(74.8%,89.8%,62.7%);stroke-opacity:1.0;stroke-width:3"></path><path d="M 216.0 179.0 L 238.0 179.0 L 238.0 219.1" id="6,4" style="stroke:rgb(74.8%,89.8%,62.7%);stroke-opacity:1.0;stroke-width:3"></path><path d="M 133.5 58.9 L 84.0 58.9 L 84.0 179.0" id="8,5" style="stroke:rgb(62.0%,0.4%,25.9%);stroke-opacity:1.0;stroke-width:3"></path><path d="M 183.0 99.0 L 216.0 99.0 L 216.0 179.0" id="7,6" style="stroke:rgb(99.3%,74.8%,43.5%);stroke-opacity:1.0;stroke-width:3"></path><path d="M 133.5 58.9 L 183.0 58.9 L 183.0 99.0" id="8,7" style="stroke:rgb(74.8%,89.8%,62.7%);stroke-opacity:1.0;stroke-width:3"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(61.9817,219.081)"><circle r="7.5"></circle></g><g id="Node-1" transform="translate(105.991,219.081)"><circle r="7.5"></circle></g><g id="Node-2" transform="translate(150,219.081)"><circle r="7.5"></circle></g><g id="Node-3" transform="translate(194.009,219.081)"><circle r="7.5"></circle></g><g id="Node-4" transform="translate(238.018,219.081)"><circle r="7.5"></circle></g><g id="Node-5" transform="translate(83.9863,179.046)"><circle r="7.5"></circle></g><g id="Node-6" transform="translate(216.014,179.046)"><circle r="7.5"></circle></g><g id="Node-7" transform="translate(183.007,98.9767)"><circle r="7.5"></circle></g><g id="Node-8" transform="translate(133.497,58.9418)"><circle r="7.5"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(61.9817,219.081)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(105.991,219.081)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(150,219.081)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(194.009,219.081)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(238.018,219.081)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(83.9863,179.046)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(216.014,179.046)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(183.007,98.9767)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(133.497,58.9418)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:20px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(61.9817,219.081)rotate(90)"><text x="20.0" y="5.109999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:20.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(105.991,219.081)rotate(90)"><text x="20.0" y="5.109999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:20.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(150,219.081)rotate(90)"><text x="20.0" y="5.109999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:20.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(194.009,219.081)rotate(90)"><text x="20.0" y="5.109999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:20.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(238.018,219.081)rotate(90)"><text x="20.0" y="5.109999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:20.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "ta6902383ef084b3092b2db851d45ccce";
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
        })(modules["toyplot.coordinates.Axis"],"t739b100638f04c5fb844a40437f21b1b",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 4.223351264800001, "min": -0.7722990400640009}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


## Class objects

The core `toytree` objects form a simple hierarchy. A [`Node`](node.md) stores local tree data and relationships. A collection of connected nodes is wrapped by a [`ToyTree`](tree.md), which is the main object most users work with. A collection of trees can then be grouped into a [`MultiTree`](multitree.md).

You do not need to memorize the full class structure to get started. In practice, most work begins with a `ToyTree`, and `Node` or `MultiTree` objects become important when you need direct access to one part of a tree or to many trees at once.

**Node**: See the [Node class](core-node.md) docs for the full API. In everyday use, you usually reach `Node` objects by indexing or traversing a tree. Nodes store local information such as names, distances, and any extra features you assign. Each node in a `ToyTree` also has an `idx` value that reflects the tree's cached traversal order; see [traversal and node selection](core-traversal.md) for more on that.


```python
# you can create a Node object on its own
toytree.Node(name="X")
```




    <Node(name='X')>




```python
# but more often you will select Nodes from a tree by slicing or indexing
tree[0]
```




    <Node(idx=0, name='a')>




```python
# a Node's parent is at .up
tree[0].up
```




    <Node(idx=5)>




```python
# a Node's children are at .children
tree[5].children
```




    (<Node(idx=0, name='a')>, <Node(idx=1, name='b')>)




```python
# select one or more Nodes from a ToyTree by name
tree.get_nodes("a", "c")
```




    [<Node(idx=0, name='a')>, <Node(idx=2, name='c')>]




```python
# access data from attributes of a Node in a ToyTree
tree[0].idx, tree[0].name, tree[0].dist
```




    (0, 'a', 1.0)



**ToyTree**: See the [ToyTree class](core-toytree.md) docs for the full API. `ToyTree` is the main container for a connected set of nodes and the object you will usually pass around in analysis and plotting code. It caches useful derived information such as node heights, tip counts, and traversal order, while also exposing methods for rooting, pruning, editing data, and drawing. If a structural operation changes the tree, the cached view is rebuilt automatically.


```python
# create a tree from a Node object to serve as its root Node
toytree.ToyTree(toytree.Node("root"))
```




    <toytree.ToyTree at 0x7400214206e0>




```python
# parse a tree from newick data
toytree.tree("((a,b),c);")
```




    <toytree.ToyTree at 0x740021421eb0>




```python
tree.ntips
```




    5




```python
tree.nnodes
```




    9




```python
tree[5].height
```




    1.0




```python
# all nodes in the cached idx order (tips first then postorder traversal)
tree[:]
```




    [<Node(idx=0, name='a')>,
     <Node(idx=1, name='b')>,
     <Node(idx=2, name='c')>,
     <Node(idx=3, name='d')>,
     <Node(idx=4, name='e')>,
     <Node(idx=5)>,
     <Node(idx=6)>,
     <Node(idx=7)>,
     <Node(idx=8)>]




```python
# or, use .traverse() to visit Nodes in other traversal orders
list(tree.traverse("postorder"))
```




    [<Node(idx=0, name='a')>,
     <Node(idx=1, name='b')>,
     <Node(idx=5)>,
     <Node(idx=2, name='c')>,
     <Node(idx=3, name='d')>,
     <Node(idx=4, name='e')>,
     <Node(idx=6)>,
     <Node(idx=7)>,
     <Node(idx=8)>]



**MultiTree**: See the [MultiTree docs](core-multitree.md) for the full API. A `MultiTree` stores multiple `ToyTree` objects together so you can compare, summarize, or draw them as a set. The `toytree.mtree()` function parses multi-tree inputs, and `toytree.MultiTree()` can also be built from a collection of existing trees.


```python
# create a MultiTree containing three copies of 'tree' rooted differently
mtree = toytree.mtree([tree, tree.root('c'), tree.root('d', 'e')])
mtree
```




    <toytree.MultiTree ntrees=3>




```python
# select individual ToyTrees by indexing or slicing
mtree[0]
```




    <toytree.ToyTree at 0x740021410e00>




```python
# visualization methods for multiple trees. Takes similar arguments as ToyTree.draw()
mtree.draw(shape=(1, 3), tip_labels_style={"font-size": 16});
```


<div class="toyplot" id="tc0e8bf83dd4b4b21a36bfc52cda3850a" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="675.0px" height="250.0px" viewBox="0 0 675.0 250.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tf9fb88b14f364f52a3740ddbb7f3083f"><g class="toyplot-coordinates-Cartesian" id="tbbd9656dfe404a4bb277de545f72572f"><clipPath id="t8dea7e247cd24213b52ae64dcaeafa40"><rect x="20.0" y="40.0" width="205.0" height="170.0"></rect></clipPath><g clip-path="url(#t8dea7e247cd24213b52ae64dcaeafa40)"></g></g><g class="toyplot-coordinates-Cartesian" id="tf82db7a571864af48a4287cfa627e11d"><clipPath id="t9c92a6954f9f49f28684fb2625f07c6a"><rect x="20.0" y="40.0" width="205.0" height="170.0"></rect></clipPath><g clip-path="url(#t9c92a6954f9f49f28684fb2625f07c6a)"><g class="toytree-mark-Toytree" id="t7eecf844bb35427d9b591a3ba770ec59"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 155.0 174.2 L 155.0 190.5 L 196.3 190.5" id="5,0" style=""></path><path d="M 155.0 174.2 L 155.0 157.8 L 196.3 157.8" id="5,1" style=""></path><path d="M 72.3 100.4 L 72.3 125.0 L 196.3 125.0" id="7,2" style=""></path><path d="M 155.0 75.8 L 155.0 92.2 L 196.3 92.2" id="6,3" style=""></path><path d="M 155.0 75.8 L 155.0 59.5 L 196.3 59.5" id="6,4" style=""></path><path d="M 31.0 137.3 L 31.0 174.2 L 155.0 174.2" id="8,5" style=""></path><path d="M 72.3 100.4 L 72.3 75.8 L 155.0 75.8" id="7,6" style=""></path><path d="M 31.0 137.3 L 31.0 100.4 L 72.3 100.4" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:16px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(196.299,190.537)"><text x="10.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(196.299,157.769)"><text x="10.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(196.299,125)"><text x="10.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(196.299,92.2313)"><text x="10.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(196.299,59.4626)"><text x="10.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="td5d8793bee0e489fbd58ad820cb6ed97"><clipPath id="t83f0ec97123a48e89355a80f7fcecef0"><rect x="245.0" y="40.0" width="205.0" height="170.0"></rect></clipPath><g clip-path="url(#t83f0ec97123a48e89355a80f7fcecef0)"></g></g><g class="toyplot-coordinates-Cartesian" id="t48fde50dd24d4a329795efe43f425103"><clipPath id="t98dd4b384e0f436891681f9222844859"><rect x="245.0" y="40.0" width="205.0" height="170.0"></rect></clipPath><g clip-path="url(#t98dd4b384e0f436891681f9222844859)"><g class="toytree-mark-Toytree" id="ta40ac1d098724864b3e6d6dbcb8da741"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 256.0 149.6 L 256.0 190.5 L 294.1 190.5" id="8,0" style=""></path><path d="M 345.0 141.4 L 345.0 157.8 L 370.4 157.8" id="5,1" style=""></path><path d="M 345.0 141.4 L 345.0 125.0 L 370.4 125.0" id="5,2" style=""></path><path d="M 395.9 75.8 L 395.9 92.2 L 421.3 92.2" id="6,3" style=""></path><path d="M 395.9 75.8 L 395.9 59.5 L 421.3 59.5" id="6,4" style=""></path><path d="M 294.1 108.6 L 294.1 141.4 L 345.0 141.4" id="7,5" style=""></path><path d="M 294.1 108.6 L 294.1 75.8 L 395.9 75.8" id="7,6" style=""></path><path d="M 256.0 149.6 L 256.0 108.6 L 294.1 108.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:16px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(294.138,190.537)"><text x="10.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(370.435,157.769)"><text x="10.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(370.435,125)"><text x="10.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(421.299,92.2313)"><text x="10.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(421.299,59.4626)"><text x="10.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="tf95488d2061f4eb79318a6b503e5ef77"><clipPath id="t1c863fce8233447288c95b46b6005bac"><rect x="470.0" y="40.0" width="205.0" height="170.0"></rect></clipPath><g clip-path="url(#t1c863fce8233447288c95b46b6005bac)"></g></g><g class="toyplot-coordinates-Cartesian" id="t9d5c6d0c41ec44479d5356b9f78be4b0"><clipPath id="t5fd3a8cde66940599862e337393f37c8"><rect x="470.0" y="40.0" width="205.0" height="170.0"></rect></clipPath><g clip-path="url(#t5fd3a8cde66940599862e337393f37c8)"><g class="toytree-mark-Toytree" id="t66ee685844ef466bbdfcafd7a9221ee8"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 508.5 174.2 L 508.5 190.5 L 536.1 190.5" id="5,0" style=""></path><path d="M 508.5 174.2 L 508.5 157.8 L 536.1 157.8" id="5,1" style=""></path><path d="M 508.5 100.4 L 508.5 125.0 L 591.2 125.0" id="7,2" style=""></path><path d="M 618.7 75.8 L 618.7 92.2 L 646.3 92.2" id="6,3" style=""></path><path d="M 618.7 75.8 L 618.7 59.5 L 646.3 59.5" id="6,4" style=""></path><path d="M 481.0 137.3 L 481.0 174.2 L 508.5 174.2" id="8,5" style=""></path><path d="M 508.5 100.4 L 508.5 75.8 L 618.7 75.8" id="7,6" style=""></path><path d="M 481.0 137.3 L 481.0 100.4 L 508.5 100.4" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:16px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(536.093,190.537)"><text x="10.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(536.093,157.769)"><text x="10.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(591.196,125)"><text x="10.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(646.299,92.2313)"><text x="10.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(646.299,59.4626)"><text x="10.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Learning to use `toytree`

One of the fastest ways to learn `toytree` is to explore objects interactively in Jupyter or an IDE with tab completion. A `ToyTree` exposes many attributes and methods, and seeing them in context is often more useful than reading a long reference page from top to bottom.

In a notebook, type a variable name such as <i>tree</i>, add a dot, and press <kbd>tab</kbd> to inspect the available methods. A few examples are shown below.


```python
tree.copy()
```




    <toytree.ToyTree at 0x74002149b6e0>




```python
tree.is_rooted()
```




    True




```python
tree.is_monophyletic("a", "b")
```




    True




```python
tree.get_ancestors("a")
```




    {<Node(idx=0, name='a')>, <Node(idx=5)>, <Node(idx=8)>}




```python
tree.get_mrca_node("d", "e")
```




    <Node(idx=6)>




```python
tree.get_tip_labels()
```




    ['a', 'b', 'c', 'd', 'e']



## Selecting nodes
Many tree operations need one or more nodes as input. `toytree` tries to make that practical by allowing selection by name, regular expression, integer `idx`, or MRCA queries instead of forcing you to rely on one fragile indexing scheme.

The examples below use `get_nodes()` and `get_mrca_node()`, which cover most everyday selection tasks. The fuller selection guide is [node query and selection](core-query.md).


```python
# select nodes by name
tree.get_nodes("a", "b")
```




    [<Node(idx=0, name='a')>, <Node(idx=1, name='b')>]




```python
# select nodes by regular expression
tree.get_nodes("~[a-c]")
```




    [<Node(idx=0, name='a')>, <Node(idx=2, name='c')>, <Node(idx=1, name='b')>]




```python
# select internal node by mrca of tip names
tree.get_mrca_node("a", "b")
```




    <Node(idx=5)>




```python
# or, select a node directly by its idx label
tree[5]
```




    <Node(idx=5)>



## Subpackages
The `ToyTree` object is intentionally kept focused on the most common tree operations. More specialized algorithms live in subpackages such as `rtree`, `mod`, `distance`, `annotate`, and `pcm`. This keeps the main object easier to explore while still making the broader toolkit available when you need it.

The examples below are only a brief orientation. Treat this section as a map of where to look next, not as a full tour of each subpackage.

**rtree**: Random tree generation functions. Use `rtree` when you need small example trees, test data, or simulated topologies for an analysis workflow.


```python
# generate a birth-death tree
btree = toytree.rtree.bdtree(ntips=8, b=1, d=0.1, seed=123, random_names=True)
btree.draw(scale_bar=True);
```


<div class="toyplot" id="t30805e3223db49bc89570eb9073d30bc" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t4ae76f7a969f4dc5a93e9eb3ea1caa80"><g class="toyplot-coordinates-Cartesian" id="t7ccd46e265f04cd1b14b60bbd0bfde0b"><clipPath id="teed344f9ad0a4b01b5c9f8fe31031cca"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#teed344f9ad0a4b01b5c9f8fe31031cca)"></g><g class="toyplot-coordinates-Axis" id="t5e30f05b566a41b88d981a7ede359652" transform="translate(50.0,225.0)translate(0,15.0)"><line x1="0.9845545534227687" y1="0" x2="174.72845372274378" y2="0" style=""></line><g><line x1="5.929188970062591" y1="0" x2="5.929188970062591" y2="-5" style=""></line><line x1="90.3288213464032" y1="0" x2="90.3288213464032" y2="-5" style=""></line><line x1="174.72845372274378" y1="0" x2="174.72845372274378" y2="-5" style=""></line></g><g><g transform="translate(5.929188970062591,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(90.3288213464032,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(174.72845372274378,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="t52c3e927a37c4d5aa788b2e52d650bc9"><clipPath id="t2757038787a4429198e0aa1ce84df0d2"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t2757038787a4429198e0aa1ce84df0d2)"><g class="toytree-mark-Toytree" id="td597af3cde6341aaa6bfeae80caa58b0"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 211.7 206.4 L 211.7 217.8 L 224.7 217.8" id="8,0" style=""></path><path d="M 211.7 206.4 L 211.7 194.9 L 224.7 194.9" id="8,1" style=""></path><path d="M 186.3 189.2 L 186.3 171.9 L 224.7 171.9" id="9,2" style=""></path><path d="M 139.8 131.8 L 139.8 149.0 L 224.7 149.0" id="11,3" style=""></path><path d="M 212.1 114.5 L 212.1 126.0 L 224.7 126.0" id="10,4" style=""></path><path d="M 212.1 114.5 L 212.1 103.1 L 224.7 103.1" id="10,5" style=""></path><path d="M 192.1 68.6 L 192.1 80.1 L 224.7 80.1" id="12,6" style=""></path><path d="M 192.1 68.6 L 192.1 57.2 L 224.7 57.2" id="12,7" style=""></path><path d="M 186.3 189.2 L 186.3 206.4 L 211.7 206.4" id="9,8" style=""></path><path d="M 51.0 144.7 L 51.0 189.2 L 186.3 189.2" id="14,9" style=""></path><path d="M 139.8 131.8 L 139.8 114.5 L 212.1 114.5" id="11,10" style=""></path><path d="M 117.1 100.2 L 117.1 131.8 L 139.8 131.8" id="13,11" style=""></path><path d="M 117.1 100.2 L 117.1 68.6 L 192.1 68.6" id="13,12" style=""></path><path d="M 51.0 144.7 L 51.0 100.2 L 117.1 100.2" id="14,13" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.728,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.728,194.889)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.728,171.933)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.728,148.978)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.728,126.022)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.728,103.067)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.728,80.1109)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.728,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t4ae76f7a969f4dc5a93e9eb3ea1caa80";
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
        })(modules["toyplot.coordinates.Axis"],"t5e30f05b566a41b88d981a7ede359652",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.29942720798320044, "min": -2.0702513601436574}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


**enum**: enumeration of tree data. Use `enum` when you need exact sets of tree-derived objects such as quartets or bipartitions, often for testing or algorithm development.


```python
# expand a generator over all quartets in a tree
list(toytree.enum.iter_quartets(tree))
```




    [({'a', 'b'}, {'c', 'e'}),
     ({'a', 'b'}, {'c', 'd'}),
     ({'a', 'b'}, {'d', 'e'}),
     ({'d', 'e'}, {'a', 'c'}),
     ({'d', 'e'}, {'b', 'c'})]



**distance**: node and tree distance metrics. Use `distance` to measure paths within one tree or to compare the similarity of two trees.


```python
# return a matrix of distances between tips in a tree
toytree.distance.get_tip_distance_matrix(tree, df=True)
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
      <th>a</th>
      <th>b</th>
      <th>c</th>
      <th>d</th>
      <th>e</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>a</th>
      <td>0.0</td>
      <td>2.0</td>
      <td>8.0</td>
      <td>8.0</td>
      <td>8.0</td>
    </tr>
    <tr>
      <th>b</th>
      <td>2.0</td>
      <td>0.0</td>
      <td>8.0</td>
      <td>8.0</td>
      <td>8.0</td>
    </tr>
    <tr>
      <th>c</th>
      <td>8.0</td>
      <td>8.0</td>
      <td>0.0</td>
      <td>6.0</td>
      <td>6.0</td>
    </tr>
    <tr>
      <th>d</th>
      <td>8.0</td>
      <td>8.0</td>
      <td>6.0</td>
      <td>0.0</td>
      <td>2.0</td>
    </tr>
    <tr>
      <th>e</th>
      <td>8.0</td>
      <td>8.0</td>
      <td>6.0</td>
      <td>2.0</td>
      <td>0.0</td>
    </tr>
  </tbody>
</table>
</div>




```python
# return the Robinson-Foulds tree distance between two random 10-tip trees
rtree1 = toytree.rtree.rtree(10, seed=123)
rtree2 = toytree.rtree.rtree(10, seed=321)
toytree.distance.get_treedist_rf(rtree1, rtree2, normalize=True)
```




    0.42857142857142855



**mod**: Tree modifications. Use `mod` for tree-editing operations such as rerooting, pruning, rescaling branch lengths, or changing topology.


```python
# return a tree with edges scaled so root is at height=100
modified = toytree.mod.edges_scale_to_root_height(tree, 100)

# show the original and modified trees side by side
toytree.mtree([tree, modified]).draw(shape=(1, 2), scale_bar=True, tip_labels_style={'font-size': 15});
```


<div class="toyplot" id="t03c4404038fd4cb49432324c9a1bb205" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="450.0px" height="250.0px" viewBox="0 0 450.0 250.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="taf3f04a14d36486b86cec92c46ed3de3"><g class="toyplot-coordinates-Cartesian" id="t2b5723af86fc47019a160a22bb7b1bff"><clipPath id="t31f55bf0e7c84dafb315956fca349487"><rect x="20.0" y="40.0" width="205.0" height="150.0"></rect></clipPath><g clip-path="url(#t31f55bf0e7c84dafb315956fca349487)"></g><g class="toyplot-coordinates-Axis" id="ta4ea0fec74a949adb96d21c8b631de27" transform="translate(30.0,180.0)translate(0,10.0)"><line x1="0.9902025766573388" y1="0" x2="166.839684744105" y2="0" style=""></line><g><line x1="0.9902025766573388" y1="0" x2="0.9902025766573388" y2="-5" style=""></line><line x1="42.45257311851926" y1="0" x2="42.45257311851926" y2="-5" style=""></line><line x1="83.91494366038117" y1="0" x2="83.91494366038117" y2="-5" style=""></line><line x1="125.3773142022431" y1="0" x2="125.3773142022431" y2="-5" style=""></line><line x1="166.839684744105" y1="0" x2="166.839684744105" y2="-5" style=""></line></g><g><g transform="translate(0.9902025766573388,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(42.45257311851926,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(83.91494366038117,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(125.3773142022431,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(166.839684744105,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="t0be4ded70f2341bcab0432b6bbbff99a"><clipPath id="tc08e49e78912492a8275447a994db5c5"><rect x="20.0" y="40.0" width="205.0" height="150.0"></rect></clipPath><g clip-path="url(#tc08e49e78912492a8275447a994db5c5)"><g class="toytree-mark-Toytree" id="t2e3331e43f714a28afc4f097673d9335"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 155.4 157.1 L 155.4 171.1 L 196.8 171.1" id="5,0" style=""></path><path d="M 155.4 157.1 L 155.4 143.1 L 196.8 143.1" id="5,1" style=""></path><path d="M 72.5 93.9 L 72.5 115.0 L 196.8 115.0" id="7,2" style=""></path><path d="M 155.4 72.9 L 155.4 86.9 L 196.8 86.9" id="6,3" style=""></path><path d="M 155.4 72.9 L 155.4 58.9 L 196.8 58.9" id="6,4" style=""></path><path d="M 31.0 125.5 L 31.0 157.1 L 155.4 157.1" id="8,5" style=""></path><path d="M 72.5 93.9 L 72.5 72.9 L 155.4 72.9" id="7,6" style=""></path><path d="M 31.0 125.5 L 31.0 93.9 L 72.5 93.9" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:15px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(196.84,171.149)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(196.84,143.075)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(196.84,115)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(196.84,86.9255)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(196.84,58.851)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="tb521fd5a0db842af8a38fa13171bec98"><clipPath id="tdd8402343b244b1baecb567b55c084ac"><rect x="245.0" y="40.0" width="205.0" height="150.0"></rect></clipPath><g clip-path="url(#tdd8402343b244b1baecb567b55c084ac)"></g><g class="toyplot-coordinates-Axis" id="tc7e2ba1207744fd8a353ff2cbcf98e66" transform="translate(255.0,180.0)translate(0,10.0)"><line x1="0.9902025766572762" y1="0" x2="166.83968474410506" y2="0" style=""></line><g><line x1="0.9902025766572762" y1="0" x2="0.9902025766572762" y2="-5" style=""></line><line x1="83.91494366038117" y1="0" x2="83.91494366038117" y2="-5" style=""></line><line x1="166.83968474410506" y1="0" x2="166.83968474410506" y2="-5" style=""></line></g><g><g transform="translate(0.9902025766572762,6)"><text x="-8.34" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">100</text></g><g transform="translate(83.91494366038117,6)"><text x="-5.56" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">50</text></g><g transform="translate(166.83968474410506,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="t87348653c1234f2b9843e3547012d97a"><clipPath id="tb4eef617ac30475ca99505598d8a7721"><rect x="245.0" y="40.0" width="205.0" height="150.0"></rect></clipPath><g clip-path="url(#tb4eef617ac30475ca99505598d8a7721)"><g class="toytree-mark-Toytree" id="t900789a969e34db0a3a0749407f35e09"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 380.4 157.1 L 380.4 171.1 L 421.8 171.1" id="5,0" style=""></path><path d="M 380.4 157.1 L 380.4 143.1 L 421.8 143.1" id="5,1" style=""></path><path d="M 297.5 93.9 L 297.5 115.0 L 421.8 115.0" id="7,2" style=""></path><path d="M 380.4 72.9 L 380.4 86.9 L 421.8 86.9" id="6,3" style=""></path><path d="M 380.4 72.9 L 380.4 58.9 L 421.8 58.9" id="6,4" style=""></path><path d="M 256.0 125.5 L 256.0 157.1 L 380.4 157.1" id="8,5" style=""></path><path d="M 297.5 93.9 L 297.5 72.9 L 380.4 72.9" id="7,6" style=""></path><path d="M 256.0 125.5 L 256.0 93.9 L 297.5 93.9" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:15px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(421.84,171.149)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(421.84,143.075)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(421.84,115)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(421.84,86.9255)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(421.84,58.851)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "taf3f04a14d36486b86cec92c46ed3de3";
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
        })(modules["toyplot.coordinates.Axis"],"ta4ea0fec74a949adb96d21c8b631de27",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.4379951029948873, "min": -4.02388195763331}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 185.0, "min": 0.0}, "scale": "linear"}]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"tc7e2ba1207744fd8a353ff2cbcf98e66",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 10.949877574872131, "min": -100.5970489408327}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 185.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>



```python
# return a tree with a new split (internal node and child) added
modified = toytree.mod.add_internal_node_and_child(tree, "d", name="x")

# show the original and modified trees side by side
toytree.mtree([tree, modified]).draw(shape=(1, 2), tip_labels_style={'font-size': 15});
```


<div class="toyplot" id="t84a3a0f1c48b492da2d7c4f1db2ea9ab" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="450.0px" height="250.0px" viewBox="0 0 450.0 250.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tc091105f6028467983f4bfb680eec9b1"><g class="toyplot-coordinates-Cartesian" id="t66a6cea4b9874e2fabae5280a7f3fe98"><clipPath id="tccbad2f0214945488ce3921a0e73684d"><rect x="20.0" y="40.0" width="205.0" height="170.0"></rect></clipPath><g clip-path="url(#tccbad2f0214945488ce3921a0e73684d)"></g></g><g class="toyplot-coordinates-Cartesian" id="t9c5dfceed8d5474baf1ffac61caa199c"><clipPath id="tc121bcd1011946b1b84a136a5cea3eb3"><rect x="20.0" y="40.0" width="205.0" height="170.0"></rect></clipPath><g clip-path="url(#tc121bcd1011946b1b84a136a5cea3eb3)"><g class="toytree-mark-Toytree" id="t2fa7325ca1754faab278fee1a48a62a4"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 155.4 174.6 L 155.4 191.1 L 196.8 191.1" id="5,0" style=""></path><path d="M 155.4 174.6 L 155.4 158.1 L 196.8 158.1" id="5,1" style=""></path><path d="M 72.5 100.2 L 72.5 125.0 L 196.8 125.0" id="7,2" style=""></path><path d="M 155.4 75.4 L 155.4 91.9 L 196.8 91.9" id="6,3" style=""></path><path d="M 155.4 75.4 L 155.4 58.9 L 196.8 58.9" id="6,4" style=""></path><path d="M 31.0 137.4 L 31.0 174.6 L 155.4 174.6" id="8,5" style=""></path><path d="M 72.5 100.2 L 72.5 75.4 L 155.4 75.4" id="7,6" style=""></path><path d="M 31.0 137.4 L 31.0 100.2 L 72.5 100.2" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:15px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(196.84,191.114)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(196.84,158.057)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(196.84,125)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(196.84,91.9429)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(196.84,58.8858)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t0fa0be47c1104570b927da861342d9b6"><clipPath id="t8086ee7456834dc48bced35171cdf570"><rect x="245.0" y="40.0" width="205.0" height="170.0"></rect></clipPath><g clip-path="url(#t8086ee7456834dc48bced35171cdf570)"></g></g><g class="toyplot-coordinates-Cartesian" id="t815ebf1b4db04a7b8eafc06252170160"><clipPath id="td1de3a26101a4bb38007345277fd628f"><rect x="245.0" y="40.0" width="205.0" height="170.0"></rect></clipPath><g clip-path="url(#td1de3a26101a4bb38007345277fd628f)"><g class="toytree-mark-Toytree" id="ta7e4653f73d64584bfc810e628a63fc7"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 380.4 177.9 L 380.4 191.1 L 421.8 191.1" id="6,0" style=""></path><path d="M 380.4 177.9 L 380.4 164.7 L 421.8 164.7" id="6,1" style=""></path><path d="M 297.5 115.1 L 297.5 138.2 L 421.8 138.2" id="9,2" style=""></path><path d="M 380.4 91.9 L 380.4 111.8 L 421.8 111.8" id="8,3" style=""></path><path d="M 401.1 72.1 L 401.1 85.3 L 421.8 85.3" id="7,4" style=""></path><path d="M 401.1 72.1 L 401.1 58.9 L 421.8 58.9" id="7,5" style=""></path><path d="M 256.0 146.5 L 256.0 177.9 L 380.4 177.9" id="10,6" style=""></path><path d="M 380.4 91.9 L 380.4 72.1 L 401.1 72.1" id="8,7" style=""></path><path d="M 297.5 115.1 L 297.5 91.9 L 380.4 91.9" id="9,8" style=""></path><path d="M 256.0 146.5 L 256.0 115.1 L 297.5 115.1" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:15px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(421.84,191.114)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(421.84,164.669)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(421.84,138.223)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(421.84,111.777)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(421.84,85.3315)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(421.84,58.8858)"><text x="10.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">x</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


**annotate**: add annotations to tree drawings. Use `annotate` when you want to add labels, markers, bars, or other extras after the initial `draw()` call.


```python
# draw a tree and store returned objects
canvas, axes, mark = tree.draw()

# annotate method to add node markers
toytree.annotate.add_tip_markers(tree, axes, color="salmon", size=12);

# annotate method to add to edge labels
toytree.annotate.add_edge_labels(tree, axes, labels="idx", font_size=15, yshift=-12, mask=False);
```


<div class="toyplot" id="t4892fb0bdbad4afb99ae6d17f7388cf0" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t231d1b71ec014cf09738fed7a81a8976"><g class="toyplot-coordinates-Cartesian" id="t465eca0957ab4e36a8e6729c927a7819"><clipPath id="t9c88eecfe78841fcb4acbdfc8721f990"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t9c88eecfe78841fcb4acbdfc8721f990)"></g></g><g class="toyplot-coordinates-Cartesian" id="t9cad21960a914d70bc65e0fff58e771d"><clipPath id="tf27550eae19a4ed39834897749059500"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tf27550eae19a4ed39834897749059500)"><g class="toytree-mark-Toytree" id="t9e6a4af3f0eb452e83b41ec34e749b06"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 184.2 196.4 L 184.2 216.1 L 228.6 216.1" id="5,0" style=""></path><path d="M 184.2 196.4 L 184.2 176.8 L 228.6 176.8" id="5,1" style=""></path><path d="M 95.4 108.0 L 95.4 137.5 L 228.6 137.5" id="7,2" style=""></path><path d="M 184.2 78.6 L 184.2 98.2 L 228.6 98.2" id="6,3" style=""></path><path d="M 184.2 78.6 L 184.2 58.9 L 228.6 58.9" id="6,4" style=""></path><path d="M 51.0 152.2 L 51.0 196.4 L 184.2 196.4" id="8,5" style=""></path><path d="M 95.4 108.0 L 95.4 78.6 L 184.2 78.6" id="7,6" style=""></path><path d="M 51.0 152.2 L 51.0 108.0 L 95.4 108.0" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(228.575,216.086)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(228.575,176.793)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(228.575,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(228.575,98.2072)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(228.575,58.9145)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g></g></g><g class="toytree-Annotation-Markers" id="t5605a9bbfa6b4a80acdfb0493c6df75b" style="fill:rgb(98.0%,50.2%,44.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Mark-0" style="fill-opacity: 1.000" transform="translate(228.575,216.086)"><circle r="6.0"></circle></g><g id="Mark-1" style="fill-opacity: 1.000" transform="translate(228.575,176.793)"><circle r="6.0"></circle></g><g id="Mark-2" style="fill-opacity: 1.000" transform="translate(228.575,137.5)"><circle r="6.0"></circle></g><g id="Mark-3" style="fill-opacity: 1.000" transform="translate(228.575,98.2072)"><circle r="6.0"></circle></g><g id="Mark-4" style="fill-opacity: 1.000" transform="translate(228.575,58.9145)"><circle r="6.0"></circle></g></g><g class="toyplot-mark-Text" id="tda85f8f3e2e044e39c7c66664457394d"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(206.37694873766515,216.08551570427286)"><text x="-4.170000000000001" y="-8.1675" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:15.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g class="toyplot-Datum" transform="translate(206.37694873766515,176.79275785213645)"><text x="-4.170000000000001" y="-8.1675" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:15.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g class="toyplot-Datum" transform="translate(161.9802747040583,137.50000000000003)"><text x="-4.170000000000001" y="-8.1675" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:15.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g class="toyplot-Datum" transform="translate(206.37694873766515,98.20724214786358)"><text x="-4.170000000000001" y="-8.1675" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:15.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g class="toyplot-Datum" transform="translate(206.37694873766515,58.91448429572716)"><text x="-4.170000000000001" y="-8.1675" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:15.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g class="toyplot-Datum" transform="translate(117.58360067045143,196.43913677820464)"><text x="-4.170000000000001" y="-8.1675" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:15.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">8</text></g><g class="toyplot-Datum" transform="translate(139.78193768725487,78.56086322179537)"><text x="-4.170000000000001" y="-8.1675" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:15.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">6</text></g><g class="toyplot-Datum" transform="translate(73.18692663684456,108.0304316108977)"><text x="-4.170000000000001" y="-8.1675" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:15.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">8</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


**pcm**: phylogenetic comparative methods. This subpackage currently includes simulation and model-fitting tools for discrete and continuous traits, and it is the place to look when your tree is part of a comparative analysis.


```python
# get variance-covariance matrix from tree
toytree.pcm.get_vcv_matrix_from_tree(tree, df=True)
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
      <th>a</th>
      <th>b</th>
      <th>c</th>
      <th>d</th>
      <th>e</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>a</th>
      <td>4.0</td>
      <td>3.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>b</th>
      <td>3.0</td>
      <td>4.0</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>c</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>4.0</td>
      <td>1.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>d</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>4.0</td>
      <td>3.0</td>
    </tr>
    <tr>
      <th>e</th>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>3.0</td>
      <td>4.0</td>
    </tr>
  </tbody>
</table>
</div>




```python
# simulate a discrete trait under a Markov transition model
toytree.pcm.simulate_discrete_trait(tree, nstates=3, model="ER")
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
      <th>t0</th>
      <th>t1</th>
      <th>t2</th>
      <th>t3</th>
      <th>t4</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2</td>
      <td>2</td>
      <td>0</td>
      <td>2</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2</td>
      <td>2</td>
      <td>0</td>
      <td>2</td>
      <td>1</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>2</td>
      <td>0</td>
      <td>1</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2</td>
      <td>1</td>
      <td>2</td>
      <td>1</td>
      <td>2</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2</td>
      <td>1</td>
      <td>1</td>
      <td>2</td>
      <td>1</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2</td>
      <td>2</td>
      <td>0</td>
      <td>2</td>
      <td>2</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2</td>
      <td>1</td>
      <td>2</td>
      <td>2</td>
      <td>1</td>
    </tr>
    <tr>
      <th>7</th>
      <td>1</td>
      <td>2</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
    </tr>
    <tr>
      <th>8</th>
      <td>1</td>
      <td>2</td>
      <td>2</td>
      <td>0</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



## Storing data to trees
Trees often need more than topology and branch lengths. `toytree` lets you attach arbitrary features to nodes, either by assigning attributes directly or, more commonly, by using `set_node_data()` to update many nodes at once.

After adding data, `get_node_data()` is the quickest way to inspect what is present across the full tree. The examples below show a few common patterns: setting one default for all nodes, setting one value for tips and another for internal nodes, and leaving some nodes missing.


```python
# make a copy of tree on which we will add a bunch of data
dtree = tree.copy()

# add a feature and set all Nodes to a default value
dtree = dtree.set_node_data("trait1", default=10)

# or set some to specific values and others to a default
dtree = dtree.set_node_data("trait2", {i: 5 for i in range(dtree.ntips)}, default=1)

# or add some to specific values and leave others as NaN
dtree = dtree.set_node_data("trait3", {0: "X", 1: "Y"})

# or, add a feature by assigning as an attribute to one or more Nodes
dtree[6].trait4 = "special"

# show the data
dtree.get_node_data()
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
      <th>trait1</th>
      <th>trait2</th>
      <th>trait3</th>
      <th>trait4</th>
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
      <td>10</td>
      <td>5</td>
      <td>X</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>b</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
      <td>10</td>
      <td>5</td>
      <td>Y</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>c</td>
      <td>0.0</td>
      <td>3.0</td>
      <td>NaN</td>
      <td>10</td>
      <td>5</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>d</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
      <td>10</td>
      <td>5</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>4</td>
      <td>e</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>NaN</td>
      <td>10</td>
      <td>5</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>5</th>
      <td>5</td>
      <td></td>
      <td>1.0</td>
      <td>3.0</td>
      <td>90.0</td>
      <td>10</td>
      <td>1</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>6</th>
      <td>6</td>
      <td></td>
      <td>1.0</td>
      <td>2.0</td>
      <td>100.0</td>
      <td>10</td>
      <td>1</td>
      <td>NaN</td>
      <td>special</td>
    </tr>
    <tr>
      <th>7</th>
      <td>7</td>
      <td></td>
      <td>3.0</td>
      <td>1.0</td>
      <td>100.0</td>
      <td>10</td>
      <td>1</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>8</th>
      <td>8</td>
      <td></td>
      <td>4.0</td>
      <td>0.0</td>
      <td>NaN</td>
      <td>10</td>
      <td>1</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



## Tree drawings
When you call `.draw()` on a tree it returns three objects: a Canvas, Cartesian axes, and a Mark. This follows the structure of the [Toyplot documentation](https://toyplot.readthedocs.io/) because `toytree` uses Toyplot as its default drawing backend. The canvas holds the figure, the Cartesian object controls the coordinate system, and the mark represents the tree itself.

You can ignore those return values for quick plots, but they become useful when you want to add annotations, adjust axes, or save figures with more control.


```python
# the draw function returns three objects
tree.draw()
```




    (<toyplot.canvas.Canvas at 0x740021477a70>,
     <toyplot.coordinates.Cartesian at 0x7400214cecf0>,
     <toytree.drawing.src.mark_toytree.ToyTreeMark at 0x74002140c320>)




<div class="toyplot" id="t6b01f68069c2472bbbe2b24f484e8ef1" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="td8789b0597444f089191307087278dbf"><g class="toyplot-coordinates-Cartesian" id="tffebad1bc838497dace17f4c756e3add"><clipPath id="t9cdbcb16df4d4193ab0901f5634bda75"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t9cdbcb16df4d4193ab0901f5634bda75)"></g></g><g class="toyplot-coordinates-Cartesian" id="t746bac115aca4d03b9af274848c1d7d3"><clipPath id="t0811dc47664043d5b53f4d171eac3253"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t0811dc47664043d5b53f4d171eac3253)"><g class="toytree-mark-Toytree" id="td3ca49bcf2184f9686892ee0be6f034b"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 184.2 197.8 L 184.2 217.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 184.2 197.8 L 184.2 177.7 L 228.6 177.7" id="5,1" style=""></path><path d="M 95.4 107.4 L 95.4 137.5 L 228.6 137.5" id="7,2" style=""></path><path d="M 184.2 77.2 L 184.2 97.3 L 228.6 97.3" id="6,3" style=""></path><path d="M 184.2 77.2 L 184.2 57.2 L 228.6 57.2" id="6,4" style=""></path><path d="M 51.0 152.6 L 51.0 197.8 L 184.2 197.8" id="8,5" style=""></path><path d="M 95.4 107.4 L 95.4 77.2 L 184.2 77.2" id="7,6" style=""></path><path d="M 51.0 152.6 L 51.0 107.4 L 95.4 107.4" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(228.575,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(228.575,177.672)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(228.575,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(228.575,97.3276)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(228.575,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


Many drawing calls here end with a semicolon. In a notebook this simply hides the textual return value so the rendered figure is easier to read. The figure still displays normally, and if you save the notebook the output is saved with it.


```python
# the semicolon hides the returned text of the Canvas and Cartesian objects
tree.draw();
```


<div class="toyplot" id="tc00bdafa15624ea6b10a12d4d3533cf3" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t214bb1149e3148fd8805c9875f05f766"><g class="toyplot-coordinates-Cartesian" id="t0894fa174b9840179516c7aecc4891be"><clipPath id="ta4923930be004a548269a271fb6948d2"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#ta4923930be004a548269a271fb6948d2)"></g></g><g class="toyplot-coordinates-Cartesian" id="tc127ec2be715442d97e0547d90175f60"><clipPath id="tecc689ec257b45158dd2ce620cea3db0"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tecc689ec257b45158dd2ce620cea3db0)"><g class="toytree-mark-Toytree" id="t8b0dd6d9fe8c46f5a5cf3f4ac8ea830b"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 184.2 197.8 L 184.2 217.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 184.2 197.8 L 184.2 177.7 L 228.6 177.7" id="5,1" style=""></path><path d="M 95.4 107.4 L 95.4 137.5 L 228.6 137.5" id="7,2" style=""></path><path d="M 184.2 77.2 L 184.2 97.3 L 228.6 97.3" id="6,3" style=""></path><path d="M 184.2 77.2 L 184.2 57.2 L 228.6 57.2" id="6,4" style=""></path><path d="M 51.0 152.6 L 51.0 197.8 L 184.2 197.8" id="8,5" style=""></path><path d="M 95.4 107.4 L 95.4 77.2 L 184.2 77.2" id="7,6" style=""></path><path d="M 51.0 152.6 L 51.0 107.4 L 95.4 107.4" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(228.575,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(228.575,177.672)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(228.575,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(228.575,97.3276)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(228.575,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


You can also keep the returned objects and edit them after the initial draw call. This is useful when the main tree layout is correct but you want to tune labels, axes, or other presentation details.


```python
# or, we can store them as variables
canvas, axes, mark = tree.draw(scale_bar=True)

# and then optionally add additional styling
axes.x.label.text = "Time (Mya)"
axes.x.label.style["font-size"] = 14
axes.x.label.offset = 20
```


<div class="toyplot" id="t43f0b5dce0324b05bcd154aaca569c75" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t22ab9c743a90498ca8c76c1f0b4daf31"><g class="toyplot-coordinates-Cartesian" id="tc1d0301ae95048e48556a5ea47ae7e26"><clipPath id="tb9f665dfdf94466bbf44f17e5f0fd34a"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tb9f665dfdf94466bbf44f17e5f0fd34a)"></g><g class="toyplot-coordinates-Axis" id="te30751b48d194c0ba56dbf323cef9604" transform="translate(50.0,225.0)translate(0,15.0)"><line x1="0.9885896200411278" y1="0" x2="178.57528575446858" y2="0" style=""></line><g><line x1="0.9885896200411278" y1="0" x2="0.9885896200411278" y2="-5" style=""></line><line x1="45.385263653647996" y1="0" x2="45.385263653647996" y2="-5" style=""></line><line x1="89.78193768725487" y1="0" x2="89.78193768725487" y2="-5" style=""></line><line x1="134.17861172086174" y1="0" x2="134.17861172086174" y2="-5" style=""></line><line x1="178.57528575446858" y1="0" x2="178.57528575446858" y2="-5" style=""></line></g><g><g transform="translate(0.9885896200411278,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(45.385263653647996,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(89.78193768725487,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(134.17861172086174,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(178.57528575446858,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="t62ad0231aba9441ab3a8dc117111e2a7"><clipPath id="t4ecea2efa10048119602a6f06d45dc92"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t4ecea2efa10048119602a6f06d45dc92)"><g class="toytree-mark-Toytree" id="tbc8705c963f849f8ac49c8eb3ec0f596"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 184.2 197.8 L 184.2 217.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 184.2 197.8 L 184.2 177.7 L 228.6 177.7" id="5,1" style=""></path><path d="M 95.4 107.4 L 95.4 137.5 L 228.6 137.5" id="7,2" style=""></path><path d="M 184.2 77.2 L 184.2 97.3 L 228.6 97.3" id="6,3" style=""></path><path d="M 184.2 77.2 L 184.2 57.2 L 228.6 57.2" id="6,4" style=""></path><path d="M 51.0 152.6 L 51.0 197.8 L 184.2 197.8" id="8,5" style=""></path><path d="M 95.4 107.4 L 95.4 77.2 L 184.2 77.2" id="7,6" style=""></path><path d="M 51.0 152.6 L 51.0 107.4 L 95.4 107.4" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(228.575,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(228.575,177.672)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(228.575,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(228.575,97.3276)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(228.575,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t22ab9c743a90498ca8c76c1f0b4daf31";
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
        })(modules["toyplot.coordinates.Axis"],"te30751b48d194c0ba56dbf323cef9604",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.48257475840000025, "min": -4.0222672}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


## Styling tree drawings
You can style drawings one option at a time, or start from a built-in tree style and then adjust individual settings. The second approach is often easier when you want a coherent look without writing every style argument from scratch.

The examples below show both patterns. For more focused drawing guides, see [drawing basics](drawing-basics.md).


```python
# drawing with pre-built tree_styles
tree.draw(tree_style='c');  # coalescent-style
tree.draw(tree_style='d');  # dark-style

# 'ts' is also a shortcut for tree_style
tree.draw(ts='o');          # umlaut-style
```


<div class="toyplot" id="t2f5414fbb32e4cc3b89eedcb6bc9f44d" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t29d634ded91848639fb9702351d31132"><g class="toyplot-coordinates-Cartesian" id="t4490f08ebcb14aee90917589e1ca2d73"><clipPath id="t9392a5e4e62b49e58046e793cda526e4"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t9392a5e4e62b49e58046e793cda526e4)"></g><g class="toyplot-coordinates-Axis" id="tb92e4cd5e09844cf917fb985fa4d4b72" transform="translate(50.0,250.0)rotate(-90.0)translate(0,-15.0)"><line x1="18.44099959261198" y1="0" x2="195.06185743556875" y2="0" style=""></line><g><line x1="18.44099959261198" y1="0" x2="18.44099959261198" y2="5" style=""></line><line x1="62.596214053351176" y1="0" x2="62.596214053351176" y2="5" style=""></line><line x1="106.75142851409036" y1="0" x2="106.75142851409036" y2="5" style=""></line><line x1="150.90664297482957" y1="0" x2="150.90664297482957" y2="5" style=""></line><line x1="195.06185743556875" y1="0" x2="195.06185743556875" y2="5" style=""></line></g><g><g transform="translate(18.44099959261198,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(62.596214053351176,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(106.75142851409036,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(150.90664297482957,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(195.06185743556875,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="t705c6344654948fea76f576f52c9deed"><clipPath id="t7f71241466444f2f884ac5ea1e14c7d0"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t7f71241466444f2f884ac5ea1e14c7d0)"><g class="toytree-mark-Toytree" id="t6efef38bb6684ca9be5460a415e80c21"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 80.4 187.4 L 57.2 231.6" id="5,0" style=""></path><path d="M 80.4 187.4 L 103.6 231.6" id="5,1" style=""></path><path d="M 184.8 99.1 L 150.0 231.6" id="7,2" style=""></path><path d="M 219.6 187.4 L 196.4 231.6" id="6,3" style=""></path><path d="M 219.6 187.4 L 242.8 231.6" id="6,4" style=""></path><path d="M 132.6 54.9 L 80.4 187.4" id="8,5" style=""></path><path d="M 184.8 99.1 L 219.6 187.4" id="7,6" style=""></path><path d="M 132.6 54.9 L 184.8 99.1" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(57.1653,231.559)"><circle r="3.5"></circle></g><g id="Node-1" transform="translate(103.583,231.559)"><circle r="3.5"></circle></g><g id="Node-2" transform="translate(150,231.559)"><circle r="3.5"></circle></g><g id="Node-3" transform="translate(196.417,231.559)"><circle r="3.5"></circle></g><g id="Node-4" transform="translate(242.835,231.559)"><circle r="3.5"></circle></g><g id="Node-5" transform="translate(80.374,187.404)"><circle r="3.5"></circle></g><g id="Node-6" transform="translate(219.626,187.404)"><circle r="3.5"></circle></g><g id="Node-7" transform="translate(184.813,99.0934)"><circle r="3.5"></circle></g><g id="Node-8" transform="translate(132.594,54.9381)"><circle r="3.5"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(57.1653,231.559)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(103.583,231.559)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(150,231.559)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(196.417,231.559)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(242.835,231.559)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t29d634ded91848639fb9702351d31132";
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
        })(modules["toyplot.coordinates.Axis"],"tb92e4cd5e09844cf917fb985fa4d4b72",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 4.111836, "min": -0.4176403584}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>



<div class="toyplot" id="t5d01b6f1e4f94c40be8fdfe97e23487e" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t3509dfac8cc94f8db77b2e6e8acaff59"><g class="toyplot-coordinates-Cartesian" id="t0c240e18d22e4dfc8140c13897994e6e"><clipPath id="t9a759b57d0fd4ce99dcf377f4af0cdaa"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t9a759b57d0fd4ce99dcf377f4af0cdaa)"></g></g><g class="toyplot-coordinates-Cartesian" id="t7aafb16e5a7746d08ce5c46c3b329237"><clipPath id="t05a497931411433eadc19ad44db793e6"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t05a497931411433eadc19ad44db793e6)"><g class="toytree-mark-Toytree" id="teddd9314456c43f3a0600df4c67a8b88"><g class="toytree-Edges" style="stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 189.3 197.8 L 189.3 217.8 L 235.4 217.8" id="5,0" style=""></path><path d="M 189.3 197.8 L 189.3 177.7 L 235.4 177.7" id="5,1" style=""></path><path d="M 97.1 107.4 L 97.1 137.5 L 235.4 137.5" id="7,2" style=""></path><path d="M 189.3 77.2 L 189.3 97.3 L 235.4 97.3" id="6,3" style=""></path><path d="M 189.3 77.2 L 189.3 57.2 L 235.4 57.2" id="6,4" style=""></path><path d="M 51.0 152.6 L 51.0 197.8 L 189.3 197.8" id="8,5" style=""></path><path d="M 97.1 107.4 L 97.1 77.2 L 189.3 77.2" id="7,6" style=""></path><path d="M 51.0 152.6 L 51.0 107.4 L 97.1 107.4" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:none;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(235.411,217.845)"><text x="8.0" y="3.066" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(235.411,177.672)"><text x="8.0" y="3.066" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(235.411,137.5)"><text x="8.0" y="3.066" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(235.411,97.3276)"><text x="8.0" y="3.066" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(235.411,57.1552)"><text x="8.0" y="3.066" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



<div class="toyplot" id="tfcfba1f540ca41b6bb6485bf3c55eda6" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t437826636d6c42729add8666720fb762"><g class="toyplot-coordinates-Cartesian" id="t45ee7c9f71e34aec883df132432bf4e0"><clipPath id="tef7a16cd321a408c8c381d73bfd8efa3"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tef7a16cd321a408c8c381d73bfd8efa3)"></g></g><g class="toyplot-coordinates-Cartesian" id="t424869bdfcc7471bb0eacdde8cca3892"><clipPath id="ta1a1719d74e44d959291be5c4c9512cf"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#ta1a1719d74e44d959291be5c4c9512cf)"><g class="toytree-mark-Toytree" id="tcf5da8297cb8417aaad9b64b8dc710c4"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 185.4 197.8 L 228.7 217.8" id="5,0" style=""></path><path d="M 185.4 197.8 L 228.7 177.7" id="5,1" style=""></path><path d="M 98.7 107.4 L 228.7 137.5" id="7,2" style=""></path><path d="M 185.4 77.2 L 228.7 97.3" id="6,3" style=""></path><path d="M 185.4 77.2 L 228.7 57.2" id="6,4" style=""></path><path d="M 55.4 152.6 L 185.4 197.8" id="8,5" style=""></path><path d="M 98.7 107.4 L 185.4 77.2" id="7,6" style=""></path><path d="M 55.4 152.6 L 98.7 107.4" id="8,7" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 228.7 217.8 L 228.7 217.8"></path><path d="M 228.7 177.7 L 228.7 177.7"></path><path d="M 228.7 137.5 L 228.7 137.5"></path><path d="M 228.7 97.3 L 228.7 97.3"></path><path d="M 228.7 57.2 L 228.7 57.2"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(185.359,197.759)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(185.359,77.2414)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(98.7277,107.371)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(55.4121,152.565)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(228.675,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(228.675,177.672)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(228.675,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(228.675,97.3276)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(228.675,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# define a style dictionary
mystyle = {
    "layout": 'd',
    "edge_type": 'p',
    "edge_style": {
        "stroke": "darkcyan",
        "stroke-width": 2.5,
    },
    "tip_labels_colors": "black",
    "tip_labels_style": {
        "font-size": "16px"
    },
    "node_sizes": 8,
    "node_colors": "dist",
    "node_labels": "support",
    "node_labels_style": {"baseline-shift": 12, "anchor-shift": 15, "font-size": 12},
    "node_mask": (0, 1, 0),
}

# use your custom style dictionary in one or more tree drawings
tree.draw(height=300, **mystyle);
```


<div class="toyplot" id="tfdb2f655167b477c82b9029a9c3ba0a2" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tff7b50dd1e8f46b883a038a24cdb6712"><g class="toyplot-coordinates-Cartesian" id="t9c51a30ba38e4dd993fb9e2cfd2fe066"><clipPath id="t952bed7a06664c048bd6520b5b07e2dd"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t952bed7a06664c048bd6520b5b07e2dd)"></g></g><g class="toyplot-coordinates-Cartesian" id="t14139ff1a62e4c2dac66791a48afa432"><clipPath id="tccc5ca06c877418d9f82a9732ff05ee0"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#tccc5ca06c877418d9f82a9732ff05ee0)"><g class="toytree-mark-Toytree" id="t00d774d6847443e5b2b09c5baed828d0"><g class="toytree-Edges" style="stroke:rgb(0.0%,54.5%,54.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.5;fill:none"><path d="M 80.3 183.9 L 59.6 183.9 L 59.6 226.2" id="5,0" style=""></path><path d="M 80.3 183.9 L 100.9 183.9 L 100.9 226.2" id="5,1" style=""></path><path d="M 173.4 99.4 L 142.3 99.4 L 142.3 226.2" id="7,2" style=""></path><path d="M 204.4 183.9 L 183.7 183.9 L 183.7 226.2" id="6,3" style=""></path><path d="M 204.4 183.9 L 225.1 183.9 L 225.1 226.2" id="6,4" style=""></path><path d="M 126.8 57.2 L 80.3 57.2 L 80.3 183.9" id="8,5" style=""></path><path d="M 173.4 99.4 L 204.4 99.4 L 204.4 183.9" id="7,6" style=""></path><path d="M 126.8 57.2 L 173.4 57.2 L 173.4 99.4" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" style="fill:rgb(62.0%,0.4%,25.9%)" transform="translate(80.2514,183.929)"><circle r="4.0"></circle></g><g id="Node-6" style="fill:rgb(99.3%,74.8%,43.5%)" transform="translate(204.407,183.929)"><circle r="4.0"></circle></g><g id="Node-7" style="fill:rgb(74.8%,89.8%,62.7%)" transform="translate(173.368,99.4278)"><circle r="4.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(80.2514,183.929)"><text x="8.328" y="-8.934000000000001" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">90</text></g><g class="toytree-NodeLabel" transform="translate(204.407,183.929)"><text x="4.992000000000001" y="-8.934000000000001" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">100</text></g><g class="toytree-NodeLabel" transform="translate(173.368,99.4278)"><text x="4.992000000000001" y="-8.934000000000001" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">100</text></g></g><g class="toytree-TipLabels" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:1.0;font-family:Helvetica;font-size:16px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(59.5588,226.18)rotate(90)"><text x="15.0" y="4.087999999999999" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(100.944,226.18)rotate(90)"><text x="15.0" y="4.087999999999999" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(142.329,226.18)rotate(90)"><text x="15.0" y="4.087999999999999" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(183.714,226.18)rotate(90)"><text x="15.0" y="4.087999999999999" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(225.099,226.18)rotate(90)"><text x="15.0" y="4.087999999999999" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Saving tree drawings
Figures can be saved as HTML, SVG, PDF, or PNG. In most cases `toytree.save()` is the easiest entry point because the output format is inferred from the file suffix. If you already work directly with Toyplot objects, you can also save through Toyplot itself.


```python
# draw a plot and store the Canvas object to a variable
canvas, axes, mark = tree.draw(ts='p');
```


<div class="toyplot" id="t64b9ceb9811b40f8a141eb100ee4b799" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t83888816ba6b40f6810866e64b4589d5"><g class="toyplot-coordinates-Cartesian" id="t55ef99855caf4efa8a71349dfd9aa389"><clipPath id="ted1304473f484204aa1fe99ca7464d0e"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#ted1304473f484204aa1fe99ca7464d0e)"></g><g class="toyplot-coordinates-Axis" id="tfca4293e8b6e4a33ad58055bd452954f" transform="translate(50.0,250.0)rotate(-90.0)translate(0,-15.0)"><line x1="21.251737960916266" y1="0" x2="191.66483145682045" y2="0" style=""></line><g><line x1="21.251737960916266" y1="0" x2="21.251737960916266" y2="5" style=""></line><line x1="63.85501133489231" y1="0" x2="63.85501133489231" y2="5" style=""></line><line x1="106.45828470886836" y1="0" x2="106.45828470886836" y2="5" style=""></line><line x1="149.0615580828444" y1="0" x2="149.0615580828444" y2="5" style=""></line><line x1="191.66483145682045" y1="0" x2="191.66483145682045" y2="5" style=""></line></g><g><g transform="translate(21.251737960916266,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(63.85501133489231,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(106.45828470886836,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(149.0615580828444,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(191.66483145682045,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="t3a57504c24a84087bcfc20011c88c575"><clipPath id="tccdee2c942494a8aa0ecfd9a3ad21880"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#tccdee2c942494a8aa0ecfd9a3ad21880)"><g class="toytree-mark-Toytree" id="t369768633ec84bb1b75c97944708d52e"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 81.3 186.1 L 58.4 228.7" id="5,0" style=""></path><path d="M 81.3 186.1 L 104.2 228.7" id="5,1" style=""></path><path d="M 184.3 100.9 L 150.0 228.7" id="7,2" style=""></path><path d="M 218.7 186.1 L 195.8 228.7" id="6,3" style=""></path><path d="M 218.7 186.1 L 241.6 228.7" id="6,4" style=""></path><path d="M 132.8 58.3 L 81.3 186.1" id="8,5" style=""></path><path d="M 184.3 100.9 L 218.7 186.1" id="7,6" style=""></path><path d="M 132.8 58.3 L 184.3 100.9" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.0"><g id="Node-0" transform="translate(58.4438,228.748)"><circle r="7.5"></circle></g><g id="Node-1" transform="translate(104.222,228.748)"><circle r="7.5"></circle></g><g id="Node-2" transform="translate(150,228.748)"><circle r="7.5"></circle></g><g id="Node-3" transform="translate(195.778,228.748)"><circle r="7.5"></circle></g><g id="Node-4" transform="translate(241.556,228.748)"><circle r="7.5"></circle></g><g id="Node-5" transform="translate(81.3328,186.145)"><circle r="7.5"></circle></g><g id="Node-6" transform="translate(218.667,186.145)"><circle r="7.5"></circle></g><g id="Node-7" transform="translate(184.334,100.938)"><circle r="7.5"></circle></g><g id="Node-8" transform="translate(132.833,58.3352)"><circle r="7.5"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(58.4438,228.748)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(104.222,228.748)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(150,228.748)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(195.778,228.748)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(241.556,228.748)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(81.3328,186.145)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(218.667,186.145)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(184.334,100.938)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(132.833,58.3352)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(58.4438,228.748)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(104.222,228.748)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(150,228.748)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(195.778,228.748)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(241.556,228.748)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t83888816ba6b40f6810866e64b4589d5";
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
        })(modules["toyplot.coordinates.Axis"],"tfca4293e8b6e4a33ad58055bd452954f",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 4.195646199999999, "min": -0.4988287584000003}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


HTML is the default save format. It preserves vector graphics and can also preserve interactive behavior, which makes it a good choice for sharing in a browser or embedding on a website.


```python
# HTML allows for interactivity and embedding in web sites
toytree.save(canvas, "/tmp/tree-plot.html")
```


```python
# SVG for figures you will further edit in Illustrator/Inkscape
toytree.save(canvas, "/tmp/tree-plot.svg")
```


```python
# PDF for final shareable figures
toytree.save(canvas, "/tmp/tree-plot.pdf")
```


```python
# PNG for small and easy to share figures 
toytree.save(canvas, "/tmp/tree-plot.png")
```

Toyplot also exposes lower-level save functions. `toytree.save()` is mainly a convenience wrapper around that functionality, so you can stay in the `toytree` API for common cases.


```python
import toyplot
toyplot.html.render(canvas, "/tmp/tree-plot.html")
```


```python
import toyplot.svg
toyplot.svg.render(canvas, "/tmp/tree-plot.svg")
```


```python
import toyplot.pdf
toyplot.pdf.render(canvas, "/tmp/tree-plot.pdf")
```


```python
import toyplot.png
toyplot.png.render(canvas, "/tmp/tree-plot.png")
```
