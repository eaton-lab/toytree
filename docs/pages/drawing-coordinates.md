<div class="nb-md-page-hook" aria-hidden="true"></div>

# Drawing coordinates

This guide describes the Cartesian coordinates and axis styling in ``toytree`` plots.

## Cartesian object

The `draw` command returns three objects (``Canvas``, ``Cartesian``, and ``Mark``) of which the ``Cartesian`` plays a critical role, defining both the coordinate space on which data is plotted, and the styling of axes spines, ticks, labels, and tick labels. 


```python
import toyplot
import toytree
tree = toytree.rtree.unittree(10, seed=123, treeheight=4)
```

## Tree layout and positioning
Tree drawings are positioned so that a particular node is always placed at an expected location in Cartesian coordinate space. This depends primarily on the ``layout`` style of the tree drawing, where Linear layouts (``r``, ``l``, ``u``, ``d``) place node 0 at position (0, 0), whereas the Circular (``c``) or Unrooted (``unr``) layouts place the root node at position (0, 0). 

All other nodes are positioned along the 'depth' and 'span' axes, which vary depending on the layout.

- **Depth-axis**: The depth axis represents the distance between the root treenode and the tip nodes, and depends on the edge 'dist' values on the tree.

- **Span-axis**: The span axis represents the axis along which tip nodes are spaced. The default spacing between tips is 1 unit.

The plots below show how node positions vary under different layouts by using an overlay grid to highight the coordinate space.

#### Linear right
In the linear right layout Node idx=0 is positioned at (0, 0). The depth-axis corresponds to -treeheight to 0 along the x-axis, while the span-axis corresponds to 0 to ntips along the y-axis.


```python
# draw a tree with 'depth' axis (x) scale_bar
canvas, axes, mark = tree.draw(ts='o', layout='r', node_mask=False, height=350, width=350);

# overlay a grid 
axes.hlines(range(0, tree.ntips), style={"stroke": "red", "stroke-dasharray": "2,4"})
axes.vlines(range(-4, 1), style={"stroke": "blue", "stroke-dasharray": "2,4"});

# show both span and depth axes
axes.x.show = True
axes.x.ticks.show = True
axes.y.show = True
axes.y.ticks.show = True
axes.y.ticks.locator = toyplot.locator.Explicit(locations=range(0, tree.ntips))
```


<div class="toyplot" id="tf730c869ed0040a1afb0250f178ef9a4" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="350.0px" height="350.0px" viewBox="0 0 350.0 350.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t0f842ca518e9425db4988868440044b5"><g class="toyplot-coordinates-Cartesian" id="t31d4bbb77ae54d39bc5aedd3039a3661"><clipPath id="t5957ae5efc774ff6ad9a7f735e58e296"><rect x="35.0" y="35.0" width="280.0" height="280.0"></rect></clipPath><g clip-path="url(#t5957ae5efc774ff6ad9a7f735e58e296)"><g class="toytree-mark-Toytree" id="t070ea04aceb84ea09c494aef876d7b4d"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 79.8 273.2 L 274.7 292.8" id="11,0" style=""></path><path d="M 128.5 253.5 L 274.7 266.6" id="10,1" style=""></path><path d="M 128.5 253.5 L 274.7 240.5" id="10,2" style=""></path><path d="M 177.2 201.2 L 274.7 214.3" id="12,3" style=""></path><path d="M 177.2 201.2 L 274.7 188.1" id="12,4" style=""></path><path d="M 128.5 181.5 L 274.7 161.9" id="13,5" style=""></path><path d="M 128.5 112.8 L 274.7 135.7" id="16,6" style=""></path><path d="M 177.2 89.9 L 274.7 109.5" id="15,7" style=""></path><path d="M 226.0 70.3 L 274.7 83.4" id="14,8" style=""></path><path d="M 226.0 70.3 L 274.7 57.2" id="14,9" style=""></path><path d="M 79.8 273.2 L 128.5 253.5" id="11,10" style=""></path><path d="M 55.4 210.2 L 79.8 273.2" id="18,11" style=""></path><path d="M 128.5 181.5 L 177.2 201.2" id="13,12" style=""></path><path d="M 79.8 147.2 L 128.5 181.5" id="17,13" style=""></path><path d="M 177.2 89.9 L 226.0 70.3" id="15,14" style=""></path><path d="M 128.5 112.8 L 177.2 89.9" id="16,15" style=""></path><path d="M 79.8 147.2 L 128.5 112.8" id="17,16" style=""></path><path d="M 55.4 210.2 L 79.8 147.2" id="18,17" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 274.7 292.8 L 274.7 292.8"></path><path d="M 274.7 266.6 L 274.7 266.6"></path><path d="M 274.7 240.5 L 274.7 240.5"></path><path d="M 274.7 214.3 L 274.7 214.3"></path><path d="M 274.7 188.1 L 274.7 188.1"></path><path d="M 274.7 161.9 L 274.7 161.9"></path><path d="M 274.7 135.7 L 274.7 135.7"></path><path d="M 274.7 109.5 L 274.7 109.5"></path><path d="M 274.7 83.4 L 274.7 83.4"></path><path d="M 274.7 57.2 L 274.7 57.2"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(274.682,292.823)"><circle r="4.0"></circle></g><g id="Node-1" transform="translate(274.682,266.64)"><circle r="4.0"></circle></g><g id="Node-2" transform="translate(274.682,240.457)"><circle r="4.0"></circle></g><g id="Node-3" transform="translate(274.682,214.274)"><circle r="4.0"></circle></g><g id="Node-4" transform="translate(274.682,188.091)"><circle r="4.0"></circle></g><g id="Node-5" transform="translate(274.682,161.909)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(274.682,135.726)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(274.682,109.543)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(274.682,83.3603)"><circle r="4.0"></circle></g><g id="Node-9" transform="translate(274.682,57.1775)"><circle r="4.0"></circle></g><g id="Node-10" transform="translate(128.511,253.548)"><circle r="4.0"></circle></g><g id="Node-11" transform="translate(79.7869,273.185)"><circle r="4.0"></circle></g><g id="Node-12" transform="translate(177.234,201.183)"><circle r="4.0"></circle></g><g id="Node-13" transform="translate(128.511,181.546)"><circle r="4.0"></circle></g><g id="Node-14" transform="translate(225.958,70.2689)"><circle r="4.0"></circle></g><g id="Node-15" transform="translate(177.234,89.906)"><circle r="4.0"></circle></g><g id="Node-16" transform="translate(128.511,112.816)"><circle r="4.0"></circle></g><g id="Node-17" transform="translate(79.7869,147.181)"><circle r="4.0"></circle></g><g id="Node-18" transform="translate(55.425,210.183)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(274.682,292.823)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(274.682,266.64)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(274.682,240.457)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(274.682,214.274)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(274.682,188.091)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(274.682,161.909)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(274.682,135.726)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(274.682,109.543)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(274.682,83.3603)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(274.682,57.1775)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g><g class="toyplot-mark-AxisLines" style="stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0" id="te274ab1a788344579a469488b7fcabc4"><g class="toyplot-Series"><line class="toyplot-Datum" y1="292.822516233492" y2="292.822516233492" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="266.6397348482716" y2="266.6397348482716" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="240.45695346305115" y2="240.45695346305115" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="214.27417207783068" y2="214.27417207783068" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="188.09139069261022" y2="188.09139069261022" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="161.9086093073898" y2="161.9086093073898" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="135.72582792216934" y2="135.72582792216934" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="109.54304653694892" y2="109.54304653694892" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="83.36026515172847" y2="83.36026515172847" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="57.17748376650801" y2="57.17748376650801" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line></g></g><g class="toyplot-mark-AxisLines" style="stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0" id="t0e63b6af9bdb4f10a2087e2d6efb59de"><g class="toyplot-Series"><line class="toyplot-Datum" x1="55.425025470068434" x2="55.425025470068434" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="110.23924393138242" x2="110.23924393138242" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="165.0534623926964" x2="165.0534623926964" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="219.86768085401036" x2="219.86768085401036" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="274.68189931532436" x2="274.68189931532436" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line></g></g></g><g class="toyplot-coordinates-Axis" id="t9d86a32975d74d97be760da9e007d992" transform="translate(50.0,300.0)translate(0,15.0)"><line x1="4.890314687304391" y1="0" x2="227.17734592841288" y2="0" style=""></line><g><line x1="4.890314687304391" y1="0" x2="4.890314687304391" y2="-5" style=""></line><line x1="60.46207249758152" y1="0" x2="60.46207249758152" y2="-5" style=""></line><line x1="116.03383030785865" y1="0" x2="116.03383030785865" y2="-5" style=""></line><line x1="171.60558811813576" y1="0" x2="171.60558811813576" y2="-5" style=""></line><line x1="227.17734592841288" y1="0" x2="227.17734592841288" y2="-5" style=""></line></g><g><g transform="translate(4.890314687304391,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-4</text></g><g transform="translate(60.46207249758152,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-3</text></g><g transform="translate(116.03383030785865,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-2</text></g><g transform="translate(171.60558811813576,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-1</text></g><g transform="translate(227.17734592841288,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g><g class="toyplot-coordinates-Axis" id="t56643302e7e14878ad58709277c32941" transform="translate(50.0,300.0)rotate(-90.0)translate(0,-15.0)"><line x1="6.80786686838123" y1="0" x2="243.1921331316188" y2="0" style=""></line><g><line x1="6.80786686838123" y1="0" x2="6.80786686838123" y2="5" style=""></line><line x1="33.07278534207429" y1="0" x2="33.07278534207429" y2="5" style=""></line><line x1="59.33770381576734" y1="0" x2="59.33770381576734" y2="5" style=""></line><line x1="85.6026222894604" y1="0" x2="85.6026222894604" y2="5" style=""></line><line x1="111.86754076315347" y1="0" x2="111.86754076315347" y2="5" style=""></line><line x1="138.13245923684653" y1="0" x2="138.13245923684653" y2="5" style=""></line><line x1="164.3973777105396" y1="0" x2="164.3973777105396" y2="5" style=""></line><line x1="190.66229618423264" y1="0" x2="190.66229618423264" y2="5" style=""></line><line x1="216.9272146579257" y1="0" x2="216.9272146579257" y2="5" style=""></line><line x1="243.1921331316188" y1="0" x2="243.1921331316188" y2="5" style=""></line></g><g><g transform="translate(6.80786686838123,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(33.07278534207429,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(59.33770381576734,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(85.6026222894604,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(111.86754076315347,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(138.13245923684653,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">5</text></g><g transform="translate(164.3973777105396,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">6</text></g><g transform="translate(190.66229618423264,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">7</text></g><g transform="translate(216.9272146579257,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">8</text></g><g transform="translate(243.1921331316188,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">9</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t0f842ca518e9425db4988868440044b5";
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
        })(modules["toyplot.coordinates.Axis"],"t9d86a32975d74d97be760da9e007d992",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.4106880000000004, "min": -4.088}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 250.0, "min": 0.0}, "scale": "linear"}]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"t56643302e7e14878ad58709277c32941",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 9.2592, "min": -0.2591999999999996}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 250.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


#### Linear down
In the linear down layout Node idx=0 is positioned at (0, 0). The depth-axis corresponds to -treeheight to 0 along the y-axis, while the span-axis corresponds to 0 to ntips along the x-axis. In other words, the x and y are swapped relative to linear-right.


```python
# draw a tree with 'depth' axis (x) scale_bar
canvas, axes, mark = tree.draw(ts='o', layout='d', node_mask=False, height=350, width=350);

# overlay a grid 
axes.vlines(range(0, tree.ntips), style={"stroke": "red", "stroke-dasharray": "2,4"})
axes.hlines(range(0, 4), style={"stroke": "blue", "stroke-dasharray": "2,4"});

# show both span and depth axes
axes.y.show = True
axes.y.ticks.show = True
axes.x.show = True
axes.x.ticks.show = True
axes.x.ticks.locator = toyplot.locator.Explicit(locations=range(0, tree.ntips))
```


<div class="toyplot" id="t2dffa41a63024385a32fb4e94b524ada" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="350.0px" height="350.0px" viewBox="0 0 350.0 350.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t831e999f1e99474a91a61437d3745d72"><g class="toyplot-coordinates-Cartesian" id="t38c9fb595c4c4f3f8a5073e3381f3371"><clipPath id="t048491c73e85401a962f5bc6dcd4c118"><rect x="35.0" y="35.0" width="280.0" height="280.0"></rect></clipPath><g clip-path="url(#t048491c73e85401a962f5bc6dcd4c118)"><g class="toytree-mark-Toytree" id="t39a6d64c01784429aeb88278d213b9d4"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 76.8 79.8 L 57.2 274.7" id="11,0" style=""></path><path d="M 96.5 128.5 L 83.4 274.7" id="10,1" style=""></path><path d="M 96.5 128.5 L 109.5 274.7" id="10,2" style=""></path><path d="M 148.8 177.2 L 135.7 274.7" id="12,3" style=""></path><path d="M 148.8 177.2 L 161.9 274.7" id="12,4" style=""></path><path d="M 168.5 128.5 L 188.1 274.7" id="13,5" style=""></path><path d="M 237.2 128.5 L 214.3 274.7" id="16,6" style=""></path><path d="M 260.1 177.2 L 240.5 274.7" id="15,7" style=""></path><path d="M 279.7 226.0 L 266.6 274.7" id="14,8" style=""></path><path d="M 279.7 226.0 L 292.8 274.7" id="14,9" style=""></path><path d="M 76.8 79.8 L 96.5 128.5" id="11,10" style=""></path><path d="M 139.8 55.4 L 76.8 79.8" id="18,11" style=""></path><path d="M 168.5 128.5 L 148.8 177.2" id="13,12" style=""></path><path d="M 202.8 79.8 L 168.5 128.5" id="17,13" style=""></path><path d="M 260.1 177.2 L 279.7 226.0" id="15,14" style=""></path><path d="M 237.2 128.5 L 260.1 177.2" id="16,15" style=""></path><path d="M 202.8 79.8 L 237.2 128.5" id="17,16" style=""></path><path d="M 139.8 55.4 L 202.8 79.8" id="18,17" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 57.2 274.7 L 57.2 274.7"></path><path d="M 83.4 274.7 L 83.4 274.7"></path><path d="M 109.5 274.7 L 109.5 274.7"></path><path d="M 135.7 274.7 L 135.7 274.7"></path><path d="M 161.9 274.7 L 161.9 274.7"></path><path d="M 188.1 274.7 L 188.1 274.7"></path><path d="M 214.3 274.7 L 214.3 274.7"></path><path d="M 240.5 274.7 L 240.5 274.7"></path><path d="M 266.6 274.7 L 266.6 274.7"></path><path d="M 292.8 274.7 L 292.8 274.7"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(57.1775,274.682)"><circle r="4.0"></circle></g><g id="Node-1" transform="translate(83.3603,274.682)"><circle r="4.0"></circle></g><g id="Node-2" transform="translate(109.543,274.682)"><circle r="4.0"></circle></g><g id="Node-3" transform="translate(135.726,274.682)"><circle r="4.0"></circle></g><g id="Node-4" transform="translate(161.909,274.682)"><circle r="4.0"></circle></g><g id="Node-5" transform="translate(188.091,274.682)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(214.274,274.682)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(240.457,274.682)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(266.64,274.682)"><circle r="4.0"></circle></g><g id="Node-9" transform="translate(292.823,274.682)"><circle r="4.0"></circle></g><g id="Node-10" transform="translate(96.4517,128.511)"><circle r="4.0"></circle></g><g id="Node-11" transform="translate(76.8146,79.7869)"><circle r="4.0"></circle></g><g id="Node-12" transform="translate(148.817,177.234)"><circle r="4.0"></circle></g><g id="Node-13" transform="translate(168.454,128.511)"><circle r="4.0"></circle></g><g id="Node-14" transform="translate(279.731,225.958)"><circle r="4.0"></circle></g><g id="Node-15" transform="translate(260.094,177.234)"><circle r="4.0"></circle></g><g id="Node-16" transform="translate(237.184,128.511)"><circle r="4.0"></circle></g><g id="Node-17" transform="translate(202.819,79.7869)"><circle r="4.0"></circle></g><g id="Node-18" transform="translate(139.817,55.425)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(57.1775,274.682)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(83.3603,274.682)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(109.543,274.682)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(135.726,274.682)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(161.909,274.682)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(188.091,274.682)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(214.274,274.682)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(240.457,274.682)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(266.64,274.682)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(292.823,274.682)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g><g class="toyplot-mark-AxisLines" style="stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0" id="t51e54061ca264aaeb9ee6fbe83141f20"><g class="toyplot-Series"><line class="toyplot-Datum" x1="57.17748376650796" x2="57.17748376650796" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="83.36026515172841" x2="83.36026515172841" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="109.54304653694885" x2="109.54304653694885" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="135.7258279221693" x2="135.7258279221693" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="161.90860930738975" x2="161.90860930738975" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="188.0913906926102" x2="188.0913906926102" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="214.27417207783066" x2="214.27417207783066" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="240.4569534630511" x2="240.4569534630511" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="266.63973484827153" x2="266.63973484827153" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="292.822516233492" x2="292.822516233492" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line></g></g><g class="toyplot-mark-AxisLines" style="stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0" id="tcb23c842196c4e079a4174eb3568fb53"><g class="toyplot-Series"><line class="toyplot-Datum" y1="274.6818993153243" y2="274.6818993153243" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="219.8676808540103" y2="219.8676808540103" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="165.05346239269636" y2="165.05346239269636" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="110.23924393138242" y2="110.23924393138242" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line></g></g></g><g class="toyplot-coordinates-Axis" id="t7598b4c7f3cd46f5a12dc50cdea73302" transform="translate(50.0,300.0)translate(0,15.0)"><line x1="6.807866868381236" y1="0" x2="243.1921331316188" y2="0" style=""></line><g><line x1="6.807866868381236" y1="0" x2="6.807866868381236" y2="-5" style=""></line><line x1="33.07278534207429" y1="0" x2="33.07278534207429" y2="-5" style=""></line><line x1="59.337703815767355" y1="0" x2="59.337703815767355" y2="-5" style=""></line><line x1="85.60262228946041" y1="0" x2="85.60262228946041" y2="-5" style=""></line><line x1="111.86754076315347" y1="0" x2="111.86754076315347" y2="-5" style=""></line><line x1="138.13245923684653" y1="0" x2="138.13245923684653" y2="-5" style=""></line><line x1="164.3973777105396" y1="0" x2="164.3973777105396" y2="-5" style=""></line><line x1="190.66229618423264" y1="0" x2="190.66229618423264" y2="-5" style=""></line><line x1="216.9272146579257" y1="0" x2="216.9272146579257" y2="-5" style=""></line><line x1="243.1921331316188" y1="0" x2="243.1921331316188" y2="-5" style=""></line></g><g><g transform="translate(6.807866868381236,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(33.07278534207429,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(59.337703815767355,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(85.60262228946041,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(111.86754076315347,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(138.13245923684653,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">5</text></g><g transform="translate(164.3973777105396,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">6</text></g><g transform="translate(190.66229618423264,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">7</text></g><g transform="translate(216.9272146579257,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">8</text></g><g transform="translate(243.1921331316188,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">9</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g><g class="toyplot-coordinates-Axis" id="t4f9e94b056cf4008a49f149f91d771aa" transform="translate(50.0,300.0)rotate(-90.0)translate(0,-15.0)"><line x1="22.8226540715871" y1="0" x2="245.1096853126956" y2="0" style=""></line><g><line x1="22.8226540715871" y1="0" x2="22.8226540715871" y2="5" style=""></line><line x1="78.39441188186422" y1="0" x2="78.39441188186422" y2="5" style=""></line><line x1="133.96616969214134" y1="0" x2="133.96616969214134" y2="5" style=""></line><line x1="189.53792750241846" y1="0" x2="189.53792750241846" y2="5" style=""></line><line x1="245.1096853126956" y1="0" x2="245.1096853126956" y2="5" style=""></line></g><g><g transform="translate(22.8226540715871,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(78.39441188186422,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(133.96616969214134,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(189.53792750241846,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(245.1096853126956,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t831e999f1e99474a91a61437d3745d72";
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
        })(modules["toyplot.coordinates.Axis"],"t7598b4c7f3cd46f5a12dc50cdea73302",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 9.2592, "min": -0.2591999999999998}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 250.0, "min": 0.0}, "scale": "linear"}]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"t4f9e94b056cf4008a49f149f91d771aa",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 4.088, "min": -0.4106880000000001}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 250.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


#### Circular

In a circular layout the the treenode is positioned at (0, 0) and the farthest tip is positioned away from it by treeheight. Thus, here the depth-axis is 0 to treeheight, while the span axis is from 0 to 360 degrees around the circle. 


```python
# draw a tree with 'depth' axis (x) scale_bar
canvas, axes, mark = tree.draw(ts='o', layout='c', node_mask=False, height=350, width=350);

# overlay a grid 
axes.vlines(range(-4, 5), style={"stroke": "red", "stroke-dasharray": "2,4"})
axes.hlines(range(-4, 5), style={"stroke": "blue", "stroke-dasharray": "2,4"});

# show both span and depth axes
axes.x.show = True
axes.x.ticks.show = True
axes.x.ticks.locator = toyplot.locator.Explicit(locations=range(-4, 5))
axes.y.show = True
axes.y.ticks.show = True
axes.y.ticks.locator = toyplot.locator.Explicit(locations=range(-4, 5))
```


<div class="toyplot" id="tb989acd5ec774a04bb7dbc6146c7bbb9" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="350.0px" height="350.0px" viewBox="0 0 350.0 350.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t60e1aac8f2c045e58a4ce1aeffe64170"><g class="toyplot-coordinates-Cartesian" id="t256481e894744476993107aabcaa04d7"><clipPath id="ta6802ac586bd48d8b10df049a1864127"><rect x="35.0" y="35.0" width="280.0" height="280.0"></rect></clipPath><g clip-path="url(#ta6802ac586bd48d8b10df049a1864127)"><g class="toytree-mark-Toytree" id="t693158ed2eea4e7785a0229efa7c327c"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 184.9 170.0 L 274.5 175.0" id="11,0" style=""></path><path d="M 194.5 148.2 L 255.5 116.5" id="10,1" style=""></path><path d="M 194.5 148.2 L 205.7 80.4" id="10,2" style=""></path><path d="M 142.5 130.3 L 144.3 80.4" id="12,3" style=""></path><path d="M 142.5 130.3 L 94.5 116.5" id="12,4" style=""></path><path d="M 145.4 159.9 L 75.5 175.0" id="13,5" style=""></path><path d="M 162.3 205.6 L 94.5 233.5" id="16,6" style=""></path><path d="M 183.6 229.6 L 144.3 269.6" id="15,7" style=""></path><path d="M 220.5 237.6 L 205.7 269.6" id="14,8" style=""></path><path d="M 220.5 237.6 L 255.5 233.5" id="14,9" style=""></path><path d="M 184.9 170.0 L 194.5 148.2" id="11,10" style=""></path><path d="M 175.0 175.0 L 184.9 170.0" id="18,11" style=""></path><path d="M 145.4 159.9 L 142.5 130.3" id="13,12" style=""></path><path d="M 164.6 178.8 L 145.4 159.9" id="17,13" style=""></path><path d="M 183.6 229.6 L 220.5 237.6" id="15,14" style=""></path><path d="M 162.3 205.6 L 183.6 229.6" id="16,15" style=""></path><path d="M 164.6 178.8 L 162.3 205.6" id="17,16" style=""></path><path d="M 175.0 175.0 L 164.6 178.8" id="18,17" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 274.5 175.0 L 274.5 175.0"></path><path d="M 255.5 116.5 L 255.5 116.5"></path><path d="M 205.7 80.4 L 205.7 80.4"></path><path d="M 144.3 80.4 L 144.3 80.4"></path><path d="M 94.5 116.5 L 94.5 116.5"></path><path d="M 75.5 175.0 L 75.5 175.0"></path><path d="M 94.5 233.5 L 94.5 233.5"></path><path d="M 144.3 269.6 L 144.3 269.6"></path><path d="M 205.7 269.6 L 205.7 269.6"></path><path d="M 255.5 233.5 L 255.5 233.5"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(274.509,175)"><circle r="4.0"></circle></g><g id="Node-1" transform="translate(255.504,116.51)"><circle r="4.0"></circle></g><g id="Node-2" transform="translate(205.75,80.3614)"><circle r="4.0"></circle></g><g id="Node-3" transform="translate(144.25,80.3614)"><circle r="4.0"></circle></g><g id="Node-4" transform="translate(94.4956,116.51)"><circle r="4.0"></circle></g><g id="Node-5" transform="translate(75.4911,175)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(94.4956,233.49)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(144.25,269.639)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(205.75,269.639)"><circle r="4.0"></circle></g><g id="Node-9" transform="translate(255.504,233.49)"><circle r="4.0"></circle></g><g id="Node-10" transform="translate(194.497,148.165)"><circle r="4.0"></circle></g><g id="Node-11" transform="translate(184.851,169.98)"><circle r="4.0"></circle></g><g id="Node-12" transform="translate(142.506,130.275)"><circle r="4.0"></circle></g><g id="Node-13" transform="translate(145.446,159.941)"><circle r="4.0"></circle></g><g id="Node-14" transform="translate(220.492,237.615)"><circle r="4.0"></circle></g><g id="Node-15" transform="translate(183.648,229.602)"><circle r="4.0"></circle></g><g id="Node-16" transform="translate(162.307,205.645)"><circle r="4.0"></circle></g><g id="Node-17" transform="translate(164.627,178.827)"><circle r="4.0"></circle></g><g id="Node-18" transform="translate(175,175)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(274.509,175)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(255.504,116.51)rotate(-36)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(205.75,80.3614)rotate(-72)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(144.25,80.3614)rotate(72)"><text x="-25.668" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(94.4956,116.51)rotate(36)"><text x="-25.668" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(75.4911,175)"><text x="-25.668" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(94.4956,233.49)rotate(-36)"><text x="-25.668" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(144.25,269.639)rotate(-72)"><text x="-25.668" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(205.75,269.639)rotate(-288)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(255.504,233.49)rotate(-324)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g><g class="toyplot-mark-AxisLines" style="stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0" id="tffb1d75d1f8c40258c017cc5b1863244"><g class="toyplot-Series"><line class="toyplot-Datum" x1="75.49107463240385" x2="75.49107463240385" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="100.36830597430288" x2="100.36830597430288" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="125.2455373162019" x2="125.2455373162019" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="150.12276865810094" x2="150.12276865810094" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="174.99999999999997" x2="174.99999999999997" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="199.877231341899" x2="199.877231341899" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="224.75446268379807" x2="224.75446268379807" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="249.6316940256971" x2="249.6316940256971" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="274.5089253675961" x2="274.5089253675961" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line></g></g><g class="toyplot-mark-AxisLines" style="stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0" id="ta2c304fc2fa04427a18dfbfb4b5343f4"><g class="toyplot-Series"><line class="toyplot-Datum" y1="274.50892536759613" y2="274.50892536759613" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="249.63169402569713" y2="249.63169402569713" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="224.75446268379807" y2="224.75446268379807" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="199.87723134189906" y2="199.87723134189906" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="175.00000000000003" y2="175.00000000000003" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="150.122768658101" y2="150.122768658101" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="125.24553731620196" y2="125.24553731620196" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="100.36830597430293" y2="100.36830597430293" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="75.49107463240388" y2="75.49107463240388" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line></g></g></g><g class="toyplot-coordinates-Axis" id="tbfa9000881fe40ff94a556f141f2d4e7" transform="translate(50.0,300.0)translate(0,15.0)"><line x1="21.295165529508605" y1="0" x2="228.7048344704914" y2="0" style=""></line><g><line x1="21.295165529508605" y1="0" x2="21.295165529508605" y2="-5" style=""></line><line x1="47.221374147131456" y1="0" x2="47.221374147131456" y2="-5" style=""></line><line x1="73.1475827647543" y1="0" x2="73.1475827647543" y2="-5" style=""></line><line x1="99.07379138237715" y1="0" x2="99.07379138237715" y2="-5" style=""></line><line x1="125.0" y1="0" x2="125.0" y2="-5" style=""></line><line x1="150.92620861762285" y1="0" x2="150.92620861762285" y2="-5" style=""></line><line x1="176.8524172352457" y1="0" x2="176.8524172352457" y2="-5" style=""></line><line x1="202.77862585286854" y1="0" x2="202.77862585286854" y2="-5" style=""></line><line x1="228.7048344704914" y1="0" x2="228.7048344704914" y2="-5" style=""></line></g><g><g transform="translate(21.295165529508605,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-4</text></g><g transform="translate(47.221374147131456,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-3</text></g><g transform="translate(73.1475827647543,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-2</text></g><g transform="translate(99.07379138237715,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-1</text></g><g transform="translate(125.0,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(150.92620861762285,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(176.8524172352457,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(202.77862585286854,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(228.7048344704914,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g><g class="toyplot-coordinates-Axis" id="tf6d075cc431c4e489fb6e3644a1a77c2" transform="translate(50.0,300.0)rotate(-90.0)translate(0,-15.0)"><line x1="21.295165529508605" y1="0" x2="228.7048344704914" y2="0" style=""></line><g><line x1="21.295165529508605" y1="0" x2="21.295165529508605" y2="5" style=""></line><line x1="47.221374147131456" y1="0" x2="47.221374147131456" y2="5" style=""></line><line x1="73.1475827647543" y1="0" x2="73.1475827647543" y2="5" style=""></line><line x1="99.07379138237715" y1="0" x2="99.07379138237715" y2="5" style=""></line><line x1="125.0" y1="0" x2="125.0" y2="5" style=""></line><line x1="150.92620861762285" y1="0" x2="150.92620861762285" y2="5" style=""></line><line x1="176.8524172352457" y1="0" x2="176.8524172352457" y2="5" style=""></line><line x1="202.77862585286854" y1="0" x2="202.77862585286854" y2="5" style=""></line><line x1="228.7048344704914" y1="0" x2="228.7048344704914" y2="5" style=""></line></g><g><g transform="translate(21.295165529508605,-6)"><text x="-4.445" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-4</text></g><g transform="translate(47.221374147131456,-6)"><text x="-4.445" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-3</text></g><g transform="translate(73.1475827647543,-6)"><text x="-4.445" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-2</text></g><g transform="translate(99.07379138237715,-6)"><text x="-4.445" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-1</text></g><g transform="translate(125.0,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(150.92620861762285,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(176.8524172352457,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(202.77862585286854,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(228.7048344704914,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t60e1aac8f2c045e58a4ce1aeffe64170";
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
        })(modules["toyplot.coordinates.Axis"],"tbfa9000881fe40ff94a556f141f2d4e7",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 4.821376000000001, "min": -4.821376000000001}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 250.0, "min": 0.0}, "scale": "linear"}]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"tf6d075cc431c4e489fb6e3644a1a77c2",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 4.821376000000001, "min": -4.821376000000001}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 250.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


#### Unrooted
The unrooted layout positioning is similar to the circular layout, with the treenode at (0, 0), however the positions of tip nodes is not uniform in this layout, since it results from an algorthmic layout optimization.


```python
# draw a tree with 'depth' axis (x) scale_bar
canvas, axes, mark = tree.draw(ts='o', layout='unr', node_mask=False, height=350, width=350);

# overlay a grid 
axes.vlines(range(-4, 5), style={"stroke": "red", "stroke-dasharray": "2,4"})
axes.hlines(range(-4, 5), style={"stroke": "blue", "stroke-dasharray": "2,4"});

# show both span and depth axes w/ explicit ticks
axes.x.show = True
axes.x.ticks.show = True
axes.x.ticks.locator = toyplot.locator.Explicit(locations=range(-4, 5))
axes.y.show = True
axes.y.ticks.show = True
axes.y.ticks.locator = toyplot.locator.Explicit(locations=range(-4, 5))
```


<div class="toyplot" id="t143e1b774a3946d09d5b991f80562e48" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="350.0px" height="350.0px" viewBox="0 0 350.0 350.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t73002683f4d849e690e1f8a9a196a240"><g class="toyplot-coordinates-Cartesian" id="t6f23a5d55a074413a06874ae96a2c5a3"><clipPath id="tdf55a0425f0f429c9ea67a151e433f88"><rect x="35.0" y="35.0" width="280.0" height="280.0"></rect></clipPath><g clip-path="url(#tdf55a0425f0f429c9ea67a151e433f88)"><g class="toytree-mark-Toytree" id="te4810705ee984dc1bb937c5a355e311c"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 180.7 169.2 L 273.9 186.4" id="11,0" style=""></path><path d="M 191.2 147.7 L 249.5 106.5" id="10,1" style=""></path><path d="M 191.2 147.7 L 185.6 75.9" id="10,2" style=""></path><path d="M 127.8 154.0 L 112.1 108.7" id="12,3" style=""></path><path d="M 127.8 154.0 L 81.9 142.1" id="12,4" style=""></path><path d="M 142.1 173.2 L 76.4 200.6" id="13,5" style=""></path><path d="M 166.8 208.5 L 114.7 257.4" id="16,6" style=""></path><path d="M 180.3 228.2 L 167.4 274.4" id="15,7" style=""></path><path d="M 200.2 241.1 L 205.2 264.6" id="14,8" style=""></path><path d="M 200.2 241.1 L 222.3 249.7" id="14,9" style=""></path><path d="M 180.7 169.2 L 191.2 147.7" id="11,10" style=""></path><path d="M 171.4 176.6 L 180.7 169.2" id="18,11" style=""></path><path d="M 142.1 173.2 L 127.8 154.0" id="13,12" style=""></path><path d="M 162.8 184.8 L 142.1 173.2" id="17,13" style=""></path><path d="M 180.3 228.2 L 200.2 241.1" id="15,14" style=""></path><path d="M 166.8 208.5 L 180.3 228.2" id="16,15" style=""></path><path d="M 162.8 184.8 L 166.8 208.5" id="17,16" style=""></path><path d="M 171.4 176.6 L 162.8 184.8" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(273.907,186.36)"><circle r="4.0"></circle></g><g id="Node-1" transform="translate(249.457,106.519)"><circle r="4.0"></circle></g><g id="Node-2" transform="translate(185.628,75.8928)"><circle r="4.0"></circle></g><g id="Node-3" transform="translate(112.11,108.734)"><circle r="4.0"></circle></g><g id="Node-4" transform="translate(81.9357,142.06)"><circle r="4.0"></circle></g><g id="Node-5" transform="translate(76.399,200.591)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(114.688,257.397)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(167.394,274.386)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(205.157,264.601)"><circle r="4.0"></circle></g><g id="Node-9" transform="translate(222.329,249.67)"><circle r="4.0"></circle></g><g id="Node-10" transform="translate(191.181,147.675)"><circle r="4.0"></circle></g><g id="Node-11" transform="translate(180.734,169.213)"><circle r="4.0"></circle></g><g id="Node-12" transform="translate(127.789,154.028)"><circle r="4.0"></circle></g><g id="Node-13" transform="translate(142.069,173.17)"><circle r="4.0"></circle></g><g id="Node-14" transform="translate(200.204,241.131)"><circle r="4.0"></circle></g><g id="Node-15" transform="translate(180.265,228.192)"><circle r="4.0"></circle></g><g id="Node-16" transform="translate(166.786,208.461)"><circle r="4.0"></circle></g><g id="Node-17" transform="translate(162.775,184.807)"><circle r="4.0"></circle></g><g id="Node-18" transform="translate(171.379,176.566)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(273.907,186.36)rotate(5.38324)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(249.457,106.519)rotate(-41.982)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(185.628,75.8928)rotate(-86.9565)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(112.11,108.734)rotate(64.7623)"><text x="-25.668" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(81.9357,142.06)rotate(27.0353)"><text x="-25.668" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(76.399,200.591)rotate(169.782)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(114.688,257.397)rotate(123.885)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(167.394,274.386)rotate(89.4645)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(205.157,264.601)rotate(55.2742)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(222.329,249.67)rotate(26.7327)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g><g class="toyplot-mark-AxisLines" style="stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0" id="t4f76a591eeaf472a86e3ccfd14e66c9e"><g class="toyplot-Series"><line class="toyplot-Datum" x1="64.84575461568362" x2="64.84575461568362" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="91.47901844869754" x2="91.47901844869754" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="118.11228228171149" x2="118.11228228171149" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="144.7455461147254" x2="144.7455461147254" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="171.37880994773934" x2="171.37880994773934" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="198.01207378075327" x2="198.01207378075327" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="224.6453376137672" x2="224.6453376137672" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="251.27860144678115" x2="251.27860144678115" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="277.91186527979505" x2="277.91186527979505" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line></g></g><g class="toyplot-mark-AxisLines" style="stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0" id="t52a933d3bf3745579a6c5f8d0c1a03b9"><g class="toyplot-Series"><line class="toyplot-Datum" y1="284.5699427739651" y2="284.5699427739651" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="257.56883454841596" y2="257.56883454841596" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="230.5677263228668" y2="230.5677263228668" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="203.56661809731764" y2="203.56661809731764" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="176.56550987176846" y2="176.56550987176846" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="149.5644016462193" y2="149.5644016462193" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="122.56329342067015" y2="122.56329342067015" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="95.56218519512095" y2="95.56218519512095" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="68.5610769695718" y2="68.5610769695718" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line></g></g></g><g class="toyplot-coordinates-Axis" id="td98eb0511136446d9ffe315fe943ec2f" transform="translate(50.0,300.0)translate(0,15.0)"><line x1="23.318849801415087" y1="0" x2="226.9516544729486" y2="0" style=""></line><g><line x1="11.407336176916633" y1="0" x2="11.407336176916633" y2="-5" style=""></line><line x1="38.86647864459126" y1="0" x2="38.86647864459126" y2="-5" style=""></line><line x1="66.32562111226589" y1="0" x2="66.32562111226589" y2="-5" style=""></line><line x1="93.78476357994052" y1="0" x2="93.78476357994052" y2="-5" style=""></line><line x1="121.24390604761514" y1="0" x2="121.24390604761514" y2="-5" style=""></line><line x1="148.7030485152898" y1="0" x2="148.7030485152898" y2="-5" style=""></line><line x1="176.1621909829644" y1="0" x2="176.1621909829644" y2="-5" style=""></line><line x1="203.62133345063904" y1="0" x2="203.62133345063904" y2="-5" style=""></line><line x1="231.08047591831365" y1="0" x2="231.08047591831365" y2="-5" style=""></line></g><g><g transform="translate(11.407336176916633,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-4</text></g><g transform="translate(38.86647864459126,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-3</text></g><g transform="translate(66.32562111226589,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-2</text></g><g transform="translate(93.78476357994052,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-1</text></g><g transform="translate(121.24390604761514,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(148.7030485152898,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(176.1621909829644,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(203.62133345063904,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(231.08047591831365,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g><g class="toyplot-coordinates-Axis" id="t03e1e6dd91de4dc89dc55eb1c5fd6a77" transform="translate(50.0,300.0)rotate(-90.0)translate(0,-15.0)"><line x1="22.856446733957174" y1="0" x2="226.8949516333332" y2="0" style=""></line><g><line x1="12.387756525754584" y1="0" x2="12.387756525754584" y2="5" style=""></line><line x1="40.143227889104" y1="0" x2="40.143227889104" y2="5" style=""></line><line x1="67.89869925245341" y1="0" x2="67.89869925245341" y2="5" style=""></line><line x1="95.65417061580283" y1="0" x2="95.65417061580283" y2="5" style=""></line><line x1="123.40964197915223" y1="0" x2="123.40964197915223" y2="5" style=""></line><line x1="151.16511334250166" y1="0" x2="151.16511334250166" y2="5" style=""></line><line x1="178.92058470585107" y1="0" x2="178.92058470585107" y2="5" style=""></line><line x1="206.67605606920048" y1="0" x2="206.67605606920048" y2="5" style=""></line><line x1="234.4315274325499" y1="0" x2="234.4315274325499" y2="5" style=""></line></g><g><g transform="translate(12.387756525754584,-6)"><text x="-4.445" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-4</text></g><g transform="translate(40.143227889104,-6)"><text x="-4.445" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-3</text></g><g transform="translate(67.89869925245341,-6)"><text x="-4.445" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-2</text></g><g transform="translate(95.65417061580283,-6)"><text x="-4.445" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-1</text></g><g transform="translate(123.40964197915223,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(151.16511334250166,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(178.92058470585107,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(206.67605606920048,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(234.4315274325499,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t73002683f4d849e690e1f8a9a196a240";
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
        })(modules["toyplot.coordinates.Axis"],"td98eb0511136446d9ffe315fe943ec2f",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 4.689006370244764, "min": -4.415429439952305}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 250.0, "min": 0.0}, "scale": "linear"}]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"t03e1e6dd91de4dc89dc55eb1c5fd6a77",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 4.560915444873618, "min": -4.446317641793408}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 250.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


## Baseline shift

The default node position (0, 0) in each layout is actually set by (``xbaseline``, ``ybaseline``).  To shift the tree in coordinate space these two arguments to ``draw`` can be set to any float value.

This example shows a tree in the default position (0, 0), and adds a second tree drawing shifted to (10, 10). 


```python
# draw a tree with with default position (0, 0)
canvas, axes, mark = tree.draw(
    ts='o', layout='r', node_mask=False, height=350, width=350,
);

# add another tree with baseline shift to (10, 10)
canvas, axes, mark = tree.draw(
    axes=axes, ybaseline=10, xbaseline=10,
    ts='o', layout='r', node_mask=False, height=350, width=350,
);

# overlay a grid 
axes.hlines(range(0, tree.ntips + 10), style={"stroke": "red", "stroke-dasharray": "2,4"})
axes.vlines(range(-4, 11), style={"stroke": "blue", "stroke-dasharray": "2,4"});

# show depth axis from -4 - 10
axes.x.show = True
axes.x.ticks.show = True
axes.x.ticks.locator = toyplot.locator.Explicit(locations=range(-4, 11, 2))

# show span axis from 0 - 10 + ntips
axes.y.show = True
axes.y.ticks.show = True
axes.y.ticks.locator = toyplot.locator.Explicit(locations=range(0, tree.ntips + 10, 2))
```


<div class="toyplot" id="t65f7e68793e44152939f369a2b07a343" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="350.0px" height="350.0px" viewBox="0 0 350.0 350.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t5208a387c43f4bd1a06f888065c7d080"><g class="toyplot-coordinates-Cartesian" id="t9c915d12321445e7bce6a16eef9d4210"><clipPath id="tc6242a64315c4f348675134d89372635"><rect x="35.0" y="35.0" width="280.0" height="280.0"></rect></clipPath><g clip-path="url(#tc6242a64315c4f348675134d89372635)"><g class="toytree-mark-Toytree" id="t0c3e2f7b913847439c38463a4e88561c"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 62.4 283.5 L 118.1 292.8" id="11,0" style=""></path><path d="M 76.3 274.2 L 118.1 280.4" id="10,1" style=""></path><path d="M 76.3 274.2 L 118.1 268.0" id="10,2" style=""></path><path d="M 90.2 249.4 L 118.1 255.6" id="12,3" style=""></path><path d="M 90.2 249.4 L 118.1 243.2" id="12,4" style=""></path><path d="M 76.3 240.1 L 118.1 230.8" id="13,5" style=""></path><path d="M 76.3 207.6 L 118.1 218.4" id="16,6" style=""></path><path d="M 90.2 196.7 L 118.1 206.0" id="15,7" style=""></path><path d="M 104.1 187.4 L 118.1 193.6" id="14,8" style=""></path><path d="M 104.1 187.4 L 118.1 181.2" id="14,9" style=""></path><path d="M 62.4 283.5 L 76.3 274.2" id="11,10" style=""></path><path d="M 55.4 253.7 L 62.4 283.5" id="18,11" style=""></path><path d="M 76.3 240.1 L 90.2 249.4" id="13,12" style=""></path><path d="M 62.4 223.8 L 76.3 240.1" id="17,13" style=""></path><path d="M 90.2 196.7 L 104.1 187.4" id="15,14" style=""></path><path d="M 76.3 207.6 L 90.2 196.7" id="16,15" style=""></path><path d="M 62.4 223.8 L 76.3 207.6" id="17,16" style=""></path><path d="M 55.4 253.7 L 62.4 223.8" id="18,17" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 118.1 292.8 L 118.1 292.8"></path><path d="M 118.1 280.4 L 118.1 280.4"></path><path d="M 118.1 268.0 L 118.1 268.0"></path><path d="M 118.1 255.6 L 118.1 255.6"></path><path d="M 118.1 243.2 L 118.1 243.2"></path><path d="M 118.1 230.8 L 118.1 230.8"></path><path d="M 118.1 218.4 L 118.1 218.4"></path><path d="M 118.1 206.0 L 118.1 206.0"></path><path d="M 118.1 193.6 L 118.1 193.6"></path><path d="M 118.1 181.2 L 118.1 181.2"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(118.07,292.823)"><circle r="4.0"></circle></g><g id="Node-1" transform="translate(118.07,280.42)"><circle r="4.0"></circle></g><g id="Node-2" transform="translate(118.07,268.018)"><circle r="4.0"></circle></g><g id="Node-3" transform="translate(118.07,255.615)"><circle r="4.0"></circle></g><g id="Node-4" transform="translate(118.07,243.213)"><circle r="4.0"></circle></g><g id="Node-5" transform="translate(118.07,230.811)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(118.07,218.408)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(118.07,206.006)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(118.07,193.604)"><circle r="4.0"></circle></g><g id="Node-9" transform="translate(118.07,181.201)"><circle r="4.0"></circle></g><g id="Node-10" transform="translate(76.3066,274.219)"><circle r="4.0"></circle></g><g id="Node-11" transform="translate(62.3856,283.521)"><circle r="4.0"></circle></g><g id="Node-12" transform="translate(90.2277,249.414)"><circle r="4.0"></circle></g><g id="Node-13" transform="translate(76.3066,240.112)"><circle r="4.0"></circle></g><g id="Node-14" transform="translate(104.149,187.402)"><circle r="4.0"></circle></g><g id="Node-15" transform="translate(90.2277,196.704)"><circle r="4.0"></circle></g><g id="Node-16" transform="translate(76.3066,207.556)"><circle r="4.0"></circle></g><g id="Node-17" transform="translate(62.3856,223.834)"><circle r="4.0"></circle></g><g id="Node-18" transform="translate(55.425,253.678)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(118.07,292.823)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(118.07,280.42)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(118.07,268.018)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(118.07,255.615)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(118.07,243.213)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(118.07,230.811)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(118.07,218.408)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(118.07,206.006)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(118.07,193.604)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(118.07,181.201)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g><g class="toytree-mark-Toytree" id="t5491677f845a4aa4af180c929f1e3447"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 219.0 159.5 L 274.7 168.8" id="11,0" style=""></path><path d="M 232.9 150.2 L 274.7 156.4" id="10,1" style=""></path><path d="M 232.9 150.2 L 274.7 144.0" id="10,2" style=""></path><path d="M 246.8 125.4 L 274.7 131.6" id="12,3" style=""></path><path d="M 246.8 125.4 L 274.7 119.2" id="12,4" style=""></path><path d="M 232.9 116.1 L 274.7 106.8" id="13,5" style=""></path><path d="M 232.9 83.5 L 274.7 94.4" id="16,6" style=""></path><path d="M 246.8 72.7 L 274.7 82.0" id="15,7" style=""></path><path d="M 260.8 63.4 L 274.7 69.6" id="14,8" style=""></path><path d="M 260.8 63.4 L 274.7 57.2" id="14,9" style=""></path><path d="M 219.0 159.5 L 232.9 150.2" id="11,10" style=""></path><path d="M 212.0 129.7 L 219.0 159.5" id="18,11" style=""></path><path d="M 232.9 116.1 L 246.8 125.4" id="13,12" style=""></path><path d="M 219.0 99.8 L 232.9 116.1" id="17,13" style=""></path><path d="M 246.8 72.7 L 260.8 63.4" id="15,14" style=""></path><path d="M 232.9 83.5 L 246.8 72.7" id="16,15" style=""></path><path d="M 219.0 99.8 L 232.9 83.5" id="17,16" style=""></path><path d="M 212.0 129.7 L 219.0 99.8" id="18,17" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 274.7 168.8 L 274.7 168.8"></path><path d="M 274.7 156.4 L 274.7 156.4"></path><path d="M 274.7 144.0 L 274.7 144.0"></path><path d="M 274.7 131.6 L 274.7 131.6"></path><path d="M 274.7 119.2 L 274.7 119.2"></path><path d="M 274.7 106.8 L 274.7 106.8"></path><path d="M 274.7 94.4 L 274.7 94.4"></path><path d="M 274.7 82.0 L 274.7 82.0"></path><path d="M 274.7 69.6 L 274.7 69.6"></path><path d="M 274.7 57.2 L 274.7 57.2"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(274.682,168.799)"><circle r="4.0"></circle></g><g id="Node-1" transform="translate(274.682,156.396)"><circle r="4.0"></circle></g><g id="Node-2" transform="translate(274.682,143.994)"><circle r="4.0"></circle></g><g id="Node-3" transform="translate(274.682,131.592)"><circle r="4.0"></circle></g><g id="Node-4" transform="translate(274.682,119.189)"><circle r="4.0"></circle></g><g id="Node-5" transform="translate(274.682,106.787)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(274.682,94.3846)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(274.682,81.9822)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(274.682,69.5799)"><circle r="4.0"></circle></g><g id="Node-9" transform="translate(274.682,57.1775)"><circle r="4.0"></circle></g><g id="Node-10" transform="translate(232.919,150.195)"><circle r="4.0"></circle></g><g id="Node-11" transform="translate(218.998,159.497)"><circle r="4.0"></circle></g><g id="Node-12" transform="translate(246.84,125.391)"><circle r="4.0"></circle></g><g id="Node-13" transform="translate(232.919,116.089)"><circle r="4.0"></circle></g><g id="Node-14" transform="translate(260.761,63.3787)"><circle r="4.0"></circle></g><g id="Node-15" transform="translate(246.84,72.6804)"><circle r="4.0"></circle></g><g id="Node-16" transform="translate(232.919,83.5325)"><circle r="4.0"></circle></g><g id="Node-17" transform="translate(218.998,99.8106)"><circle r="4.0"></circle></g><g id="Node-18" transform="translate(212.037,129.654)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(274.682,168.799)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(274.682,156.396)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(274.682,143.994)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(274.682,131.592)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(274.682,119.189)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(274.682,106.787)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(274.682,94.3846)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(274.682,81.9822)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(274.682,69.5799)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(274.682,57.1775)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g><g class="toyplot-mark-AxisLines" style="stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0" id="t4f71f9372c89482098e1dc74c66f47dc"><g class="toyplot-Series"><line class="toyplot-Datum" y1="292.822516233492" y2="292.822516233492" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="280.4201461036508" y2="280.4201461036508" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="268.01777597380953" y2="268.01777597380953" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="255.61540584396823" y2="255.61540584396823" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="243.21303571412696" y2="243.21303571412696" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="230.8106655842857" y2="230.8106655842857" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="218.40829545444439" y2="218.40829545444439" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="206.00592532460317" y2="206.00592532460317" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="193.60355519476187" y2="193.60355519476187" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="181.20118506492062" y2="181.20118506492062" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="168.79881493507935" y2="168.79881493507935" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="156.39644480523808" y2="156.39644480523808" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="143.9940746753968" y2="143.9940746753968" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="131.59170454555553" y2="131.59170454555553" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="119.18933441571428" y2="119.18933441571428" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="106.78696428587301" y2="106.78696428587301" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="94.38459415603174" y2="94.38459415603174" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="81.98222402619047" y2="81.98222402619047" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="69.57985389634919" y2="69.57985389634919" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" y1="57.17748376650795" y2="57.17748376650795" x1="50.0" x2="300.0" style="opacity:1.0;stroke:rgb(100%,0%,0%);stroke-dasharray:2,4;stroke-opacity:1.0"></line></g></g><g class="toyplot-mark-AxisLines" style="stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0" id="t3cd383291b27454bb7967d1a42ccc1a7"><g class="toyplot-Series"><line class="toyplot-Datum" x1="55.42502547006841" x2="55.42502547006841" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="71.08623074472955" x2="71.08623074472955" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="86.74743601939069" x2="86.74743601939069" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="102.40864129405182" x2="102.40864129405182" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="118.06984656871296" x2="118.06984656871296" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="133.7310518433741" x2="133.7310518433741" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="149.39225711803522" x2="149.39225711803522" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="165.05346239269636" x2="165.05346239269636" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="180.7146676673575" x2="180.7146676673575" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="196.37587294201865" x2="196.37587294201865" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="212.0370782166798" x2="212.0370782166798" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="227.69828349134093" x2="227.69828349134093" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="243.35948876600207" x2="243.35948876600207" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="259.0206940406632" x2="259.0206940406632" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line><line class="toyplot-Datum" x1="274.68189931532436" x2="274.68189931532436" y1="50.0" y2="300.0" style="opacity:1.0;stroke:rgb(0%,0%,100%);stroke-dasharray:2,4;stroke-opacity:1.0"></line></g></g></g><g class="toyplot-coordinates-Axis" id="td72c615f4be246cd9aca2808bdd58421" transform="translate(50.0,300.0)translate(0,15.0)"><line x1="4.890314687304384" y1="0" x2="227.17734592841288" y2="0" style=""></line><g><line x1="4.890314687304384" y1="0" x2="4.890314687304384" y2="-5" style=""></line><line x1="36.6456048646056" y1="0" x2="36.6456048646056" y2="-5" style=""></line><line x1="68.40089504190682" y1="0" x2="68.40089504190682" y2="-5" style=""></line><line x1="100.15618521920803" y1="0" x2="100.15618521920803" y2="-5" style=""></line><line x1="131.91147539650925" y1="0" x2="131.91147539650925" y2="-5" style=""></line><line x1="163.66676557381047" y1="0" x2="163.66676557381047" y2="-5" style=""></line><line x1="195.42205575111169" y1="0" x2="195.42205575111169" y2="-5" style=""></line><line x1="227.17734592841288" y1="0" x2="227.17734592841288" y2="-5" style=""></line></g><g><g transform="translate(4.890314687304384,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-4</text></g><g transform="translate(36.6456048646056,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-2</text></g><g transform="translate(68.40089504190682,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(100.15618521920803,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(131.91147539650925,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(163.66676557381047,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">6</text></g><g transform="translate(195.42205575111169,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">8</text></g><g transform="translate(227.17734592841288,6)"><text x="-5.56" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">10</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g><g class="toyplot-coordinates-Axis" id="t8fbdc77591f34d54aace41d3c85eed03" transform="translate(50.0,300.0)rotate(-90.0)translate(0,-15.0)"><line x1="6.80786686838123" y1="0" x2="243.19213313161876" y2="0" style=""></line><g><line x1="6.80786686838123" y1="0" x2="6.80786686838123" y2="5" style=""></line><line x1="31.69042121187992" y1="0" x2="31.69042121187992" y2="5" style=""></line><line x1="56.572975555378605" y1="0" x2="56.572975555378605" y2="5" style=""></line><line x1="81.45552989887729" y1="0" x2="81.45552989887729" y2="5" style=""></line><line x1="106.33808424237597" y1="0" x2="106.33808424237597" y2="5" style=""></line><line x1="131.22063858587467" y1="0" x2="131.22063858587467" y2="5" style=""></line><line x1="156.10319292937334" y1="0" x2="156.10319292937334" y2="5" style=""></line><line x1="180.98574727287203" y1="0" x2="180.98574727287203" y2="5" style=""></line><line x1="205.86830161637073" y1="0" x2="205.86830161637073" y2="5" style=""></line><line x1="230.7508559598694" y1="0" x2="230.7508559598694" y2="5" style=""></line></g><g><g transform="translate(6.80786686838123,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(31.69042121187992,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(56.572975555378605,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(81.45552989887729,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">6</text></g><g transform="translate(106.33808424237597,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">8</text></g><g transform="translate(131.22063858587467,-6)"><text x="-5.56" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">10</text></g><g transform="translate(156.10319292937334,-6)"><text x="-5.56" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">12</text></g><g transform="translate(180.98574727287203,-6)"><text x="-5.56" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">14</text></g><g transform="translate(205.86830161637073,-6)"><text x="-5.56" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">16</text></g><g transform="translate(230.7508559598694,-6)"><text x="-5.56" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">18</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t5208a387c43f4bd1a06f888065c7d080";
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
        })(modules["toyplot.coordinates.Axis"],"td72c615f4be246cd9aca2808bdd58421",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 11.437408000000001, "min": -4.308}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 250.0, "min": 0.0}, "scale": "linear"}]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"t8fbdc77591f34d54aace41d3c85eed03",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 19.5472, "min": -0.5471999999999991}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 250.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


## draw: ``scale_bar``
The ``scale_bar=True`` arg to ``draw()`` styles the tree depth axis and automatically chooses nicely spaced ticks from the tree domain. 



```python
tree.draw(scale_bar=True);
```


<div class="toyplot" id="taa688eb316ba4342a97e240fc8273a54" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tc00b9783bc5d4087bb28e9c520426730"><g class="toyplot-coordinates-Cartesian" id="t727e125ae75240deb2f979e040f8756a"><clipPath id="tc2bcbea7aede441f89d5aafa7c093398"><rect x="50.0" y="65.04476420858973" width="200.0" height="175.0"></rect></clipPath><g clip-path="url(#tc2bcbea7aede441f89d5aafa7c093398)"></g><g class="toyplot-coordinates-Axis" id="t4abe1139ee4249c79c7613858b002848" transform="translate(50.0,240.04476420858973)"><line x1="0.9845545534228147" y1="0" x2="174.72845372274378" y2="0" style=""></line><g><line x1="0.9845545534228147" y1="0" x2="0.9845545534228147" y2="-5.0" style=""></line><line x1="44.42052934575306" y1="0" x2="44.42052934575306" y2="-5.0" style=""></line><line x1="87.8565041380833" y1="0" x2="87.8565041380833" y2="-5.0" style=""></line><line x1="131.29247893041352" y1="0" x2="131.29247893041352" y2="-5.0" style=""></line><line x1="174.72845372274378" y1="0" x2="174.72845372274378" y2="-5.0" style=""></line></g><g><g transform="translate(0.9845545534228147,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(44.42052934575306,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(87.8565041380833,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(131.29247893041352,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(174.72845372274378,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="taec023e1359542d2a47e9ed1fdedc8fe"><clipPath id="te847ff639f374beb8f80e37339a0b8ae"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#te847ff639f374beb8f80e37339a0b8ae)"><g class="toytree-mark-Toytree" id="t69f8d64ac04e479ab0f2e574e7c5780f"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 70.3 204.5 L 70.3 217.8 L 224.7 217.8" id="11,0" style=""></path><path d="M 108.9 191.1 L 108.9 200.0 L 224.7 200.0" id="10,1" style=""></path><path d="M 108.9 191.1 L 108.9 182.1 L 224.7 182.1" id="10,2" style=""></path><path d="M 147.5 155.4 L 147.5 164.3 L 224.7 164.3" id="12,3" style=""></path><path d="M 147.5 155.4 L 147.5 146.4 L 224.7 146.4" id="12,4" style=""></path><path d="M 108.9 142.0 L 108.9 128.6 L 224.7 128.6" id="13,5" style=""></path><path d="M 108.9 95.1 L 108.9 110.7 L 224.7 110.7" id="16,6" style=""></path><path d="M 147.5 79.5 L 147.5 92.9 L 224.7 92.9" id="15,7" style=""></path><path d="M 186.1 66.1 L 186.1 75.0 L 224.7 75.0" id="14,8" style=""></path><path d="M 186.1 66.1 L 186.1 57.2 L 224.7 57.2" id="14,9" style=""></path><path d="M 70.3 204.5 L 70.3 191.1 L 108.9 191.1" id="11,10" style=""></path><path d="M 51.0 161.5 L 51.0 204.5 L 70.3 204.5" id="18,11" style=""></path><path d="M 108.9 142.0 L 108.9 155.4 L 147.5 155.4" id="13,12" style=""></path><path d="M 70.3 118.5 L 70.3 142.0 L 108.9 142.0" id="17,13" style=""></path><path d="M 147.5 79.5 L 147.5 66.1 L 186.1 66.1" id="15,14" style=""></path><path d="M 108.9 95.1 L 108.9 79.5 L 147.5 79.5" id="16,15" style=""></path><path d="M 70.3 118.5 L 70.3 95.1 L 108.9 95.1" id="17,16" style=""></path><path d="M 51.0 161.5 L 51.0 118.5 L 70.3 118.5" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.728,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.728,199.99)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.728,182.136)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.728,164.282)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.728,146.427)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.728,128.573)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.728,110.718)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.728,92.864)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.728,75.0096)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(224.728,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "tc00b9783bc5d4087bb28e9c520426730";
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
        })(modules["toyplot.coordinates.Axis"],"t4abe1139ee4249c79c7613858b002848",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.5818114224000006, "min": -4.0226668000000005}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


## anno: ``add_axes_scale_bar_to_tree``
Use ``tree.annotate.add_axes_scale_bar_to_tree()`` when you want more control over the tree depth axis. Ticks are chosen automatically from the tree domain unless you pass ``tick_locations``.


```python
canvas, axes, mark = tree.draw()

# apply custom styling to the tree scale bar
tree.annotate.add_axes_scale_bar_to_tree(
    axes=axes,                                                              # cartesian with a ToyTreeMark attached
    padding=15,                                                             # set spacing between tree and spine
    spine_style={'stroke-width': 2, 'stroke-linecap': 'round'},             # set spine style
    ticks_style={'stroke-width': 2}, ticks_near=7, ticks_far=0,             # set ticks style and size
    tick_labels_style={"font-size": 12}, tick_labels_offset=12,             # set tick labels style and offset
    label="Time (Mya)", label_style={"font-size": 16}, label_offset=-35,    # set axis label and style
    expand_margin=(0, 0, 0, 30),                                            # expand bottom margin to make room for larger label
);
```


<div class="toyplot" id="t65e9e116d24c4541b7d4dbe153592e12" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t4f4424bd0b834617a457c741537ef6ef"><g class="toyplot-coordinates-Cartesian" id="t6c64dc0efe22498eba8e882c01cd40a1"><clipPath id="tdf031406b29149ff94298957037d5b78"><rect x="50.0" y="65.0640209670863" width="200.0" height="145.0"></rect></clipPath><g clip-path="url(#tdf031406b29149ff94298957037d5b78)"></g><g class="toyplot-coordinates-Axis" id="tc8eb4f8cc73e4560aebee8a7d05b7f35" transform="translate(50.0,210.0640209670863)"><line x1="22.22222222222222" y1="0" x2="111.11111111111111" y2="0" style="stroke-linecap:round;stroke-width:2"></line><g><line x1="0.0" y1="7.0" x2="0.0" y2="0" style="stroke-width:2"></line><line x1="111.11111111111111" y1="7.0" x2="111.11111111111111" y2="0" style="stroke-width:2"></line><line x1="133.33333333333331" y1="7.0" x2="133.33333333333331" y2="0" style="stroke-width:2"></line><line x1="155.55555555555557" y1="7.0" x2="155.55555555555557" y2="0" style="stroke-width:2"></line><line x1="177.77777777777777" y1="7.0" x2="177.77777777777777" y2="0" style="stroke-width:2"></line><line x1="200.0" y1="7.0" x2="200.0" y2="0" style="stroke-width:2"></line></g><g><g transform="translate(0.0,12.0)"><text x="-3.3360000000000003" y="10.265999999999998" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">5</text></g><g transform="translate(111.11111111111111,12.0)"><text x="-3.3360000000000003" y="10.265999999999998" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(133.33333333333331,12.0)"><text x="-3.3360000000000003" y="10.265999999999998" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(155.55555555555557,12.0)"><text x="-3.3360000000000003" y="10.265999999999998" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(177.77777777777777,12.0)"><text x="-3.3360000000000003" y="10.265999999999998" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(200.0,12.0)"><text x="-3.3360000000000003" y="10.265999999999998" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g></g><g transform="translate(66.66666666666666,35.0)"><text x="-41.784" y="13.687999999999999" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:16.0px;font-weight:bold;stroke:none;vertical-align:baseline;white-space:pre">Time (Mya)</text></g></g></g><g class="toyplot-coordinates-Cartesian" id="tbd8f99efafc2424bb839c0e06af80ff0"><clipPath id="t35ac49c0789343cebc70ba455c53ed1f"><rect x="35.0" y="35.0" width="230.0" height="175.0"></rect></clipPath><g clip-path="url(#t35ac49c0789343cebc70ba455c53ed1f)"><g class="toytree-mark-Toytree" id="t81023847a36f459db9e0a148913d9b87"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 70.3 177.0 L 70.3 187.9 L 224.7 187.9" id="11,0" style=""></path><path d="M 108.9 166.1 L 108.9 173.3 L 224.7 173.3" id="10,1" style=""></path><path d="M 108.9 166.1 L 108.9 158.8 L 224.7 158.8" id="10,2" style=""></path><path d="M 147.5 137.0 L 147.5 144.3 L 224.7 144.3" id="12,3" style=""></path><path d="M 147.5 137.0 L 147.5 129.8 L 224.7 129.8" id="12,4" style=""></path><path d="M 108.9 126.1 L 108.9 115.2 L 224.7 115.2" id="13,5" style=""></path><path d="M 108.9 88.0 L 108.9 100.7 L 224.7 100.7" id="16,6" style=""></path><path d="M 147.5 75.3 L 147.5 86.2 L 224.7 86.2" id="15,7" style=""></path><path d="M 186.1 64.4 L 186.1 71.7 L 224.7 71.7" id="14,8" style=""></path><path d="M 186.1 64.4 L 186.1 57.1 L 224.7 57.1" id="14,9" style=""></path><path d="M 70.3 177.0 L 70.3 166.1 L 108.9 166.1" id="11,10" style=""></path><path d="M 51.0 142.0 L 51.0 177.0 L 70.3 177.0" id="18,11" style=""></path><path d="M 108.9 126.1 L 108.9 137.0 L 147.5 137.0" id="13,12" style=""></path><path d="M 70.3 107.1 L 70.3 126.1 L 108.9 126.1" id="17,13" style=""></path><path d="M 147.5 75.3 L 147.5 64.4 L 186.1 64.4" id="15,14" style=""></path><path d="M 108.9 88.0 L 108.9 75.3 L 147.5 75.3" id="16,15" style=""></path><path d="M 70.3 107.1 L 70.3 88.0 L 108.9 88.0" id="17,16" style=""></path><path d="M 51.0 142.0 L 51.0 107.1 L 70.3 107.1" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.728,187.864)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.728,173.339)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.728,158.813)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.728,144.288)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.728,129.763)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.728,115.237)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.728,100.712)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.728,86.1867)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.728,71.6613)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(224.728,57.136)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t4f4424bd0b834617a457c741537ef6ef";
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
        })(modules["toyplot.coordinates.Axis"],"tc8eb4f8cc73e4560aebee8a7d05b7f35",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 4.0, "min": -5.0}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


## Data vs. Pixel Space

The mapping between data and pixel coordinates can change as more things are added to a Cartesian object that expand its domain. Most `toytree.annotation` methods allow adding Marks on a tree drawing by positioning them relative to the positions of nodes or tips of a plotted tree (i.e., in data space), which can then be further nudged from those positions by a set number of pixel units.


```python
# draw a tree on a canvas defined in pixels
c, a, m = tree.draw(width=300);

# add a scale bar showing data units
m1 = tree.annotate.add_axes_scale_bar_to_tree(a);

# add a node marker by data coordinate
m2 = tree.annotate.add_node_markers(a, 'o', size=10, mask=tree.get_node_mask(14));

# add another node marker by data coordinate, then nudge by pixel units
m3 = tree.annotate.add_node_markers(a, 'o', size=10, mask=tree.get_node_mask(14), xshift=-20, color="orange");
```


<div class="toyplot" id="t0c739032632745039d697b7468d9341d" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t30fabe58a2d34496be806f32f5ff3a17"><g class="toyplot-coordinates-Cartesian" id="t9af8cb73eeec40ebbcbe495eade4be0e"><clipPath id="td0cab0f364564b8381fe43f59bd931ae"><rect x="50.0" y="65.04476420858973" width="200.0" height="175.0"></rect></clipPath><g clip-path="url(#td0cab0f364564b8381fe43f59bd931ae)"></g><g class="toyplot-coordinates-Axis" id="t842df1db85054f9187a0d49c1854ca7d" transform="translate(50.0,240.04476420858973)"><line x1="0.9845545534228147" y1="0" x2="174.72845372274378" y2="0" style=""></line><g><line x1="0.9845545534228147" y1="0" x2="0.9845545534228147" y2="-5.0" style=""></line><line x1="44.42052934575306" y1="0" x2="44.42052934575306" y2="-5.0" style=""></line><line x1="87.8565041380833" y1="0" x2="87.8565041380833" y2="-5.0" style=""></line><line x1="131.29247893041352" y1="0" x2="131.29247893041352" y2="-5.0" style=""></line><line x1="174.72845372274378" y1="0" x2="174.72845372274378" y2="-5.0" style=""></line></g><g><g transform="translate(0.9845545534228147,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(44.42052934575306,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(87.8565041380833,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(131.29247893041352,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(174.72845372274378,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t7b0f7a22d9f2427a9de0aa9327baac81"><clipPath id="tbc4f5ebd6a89448c869aa25c7ec48982"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tbc4f5ebd6a89448c869aa25c7ec48982)"><g class="toytree-mark-Toytree" id="t8186e1f5374d45ddb9c6373bc302a8a7"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 70.3 204.5 L 70.3 217.8 L 224.7 217.8" id="11,0" style=""></path><path d="M 108.9 191.1 L 108.9 200.0 L 224.7 200.0" id="10,1" style=""></path><path d="M 108.9 191.1 L 108.9 182.1 L 224.7 182.1" id="10,2" style=""></path><path d="M 147.5 155.4 L 147.5 164.3 L 224.7 164.3" id="12,3" style=""></path><path d="M 147.5 155.4 L 147.5 146.4 L 224.7 146.4" id="12,4" style=""></path><path d="M 108.9 142.0 L 108.9 128.6 L 224.7 128.6" id="13,5" style=""></path><path d="M 108.9 95.1 L 108.9 110.7 L 224.7 110.7" id="16,6" style=""></path><path d="M 147.5 79.5 L 147.5 92.9 L 224.7 92.9" id="15,7" style=""></path><path d="M 186.1 66.1 L 186.1 75.0 L 224.7 75.0" id="14,8" style=""></path><path d="M 186.1 66.1 L 186.1 57.2 L 224.7 57.2" id="14,9" style=""></path><path d="M 70.3 204.5 L 70.3 191.1 L 108.9 191.1" id="11,10" style=""></path><path d="M 51.0 161.5 L 51.0 204.5 L 70.3 204.5" id="18,11" style=""></path><path d="M 108.9 142.0 L 108.9 155.4 L 147.5 155.4" id="13,12" style=""></path><path d="M 70.3 118.5 L 70.3 142.0 L 108.9 142.0" id="17,13" style=""></path><path d="M 147.5 79.5 L 147.5 66.1 L 186.1 66.1" id="15,14" style=""></path><path d="M 108.9 95.1 L 108.9 79.5 L 147.5 79.5" id="16,15" style=""></path><path d="M 70.3 118.5 L 70.3 95.1 L 108.9 95.1" id="17,16" style=""></path><path d="M 51.0 161.5 L 51.0 118.5 L 70.3 118.5" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.728,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.728,199.99)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.728,182.136)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.728,164.282)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.728,146.427)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.728,128.573)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.728,110.718)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.728,92.864)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.728,75.0096)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(224.728,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g><g class="toytree-Annotation-Markers" id="t2cfe1e415d80456ca0cf03e7ce07a6b2" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Mark-0" style="fill-opacity: 1.000" transform="translate(186.119,66.0824)"><circle r="5.0"></circle></g></g><g class="toytree-Annotation-Markers" id="tfd41d830d8374737bb664555798f22a0" style="fill:rgb(100.0%,64.7%,0.0%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Mark-0" style="fill-opacity: 1.000" transform="translate(166.119,66.0824)"><circle r="5.0"></circle></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t30fabe58a2d34496be806f32f5ff3a17";
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
        })(modules["toyplot.coordinates.Axis"],"t842df1db85054f9187a0d49c1854ca7d",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.5818114224000006, "min": -4.0226668000000005}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


When a Mark is added outside the tree domain...


```python
# draw a tree on a canvas defined in pixels
c, a, m = tree.draw(width=300);

# add a scale bar showing data units
m1 = tree.annotate.add_axes_scale_bar_to_tree(a);

# add a node marker by data coordinate
m2 = tree.annotate.add_node_markers(a, 'o', size=10, mask=tree.get_node_mask(14));

# add another node marker by data coordinate, then nudge by pixel units
m3 = tree.annotate.add_node_markers(a, 'o', size=10, mask=tree.get_node_mask(14), xshift=-20, color="orange");

# add a tip marker that extends the viewable domain
m4 = tree.annotate.add_tip_markers(a, 's', size=10, mask=tree.get_tip_mask(8, 9), xshift=100);
```


<div class="toyplot" id="t151dc3991ac84a629e463b302bb080bb" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t2fec2c07614649c6812824f4c338085d"><g class="toyplot-coordinates-Cartesian" id="tf77870fd24324f54a5925f957fb735db"><clipPath id="t2e29236f6229493fa43b4bd8f865797b"><rect x="50.0" y="65.00000000114275" width="200.0" height="175.0"></rect></clipPath><g clip-path="url(#t2e29236f6229493fa43b4bd8f865797b)"></g><g class="toyplot-coordinates-Axis" id="tbb6c06a15edf4289b8d31d7a7b50e3ee" transform="translate(50.0,240.00000000114275)"><line x1="0.9982646265407636" y1="0" x2="93.68481727340935" y2="0" style=""></line><g><line x1="0.9982646265407636" y1="0" x2="0.9982646265407636" y2="-5.0" style=""></line><line x1="24.16990278825791" y1="0" x2="24.16990278825791" y2="-5.0" style=""></line><line x1="47.341540949975055" y1="0" x2="47.341540949975055" y2="-5.0" style=""></line><line x1="70.51317911169221" y1="0" x2="70.51317911169221" y2="-5.0" style=""></line><line x1="93.68481727340935" y1="0" x2="93.68481727340935" y2="-5.0" style=""></line></g><g><g transform="translate(0.9982646265407636,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(24.16990278825791,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(47.341540949975055,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(70.51317911169221,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(93.68481727340935,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="tadc0b58c429c4a90a2977043d81219cd"><clipPath id="tc457ef711c91442b8dab5af83b06a672"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tc457ef711c91442b8dab5af83b06a672)"><g class="toytree-mark-Toytree" id="t5b6238c63695429fac96676ce756e185"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 61.3 204.4 L 61.3 217.8 L 143.7 217.8" id="11,0" style=""></path><path d="M 81.9 191.0 L 81.9 200.0 L 143.7 200.0" id="10,1" style=""></path><path d="M 81.9 191.0 L 81.9 182.1 L 143.7 182.1" id="10,2" style=""></path><path d="M 102.5 155.3 L 102.5 164.3 L 143.7 164.3" id="12,3" style=""></path><path d="M 102.5 155.3 L 102.5 146.4 L 143.7 146.4" id="12,4" style=""></path><path d="M 81.9 142.0 L 81.9 128.6 L 143.7 128.6" id="13,5" style=""></path><path d="M 81.9 95.1 L 81.9 110.7 L 143.7 110.7" id="16,6" style=""></path><path d="M 102.5 79.5 L 102.5 92.9 L 143.7 92.9" id="15,7" style=""></path><path d="M 123.1 66.1 L 123.1 75.0 L 143.7 75.0" id="14,8" style=""></path><path d="M 123.1 66.1 L 123.1 57.2 L 143.7 57.2" id="14,9" style=""></path><path d="M 61.3 204.4 L 61.3 191.0 L 81.9 191.0" id="11,10" style=""></path><path d="M 51.0 161.5 L 51.0 204.4 L 61.3 204.4" id="18,11" style=""></path><path d="M 81.9 142.0 L 81.9 155.3 L 102.5 155.3" id="13,12" style=""></path><path d="M 61.3 118.5 L 61.3 142.0 L 81.9 142.0" id="17,13" style=""></path><path d="M 102.5 79.5 L 102.5 66.1 L 123.1 66.1" id="15,14" style=""></path><path d="M 81.9 95.1 L 81.9 79.5 L 102.5 79.5" id="16,15" style=""></path><path d="M 61.3 118.5 L 61.3 95.1 L 81.9 95.1" id="17,16" style=""></path><path d="M 51.0 161.5 L 51.0 118.5 L 61.3 118.5" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(143.685,217.8)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(143.685,199.956)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(143.685,182.111)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(143.685,164.267)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(143.685,146.422)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(143.685,128.578)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(143.685,110.733)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(143.685,92.8889)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(143.685,75.0444)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(143.685,57.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g><g class="toytree-Annotation-Markers" id="t0681a1b93ea344738dd03993b4e05ace" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Mark-0" style="fill-opacity: 1.000" transform="translate(123.088,66.1222)"><circle r="5.0"></circle></g></g><g class="toytree-Annotation-Markers" id="t12aee9530926438b9c6e7f4a483cfc88" style="fill:rgb(100.0%,64.7%,0.0%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Mark-0" style="fill-opacity: 1.000" transform="translate(103.088,66.1222)"><circle r="5.0"></circle></g></g><g class="toytree-Annotation-Markers" id="ta57ef09efce34ea885a7b884d86638f6" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Mark-0" style="fill-opacity: 1.000" transform="translate(243.685,75.0444)"><circle r="5.0"></circle></g><g id="Mark-1" style="fill-opacity: 1.000" transform="translate(243.685,57.2)"><circle r="5.0"></circle></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t2fec2c07614649c6812824f4c338085d";
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
        })(modules["toyplot.coordinates.Axis"],"tbb6c06a15edf4289b8d31d7a7b50e3ee",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 4.588159973179562, "min": -4.043081314302156}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


## Multiple trees on one Cartesian

Each tree drawn on the same ``Cartesian`` can keep its own local companion scale bar. Keep the returned ``ToyTreeMark`` objects if you want to restyle one specific tree later.


```python
c, a, m0 = tree.draw(width=400, layout='r', scale_bar=True);
_, a, m1 = tree.draw(axes=a, layout='l', xbaseline=6, scale_bar=True);
```


<div class="toyplot" id="t15013f4970d647659aa4ef352de46b02"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="400.0px" height="275.0px" viewBox="0 0 400.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t40c1e591951a4e6d919a9a3a62b6ebd0"><g class="toyplot-coordinates-Cartesian" id="tba8187ba192e420f8b04531a636f6c43"><clipPath id="t34f6f6543fff4f43b6d72634896a1209"><rect x="50.0" y="65.04476420858973" width="300.0" height="175.0"></rect></clipPath><g clip-path="url(#t34f6f6543fff4f43b6d72634896a1209)"></g><g class="toyplot-coordinates-Axis" id="t1a18c21b6b28414d9f38a716edf22e8d" transform="translate(50.0,240.04476420858973)"><line x1="0.9999558518387804" y1="0" x2="86.14283822221662" y2="0" style=""></line><g><line x1="0.9999558518387804" y1="0" x2="0.9999558518387804" y2="-5.0" style=""></line><line x1="22.28567644443324" y1="0" x2="22.28567644443324" y2="-5.0" style=""></line><line x1="43.5713970370277" y1="0" x2="43.5713970370277" y2="-5.0" style=""></line><line x1="64.85711762962215" y1="0" x2="64.85711762962215" y2="-5.0" style=""></line><line x1="86.14283822221662" y1="0" x2="86.14283822221662" y2="-5.0" style=""></line></g><g><g transform="translate(0.9999558518387804,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(22.28567644443324,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(43.5713970370277,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(64.85711762962215,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(86.14283822221662,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t63ee74ec48714a86b3ba0e3928f9eb0a"><clipPath id="t2ab8c1423bc74d398e509c3555f655a2"><rect x="50.0" y="65.04476420858973" width="300.0" height="175.0"></rect></clipPath><g clip-path="url(#t2ab8c1423bc74d398e509c3555f655a2)"></g><g class="toyplot-coordinates-Axis" id="t1d83f66d762340fcbd1b1a59a4f974d1" transform="translate(50.0,240.04476420858973)"><line x1="213.85716177778338" y1="0" x2="299.0000441481612" y2="0" style=""></line><g><line x1="213.85716177778338" y1="0" x2="213.85716177778338" y2="-5.0" style=""></line><line x1="235.14288237037783" y1="0" x2="235.14288237037783" y2="-5.0" style=""></line><line x1="256.4286029629723" y1="0" x2="256.4286029629723" y2="-5.0" style=""></line><line x1="277.71432355556675" y1="0" x2="277.71432355556675" y2="-5.0" style=""></line><line x1="299.0000441481612" y1="0" x2="299.0000441481612" y2="-5.0" style=""></line></g><g><g transform="translate(213.85716177778338,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(235.14288237037783,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(256.4286029629723,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(277.71432355556675,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(299.0000441481612,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t7a274b9e4ed14c6191e9221b2890f1d2"><clipPath id="t864a86a6f2fb4bb5b21b984a72f6d6dd"><rect x="35.0" y="35.0" width="330.0" height="205.0"></rect></clipPath><g clip-path="url(#t864a86a6f2fb4bb5b21b984a72f6d6dd)"><g class="toytree-mark-Toytree" id="t43c952116f404228bd819563228a0f0a"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 60.5 204.5 L 60.5 217.8 L 136.1 217.8" id="11,0" style=""></path><path d="M 79.4 191.1 L 79.4 200.0 L 136.1 200.0" id="10,1" style=""></path><path d="M 79.4 191.1 L 79.4 182.1 L 136.1 182.1" id="10,2" style=""></path><path d="M 98.3 155.4 L 98.3 164.3 L 136.1 164.3" id="12,3" style=""></path><path d="M 98.3 155.4 L 98.3 146.4 L 136.1 146.4" id="12,4" style=""></path><path d="M 79.4 142.0 L 79.4 128.6 L 136.1 128.6" id="13,5" style=""></path><path d="M 79.4 95.1 L 79.4 110.7 L 136.1 110.7" id="16,6" style=""></path><path d="M 98.3 79.5 L 98.3 92.9 L 136.1 92.9" id="15,7" style=""></path><path d="M 117.2 66.1 L 117.2 75.0 L 136.1 75.0" id="14,8" style=""></path><path d="M 117.2 66.1 L 117.2 57.2 L 136.1 57.2" id="14,9" style=""></path><path d="M 60.5 204.5 L 60.5 191.1 L 79.4 191.1" id="11,10" style=""></path><path d="M 51.0 161.5 L 51.0 204.5 L 60.5 204.5" id="18,11" style=""></path><path d="M 79.4 142.0 L 79.4 155.4 L 98.3 155.4" id="13,12" style=""></path><path d="M 60.5 118.5 L 60.5 142.0 L 79.4 142.0" id="17,13" style=""></path><path d="M 98.3 79.5 L 98.3 66.1 L 117.2 66.1" id="15,14" style=""></path><path d="M 79.4 95.1 L 79.4 79.5 L 98.3 79.5" id="16,15" style=""></path><path d="M 60.5 118.5 L 60.5 95.1 L 79.4 95.1" id="17,16" style=""></path><path d="M 51.0 161.5 L 51.0 118.5 L 60.5 118.5" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(136.143,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(136.143,199.99)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(136.143,182.136)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(136.143,164.282)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(136.143,146.427)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(136.143,128.573)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(136.143,110.718)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(136.143,92.864)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(136.143,75.0096)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(136.143,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g><g class="toytree-mark-Toytree" id="t327dd1bea1984d0e9ae019143b3b14d5"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 339.5 204.5 L 339.5 217.8 L 263.9 217.8" id="11,0" style=""></path><path d="M 320.6 191.1 L 320.6 200.0 L 263.9 200.0" id="10,1" style=""></path><path d="M 320.6 191.1 L 320.6 182.1 L 263.9 182.1" id="10,2" style=""></path><path d="M 301.7 155.4 L 301.7 164.3 L 263.9 164.3" id="12,3" style=""></path><path d="M 301.7 155.4 L 301.7 146.4 L 263.9 146.4" id="12,4" style=""></path><path d="M 320.6 142.0 L 320.6 128.6 L 263.9 128.6" id="13,5" style=""></path><path d="M 320.6 95.1 L 320.6 110.7 L 263.9 110.7" id="16,6" style=""></path><path d="M 301.7 79.5 L 301.7 92.9 L 263.9 92.9" id="15,7" style=""></path><path d="M 282.8 66.1 L 282.8 75.0 L 263.9 75.0" id="14,8" style=""></path><path d="M 282.8 66.1 L 282.8 57.2 L 263.9 57.2" id="14,9" style=""></path><path d="M 339.5 204.5 L 339.5 191.1 L 320.6 191.1" id="11,10" style=""></path><path d="M 349.0 161.5 L 349.0 204.5 L 339.5 204.5" id="18,11" style=""></path><path d="M 320.6 142.0 L 320.6 155.4 L 301.7 155.4" id="13,12" style=""></path><path d="M 339.5 118.5 L 339.5 142.0 L 320.6 142.0" id="17,13" style=""></path><path d="M 301.7 79.5 L 301.7 66.1 L 282.8 66.1" id="15,14" style=""></path><path d="M 320.6 95.1 L 320.6 79.5 L 301.7 79.5" id="16,15" style=""></path><path d="M 339.5 118.5 L 339.5 95.1 L 320.6 95.1" id="17,16" style=""></path><path d="M 349.0 161.5 L 349.0 118.5 L 339.5 118.5" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(263.857,217.845)"><text x="-25.668" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(263.857,199.99)"><text x="-25.668" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(263.857,182.136)"><text x="-25.668" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(263.857,164.282)"><text x="-25.668" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(263.857,146.427)"><text x="-25.668" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(263.857,128.573)"><text x="-25.668" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(263.857,110.718)"><text x="-25.668" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(263.857,92.864)"><text x="-25.668" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(263.857,75.0096)"><text x="-25.668" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(263.857,57.1552)"><text x="-25.668" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t40c1e591951a4e6d919a9a3a62b6ebd0";
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
        })(modules["toyplot.coordinates.Axis"],"t1a18c21b6b28414d9f38a716edf22e8d",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 10.046977777777778, "min": -4.046977777777778}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 300.0, "min": 0.0}, "scale": "linear"}]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"t1d83f66d762340fcbd1b1a59a4f974d1",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 10.046977777777778, "min": -4.046977777777778}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 300.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


## Multiple Cartesians on one Canvas

An easy way to plot multiple trees on the same ``Canvas`` is to create multiple ``Cartesian`` objects to add trees to.

In this example, we define two cartesians and add a tree to each. You can see that the left cartesian retains the default cartesian axes styling, whereas the right cartesian, on which a tree was drawn with ``scale_bar=True`` applies scale bar styling to the depth-axis, and hides the span-axis. 


```python
# create a canvas
canvas = toyplot.Canvas(width=600, height=300)

# create two cartesian's with pixel unit defined bounds
ax0 = canvas.cartesian(bounds=(50, 250, 50, 250))
ax1 = canvas.cartesian(bounds=(350, 550, 50, 250))

# add a tree to each cartesian
tree.draw(axes=ax0)
tree.draw(axes=ax1, scale_bar=True);
```


<div class="toyplot" id="tb832fd798d70401f82af2d4957eb6d44" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="600.0px" height="300.0px" viewBox="0 0 600.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t62a310d5224e427f95c4187fbf62d246"><g class="toyplot-coordinates-Cartesian" id="t6394970d172a459ca25f508fee2cb32a"><clipPath id="tb761ab6e95284dea869070bbaf310f9b"><rect x="40.0" y="40.0" width="220.0" height="220.0"></rect></clipPath><g clip-path="url(#tb761ab6e95284dea869070bbaf310f9b)"><g class="toytree-mark-Toytree" id="tfbf6832b00824811ba58ed8aeeec3a57"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 70.3 227.4 L 70.3 242.8 L 224.7 242.8" id="11,0" style=""></path><path d="M 108.9 211.9 L 108.9 222.2 L 224.7 222.2" id="10,1" style=""></path><path d="M 108.9 211.9 L 108.9 201.6 L 224.7 201.6" id="10,2" style=""></path><path d="M 147.5 170.6 L 147.5 180.9 L 224.7 180.9" id="12,3" style=""></path><path d="M 147.5 170.6 L 147.5 160.3 L 224.7 160.3" id="12,4" style=""></path><path d="M 108.9 155.2 L 108.9 139.7 L 224.7 139.7" id="13,5" style=""></path><path d="M 108.9 101.0 L 108.9 119.1 L 224.7 119.1" id="16,6" style=""></path><path d="M 147.5 83.0 L 147.5 98.4 L 224.7 98.4" id="15,7" style=""></path><path d="M 186.1 67.5 L 186.1 77.8 L 224.7 77.8" id="14,8" style=""></path><path d="M 186.1 67.5 L 186.1 57.2 L 224.7 57.2" id="14,9" style=""></path><path d="M 70.3 227.4 L 70.3 211.9 L 108.9 211.9" id="11,10" style=""></path><path d="M 51.0 177.7 L 51.0 227.4 L 70.3 227.4" id="18,11" style=""></path><path d="M 108.9 155.2 L 108.9 170.6 L 147.5 170.6" id="13,12" style=""></path><path d="M 70.3 128.1 L 70.3 155.2 L 108.9 155.2" id="17,13" style=""></path><path d="M 147.5 83.0 L 147.5 67.5 L 186.1 67.5" id="15,14" style=""></path><path d="M 108.9 101.0 L 108.9 83.0 L 147.5 83.0" id="16,15" style=""></path><path d="M 70.3 128.1 L 70.3 101.0 L 108.9 101.0" id="17,16" style=""></path><path d="M 51.0 177.7 L 51.0 128.1 L 70.3 128.1" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.728,242.835)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.728,222.205)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.728,201.575)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.728,180.945)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.728,160.315)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.728,139.685)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.728,119.055)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.728,98.4252)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.728,77.7953)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(224.728,57.1653)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g><g class="toyplot-coordinates-Axis" id="t67a35891bfed4a2795e657f756304ca5" transform="translate(50.0,250.0)translate(0,10.0)"><line x1="0.8823477508955642" y1="0" x2="177.35189793001217" y2="0" style=""></line><g><g transform="translate(0.8823477508955642,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-4</text></g><g transform="translate(44.99973529567471,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-3</text></g><g transform="translate(89.11712284045386,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-2</text></g><g transform="translate(133.23451038523302,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-1</text></g><g transform="translate(177.35189793001217,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g><g class="toyplot-coordinates-Axis" id="t03335251f83b44ba9f368d998bf89368" transform="translate(50.0,250.0)rotate(-90.0)translate(0,-10.0)"><line x1="6.71641791044775" y1="0" x2="193.28358208955225" y2="0" style=""></line><g><g transform="translate(6.71641791044775,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(68.90547263681592,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(131.09452736318408,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">6</text></g><g transform="translate(193.28358208955225,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">9</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="t478a248a2fd84a5397ba36e1c8e845ee"><clipPath id="t67924c3c88db4966bc5ab89224eabcc2"><rect x="350.0" y="65.03465034757289" width="200.0" height="200.0"></rect></clipPath><g clip-path="url(#t67924c3c88db4966bc5ab89224eabcc2)"></g><g class="toyplot-coordinates-Axis" id="tb8e9a862e26c441db7400c14aaac3a76" transform="translate(350.0,265.0346503475729)"><line x1="0.9845545534228145" y1="0" x2="174.72845372274375" y2="0" style=""></line><g><line x1="0.9845545534228145" y1="0" x2="0.9845545534228145" y2="-5.0" style=""></line><line x1="44.420529345753046" y1="0" x2="44.420529345753046" y2="-5.0" style=""></line><line x1="87.85650413808328" y1="0" x2="87.85650413808328" y2="-5.0" style=""></line><line x1="131.29247893041352" y1="0" x2="131.29247893041352" y2="-5.0" style=""></line><line x1="174.72845372274375" y1="0" x2="174.72845372274375" y2="-5.0" style=""></line></g><g><g transform="translate(0.9845545534228145,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(44.420529345753046,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(87.85650413808328,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(131.29247893041352,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(174.72845372274375,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t5267b61a4e3245598c7c6f07a2a60040"><clipPath id="ta1fcd34d3883476b8ce8c9b7f7b4c371"><rect x="340.0" y="40.0" width="220.0" height="220.0"></rect></clipPath><g clip-path="url(#ta1fcd34d3883476b8ce8c9b7f7b4c371)"><g class="toytree-mark-Toytree" id="tc681911b721a44df869a2780d6ae1044"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 370.3 227.4 L 370.3 242.8 L 524.7 242.8" id="11,0" style=""></path><path d="M 408.9 211.9 L 408.9 222.2 L 524.7 222.2" id="10,1" style=""></path><path d="M 408.9 211.9 L 408.9 201.6 L 524.7 201.6" id="10,2" style=""></path><path d="M 447.5 170.6 L 447.5 180.9 L 524.7 180.9" id="12,3" style=""></path><path d="M 447.5 170.6 L 447.5 160.3 L 524.7 160.3" id="12,4" style=""></path><path d="M 408.9 155.2 L 408.9 139.7 L 524.7 139.7" id="13,5" style=""></path><path d="M 408.9 101.0 L 408.9 119.1 L 524.7 119.1" id="16,6" style=""></path><path d="M 447.5 83.0 L 447.5 98.4 L 524.7 98.4" id="15,7" style=""></path><path d="M 486.1 67.5 L 486.1 77.8 L 524.7 77.8" id="14,8" style=""></path><path d="M 486.1 67.5 L 486.1 57.2 L 524.7 57.2" id="14,9" style=""></path><path d="M 370.3 227.4 L 370.3 211.9 L 408.9 211.9" id="11,10" style=""></path><path d="M 351.0 177.7 L 351.0 227.4 L 370.3 227.4" id="18,11" style=""></path><path d="M 408.9 155.2 L 408.9 170.6 L 447.5 170.6" id="13,12" style=""></path><path d="M 370.3 128.1 L 370.3 155.2 L 408.9 155.2" id="17,13" style=""></path><path d="M 447.5 83.0 L 447.5 67.5 L 486.1 67.5" id="15,14" style=""></path><path d="M 408.9 101.0 L 408.9 83.0 L 447.5 83.0" id="16,15" style=""></path><path d="M 370.3 128.1 L 370.3 101.0 L 408.9 101.0" id="17,16" style=""></path><path d="M 351.0 177.7 L 351.0 128.1 L 370.3 128.1" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(524.728,242.835)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(524.728,222.205)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(524.728,201.575)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(524.728,180.945)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(524.728,160.315)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(524.728,139.685)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(524.728,119.055)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(524.728,98.4252)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(524.728,77.7953)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(524.728,57.1653)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t62a310d5224e427f95c4187fbf62d246";
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
        })(modules["toyplot.coordinates.Axis"],"t67a35891bfed4a2795e657f756304ca5",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.5133600000000005, "min": -4.02}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"t03335251f83b44ba9f368d998bf89368",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 9.324, "min": -0.32399999999999946}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"tb8e9a862e26c441db7400c14aaac3a76",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.5818114224000016, "min": -4.0226668000000005}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


## Companion axes
Beware there is some magic that goes on under the hood to allow setting a scale bar that shows only the domain of the tree depth-axis, while still allowing you to add additional marks/annotations to the same Cartesian, and expand the viewable space to accommodate them, without the axes ticks also showing that additional non tree-related data domain. This problem is demonstrated in the plot below, where we do not set a tree scale bar using either ``scale_bar=True`` or ``tree.annotate.add_axes_scale_bar_to_tree()``, and instead try to style the returned Cartesian object that contains both tree and data marks.

You can see that the depth-scale (x-axis) now spans both the tree and data, which doesn't look very nice. 


```python
# draw a tree on a Cartesian
canvas, axes, mark = tree.draw()

# adding plots to the 'standard' axes will expand the clip
axes.scatterplot([5] * 10, range(10), size=10, color='red');

# the domain of 'axes' includes both the tree and plotted data 
axes.x.show = True
```


<div class="toyplot" id="t5219a8b5944b4919b93775a6a09c74bd" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t1604112aba07461fa08ebbb56d688190"><g class="toyplot-coordinates-Cartesian" id="t910a2b849a034ba2a32d00de2af8a6dd"><clipPath id="t20859e4040eb4843af25e79a5ec1aa3e"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t20859e4040eb4843af25e79a5ec1aa3e)"><g class="toytree-mark-Toytree" id="tae25426aef734eb68282ccce2720044e"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 78.9 204.5 L 78.9 217.8 L 150.0 217.8" id="11,0" style=""></path><path d="M 96.7 191.1 L 96.7 200.0 L 150.0 200.0" id="10,1" style=""></path><path d="M 96.7 191.1 L 96.7 182.1 L 150.0 182.1" id="10,2" style=""></path><path d="M 114.4 155.4 L 114.4 164.3 L 150.0 164.3" id="12,3" style=""></path><path d="M 114.4 155.4 L 114.4 146.4 L 150.0 146.4" id="12,4" style=""></path><path d="M 96.7 142.0 L 96.7 128.6 L 150.0 128.6" id="13,5" style=""></path><path d="M 96.7 95.1 L 96.7 110.7 L 150.0 110.7" id="16,6" style=""></path><path d="M 114.4 79.5 L 114.4 92.9 L 150.0 92.9" id="15,7" style=""></path><path d="M 132.2 66.1 L 132.2 75.0 L 150.0 75.0" id="14,8" style=""></path><path d="M 132.2 66.1 L 132.2 57.2 L 150.0 57.2" id="14,9" style=""></path><path d="M 78.9 204.5 L 78.9 191.1 L 96.7 191.1" id="11,10" style=""></path><path d="M 70.0 161.5 L 70.0 204.5 L 78.9 204.5" id="18,11" style=""></path><path d="M 96.7 142.0 L 96.7 155.4 L 114.4 155.4" id="13,12" style=""></path><path d="M 78.9 118.5 L 78.9 142.0 L 96.7 142.0" id="17,13" style=""></path><path d="M 114.4 79.5 L 114.4 66.1 L 132.2 66.1" id="15,14" style=""></path><path d="M 96.7 95.1 L 96.7 79.5 L 114.4 79.5" id="16,15" style=""></path><path d="M 78.9 118.5 L 78.9 95.1 L 96.7 95.1" id="17,16" style=""></path><path d="M 70.0 161.5 L 70.0 118.5 L 78.9 118.5" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(150,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(150,199.99)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(150,182.136)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(150,164.282)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(150,146.427)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(150,128.573)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(150,110.718)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(150,92.864)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(150,75.0096)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(150,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g><g class="toyplot-mark-Point" id="tbb23632ca96243ceb9f336875e761b3f"><g class="toyplot-Series"><g style="fill:rgb(100%,0%,0%);fill-opacity:1.0;opacity:1.0;stroke:rgb(100%,0%,0%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(250.0, 217.84476420858974)"><circle r="5.0"></circle></g><g style="fill:rgb(100%,0%,0%);fill-opacity:1.0;opacity:1.0;stroke:rgb(100%,0%,0%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(250.0, 199.9903721622365)"><circle r="5.0"></circle></g><g style="fill:rgb(100%,0%,0%);fill-opacity:1.0;opacity:1.0;stroke:rgb(100%,0%,0%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(250.0, 182.13598011588323)"><circle r="5.0"></circle></g><g style="fill:rgb(100%,0%,0%);fill-opacity:1.0;opacity:1.0;stroke:rgb(100%,0%,0%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(250.0, 164.28158806952993)"><circle r="5.0"></circle></g><g style="fill:rgb(100%,0%,0%);fill-opacity:1.0;opacity:1.0;stroke:rgb(100%,0%,0%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(250.0, 146.42719602317666)"><circle r="5.0"></circle></g><g style="fill:rgb(100%,0%,0%);fill-opacity:1.0;opacity:1.0;stroke:rgb(100%,0%,0%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(250.0, 128.57280397682337)"><circle r="5.0"></circle></g><g style="fill:rgb(100%,0%,0%);fill-opacity:1.0;opacity:1.0;stroke:rgb(100%,0%,0%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(250.0, 110.7184119304701)"><circle r="5.0"></circle></g><g style="fill:rgb(100%,0%,0%);fill-opacity:1.0;opacity:1.0;stroke:rgb(100%,0%,0%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(250.0, 92.86401988411683)"><circle r="5.0"></circle></g><g style="fill:rgb(100%,0%,0%);fill-opacity:1.0;opacity:1.0;stroke:rgb(100%,0%,0%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(250.0, 75.00962783776355)"><circle r="5.0"></circle></g><g style="fill:rgb(100%,0%,0%);fill-opacity:1.0;opacity:1.0;stroke:rgb(100%,0%,0%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(250.0, 57.15523579141026)"><circle r="5.0"></circle></g></g></g></g><g class="toyplot-coordinates-Axis" id="t212bda3e91ac4ad284b99e071c3a1998" transform="translate(50.0,225.0)translate(0,15.0)"><line x1="20.0" y1="0" x2="200.0" y2="0" style=""></line><g><g transform="translate(0.0,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-5</text></g><g transform="translate(100.0,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(200.0,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">5</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/tables"] = (function()
    {
        var tables = [];

        var module = {};

        module.set = function(owner, key, names, columns)
        {
            tables.push({owner: owner, key: key, names: names, columns: columns});
        }

        module.get = function(owner, key)
        {
            for(var i = 0; i != tables.length; ++i)
            {
                var table = tables[i];
                if(table.owner != owner)
                    continue;
                if(table.key != key)
                    continue;
                return {names: table.names, columns: table.columns};
            }
        }

        module.get_csv = function(owner, key)
        {
            var table = module.get(owner, key);
            if(table != undefined)
            {
                var csv = "";
                csv += table.names.join(",") + "\n";
                for(var i = 0; i != table.columns[0].length; ++i)
                {
                  for(var j = 0; j != table.columns.length; ++j)
                  {
                    if(j)
                      csv += ",";
                    csv += table.columns[j][i];
                  }
                  csv += "\n";
                }
                return csv;
            }
        }

        return module;
    })();
modules["toyplot/root/id"] = "t5219a8b5944b4919b93775a6a09c74bd";
modules["toyplot/root"] = (function(root_id)
    {
        return document.querySelector("#" + root_id);
    })(modules["toyplot/root/id"]);
modules["toyplot/canvas/id"] = "t1604112aba07461fa08ebbb56d688190";
modules["toyplot/canvas"] = (function(canvas_id)
    {
        return document.querySelector("#" + canvas_id);
    })(modules["toyplot/canvas/id"]);
modules["toyplot/menus/context"] = (function(root, canvas)
    {
        var wrapper = document.createElement("div");
        wrapper.innerHTML = "<ul class='toyplot-context-menu' style='background:#eee; border:1px solid #b8b8b8; border-radius:5px; box-shadow: 0px 0px 8px rgba(0%,0%,0%,0.25); margin:0; padding:3px 0; position:fixed; visibility:hidden;'></ul>"
        var menu = wrapper.firstChild;

        root.appendChild(menu);

        var items = [];

        var ignore_mouseup = null;
        function open_menu(e)
        {
            var show_menu = false;
            for(var index=0; index != items.length; ++index)
            {
                var item = items[index];
                if(item.show(e))
                {
                    item.item.style.display = "block";
                    show_menu = true;
                }
                else
                {
                    item.item.style.display = "none";
                }
            }

            if(show_menu)
            {
                ignore_mouseup = true;
                menu.style.left = (e.clientX + 1) + "px";
                menu.style.top = (e.clientY - 5) + "px";
                menu.style.visibility = "visible";
                e.stopPropagation();
                e.preventDefault();
            }
        }

        function close_menu()
        {
            menu.style.visibility = "hidden";
        }

        function contextmenu(e)
        {
            open_menu(e);
        }

        function mousemove(e)
        {
            ignore_mouseup = false;
        }

        function mouseup(e)
        {
            if(ignore_mouseup)
            {
                ignore_mouseup = false;
                return;
            }
            close_menu();
        }

        function keydown(e)
        {
            if(e.key == "Escape" || e.key == "Esc" || e.keyCode == 27)
            {
                close_menu();
            }
        }

        canvas.addEventListener("contextmenu", contextmenu);
        canvas.addEventListener("mousemove", mousemove);
        document.addEventListener("mouseup", mouseup);
        document.addEventListener("keydown", keydown);

        var module = {};
        module.add_item = function(label, show, activate)
        {
            var wrapper = document.createElement("div");
            wrapper.innerHTML = "<li class='toyplot-context-menu-item' style='background:#eee; color:#333; padding:2px 20px; list-style:none; margin:0; text-align:left;'>" + label + "</li>"
            var item = wrapper.firstChild;

            items.push({item: item, show: show});

            function mouseover()
            {
                this.style.background = "steelblue";
                this.style.color = "white";
            }

            function mouseout()
            {
                this.style.background = "#eee";
                this.style.color = "#333";
            }

            function choose_item(e)
            {
                close_menu();
                activate();

                e.stopPropagation();
                e.preventDefault();
            }

            item.addEventListener("mouseover", mouseover);
            item.addEventListener("mouseout", mouseout);
            item.addEventListener("mouseup", choose_item);
            item.addEventListener("contextmenu", choose_item);

            menu.appendChild(item);
        };
        return module;
    })(modules["toyplot/root"],modules["toyplot/canvas"]);
modules["toyplot/io"] = (function()
    {
        var module = {};
        module.save_file = function(mime_type, charset, data, filename)
        {
            var uri = "data:" + mime_type + ";charset=" + charset + "," + data;
            uri = encodeURI(uri);

            var link = document.createElement("a");
            if(typeof link.download != "undefined")
            {
              link.href = uri;
              link.style = "visibility:hidden";
              link.download = filename;

              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
            }
            else
            {
              window.open(uri);
            }
        };
        return module;
    })();
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
(function(tables, context_menu, io, owner_id, key, label, names, columns, filename)
        {
            tables.set(owner_id, key, names, columns);

            var owner = document.querySelector("#" + owner_id);
            function show_item(e)
            {
                return owner.contains(e.target);
            }

            function choose_item()
            {
                io.save_file("text/csv", "utf-8", tables.get_csv(owner_id, key), filename + ".csv");
            }

            context_menu.add_item("Save " + label + " as CSV", show_item, choose_item);
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"tbb23632ca96243ceb9f336875e761b3f","data","point",["x", "y0"],[[5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0]],"toyplot");
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"t212bda3e91ac4ad284b99e071c3a1998",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 5.0, "min": -5.0}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


## Cartesian axes styling

For most tree drawings, you can rely on ``tree.draw(scale_bar=True)``, or ``tree.annotate.add_axes_scale_bar_to_tree()`` to style the Cartesian axes to display units along the 'depth' scale of the tree. 

However, advanced users may wish to apply more custom styling, or to combine ``toytree`` plots with other ``toyplot`` data plots. In this case, you will need a better understanding of Cartesian objects. Many of these details can be found in the [toyplot documentation](toyplot.rtfd.io). Below is a simple example of how a Cartesian axis can be styled, showing the default style on the y-axis, and custom styling options applied to the x-axis. The rest of this page focuses more on toytree-specific details. 


```python
# generate (Canvas, Cartesian, Mark)
canvas = toyplot.Canvas(width=350, height=250)
axes = canvas.cartesian()
axes.scatterplot(range(10), range(5, 15), color='salmon', size=10);

# the y-axis will remain in default styling
axes.y.label.text = 'unstyled axis'

# set space between the spine and the data
axes.padding = 10                         # default is 10px

# style axes spine
axes.x.spine.show = True                  # bool
axes.x.spine.style = {'stroke-width': 2, 'stroke': 'slate-blue'} # set spine stroke style

# style axes label
axes.x.label.text = "styled axis"         # set a text label   
axes.x.label.location = "below"           # set label 'above' or 'below' (default) the spine
axes.x.label.offset = 25                  # set px distance of label from spine
axes.x.label.style = {"font-size": 14}    # set label text style

# style axes ticks
axes.x.ticks.show = True                  # set x ticks to show
axes.x.ticks.far = 0                      # set tick length on far side
axes.x.ticks.near = 5                     # set tick length on near side
axes.x.ticks.style['stroke-width'] = 2    # set tick stroke style

# style axes tick labels
axes.x.ticks.labels.show = True           # set tick labels to show
axes.x.ticks.labels.offset = 12           # set tick labels distance from spine
axes.x.ticks.labels.angle = 45            # set tick labels text angle
axes.x.ticks.labels.style = {'font-size': 12, 'fill': 'darkcyan'}  # set tick labels text style

# modify the domain (min,max scale of axis)
axes.x.domain.min = -2                    # set domain min
axes.x.domain.max = 12                    # set domain max
axes.x.domain.show = False                # extend spine to min,max (False) or only to data (True)

# set the position of ticks
axes.x.ticks.locator = toyplot.locator.Integer(step=2)
```


<div class="toyplot" id="tba51448fcade41619380f5588b840060" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="350.0px" height="250.0px" viewBox="0 0 350.0 250.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t39cd9ed1fa2f48ff9b80d59c76b08e83"><g class="toyplot-coordinates-Cartesian" id="t477721e84dff4cfdb33589c30474552f"><clipPath id="tfccc9fec9dee459c883a1d1e42ea7e4d"><rect x="40.0" y="40.0" width="270.0" height="170.0"></rect></clipPath><g clip-path="url(#tfccc9fec9dee459c883a1d1e42ea7e4d)"><g class="toyplot-mark-Point" id="tbd69bd5782024de4973be6ba032a700f"><g class="toyplot-Series"><g style="fill:rgb(98%,50.2%,44.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98%,50.2%,44.7%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(85.71428571428572, 200.0)"><circle r="5.0"></circle></g><g style="fill:rgb(98%,50.2%,44.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98%,50.2%,44.7%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(103.57142857142856, 185.0)"><circle r="5.0"></circle></g><g style="fill:rgb(98%,50.2%,44.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98%,50.2%,44.7%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(121.42857142857142, 170.0)"><circle r="5.0"></circle></g><g style="fill:rgb(98%,50.2%,44.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98%,50.2%,44.7%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(139.28571428571428, 155.0)"><circle r="5.0"></circle></g><g style="fill:rgb(98%,50.2%,44.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98%,50.2%,44.7%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(157.1428571428571, 140.0)"><circle r="5.0"></circle></g><g style="fill:rgb(98%,50.2%,44.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98%,50.2%,44.7%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(175.0, 125.0)"><circle r="5.0"></circle></g><g style="fill:rgb(98%,50.2%,44.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98%,50.2%,44.7%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(192.85714285714283, 110.0)"><circle r="5.0"></circle></g><g style="fill:rgb(98%,50.2%,44.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98%,50.2%,44.7%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(210.71428571428572, 95.0)"><circle r="5.0"></circle></g><g style="fill:rgb(98%,50.2%,44.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98%,50.2%,44.7%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(228.57142857142856, 80.0)"><circle r="5.0"></circle></g><g style="fill:rgb(98%,50.2%,44.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98%,50.2%,44.7%);stroke-opacity:1.0" class="toyplot-Datum" transform="translate(246.42857142857144, 65.0)"><circle r="5.0"></circle></g></g></g></g><g class="toyplot-coordinates-Axis" id="t21273cba5a1f4f54b90de2fc11ac2adb" transform="translate(50.0,200.0)translate(0,10.0)"><line x1="0" y1="0" x2="250.0" y2="0" style="stroke:slate-blue;stroke-width:2"></line><g><line x1="0.0" y1="5.0" x2="0.0" y2="0" style="stroke-width:2"></line><line x1="35.714285714285715" y1="5.0" x2="35.714285714285715" y2="0" style="stroke-width:2"></line><line x1="71.42857142857143" y1="5.0" x2="71.42857142857143" y2="0" style="stroke-width:2"></line><line x1="107.14285714285714" y1="5.0" x2="107.14285714285714" y2="0" style="stroke-width:2"></line><line x1="142.85714285714286" y1="5.0" x2="142.85714285714286" y2="0" style="stroke-width:2"></line><line x1="178.57142857142858" y1="5.0" x2="178.57142857142858" y2="0" style="stroke-width:2"></line><line x1="214.28571428571428" y1="5.0" x2="214.28571428571428" y2="0" style="stroke-width:2"></line><line x1="250.0" y1="5.0" x2="250.0" y2="0" style="stroke-width:2"></line></g><g><g transform="translate(0.0,12.0)rotate(-45)"><text x="-10.668" y="3.066" style="fill:rgb(0%,54.5%,54.5%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-2</text></g><g transform="translate(35.714285714285715,12.0)rotate(-45)"><text x="-6.672000000000001" y="3.066" style="fill:rgb(0%,54.5%,54.5%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(71.42857142857143,12.0)rotate(-45)"><text x="-6.672000000000001" y="3.066" style="fill:rgb(0%,54.5%,54.5%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(107.14285714285714,12.0)rotate(-45)"><text x="-6.672000000000001" y="3.066" style="fill:rgb(0%,54.5%,54.5%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(142.85714285714286,12.0)rotate(-45)"><text x="-6.672000000000001" y="3.066" style="fill:rgb(0%,54.5%,54.5%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">6</text></g><g transform="translate(178.57142857142858,12.0)rotate(-45)"><text x="-6.672000000000001" y="3.066" style="fill:rgb(0%,54.5%,54.5%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">8</text></g><g transform="translate(214.28571428571428,12.0)rotate(-45)"><text x="-13.344000000000001" y="3.066" style="fill:rgb(0%,54.5%,54.5%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">10</text></g><g transform="translate(250.0,12.0)rotate(-45)"><text x="-13.344000000000001" y="3.066" style="fill:rgb(0%,54.5%,54.5%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">12</text></g></g><g transform="translate(125.0,25.0)"><text x="-35.797999999999995" y="11.977" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:14.0px;font-weight:bold;stroke:none;vertical-align:baseline;white-space:pre">styled axis</text></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-6.0" y2="9.0" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-12.0" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g><g class="toyplot-coordinates-Axis" id="t182e0789160f44d095514d7a50d5eb78" transform="translate(50.0,200.0)rotate(-90.0)translate(0,-10.0)"><line x1="0" y1="0" x2="135.0" y2="0" style=""></line><g><g transform="translate(0.0,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">5</text></g><g transform="translate(75.0,-6)"><text x="-5.56" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">10</text></g><g transform="translate(150.0,-6)"><text x="-5.56" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">15</text></g></g><g transform="translate(75.0,-22)"><text x="-38.016" y="0.0" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:bold;stroke:none;vertical-align:baseline;white-space:pre">unstyled axis</text></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/tables"] = (function()
    {
        var tables = [];

        var module = {};

        module.set = function(owner, key, names, columns)
        {
            tables.push({owner: owner, key: key, names: names, columns: columns});
        }

        module.get = function(owner, key)
        {
            for(var i = 0; i != tables.length; ++i)
            {
                var table = tables[i];
                if(table.owner != owner)
                    continue;
                if(table.key != key)
                    continue;
                return {names: table.names, columns: table.columns};
            }
        }

        module.get_csv = function(owner, key)
        {
            var table = module.get(owner, key);
            if(table != undefined)
            {
                var csv = "";
                csv += table.names.join(",") + "\n";
                for(var i = 0; i != table.columns[0].length; ++i)
                {
                  for(var j = 0; j != table.columns.length; ++j)
                  {
                    if(j)
                      csv += ",";
                    csv += table.columns[j][i];
                  }
                  csv += "\n";
                }
                return csv;
            }
        }

        return module;
    })();
modules["toyplot/root/id"] = "tba51448fcade41619380f5588b840060";
modules["toyplot/root"] = (function(root_id)
    {
        return document.querySelector("#" + root_id);
    })(modules["toyplot/root/id"]);
modules["toyplot/canvas/id"] = "t39cd9ed1fa2f48ff9b80d59c76b08e83";
modules["toyplot/canvas"] = (function(canvas_id)
    {
        return document.querySelector("#" + canvas_id);
    })(modules["toyplot/canvas/id"]);
modules["toyplot/menus/context"] = (function(root, canvas)
    {
        var wrapper = document.createElement("div");
        wrapper.innerHTML = "<ul class='toyplot-context-menu' style='background:#eee; border:1px solid #b8b8b8; border-radius:5px; box-shadow: 0px 0px 8px rgba(0%,0%,0%,0.25); margin:0; padding:3px 0; position:fixed; visibility:hidden;'></ul>"
        var menu = wrapper.firstChild;

        root.appendChild(menu);

        var items = [];

        var ignore_mouseup = null;
        function open_menu(e)
        {
            var show_menu = false;
            for(var index=0; index != items.length; ++index)
            {
                var item = items[index];
                if(item.show(e))
                {
                    item.item.style.display = "block";
                    show_menu = true;
                }
                else
                {
                    item.item.style.display = "none";
                }
            }

            if(show_menu)
            {
                ignore_mouseup = true;
                menu.style.left = (e.clientX + 1) + "px";
                menu.style.top = (e.clientY - 5) + "px";
                menu.style.visibility = "visible";
                e.stopPropagation();
                e.preventDefault();
            }
        }

        function close_menu()
        {
            menu.style.visibility = "hidden";
        }

        function contextmenu(e)
        {
            open_menu(e);
        }

        function mousemove(e)
        {
            ignore_mouseup = false;
        }

        function mouseup(e)
        {
            if(ignore_mouseup)
            {
                ignore_mouseup = false;
                return;
            }
            close_menu();
        }

        function keydown(e)
        {
            if(e.key == "Escape" || e.key == "Esc" || e.keyCode == 27)
            {
                close_menu();
            }
        }

        canvas.addEventListener("contextmenu", contextmenu);
        canvas.addEventListener("mousemove", mousemove);
        document.addEventListener("mouseup", mouseup);
        document.addEventListener("keydown", keydown);

        var module = {};
        module.add_item = function(label, show, activate)
        {
            var wrapper = document.createElement("div");
            wrapper.innerHTML = "<li class='toyplot-context-menu-item' style='background:#eee; color:#333; padding:2px 20px; list-style:none; margin:0; text-align:left;'>" + label + "</li>"
            var item = wrapper.firstChild;

            items.push({item: item, show: show});

            function mouseover()
            {
                this.style.background = "steelblue";
                this.style.color = "white";
            }

            function mouseout()
            {
                this.style.background = "#eee";
                this.style.color = "#333";
            }

            function choose_item(e)
            {
                close_menu();
                activate();

                e.stopPropagation();
                e.preventDefault();
            }

            item.addEventListener("mouseover", mouseover);
            item.addEventListener("mouseout", mouseout);
            item.addEventListener("mouseup", choose_item);
            item.addEventListener("contextmenu", choose_item);

            menu.appendChild(item);
        };
        return module;
    })(modules["toyplot/root"],modules["toyplot/canvas"]);
modules["toyplot/io"] = (function()
    {
        var module = {};
        module.save_file = function(mime_type, charset, data, filename)
        {
            var uri = "data:" + mime_type + ";charset=" + charset + "," + data;
            uri = encodeURI(uri);

            var link = document.createElement("a");
            if(typeof link.download != "undefined")
            {
              link.href = uri;
              link.style = "visibility:hidden";
              link.download = filename;

              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
            }
            else
            {
              window.open(uri);
            }
        };
        return module;
    })();
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
(function(tables, context_menu, io, owner_id, key, label, names, columns, filename)
        {
            tables.set(owner_id, key, names, columns);

            var owner = document.querySelector("#" + owner_id);
            function show_item(e)
            {
                return owner.contains(e.target);
            }

            function choose_item()
            {
                io.save_file("text/csv", "utf-8", tables.get_csv(owner_id, key), filename + ".csv");
            }

            context_menu.add_item("Save " + label + " as CSV", show_item, choose_item);
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"tbd69bd5782024de4973be6ba032a700f","data","point",["x", "y0"],[[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0], [5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 13.0, 14.0]],"toyplot");
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"t21273cba5a1f4f54b90de2fc11ac2adb",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 12, "min": -2}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 250.0, "min": 0.0}, "scale": "linear"}]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"t182e0789160f44d095514d7a50d5eb78",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 15.0, "min": 5.0}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 150.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


## Debug Canvas Example

This example renders a tree and overlays debug fills to show
the canvas, axes range, padding, and data bounds.



```python
# set a long tip name on a tip node
_tree = tree.copy()
_tree[0].name = 'A very long name'

# draw the tree and show both axes
c, a, m = tree.draw(layout='r')
a.x.show = True
a.y.show = True

# add the debugging outlines
toytree.utils.debug_toyplot_canvas(c, a, marks=[m]);
```


<div class="toyplot" id="t750e8bdc8a934bf69c3a9350c2e8182c" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:#f2f2f2;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t5f067b89ce9d481e90bd80e65fc552cb"><g class="toyplot-coordinates-Cartesian" id="t63cf2e5f9e9d4b9f96ec43260a736de7"><clipPath id="t7ccd8a6f015e497095c7e7874f97fe0b"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t7ccd8a6f015e497095c7e7874f97fe0b)"><g class="toytree-mark-Toytree" id="ta70e70e37eea4ddc9ca844492d70e7de"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 70.3 205.6 L 70.3 218.3 L 224.7 218.3" id="11,0" style=""></path><path d="M 108.9 193.0 L 108.9 201.4 L 224.7 201.4" id="10,1" style=""></path><path d="M 108.9 193.0 L 108.9 184.6 L 224.7 184.6" id="10,2" style=""></path><path d="M 147.5 159.4 L 147.5 167.8 L 224.7 167.8" id="12,3" style=""></path><path d="M 147.5 159.4 L 147.5 151.0 L 224.7 151.0" id="12,4" style=""></path><path d="M 108.9 146.7 L 108.9 134.1 L 224.7 134.1" id="13,5" style=""></path><path d="M 108.9 102.6 L 108.9 117.3 L 224.7 117.3" id="16,6" style=""></path><path d="M 147.5 87.9 L 147.5 100.5 L 224.7 100.5" id="15,7" style=""></path><path d="M 186.1 75.2 L 186.1 83.7 L 224.7 83.7" id="14,8" style=""></path><path d="M 186.1 75.2 L 186.1 66.8 L 224.7 66.8" id="14,9" style=""></path><path d="M 70.3 205.6 L 70.3 193.0 L 108.9 193.0" id="11,10" style=""></path><path d="M 51.0 165.2 L 51.0 205.6 L 70.3 205.6" id="18,11" style=""></path><path d="M 108.9 146.7 L 108.9 159.4 L 147.5 159.4" id="13,12" style=""></path><path d="M 70.3 124.7 L 70.3 146.7 L 108.9 146.7" id="17,13" style=""></path><path d="M 147.5 87.9 L 147.5 75.2 L 186.1 75.2" id="15,14" style=""></path><path d="M 108.9 102.6 L 108.9 87.9 L 147.5 87.9" id="16,15" style=""></path><path d="M 70.3 124.7 L 70.3 102.6 L 108.9 102.6" id="17,16" style=""></path><path d="M 51.0 165.2 L 51.0 124.7 L 70.3 124.7" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.728,218.257)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.728,201.431)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.728,184.606)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.728,167.78)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.728,150.954)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.728,134.129)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.728,117.303)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.728,100.477)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.728,83.6514)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(224.728,66.8257)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g><g class="toyplot-coordinates-Axis" id="t55400bd49ab54429bb10a684f4438fd8" transform="translate(50.0,225.0)translate(0,15.0)"><line x1="0.8823477508955642" y1="0" x2="177.35189793001217" y2="0" style=""></line><g><g transform="translate(0.8823477508955642,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-4</text></g><g transform="translate(44.99973529567471,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-3</text></g><g transform="translate(89.11712284045386,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-2</text></g><g transform="translate(133.23451038523302,6)"><text x="-4.445" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-1</text></g><g transform="translate(177.35189793001217,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g><g class="toyplot-coordinates-Axis" id="t9f7819d3caf54b71918c3d4cf8339fa2" transform="translate(50.0,225.0)rotate(-90.0)translate(0,-15.0)"><line x1="6.6525871172122395" y1="0" x2="168.34741288278775" y2="0" style=""></line><g><g transform="translate(6.6525871172122395,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(60.550862372404076,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(114.44913762759592,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">6</text></g><g transform="translate(168.34741288278775,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">9</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="t125d65804c414584b817b11e1fa7eb82"><clipPath id="t881f5ad0bf5c41c0bac86cbafbf510ca"><rect x="0" y="0" width="300.0" height="275.0"></rect></clipPath><g clip-path="url(#t881f5ad0bf5c41c0bac86cbafbf510ca)"><g class="toyplot-mark-FillBoundaries" style="fill:rgb(96.9%,69%,69%);fill-opacity:1.0;stroke:none" id="t135dfb8c3bab4a00806ce1b996631641"><polygon points="35.0,35.000000000000014 265.0,35.000000000000014 265.0,240.00000000000003 35.0,240.00000000000003" style="fill:rgb(96.9%,69%,69%);fill-opacity:1.0;opacity:0.25;stroke:none"></polygon></g><g class="toyplot-mark-FillBoundaries" style="fill:rgb(72.2%,89%,69.4%);fill-opacity:1.0;stroke:none" id="tc68113aa409e475c9a4795aa08b2ad73"><polygon points="49.98455455342282,59.62570169474669 250.3964537227438,59.62570169474669 250.3964537227438,225.4570169474668 49.98455455342282,225.4570169474668" style="fill:rgb(72.2%,89%,69.4%);fill-opacity:1.0;opacity:0.25;stroke:none"></polygon></g><g class="toyplot-mark-FillBoundaries" style="fill:rgb(70.2%,83.5%,94.9%);fill-opacity:1.0;stroke:none" id="t00c067d5c98141f6aa6d05017a82133a"><polygon points="50.0,49.999999999999986 250.0,49.999999999999986 250.0,224.99999999999997 50.0,224.99999999999997" style="fill:rgb(70.2%,83.5%,94.9%);fill-opacity:1.0;opacity:0.25;stroke:none"></polygon></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t5f067b89ce9d481e90bd80e65fc552cb";
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
        })(modules["toyplot.coordinates.Axis"],"t55400bd49ab54429bb10a684f4438fd8",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.5133600000000005, "min": -4.02}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"t9f7819d3caf54b71918c3d4cf8339fa2",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 9.370285714285714, "min": -0.3702857142857137}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 175.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>

