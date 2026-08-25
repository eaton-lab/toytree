<div class="nb-md-page-hook" aria-hidden="true"></div>

# Rooting by branch lengths

When no outgroup is available, `toytree` can infer a root position from edge lengths. The three public methods are `root_on_midpoint()`, `root_on_balanced_midpoint()`, and `root_on_minimal_ancestor_deviation()`. All three operate on the current unrooted topology, but they make different assumptions about rate variation.

Use midpoint and balanced midpoint as simple clock-like heuristics. Use MAD when branch-length variation may reflect rate heterogeneity and you want edge-wise scores for alternative roots.



```python
import toytree
from loguru import logger

logger.remove()

```

## Compare the three branch-length methods

This non-ultrametric example is rooted three different ways on the same unrooted topology.



```python
base = toytree.tree("(((a:1,b:1):2,c:4):1,(d:1,e:5):1);")
utree = base.unroot()

mid = utree.mod.root_on_midpoint()
bal = utree.mod.root_on_balanced_midpoint()
mad = utree.mod.root_on_minimal_ancestor_deviation()

c, a, m = toytree.mtree([mid, bal, mad]).draw(
    layout="d",
    node_labels="idx",
    node_sizes=12,
    tip_labels=True,
    width=720,
    height=260,
)
a[0].label.text = "midpoint"
a[1].label.text = "balanced midpoint"
a[2].label.text = "MAD"
c

```




<div class="toyplot" id="tdaadc52066f242a8b0e3b94efe50b710" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="720.0px" height="260.0px" viewBox="0 0 720.0 260.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t6d01af6927f1430aabb2a8b5198820cf"><g class="toyplot-coordinates-Cartesian" id="tebf9d08948e34bcbb43665021a85d136"><clipPath id="tfe1340bf55444a598bd5f4f08b961684"><rect x="20.0" y="40.0" width="160.0" height="180.0"></rect></clipPath><g clip-path="url(#tfe1340bf55444a598bd5f4f08b961684)"><g class="toytree-mark-Toytree" id="tab21c4a378a24a129af5fc0049caa85e"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 53.1 69.9 L 37.4 69.9 L 37.4 94.8" id="5,0" style=""></path><path d="M 53.1 69.9 L 68.7 69.9 L 68.7 194.7" id="5,1" style=""></path><path d="M 115.6 144.8 L 100.0 144.8 L 100.0 169.7" id="6,2" style=""></path><path d="M 115.6 144.8 L 131.3 144.8 L 131.3 169.7" id="6,3" style=""></path><path d="M 139.1 94.8 L 162.6 94.8 L 162.6 194.7" id="7,4" style=""></path><path d="M 96.1 57.4 L 53.1 57.4 L 53.1 69.9" id="8,5" style=""></path><path d="M 139.1 94.8 L 115.6 94.8 L 115.6 144.8" id="7,6" style=""></path><path d="M 96.1 57.4 L 139.1 57.4 L 139.1 94.8" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(53.0673,69.8527)"><circle r="6.0"></circle></g><g id="Node-6" transform="translate(115.644,144.772)"><circle r="6.0"></circle></g><g id="Node-7" transform="translate(139.111,94.8257)"><circle r="6.0"></circle></g><g id="Node-8" transform="translate(96.0889,57.3663)"><circle r="6.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(53.0673,69.8527)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(115.644,144.772)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(139.111,94.8257)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(96.0889,57.3663)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(37.423,94.8257)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(68.7115,194.717)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(100,169.745)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(131.288,169.745)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(162.577,194.717)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g><g transform="translate(100.0,42.0)"><text x="-29.554000000000002" y="-4.823" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:14.0px;font-weight:bold;stroke:none;vertical-align:baseline;white-space:pre">midpoint</text></g></g><g class="toyplot-coordinates-Cartesian" id="tf1c51d3842004674a6ed023c236f19bb"><clipPath id="t7ce59fee812c42ca93eb144ab842a22a"><rect x="200.0" y="40.0" width="160.0" height="180.0"></rect></clipPath><g clip-path="url(#t7ce59fee812c42ca93eb144ab842a22a)"><g class="toytree-mark-Toytree" id="te6f213ab657e4f6dbe1f529b6de9f304"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 233.1 69.9 L 217.4 69.9 L 217.4 94.8" id="5,0" style=""></path><path d="M 233.1 69.9 L 248.7 69.9 L 248.7 194.7" id="5,1" style=""></path><path d="M 295.6 144.8 L 280.0 144.8 L 280.0 169.7" id="6,2" style=""></path><path d="M 295.6 144.8 L 311.3 144.8 L 311.3 169.7" id="6,3" style=""></path><path d="M 319.1 94.8 L 342.6 94.8 L 342.6 194.7" id="7,4" style=""></path><path d="M 276.1 57.4 L 233.1 57.4 L 233.1 69.9" id="8,5" style=""></path><path d="M 319.1 94.8 L 295.6 94.8 L 295.6 144.8" id="7,6" style=""></path><path d="M 276.1 57.4 L 319.1 57.4 L 319.1 94.8" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(233.067,69.8527)"><circle r="6.0"></circle></g><g id="Node-6" transform="translate(295.644,144.772)"><circle r="6.0"></circle></g><g id="Node-7" transform="translate(319.111,94.8257)"><circle r="6.0"></circle></g><g id="Node-8" transform="translate(276.089,57.3663)"><circle r="6.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(233.067,69.8527)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(295.644,144.772)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(319.111,94.8257)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(276.089,57.3663)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(217.423,94.8257)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(248.712,194.717)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(280,169.745)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(311.288,169.745)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(342.577,194.718)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g><g transform="translate(280.0,42.0)"><text x="-61.845000000000006" y="-4.823" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:14.0px;font-weight:bold;stroke:none;vertical-align:baseline;white-space:pre">balanced midpoint</text></g></g><g class="toyplot-coordinates-Cartesian" id="t5270155798f841b4a05bbf7c82dc23ae"><clipPath id="tebba89efa84a4f9682cf717b0ee249c0"><rect x="380.0" y="40.0" width="160.0" height="180.0"></rect></clipPath><g clip-path="url(#tebba89efa84a4f9682cf717b0ee249c0)"><g class="toytree-mark-Toytree" id="t18a61220efad4145a6e8e795fca710d3"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 413.1 90.6 L 397.4 90.6 L 397.4 111.4" id="5,0" style=""></path><path d="M 413.1 90.6 L 428.7 90.6 L 428.7 194.7" id="5,1" style=""></path><path d="M 475.6 107.4 L 460.0 107.4 L 460.0 128.3" id="6,2" style=""></path><path d="M 475.6 107.4 L 491.3 107.4 L 491.3 128.3" id="6,3" style=""></path><path d="M 499.1 65.8 L 522.6 65.8 L 522.6 149.1" id="7,4" style=""></path><path d="M 456.1 57.4 L 413.1 57.4 L 413.1 90.6" id="8,5" style=""></path><path d="M 499.1 65.8 L 475.6 65.8 L 475.6 107.4" id="7,6" style=""></path><path d="M 456.1 57.4 L 499.1 57.4 L 499.1 65.8" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(413.067,90.5876)"><circle r="6.0"></circle></g><g id="Node-6" transform="translate(475.644,107.449)"><circle r="6.0"></circle></g><g id="Node-7" transform="translate(499.111,65.7968)"><circle r="6.0"></circle></g><g id="Node-8" transform="translate(456.089,57.3663)"><circle r="6.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(413.067,90.5876)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(475.644,107.449)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(499.111,65.7968)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(456.089,57.3663)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(397.423,111.414)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(428.712,194.717)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(460,128.275)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(491.288,128.275)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(522.577,149.101)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g><g transform="translate(460.0,42.0)"><text x="-15.939" y="-4.823" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:14.0px;font-weight:bold;stroke:none;vertical-align:baseline;white-space:pre">MAD</text></g></g><g class="toyplot-coordinates-Cartesian" id="t594dda05bbfd4268b5b6104ea74a2319"><clipPath id="t222870d6d1cb498f90945913c2f252c0"><rect x="560.0" y="40.0" width="160.0" height="180.0"></rect></clipPath><g clip-path="url(#t222870d6d1cb498f90945913c2f252c0)"></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



## Midpoint rooting

`tree.mod.root_on_midpoint()` places the root at the midpoint of the longest tip-to-tip path. It is fast and often useful as a first pass, but it assumes a clock-like interpretation of branch lengths.

Reference: Farris, J. S. Estimating phylogenetic trees from distance matrices. *The American Naturalist* 106, 645-668 (1972).



```python
utree.mod.root_on_midpoint().draw(layout="d", node_labels="idx", node_sizes=14);

```


<div class="toyplot" id="td88c43f47d6b467f867666d9f5919503" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t538c430ff26b4091823ab70e180813da"><g class="toyplot-coordinates-Cartesian" id="t777a7bf0fadd41d688d399d806afaa65"><clipPath id="t6e386b52e44044acba2fcb2501b7c091"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t6e386b52e44044acba2fcb2501b7c091)"><g class="toytree-mark-Toytree" id="t25a762aaa2404d329a71daadafd8ca1c"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 81.3 99.6 L 58.4 99.6 L 58.4 125.4" id="5,0" style=""></path><path d="M 81.3 99.6 L 104.2 99.6 L 104.2 228.7" id="5,1" style=""></path><path d="M 172.9 120.5 L 150.0 120.5 L 150.0 146.3" id="6,2" style=""></path><path d="M 172.9 120.5 L 195.8 120.5 L 195.8 146.3" id="6,3" style=""></path><path d="M 207.2 68.8 L 241.6 68.8 L 241.6 172.2" id="7,4" style=""></path><path d="M 144.3 58.3 L 81.3 58.3 L 81.3 99.6" id="8,5" style=""></path><path d="M 207.2 68.8 L 172.9 68.8 L 172.9 120.5" id="7,6" style=""></path><path d="M 144.3 58.3 L 207.2 58.3 L 207.2 68.8" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(81.3328,99.5533)"><circle r="7.0"></circle></g><g id="Node-6" transform="translate(172.889,120.473)"><circle r="7.0"></circle></g><g id="Node-7" transform="translate(207.223,68.7951)"><circle r="7.0"></circle></g><g id="Node-8" transform="translate(144.278,58.3352)"><circle r="7.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(81.3328,99.5533)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(172.889,120.473)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(207.223,68.7951)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(144.278,58.3352)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(58.4438,125.392)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(104.222,228.748)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(150,146.312)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(195.778,146.312)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(241.556,172.151)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Balanced midpoint rooting

`tree.mod.root_on_balanced_midpoint()` solves a related tree-center problem by minimizing the maximum distance from the root to the tips. It is still a clock-like heuristic, but is often less sensitive than simple midpoint rooting to long outlier branches.

The `tolerance` argument controls the stopping criterion when optimizing the position on the chosen edge.



```python
utree.mod.root_on_balanced_midpoint(tolerance=1e-8).draw(
    layout="d",
    node_labels="idx",
    node_sizes=14,
);

```


<div class="toyplot" id="t35d4431f24cd4dfd8c35d1b259fab4c7" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t74bea998aaed4bef93856dd7bd1a6f3e"><g class="toyplot-coordinates-Cartesian" id="t15d4344a1f47400297f5c2e54164c5bc"><clipPath id="t3ce2f65f2bbb448db50147c8d19b844d"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t3ce2f65f2bbb448db50147c8d19b844d)"><g class="toytree-mark-Toytree" id="t1b7e48a245a443578d000789b0a428a4"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 81.3 99.6 L 58.4 99.6 L 58.4 125.4" id="5,0" style=""></path><path d="M 81.3 99.6 L 104.2 99.6 L 104.2 228.7" id="5,1" style=""></path><path d="M 172.9 120.5 L 150.0 120.5 L 150.0 146.3" id="6,2" style=""></path><path d="M 172.9 120.5 L 195.8 120.5 L 195.8 146.3" id="6,3" style=""></path><path d="M 207.2 68.8 L 241.6 68.8 L 241.6 172.2" id="7,4" style=""></path><path d="M 144.3 58.3 L 81.3 58.3 L 81.3 99.6" id="8,5" style=""></path><path d="M 207.2 68.8 L 172.9 68.8 L 172.9 120.5" id="7,6" style=""></path><path d="M 144.3 58.3 L 207.2 58.3 L 207.2 68.8" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(81.3328,99.5533)"><circle r="7.0"></circle></g><g id="Node-6" transform="translate(172.889,120.473)"><circle r="7.0"></circle></g><g id="Node-7" transform="translate(207.223,68.7951)"><circle r="7.0"></circle></g><g id="Node-8" transform="translate(144.278,58.3352)"><circle r="7.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(81.3328,99.5533)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(172.889,120.473)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(207.223,68.7951)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(144.278,58.3352)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(58.4438,125.392)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(104.222,228.748)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(150,146.312)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(195.778,146.312)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(241.556,172.151)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Minimal ancestor deviation (MAD)

`tree.mod.root_on_minimal_ancestor_deviation()` evaluates every rootable edge and chooses the edge and position that minimize the global ancestor-deviation score. It is the most informative branch-length rooting method in `toytree` because it also stores edge-wise support for alternative root positions.

Reference: Tria, F., Landan, G. & Dagan, T. Phylogenetic rooting using minimal ancestor deviation. *Nature Ecology & Evolution* 1, 0193 (2017).



```python
# example adapted from the rooting tests so the returned statistics are stable
madtree = (
    toytree.rtree.rtree(5, seed=123)
    .unroot()
    .set_node_data("name", {i: j for i, j in enumerate("abcdeXYR")})
    .set_node_data("dist", {"e": 5, "Y": 3})
)

mad_rooted, stats = madtree.mod.root_on_minimal_ancestor_deviation(return_stats=True)
stats

```




    {'minimal_ancestor_deviation': 0.3281920104298636,
     'root_ambiguity_index': 0.8020452043139147,
     'root_clock_coefficient_of_variation': 41.54087983900019}



`return_stats=True` returns a rooted tree plus a summary dictionary. The three main values are:

- `minimal_ancestor_deviation`: the best MAD score; lower is better.
- `root_ambiguity_index`: how close the next-best root is to the best root; lower means a clearer optimum.
- `root_clock_coefficient_of_variation`: how far the chosen rooting is from a strict clock interpretation.


## Constrain MAD to a chosen edge with `query`

If you want to evaluate a user-chosen root edge rather than the global optimum, pass a node query. MAD will still optimize the position along that edge and return the corresponding statistics.



```python
mad_opt, opt_stats = madtree.mod.root_on_minimal_ancestor_deviation(return_stats=True)
mad_alt, alt_stats = madtree.mod.root_on_minimal_ancestor_deviation("a", return_stats=True)

c, a, m = toytree.mtree([mad_opt, mad_alt]).draw(
    layout="d",
    node_labels="idx",
    node_sizes=12,
    tip_labels=True,
    width=520,
    height=240,
)
a[0].label.text = f"optimal MAD (CV={opt_stats['root_clock_coefficient_of_variation']:.1f})"
a[1].label.text = f"root constrained to a (CV={alt_stats['root_clock_coefficient_of_variation']:.1f})"
c

```




<div class="toyplot" id="tf99d217204244c7d97212349f959725f" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="520.0px" height="240.0px" viewBox="0 0 520.0 240.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t5edfe230c8c14d90991e3d830bc5ddc4"><g class="toyplot-coordinates-Cartesian" id="t997c636c77c34c4ba10f42709fb6fb8f"><clipPath id="t7be391f7a00c40d7a6c26add963711b5"><rect x="20.0" y="40.0" width="110.0" height="160.0"></rect></clipPath><g clip-path="url(#t7be391f7a00c40d7a6c26add963711b5)"><g class="toytree-mark-Toytree" id="t0b52140fcfca4ae48befceff58e87e0e"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 46.7 81.4 L 37.3 81.4 L 37.3 100.1" id="5,0" style=""></path><path d="M 46.7 81.4 L 56.2 81.4 L 56.2 174.8" id="5,1" style=""></path><path d="M 84.4 107.9 L 75.0 107.9 L 75.0 126.6" id="6,2" style=""></path><path d="M 84.4 107.9 L 93.8 107.9 L 93.8 126.6" id="6,3" style=""></path><path d="M 98.5 89.3 L 112.7 89.3 L 112.7 107.9" id="7,4" style=""></path><path d="M 72.6 57.3 L 46.7 57.3 L 46.7 81.4" id="8,5" style=""></path><path d="M 98.5 89.3 L 84.4 89.3 L 84.4 107.9" id="7,6" style=""></path><path d="M 72.6 57.3 L 98.5 57.3 L 98.5 89.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(46.7442,81.4135)"><circle r="6.0"></circle></g><g id="Node-6" transform="translate(84.4186,107.95)"><circle r="6.0"></circle></g><g id="Node-7" transform="translate(98.5465,89.2734)"><circle r="6.0"></circle></g><g id="Node-8" transform="translate(72.6453,57.3293)"><circle r="6.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(46.7442,81.4135)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(84.4186,107.95)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(98.5465,89.2734)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(72.6453,57.3293)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(37.3256,100.09)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(56.1628,174.794)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(75,126.626)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(93.8372,126.626)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(112.674,107.95)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g></g></g></g><g transform="translate(75.0,42.0)"><text x="-76.818" y="-4.823" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:14.0px;font-weight:bold;stroke:none;vertical-align:baseline;white-space:pre">optimal MAD (CV=41.5)</text></g></g><g class="toyplot-coordinates-Cartesian" id="t5c199560f0b34940a831ebc3ef100cc1"><clipPath id="tc628a5c6eb674214ab6931a549509104"><rect x="150.0" y="40.0" width="110.0" height="160.0"></rect></clipPath><g clip-path="url(#tc628a5c6eb674214ab6931a549509104)"><g class="toytree-mark-Toytree" id="t8ca7177f1f6143efa3ace6b719bdc8a1"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 187.3 57.3 L 167.3 57.3 L 167.3 80.8" id="8,0" style=""></path><path d="M 207.4 57.3 L 186.2 57.3 L 186.2 174.8" id="7,1" style=""></path><path d="M 214.4 151.3 L 205.0 151.3 L 205.0 174.8" id="5,2" style=""></path><path d="M 214.4 151.3 L 223.8 151.3 L 223.8 174.8" id="5,3" style=""></path><path d="M 228.5 127.8 L 242.7 127.8 L 242.7 151.3" id="6,4" style=""></path><path d="M 228.5 127.8 L 214.4 127.8 L 214.4 151.3" id="6,5" style=""></path><path d="M 207.4 57.3 L 228.5 57.3 L 228.5 127.8" id="7,6" style=""></path><path d="M 187.3 57.3 L 207.4 57.3 L 207.4 57.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(214.419,151.301)"><circle r="6.0"></circle></g><g id="Node-6" transform="translate(228.547,127.808)"><circle r="6.0"></circle></g><g id="Node-7" transform="translate(207.355,57.3293)"><circle r="6.0"></circle></g><g id="Node-8" transform="translate(187.34,57.3293)"><circle r="6.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(214.419,151.301)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(228.547,127.808)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(207.355,57.3293)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(187.34,57.3293)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:10px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(167.326,80.8223)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(186.163,174.794)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(205,174.794)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(223.837,174.794)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(242.674,151.301)rotate(90)"><text x="10.0" y="2.5549999999999997" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:10.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g></g></g></g><g transform="translate(205.0,42.0)"><text x="-103.66300000000001" y="-4.823" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:14.0px;font-weight:bold;stroke:none;vertical-align:baseline;white-space:pre">root constrained to a (CV=43.3)</text></g></g><g class="toyplot-coordinates-Cartesian" id="t67982cdcecb542e7a88fe68cbd2e0fbe"><clipPath id="t68cc18cccedd4f939fccf0f1e5212104"><rect x="280.0" y="40.0" width="110.0" height="160.0"></rect></clipPath><g clip-path="url(#t68cc18cccedd4f939fccf0f1e5212104)"></g></g><g class="toyplot-coordinates-Cartesian" id="tf079450a57d24512a95bbd37444abf34"><clipPath id="t11a862e48a1f44b5b751b5b949577611"><rect x="410.0" y="40.0" width="110.0" height="160.0"></rect></clipPath><g clip-path="url(#t11a862e48a1f44b5b751b5b949577611)"></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



## Plot `MAD` and `MAD_root_prob` on branches

The returned rooted tree stores two edge features automatically:

- `MAD`: the deviation score if the tree were rooted on that edge.
- `MAD_root_prob`: the relative support for each possible root edge.



```python
mad_rooted.get_node_data()[["name", "MAD", "MAD_root_prob"]]

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
      <th>MAD</th>
      <th>MAD_root_prob</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>b</td>
      <td>0.616481</td>
      <td>0.107250</td>
    </tr>
    <tr>
      <th>1</th>
      <td>c</td>
      <td>0.616481</td>
      <td>0.107250</td>
    </tr>
    <tr>
      <th>2</th>
      <td>d</td>
      <td>0.507329</td>
      <td>0.137775</td>
    </tr>
    <tr>
      <th>3</th>
      <td>a</td>
      <td>0.439079</td>
      <td>0.156861</td>
    </tr>
    <tr>
      <th>4</th>
      <td>e</td>
      <td>0.409194</td>
      <td>0.165218</td>
    </tr>
    <tr>
      <th>5</th>
      <td>X</td>
      <td>0.507329</td>
      <td>0.137775</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Y</td>
      <td>0.328192</td>
      <td>0.187870</td>
    </tr>
    <tr>
      <th>7</th>
      <td>R</td>
      <td>0.328192</td>
      <td>0.187870</td>
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
c, a, m = mad_rooted.draw(layout="d", width=480, node_sizes=10, node_labels="idx")
mad_rooted.annotate.add_edge_labels(a, "MAD_root_prob", mask=False, font_size=11)
c

```




<div class="toyplot" id="teb7227c6112047e1b139794464622a60" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="480.0px" height="300.0px" viewBox="0 0 480.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tb8edeb90c14f4337b428d5c33b6bf6a6"><g class="toyplot-coordinates-Cartesian" id="t62973d94dde5467182877f725a2c67a3"><clipPath id="tda0a4d4457a747739ae875514c43a4c0"><rect x="35.0" y="35.0" width="410.0" height="230.0"></rect></clipPath><g clip-path="url(#tda0a4d4457a747739ae875514c43a4c0)"><g class="toytree-mark-Toytree" id="t6fde521fe1fb491cb41b9ae1b0cb70e5"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 110.0 130.6 L 66.7 130.6 L 66.7 158.0" id="5,0" style=""></path><path d="M 110.0 130.6 L 153.3 130.6 L 153.3 158.0" id="5,1" style=""></path><path d="M 175.0 103.2 L 240.0 103.2 L 240.0 130.6" id="6,2" style=""></path><path d="M 370.0 91.7 L 326.7 91.7 L 326.7 119.1" id="7,3" style=""></path><path d="M 370.0 91.7 L 413.3 91.7 L 413.3 228.7" id="7,4" style=""></path><path d="M 175.0 103.2 L 110.0 103.2 L 110.0 130.6" id="6,5" style=""></path><path d="M 272.5 56.4 L 175.0 56.4 L 175.0 103.2" id="8,6" style=""></path><path d="M 272.5 56.4 L 370.0 56.4 L 370.0 91.7" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-5" transform="translate(110.024,130.644)"><circle r="5.0"></circle></g><g id="Node-6" transform="translate(175.012,103.248)"><circle r="5.0"></circle></g><g id="Node-7" transform="translate(369.976,91.7182)"><circle r="5.0"></circle></g><g id="Node-8" transform="translate(272.494,56.3889)"><circle r="5.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(110.024,130.644)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(175.012,103.248)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(369.976,91.7182)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(272.494,56.3889)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(66.6988,158.04)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(153.349,158.04)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g><g class="toytree-TipLabel" transform="translate(240,130.644)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(326.651,119.114)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(413.301,228.698)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g></g></g><g class="toyplot-mark-Text" id="t674d8ecafe0b4026a1f8d7e2cb8e724d"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(66.6987898042548,144.3418754150252)"><text x="-16.819000000000003" y="2.8104999999999993" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:11.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0.1073</text></g><g class="toyplot-Datum" transform="translate(153.34939490212741,144.3418754150252)"><text x="-16.819000000000003" y="2.8104999999999993" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:11.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0.1073</text></g><g class="toyplot-Datum" transform="translate(240.0,116.94581502109665)"><text x="-16.819000000000003" y="2.8104999999999993" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:11.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0.1378</text></g><g class="toyplot-Datum" transform="translate(326.65060509787264,105.41619887075603)"><text x="-16.819000000000003" y="2.8104999999999993" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:11.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0.1569</text></g><g class="toyplot-Datum" transform="translate(413.30121019574517,160.2083196586132)"><text x="-16.819000000000003" y="2.8104999999999993" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:11.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0.1652</text></g><g class="toyplot-Datum" transform="translate(110.02409235319111,116.94581502109665)"><text x="-16.819000000000003" y="2.8104999999999993" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:11.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0.1378</text></g><g class="toyplot-Datum" transform="translate(175.01204617659556,79.81833549110075)"><text x="-16.819000000000003" y="2.8104999999999993" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:11.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0.1879</text></g><g class="toyplot-Datum" transform="translate(369.9759076468089,74.05352741593046)"><text x="-16.819000000000003" y="2.8104999999999993" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:11.0px;font-weight:300;opacity:1;stroke:none;vertical-align:baseline;white-space:pre">0.1879</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



## Related APIs

- [`mod-rooting-outgroup.md`](mod-rooting-outgroup.md) for manual outgroup rooting.
- [`mod-rooting-dlc.md`](mod-rooting-dlc.md) for reconciliation-based rooting of gene trees.

