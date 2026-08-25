<div class="nb-md-page-hook" aria-hidden="true"></div>

# Rooting by duplication-loss-coalescence reconciliation

`tree.mod.root_on_minimal_dlc()` roots a gene tree by testing every rootable edge on the unrooted gene-tree topology and choosing the edge with the lowest weighted duplication-loss-coalescence (DLC) reconciliation cost against a rooted species tree.

Use this method when you have a gene tree, a rooted species tree, and a mapping from gene tips to species tips.



```python
import toytree

```

## Main function

`tree.mod.root_on_minimal_dlc(species_tree, imap, return_stats=False, store_scores=False, weight_duplications=3.0, weight_losses=1.0, weight_coalescences=0.0)`

The species tree must already be rooted. In practice it is safest to pass `imap` explicitly, especially when the gene tree contains duplicated genes per species.



```python
species_tree = toytree.tree("(((A,B),C),D);")
gene_tree = toytree.tree("((((a1,a2),b1),c1),d1);")
imap = {"a1": "A", "a2": "A", "b1": "B", "c1": "C", "d1": "D"}

```

## A simple DLC-rooting example

The species tree and gene tree below use the same set of sampled lineages, but the gene tree contains a duplication in species `A`. The rooting algorithm evaluates every candidate root edge on the gene tree and selects the one with the lowest weighted reconciliation cost.



```python
c, a, m = toytree.mtree([species_tree, gene_tree.unroot()]).draw(
    layout="d",
    node_sizes=12,
    node_labels="idx",
    tip_labels=True,
    width=520,
    height=240,
)
a[0].label.text = "rooted species tree"
a[1].label.text = "unrooted gene tree"
c

```




<div class="toyplot" id="t754b766635d84d55851521d1c849499c" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="520.0px" height="240.0px" viewBox="0 0 520.0 240.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t3027a1c2ec0d4a6b8028716d232863da"><g class="toyplot-coordinates-Cartesian" id="tff3d382550df4d95856e7c70961dd3d7"><clipPath id="t06f997345e4e41e7891ce5253a6a19c1"><rect x="20.0" y="40.0" width="110.0" height="160.0"></rect></clipPath><g clip-path="url(#t06f997345e4e41e7891ce5253a6a19c1)"><g class="toytree-mark-Toytree" id="t83fbe013293a41d2909e15248ce63012"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 49.9 134.9 L 37.3 134.9 L 37.3 173.7" id="4,0" style=""></path><path d="M 49.9 134.9 L 62.4 134.9 L 62.4 173.7" id="4,1" style=""></path><path d="M 68.7 96.1 L 87.6 96.1 L 87.6 134.9" id="5,2" style=""></path><path d="M 90.7 57.3 L 112.7 57.3 L 112.7 96.1" id="6,3" style=""></path><path d="M 68.7 96.1 L 49.9 96.1 L 49.9 134.9" id="5,4" style=""></path><path d="M 90.7 57.3 L 68.7 57.3 L 68.7 96.1" id="6,5" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-4" transform="translate(49.8837,134.934)"><circle r="6.0"></circle></g><g id="Node-5" transform="translate(68.7209,96.1238)"><circle r="6.0"></circle></g><g id="Node-6" transform="translate(90.6977,57.3141)"><circle r="6.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(49.8837,134.934)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(68.7209,96.1238)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(90.6977,57.3141)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(37.3256,173.743)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">A</text></g><g class="toytree-TipLabel" transform="translate(62.4419,173.743)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">B</text></g><g class="toytree-TipLabel" transform="translate(87.5581,134.934)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">C</text></g><g class="toytree-TipLabel" transform="translate(112.674,96.1238)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">D</text></g></g></g></g><g transform="translate(75.0,42.0)"><text x="-64.19" y="-4.823" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:14.0px;font-weight:bold;stroke:none;vertical-align:baseline;white-space:pre">rooted species tree</text></g></g><g class="toyplot-coordinates-Cartesian" id="tc980b8a66f884025ba81eab714c04c77"><clipPath id="ta50f65a6c29a459dbb4f57aa600820d1"><rect x="150.0" y="40.0" width="110.0" height="160.0"></rect></clipPath><g clip-path="url(#ta50f65a6c29a459dbb4f57aa600820d1)"><g class="toytree-mark-Toytree" id="t7bd6eddf90dc46afbb1ea45f789139da"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 176.9 131.8 L 167.5 131.8 L 167.5 169.0" id="5,0" style=""></path><path d="M 176.9 131.8 L 186.2 131.8 L 186.2 169.0" id="5,1" style=""></path><path d="M 190.9 94.6 L 205.0 94.6 L 205.0 131.8" id="6,2" style=""></path><path d="M 219.1 57.4 L 223.8 57.4 L 223.8 94.6" id="7,3" style=""></path><path d="M 219.1 57.4 L 242.5 57.4 L 242.5 131.8" id="7,4" style=""></path><path d="M 190.9 94.6 L 176.9 94.6 L 176.9 131.8" id="6,5" style=""></path><path d="M 219.1 57.4 L 190.9 57.4 L 190.9 94.6" id="7,6" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(176.853,131.832)"><circle r="6.0"></circle></g><g id="Node-6" transform="translate(190.927,94.6406)"><circle r="6.0"></circle></g><g id="Node-7" transform="translate(219.073,57.4489)"><circle r="6.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(176.853,131.832)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(190.927,94.6406)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(219.073,57.4489)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(167.471,169.024)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a1</text></g><g class="toytree-TipLabel" transform="translate(186.236,169.024)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a2</text></g><g class="toytree-TipLabel" transform="translate(205,131.832)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b1</text></g><g class="toytree-TipLabel" transform="translate(223.764,94.6406)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c1</text></g><g class="toytree-TipLabel" transform="translate(242.529,131.832)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d1</text></g></g></g></g><g transform="translate(205.0,42.0)"><text x="-63.399" y="-4.823" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:14.0px;font-weight:bold;stroke:none;vertical-align:baseline;white-space:pre">unrooted gene tree</text></g></g><g class="toyplot-coordinates-Cartesian" id="t48f5a53dc04c479f923e56f91dcad8aa"><clipPath id="t826f9e7f1cbc4729acc7dc70839a4fca"><rect x="280.0" y="40.0" width="110.0" height="160.0"></rect></clipPath><g clip-path="url(#t826f9e7f1cbc4729acc7dc70839a4fca)"></g></g><g class="toyplot-coordinates-Cartesian" id="t43415343bf4f4bc09a9ffbe32fb5c6d6"><clipPath id="tdec820943b5947c29243ca610e9bf31d"><rect x="410.0" y="40.0" width="110.0" height="160.0"></rect></clipPath><g clip-path="url(#tdec820943b5947c29243ca610e9bf31d)"></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>




```python
rooted_gene = gene_tree.mod.root_on_minimal_dlc(species_tree, imap)
rooted_gene.draw(layout="d", node_labels="idx", node_sizes=12);

```


<div class="toyplot" id="t1f7c199f0427457182853098d0088b9d" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t09585c11087a4f208a6fdc2f79d35370"><g class="toyplot-coordinates-Cartesian" id="t19a4c07d7edd4e3181931a9219a69571"><clipPath id="t893a862731c2498db43ba193708c5e1f"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t893a862731c2498db43ba193708c5e1f)"><g class="toytree-mark-Toytree" id="tedb3d5ce36c04411bf6e79862374feab"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 129.8 57.5 L 57.5 57.5 L 57.5 98.5" id="8,0" style=""></path><path d="M 126.9 180.7 L 103.7 180.7 L 103.7 221.8" id="5,1" style=""></path><path d="M 126.9 180.7 L 150.0 180.7 L 150.0 221.8" id="5,2" style=""></path><path d="M 161.6 139.6 L 196.3 139.6 L 196.3 180.7" id="6,3" style=""></path><path d="M 202.0 98.5 L 242.5 98.5 L 242.5 139.6" id="7,4" style=""></path><path d="M 161.6 139.6 L 126.9 139.6 L 126.9 180.7" id="6,5" style=""></path><path d="M 202.0 98.5 L 161.6 98.5 L 161.6 139.6" id="7,6" style=""></path><path d="M 129.8 57.5 L 202.0 57.5 L 202.0 98.5" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(126.874,180.709)"><circle r="6.0"></circle></g><g id="Node-6" transform="translate(161.563,139.627)"><circle r="6.0"></circle></g><g id="Node-7" transform="translate(202.033,98.5459)"><circle r="6.0"></circle></g><g id="Node-8" transform="translate(129.765,57.4645)"><circle r="6.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(126.874,180.709)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(161.563,139.627)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(202.033,98.5459)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(129.765,57.4645)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(57.4971,98.5459)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d1</text></g><g class="toytree-TipLabel" transform="translate(103.749,221.79)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a1</text></g><g class="toytree-TipLabel" transform="translate(150,221.79)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a2</text></g><g class="toytree-TipLabel" transform="translate(196.251,180.709)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b1</text></g><g class="toytree-TipLabel" transform="translate(242.503,139.627)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c1</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Inspect the selected root with `return_stats=True`

If you request stats, the function returns `(tree, stats)`. The stats dictionary includes the chosen edge, the weighted score, the event counts on that best solution, and a full score table for all candidate edges.



```python
rooted_gene, stats = gene_tree.mod.root_on_minimal_dlc(
    species_tree,
    imap,
    return_stats=True,
)

stats["best_edge_idx"], stats["best_score"], stats["best_counts"]

```




    (4, 3.0, {'duplications': 1, 'losses': 0, 'coalescences': 0})




```python
stats["score_table"]

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
      <th>edge_idx</th>
      <th>duplications</th>
      <th>losses</th>
      <th>coalescences</th>
      <th>score</th>
      <th>root_clock_cv</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>4</td>
      <td>1</td>
      <td>0</td>
      <td>0</td>
      <td>3.0</td>
      <td>41.649656</td>
    </tr>
    <tr>
      <th>1</th>
      <td>6</td>
      <td>2</td>
      <td>3</td>
      <td>1</td>
      <td>9.0</td>
      <td>23.328474</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>2</td>
      <td>3</td>
      <td>1</td>
      <td>9.0</td>
      <td>43.817805</td>
    </tr>
    <tr>
      <th>3</th>
      <td>5</td>
      <td>3</td>
      <td>7</td>
      <td>3</td>
      <td>16.0</td>
      <td>38.095238</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2</td>
      <td>3</td>
      <td>7</td>
      <td>3</td>
      <td>16.0</td>
      <td>42.599822</td>
    </tr>
    <tr>
      <th>5</th>
      <td>0</td>
      <td>3</td>
      <td>10</td>
      <td>6</td>
      <td>19.0</td>
      <td>56.568542</td>
    </tr>
    <tr>
      <th>6</th>
      <td>1</td>
      <td>3</td>
      <td>10</td>
      <td>6</td>
      <td>19.0</td>
      <td>56.568542</td>
    </tr>
  </tbody>
</table>
</div>



## Store per-edge scores with `store_scores=True`

When `store_scores=True`, the returned tree stores two edge features:

- `DLC`: the weighted reconciliation score for rooting on each edge.
- `DLC_root_prob`: a simple probability mass spread across the tied best edges.



```python
scored_gene = gene_tree.mod.root_on_minimal_dlc(
    species_tree,
    imap,
    store_scores=True,
)

scored_gene.get_node_data()[["name", "DLC", "DLC_root_prob"]]

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
      <th>name</th>
      <th>DLC</th>
      <th>DLC_root_prob</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>d1</td>
      <td>3.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>a1</td>
      <td>19.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>a2</td>
      <td>19.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>b1</td>
      <td>16.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>c1</td>
      <td>9.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>5</th>
      <td></td>
      <td>16.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>6</th>
      <td></td>
      <td>9.0</td>
      <td>0.0</td>
    </tr>
    <tr>
      <th>7</th>
      <td></td>
      <td>3.0</td>
      <td>1.0</td>
    </tr>
    <tr>
      <th>8</th>
      <td>root</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>




```python
c, a, m = scored_gene.draw(layout="d", width=480, node_sizes=10, node_labels="idx")
scored_gene.annotate.add_edge_labels(a, "DLC_root_prob", mask=False, font_size=11)
c

```




<div class="toyplot" id="t57fd2e0bca52403a98faa362652d5138" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="480.0px" height="300.0px" viewBox="0 0 480.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t9c7be08676c84bd8b76731fbf3161057"><g class="toyplot-coordinates-Cartesian" id="tb878907270544c798b2d8f245906098f"><clipPath id="t81da1b3aa71a49b1a3a38b9789e86b08"><rect x="35.0" y="35.0" width="410.0" height="230.0"></rect></clipPath><g clip-path="url(#t81da1b3aa71a49b1a3a38b9789e86b08)"><g class="toytree-mark-Toytree" id="t733cafa94d454de79e7182eca29e6712"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 200.0 56.5 L 57.2 56.5 L 57.2 97.8" id="8,0" style=""></path><path d="M 194.3 180.5 L 148.6 180.5 L 148.6 221.8" id="5,1" style=""></path><path d="M 194.3 180.5 L 240.0 180.5 L 240.0 221.8" id="5,2" style=""></path><path d="M 262.9 139.1 L 331.4 139.1 L 331.4 180.5" id="6,3" style=""></path><path d="M 342.8 97.8 L 422.8 97.8 L 422.8 139.1" id="7,4" style=""></path><path d="M 262.9 139.1 L 194.3 139.1 L 194.3 180.5" id="6,5" style=""></path><path d="M 342.8 97.8 L 262.9 97.8 L 262.9 139.1" id="7,6" style=""></path><path d="M 200.0 56.5 L 342.8 56.5 L 342.8 97.8" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(194.3,180.453)"><circle r="5.0"></circle></g><g id="Node-6" transform="translate(262.85,139.126)"><circle r="5.0"></circle></g><g id="Node-7" transform="translate(342.825,97.7987)"><circle r="5.0"></circle></g><g id="Node-8" transform="translate(200.012,56.4716)"><circle r="5.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(194.3,180.453)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(262.85,139.126)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(342.825,97.7987)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(200.012,56.4716)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(57.1996,97.7987)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d1</text></g><g class="toytree-TipLabel" transform="translate(148.6,221.78)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a1</text></g><g class="toytree-TipLabel" transform="translate(240,221.78)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a2</text></g><g class="toytree-TipLabel" transform="translate(331.4,180.453)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b1</text></g><g class="toytree-TipLabel" transform="translate(422.8,139.126)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c1</text></g></g></g><g class="toyplot-mark-Text" id="t463d263e87474593ae19381c73104d8b"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(57.199623042256654,77.13512686805414)"><text x="-3.0580000000000003" y="2.8104999999999993" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:11.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g class="toyplot-Datum" transform="translate(148.59981152112834,201.11634839155238)"><text x="-3.0580000000000003" y="2.8104999999999993" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:11.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g class="toyplot-Datum" transform="translate(240.00000000000006,201.11634839155238)"><text x="-3.0580000000000003" y="2.8104999999999993" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:11.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g class="toyplot-Datum" transform="translate(331.40018847887177,159.7892745503863)"><text x="-3.0580000000000003" y="2.8104999999999993" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:11.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g class="toyplot-Datum" transform="translate(422.80037695774337,118.46220070922024)"><text x="-3.0580000000000003" y="2.8104999999999993" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:11.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g class="toyplot-Datum" transform="translate(194.2999057605642,159.7892745503863)"><text x="-3.0580000000000003" y="2.8104999999999993" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:11.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g class="toyplot-Datum" transform="translate(262.85004711971794,118.46220070922024)"><text x="-3.0580000000000003" y="2.8104999999999993" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:11.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g class="toyplot-Datum" transform="translate(342.8252120387307,77.13512686805414)"><text x="-3.0580000000000003" y="2.8104999999999993" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:11.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">1</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



## Change the objective with the weight parameters

The default objective emphasizes duplications more heavily than losses and ignores coalescences. You can change that balance by adjusting the three weight parameters. In this example the preferred root stays the same, but the edge scores and ranking criterion change.



```python
_, default_stats = gene_tree.mod.root_on_minimal_dlc(
    species_tree,
    imap,
    return_stats=True,
)
_, alt_stats = gene_tree.mod.root_on_minimal_dlc(
    species_tree,
    imap,
    return_stats=True,
    weight_duplications=0.5,
    weight_losses=3.0,
    weight_coalescences=0.0,
)

comparison = default_stats["score_table"][["edge_idx", "score"]].rename(
    columns={"score": "default_score"}
).merge(
    alt_stats["score_table"][["edge_idx", "score"]].rename(
        columns={"score": "loss_weighted_score"}
    ),
    on="edge_idx",
)
comparison

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
      <th>edge_idx</th>
      <th>default_score</th>
      <th>loss_weighted_score</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>4</td>
      <td>3.0</td>
      <td>0.5</td>
    </tr>
    <tr>
      <th>1</th>
      <td>6</td>
      <td>9.0</td>
      <td>10.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>3</td>
      <td>9.0</td>
      <td>10.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>5</td>
      <td>16.0</td>
      <td>22.5</td>
    </tr>
    <tr>
      <th>4</th>
      <td>2</td>
      <td>16.0</td>
      <td>22.5</td>
    </tr>
    <tr>
      <th>5</th>
      <td>0</td>
      <td>19.0</td>
      <td>31.5</td>
    </tr>
    <tr>
      <th>6</th>
      <td>1</td>
      <td>19.0</td>
      <td>31.5</td>
    </tr>
  </tbody>
</table>
</div>



## Related APIs

- [`mod-rooting-outgroup.md`](mod-rooting-outgroup.md) for manual rooting.
- [`mod-rooting-branch-length.md`](mod-rooting-branch-length.md) for midpoint, balanced midpoint, and MAD rooting.

