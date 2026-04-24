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


<div class="toyplot" id="t885302ea69cc42e996d1c4e6db467705" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="500.0px" height="350.0px" viewBox="0 0 500.0 350.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tf0299d9dc38043bb86ee5e8ee6c6d2f7"><g class="toyplot-coordinates-Cartesian" id="tdc1248a2b13441b48f86cc3b8d992406"><clipPath id="t05432112a94e468a99d75397f9a53a70"><rect x="35.0" y="35.0" width="430.0" height="280.0"></rect></clipPath><g clip-path="url(#t05432112a94e468a99d75397f9a53a70)"><g class="toytree-mark-Toytree" id="t5d582519f05b4db895869203b12260cc"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 89.3 274.1 L 89.3 292.8 L 417.9 292.8" id="14,0" style=""></path><path d="M 155.0 255.3 L 155.0 271.4 L 417.9 271.4" id="13,1" style=""></path><path d="M 220.8 239.3 L 220.8 250.0 L 417.9 250.0" id="12,2" style=""></path><path d="M 220.8 239.3 L 220.8 228.6 L 417.9 228.6" id="12,3" style=""></path><path d="M 220.8 196.4 L 220.8 207.1 L 417.9 207.1" id="15,4" style=""></path><path d="M 220.8 196.4 L 220.8 185.7 L 417.9 185.7" id="15,5" style=""></path><path d="M 155.0 180.4 L 155.0 164.3 L 417.9 164.3" id="16,6" style=""></path><path d="M 155.0 122.8 L 155.0 142.9 L 417.9 142.9" id="20,7" style=""></path><path d="M 220.8 102.7 L 220.8 121.4 L 417.9 121.4" id="19,8" style=""></path><path d="M 286.5 84.0 L 286.5 100.0 L 417.9 100.0" id="18,9" style=""></path><path d="M 352.2 67.9 L 352.2 78.6 L 417.9 78.6" id="17,10" style=""></path><path d="M 352.2 67.9 L 352.2 57.2 L 417.9 57.2" id="17,11" style=""></path><path d="M 155.0 255.3 L 155.0 239.3 L 220.8 239.3" id="13,12" style=""></path><path d="M 89.3 274.1 L 89.3 255.3 L 155.0 255.3" id="14,13" style=""></path><path d="M 56.4 212.8 L 56.4 274.1 L 89.3 274.1" id="22,14" style=""></path><path d="M 155.0 180.4 L 155.0 196.4 L 220.8 196.4" id="16,15" style=""></path><path d="M 89.3 151.6 L 89.3 180.4 L 155.0 180.4" id="21,16" style=""></path><path d="M 286.5 84.0 L 286.5 67.9 L 352.2 67.9" id="18,17" style=""></path><path d="M 220.8 102.7 L 220.8 84.0 L 286.5 84.0" id="19,18" style=""></path><path d="M 155.0 122.8 L 155.0 102.7 L 220.8 102.7" id="20,19" style=""></path><path d="M 89.3 151.6 L 89.3 122.8 L 155.0 122.8" id="21,20" style=""></path><path d="M 56.4 212.8 L 56.4 151.6 L 89.3 151.6" id="22,21" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(55.3%,62.7%,79.6%)" transform="translate(417.936,292.823)"><circle r="5.0"></circle></g><g id="Node-1" style="fill:rgb(98.8%,55.3%,38.4%)" transform="translate(417.936,271.4)"><circle r="5.0"></circle></g><g id="Node-2" style="fill:rgb(98.8%,55.3%,38.4%)" transform="translate(417.936,249.978)"><circle r="5.0"></circle></g><g id="Node-3" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(417.936,228.556)"><circle r="5.0"></circle></g><g id="Node-4" style="fill:rgb(55.3%,62.7%,79.6%)" transform="translate(417.936,207.133)"><circle r="5.0"></circle></g><g id="Node-5" style="fill:rgb(55.3%,62.7%,79.6%)" transform="translate(417.936,185.711)"><circle r="5.0"></circle></g><g id="Node-6" style="fill:rgb(98.8%,55.3%,38.4%)" transform="translate(417.936,164.289)"><circle r="5.0"></circle></g><g id="Node-7" style="fill:rgb(98.8%,55.3%,38.4%)" transform="translate(417.936,142.867)"><circle r="5.0"></circle></g><g id="Node-8" style="fill:rgb(55.3%,62.7%,79.6%)" transform="translate(417.936,121.444)"><circle r="5.0"></circle></g><g id="Node-9" style="fill:rgb(55.3%,62.7%,79.6%)" transform="translate(417.936,100.022)"><circle r="5.0"></circle></g><g id="Node-10" style="fill:rgb(55.3%,62.7%,79.6%)" transform="translate(417.936,78.5998)"><circle r="5.0"></circle></g><g id="Node-11" style="fill:rgb(55.3%,62.7%,79.6%)" transform="translate(417.936,57.1775)"><circle r="5.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(417.936,292.823)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(417.936,271.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(417.936,249.978)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(417.936,228.556)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(417.936,207.133)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(417.936,185.711)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(417.936,164.289)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(417.936,142.867)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(417.936,121.444)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(417.936,100.022)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g><g class="toytree-TipLabel" transform="translate(417.936,78.5998)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r10</text></g><g class="toytree-TipLabel" transform="translate(417.936,57.1775)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r11</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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
      <td>C</td>
      <td>0.000000</td>
      <td>0.909091</td>
      <td>0.909091</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>1</td>
      <td>1</td>
      <td>13</td>
      <td>B</td>
      <td>0.000000</td>
      <td>0.727273</td>
      <td>0.727273</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0</td>
      <td>2</td>
      <td>2</td>
      <td>12</td>
      <td>B</td>
      <td>0.000000</td>
      <td>0.402457</td>
      <td>0.402457</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0</td>
      <td>2</td>
      <td>2</td>
      <td>12</td>
      <td>A</td>
      <td>0.402457</td>
      <td>0.545455</td>
      <td>0.142998</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0</td>
      <td>3</td>
      <td>3</td>
      <td>12</td>
      <td>A</td>
      <td>0.000000</td>
      <td>0.353753</td>
      <td>0.353753</td>
    </tr>
    <tr>
      <th>5</th>
      <td>0</td>
      <td>3</td>
      <td>3</td>
      <td>12</td>
      <td>B</td>
      <td>0.353753</td>
      <td>0.379754</td>
      <td>0.026001</td>
    </tr>
    <tr>
      <th>6</th>
      <td>0</td>
      <td>3</td>
      <td>3</td>
      <td>12</td>
      <td>A</td>
      <td>0.379754</td>
      <td>0.545455</td>
      <td>0.165700</td>
    </tr>
    <tr>
      <th>7</th>
      <td>0</td>
      <td>4</td>
      <td>4</td>
      <td>15</td>
      <td>C</td>
      <td>0.000000</td>
      <td>0.545455</td>
      <td>0.545455</td>
    </tr>
    <tr>
      <th>8</th>
      <td>0</td>
      <td>5</td>
      <td>5</td>
      <td>15</td>
      <td>C</td>
      <td>0.000000</td>
      <td>0.545455</td>
      <td>0.545455</td>
    </tr>
    <tr>
      <th>9</th>
      <td>0</td>
      <td>6</td>
      <td>6</td>
      <td>16</td>
      <td>B</td>
      <td>0.000000</td>
      <td>0.228353</td>
      <td>0.228353</td>
    </tr>
    <tr>
      <th>10</th>
      <td>0</td>
      <td>6</td>
      <td>6</td>
      <td>16</td>
      <td>A</td>
      <td>0.228353</td>
      <td>0.648517</td>
      <td>0.420164</td>
    </tr>
    <tr>
      <th>11</th>
      <td>0</td>
      <td>6</td>
      <td>6</td>
      <td>16</td>
      <td>B</td>
      <td>0.648517</td>
      <td>0.727273</td>
      <td>0.078756</td>
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


<div class="toyplot" id="t5ad12858b76547cb9b577b17caa00d7a" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="550.0px" height="350.0px" viewBox="0 0 550.0 350.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t0f24f6577347482b9f8a09d8b1c8514c"><g class="toyplot-coordinates-Cartesian" id="ta036adfdcfee4b8a99777dd68b200a0c"><clipPath id="t5e8d54f4d09f4e388dd7bef00644d104"><rect x="35.0" y="35.0" width="480.0" height="280.0"></rect></clipPath><g clip-path="url(#t5e8d54f4d09f4e388dd7bef00644d104)"><g class="toytree-mark-Toytree" id="tc53e883055df415d917e1dd4b0c45bee"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 88.9 274.1 L 88.9 292.8 L 467.8 292.8" id="14,0" style=""></path><path d="M 164.7 255.3 L 164.7 271.4 L 467.8 271.4" id="13,1" style=""></path><path d="M 240.5 239.3 L 240.5 250.0 L 467.8 250.0" id="12,2" style=""></path><path d="M 240.5 239.3 L 240.5 228.6 L 467.8 228.6" id="12,3" style=""></path><path d="M 240.5 196.4 L 240.5 207.1 L 467.8 207.1" id="15,4" style=""></path><path d="M 240.5 196.4 L 240.5 185.7 L 467.8 185.7" id="15,5" style=""></path><path d="M 164.7 180.4 L 164.7 164.3 L 467.8 164.3" id="16,6" style=""></path><path d="M 164.7 122.8 L 164.7 142.9 L 467.8 142.9" id="20,7" style=""></path><path d="M 240.5 102.7 L 240.5 121.4 L 467.8 121.4" id="19,8" style=""></path><path d="M 316.3 84.0 L 316.3 100.0 L 467.8 100.0" id="18,9" style=""></path><path d="M 392.0 67.9 L 392.0 78.6 L 467.8 78.6" id="17,10" style=""></path><path d="M 392.0 67.9 L 392.0 57.2 L 467.8 57.2" id="17,11" style=""></path><path d="M 164.7 255.3 L 164.7 239.3 L 240.5 239.3" id="13,12" style=""></path><path d="M 88.9 274.1 L 88.9 255.3 L 164.7 255.3" id="14,13" style=""></path><path d="M 51.0 212.8 L 51.0 274.1 L 88.9 274.1" id="22,14" style=""></path><path d="M 164.7 180.4 L 164.7 196.4 L 240.5 196.4" id="16,15" style=""></path><path d="M 88.9 151.6 L 88.9 180.4 L 164.7 180.4" id="21,16" style=""></path><path d="M 316.3 84.0 L 316.3 67.9 L 392.0 67.9" id="18,17" style=""></path><path d="M 240.5 102.7 L 240.5 84.0 L 316.3 84.0" id="19,18" style=""></path><path d="M 164.7 122.8 L 164.7 102.7 L 240.5 102.7" id="20,19" style=""></path><path d="M 88.9 151.6 L 88.9 122.8 L 164.7 122.8" id="21,20" style=""></path><path d="M 51.0 212.8 L 51.0 151.6 L 88.9 151.6" id="22,21" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(467.824,292.823)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(467.824,271.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(467.824,249.978)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(467.824,228.556)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(467.824,207.133)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(467.824,185.711)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(467.824,164.289)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(467.824,142.867)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(467.824,121.444)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(467.824,100.022)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g><g class="toytree-TipLabel" transform="translate(467.824,78.5998)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r10</text></g><g class="toytree-TipLabel" transform="translate(467.824,57.1775)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r11</text></g></g></g><g class="toytree-Annotation-Lines" id="t493b5e1ced1f4703902c5af5cb6ecfb5" style="stroke-linecap:butt"><path id="Line-0" d="M 467.82443 292.82252 L 88.888508 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-1" d="M 88.888508 292.82252 L 88.888508 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-2" d="M 467.82443 271.40024 L 164.67569 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-3" d="M 164.67569 271.40024 L 164.67569 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-4" d="M 467.82443 249.97796 L 300.06849 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-5" d="M 300.06849 249.97796 L 240.46288 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-6" d="M 240.46288 249.97796 L 240.46288 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-7" d="M 467.82443 228.55569 L 320.36973 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-8" d="M 320.36973 228.55569 L 309.53168 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-9" d="M 309.53168 228.55569 L 240.46288 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-10" d="M 240.46288 228.55569 L 240.46288 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-11" d="M 467.82443 207.13341 L 240.46288 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-12" d="M 240.46288 207.13341 L 240.46288 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-13" d="M 467.82443 185.71114 L 240.46288 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-14" d="M 240.46288 185.71114 L 240.46288 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-15" d="M 467.82443 164.28886 L 372.63997 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-16" d="M 372.63997 164.28886 L 197.50335 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-17" d="M 197.50335 164.28886 L 164.67569 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-18" d="M 164.67569 164.28886 L 164.67569 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-19" d="M 467.82443 142.86659 L 324.9475 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-20" d="M 324.9475 142.86659 L 164.67569 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-21" d="M 164.67569 142.86659 L 164.67569 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-22" d="M 467.82443 121.44431 L 240.46288 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-23" d="M 240.46288 121.44431 L 240.46288 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-24" d="M 467.82443 100.02204 L 316.25006 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-25" d="M 316.25006 100.02204 L 316.25006 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-26" d="M 467.82443 78.599759 L 392.03725 78.599759" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-27" d="M 392.03725 78.599759 L 392.03725 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-28" d="M 467.82443 57.177484 L 392.03725 57.177484" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-29" d="M 392.03725 57.177484 L 392.03725 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-30" d="M 240.46288 239.26683 L 190.40544 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-31" d="M 190.40544 239.26683 L 164.67569 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-32" d="M 164.67569 239.26683 L 164.67569 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-33" d="M 164.67569 255.33353 L 148.97326 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-34" d="M 148.97326 255.33353 L 88.888508 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-35" d="M 88.888508 255.33353 L 88.888508 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-36" d="M 88.888508 274.07803 L 50.994915 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-37" d="M 50.994915 274.07803 L 50.994915 212.82371" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-38" d="M 240.46288 196.42228 L 184.24723 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-39" d="M 184.24723 196.42228 L 164.67569 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-40" d="M 164.67569 196.42228 L 164.67569 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-41" d="M 164.67569 180.35557 L 88.888508 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-42" d="M 88.888508 180.35557 L 88.888508 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-43" d="M 392.03725 67.888622 L 316.25006 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-44" d="M 316.25006 67.888622 L 316.25006 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-45" d="M 316.25006 83.955328 L 240.46288 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-46" d="M 240.46288 83.955328 L 240.46288 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-47" d="M 240.46288 102.69982 L 164.67569 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-48" d="M 164.67569 102.69982 L 164.67569 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-49" d="M 164.67569 122.7832 L 102.52446 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-50" d="M 102.52446 122.7832 L 88.888508 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-51" d="M 88.888508 122.7832 L 88.888508 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-52" d="M 88.888508 151.56939 L 60.138432 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-53" d="M 60.138432 151.56939 L 50.994915 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-54" d="M 50.994915 151.56939 L 50.994915 212.82371" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path></g><g class="toytree-Annotation-Markers" id="t53f9fece4d4e4711987602f0dfe6ddd6" style="stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Mark-0" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,292.823)"><circle r="5.0"></circle></g><g id="Mark-1" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0" transform="translate(467.824,271.4)"><circle r="5.0"></circle></g><g id="Mark-2" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0" transform="translate(467.824,249.978)"><circle r="5.0"></circle></g><g id="Mark-3" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0" transform="translate(467.824,228.556)"><circle r="5.0"></circle></g><g id="Mark-4" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,207.133)"><circle r="5.0"></circle></g><g id="Mark-5" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,185.711)"><circle r="5.0"></circle></g><g id="Mark-6" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0" transform="translate(467.824,164.289)"><circle r="5.0"></circle></g><g id="Mark-7" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0" transform="translate(467.824,142.867)"><circle r="5.0"></circle></g><g id="Mark-8" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,121.444)"><circle r="5.0"></circle></g><g id="Mark-9" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,100.022)"><circle r="5.0"></circle></g><g id="Mark-10" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,78.5998)"><circle r="5.0"></circle></g><g id="Mark-11" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,57.1775)"><circle r="5.0"></circle></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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
      <td>1.202706</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>1</td>
      <td>B</td>
      <td>2.235467</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0</td>
      <td>2</td>
      <td>C</td>
      <td>4.743645</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1</td>
      <td>0</td>
      <td>A</td>
      <td>0.973180</td>
    </tr>
    <tr>
      <th>4</th>
      <td>1</td>
      <td>1</td>
      <td>B</td>
      <td>2.094468</td>
    </tr>
    <tr>
      <th>5</th>
      <td>1</td>
      <td>2</td>
      <td>C</td>
      <td>5.114169</td>
    </tr>
    <tr>
      <th>6</th>
      <td>2</td>
      <td>0</td>
      <td>A</td>
      <td>0.288469</td>
    </tr>
    <tr>
      <th>7</th>
      <td>2</td>
      <td>1</td>
      <td>B</td>
      <td>2.581000</td>
    </tr>
    <tr>
      <th>8</th>
      <td>2</td>
      <td>2</td>
      <td>C</td>
      <td>5.312350</td>
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
      <td>0.711</td>
      <td>0.463</td>
      <td>0.078</td>
      <td>0.850</td>
      <td>1.288</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>B</td>
      <td>2.354</td>
      <td>0.581</td>
      <td>1.295</td>
      <td>2.408</td>
      <td>3.010</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>C</td>
      <td>5.117</td>
      <td>0.414</td>
      <td>4.443</td>
      <td>5.130</td>
      <td>5.821</td>
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
      <td>1.4</td>
      <td>1.075</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>3.000</td>
      <td>0.8</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>2</td>
      <td>A</td>
      <td>C</td>
      <td>0.6</td>
      <td>0.843</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>2.000</td>
      <td>0.4</td>
    </tr>
    <tr>
      <th>2</th>
      <td>1</td>
      <td>0</td>
      <td>B</td>
      <td>A</td>
      <td>1.1</td>
      <td>0.876</td>
      <td>0.0</td>
      <td>1.0</td>
      <td>2.775</td>
      <td>0.8</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1</td>
      <td>2</td>
      <td>B</td>
      <td>C</td>
      <td>1.7</td>
      <td>1.252</td>
      <td>0.0</td>
      <td>2.0</td>
      <td>3.775</td>
      <td>0.8</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2</td>
      <td>0</td>
      <td>C</td>
      <td>A</td>
      <td>1.3</td>
      <td>0.949</td>
      <td>0.0</td>
      <td>2.0</td>
      <td>2.000</td>
      <td>0.7</td>
    </tr>
    <tr>
      <th>5</th>
      <td>2</td>
      <td>1</td>
      <td>C</td>
      <td>B</td>
      <td>3.3</td>
      <td>0.483</td>
      <td>3.0</td>
      <td>3.0</td>
      <td>4.000</td>
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
      <td>0.1</td>
      <td>0.316228</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.775</td>
      <td>0.1</td>
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
      <td>0.1</td>
      <td>0.316228</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.775</td>
      <td>0.1</td>
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
      <td>0.0</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.000</td>
      <td>0.0</td>
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
      <td>0.3</td>
      <td>0.483046</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.000</td>
      <td>0.3</td>
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
      <td>0.0</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.000</td>
      <td>0.0</td>
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
      <td>0.0</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.000</td>
      <td>0.0</td>
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
      <td>0.3</td>
      <td>0.483046</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>1.000</td>
      <td>0.3</td>
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
      <td>0.1</td>
      <td>0.316228</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.775</td>
      <td>0.1</td>
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
      <td>0.0</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.000</td>
      <td>0.0</td>
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
      <td>0.0</td>
      <td>0.000000</td>
      <td>0.0</td>
      <td>0.0</td>
      <td>0.000</td>
      <td>0.0</td>
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
      <td>1.203</td>
      <td>2.235</td>
      <td>4.744</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.973</td>
      <td>2.094</td>
      <td>5.114</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0.288</td>
      <td>2.581</td>
      <td>5.312</td>
    </tr>
    <tr>
      <th>3</th>
      <td>1.313</td>
      <td>1.908</td>
      <td>4.961</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0.893</td>
      <td>2.144</td>
      <td>5.145</td>
    </tr>
    <tr>
      <th>5</th>
      <td>0.226</td>
      <td>2.663</td>
      <td>5.293</td>
    </tr>
    <tr>
      <th>6</th>
      <td>0.271</td>
      <td>2.802</td>
      <td>5.108</td>
    </tr>
    <tr>
      <th>7</th>
      <td>1.097</td>
      <td>1.117</td>
      <td>5.968</td>
    </tr>
    <tr>
      <th>8</th>
      <td>0.807</td>
      <td>3.019</td>
      <td>4.356</td>
    </tr>
    <tr>
      <th>9</th>
      <td>0.035</td>
      <td>2.980</td>
      <td>5.166</td>
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


<div class="toyplot" id="t02a80732280e460a983d3799e2a48f1b" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="550.0px" height="350.0px" viewBox="0 0 550.0 350.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t3d5d2399bab54adf94b27d82058b3c72"><g class="toyplot-coordinates-Cartesian" id="tabae4e1aaebb4cb4b78853b21d747f59"><clipPath id="te58572672d2e4c61a245bf89f465751d"><rect x="35.0" y="35.0" width="480.0" height="280.0"></rect></clipPath><g clip-path="url(#te58572672d2e4c61a245bf89f465751d)"><g class="toytree-mark-Toytree" id="t9622f11a6d9f4e22bf573497401ba688"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 88.9 274.1 L 88.9 292.8 L 467.8 292.8" id="14,0" style=""></path><path d="M 164.7 255.3 L 164.7 271.4 L 467.8 271.4" id="13,1" style=""></path><path d="M 240.5 239.3 L 240.5 250.0 L 467.8 250.0" id="12,2" style=""></path><path d="M 240.5 239.3 L 240.5 228.6 L 467.8 228.6" id="12,3" style=""></path><path d="M 240.5 196.4 L 240.5 207.1 L 467.8 207.1" id="15,4" style=""></path><path d="M 240.5 196.4 L 240.5 185.7 L 467.8 185.7" id="15,5" style=""></path><path d="M 164.7 180.4 L 164.7 164.3 L 467.8 164.3" id="16,6" style=""></path><path d="M 164.7 122.8 L 164.7 142.9 L 467.8 142.9" id="20,7" style=""></path><path d="M 240.5 102.7 L 240.5 121.4 L 467.8 121.4" id="19,8" style=""></path><path d="M 316.3 84.0 L 316.3 100.0 L 467.8 100.0" id="18,9" style=""></path><path d="M 392.0 67.9 L 392.0 78.6 L 467.8 78.6" id="17,10" style=""></path><path d="M 392.0 67.9 L 392.0 57.2 L 467.8 57.2" id="17,11" style=""></path><path d="M 164.7 255.3 L 164.7 239.3 L 240.5 239.3" id="13,12" style=""></path><path d="M 88.9 274.1 L 88.9 255.3 L 164.7 255.3" id="14,13" style=""></path><path d="M 51.0 212.8 L 51.0 274.1 L 88.9 274.1" id="22,14" style=""></path><path d="M 164.7 180.4 L 164.7 196.4 L 240.5 196.4" id="16,15" style=""></path><path d="M 88.9 151.6 L 88.9 180.4 L 164.7 180.4" id="21,16" style=""></path><path d="M 316.3 84.0 L 316.3 67.9 L 392.0 67.9" id="18,17" style=""></path><path d="M 240.5 102.7 L 240.5 84.0 L 316.3 84.0" id="19,18" style=""></path><path d="M 164.7 122.8 L 164.7 102.7 L 240.5 102.7" id="20,19" style=""></path><path d="M 88.9 151.6 L 88.9 122.8 L 164.7 122.8" id="21,20" style=""></path><path d="M 51.0 212.8 L 51.0 151.6 L 88.9 151.6" id="22,21" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(467.824,292.823)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(467.824,271.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(467.824,249.978)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(467.824,228.556)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(467.824,207.133)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(467.824,185.711)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(467.824,164.289)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(467.824,142.867)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(467.824,121.444)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(467.824,100.022)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g><g class="toytree-TipLabel" transform="translate(467.824,78.5998)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r10</text></g><g class="toytree-TipLabel" transform="translate(467.824,57.1775)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r11</text></g></g></g><g class="toytree-Annotation-Lines" id="tbffa4751f7d145caa3860cf3675bae2a" style="stroke-linecap:butt"><path id="Line-0" d="M 467.82443 292.82252 L 88.888508 292.82252" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-1" d="M 88.888508 292.82252 L 88.888508 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-2" d="M 467.82443 271.40024 L 408.2135 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-3" d="M 408.2135 271.40024 L 164.67569 271.40024" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-4" d="M 164.67569 271.40024 L 164.67569 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-5" d="M 467.82443 249.97796 L 298.0171 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-6" d="M 298.0171 249.97796 L 240.46288 249.97796" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-7" d="M 240.46288 249.97796 L 240.46288 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-8" d="M 467.82443 228.55569 L 338.91546 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-9" d="M 338.91546 228.55569 L 240.46288 228.55569" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-10" d="M 240.46288 228.55569 L 240.46288 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-11" d="M 467.82443 207.13341 L 240.46288 207.13341" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-12" d="M 240.46288 207.13341 L 240.46288 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-13" d="M 467.82443 185.71114 L 240.46288 185.71114" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-14" d="M 240.46288 185.71114 L 240.46288 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-15" d="M 467.82443 164.28886 L 175.48061 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-16" d="M 175.48061 164.28886 L 164.67569 164.28886" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-17" d="M 164.67569 164.28886 L 164.67569 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-18" d="M 467.82443 142.86659 L 283.84838 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-19" d="M 283.84838 142.86659 L 164.67569 142.86659" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-20" d="M 164.67569 142.86659 L 164.67569 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-21" d="M 467.82443 121.44431 L 455.52559 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-22" d="M 455.52559 121.44431 L 288.22757 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-23" d="M 288.22757 121.44431 L 240.46288 121.44431" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-24" d="M 240.46288 121.44431 L 240.46288 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-25" d="M 467.82443 100.02204 L 316.25006 100.02204" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-26" d="M 316.25006 100.02204 L 316.25006 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-27" d="M 467.82443 78.599759 L 392.03725 78.599759" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-28" d="M 392.03725 78.599759 L 392.03725 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-29" d="M 467.82443 57.177484 L 392.03725 57.177484" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-30" d="M 392.03725 57.177484 L 392.03725 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-31" d="M 240.46288 239.26683 L 175.38882 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-32" d="M 175.38882 239.26683 L 164.67569 239.26683" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-33" d="M 164.67569 239.26683 L 164.67569 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-34" d="M 164.67569 255.33353 L 142.18526 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-35" d="M 142.18526 255.33353 L 88.888508 255.33353" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-36" d="M 88.888508 255.33353 L 88.888508 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-37" d="M 88.888508 274.07803 L 50.994915 274.07803" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-38" d="M 50.994915 274.07803 L 50.994915 212.82371" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-39" d="M 240.46288 196.42228 L 164.67569 196.42228" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-40" d="M 164.67569 196.42228 L 164.67569 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-41" d="M 164.67569 180.35557 L 88.888508 180.35557" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-42" d="M 88.888508 180.35557 L 88.888508 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-43" d="M 392.03725 67.888622 L 316.25006 67.888622" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-44" d="M 316.25006 67.888622 L 316.25006 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-45" d="M 316.25006 83.955328 L 240.46288 83.955328" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-46" d="M 240.46288 83.955328 L 240.46288 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-47" d="M 240.46288 102.69982 L 164.67569 102.69982" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-48" d="M 164.67569 102.69982 L 164.67569 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-49" d="M 164.67569 122.7832 L 88.888508 122.7832" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-50" d="M 88.888508 122.7832 L 88.888508 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-51" d="M 88.888508 151.56939 L 50.994915 151.56939" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path><path id="Line-52" d="M 50.994915 151.56939 L 50.994915 212.82371" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(55.3%,62.7%,79.6%);stroke-opacity:1.0;stroke-linecap:butt;stroke-width:4.0"></path></g><g class="toytree-Annotation-Markers" id="tc1fb51e57b704182980a30e1ab50b574" style="stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Mark-0" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,292.823)"><circle r="5.0"></circle></g><g id="Mark-1" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0" transform="translate(467.824,271.4)"><circle r="5.0"></circle></g><g id="Mark-2" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0" transform="translate(467.824,249.978)"><circle r="5.0"></circle></g><g id="Mark-3" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0" transform="translate(467.824,228.556)"><circle r="5.0"></circle></g><g id="Mark-4" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,207.133)"><circle r="5.0"></circle></g><g id="Mark-5" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,185.711)"><circle r="5.0"></circle></g><g id="Mark-6" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0" transform="translate(467.824,164.289)"><circle r="5.0"></circle></g><g id="Mark-7" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0" transform="translate(467.824,142.867)"><circle r="5.0"></circle></g><g id="Mark-8" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,121.444)"><circle r="5.0"></circle></g><g id="Mark-9" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,100.022)"><circle r="5.0"></circle></g><g id="Mark-10" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,78.5998)"><circle r="5.0"></circle></g><g id="Mark-11" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0" transform="translate(467.824,57.1775)"><circle r="5.0"></circle></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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


<div class="toyplot" id="t97d35878e17f4b55808efaf77d3d2b53" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="550.0px" height="350.0px" viewBox="0 0 550.0 350.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t040f228032d24d26af2f423a54dad405"><g class="toyplot-coordinates-Cartesian" id="t9fad2b8a94d64644915aca89466aaa85"><clipPath id="t37cdfac7ca4d4b2a8b8ee4e3b0a7cb51"><rect x="35.0" y="35.0" width="480.0" height="280.0"></rect></clipPath><g clip-path="url(#t37cdfac7ca4d4b2a8b8ee4e3b0a7cb51)"><g class="toytree-mark-Toytree" id="t6eb62afde487497bab4504c4dce0e87a"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 93.9 274.1 L 93.9 292.8 L 467.9 292.8" id="14,0" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 168.7 255.3 L 168.7 271.4 L 467.9 271.4" id="13,1" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 243.5 239.3 L 243.5 250.0 L 467.9 250.0" id="12,2" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 243.5 239.3 L 243.5 228.6 L 467.9 228.6" id="12,3" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 243.5 196.4 L 243.5 207.1 L 467.9 207.1" id="15,4" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 243.5 196.4 L 243.5 185.7 L 467.9 185.7" id="15,5" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 168.7 180.4 L 168.7 164.3 L 467.9 164.3" id="16,6" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 168.7 122.8 L 168.7 142.9 L 467.9 142.9" id="20,7" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 243.5 102.7 L 243.5 121.4 L 467.9 121.4" id="19,8" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 318.3 84.0 L 318.3 100.0 L 467.9 100.0" id="18,9" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 393.1 67.9 L 393.1 78.6 L 467.9 78.6" id="17,10" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 393.1 67.9 L 393.1 57.2 L 467.9 57.2" id="17,11" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 168.7 255.3 L 168.7 239.3 L 243.5 239.3" id="13,12" style="stroke:rgb(100.0%,54.9%,0.0%);stroke-opacity:1.0;stroke-width:5"></path><path d="M 93.9 274.1 L 93.9 255.3 L 168.7 255.3" id="14,13" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 56.5 212.8 L 56.5 274.1 L 93.9 274.1" id="22,14" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 168.7 180.4 L 168.7 196.4 L 243.5 196.4" id="16,15" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 93.9 151.6 L 93.9 180.4 L 168.7 180.4" id="21,16" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 318.3 84.0 L 318.3 67.9 L 393.1 67.9" id="18,17" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 243.5 102.7 L 243.5 84.0 L 318.3 84.0" id="19,18" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 168.7 122.8 L 168.7 102.7 L 243.5 102.7" id="20,19" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 93.9 151.6 L 93.9 122.8 L 168.7 122.8" id="21,20" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path><path d="M 56.5 212.8 L 56.5 151.6 L 93.9 151.6" id="22,21" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-width:2"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(467.88,292.823)"><circle r="5.0"></circle></g><g id="Node-1" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(467.88,271.4)"><circle r="5.0"></circle></g><g id="Node-2" style="fill:rgb(98.8%,55.3%,38.4%)" transform="translate(467.88,249.978)"><circle r="5.0"></circle></g><g id="Node-3" style="fill:rgb(98.8%,55.3%,38.4%)" transform="translate(467.88,228.556)"><circle r="5.0"></circle></g><g id="Node-4" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(467.88,207.133)"><circle r="5.0"></circle></g><g id="Node-5" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(467.88,185.711)"><circle r="5.0"></circle></g><g id="Node-6" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(467.88,164.289)"><circle r="5.0"></circle></g><g id="Node-7" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(467.88,142.867)"><circle r="5.0"></circle></g><g id="Node-8" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(467.88,121.444)"><circle r="5.0"></circle></g><g id="Node-9" style="fill:rgb(40.0%,76.1%,64.7%)" transform="translate(467.88,100.022)"><circle r="5.0"></circle></g><g id="Node-10" style="fill:rgb(98.8%,55.3%,38.4%)" transform="translate(467.88,78.5998)"><circle r="5.0"></circle></g><g id="Node-11" style="fill:rgb(98.8%,55.3%,38.4%)" transform="translate(467.88,57.1775)"><circle r="5.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(467.88,292.823)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(467.88,271.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(467.88,249.978)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(467.88,228.556)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(467.88,207.133)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(467.88,185.711)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(467.88,164.289)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(467.88,142.867)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(467.88,121.444)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(467.88,100.022)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g><g class="toytree-TipLabel" transform="translate(467.88,78.5998)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r10</text></g><g class="toytree-TipLabel" transform="translate(467.88,57.1775)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r11</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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
      <td>0.515</td>
      <td>0.515</td>
    </tr>
    <tr>
      <th>1</th>
      <td>ARD</td>
      <td>-7.190</td>
      <td>0.445</td>
      <td>0.440</td>
    </tr>
  </tbody>
</table>
</div>



Here we can see the probability of a transition to the derived state on branch ancestral to tips "r2" and "r3" is higher under the "ER" model than the "ARD" model. But in both it is only around 50% probability. This suggests that we can not state with high confidence that a single transition occurred in their ancestor. Instead, transitions could have occurred independently on the long branches leading to each tip, or in a different ancestor. We could compute and plot the probabilities of this transition on each of those branches if we cared to examine it more explicitly.

## Posterior Constraints

In addition to providing a fixed state for each tip in the tree, you can also fix the states of one or more internal nodes of the tree, or set them to non-fixed states, as posterior probability vectors, such as those returned by ancestral-state reconstruction. 

In this mode, non-missing entries must all be vectors of length `nstates` that sum to 1. One-hot vectors behave as fixed state constraints, while non-one-hot vectors are sampled from their probabilities.

Posterior vectors are ordered by the fitted model states. When maps are sampled from vectors only, the `state` column reports state indices rather than the original tip-state labels.


```python
# fit a CTMC model and infer ancestral state posterior probabilities
asr = tree.pcm.infer_ancestral_states_discrete_ctmc(
    data="X",
    nstates=3,
    model="ER",
)
posteriors = asr["data"]["X_anc_posterior"]
posteriors
```




    0                                       (0.0, 0.0, 1.0)
    1                                       (0.0, 1.0, 0.0)
    2                                       (0.0, 1.0, 0.0)
    3                                       (1.0, 0.0, 0.0)
    4                                       (0.0, 0.0, 1.0)
    5                                       (0.0, 0.0, 1.0)
    6                                       (0.0, 1.0, 0.0)
    7                                       (0.0, 1.0, 0.0)
    8                                       (0.0, 0.0, 1.0)
    9                                       (0.0, 0.0, 1.0)
    10                                      (0.0, 0.0, 1.0)
    11                                      (0.0, 0.0, 1.0)
    12    (0.22975007401102754, 0.5507508602960469, 0.21...
    13    (0.1375626617872403, 0.5240922810395716, 0.338...
    14    (0.07247423302851404, 0.3176720647501351, 0.60...
    15    (0.026724406205176465, 0.10342172261557021, 0....
    16    (0.033496920790761914, 0.22666041288207353, 0....
    17    (0.000902272121284814, 0.0012796479185912019, ...
    18    (0.0037347461949648704, 0.009146743345504195, ...
    19    (0.012309527248855033, 0.05054669216112823, 0....
    20    (0.028691787095824706, 0.2078099635623917, 0.7...
    21    (0.03362646044402534, 0.23942281407941515, 0.7...
    22    (0.05579211415709752, 0.27853715854991745, 0.6...
    Name: X_anc_posterior, dtype: object




```python
# draw the tree node state posteriors
canvas, axes, mark = btree.draw(width=550, height=350)
btree.annotate.add_node_pie_markers(
    axes, data=posteriors, 
    colors="Set2", size=15, 
    istroke="black", istroke_width=1,
);
```


<div class="toyplot" id="t77857e822ebb4d16919f80d469ef4435" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="550.0px" height="350.0px" viewBox="0 0 550.0 350.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tc17a298375cf419fa24d20ffdb03fa3a"><g class="toyplot-coordinates-Cartesian" id="t67f015ecce9546daac9d9c07184a41dc"><clipPath id="t5017dc35e7f1480fb48d165414e3bedc"><rect x="35.0" y="35.0" width="480.0" height="280.0"></rect></clipPath><g clip-path="url(#t5017dc35e7f1480fb48d165414e3bedc)"><g class="toytree-mark-Toytree" id="ta177cc759ad943ee9213f4d2cace7de4"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 91.4 274.1 L 91.4 292.8 L 467.9 292.8" id="14,0" style=""></path><path d="M 166.7 255.3 L 166.7 271.4 L 467.9 271.4" id="13,1" style=""></path><path d="M 242.0 239.3 L 242.0 250.0 L 467.9 250.0" id="12,2" style=""></path><path d="M 242.0 239.3 L 242.0 228.6 L 467.9 228.6" id="12,3" style=""></path><path d="M 242.0 196.4 L 242.0 207.1 L 467.9 207.1" id="15,4" style=""></path><path d="M 242.0 196.4 L 242.0 185.7 L 467.9 185.7" id="15,5" style=""></path><path d="M 166.7 180.4 L 166.7 164.3 L 467.9 164.3" id="16,6" style=""></path><path d="M 166.7 122.8 L 166.7 142.9 L 467.9 142.9" id="20,7" style=""></path><path d="M 242.0 102.7 L 242.0 121.4 L 467.9 121.4" id="19,8" style=""></path><path d="M 317.3 84.0 L 317.3 100.0 L 467.9 100.0" id="18,9" style=""></path><path d="M 392.6 67.9 L 392.6 78.6 L 467.9 78.6" id="17,10" style=""></path><path d="M 392.6 67.9 L 392.6 57.2 L 467.9 57.2" id="17,11" style=""></path><path d="M 166.7 255.3 L 166.7 239.3 L 242.0 239.3" id="13,12" style=""></path><path d="M 91.4 274.1 L 91.4 255.3 L 166.7 255.3" id="14,13" style=""></path><path d="M 53.7 212.8 L 53.7 274.1 L 91.4 274.1" id="22,14" style=""></path><path d="M 166.7 180.4 L 166.7 196.4 L 242.0 196.4" id="16,15" style=""></path><path d="M 91.4 151.6 L 91.4 180.4 L 166.7 180.4" id="21,16" style=""></path><path d="M 317.3 84.0 L 317.3 67.9 L 392.6 67.9" id="18,17" style=""></path><path d="M 242.0 102.7 L 242.0 84.0 L 317.3 84.0" id="19,18" style=""></path><path d="M 166.7 122.8 L 166.7 102.7 L 242.0 102.7" id="20,19" style=""></path><path d="M 91.4 151.6 L 91.4 122.8 L 166.7 122.8" id="21,20" style=""></path><path d="M 53.7 212.8 L 53.7 151.6 L 91.4 151.6" id="22,21" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(467.851,292.823)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(467.851,271.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(467.851,249.978)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(467.851,228.556)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(467.851,207.133)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(467.851,185.711)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(467.851,164.289)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(467.851,142.867)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(467.851,121.444)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(467.851,100.022)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g><g class="toytree-TipLabel" transform="translate(467.851,78.5998)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r10</text></g><g class="toytree-TipLabel" transform="translate(467.851,57.1775)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r11</text></g></g></g><g class="toytree-mark-PieCharts" id="t34ac1f08afad43bfb1a605522436d81f"><g id="pie-0" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(467.8514,292.8225) rotate(-45)"><title>0, 0, 1</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></circle><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-1" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(467.8514,271.4002) rotate(-45)"><title>0, 1, 0</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></circle><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-2" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(467.8514,249.9780) rotate(-45)"><title>0, 1, 0</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></circle><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-3" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(467.8514,228.5557) rotate(-45)"><title>1, 0, 0</title><circle r="7.5" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></circle><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-4" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(467.8514,207.1334) rotate(-45)"><title>0, 0, 1</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></circle><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-5" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(467.8514,185.7111) rotate(-45)"><title>0, 0, 1</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></circle><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-6" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(467.8514,164.2889) rotate(-45)"><title>0, 1, 0</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></circle><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-7" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(467.8514,142.8666) rotate(-45)"><title>0, 1, 0</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></circle><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-8" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(467.8514,121.4443) rotate(-45)"><title>0, 0, 1</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></circle><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-9" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(467.8514,100.0220) rotate(-45)"><title>0, 0, 1</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></circle><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-10" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(467.8514,78.5998) rotate(-45)"><title>0, 0, 1</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></circle><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-11" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(467.8514,57.1775) rotate(-45)"><title>0, 0, 1</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></circle><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-12" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(241.9658,239.2668) rotate(-45)"><title>0.22975, 0.550751, 0.219499</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 0.9516825 7.439375249999999 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 0.9516825 7.439375249999999 A 7.5 7.5 0 1 1 1.42854075 -7.3626945 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><path d="M 0 0 L 1.42854075 -7.3626945 A 7.5 7.5 0 0 1 7.5 0.0 L 0 0" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-13" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(166.6706,255.3335) rotate(-45)"><title>0.137563, 0.524092, 0.338345</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 4.8686145 5.704962 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 4.8686145 5.704962 A 7.5 7.5 0 1 1 -3.952638 -6.373904250000001 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><path d="M 0 0 L -3.952638 -6.373904250000001 A 7.5 7.5 0 0 1 7.5 -0.0 L 0 0" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-14" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(91.3754,274.0780) rotate(-45)"><title>0.0724742, 0.317672, 0.609854</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 6.735741 3.2984535 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 6.735741 3.2984535 A 7.5 7.5 0 0 1 -5.783240999999999 4.77536625 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><path d="M 0 0 L -5.783240999999999 4.77536625 A 7.5 7.5 0 1 1 7.5 -0.0 L 0 0" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-15" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(241.9658,196.4223) rotate(-45)"><title>0.0267244, 0.103422, 0.869854</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.39451625 1.2534480000000001 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 7.39451625 1.2534480000000001 A 7.5 7.5 0 0 1 5.1290812500000005 5.471976000000001 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><path d="M 0 0 L 5.1290812500000005 5.471976000000001 A 7.5 7.5 0 1 1 7.5 -0.0 L 0 0" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-16" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(166.6706,180.3556) rotate(-45)"><title>0.0334969, 0.22666, 0.739843</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.3345005 1.5668775 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 7.3345005 1.5668775 A 7.5 7.5 0 0 1 -0.47832825 7.4847315 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><path d="M 0 0 L -0.47832825 7.4847315 A 7.5 7.5 0 1 1 7.5 -0.0 L 0 0" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-17" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(392.5562,67.8886) rotate(-45)"><title>0.000902272, 0.00127965, 0.997818</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.49987925 0.04251825 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 7.49987925 0.04251825 A 7.5 7.5 0 0 1 7.499295 0.1028175 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><path d="M 0 0 L 7.499295 0.1028175 A 7.5 7.5 0 1 1 7.5 -0.0 L 0 0" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-18" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(317.2610,83.9553) rotate(-45)"><title>0.00373475, 0.00914674, 0.987119</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.49793525 0.17597925 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 7.49793525 0.17597925 A 7.5 7.5 0 0 1 7.475448 0.606363 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><path d="M 0 0 L 7.475448 0.606363 A 7.5 7.5 0 1 1 7.5 -0.0 L 0 0" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-19" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(241.9658,102.6998) rotate(-45)"><title>0.0123095, 0.0505467, 0.937144</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.47757875 0.579495 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 7.47757875 0.579495 A 7.5 7.5 0 0 1 6.92265525 2.8856272499999998 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><path d="M 0 0 L 6.92265525 2.8856272499999998 A 7.5 7.5 0 1 1 7.5 -0.0 L 0 0" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-20" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(166.6706,122.7832) rotate(-45)"><title>0.0286918, 0.20781, 0.763498</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.37845725 1.3447567500000002 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 7.37845725 1.3447567500000002 A 7.5 7.5 0 0 1 0.635328 7.473042 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><path d="M 0 0 L 0.635328 7.473042 A 7.5 7.5 0 1 1 7.5 -0.0 L 0 0" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-21" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(91.3754,151.5694) rotate(-45)"><title>0.0336265, 0.239423, 0.726951</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.333222500000001 1.57284675 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 7.333222500000001 1.57284675 A 7.5 7.5 0 0 1 -1.08237825 7.42148625 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><path d="M 0 0 L -1.08237825 7.42148625 A 7.5 7.5 0 1 1 7.5 -0.0 L 0 0" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g><g id="pie-22" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:1" transform="translate(53.7278,212.8237) rotate(-45)"><title>0.0557921, 0.278537, 0.665671</title><path d="M 0 0 L 7.5 0.0 A 7.5 7.5 0 0 1 7.043874 2.57562375 L 0 0" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0"></path><path d="M 0 0 L 7.043874 2.57562375 A 7.5 7.5 0 0 1 -3.7905712499999997 6.471597 L 0 0" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0"></path><path d="M 0 0 L -3.7905712499999997 6.471597 A 7.5 7.5 0 1 1 7.5 -0.0 L 0 0" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0"></path><circle r="7.5" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></circle></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
posterior_result = tree.pcm.simulate_stochastic_map(
    data=posteriors,
    model_fit=asr["model_fit"],
    nreplicates=2,
    seed=4,
)

posterior_result.segments[columns].head(10)
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
      <td>2</td>
      <td>0.000000</td>
      <td>0.909091</td>
      <td>0.909091</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0</td>
      <td>1</td>
      <td>1</td>
      <td>13</td>
      <td>1</td>
      <td>0.000000</td>
      <td>0.727273</td>
      <td>0.727273</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0</td>
      <td>2</td>
      <td>2</td>
      <td>12</td>
      <td>1</td>
      <td>0.000000</td>
      <td>0.536811</td>
      <td>0.536811</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0</td>
      <td>2</td>
      <td>2</td>
      <td>12</td>
      <td>2</td>
      <td>0.536811</td>
      <td>0.545455</td>
      <td>0.008644</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0</td>
      <td>3</td>
      <td>3</td>
      <td>12</td>
      <td>0</td>
      <td>0.000000</td>
      <td>0.528509</td>
      <td>0.528509</td>
    </tr>
    <tr>
      <th>5</th>
      <td>0</td>
      <td>3</td>
      <td>3</td>
      <td>12</td>
      <td>2</td>
      <td>0.528509</td>
      <td>0.545455</td>
      <td>0.016946</td>
    </tr>
    <tr>
      <th>6</th>
      <td>0</td>
      <td>4</td>
      <td>4</td>
      <td>15</td>
      <td>2</td>
      <td>0.000000</td>
      <td>0.332101</td>
      <td>0.332101</td>
    </tr>
    <tr>
      <th>7</th>
      <td>0</td>
      <td>4</td>
      <td>4</td>
      <td>15</td>
      <td>0</td>
      <td>0.332101</td>
      <td>0.384472</td>
      <td>0.052371</td>
    </tr>
    <tr>
      <th>8</th>
      <td>0</td>
      <td>4</td>
      <td>4</td>
      <td>15</td>
      <td>1</td>
      <td>0.384472</td>
      <td>0.545455</td>
      <td>0.160983</td>
    </tr>
    <tr>
      <th>9</th>
      <td>0</td>
      <td>5</td>
      <td>5</td>
      <td>15</td>
      <td>2</td>
      <td>0.000000</td>
      <td>0.072761</td>
      <td>0.072761</td>
    </tr>
  </tbody>
</table>
</div>



Posterior-vector input is useful when you want stochastic maps conditioned on inferred node uncertainty, or a fixed internal node state, rather than only on scalar observed states at the tips. Do not mix scalar states and posterior vectors in one call; use one input mode for all non-missing entries.

## Related APIs

- `tree.pcm.simulate_stochastic_map()` samples stochastic-map results with segment, event, dwell-time, transition-count, node-state, and branch-specific summary tables.
- `tree.annotate.add_edge_stochastic_map()` draws one replicate on an existing tree plot.
- `tree.pcm.fit_discrete_ctmc()` fits the Mk model used for mapping.
- `tree.pcm.infer_ancestral_states_discrete_ctmc()` estimates node-state posteriors that can be used as mapping constraints.
- `tree.pcm.simulate_discrete_trait()` creates example discrete traits for testing workflows.

## References

- Nielsen, R. 2002. Mapping mutations on phylogenies. *Systematic Biology* 51:729-739. https://doi.org/10.1080/10635150290102393
- Huelsenbeck, J. P., Nielsen, R., and Bollback, J. P. 2003. Stochastic mapping of morphological characters. *Systematic Biology* 52:131-158. https://doi.org/10.1080/10635150390192780
- Bollback, J. P. 2006. SIMMAP: stochastic character mapping of discrete traits on phylogenies. *BMC Bioinformatics* 7:88. https://doi.org/10.1186/1471-2105-7-88
- Minin, V. N., and Suchard, M. A. 2008. Counting labeled transitions in continuous-time Markov models of evolution. *Journal of Mathematical Biology* 56:391-412. https://doi.org/10.1007/s00285-007-0120-8

