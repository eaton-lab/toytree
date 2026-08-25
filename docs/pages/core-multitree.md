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




    <toytree.ToyTree at 0x77f26c1ff3e0>




```python
# get all trees
mtree1[:]
```




    [<toytree.ToyTree at 0x77f26c1ff3e0>,
     <toytree.ToyTree at 0x77f26c225580>,
     <toytree.ToyTree at 0x77f26c225160>,
     <toytree.ToyTree at 0x77f26c225460>,
     <toytree.ToyTree at 0x77f26c225850>,
     <toytree.ToyTree at 0x77f26c225b20>,
     <toytree.ToyTree at 0x77f26c225df0>,
     <toytree.ToyTree at 0x77f26c2260c0>]




```python
# slice the first three trees
mtree1[:3]
```




    [<toytree.ToyTree at 0x77f26c1ff3e0>,
     <toytree.ToyTree at 0x77f26c225580>,
     <toytree.ToyTree at 0x77f26c225160>]




```python
# iterate over ToyTrees in a MultiTree
for tree in mtree1:
    print(tree)
```

    <toytree.ToyTree at 0x77f26c1ff3e0>
    <toytree.ToyTree at 0x77f26c225580>
    <toytree.ToyTree at 0x77f26c225160>
    <toytree.ToyTree at 0x77f26c225460>
    <toytree.ToyTree at 0x77f26c225850>
    <toytree.ToyTree at 0x77f26c225b20>
    <toytree.ToyTree at 0x77f26c225df0>
    <toytree.ToyTree at 0x77f26c2260c0>



```python
# re-arrange trees in the treelist to send the first to be last
mtree1.treelist = mtree1.treelist[1:] + [mtree1.treelist[0]]
mtree1[:]
```




    [<toytree.ToyTree at 0x77f26c225580>,
     <toytree.ToyTree at 0x77f26c225160>,
     <toytree.ToyTree at 0x77f26c225460>,
     <toytree.ToyTree at 0x77f26c225850>,
     <toytree.ToyTree at 0x77f26c225b20>,
     <toytree.ToyTree at 0x77f26c225df0>,
     <toytree.ToyTree at 0x77f26c2260c0>,
     <toytree.ToyTree at 0x77f26c1ff3e0>]



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
c, a, m = ctree.draw(layout="unr", height=350)
ctree.annotate.add_edge_labels(a, "support", color="grey");
```


<div class="toyplot" id="t81394f82cbdf4f4bb1f0d9676877c78d" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="314.0px" height="350.0px" viewBox="0 0 314.0 350.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tb21ef5ff846543eebc56a8c79cbef17a"><g class="toyplot-coordinates-Cartesian" id="te8c551df18da42dc87e20674bd0ef105"><clipPath id="t6c429d97abea4bd0922c264806303bb1"><rect x="35.0" y="35.0" width="244.0" height="280.0"></rect></clipPath><g clip-path="url(#t6c429d97abea4bd0922c264806303bb1)"><g class="toytree-mark-Toytree" id="t651c4b0941d54d0daca65a0c8bd26e7c"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 199.0 138.6 L 241.5 164.0" id="5,0" style=""></path><path d="M 199.0 138.6 L 238.5 107.5" id="5,1" style=""></path><path d="M 127.7 117.2 L 127.2 72.7" id="6,2" style=""></path><path d="M 127.7 117.2 L 72.7 113.1" id="6,3" style=""></path><path d="M 158.5 135.2 L 85.0 277.9" id="7,4" style=""></path><path d="M 158.5 135.2 L 199.0 138.6" id="7,5" style=""></path><path d="M 158.5 135.2 L 127.7 117.2" id="7,6" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(241.463,163.964)rotate(24.4322)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(238.514,107.482)rotate(-24.4123)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(127.192,72.7046)rotate(69.0544)"><text x="-21.672" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(72.6629,113.132)rotate(18.6055)"><text x="-21.672" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(85.0089,277.928)rotate(111.466)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g><g class="toyplot-mark-Text" id="t988bc5f3ab924424947fe1c148e937ee"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(178.78096357640436,136.9153847931795)"><text x="-11.676" y="3.066" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0.75</text></g><g class="toyplot-Datum" transform="translate(143.1268216007924,126.17806803198238)"><text x="-11.676" y="3.066" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0.75</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Unique trees
Given a set of trees it is useful to be able to pull out just the unique topologies from the set. The function `get_unique_topologies()` returns a list of `(tree, int)` tuples from a `MultiTree` with each unique topology paired with its number of occurrences in the set. Note, this condenses all trees with the same topology into a single representative, using the first occurrence as the returned tree, thus branch length variation is not retained.


```python
# get (tree, count) for each unique topology in the MultiTree
mtree1.get_unique_topologies()
```




    [(<toytree.ToyTree at 0x77f26c225160>, 6),
     (<toytree.ToyTree at 0x77f26c225580>, 1),
     (<toytree.ToyTree at 0x77f26c2260c0>, 1)]



## Drawing with MultiTrees

### Grid tree drawings
See [MultiTree.draw()](/drawing-mtree-grid/) for a detailed description of MultiTree grid drawings.

The `MultiTree.draw()` method returns a drawing with multiple trees displayed on a grid. The `shape` and `idxs` arguments can be used to designate the grid layout and select which trees to show. All standard tree drawing style arguments are accepted. The `fixed_order` argument is often useful in this context to fix the order of tips to emphasize discordance among trees in a set.


```python
# draw a 2x4 grid of trees 8 trees from a collection
mtree1.draw(
    ts="o", shape=(2, 4), width=600, height=300, fixed_order=["c", "b", "e", "a", "d"]
);
```


<div class="toyplot" id="tc9ea3cb452b143a0a2b571e11e125fc3" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="600.0px" height="300.0px" viewBox="0 0 600.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t65ed7ac8eaad4e6991e480f99f6ac7e0"><g class="toyplot-coordinates-Cartesian" id="t5cce0c8bdfa04c4d808c9082fb14b92f"><clipPath id="t139b39aeb1dd4d8e92bfa83e68e65e1f"><rect x="20.0" y="30.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#t139b39aeb1dd4d8e92bfa83e68e65e1f)"><g class="toytree-mark-Toytree" id="tbc84dbe60bf240e7b1c712b83592d50e"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 81.5 55.7 L 104.6 65.5" id="5,0" style=""></path><path d="M 81.5 55.7 L 104.6 46.0" id="5,1" style=""></path><path d="M 81.5 94.8 L 104.6 104.5" id="6,2" style=""></path><path d="M 81.5 94.8 L 104.6 85.0" id="6,3" style=""></path><path d="M 35.4 99.6 L 104.6 124.0" id="8,4" style=""></path><path d="M 58.5 75.2 L 81.5 55.7" id="7,5" style=""></path><path d="M 58.5 75.2 L 81.5 94.8" id="7,6" style=""></path><path d="M 35.4 99.6 L 58.5 75.2" id="8,7" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 104.6 65.5 L 104.6 65.5"></path><path d="M 104.6 46.0 L 104.6 46.0"></path><path d="M 104.6 104.5 L 104.6 104.5"></path><path d="M 104.6 85.0 L 104.6 85.0"></path><path d="M 104.6 124.0 L 104.6 124.0"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(81.5441,55.7408)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(81.5441,94.7531)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(58.495,75.2469)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(35.4459,99.6296)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(104.593,65.4938)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(104.593,45.9877)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(104.593,104.506)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(104.593,85)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(104.593,124.012)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t181dc892474744818744c8227d7742fd"><clipPath id="t3c62a10d5e474b289bca4f433d5af5cd"><rect x="170.0" y="30.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#t3c62a10d5e474b289bca4f433d5af5cd)"><g class="toytree-mark-Toytree" id="t1f4b6abe4a964b04b91aa47b1e318eea"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 225.0 85.0 L 254.6 65.5" id="5,0" style=""></path><path d="M 225.0 85.0 L 254.6 104.5" id="5,1" style=""></path><path d="M 234.8 65.5 L 254.6 46.0" id="6,2" style=""></path><path d="M 234.8 65.5 L 254.6 85.0" id="6,3" style=""></path><path d="M 185.4 99.6 L 254.6 124.0" id="8,4" style=""></path><path d="M 205.2 75.2 L 225.0 85.0" id="7,5" style=""></path><path d="M 205.2 75.2 L 234.8 65.5" id="7,6" style=""></path><path d="M 185.4 99.6 L 205.2 75.2" id="8,7" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 254.6 65.5 L 254.6 65.5"></path><path d="M 254.6 104.5 L 254.6 104.5"></path><path d="M 254.6 46.0 L 254.6 46.0"></path><path d="M 254.6 85.0 L 254.6 85.0"></path><path d="M 254.6 124.0 L 254.6 124.0"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(224.959,85)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(234.837,65.4938)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(205.202,75.2469)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(185.446,99.6296)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(254.593,65.4938)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(254.593,104.506)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(254.593,45.9877)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(254.593,85)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(254.593,124.012)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t7db35831a2ca46a5a9bcf4efd3d340fe"><clipPath id="t2ed87456d03d4622b0a51875bb550a84"><rect x="320.0" y="30.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#t2ed87456d03d4622b0a51875bb550a84)"><g class="toytree-mark-Toytree" id="tcae026ec20764cf78016394ff81fc65a"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 375.8 85.0 L 404.6 65.5" id="5,0" style=""></path><path d="M 375.8 85.0 L 404.6 104.5" id="5,1" style=""></path><path d="M 381.5 65.5 L 404.6 46.0" id="6,2" style=""></path><path d="M 381.5 65.5 L 404.6 85.0" id="6,3" style=""></path><path d="M 335.4 99.6 L 404.6 124.0" id="8,4" style=""></path><path d="M 358.5 75.2 L 375.8 85.0" id="7,5" style=""></path><path d="M 358.5 75.2 L 381.5 65.5" id="7,6" style=""></path><path d="M 335.4 99.6 L 358.5 75.2" id="8,7" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 404.6 65.5 L 404.6 65.5"></path><path d="M 404.6 104.5 L 404.6 104.5"></path><path d="M 404.6 46.0 L 404.6 46.0"></path><path d="M 404.6 85.0 L 404.6 85.0"></path><path d="M 404.6 124.0 L 404.6 124.0"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(375.782,85)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(381.544,65.4938)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(358.495,75.2469)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(335.446,99.6296)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(404.593,65.4938)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(404.593,104.506)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(404.593,45.9877)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(404.593,85)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(404.593,124.012)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t537e678f74a640f5b10335f16ff0aade"><clipPath id="t988d5cf6fa3e490484b30cad2a4aa2b3"><rect x="470.0" y="30.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#t988d5cf6fa3e490484b30cad2a4aa2b3)"><g class="toytree-mark-Toytree" id="tb97a910994384dbe984d3994c96fe073"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 531.5 85.0 L 554.6 65.5" id="5,0" style=""></path><path d="M 531.5 85.0 L 554.6 104.5" id="5,1" style=""></path><path d="M 520.0 65.5 L 554.6 46.0" id="6,2" style=""></path><path d="M 520.0 65.5 L 554.6 85.0" id="6,3" style=""></path><path d="M 485.4 99.6 L 554.6 124.0" id="8,4" style=""></path><path d="M 508.5 75.2 L 531.5 85.0" id="7,5" style=""></path><path d="M 508.5 75.2 L 520.0 65.5" id="7,6" style=""></path><path d="M 485.4 99.6 L 508.5 75.2" id="8,7" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 554.6 65.5 L 554.6 65.5"></path><path d="M 554.6 104.5 L 554.6 104.5"></path><path d="M 554.6 46.0 L 554.6 46.0"></path><path d="M 554.6 85.0 L 554.6 85.0"></path><path d="M 554.6 124.0 L 554.6 124.0"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(531.544,85)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(520.02,65.4938)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(508.495,75.2469)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(485.446,99.6296)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(554.593,65.4938)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(554.593,104.506)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(554.593,45.9877)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(554.593,85)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(554.593,124.012)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t875fb5ef6bb04d31ba3d7493cf56c49b"><clipPath id="tb416ee3068d9423db062964cf788aba8"><rect x="20.0" y="160.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#tb416ee3068d9423db062964cf788aba8)"><g class="toytree-mark-Toytree" id="t5ca599d2b3fe4097a09e9ff73f4430bb"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 87.3 215.0 L 104.6 234.5" id="5,0" style=""></path><path d="M 87.3 215.0 L 104.6 195.5" id="5,1" style=""></path><path d="M 78.7 195.5 L 104.6 176.0" id="6,2" style=""></path><path d="M 78.7 195.5 L 104.6 215.0" id="6,3" style=""></path><path d="M 35.4 229.6 L 104.6 254.0" id="8,4" style=""></path><path d="M 70.0 205.2 L 87.3 215.0" id="7,5" style=""></path><path d="M 70.0 205.2 L 78.7 195.5" id="7,6" style=""></path><path d="M 35.4 229.6 L 70.0 205.2" id="8,7" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 104.6 234.5 L 104.6 234.5"></path><path d="M 104.6 195.5 L 104.6 195.5"></path><path d="M 104.6 176.0 L 104.6 176.0"></path><path d="M 104.6 215.0 L 104.6 215.0"></path><path d="M 104.6 254.0 L 104.6 254.0"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(87.3063,215)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(78.6629,195.494)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(70.0195,205.247)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(35.4459,229.63)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(104.593,234.506)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(104.593,195.494)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(104.593,175.988)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(104.593,215)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(104.593,254.012)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="td3b88e262fc149f89881d6d8c64068b3"><clipPath id="t028136f136094b45b725183a50fd77b6"><rect x="170.0" y="160.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#t028136f136094b45b725183a50fd77b6)"><g class="toytree-mark-Toytree" id="t515d61ba77d043c4afff491d5781b044"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 220.0 215.0 L 254.6 195.5" id="5,0" style=""></path><path d="M 220.0 215.0 L 254.6 234.5" id="5,1" style=""></path><path d="M 231.5 195.5 L 254.6 176.0" id="6,2" style=""></path><path d="M 231.5 195.5 L 254.6 215.0" id="6,3" style=""></path><path d="M 185.4 229.6 L 254.6 254.0" id="8,4" style=""></path><path d="M 208.5 205.2 L 220.0 215.0" id="7,5" style=""></path><path d="M 208.5 205.2 L 231.5 195.5" id="7,6" style=""></path><path d="M 185.4 229.6 L 208.5 205.2" id="8,7" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 254.6 195.5 L 254.6 195.5"></path><path d="M 254.6 234.5 L 254.6 234.5"></path><path d="M 254.6 176.0 L 254.6 176.0"></path><path d="M 254.6 215.0 L 254.6 215.0"></path><path d="M 254.6 254.0 L 254.6 254.0"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(220.02,215)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(231.544,195.494)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(208.495,205.247)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(185.446,229.63)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(254.593,195.494)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(254.593,234.506)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(254.593,175.988)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(254.593,215)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(254.593,254.012)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t39492943709e447cba0615f16cb96751"><clipPath id="t0c6e501fd0684b8581ebfcc873051057"><rect x="320.0" y="160.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#t0c6e501fd0684b8581ebfcc873051057)"><g class="toytree-mark-Toytree" id="t3b9b64b6a2fb40558ba864d7824021b3"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 370.0 205.2 L 404.6 234.5" id="5,0" style=""></path><path d="M 370.0 205.2 L 404.6 176.0" id="5,1" style=""></path><path d="M 381.5 205.2 L 404.6 195.5" id="6,2" style=""></path><path d="M 381.5 205.2 L 404.6 215.0" id="6,3" style=""></path><path d="M 335.4 229.6 L 404.6 254.0" id="8,4" style=""></path><path d="M 358.5 205.2 L 370.0 205.2" id="7,5" style=""></path><path d="M 358.5 205.2 L 381.5 205.2" id="7,6" style=""></path><path d="M 335.4 229.6 L 358.5 205.2" id="8,7" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 404.6 234.5 L 404.6 234.5"></path><path d="M 404.6 176.0 L 404.6 176.0"></path><path d="M 404.6 195.5 L 404.6 195.5"></path><path d="M 404.6 215.0 L 404.6 215.0"></path><path d="M 404.6 254.0 L 404.6 254.0"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(370.02,205.247)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(381.544,205.247)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(358.495,205.247)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(335.446,229.63)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(404.593,234.506)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(404.593,175.988)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(404.593,195.494)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(404.593,215)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(404.593,254.012)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t4d312ecd51344d7a9320d555437cd93e"><clipPath id="t17ea18e5195145279668170b10c081c7"><rect x="470.0" y="160.0" width="110.0" height="110.0"></rect></clipPath><g clip-path="url(#t17ea18e5195145279668170b10c081c7)"><g class="toytree-mark-Toytree" id="t30241eea28c54796964fe849e20f3712"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 531.5 215.0 L 554.6 195.5" id="5,0" style=""></path><path d="M 531.5 215.0 L 554.6 234.5" id="5,1" style=""></path><path d="M 520.0 195.5 L 554.6 176.0" id="6,2" style=""></path><path d="M 520.0 195.5 L 554.6 215.0" id="6,3" style=""></path><path d="M 485.4 229.6 L 554.6 254.0" id="8,4" style=""></path><path d="M 508.5 205.2 L 531.5 215.0" id="7,5" style=""></path><path d="M 508.5 205.2 L 520.0 195.5" id="7,6" style=""></path><path d="M 485.4 229.6 L 508.5 205.2" id="8,7" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 554.6 195.5 L 554.6 195.5"></path><path d="M 554.6 234.5 L 554.6 234.5"></path><path d="M 554.6 176.0 L 554.6 176.0"></path><path d="M 554.6 215.0 L 554.6 215.0"></path><path d="M 554.6 254.0 L 554.6 254.0"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(531.544,215)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(520.02,195.494)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(508.495,205.247)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(485.446,229.63)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(554.593,195.494)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(554.593,234.506)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(554.593,175.988)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(554.593,215)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(554.593,254.012)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


### Cloud tree drawings
See [MultiTree.draw_cloud_tree()](/drawing-mtree-cloud/) for a detailed description of MultiTree cloud tree drawings.

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


<div class="toyplot" id="t9b3a0b841c50481795e334d6db654422" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t5da73de5e92f4ff9a41838bb15902c5a"><g class="toyplot-coordinates-Cartesian" id="tecb243d5591b42d3931d2d5d65bc32b1"><clipPath id="t77c5fe0599c14b56988bad5ea17292ef"><rect x="50.0" y="59.34476420858974" width="200.0" height="175.0"></rect></clipPath><g clip-path="url(#t77c5fe0599c14b56988bad5ea17292ef)"></g><g class="toyplot-coordinates-Axis" id="tcd586e14f42f41678a94f0d4d9903f08" transform="translate(50.0,234.34476420858974)"><line x1="1.482169837163175" y1="0" x2="178.58561019266625" y2="0" style=""></line><g><line x1="1.482169837163175" y1="0" x2="1.482169837163175" y2="-5.0" style=""></line><line x1="45.758029926038944" y1="0" x2="45.758029926038944" y2="-5.0" style=""></line><line x1="90.0338900149147" y1="0" x2="90.0338900149147" y2="-5.0" style=""></line><line x1="134.30975010379046" y1="0" x2="134.30975010379046" y2="-5.0" style=""></line><line x1="178.58561019266625" y1="0" x2="178.58561019266625" y2="-5.0" style=""></line></g><g><g transform="translate(1.482169837163175,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(45.758029926038944,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(90.0338900149147,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(134.30975010379046,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(178.58561019266625,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t0712afad66c54e3080aa54e0e058aaf0"><clipPath id="t5648d2b108ad4db9bff2b19bb71d661f"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t5648d2b108ad4db9bff2b19bb71d661f)"><g class="toytree-mark-Toytree" id="t9ae213cd2c034dedbdbe442d99e32f6d"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:3;fill:none"><path d="M 184.3 177.7 L 228.6 217.8" id="5,0" style=""></path><path d="M 184.3 177.7 L 228.6 137.5" id="5,1" style=""></path><path d="M 184.3 137.5 L 228.6 177.7" id="6,2" style=""></path><path d="M 184.3 137.5 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.8 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 140.0 157.6 L 184.3 177.7" id="7,5" style=""></path><path d="M 140.0 157.6 L 184.3 137.5" id="7,6" style=""></path><path d="M 95.8 137.5 L 140.0 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(228.586,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(228.586,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(228.586,177.672)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(228.586,97.3276)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(228.586,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g><g class="toytree-mark-Toytree" id="teaeb7784d96a4f76a0c30840cd7e22ff"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:3;fill:none"><path d="M 162.2 197.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 162.2 197.8 L 228.6 177.7" id="5,1" style=""></path><path d="M 184.3 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 184.3 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 73.6 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 117.9 157.6 L 162.2 197.8" id="7,5" style=""></path><path d="M 117.9 157.6 L 184.3 117.4" id="7,6" style=""></path><path d="M 73.6 137.5 L 117.9 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t0f50266f2c2a457b933c8ccc260f143b"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:3;fill:none"><path d="M 173.2 197.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 173.2 197.8 L 228.6 177.7" id="5,1" style=""></path><path d="M 184.3 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 184.3 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.8 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 140.0 157.6 L 173.2 197.8" id="7,5" style=""></path><path d="M 140.0 157.6 L 184.3 117.4" id="7,6" style=""></path><path d="M 95.8 137.5 L 140.0 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t08954ad0625742d3abab42c72ba23318"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:3;fill:none"><path d="M 184.3 197.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 184.3 197.8 L 228.6 177.7" id="5,1" style=""></path><path d="M 162.2 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 162.2 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.8 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 140.0 157.6 L 184.3 197.8" id="7,5" style=""></path><path d="M 140.0 157.6 L 162.2 117.4" id="7,6" style=""></path><path d="M 95.8 137.5 L 140.0 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t8a73f221c3fb4771bc546e71163eb843"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:3;fill:none"><path d="M 184.3 197.8 L 228.6 177.7" id="5,0" style=""></path><path d="M 184.3 197.8 L 228.6 217.8" id="5,1" style=""></path><path d="M 162.2 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 162.2 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 51.5 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 140.0 157.6 L 184.3 197.8" id="7,5" style=""></path><path d="M 140.0 157.6 L 162.2 117.4" id="7,6" style=""></path><path d="M 51.5 137.5 L 140.0 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t630f3b2b79f14d879cf6559559fed07f"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:3;fill:none"><path d="M 162.2 197.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 162.2 197.8 L 228.6 177.7" id="5,1" style=""></path><path d="M 184.3 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 184.3 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.8 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 140.0 157.6 L 162.2 197.8" id="7,5" style=""></path><path d="M 140.0 157.6 L 184.3 117.4" id="7,6" style=""></path><path d="M 95.8 137.5 L 140.0 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t5a910cc736414c75bcd1a2645042a6e1"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:3;fill:none"><path d="M 162.2 157.6 L 228.6 177.7" id="5,0" style=""></path><path d="M 162.2 157.6 L 228.6 137.5" id="5,1" style=""></path><path d="M 184.3 157.6 L 228.6 217.8" id="6,2" style=""></path><path d="M 184.3 157.6 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.8 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 140.0 157.6 L 162.2 157.6" id="7,5" style=""></path><path d="M 140.0 157.6 L 184.3 157.6" id="7,6" style=""></path><path d="M 95.8 137.5 L 140.0 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="te002a47140b94200bf827b2275936328"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:3;fill:none"><path d="M 184.3 197.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 184.3 197.8 L 228.6 177.7" id="5,1" style=""></path><path d="M 162.2 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 162.2 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.8 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 140.0 157.6 L 184.3 197.8" id="7,5" style=""></path><path d="M 140.0 157.6 L 162.2 117.4" id="7,6" style=""></path><path d="M 95.8 137.5 L 140.0 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t5da73de5e92f4ff9a41838bb15902c5a";
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
        })(modules["toyplot.coordinates.Axis"],"tcd586e14f42f41678a94f0d4d9903f08",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.4836583584000005, "min": -4.0334758}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>

