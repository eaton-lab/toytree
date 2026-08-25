<div class="nb-md-page-hook" aria-hidden="true"></div>

# Stochastic Character Mapping

This page demonstrates the method ``simulate_stochastic_map`` for examining transitions in a discrete character across the edges of a phylogeny.

Stochastic character mapping samples complete histories of a discrete trait on a phylogeny. Instead of assigning one state to each node, it samples where state changes may have occurred along every branch, conditional on observed data and a fitted continuous-time Markov chain (CTMC) model.

The method was introduced for mapping substitutions and character changes on trees by Nielsen (2002) and Huelsenbeck, Nielsen, and Bollback (2003), and popularized for discrete-trait analyses by SIMMAP (Bollback 2006). Related CTMC summaries, such as labeled transition counts, can be interpreted as stochastic-map statistics (Minin and Suchard 2008).

Replicate stochastic maps can be used to compute several practical summaries: total branch time spent in each state (dwell time), counts of transitions among states, directional gains and losses, branch-specific probabilities that a transition occurred, and uncertainty in where along the tree transitions are placed.


```python
import numpy as np
import pandas as pd
import toytree
```

## Setup

A stochastic map requires a tree, observed discrete states, and a fitted Mk model. Here we simulate a small three-state trait only at the tips, then fit an equal-rates model with `fit_discrete_ctmc()`.

The observed tip states are stored to the tree as the node feature `X`. Internal nodes are missing because they will be treated as unknown during fitting and mapping.


```python
# simulate a small tree
tree = toytree.rtree.unittree(ntips=12, treeheight=1.0, seed=123)

# simulate a 3-state trait on the tips
tree.pcm.simulate_discrete_trait(
    nstates=3,
    model="ER",
    name="X",
    state_names="ABC",
    tips_only=True,
    inplace=True,
    seed=2,
)

# fit a CTMC equal-rates model
fit = tree.pcm.fit_discrete_ctmc(data="X", nstates=3, model="ER")
```


```python
tree.draw(
    width=500,
    height=350,
    node_sizes=10,
    node_mask=(1, 0, 0),
    node_colors=("X", "Set2"),
);
```


<div class="toyplot" id="t2362041163b8498a9c4c194c7b9929cf" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="500.0px" height="350.0px" viewBox="0 0 500.0 350.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tfbe2819c52a349c6900a279bd3ee28c4"><g class="toyplot-coordinates-Cartesian" id="t3c43f8ca487c4dbab5be980e84d1e780"><clipPath id="td32b0447f74744a485b298871abcd8e0"><rect x="35.0" y="35.0" width="430.0" height="280.0"></rect></clipPath><g clip-path="url(#td32b0447f74744a485b298871abcd8e0)"><g class="toytree-mark-Toytree" id="t3c543b6d150b46be881bc8ea0e731c41"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 89.3 274.1 L 89.3 292.8 L 417.9 292.8" id="14,0" style=""></path><path d="M 155.0 255.3 L 155.0 271.4 L 417.9 271.4" id="13,1" style=""></path><path d="M 220.8 239.3 L 220.8 250.0 L 417.9 250.0" id="12,2" style=""></path><path d="M 220.8 239.3 L 220.8 228.6 L 417.9 228.6" id="12,3" style=""></path><path d="M 220.8 196.4 L 220.8 207.1 L 417.9 207.1" id="15,4" style=""></path><path d="M 220.8 196.4 L 220.8 185.7 L 417.9 185.7" id="15,5" style=""></path><path d="M 155.0 180.4 L 155.0 164.3 L 417.9 164.3" id="16,6" style=""></path><path d="M 155.0 122.8 L 155.0 142.9 L 417.9 142.9" id="20,7" style=""></path><path d="M 220.8 102.7 L 220.8 121.4 L 417.9 121.4" id="19,8" style=""></path><path d="M 286.5 84.0 L 286.5 100.0 L 417.9 100.0" id="18,9" style=""></path><path d="M 352.2 67.9 L 352.2 78.6 L 417.9 78.6" id="17,10" style=""></path><path d="M 352.2 67.9 L 352.2 57.2 L 417.9 57.2" id="17,11" style=""></path><path d="M 155.0 255.3 L 155.0 239.3 L 220.8 239.3" id="13,12" style=""></path><path d="M 89.3 274.1 L 89.3 255.3 L 155.0 255.3" id="14,13" style=""></path><path d="M 56.4 212.8 L 56.4 274.1 L 89.3 274.1" id="22,14" style=""></path><path d="M 155.0 180.4 L 155.0 196.4 L 220.8 196.4" id="16,15" style=""></path><path d="M 89.3 151.6 L 89.3 180.4 L 155.0 180.4" id="21,16" style=""></path><path d="M 286.5 84.0 L 286.5 67.9 L 352.2 67.9" id="18,17" style=""></path><path d="M 220.8 102.7 L 220.8 84.0 L 286.5 84.0" id="19,18" style=""></path><path d="M 155.0 122.8 L 155.0 102.7 L 220.8 102.7" id="20,19" style=""></path><path d="M 89.3 151.6 L 89.3 122.8 L 155.0 122.8" id="21,20" style=""></path><path d="M 56.4 212.8 L 56.4 151.6 L 89.3 151.6" id="22,21" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(417.936,292.823)"><circle r="5.0"></circle></g><g id="Node-1" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(417.936,271.4)"><circle r="5.0"></circle></g><g id="Node-2" style="fill:rgb(55.3%,62.7%,79.6%)" transform="translate(417.936,249.978)"><circle r="5.0"></circle></g><g id="Node-3" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(417.936,228.556)"><circle r="5.0"></circle></g><g id="Node-4" style="fill:rgb(98.8%,55.3%,38.4%)" transform="translate(417.936,207.133)"><circle r="5.0"></circle></g><g id="Node-5" style="fill:rgb(98.8%,55.3%,38.4%)" transform="translate(417.936,185.711)"><circle r="5.0"></circle></g><g id="Node-6" style="fill:rgb(55.3%,62.7%,79.6%)" transform="translate(417.936,164.289)"><circle r="5.0"></circle></g><g id="Node-7" style="fill:rgb(98.8%,55.3%,38.4%)" transform="translate(417.936,142.867)"><circle r="5.0"></circle></g><g id="Node-8" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(417.936,121.444)"><circle r="5.0"></circle></g><g id="Node-9" style="fill:rgb(55.3%,62.7%,79.6%)" transform="translate(417.936,100.022)"><circle r="5.0"></circle></g><g id="Node-10" style="fill:rgb(98.8%,55.3%,38.4%)" transform="translate(417.936,78.5998)"><circle r="5.0"></circle></g><g id="Node-11" style="fill:rgb(55.3%,62.7%,79.6%)" transform="translate(417.936,57.1775)"><circle r="5.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(417.936,292.823)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(417.936,271.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(417.936,249.978)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(417.936,228.556)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(417.936,207.133)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(417.936,185.711)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(417.936,164.289)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(417.936,142.867)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(417.936,121.444)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(417.936,100.022)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g><g class="toytree-TipLabel" transform="translate(417.936,78.5998)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r10</text></g><g class="toytree-TipLabel" transform="translate(417.936,57.1775)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r11</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Sample Maps

`simulate_stochastic_map()` samples one or more full branch histories under the fitted model and returns a `PCMStochasticMapResult` object. 




```python
result = tree.pcm.simulate_stochastic_map(
    data="X",
    model_fit=fit,
    nreplicates=10,
    seed=3,
)
```

The fundamental result is stored in the `segments` table, where each row in a sampled branch interval that records a state, the edge it belongs to, and its start and end time measured from the child end of that branch. 

Each ``map_id`` is one stochastic replicate, representing one sampled history that can be plotted. The `duration` values for all segments on an edge sum to that branch length. 


```python
columns = ["map_id", "edge_id", "child", "parent", "state", "t_start", "t_end", "duration"]
result.segments[columns].head(12)
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
      <th>map_id</th>
      <th>edge_id</th>
      <th>child</th>
      <th>parent</th>
      <th>state</th>
      <th>t_start</th>
      <th>t_end</th>
      <th>duration</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>A</td>
      <td>0.000000</td>
      <td>0.093018</td>
      <td>0.093018</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>C</td>
      <td>0.093018</td>
      <td>0.133031</td>
      <td>0.040013</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>B</td>
      <td>0.133031</td>
      <td>0.163898</td>
      <td>0.030866</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>A</td>
      <td>0.163898</td>
      <td>0.178763</td>
      <td>0.014865</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>C</td>
      <td>0.178763</td>
      <td>0.187068</td>
      <td>0.008305</td>
    </tr>
    <tr>
      <th>5</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>A</td>
      <td>0.187068</td>
      <td>0.250340</td>
      <td>0.063272</td>
    </tr>
    <tr>
      <th>6</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>C</td>
      <td>0.250340</td>
      <td>0.265435</td>
      <td>0.015095</td>
    </tr>
    <tr>
      <th>7</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>A</td>
      <td>0.265435</td>
      <td>0.358116</td>
      <td>0.092681</td>
    </tr>
    <tr>
      <th>8</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>B</td>
      <td>0.358116</td>
      <td>0.363324</td>
      <td>0.005208</td>
    </tr>
    <tr>
      <th>9</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>C</td>
      <td>0.363324</td>
      <td>0.436076</td>
      <td>0.072752</td>
    </tr>
    <tr>
      <th>10</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>B</td>
      <td>0.436076</td>
      <td>0.510736</td>
      <td>0.074660</td>
    </tr>
    <tr>
      <th>11</th>
      <td>0</td>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>A</td>
      <td>0.510736</td>
      <td>0.515434</td>
      <td>0.004698</td>
    </tr>
  </tbody>
</table>
</div>



## Visualize a Map

Use `tree.annotate.add_edge_stochastic_map()` to overlay one replicate on an existing tree drawing.


```python
canvas, axes, mark = tree.draw(width=550, height=350)
tree.annotate.add_edge_stochastic_map(
    axes,
    data=result,
    map_id=0,
    color="Set2",
    width=4,
);
tree.annotate.add_tip_markers(axes, color=("X", "Set2"), size=10);
```


<div class="toyplot" id="td785298bb667497090f99b70d47eff45" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="550.0px" height="350.0px" viewBox="0 0 550.0 350.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="teda9f6bacbd140efb4bb0b29626f02f4"><g class="toyplot-coordinates-Cartesian" id="t64a2c66794f04ab6af090f07c48da459"><clipPath id="t48f144a382de4901a8f557c5ebe795c7"><rect x="35.0" y="35.0" width="480.0" height="280.0"></rect></clipPath><g clip-path="url(#t48f144a382de4901a8f557c5ebe795c7)"><g class="toytree-mark-Toytree" id="tb583ad448c704d97afdae737352b30ff"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 88.9 274.1 L 88.9 292.8 L 467.8 292.8" id="14,0" style=""></path><path d="M 164.7 255.3 L 164.7 271.4 L 467.8 271.4" id="13,1" style=""></path><path d="M 240.5 239.3 L 240.5 250.0 L 467.8 250.0" id="12,2" style=""></path><path d="M 240.5 239.3 L 240.5 228.6 L 467.8 228.6" id="12,3" style=""></path><path d="M 240.5 196.4 L 240.5 207.1 L 467.8 207.1" id="15,4" style=""></path><path d="M 240.5 196.4 L 240.5 185.7 L 467.8 185.7" id="15,5" style=""></path><path d="M 164.7 180.4 L 164.7 164.3 L 467.8 164.3" id="16,6" style=""></path><path d="M 164.7 122.8 L 164.7 142.9 L 467.8 142.9" id="20,7" style=""></path><path d="M 240.5 102.7 L 240.5 121.4 L 467.8 121.4" id="19,8" style=""></path><path d="M 316.3 84.0 L 316.3 100.0 L 467.8 100.0" id="18,9" style=""></path><path d="M 392.0 67.9 L 392.0 78.6 L 467.8 78.6" id="17,10" style=""></path><path d="M 392.0 67.9 L 392.0 57.2 L 467.8 57.2" id="17,11" style=""></path><path d="M 164.7 255.3 L 164.7 239.3 L 240.5 239.3" id="13,12" style=""></path><path d="M 88.9 274.1 L 88.9 255.3 L 164.7 255.3" id="14,13" style=""></path><path d="M 51.0 212.8 L 51.0 274.1 L 88.9 274.1" id="22,14" style=""></path><path d="M 164.7 180.4 L 164.7 196.4 L 240.5 196.4" id="16,15" style=""></path><path d="M 88.9 151.6 L 88.9 180.4 L 164.7 180.4" id="21,16" style=""></path><path d="M 316.3 84.0 L 316.3 67.9 L 392.0 67.9" id="18,17" style=""></path><path d="M 240.5 102.7 L 240.5 84.0 L 316.3 84.0" id="19,18" style=""></path><path d="M 164.7 122.8 L 164.7 102.7 L 240.5 102.7" id="20,19" style=""></path><path d="M 88.9 151.6 L 88.9 122.8 L 164.7 122.8" id="21,20" style=""></path><path d="M 51.0 212.8 L 51.0 151.6 L 88.9 151.6" id="22,21" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(467.824,292.823)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(467.824,271.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(467.824,249.978)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(467.824,228.556)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(467.824,207.133)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(467.824,185.711)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(467.824,164.289)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(467.824,142.867)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(467.824,121.444)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(467.824,100.022)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g><g class="toytree-TipLabel" transform="translate(467.824,78.5998)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r10</text></g><g class="toytree-TipLabel" transform="translate(467.824,57.1775)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r11</text></g></g></g><g class="toytree-Annotation-Lines" id="t3f6246f5a3064103a4111d9a8ca5b3ac" style="stroke-linecap:butt"><path id="Line-0" d="M 88.888508 292.82252 L 127.6612 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-1" d="M 127.6612 292.82252 L 144.33993 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-2" d="M 144.33993 292.82252 L 157.20593 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-3" d="M 157.20593 292.82252 L 163.40218 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-4" d="M 163.40218 292.82252 L 166.86407 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-5" d="M 166.86407 292.82252 L 193.23775 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-6" d="M 193.23775 292.82252 L 199.5297 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-7" d="M 199.5297 292.82252 L 238.16173 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-8" d="M 238.16173 292.82252 L 240.33261 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-9" d="M 240.33261 292.82252 L 270.65798 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-10" d="M 270.65798 292.82252 L 301.77839 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-11" d="M 301.77839 292.82252 L 303.73679 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-12" d="M 303.73679 292.82252 L 321.14193 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-13" d="M 321.14193 292.82252 L 353.54734 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-14" d="M 353.54734 292.82252 L 371.90074 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-15" d="M 371.90074 292.82252 L 373.93299 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-16" d="M 373.93299 292.82252 L 376.38926 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-17" d="M 376.38926 292.82252 L 410.89626 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-18" d="M 410.89626 292.82252 L 411.32551 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-19" d="M 411.32551 292.82252 L 418.99443 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-20" d="M 418.99443 292.82252 L 421.77621 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-21" d="M 421.77621 292.82252 L 437.91869 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-22" d="M 437.91869 292.82252 L 467.82443 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-23" d="M 88.888508 292.82252 L 88.888508 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-24" d="M 164.67569 271.40024 L 180.40382 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-25" d="M 180.40382 271.40024 L 224.74453 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-26" d="M 224.74453 271.40024 L 229.4547 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-27" d="M 229.4547 271.40024 L 314.79113 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-28" d="M 314.79113 271.40024 L 323.23757 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-29" d="M 323.23757 271.40024 L 329.88651 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-30" d="M 329.88651 271.40024 L 332.84365 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-31" d="M 332.84365 271.40024 L 343.44259 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-32" d="M 343.44259 271.40024 L 367.52085 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-33" d="M 367.52085 271.40024 L 367.64386 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-34" d="M 367.64386 271.40024 L 370.78172 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-35" d="M 370.78172 271.40024 L 378.68629 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-36" d="M 378.68629 271.40024 L 379.34889 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-37" d="M 379.34889 271.40024 L 422.18855 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-38" d="M 422.18855 271.40024 L 457.28438 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-39" d="M 457.28438 271.40024 L 467.82443 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-40" d="M 164.67569 271.40024 L 164.67569 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-41" d="M 240.46288 249.97796 L 319.58919 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-42" d="M 319.58919 249.97796 L 319.77832 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-43" d="M 319.77832 249.97796 L 329.80925 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-44" d="M 329.80925 249.97796 L 364.77222 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-45" d="M 364.77222 249.97796 L 368.44971 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-46" d="M 368.44971 249.97796 L 409.59946 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-47" d="M 409.59946 249.97796 L 447.23789 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-48" d="M 447.23789 249.97796 L 449.96006 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-49" d="M 449.96006 249.97796 L 455.80625 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-50" d="M 455.80625 249.97796 L 467.82443 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-51" d="M 240.46288 249.97796 L 240.46288 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-52" d="M 240.46288 228.55569 L 269.11472 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-53" d="M 269.11472 228.55569 L 273.1204 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-54" d="M 273.1204 228.55569 L 273.89965 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-55" d="M 273.89965 228.55569 L 285.30284 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-56" d="M 285.30284 228.55569 L 291.6456 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-57" d="M 291.6456 228.55569 L 295.91556 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-58" d="M 295.91556 228.55569 L 304.10005 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-59" d="M 304.10005 228.55569 L 316.14169 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-60" d="M 316.14169 228.55569 L 317.70314 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-61" d="M 317.70314 228.55569 L 332.45194 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-62" d="M 332.45194 228.55569 L 334.85535 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-63" d="M 334.85535 228.55569 L 362.40062 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-64" d="M 362.40062 228.55569 L 362.62373 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-65" d="M 362.62373 228.55569 L 391.73713 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-66" d="M 391.73713 228.55569 L 392.37619 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-67" d="M 392.37619 228.55569 L 441.61305 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-68" d="M 441.61305 228.55569 L 452.3287 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-69" d="M 452.3287 228.55569 L 453.48562 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-70" d="M 453.48562 228.55569 L 467.77965 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-71" d="M 467.77965 228.55569 L 467.82443 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-72" d="M 240.46288 228.55569 L 240.46288 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-73" d="M 240.46288 207.13341 L 240.72398 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-74" d="M 240.72398 207.13341 L 276.83429 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-75" d="M 276.83429 207.13341 L 314.10806 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-76" d="M 314.10806 207.13341 L 317.84913 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-77" d="M 317.84913 207.13341 L 341.34271 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-78" d="M 341.34271 207.13341 L 357.84977 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-79" d="M 357.84977 207.13341 L 364.88161 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-80" d="M 364.88161 207.13341 L 368.00786 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-81" d="M 368.00786 207.13341 L 368.34658 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-82" d="M 368.34658 207.13341 L 368.90348 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-83" d="M 368.90348 207.13341 L 391.37253 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-84" d="M 391.37253 207.13341 L 391.97137 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-85" d="M 391.97137 207.13341 L 392.66671 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-86" d="M 392.66671 207.13341 L 395.8762 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-87" d="M 395.8762 207.13341 L 396.46723 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-88" d="M 396.46723 207.13341 L 415.31532 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-89" d="M 415.31532 207.13341 L 418.69582 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-90" d="M 418.69582 207.13341 L 438.8961 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-91" d="M 438.8961 207.13341 L 439.72957 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-92" d="M 439.72957 207.13341 L 459.82484 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-93" d="M 459.82484 207.13341 L 467.82443 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-94" d="M 240.46288 207.13341 L 240.46288 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-95" d="M 240.46288 185.71114 L 243.25092 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-96" d="M 243.25092 185.71114 L 266.69529 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-97" d="M 266.69529 185.71114 L 277.18033 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-98" d="M 277.18033 185.71114 L 301.93253 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-99" d="M 301.93253 185.71114 L 304.15493 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-100" d="M 304.15493 185.71114 L 327.3638 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-101" d="M 327.3638 185.71114 L 331.66337 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-102" d="M 331.66337 185.71114 L 339.17863 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-103" d="M 339.17863 185.71114 L 339.54683 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-104" d="M 339.54683 185.71114 L 351.22522 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-105" d="M 351.22522 185.71114 L 368.32212 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-106" d="M 368.32212 185.71114 L 390.40871 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-107" d="M 390.40871 185.71114 L 390.53304 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-108" d="M 390.53304 185.71114 L 404.33876 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-109" d="M 404.33876 185.71114 L 424.82955 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-110" d="M 424.82955 185.71114 L 443.72908 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-111" d="M 443.72908 185.71114 L 467.82443 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-112" d="M 240.46288 185.71114 L 240.46288 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-113" d="M 164.67569 164.28886 L 168.35982 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-114" d="M 168.35982 164.28886 L 171.19476 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-115" d="M 171.19476 164.28886 L 209.6335 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-116" d="M 209.6335 164.28886 L 221.53285 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-117" d="M 221.53285 164.28886 L 222.36571 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-118" d="M 222.36571 164.28886 L 224.81198 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-119" d="M 224.81198 164.28886 L 228.24729 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-120" d="M 228.24729 164.28886 L 236.36037 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-121" d="M 236.36037 164.28886 L 245.34298 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-122" d="M 245.34298 164.28886 L 305.32201 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-123" d="M 305.32201 164.28886 L 311.7357 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-124" d="M 311.7357 164.28886 L 315.89036 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-125" d="M 315.89036 164.28886 L 316.71137 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-126" d="M 316.71137 164.28886 L 334.75146 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-127" d="M 334.75146 164.28886 L 346.62328 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-128" d="M 346.62328 164.28886 L 349.4764 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-129" d="M 349.4764 164.28886 L 407.82542 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-130" d="M 407.82542 164.28886 L 409.5795 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-131" d="M 409.5795 164.28886 L 413.43231 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-132" d="M 413.43231 164.28886 L 423.00281 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-133" d="M 423.00281 164.28886 L 430.82084 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-134" d="M 430.82084 164.28886 L 440.20711 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-135" d="M 440.20711 164.28886 L 440.76848 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-136" d="M 440.76848 164.28886 L 445.57914 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-137" d="M 445.57914 164.28886 L 464.38314 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-138" d="M 464.38314 164.28886 L 467.82443 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-139" d="M 164.67569 164.28886 L 164.67569 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-140" d="M 164.67569 142.86659 L 165.61347 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-141" d="M 165.61347 142.86659 L 167.86094 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-142" d="M 167.86094 142.86659 L 178.54342 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-143" d="M 178.54342 142.86659 L 179.39059 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-144" d="M 179.39059 142.86659 L 234.8268 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-145" d="M 234.8268 142.86659 L 264.70226 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-146" d="M 264.70226 142.86659 L 265.62443 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-147" d="M 265.62443 142.86659 L 285.70686 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-148" d="M 285.70686 142.86659 L 294.24627 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-149" d="M 294.24627 142.86659 L 300.26681 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-150" d="M 300.26681 142.86659 L 304.60592 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-151" d="M 304.60592 142.86659 L 355.15162 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-152" d="M 355.15162 142.86659 L 370.13865 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-153" d="M 370.13865 142.86659 L 374.12484 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-154" d="M 374.12484 142.86659 L 385.09103 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-155" d="M 385.09103 142.86659 L 409.12543 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-156" d="M 409.12543 142.86659 L 431.64491 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-157" d="M 431.64491 142.86659 L 449.10147 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-158" d="M 449.10147 142.86659 L 450.24921 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-159" d="M 450.24921 142.86659 L 450.85555 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-160" d="M 450.85555 142.86659 L 465.86568 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-161" d="M 465.86568 142.86659 L 467.82443 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-162" d="M 164.67569 142.86659 L 164.67569 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-163" d="M 240.46288 121.44431 L 268.48402 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-164" d="M 268.48402 121.44431 L 295.60795 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-165" d="M 295.60795 121.44431 L 299.23398 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-166" d="M 299.23398 121.44431 L 307.41079 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-167" d="M 307.41079 121.44431 L 309.56198 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-168" d="M 309.56198 121.44431 L 314.18141 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-169" d="M 314.18141 121.44431 L 375.16039 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-170" d="M 375.16039 121.44431 L 377.93023 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-171" d="M 377.93023 121.44431 L 399.83818 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-172" d="M 399.83818 121.44431 L 406.57468 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-173" d="M 406.57468 121.44431 L 445.98945 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-174" d="M 445.98945 121.44431 L 467.82443 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-175" d="M 240.46288 121.44431 L 240.46288 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-176" d="M 316.25006 100.02204 L 326.83728 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-177" d="M 326.83728 100.02204 L 347.34524 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-178" d="M 347.34524 100.02204 L 357.52379 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-179" d="M 357.52379 100.02204 L 387.42385 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-180" d="M 387.42385 100.02204 L 392.97435 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-181" d="M 392.97435 100.02204 L 397.28283 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-182" d="M 397.28283 100.02204 L 405.29768 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-183" d="M 405.29768 100.02204 L 441.61553 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-184" d="M 441.61553 100.02204 L 453.32396 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-185" d="M 453.32396 100.02204 L 461.46847 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-186" d="M 461.46847 100.02204 L 462.03587 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-187" d="M 462.03587 100.02204 L 467.82443 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-188" d="M 316.25006 100.02204 L 316.25006 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-189" d="M 392.03725 78.599759 L 408.16943 78.599759" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-190" d="M 408.16943 78.599759 L 414.92409 78.599759" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-191" d="M 414.92409 78.599759 L 446.62211 78.599759" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-192" d="M 446.62211 78.599759 L 467.82443 78.599759" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-193" d="M 392.03725 78.599759 L 392.03725 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-194" d="M 392.03725 57.177484 L 393.53524 57.177484" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-195" d="M 393.53524 57.177484 L 396.30735 57.177484" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-196" d="M 396.30735 57.177484 L 463.69563 57.177484" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-197" d="M 463.69563 57.177484 L 467.82443 57.177484" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-198" d="M 392.03725 57.177484 L 392.03725 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-199" d="M 164.67569 239.26683 L 170.34419 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-200" d="M 170.34419 239.26683 L 171.04419 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-201" d="M 171.04419 239.26683 L 204.25862 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-202" d="M 204.25862 239.26683 L 204.48428 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-203" d="M 204.48428 239.26683 L 209.81104 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-204" d="M 209.81104 239.26683 L 220.20338 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-205" d="M 220.20338 239.26683 L 238.79091 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-206" d="M 238.79091 239.26683 L 240.46288 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-207" d="M 164.67569 239.26683 L 164.67569 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-208" d="M 88.888508 255.33353 L 100.09197 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-209" d="M 100.09197 255.33353 L 104.6439 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-210" d="M 104.6439 255.33353 L 109.09556 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-211" d="M 109.09556 255.33353 L 119.04584 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-212" d="M 119.04584 255.33353 L 143.00626 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-213" d="M 143.00626 255.33353 L 152.1055 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-214" d="M 152.1055 255.33353 L 164.67569 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-215" d="M 88.888508 255.33353 L 88.888508 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-216" d="M 50.994915 274.07803 L 59.291451 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-217" d="M 59.291451 274.07803 L 84.864253 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-218" d="M 84.864253 274.07803 L 88.888508 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-219" d="M 50.994915 274.07803 L 50.994915 212.82371" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-220" d="M 164.67569 196.42228 L 190.95316 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-221" d="M 190.95316 196.42228 L 209.49884 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-222" d="M 209.49884 196.42228 L 216.07328 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-223" d="M 216.07328 196.42228 L 240.46288 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-224" d="M 164.67569 196.42228 L 164.67569 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-225" d="M 88.888508 180.35557 L 92.35779 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-226" d="M 92.35779 180.35557 L 102.66895 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-227" d="M 102.66895 180.35557 L 104.58185 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-228" d="M 104.58185 180.35557 L 116.99569 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-229" d="M 116.99569 180.35557 L 123.06093 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-230" d="M 123.06093 180.35557 L 126.23798 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-231" d="M 126.23798 180.35557 L 148.13559 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-232" d="M 148.13559 180.35557 L 164.67569 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-233" d="M 88.888508 180.35557 L 88.888508 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-234" d="M 316.25006 67.888622 L 346.2476 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-235" d="M 346.2476 67.888622 L 354.62748 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-236" d="M 354.62748 67.888622 L 359.7008 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-237" d="M 359.7008 67.888622 L 360.01325 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-238" d="M 360.01325 67.888622 L 361.23662 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-239" d="M 361.23662 67.888622 L 384.57831 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-240" d="M 384.57831 67.888622 L 388.26664 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-241" d="M 388.26664 67.888622 L 392.03725 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-242" d="M 316.25006 67.888622 L 316.25006 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-243" d="M 240.46288 83.955328 L 243.52072 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-244" d="M 243.52072 83.955328 L 268.85918 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-245" d="M 268.85918 83.955328 L 316.25006 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-246" d="M 240.46288 83.955328 L 240.46288 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-247" d="M 164.67569 102.69982 L 167.63612 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-248" d="M 167.63612 102.69982 L 168.15452 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-249" d="M 168.15452 102.69982 L 174.69086 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-250" d="M 174.69086 102.69982 L 178.88918 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-251" d="M 178.88918 102.69982 L 202.6918 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-252" d="M 202.6918 102.69982 L 224.19378 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-253" d="M 224.19378 102.69982 L 224.48098 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-254" d="M 224.48098 102.69982 L 240.46288 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-255" d="M 164.67569 102.69982 L 164.67569 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-256" d="M 88.888508 122.7832 L 89.060963 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-257" d="M 89.060963 122.7832 L 92.64311 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-258" d="M 92.64311 122.7832 L 103.60776 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-259" d="M 103.60776 122.7832 L 108.79855 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-260" d="M 108.79855 122.7832 L 130.80982 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-261" d="M 130.80982 122.7832 L 159.42938 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-262" d="M 159.42938 122.7832 L 164.67569 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-263" d="M 88.888508 122.7832 L 88.888508 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-264" d="M 50.994915 151.56939 L 60.969156 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-265" d="M 60.969156 151.56939 L 69.899827 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-266" d="M 69.899827 151.56939 L 79.863353 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-267" d="M 79.863353 151.56939 L 83.809686 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-268" d="M 83.809686 151.56939 L 84.177325 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-269" d="M 84.177325 151.56939 L 88.888508 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-270" d="M 50.994915 151.56939 L 50.994915 212.82371" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path></g><g class="toytree-Annotation-Markers" id="t7668732dd7154039953b0cc824a2599f" style="stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Mark-0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0" transform="translate(467.824,292.823)"><circle r="5.0"></circle></g><g id="Mark-1" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0" transform="translate(467.824,271.4)"><circle r="5.0"></circle></g><g id="Mark-2" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,249.978)"><circle r="5.0"></circle></g><g id="Mark-3" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0" transform="translate(467.824,228.556)"><circle r="5.0"></circle></g><g id="Mark-4" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0" transform="translate(467.824,207.133)"><circle r="5.0"></circle></g><g id="Mark-5" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0" transform="translate(467.824,185.711)"><circle r="5.0"></circle></g><g id="Mark-6" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,164.289)"><circle r="5.0"></circle></g><g id="Mark-7" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0" transform="translate(467.824,142.867)"><circle r="5.0"></circle></g><g id="Mark-8" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0" transform="translate(467.824,121.444)"><circle r="5.0"></circle></g><g id="Mark-9" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,100.022)"><circle r="5.0"></circle></g><g id="Mark-10" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0" transform="translate(467.824,78.5998)"><circle r="5.0"></circle></g><g id="Mark-11" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,57.1775)"><circle r="5.0"></circle></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


The colored edge segments show the sampled state through time. This is one possible history, not a single best reconstruction. Repeating the mapping samples alternative histories that are also compatible with the model and data.

## Interpret Statistics

In addition to the `segments` table, the `PCMStochasticMapResult` object also stores several summary properties computed across replicates maps. 

### `dwell`
The `dwell` table reports total branch time spent in each state for each map replicate.


```python
result.dwell.head(9)
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
      <th>map_id</th>
      <th>state_idx</th>
      <th>state</th>
      <th>total_time</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>0</td>
      <td>A</td>
      <td>2.534975</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>1</td>
      <td>B</td>
      <td>2.898691</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0</td>
      <td>2</td>
      <td>C</td>
      <td>2.748153</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1</td>
      <td>0</td>
      <td>A</td>
      <td>2.440524</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1</td>
      <td>1</td>
      <td>B</td>
      <td>2.726810</td>
    </tr>
    <tr>
      <th>5</th>
      <td>1</td>
      <td>2</td>
      <td>C</td>
      <td>3.014484</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2</td>
      <td>0</td>
      <td>A</td>
      <td>2.997069</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2</td>
      <td>1</td>
      <td>B</td>
      <td>2.518279</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2</td>
      <td>2</td>
      <td>C</td>
      <td>2.666470</td>
    </tr>
  </tbody>
</table>
</div>



### ``dwell_stats``

The `dwell_stats` table summarizes dwell times across replicate simulations.

Dwell time is measured in the same units as branch lengths. Averaging over replicates gives a compact summary of sampled histories, while the variation among replicates shows uncertainty in those histories.


```python
result.dwell_stats.round(3)
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
      <th>state_idx</th>
      <th>state</th>
      <th>mean_total_time</th>
      <th>sd_total_time</th>
      <th>q025_total_time</th>
      <th>q50_total_time</th>
      <th>q975_total_time</th>
      <th>prob_nonzero_total_time</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>A</td>
      <td>2.602</td>
      <td>0.288</td>
      <td>2.208</td>
      <td>2.571</td>
      <td>2.995</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>B</td>
      <td>2.713</td>
      <td>0.307</td>
      <td>2.190</td>
      <td>2.721</td>
      <td>3.170</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>C</td>
      <td>2.867</td>
      <td>0.327</td>
      <td>2.384</td>
      <td>2.809</td>
      <td>3.353</td>
      <td>1.0</td>
    </tr>
  </tbody>
</table>
</div>



### ``transition_stats``

Transition counts are sampled events, not fitted rate parameters. A large count for one state change means that transition occurred often in the sampled histories. It does not by itself imply a high instantaneous rate unless branch lengths, state frequencies, and model uncertainty are also considered.


```python
result.transition_stats.round(3)
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
      <th>from_state_idx</th>
      <th>to_state_idx</th>
      <th>from_state</th>
      <th>to_state</th>
      <th>mean</th>
      <th>sd</th>
      <th>q025</th>
      <th>q50</th>
      <th>q975</th>
      <th>prob_nonzero</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>1</td>
      <td>A</td>
      <td>B</td>
      <td>35.6</td>
      <td>2.271</td>
      <td>33.000</td>
      <td>35.0</td>
      <td>39.000</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>2</td>
      <td>A</td>
      <td>C</td>
      <td>34.8</td>
      <td>5.138</td>
      <td>28.000</td>
      <td>36.0</td>
      <td>42.325</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1</td>
      <td>0</td>
      <td>B</td>
      <td>A</td>
      <td>32.9</td>
      <td>3.381</td>
      <td>29.000</td>
      <td>32.5</td>
      <td>38.550</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1</td>
      <td>2</td>
      <td>B</td>
      <td>C</td>
      <td>35.9</td>
      <td>3.178</td>
      <td>32.225</td>
      <td>35.0</td>
      <td>40.775</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2</td>
      <td>0</td>
      <td>C</td>
      <td>A</td>
      <td>36.7</td>
      <td>4.990</td>
      <td>29.125</td>
      <td>36.5</td>
      <td>44.650</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2</td>
      <td>1</td>
      <td>C</td>
      <td>B</td>
      <td>33.5</td>
      <td>5.255</td>
      <td>24.675</td>
      <td>35.5</td>
      <td>38.775</td>
      <td>1.0</td>
    </tr>
  </tbody>
</table>
</div>



### ``edge_transition_stats``

This table summarizes all possible transition events on each edge of the tree across all simulations. It provides stats to investigate questions like "how frequently did state A change to B on branch 10?". 


```python
result.edge_transition_stats.head(10)
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
      <th>edge_id</th>
      <th>child</th>
      <th>parent</th>
      <th>from_state_idx</th>
      <th>to_state_idx</th>
      <th>from_state</th>
      <th>to_state</th>
      <th>mean</th>
      <th>sd</th>
      <th>q025</th>
      <th>q50</th>
      <th>q975</th>
      <th>prob_nonzero</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>0</td>
      <td>1</td>
      <td>A</td>
      <td>B</td>
      <td>3.6</td>
      <td>1.429841</td>
      <td>1.225</td>
      <td>4.0</td>
      <td>5.775</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>0</td>
      <td>2</td>
      <td>A</td>
      <td>C</td>
      <td>3.9</td>
      <td>2.233582</td>
      <td>0.225</td>
      <td>4.0</td>
      <td>6.775</td>
      <td>0.9</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>1</td>
      <td>0</td>
      <td>B</td>
      <td>A</td>
      <td>3.5</td>
      <td>1.080123</td>
      <td>3.000</td>
      <td>3.0</td>
      <td>5.775</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>1</td>
      <td>2</td>
      <td>B</td>
      <td>C</td>
      <td>4.3</td>
      <td>1.059350</td>
      <td>3.000</td>
      <td>4.0</td>
      <td>6.000</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>2</td>
      <td>0</td>
      <td>C</td>
      <td>A</td>
      <td>4.6</td>
      <td>2.674987</td>
      <td>0.225</td>
      <td>4.5</td>
      <td>8.000</td>
      <td>0.9</td>
    </tr>
    <tr>
      <th>5</th>
      <td>0</td>
      <td>0</td>
      <td>14</td>
      <td>2</td>
      <td>1</td>
      <td>C</td>
      <td>B</td>
      <td>3.9</td>
      <td>1.370320</td>
      <td>2.000</td>
      <td>4.0</td>
      <td>5.775</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>6</th>
      <td>1</td>
      <td>1</td>
      <td>13</td>
      <td>0</td>
      <td>1</td>
      <td>A</td>
      <td>B</td>
      <td>2.5</td>
      <td>1.509231</td>
      <td>1.000</td>
      <td>2.5</td>
      <td>5.325</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>7</th>
      <td>1</td>
      <td>1</td>
      <td>13</td>
      <td>0</td>
      <td>2</td>
      <td>A</td>
      <td>C</td>
      <td>3.3</td>
      <td>2.110819</td>
      <td>0.225</td>
      <td>3.0</td>
      <td>6.775</td>
      <td>0.9</td>
    </tr>
    <tr>
      <th>8</th>
      <td>1</td>
      <td>1</td>
      <td>13</td>
      <td>1</td>
      <td>0</td>
      <td>B</td>
      <td>A</td>
      <td>2.5</td>
      <td>1.178511</td>
      <td>1.000</td>
      <td>2.5</td>
      <td>4.550</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>9</th>
      <td>1</td>
      <td>1</td>
      <td>13</td>
      <td>1</td>
      <td>2</td>
      <td>B</td>
      <td>C</td>
      <td>3.1</td>
      <td>1.449138</td>
      <td>1.000</td>
      <td>3.0</td>
      <td>5.000</td>
      <td>1.0</td>
    </tr>
  </tbody>
</table>
</div>



## Replicates and `map_id`

Increasing `nreplicates` gives more sampled histories. The `map_id` key is also useful for further examining statistics across replicates.


```python
replicate_dwell = (
    result.dwell.pivot(index="map_id", columns="state", values="total_time")
    .round(3)
)
replicate_dwell
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
      <th>state</th>
      <th>A</th>
      <th>B</th>
      <th>C</th>
    </tr>
    <tr>
      <th>map_id</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>2.535</td>
      <td>2.899</td>
      <td>2.748</td>
    </tr>
    <tr>
      <th>1</th>
      <td>2.441</td>
      <td>2.727</td>
      <td>3.014</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2.997</td>
      <td>2.518</td>
      <td>2.666</td>
    </tr>
    <tr>
      <th>3</th>
      <td>2.171</td>
      <td>2.843</td>
      <td>3.168</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2.716</td>
      <td>2.716</td>
      <td>2.750</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2.352</td>
      <td>2.962</td>
      <td>2.868</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2.607</td>
      <td>3.231</td>
      <td>2.344</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2.880</td>
      <td>2.117</td>
      <td>3.186</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2.337</td>
      <td>2.443</td>
      <td>3.402</td>
    </tr>
    <tr>
      <th>9</th>
      <td>2.989</td>
      <td>2.672</td>
      <td>2.521</td>
    </tr>
  </tbody>
</table>
</div>



Also use `map_id` to select which replicate to draw. Compared to the drawing above, this uses the same tree, observations, and fitted model, but a different `map_id`. Differences among replicates represent uncertainty in where transitions occurred and which states occupied unsampled parts of the tree.


```python
canvas, axes, mark = tree.draw(width=550, height=350)
tree.annotate.add_edge_stochastic_map(
    axes,
    data=result,
    map_id=1,
    color="Set2",
    width=4,
);
tree.annotate.add_tip_markers(axes, color=("X", "Set2"), size=10);
```


<div class="toyplot" id="tce862fb6730043c4845c7c70bd83ce3e" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="550.0px" height="350.0px" viewBox="0 0 550.0 350.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t023ab2beacf24c5c865550ce2699c861"><g class="toyplot-coordinates-Cartesian" id="tccd41b3318904bb8b51baf8410b7bc1c"><clipPath id="tb3ca5c7b81584c0b948ddd1a9ec125c0"><rect x="35.0" y="35.0" width="480.0" height="280.0"></rect></clipPath><g clip-path="url(#tb3ca5c7b81584c0b948ddd1a9ec125c0)"><g class="toytree-mark-Toytree" id="tcf9bf162af754a2f89627745be30d0aa"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 88.9 274.1 L 88.9 292.8 L 467.8 292.8" id="14,0" style=""></path><path d="M 164.7 255.3 L 164.7 271.4 L 467.8 271.4" id="13,1" style=""></path><path d="M 240.5 239.3 L 240.5 250.0 L 467.8 250.0" id="12,2" style=""></path><path d="M 240.5 239.3 L 240.5 228.6 L 467.8 228.6" id="12,3" style=""></path><path d="M 240.5 196.4 L 240.5 207.1 L 467.8 207.1" id="15,4" style=""></path><path d="M 240.5 196.4 L 240.5 185.7 L 467.8 185.7" id="15,5" style=""></path><path d="M 164.7 180.4 L 164.7 164.3 L 467.8 164.3" id="16,6" style=""></path><path d="M 164.7 122.8 L 164.7 142.9 L 467.8 142.9" id="20,7" style=""></path><path d="M 240.5 102.7 L 240.5 121.4 L 467.8 121.4" id="19,8" style=""></path><path d="M 316.3 84.0 L 316.3 100.0 L 467.8 100.0" id="18,9" style=""></path><path d="M 392.0 67.9 L 392.0 78.6 L 467.8 78.6" id="17,10" style=""></path><path d="M 392.0 67.9 L 392.0 57.2 L 467.8 57.2" id="17,11" style=""></path><path d="M 164.7 255.3 L 164.7 239.3 L 240.5 239.3" id="13,12" style=""></path><path d="M 88.9 274.1 L 88.9 255.3 L 164.7 255.3" id="14,13" style=""></path><path d="M 51.0 212.8 L 51.0 274.1 L 88.9 274.1" id="22,14" style=""></path><path d="M 164.7 180.4 L 164.7 196.4 L 240.5 196.4" id="16,15" style=""></path><path d="M 88.9 151.6 L 88.9 180.4 L 164.7 180.4" id="21,16" style=""></path><path d="M 316.3 84.0 L 316.3 67.9 L 392.0 67.9" id="18,17" style=""></path><path d="M 240.5 102.7 L 240.5 84.0 L 316.3 84.0" id="19,18" style=""></path><path d="M 164.7 122.8 L 164.7 102.7 L 240.5 102.7" id="20,19" style=""></path><path d="M 88.9 151.6 L 88.9 122.8 L 164.7 122.8" id="21,20" style=""></path><path d="M 51.0 212.8 L 51.0 151.6 L 88.9 151.6" id="22,21" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(467.824,292.823)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(467.824,271.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(467.824,249.978)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(467.824,228.556)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(467.824,207.133)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(467.824,185.711)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(467.824,164.289)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(467.824,142.867)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(467.824,121.444)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(467.824,100.022)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g><g class="toytree-TipLabel" transform="translate(467.824,78.5998)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r10</text></g><g class="toytree-TipLabel" transform="translate(467.824,57.1775)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r11</text></g></g></g><g class="toytree-Annotation-Lines" id="ta420128345be4fa3a2564227f42e27ed" style="stroke-linecap:butt"><path id="Line-0" d="M 88.888508 292.82252 L 92.932428 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-1" d="M 92.932428 292.82252 L 100.12473 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-2" d="M 100.12473 292.82252 L 103.87326 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-3" d="M 103.87326 292.82252 L 113.53809 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-4" d="M 113.53809 292.82252 L 117.37796 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-5" d="M 117.37796 292.82252 L 163.09925 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-6" d="M 163.09925 292.82252 L 205.14732 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-7" d="M 205.14732 292.82252 L 251.89546 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-8" d="M 251.89546 292.82252 L 255.31359 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-9" d="M 255.31359 292.82252 L 268.79551 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-10" d="M 268.79551 292.82252 L 280.75974 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-11" d="M 280.75974 292.82252 L 284.6997 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-12" d="M 284.6997 292.82252 L 289.6536 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-13" d="M 289.6536 292.82252 L 311.21432 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-14" d="M 311.21432 292.82252 L 331.32376 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-15" d="M 331.32376 292.82252 L 332.83704 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-16" d="M 332.83704 292.82252 L 333.69516 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-17" d="M 333.69516 292.82252 L 334.09015 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-18" d="M 334.09015 292.82252 L 367.02402 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-19" d="M 367.02402 292.82252 L 372.01325 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-20" d="M 372.01325 292.82252 L 386.01879 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-21" d="M 386.01879 292.82252 L 400.30472 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-22" d="M 400.30472 292.82252 L 408.86173 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-23" d="M 408.86173 292.82252 L 412.19609 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-24" d="M 412.19609 292.82252 L 428.82876 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-25" d="M 428.82876 292.82252 L 440.82548 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-26" d="M 440.82548 292.82252 L 454.95599 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-27" d="M 454.95599 292.82252 L 457.50395 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-28" d="M 457.50395 292.82252 L 467.82443 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-29" d="M 88.888508 292.82252 L 88.888508 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-30" d="M 164.67569 271.40024 L 172.49103 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-31" d="M 172.49103 271.40024 L 183.84484 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-32" d="M 183.84484 271.40024 L 190.77469 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-33" d="M 190.77469 271.40024 L 201.52316 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-34" d="M 201.52316 271.40024 L 214.73554 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-35" d="M 214.73554 271.40024 L 225.11889 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-36" d="M 225.11889 271.40024 L 234.34227 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-37" d="M 234.34227 271.40024 L 249.41619 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-38" d="M 249.41619 271.40024 L 251.21755 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-39" d="M 251.21755 271.40024 L 265.52016 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-40" d="M 265.52016 271.40024 L 290.81637 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-41" d="M 290.81637 271.40024 L 290.93963 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-42" d="M 290.93963 271.40024 L 294.3417 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-43" d="M 294.3417 271.40024 L 315.9674 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-44" d="M 315.9674 271.40024 L 362.72012 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-45" d="M 362.72012 271.40024 L 362.74742 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-46" d="M 362.74742 271.40024 L 385.08186 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-47" d="M 385.08186 271.40024 L 465.22405 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-48" d="M 465.22405 271.40024 L 467.82443 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-49" d="M 164.67569 271.40024 L 164.67569 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-50" d="M 240.46288 249.97796 L 243.64975 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-51" d="M 243.64975 249.97796 L 257.24203 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-52" d="M 257.24203 249.97796 L 258.96707 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-53" d="M 258.96707 249.97796 L 277.02239 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-54" d="M 277.02239 249.97796 L 289.47213 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-55" d="M 289.47213 249.97796 L 304.95287 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-56" d="M 304.95287 249.97796 L 305.74091 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-57" d="M 305.74091 249.97796 L 308.59701 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-58" d="M 308.59701 249.97796 L 309.3142 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-59" d="M 309.3142 249.97796 L 333.72816 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-60" d="M 333.72816 249.97796 L 351.18062 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-61" d="M 351.18062 249.97796 L 353.7502 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-62" d="M 353.7502 249.97796 L 369.61978 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-63" d="M 369.61978 249.97796 L 392.08133 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-64" d="M 392.08133 249.97796 L 395.8601 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-65" d="M 395.8601 249.97796 L 402.67017 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-66" d="M 402.67017 249.97796 L 410.07353 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-67" d="M 410.07353 249.97796 L 419.79911 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-68" d="M 419.79911 249.97796 L 467.82443 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-69" d="M 240.46288 249.97796 L 240.46288 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-70" d="M 240.46288 228.55569 L 252.08616 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-71" d="M 252.08616 228.55569 L 263.61627 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-72" d="M 263.61627 228.55569 L 274.84802 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-73" d="M 274.84802 228.55569 L 281.82963 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-74" d="M 281.82963 228.55569 L 282.42176 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-75" d="M 282.42176 228.55569 L 315.35068 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-76" d="M 315.35068 228.55569 L 339.68887 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-77" d="M 339.68887 228.55569 L 428.86245 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-78" d="M 428.86245 228.55569 L 436.06247 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-79" d="M 436.06247 228.55569 L 446.54941 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-80" d="M 446.54941 228.55569 L 467.38834 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-81" d="M 467.38834 228.55569 L 467.82443 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-82" d="M 240.46288 228.55569 L 240.46288 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-83" d="M 240.46288 207.13341 L 260.72967 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-84" d="M 260.72967 207.13341 L 266.96093 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-85" d="M 266.96093 207.13341 L 309.87984 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-86" d="M 309.87984 207.13341 L 313.10704 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-87" d="M 313.10704 207.13341 L 334.75008 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-88" d="M 334.75008 207.13341 L 354.64271 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-89" d="M 354.64271 207.13341 L 388.05585 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-90" d="M 388.05585 207.13341 L 429.31135 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-91" d="M 429.31135 207.13341 L 430.47769 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-92" d="M 430.47769 207.13341 L 460.31512 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-93" d="M 460.31512 207.13341 L 463.17857 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-94" d="M 463.17857 207.13341 L 467.82443 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-95" d="M 240.46288 207.13341 L 240.46288 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-96" d="M 240.46288 185.71114 L 241.2474 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-97" d="M 241.2474 185.71114 L 270.46016 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-98" d="M 270.46016 185.71114 L 272.42528 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-99" d="M 272.42528 185.71114 L 274.27436 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-100" d="M 274.27436 185.71114 L 296.00624 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-101" d="M 296.00624 185.71114 L 300.99417 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-102" d="M 300.99417 185.71114 L 301.23769 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-103" d="M 301.23769 185.71114 L 302.01828 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-104" d="M 302.01828 185.71114 L 307.78767 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-105" d="M 307.78767 185.71114 L 314.67449 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-106" d="M 314.67449 185.71114 L 373.30912 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-107" d="M 373.30912 185.71114 L 376.8187 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-108" d="M 376.8187 185.71114 L 379.64144 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-109" d="M 379.64144 185.71114 L 385.07312 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-110" d="M 385.07312 185.71114 L 386.96448 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-111" d="M 386.96448 185.71114 L 391.0912 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-112" d="M 391.0912 185.71114 L 404.08124 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-113" d="M 404.08124 185.71114 L 404.82554 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-114" d="M 404.82554 185.71114 L 438.22848 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-115" d="M 438.22848 185.71114 L 452.59281 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-116" d="M 452.59281 185.71114 L 454.60359 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-117" d="M 454.60359 185.71114 L 467.82443 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-118" d="M 240.46288 185.71114 L 240.46288 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-119" d="M 164.67569 164.28886 L 166.49835 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-120" d="M 166.49835 164.28886 L 172.73791 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-121" d="M 172.73791 164.28886 L 188.3749 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-122" d="M 188.3749 164.28886 L 196.50177 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-123" d="M 196.50177 164.28886 L 211.63325 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-124" d="M 211.63325 164.28886 L 222.44537 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-125" d="M 222.44537 164.28886 L 236.95746 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-126" d="M 236.95746 164.28886 L 241.5081 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-127" d="M 241.5081 164.28886 L 249.52352 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-128" d="M 249.52352 164.28886 L 290.341 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-129" d="M 290.341 164.28886 L 303.01857 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-130" d="M 303.01857 164.28886 L 355.76987 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-131" d="M 355.76987 164.28886 L 361.12429 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-132" d="M 361.12429 164.28886 L 380.1954 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-133" d="M 380.1954 164.28886 L 389.15464 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-134" d="M 389.15464 164.28886 L 400.69568 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-135" d="M 400.69568 164.28886 L 405.69461 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-136" d="M 405.69461 164.28886 L 427.00954 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-137" d="M 427.00954 164.28886 L 429.08284 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-138" d="M 429.08284 164.28886 L 430.22298 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-139" d="M 430.22298 164.28886 L 432.0824 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-140" d="M 432.0824 164.28886 L 447.80844 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-141" d="M 447.80844 164.28886 L 454.55824 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-142" d="M 454.55824 164.28886 L 467.82443 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-143" d="M 164.67569 164.28886 L 164.67569 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-144" d="M 164.67569 142.86659 L 176.30426 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-145" d="M 176.30426 142.86659 L 183.16062 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-146" d="M 183.16062 142.86659 L 195.44759 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-147" d="M 195.44759 142.86659 L 268.08721 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-148" d="M 268.08721 142.86659 L 269.48511 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-149" d="M 269.48511 142.86659 L 293.41001 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-150" d="M 293.41001 142.86659 L 308.51427 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-151" d="M 308.51427 142.86659 L 317.24395 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-152" d="M 317.24395 142.86659 L 319.56996 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-153" d="M 319.56996 142.86659 L 320.5592 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-154" d="M 320.5592 142.86659 L 335.3998 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-155" d="M 335.3998 142.86659 L 358.6274 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-156" d="M 358.6274 142.86659 L 361.08487 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-157" d="M 361.08487 142.86659 L 362.23657 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-158" d="M 362.23657 142.86659 L 379.10784 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-159" d="M 379.10784 142.86659 L 392.57947 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-160" d="M 392.57947 142.86659 L 412.35654 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-161" d="M 412.35654 142.86659 L 448.04024 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-162" d="M 448.04024 142.86659 L 465.37991 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-163" d="M 465.37991 142.86659 L 467.82443 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-164" d="M 164.67569 142.86659 L 164.67569 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-165" d="M 240.46288 121.44431 L 241.35223 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-166" d="M 241.35223 121.44431 L 245.18395 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-167" d="M 245.18395 121.44431 L 260.64401 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-168" d="M 260.64401 121.44431 L 267.44811 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-169" d="M 267.44811 121.44431 L 274.59236 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-170" d="M 274.59236 121.44431 L 287.36932 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-171" d="M 287.36932 121.44431 L 296.59705 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-172" d="M 296.59705 121.44431 L 306.87718 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-173" d="M 306.87718 121.44431 L 310.36591 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-174" d="M 310.36591 121.44431 L 336.38609 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-175" d="M 336.38609 121.44431 L 348.26294 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-176" d="M 348.26294 121.44431 L 348.2845 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-177" d="M 348.2845 121.44431 L 440.96587 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-178" d="M 440.96587 121.44431 L 465.03135 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-179" d="M 465.03135 121.44431 L 467.82443 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-180" d="M 240.46288 121.44431 L 240.46288 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-181" d="M 316.25006 100.02204 L 322.76984 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-182" d="M 322.76984 100.02204 L 354.95767 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-183" d="M 354.95767 100.02204 L 361.85889 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-184" d="M 361.85889 100.02204 L 373.93285 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-185" d="M 373.93285 100.02204 L 380.33667 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-186" d="M 380.33667 100.02204 L 418.16024 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-187" d="M 418.16024 100.02204 L 421.14264 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-188" d="M 421.14264 100.02204 L 457.05015 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-189" d="M 457.05015 100.02204 L 460.1695 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-190" d="M 460.1695 100.02204 L 467.82443 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-191" d="M 316.25006 100.02204 L 316.25006 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-192" d="M 392.03725 78.599759 L 396.49136 78.599759" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-193" d="M 396.49136 78.599759 L 408.74565 78.599759" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-194" d="M 408.74565 78.599759 L 423.13626 78.599759" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-195" d="M 423.13626 78.599759 L 425.93738 78.599759" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-196" d="M 425.93738 78.599759 L 434.02559 78.599759" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-197" d="M 434.02559 78.599759 L 449.43168 78.599759" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-198" d="M 449.43168 78.599759 L 449.92864 78.599759" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-199" d="M 449.92864 78.599759 L 467.82443 78.599759" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-200" d="M 392.03725 78.599759 L 392.03725 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-201" d="M 392.03725 57.177484 L 402.3984 57.177484" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-202" d="M 402.3984 57.177484 L 417.72888 57.177484" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-203" d="M 417.72888 57.177484 L 467.70516 57.177484" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-204" d="M 467.70516 57.177484 L 467.82443 57.177484" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-205" d="M 392.03725 57.177484 L 392.03725 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-206" d="M 164.67569 239.26683 L 170.78139 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-207" d="M 170.78139 239.26683 L 190.04294 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-208" d="M 190.04294 239.26683 L 194.42547 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-209" d="M 194.42547 239.26683 L 227.83935 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-210" d="M 227.83935 239.26683 L 239.15772 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-211" d="M 239.15772 239.26683 L 240.46288 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-212" d="M 164.67569 239.26683 L 164.67569 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-213" d="M 88.888508 255.33353 L 105.37114 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-214" d="M 105.37114 255.33353 L 112.94855 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-215" d="M 112.94855 255.33353 L 131.64253 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-216" d="M 131.64253 255.33353 L 164.67569 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-217" d="M 88.888508 255.33353 L 88.888508 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-218" d="M 50.994915 274.07803 L 56.870128 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-219" d="M 56.870128 274.07803 L 81.436947 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-220" d="M 81.436947 274.07803 L 83.726482 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-221" d="M 83.726482 274.07803 L 86.300307 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-222" d="M 86.300307 274.07803 L 88.888508 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-223" d="M 50.994915 274.07803 L 50.994915 212.82371" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-224" d="M 164.67569 196.42228 L 169.36192 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-225" d="M 169.36192 196.42228 L 170.1473 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-226" d="M 170.1473 196.42228 L 213.76304 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-227" d="M 213.76304 196.42228 L 240.46288 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-228" d="M 164.67569 196.42228 L 164.67569 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-229" d="M 88.888508 180.35557 L 132.54843 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-230" d="M 132.54843 180.35557 L 144.77093 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-231" d="M 144.77093 180.35557 L 157.54603 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-232" d="M 157.54603 180.35557 L 164.67569 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-233" d="M 88.888508 180.35557 L 88.888508 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-234" d="M 316.25006 67.888622 L 322.7044 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-235" d="M 322.7044 67.888622 L 353.17908 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-236" d="M 353.17908 67.888622 L 361.98181 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-237" d="M 361.98181 67.888622 L 387.0888 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-238" d="M 387.0888 67.888622 L 390.55046 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-239" d="M 390.55046 67.888622 L 392.03725 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-240" d="M 316.25006 67.888622 L 316.25006 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-241" d="M 240.46288 83.955328 L 242.54361 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-242" d="M 242.54361 83.955328 L 244.09765 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-243" d="M 244.09765 83.955328 L 259.36081 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-244" d="M 259.36081 83.955328 L 266.04664 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-245" d="M 266.04664 83.955328 L 292.44351 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-246" d="M 292.44351 83.955328 L 316.25006 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-247" d="M 240.46288 83.955328 L 240.46288 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-248" d="M 164.67569 102.69982 L 201.09988 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-249" d="M 201.09988 102.69982 L 205.17084 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-250" d="M 205.17084 102.69982 L 211.9217 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-251" d="M 211.9217 102.69982 L 223.7188 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-252" d="M 223.7188 102.69982 L 237.56096 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-253" d="M 237.56096 102.69982 L 238.31481 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-254" d="M 238.31481 102.69982 L 240.46288 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-255" d="M 164.67569 102.69982 L 164.67569 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-256" d="M 88.888508 122.7832 L 118.13072 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-257" d="M 118.13072 122.7832 L 136.24794 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-258" d="M 136.24794 122.7832 L 154.03136 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-259" d="M 154.03136 122.7832 L 158.83842 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-260" d="M 158.83842 122.7832 L 164.67569 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-261" d="M 88.888508 122.7832 L 88.888508 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-262" d="M 50.994915 151.56939 L 57.074118 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-263" d="M 57.074118 151.56939 L 67.388726 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-264" d="M 67.388726 151.56939 L 73.237938 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-265" d="M 73.237938 151.56939 L 85.042572 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-266" d="M 85.042572 151.56939 L 88.888508 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-267" d="M 50.994915 151.56939 L 50.994915 212.82371" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path></g><g class="toytree-Annotation-Markers" id="ta8e4482599874a859558e9e598115178" style="stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Mark-0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0" transform="translate(467.824,292.823)"><circle r="5.0"></circle></g><g id="Mark-1" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0" transform="translate(467.824,271.4)"><circle r="5.0"></circle></g><g id="Mark-2" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,249.978)"><circle r="5.0"></circle></g><g id="Mark-3" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0" transform="translate(467.824,228.556)"><circle r="5.0"></circle></g><g id="Mark-4" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0" transform="translate(467.824,207.133)"><circle r="5.0"></circle></g><g id="Mark-5" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0" transform="translate(467.824,185.711)"><circle r="5.0"></circle></g><g id="Mark-6" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,164.289)"><circle r="5.0"></circle></g><g id="Mark-7" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0" transform="translate(467.824,142.867)"><circle r="5.0"></circle></g><g id="Mark-8" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0" transform="translate(467.824,121.444)"><circle r="5.0"></circle></g><g id="Mark-9" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,100.022)"><circle r="5.0"></circle></g><g id="Mark-10" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0" transform="translate(467.824,78.5998)"><circle r="5.0"></circle></g><g id="Mark-11" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,57.1775)"><circle r="5.0"></circle></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Branch-Specific Gains

A common use of stochastic maps is to estimate how often a particular transition occurred on a particular branch. In this example a rare derived trait appears in two separated clades, suggesting that it evolved twice. We will ask how often stochastic maps place a transition to the derived state on the branch subtending one of those clades.

We compare an `ER` model to an `ARD` model. The `ARD` model allows asymmetric transition rates. For binary data this is a gain-loss model with different forward and reverse rates.


```python
# set derived state in two clades
derived_tips = {"r2", "r3", "r10", "r11"}
btree = tree.set_node_data(
    feature="rare_trait",
    data={i: "derived" if i in derived_tips else "ancestral" for i in tree.get_tip_labels()},
    default=np.nan,
)

# select a focal edge
target_node = btree.get_mrca_node("r2", "r3")
```


```python
# set vectors of edge colors and widths in node idx order
edge_colors = ["darkorange" if node.idx == target_node.idx else "black" for node in btree]
edge_widths = [5 if node.idx == target_node.idx else 2 for node in btree]

# draw the tree with tip states and focal edge highlighted
canvas, axes, mark = btree.draw(
    width=550,
    height=350,
    node_sizes=10,
    node_mask=(1, 0, 0),
    node_colors=("rare_trait", "Set2"),
    edge_colors=edge_colors,
    edge_widths=edge_widths,
)
```


<div class="toyplot" id="t86294e1ddbc749bfb26dff003f50fd7a" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="550.0px" height="350.0px" viewBox="0 0 550.0 350.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="ta36211d5a1e343479ada431ddf835690"><g class="toyplot-coordinates-Cartesian" id="t1fd2fb22f1154fb4a4f95866e8171f8a"><clipPath id="te6e9679e73aa482181cc34a7aa67079e"><rect x="35.0" y="35.0" width="480.0" height="280.0"></rect></clipPath><g clip-path="url(#te6e9679e73aa482181cc34a7aa67079e)"><g class="toytree-mark-Toytree" id="t76eda17c59194a8695a206d72b9bd94a"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 93.9 274.1 L 93.9 292.8 L 467.9 292.8" id="14,0" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 168.7 255.3 L 168.7 271.4 L 467.9 271.4" id="13,1" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 243.5 239.3 L 243.5 250.0 L 467.9 250.0" id="12,2" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 243.5 239.3 L 243.5 228.6 L 467.9 228.6" id="12,3" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 243.5 196.4 L 243.5 207.1 L 467.9 207.1" id="15,4" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 243.5 196.4 L 243.5 185.7 L 467.9 185.7" id="15,5" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 168.7 180.4 L 168.7 164.3 L 467.9 164.3" id="16,6" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 168.7 122.8 L 168.7 142.9 L 467.9 142.9" id="20,7" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 243.5 102.7 L 243.5 121.4 L 467.9 121.4" id="19,8" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 318.3 84.0 L 318.3 100.0 L 467.9 100.0" id="18,9" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 393.1 67.9 L 393.1 78.6 L 467.9 78.6" id="17,10" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 393.1 67.9 L 393.1 57.2 L 467.9 57.2" id="17,11" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 168.7 255.3 L 168.7 239.3 L 243.5 239.3" id="13,12" style="stroke:rgb(100.0%,54.9%,0.0%);stroke-opacity:1.0;stroke-width:5"></path><path d="M 93.9 274.1 L 93.9 255.3 L 168.7 255.3" id="14,13" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 56.5 212.8 L 56.5 274.1 L 93.9 274.1" id="22,14" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 168.7 180.4 L 168.7 196.4 L 243.5 196.4" id="16,15" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 93.9 151.6 L 93.9 180.4 L 168.7 180.4" id="21,16" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 318.3 84.0 L 318.3 67.9 L 393.1 67.9" id="18,17" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 243.5 102.7 L 243.5 84.0 L 318.3 84.0" id="19,18" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 168.7 122.8 L 168.7 102.7 L 243.5 102.7" id="20,19" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 93.9 151.6 L 93.9 122.8 L 168.7 122.8" id="21,20" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 56.5 212.8 L 56.5 151.6 L 93.9 151.6" id="22,21" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(467.88,292.823)"><circle r="5.0"></circle></g><g id="Node-1" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(467.88,271.4)"><circle r="5.0"></circle></g><g id="Node-2" style="fill:rgb(98.8%,55.3%,38.4%)" transform="translate(467.88,249.978)"><circle r="5.0"></circle></g><g id="Node-3" style="fill:rgb(98.8%,55.3%,38.4%)" transform="translate(467.88,228.556)"><circle r="5.0"></circle></g><g id="Node-4" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(467.88,207.133)"><circle r="5.0"></circle></g><g id="Node-5" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(467.88,185.711)"><circle r="5.0"></circle></g><g id="Node-6" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(467.88,164.289)"><circle r="5.0"></circle></g><g id="Node-7" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(467.88,142.867)"><circle r="5.0"></circle></g><g id="Node-8" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(467.88,121.444)"><circle r="5.0"></circle></g><g id="Node-9" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(467.88,100.022)"><circle r="5.0"></circle></g><g id="Node-10" style="fill:rgb(98.8%,55.3%,38.4%)" transform="translate(467.88,78.5998)"><circle r="5.0"></circle></g><g id="Node-11" style="fill:rgb(98.8%,55.3%,38.4%)" transform="translate(467.88,57.1775)"><circle r="5.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(467.88,292.823)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(467.88,271.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(467.88,249.978)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(467.88,228.556)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(467.88,207.133)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(467.88,185.711)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(467.88,164.289)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(467.88,142.867)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(467.88,121.444)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(467.88,100.022)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g><g class="toytree-TipLabel" transform="translate(467.88,78.5998)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r10</text></g><g class="toytree-TipLabel" transform="translate(467.88,57.1775)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r11</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


The highlighted edge is the branch subtending tips `r2` and `r3`. We will estimate how many sampled maps include a gain from `ancestral` to `derived` on this edge.


```python
# fit a model and simulate maps
fit = btree.pcm.fit_discrete_ctmc("rare_trait", nstates=2, model="ER")
smap = btree.pcm.simulate_stochastic_map("rare_trait", model_fit=fit, nreplicates=200, seed=12)

# extract stats for the specified edge and transition of interest
row = smap.edge_transition_stats.query(
    "edge_id==@target_node.idx "
    "and from_state=='ancestral' "
    "and to_state=='derived'"
).iloc[0]

# store result
er_result = {
    "model": fit.model, 
    "log_likelihood": fit.log_likelihood,
    "mean_gains_on_branch": row['mean'], 
    "prob_any_gain_on_branch": row['prob_nonzero'],
}
```

Next we do the same thing but fitting an "ARD" model:


```python
# fit a model and simulate maps
fit = btree.pcm.fit_discrete_ctmc("rare_trait", nstates=2, model="ARD")
smap = btree.pcm.simulate_stochastic_map("rare_trait", model_fit=fit, nreplicates=200, seed=12)

# extract stats for the specified edge and transition of interest
row = smap.edge_transition_stats.query(
    "edge_id==@target_node.idx "
    "and from_state=='ancestral' "
    "and to_state=='derived'"
).iloc[0]

# store result
ard_result = {
    "model": fit.model, 
    "log_likelihood": fit.log_likelihood,
    "mean_gains_on_branch": row['mean'], 
    "prob_any_gain_on_branch": row['prob_nonzero'],
}
```

### Result

The final column estimates the conditional frequency, under each fitted model, that at least one gain to the derived state occurred on the target branch. This quantity is computed from the replicate stochastic maps through `edge_transition_stats`. Changing the model can change this branch-specific conclusion because the fitted model changes the probabilities of gains, losses, and node states that condition the sampled histories.


```python
pd.DataFrame([er_result, ard_result]).round(3)
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
      <th>model</th>
      <th>log_likelihood</th>
      <th>mean_gains_on_branch</th>
      <th>prob_any_gain_on_branch</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>ER</td>
      <td>-7.881</td>
      <td>0.410</td>
      <td>0.410</td>
    </tr>
    <tr>
      <th>1</th>
      <td>ARD</td>
      <td>-7.246</td>
      <td>0.205</td>
      <td>0.205</td>
    </tr>
  </tbody>
</table>
</div>



Here we can see the probability of a transition to the derived state on branch ancestral to tips "r2" and "r3" is higher under the "ER" model than the "ARD" model. But in both it is only around 50% probability. This suggests that we can not state with high confidence that a single transition occurred in their ancestor. Instead, transitions could have occurred independently on the long branches leading to each tip, or in a different ancestor. We could compute and plot the probabilities of this transition on each of those branches if we cared to examine it more explicitly.

Stochastic maps must be conditioned on the original scalar observations. The implementation samples the root from its posterior, then samples descendants conditional on their sampled parent and descendant-subtree likelihood before simulating each branch from parent to child.

## Related APIs

- `tree.pcm.simulate_stochastic_map()` samples stochastic-map results with segment, event, dwell-time, transition-count, node-state, and branch-specific summary tables.
- `tree.annotate.add_edge_stochastic_map()` draws one replicate on an existing tree plot.
- `tree.pcm.fit_discrete_ctmc()` fits the Mk model used for mapping.
- `tree.pcm.infer_ancestral_states_discrete_ctmc()` estimates marginal node-state posteriors as a separate summary.
- `tree.pcm.simulate_discrete_trait()` creates example discrete traits for testing workflows.

## References

- Nielsen, R. 2002. Mapping mutations on phylogenies. *Systematic Biology* 51:729-739. https://doi.org/10.1080/10635150290102393
- Huelsenbeck, J. P., Nielsen, R., and Bollback, J. P. 2003. Stochastic mapping of morphological characters. *Systematic Biology* 52:131-158. https://doi.org/10.1080/10635150390192780
- Bollback, J. P. 2006. SIMMAP: stochastic character mapping of discrete traits on phylogenies. *BMC Bioinformatics* 7:88. https://doi.org/10.1186/1471-2105-7-88
- Minin, V. N., and Suchard, M. A. 2008. Counting labeled transitions in continuous-time Markov models of evolution. *Journal of Mathematical Biology* 56:391-412. https://doi.org/10.1007/s00285-007-0120-8

