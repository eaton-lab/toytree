<div class="nb-md-page-hook" aria-hidden="true"></div>

# MultiTree

The `toytree.MultiTree` class object is used to represent a collection of `ToyTree` objects and includes attributes and methods for describing this set or performing operations on it. Common examples of tree sets include bootstrap replicate samples or posterior distributions of sampled trees; common operations on sets of trees include *consensus tree inference*, computing discordance or distance statistics, and plotting tree grids or cloud trees.


```python
import toytree
```

## Generating MultiTrees

MultiTree objects can be generated from a list of Toytrees or newick strings, or by parsing a file, url, or string of text that includes newick trees separated by newlines. The convenience function `toytree.mtree()` can be used to parse multitree input data similar to how the function `toytree.tree` is used to parse individual trees, and supports the same file formats.

### From tree data
Below is an example multi-newick string representing multiple trees as newick strings separated by newlines. You can create a MultiTree from this input data, entered as a string or filepath, by passing it to the `toytree.mtree()` convenience parsing function. Each tree will be parsed individually and stored as a list of `ToyTree` objects contained within a returned `MultiTree` object.


```python
multinewick = """\
(((a:1,b:1):1,(d:1.5,e:1.5):0.5):1,c:3);
(((a:1,d:1):1,(b:1,e:1):1):1,c:3);
(((a:1.5,b:1.5):1,(d:1,e:1):1.5):1,c:3.5);
(((a:1.25,b:1.25):0.75,(d:1,e:1):1):1,c:3);
(((a:1,b:1):1,(d:1.5,e:1.5):0.5):1,c:3);
(((b:1,a:1):1,(d:1.5,e:1.5):0.5):2,c:4);
(((a:1.5,b:1.5):0.5,(d:1,e:1):1):1,c:3);
(((b:1.5,d:1.5):0.5,(a:1,e:1):1):1,c:3);
"""
```


```python
# create an mtree from a string, list of strings, url, or file.
mtree1 = toytree.mtree(multinewick)
mtree1
```




    <toytree.MultiTree ntrees=8>



### From a collection of trees
Similarly, you can create a `MultiTree` by providing a collection of `ToyTree` objects to the `toytree.mtree` function. Here we generate a list of 50 random coalescent trees and pass the list as input to create a new `MultiTree`.


```python
# generate 50 random coalescent trees each with 6 tips
coaltrees = [toytree.rtree.coaltree(k=6) for i in range(50)]
```


```python
# create a MultiTree from a list of ToyTrees
mtree2 = toytree.mtree(coaltrees)
mtree2
```




    <toytree.MultiTree ntrees=50>



## Indexable and Iterable
One or more trees can be indexed or sliced from a `MultiTree`, and sequential trees can be accessed through iteration. The trees themselves are stored in the `.treelist` attribute of the `MultiTree` object as a list. This can be modified to remove, add, or reorder the trees. Several example operations are shown below for accessing one or more trees.


```python
# get first tree
mtree1[0]
```




    <toytree.ToyTree at 0x7144b24aee70>




```python
# get all trees
mtree1[:]
```




    [<toytree.ToyTree at 0x7144b24aee70>,
     <toytree.ToyTree at 0x7144b24de660>,
     <toytree.ToyTree at 0x7144b24de900>,
     <toytree.ToyTree at 0x7144b24ded50>,
     <toytree.ToyTree at 0x7144b24df020>,
     <toytree.ToyTree at 0x7144b24df2f0>,
     <toytree.ToyTree at 0x7144b24df5c0>,
     <toytree.ToyTree at 0x7144b24df890>]




```python
# slice the first three trees
mtree1[:3]
```




    [<toytree.ToyTree at 0x7144b24aee70>,
     <toytree.ToyTree at 0x7144b24de660>,
     <toytree.ToyTree at 0x7144b24de900>]




```python
# iterate over ToyTrees in a MultiTree
for tree in mtree1:
    print(tree)
```

    <toytree.ToyTree at 0x7144b24aee70>
    <toytree.ToyTree at 0x7144b24de660>
    <toytree.ToyTree at 0x7144b24de900>
    <toytree.ToyTree at 0x7144b24ded50>
    <toytree.ToyTree at 0x7144b24df020>
    <toytree.ToyTree at 0x7144b24df2f0>
    <toytree.ToyTree at 0x7144b24df5c0>
    <toytree.ToyTree at 0x7144b24df890>



```python
# re-arrange trees in the treelist to send the first to be last
mtree1.treelist = mtree1.treelist[1:] + [mtree1.treelist[0]]
mtree1[:]
```




    [<toytree.ToyTree at 0x7144b24de660>,
     <toytree.ToyTree at 0x7144b24de900>,
     <toytree.ToyTree at 0x7144b24ded50>,
     <toytree.ToyTree at 0x7144b24df020>,
     <toytree.ToyTree at 0x7144b24df2f0>,
     <toytree.ToyTree at 0x7144b24df5c0>,
     <toytree.ToyTree at 0x7144b24df890>,
     <toytree.ToyTree at 0x7144b24aee70>]



## Attributes and types of tree sets
Most of the time `MultiTree` objects are used to hold a collection of trees that all share the same tip labels, such as a collection of bootstrap replicates. But, in other cases, a `MultiTree` could hold a collection of unrelated trees, in which case some of the built-in functions for comparing trees (such as consensus tree inference) will raise an error, but it still provides a useful container for drawing trees. These methods will raise a ToyTreeError when attempted if the tree set is a mixed collection of trees. The  `MultiTree` class contains several functions to quickly check attributes of the tree set to examine the number of trees, whether they share the same tip names, and whether the trees are rooted or ultrametric.


```python
mtree1.ntrees
```




    8




```python
mtree1.all_tree_tip_labels_same()
```




    True




```python
mtree1.all_tree_topologies_same()
```




    False




```python
mtree1.all_tree_tips_aligned()
```




    False



## Consensus trees
For a full parameter and output-field reference see: [Inference: Consensus Trees](/toytree/infer-consensus/).

A majority-rule consensus tree summarizes the most common non-conflicting splits among a set of input trees. A consensus tree can be inferred from `MultiTree.get_consensus_tree(min_freq=...)`. The returned `ToyTree` is unrooted and stores split support scores in the "support" feature, and edge distance summaries (e.g., `dist_mean`, `dist_std`). There are additional options to summarize other feature data from the set of input trees onto the consensus tree.


```python
# get a consensus tree 
ctree = mtree1.get_consensus_tree()

# plot the unrooted tree showing 'support' values
c, a, m = ctree.draw(layout='unr', height=350)
ctree.annotate.add_edge_labels(a, "support", color="grey");
```


<div class="toyplot" id="t80ad832325d246cabd27de5729c25c2d" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="314.0px" height="350.0px" viewBox="0 0 314.0 350.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t03af1e88327f494bada56b95bb559783"><g class="toyplot-coordinates-Cartesian" id="tf0cfb597bb99486fb83d8bbb9f737509"><clipPath id="t428e582ffdc243f197480b5bc2e7b6e5"><rect x="35.0" y="35.0" width="244.0" height="280.0"></rect></clipPath><g clip-path="url(#t428e582ffdc243f197480b5bc2e7b6e5)"></g></g><g class="toyplot-coordinates-Cartesian" id="ta581819a3d714dc2b591a2d3ddd7d094"><clipPath id="te008db70669d4925a1fc495238daba6f"><rect x="35.0" y="35.0" width="244.0" height="280.0"></rect></clipPath><g clip-path="url(#te008db70669d4925a1fc495238daba6f)"><g class="toytree-mark-Toytree" id="td5888882530949c881686790f4152831"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 199.0 138.6 L 241.5 164.0" id="5,0" style=""></path><path d="M 199.0 138.6 L 238.5 107.5" id="5,1" style=""></path><path d="M 127.7 117.2 L 127.2 72.7" id="6,2" style=""></path><path d="M 127.7 117.2 L 72.7 113.1" id="6,3" style=""></path><path d="M 158.5 135.2 L 85.0 277.9" id="7,4" style=""></path><path d="M 158.5 135.2 L 199.0 138.6" id="7,5" style=""></path><path d="M 158.5 135.2 L 127.7 117.2" id="7,6" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(241.463,163.964)rotate(24.4322)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(238.514,107.482)rotate(-24.4123)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(127.192,72.7046)rotate(69.0544)"><text x="-21.672" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(72.6629,113.132)rotate(18.6055)"><text x="-21.672" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(85.0089,277.928)rotate(111.466)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g><g class="toyplot-mark-Text" id="td14d85fe79dd45afb9075c42edb1b65e"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(178.78096357640442,136.9153847931795)"><text x="-11.676" y="3.066" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0.75</text></g><g class="toyplot-Datum" transform="translate(143.12682160079243,126.17806803198243)"><text x="-11.676" y="3.066" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0.75</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Unique trees
Given a set of trees it is useful to be able to pull out just the unique topologies from the set. The function `get_unique_topologies()` returns a list of `(tree, int)` tuples from a `MultiTree` with each unique topology paired with its number of occurrences in the set. Note, this condenses all trees with the same topology into a single representative, using the first occurrence as the returned tree, thus branch length variation is not retained.


```python
# get (tree, count) for each unique topology in the MultiTree
mtree1.get_unique_topologies()
```




    [(<toytree.ToyTree at 0x7144b24de900>, 6),
     (<toytree.ToyTree at 0x7144b24de660>, 1),
     (<toytree.ToyTree at 0x7144b24df890>, 1)]



## Drawing with MultiTrees

### Grid tree drawings
See [MultiTree.draw()](drawing-multitree-grids) for a detailed description of MultiTree grid drawings.

The `MultiTree.draw()` method returns a drawing with multiple trees displayed on a grid. The `shape` and `idxs` arguments can be used to designate the grid layout and select which trees to show. All standard tree drawing style arguments are accepted. The `fixed_order` argument is often useful in this context to fix the order of tips to emphasize discordance among trees in a set.


```python
# draw a 2x4 grid of trees 8 trees from a collection
mtree1.draw(ts='o', shape=(2, 4), width=600, height=300, fixed_order=['c', 'b', 'e', 'a', 'd']);
```


<div class="toyplot" id="t9f7836da23d04663a10dd1ea0dcebe2d" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="600.0px" height="300.0px" viewBox="0 0 600.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t03c73852a1424308b47395ac04fb8954"><g class="toyplot-coordinates-Cartesian" id="tafab2969c0b44ca6bd9b0df1cbe82cd4"><clipPath id="tf9b55cbcb78e4d7990d57893b4e2fca6"><rect x="20.0" y="30.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#tf9b55cbcb78e4d7990d57893b4e2fca6)"></g></g><g class="toyplot-coordinates-Cartesian" id="t919272fc843247c1857b786c22828f7e"><clipPath id="td5478e0f96ad4df19f956b78361a618a"><rect x="20.0" y="30.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#td5478e0f96ad4df19f956b78361a618a)"><g class="toytree-mark-Toytree" id="td39ca99a8d964440b3b6cdd2cb6f9d33"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 81.5 55.7 L 104.6 65.5" id="5,0" style=""></path><path d="M 81.5 55.7 L 104.6 46.0" id="5,1" style=""></path><path d="M 81.5 94.8 L 104.6 104.5" id="6,2" style=""></path><path d="M 81.5 94.8 L 104.6 85.0" id="6,3" style=""></path><path d="M 35.4 99.6 L 104.6 124.0" id="8,4" style=""></path><path d="M 58.5 75.2 L 81.5 55.7" id="7,5" style=""></path><path d="M 58.5 75.2 L 81.5 94.8" id="7,6" style=""></path><path d="M 35.4 99.6 L 58.5 75.2" id="8,7" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 104.6 65.5 L 104.6 65.5"></path><path d="M 104.6 46.0 L 104.6 46.0"></path><path d="M 104.6 104.5 L 104.6 104.5"></path><path d="M 104.6 85.0 L 104.6 85.0"></path><path d="M 104.6 124.0 L 104.6 124.0"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(81.5441,55.7408)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(81.5441,94.7531)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(58.495,75.2469)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(35.4459,99.6296)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(104.593,65.4938)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(104.593,45.9877)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(104.593,104.506)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(104.593,85)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(104.593,124.012)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t83acf1d88b504751b026814ebc237894"><clipPath id="te794d12334154123bbfd6a85d32c87c8"><rect x="170.0" y="30.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#te794d12334154123bbfd6a85d32c87c8)"></g></g><g class="toyplot-coordinates-Cartesian" id="t83d9c203251e4a8ba075faa3eda920cf"><clipPath id="tdc601bf63a724df899c787c55f8d01ec"><rect x="170.0" y="30.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#tdc601bf63a724df899c787c55f8d01ec)"><g class="toytree-mark-Toytree" id="td118926f7e6f402087b055d1e3ccc6c5"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 225.0 85.0 L 254.6 65.5" id="5,0" style=""></path><path d="M 225.0 85.0 L 254.6 104.5" id="5,1" style=""></path><path d="M 234.8 65.5 L 254.6 46.0" id="6,2" style=""></path><path d="M 234.8 65.5 L 254.6 85.0" id="6,3" style=""></path><path d="M 185.4 99.6 L 254.6 124.0" id="8,4" style=""></path><path d="M 205.2 75.2 L 225.0 85.0" id="7,5" style=""></path><path d="M 205.2 75.2 L 234.8 65.5" id="7,6" style=""></path><path d="M 185.4 99.6 L 205.2 75.2" id="8,7" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 254.6 65.5 L 254.6 65.5"></path><path d="M 254.6 104.5 L 254.6 104.5"></path><path d="M 254.6 46.0 L 254.6 46.0"></path><path d="M 254.6 85.0 L 254.6 85.0"></path><path d="M 254.6 124.0 L 254.6 124.0"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(224.959,85)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(234.837,65.4938)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(205.202,75.2469)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(185.446,99.6296)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(254.593,65.4938)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(254.593,104.506)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(254.593,45.9877)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(254.593,85)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(254.593,124.012)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t0ce5062c10984895abdc49250e714d80"><clipPath id="tf375a0a00c324fb2ab8fb12ebdbd5670"><rect x="320.0" y="30.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#tf375a0a00c324fb2ab8fb12ebdbd5670)"></g></g><g class="toyplot-coordinates-Cartesian" id="t929fb58e706d4a9e9c018cd6559a0da8"><clipPath id="t3198dd76631f425a99a5e4e1ac3fd4ae"><rect x="320.0" y="30.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#t3198dd76631f425a99a5e4e1ac3fd4ae)"><g class="toytree-mark-Toytree" id="td7e14e17e89e4a059790c790f24a59ed"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 375.8 85.0 L 404.6 65.5" id="5,0" style=""></path><path d="M 375.8 85.0 L 404.6 104.5" id="5,1" style=""></path><path d="M 381.5 65.5 L 404.6 46.0" id="6,2" style=""></path><path d="M 381.5 65.5 L 404.6 85.0" id="6,3" style=""></path><path d="M 335.4 99.6 L 404.6 124.0" id="8,4" style=""></path><path d="M 358.5 75.2 L 375.8 85.0" id="7,5" style=""></path><path d="M 358.5 75.2 L 381.5 65.5" id="7,6" style=""></path><path d="M 335.4 99.6 L 358.5 75.2" id="8,7" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 404.6 65.5 L 404.6 65.5"></path><path d="M 404.6 104.5 L 404.6 104.5"></path><path d="M 404.6 46.0 L 404.6 46.0"></path><path d="M 404.6 85.0 L 404.6 85.0"></path><path d="M 404.6 124.0 L 404.6 124.0"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(375.782,85)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(381.544,65.4938)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(358.495,75.2469)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(335.446,99.6296)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(404.593,65.4938)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(404.593,104.506)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(404.593,45.9877)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(404.593,85)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(404.593,124.012)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t12e39c6004624cebac3c0d970657559b"><clipPath id="t05c33b3d9ce44d5893ba6e8b739eceb8"><rect x="470.0" y="30.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#t05c33b3d9ce44d5893ba6e8b739eceb8)"></g></g><g class="toyplot-coordinates-Cartesian" id="t0744c5d37408410bba078171842d75d0"><clipPath id="t376675070c8e49d09e90f0774383014a"><rect x="470.0" y="30.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#t376675070c8e49d09e90f0774383014a)"><g class="toytree-mark-Toytree" id="t0c568ec6d41a40c1987631fd39084903"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 531.5 85.0 L 554.6 65.5" id="5,0" style=""></path><path d="M 531.5 85.0 L 554.6 104.5" id="5,1" style=""></path><path d="M 520.0 65.5 L 554.6 46.0" id="6,2" style=""></path><path d="M 520.0 65.5 L 554.6 85.0" id="6,3" style=""></path><path d="M 485.4 99.6 L 554.6 124.0" id="8,4" style=""></path><path d="M 508.5 75.2 L 531.5 85.0" id="7,5" style=""></path><path d="M 508.5 75.2 L 520.0 65.5" id="7,6" style=""></path><path d="M 485.4 99.6 L 508.5 75.2" id="8,7" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 554.6 65.5 L 554.6 65.5"></path><path d="M 554.6 104.5 L 554.6 104.5"></path><path d="M 554.6 46.0 L 554.6 46.0"></path><path d="M 554.6 85.0 L 554.6 85.0"></path><path d="M 554.6 124.0 L 554.6 124.0"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(531.544,85)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(520.02,65.4938)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(508.495,75.2469)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(485.446,99.6296)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(554.593,65.4938)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(554.593,104.506)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(554.593,45.9877)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(554.593,85)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(554.593,124.012)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t147e00b798d8418eb817b6e345ab7fd0"><clipPath id="t04fa1ba2db1f4f559ecf1ac4d3cef328"><rect x="20.0" y="160.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#t04fa1ba2db1f4f559ecf1ac4d3cef328)"></g></g><g class="toyplot-coordinates-Cartesian" id="tce6cf033ba234ad18e893dd743a651d6"><clipPath id="t5a261ab12d284ca0b10a510e0962c65b"><rect x="20.0" y="160.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#t5a261ab12d284ca0b10a510e0962c65b)"><g class="toytree-mark-Toytree" id="tcd5a4cf3f743455ab5fc1ab56ef16b54"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 87.3 215.0 L 104.6 234.5" id="5,0" style=""></path><path d="M 87.3 215.0 L 104.6 195.5" id="5,1" style=""></path><path d="M 78.7 195.5 L 104.6 176.0" id="6,2" style=""></path><path d="M 78.7 195.5 L 104.6 215.0" id="6,3" style=""></path><path d="M 35.4 229.6 L 104.6 254.0" id="8,4" style=""></path><path d="M 70.0 205.2 L 87.3 215.0" id="7,5" style=""></path><path d="M 70.0 205.2 L 78.7 195.5" id="7,6" style=""></path><path d="M 35.4 229.6 L 70.0 205.2" id="8,7" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 104.6 234.5 L 104.6 234.5"></path><path d="M 104.6 195.5 L 104.6 195.5"></path><path d="M 104.6 176.0 L 104.6 176.0"></path><path d="M 104.6 215.0 L 104.6 215.0"></path><path d="M 104.6 254.0 L 104.6 254.0"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(87.3063,215)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(78.6629,195.494)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(70.0195,205.247)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(35.4459,229.63)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(104.593,234.506)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(104.593,195.494)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(104.593,175.988)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(104.593,215)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(104.593,254.012)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t842119a44de747e58029242cac5c7ed2"><clipPath id="tbbb4e5248e054b20bcad9379cc4ffeeb"><rect x="170.0" y="160.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#tbbb4e5248e054b20bcad9379cc4ffeeb)"></g></g><g class="toyplot-coordinates-Cartesian" id="t000e4adf89f24000b1c48623b201a8e8"><clipPath id="tbcbb38098e964b8398b907ac516e58f1"><rect x="170.0" y="160.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#tbcbb38098e964b8398b907ac516e58f1)"><g class="toytree-mark-Toytree" id="t9857af0be9b6469596adda20f99d4d7a"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 220.0 215.0 L 254.6 195.5" id="5,0" style=""></path><path d="M 220.0 215.0 L 254.6 234.5" id="5,1" style=""></path><path d="M 231.5 195.5 L 254.6 176.0" id="6,2" style=""></path><path d="M 231.5 195.5 L 254.6 215.0" id="6,3" style=""></path><path d="M 185.4 229.6 L 254.6 254.0" id="8,4" style=""></path><path d="M 208.5 205.2 L 220.0 215.0" id="7,5" style=""></path><path d="M 208.5 205.2 L 231.5 195.5" id="7,6" style=""></path><path d="M 185.4 229.6 L 208.5 205.2" id="8,7" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 254.6 195.5 L 254.6 195.5"></path><path d="M 254.6 234.5 L 254.6 234.5"></path><path d="M 254.6 176.0 L 254.6 176.0"></path><path d="M 254.6 215.0 L 254.6 215.0"></path><path d="M 254.6 254.0 L 254.6 254.0"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(220.02,215)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(231.544,195.494)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(208.495,205.247)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(185.446,229.63)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(254.593,195.494)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(254.593,234.506)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(254.593,175.988)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(254.593,215)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(254.593,254.012)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t9ed41bb10dee4616822220161fe8c412"><clipPath id="ta3ef69905ff24278ad88d9a1316f7968"><rect x="320.0" y="160.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#ta3ef69905ff24278ad88d9a1316f7968)"></g></g><g class="toyplot-coordinates-Cartesian" id="t811e2564c5fd4137bf20f35699accff3"><clipPath id="t1ddc75233db34d0db335471a5b458765"><rect x="320.0" y="160.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#t1ddc75233db34d0db335471a5b458765)"><g class="toytree-mark-Toytree" id="te730629c9c7b4d0fbac5a2e92ea05a72"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 370.0 205.2 L 404.6 234.5" id="5,0" style=""></path><path d="M 370.0 205.2 L 404.6 176.0" id="5,1" style=""></path><path d="M 381.5 205.2 L 404.6 195.5" id="6,2" style=""></path><path d="M 381.5 205.2 L 404.6 215.0" id="6,3" style=""></path><path d="M 335.4 229.6 L 404.6 254.0" id="8,4" style=""></path><path d="M 358.5 205.2 L 370.0 205.2" id="7,5" style=""></path><path d="M 358.5 205.2 L 381.5 205.2" id="7,6" style=""></path><path d="M 335.4 229.6 L 358.5 205.2" id="8,7" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 404.6 234.5 L 404.6 234.5"></path><path d="M 404.6 176.0 L 404.6 176.0"></path><path d="M 404.6 195.5 L 404.6 195.5"></path><path d="M 404.6 215.0 L 404.6 215.0"></path><path d="M 404.6 254.0 L 404.6 254.0"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(370.02,205.247)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(381.544,205.247)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(358.495,205.247)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(335.446,229.63)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(404.593,234.506)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(404.593,175.988)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(404.593,195.494)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(404.593,215)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(404.593,254.012)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t26a8b3051eb849eca74655474705abf4"><clipPath id="tfe602aa51d7045fdb64268bf0aca0cb3"><rect x="470.0" y="160.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#tfe602aa51d7045fdb64268bf0aca0cb3)"></g></g><g class="toyplot-coordinates-Cartesian" id="t7b1222730a47428db8db81b15ce262cf"><clipPath id="tf548875316a14605b75ba72852ef1eb3"><rect x="470.0" y="160.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#tf548875316a14605b75ba72852ef1eb3)"><g class="toytree-mark-Toytree" id="ta3f0d23a862f4d1a9833015b403a8434"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 531.5 215.0 L 554.6 195.5" id="5,0" style=""></path><path d="M 531.5 215.0 L 554.6 234.5" id="5,1" style=""></path><path d="M 520.0 195.5 L 554.6 176.0" id="6,2" style=""></path><path d="M 520.0 195.5 L 554.6 215.0" id="6,3" style=""></path><path d="M 485.4 229.6 L 554.6 254.0" id="8,4" style=""></path><path d="M 508.5 205.2 L 531.5 215.0" id="7,5" style=""></path><path d="M 508.5 205.2 L 520.0 195.5" id="7,6" style=""></path><path d="M 485.4 229.6 L 508.5 205.2" id="8,7" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 554.6 195.5 L 554.6 195.5"></path><path d="M 554.6 234.5 L 554.6 234.5"></path><path d="M 554.6 176.0 L 554.6 176.0"></path><path d="M 554.6 215.0 L 554.6 215.0"></path><path d="M 554.6 254.0 L 554.6 254.0"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(531.544,215)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(520.02,195.494)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(508.495,205.247)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(485.446,229.63)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(554.593,195.494)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(554.593,234.506)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(554.593,175.988)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(554.593,215)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(554.593,254.012)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


### Cloud tree drawings
See [MultiTree.draw_cloud_tree()](drawing-multitree-cloud-trees) for a detailed description of MultiTree cloud tree drawings.

It is sometimes even more informative to plot a number of trees on top of each other to visualize their discordance. These are sometimes called “densitree” plots, or here, “cloud tree plots”.


```python
# draw a cloud tree
mtree1.draw_cloud_tree(
    scale_bar=True,
    edge_style={
        "stroke-opacity": 0.1,
        "stroke-width": 3,
    },
);
```


<div class="toyplot" id="t2872935925904ae3bc599d9fc00aaca1" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="td92a629f8e964a3dbb3ee38fb10e4127"><g class="toyplot-coordinates-Cartesian" id="t4326462135014f2a9a008efcf1329f09"><clipPath id="tcabfd26e9dcb4bedb8047f239cc47b6c"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tcabfd26e9dcb4bedb8047f239cc47b6c)"></g><g class="toyplot-coordinates-Axis" id="tf3a512a4763249c49871994f77243138" transform="translate(50.0,225.0)translate(0,15.0)"><line x1="0" y1="0" x2="200.0" y2="0" style=""></line><g><line x1="1.482169837163175" y1="0" x2="1.482169837163175" y2="-5" style=""></line><line x1="45.758029926038944" y1="0" x2="45.758029926038944" y2="-5" style=""></line><line x1="90.0338900149147" y1="0" x2="90.0338900149147" y2="-5" style=""></line><line x1="134.30975010379046" y1="0" x2="134.30975010379046" y2="-5" style=""></line><line x1="178.58561019266625" y1="0" x2="178.58561019266625" y2="-5" style=""></line></g><g><g transform="translate(1.482169837163175,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(45.758029926038944,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(90.0338900149147,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(134.30975010379046,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(178.58561019266625,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="tcf741245f32a4934b094b9535099866a"><clipPath id="t6e7520cdebce4c74bd82723c9932c465"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t6e7520cdebce4c74bd82723c9932c465)"><g class="toytree-mark-Toytree" id="te9740448fb7d497cae3dc1e903386e74"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:3;fill:none"><path d="M 184.3 177.7 L 228.6 217.8" id="5,0" style=""></path><path d="M 184.3 177.7 L 228.6 137.5" id="5,1" style=""></path><path d="M 184.3 137.5 L 228.6 177.7" id="6,2" style=""></path><path d="M 184.3 137.5 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.8 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 140.0 157.6 L 184.3 177.7" id="7,5" style=""></path><path d="M 140.0 157.6 L 184.3 137.5" id="7,6" style=""></path><path d="M 95.8 137.5 L 140.0 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(228.586,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(228.586,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(228.586,177.672)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(228.586,97.3276)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(228.586,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g><g class="toytree-mark-Toytree" id="t466f37d6806348d3a8c5f0f973ee7234"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:3;fill:none"><path d="M 162.2 197.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 162.2 197.8 L 228.6 177.7" id="5,1" style=""></path><path d="M 184.3 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 184.3 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 73.6 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 117.9 157.6 L 162.2 197.8" id="7,5" style=""></path><path d="M 117.9 157.6 L 184.3 117.4" id="7,6" style=""></path><path d="M 73.6 137.5 L 117.9 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t5a53489a242c4abd93307a0d0372b66b"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:3;fill:none"><path d="M 173.2 197.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 173.2 197.8 L 228.6 177.7" id="5,1" style=""></path><path d="M 184.3 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 184.3 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.8 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 140.0 157.6 L 173.2 197.8" id="7,5" style=""></path><path d="M 140.0 157.6 L 184.3 117.4" id="7,6" style=""></path><path d="M 95.8 137.5 L 140.0 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tce3330984f304062a7397680d54b9362"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:3;fill:none"><path d="M 184.3 197.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 184.3 197.8 L 228.6 177.7" id="5,1" style=""></path><path d="M 162.2 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 162.2 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.8 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 140.0 157.6 L 184.3 197.8" id="7,5" style=""></path><path d="M 140.0 157.6 L 162.2 117.4" id="7,6" style=""></path><path d="M 95.8 137.5 L 140.0 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t48c5a4e50db34a7bbe1ece4fa1f9bfe4"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:3;fill:none"><path d="M 184.3 197.8 L 228.6 177.7" id="5,0" style=""></path><path d="M 184.3 197.8 L 228.6 217.8" id="5,1" style=""></path><path d="M 162.2 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 162.2 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 51.5 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 140.0 157.6 L 184.3 197.8" id="7,5" style=""></path><path d="M 140.0 157.6 L 162.2 117.4" id="7,6" style=""></path><path d="M 51.5 137.5 L 140.0 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="ta3ce73a680974d1284f420ac83b04317"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:3;fill:none"><path d="M 162.2 197.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 162.2 197.8 L 228.6 177.7" id="5,1" style=""></path><path d="M 184.3 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 184.3 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.8 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 140.0 157.6 L 162.2 197.8" id="7,5" style=""></path><path d="M 140.0 157.6 L 184.3 117.4" id="7,6" style=""></path><path d="M 95.8 137.5 L 140.0 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t385824b5857c4a0baaf80ba7be70be1b"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:3;fill:none"><path d="M 162.2 157.6 L 228.6 177.7" id="5,0" style=""></path><path d="M 162.2 157.6 L 228.6 137.5" id="5,1" style=""></path><path d="M 184.3 157.6 L 228.6 217.8" id="6,2" style=""></path><path d="M 184.3 157.6 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.8 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 140.0 157.6 L 162.2 157.6" id="7,5" style=""></path><path d="M 140.0 157.6 L 184.3 157.6" id="7,6" style=""></path><path d="M 95.8 137.5 L 140.0 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tc27c78f087794fb0b87f1897d16a3c5a"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:3;fill:none"><path d="M 184.3 197.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 184.3 197.8 L 228.6 177.7" id="5,1" style=""></path><path d="M 162.2 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 162.2 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.8 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 140.0 157.6 L 184.3 197.8" id="7,5" style=""></path><path d="M 140.0 157.6 L 162.2 117.4" id="7,6" style=""></path><path d="M 95.8 137.5 L 140.0 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "td92a629f8e964a3dbb3ee38fb10e4127";
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
        })(modules["toyplot.coordinates.Axis"],"tf3a512a4763249c49871994f77243138",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.4836583584000005, "min": -4.0334758}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>

