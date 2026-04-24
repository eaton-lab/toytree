<div class="nb-md-page-hook" aria-hidden="true"></div>

# Tree Styles
There are innumerous ways to style toytree drawings by combining different arguments to the `.draw` function. As a convenience, we also provide a number of pre-built tree styles that represent collections of style arguments that can be set using a single command.


```python
import toytree
tree = toytree.rtree.bdtree(ntips=10, seed=123)
```

## Builtins

### Simple (``s``)
The ``s`` style is useful for evaluating tree data. It sets `use_edge_lengths=False` to align tips and space and internal edges to make it easy to read the topology regardless of variatio in edge lengths. Nodes are labeled by "idx" number, and ``node_hover=True`` is set to show all node data when a cursor is hovered over a tree node.


```python
tree.draw(tree_style='s');  # simple-style
```


<div class="toyplot" id="t781fdae2845749389597ed2362e49bc2" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="318.5px" viewBox="0 0 300.0 318.5" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t20879ca7555b4471af4ed76fddd4d2d2"><g class="toyplot-coordinates-Cartesian" id="tc9bde3dd481349aabb16cf4badfbcb7a"><clipPath id="t3684c0638bb642c5a4b20e3fda839f04"><rect x="35.0" y="35.0" width="230.0" height="248.5"></rect></clipPath><g clip-path="url(#t3684c0638bb642c5a4b20e3fda839f04)"></g></g><g class="toyplot-coordinates-Cartesian" id="tcb409eba81f443998ecc24c4e10bcd81"><clipPath id="t5083f107c59543618ba38b55ca35db2c"><rect x="35.0" y="35.0" width="230.0" height="248.5"></rect></clipPath><g clip-path="url(#t5083f107c59543618ba38b55ca35db2c)"><g class="toytree-mark-Toytree" id="tcabcc2b226504ce89c588d541ad63a07"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 142.0 242.4 L 142.0 259.0 L 224.4 259.0" id="11,0" style=""></path><path d="M 183.2 225.8 L 183.2 236.8 L 224.4 236.8" id="10,1" style=""></path><path d="M 183.2 225.8 L 183.2 214.7 L 224.4 214.7" id="10,2" style=""></path><path d="M 183.2 181.4 L 183.2 192.5 L 224.4 192.5" id="12,3" style=""></path><path d="M 183.2 181.4 L 183.2 170.3 L 224.4 170.3" id="12,4" style=""></path><path d="M 183.2 137.1 L 183.2 148.2 L 224.4 148.2" id="13,5" style=""></path><path d="M 183.2 137.1 L 183.2 126.0 L 224.4 126.0" id="13,6" style=""></path><path d="M 142.0 87.2 L 142.0 103.8 L 224.4 103.8" id="16,7" style=""></path><path d="M 183.2 70.6 L 183.2 81.7 L 224.4 81.7" id="15,8" style=""></path><path d="M 183.2 70.6 L 183.2 59.5 L 224.4 59.5" id="15,9" style=""></path><path d="M 142.0 242.4 L 142.0 225.8 L 183.2 225.8" id="11,10" style=""></path><path d="M 59.5 182.8 L 59.5 242.4 L 142.0 242.4" id="18,11" style=""></path><path d="M 142.0 159.2 L 142.0 181.4 L 183.2 181.4" id="14,12" style=""></path><path d="M 142.0 159.2 L 142.0 137.1 L 183.2 137.1" id="14,13" style=""></path><path d="M 100.7 123.2 L 100.7 159.2 L 142.0 159.2" id="17,14" style=""></path><path d="M 142.0 87.2 L 142.0 70.6 L 183.2 70.6" id="16,15" style=""></path><path d="M 100.7 123.2 L 100.7 87.2 L 142.0 87.2" id="17,16" style=""></path><path d="M 59.5 182.8 L 59.5 123.2 L 100.7 123.2" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(224.447,259.006)"><circle r="8.0"></circle></g><g id="Node-1" transform="translate(224.447,236.838)"><circle r="8.0"></circle></g><g id="Node-2" transform="translate(224.447,214.67)"><circle r="8.0"></circle></g><g id="Node-3" transform="translate(224.447,192.502)"><circle r="8.0"></circle></g><g id="Node-4" transform="translate(224.447,170.334)"><circle r="8.0"></circle></g><g id="Node-5" transform="translate(224.447,148.166)"><circle r="8.0"></circle></g><g id="Node-6" transform="translate(224.447,125.998)"><circle r="8.0"></circle></g><g id="Node-7" transform="translate(224.447,103.83)"><circle r="8.0"></circle></g><g id="Node-8" transform="translate(224.447,81.6622)"><circle r="8.0"></circle></g><g id="Node-9" transform="translate(224.447,59.4943)"><circle r="8.0"></circle></g><g id="Node-10" transform="translate(183.2,225.754)"><circle r="8.0"></circle></g><g id="Node-11" transform="translate(141.952,242.38)"><circle r="8.0"></circle></g><g id="Node-12" transform="translate(183.2,181.418)"><circle r="8.0"></circle></g><g id="Node-13" transform="translate(183.2,137.082)"><circle r="8.0"></circle></g><g id="Node-14" transform="translate(141.952,159.25)"><circle r="8.0"></circle></g><g id="Node-15" transform="translate(183.2,70.5783)"><circle r="8.0"></circle></g><g id="Node-16" transform="translate(141.952,87.2042)"><circle r="8.0"></circle></g><g id="Node-17" transform="translate(100.705,123.227)"><circle r="8.0"></circle></g><g id="Node-18" transform="translate(59.4574,182.803)"><circle r="8.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(224.447,259.006)"><title>idx: 0
dist: 1.60125467529
support: nan
height: 0
name: r0</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(224.447,236.838)"><title>idx: 1
dist: 0.195254716064
support: nan
height: 0
name: r1</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(224.447,214.67)"><title>idx: 2
dist: 0.195254716064
support: nan
height: 0
name: r2</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(224.447,192.502)"><title>idx: 3
dist: 0.213535884496
support: nan
height: 0
name: r3</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(224.447,170.334)"><title>idx: 4
dist: 0.213535884496
support: nan
height: 0
name: r4</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(224.447,148.166)"><title>idx: 5
dist: 0.1532383712
support: nan
height: 0
name: r5</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(224.447,125.998)"><title>idx: 6
dist: 0.1532383712
support: nan
height: 0
name: r6</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(224.447,103.83)"><title>idx: 7
dist: 0.778722829837
support: nan
height: 0
name: r7</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(224.447,81.6622)"><title>idx: 8
dist: 0.600849520663
support: nan
height: 0
name: r8</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(224.447,59.4943)"><title>idx: 9
dist: 0.600849520663
support: nan
height: 0
name: r9</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(183.2,225.754)"><title>idx: 10
dist: 1.40599995922
support: nan
height: 0.195254716064
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(141.952,242.38)"><title>idx: 11
dist: 0.125897349747
support: nan
height: 1.60125467529
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(183.2,181.418)"><title>idx: 12
dist: 0.115592406821
support: nan
height: 0.213535884496
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(183.2,137.082)"><title>idx: 13
dist: 0.175889920117
support: nan
height: 0.1532383712
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(141.952,159.25)"><title>idx: 14
dist: 0.488252765456
support: nan
height: 0.329128291317
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g><g class="toytree-NodeLabel" transform="translate(183.2,70.5783)"><title>idx: 15
dist: 0.177873309174
support: nan
height: 0.600849520663
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">15</text></g><g class="toytree-NodeLabel" transform="translate(141.952,87.2042)"><title>idx: 16
dist: 0.0386582269365
support: nan
height: 0.778722829837
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">16</text></g><g class="toytree-NodeLabel" transform="translate(100.705,123.227)"><title>idx: 17
dist: 0.90977096826
support: nan
height: 0.817381056773
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">17</text></g><g class="toytree-NodeLabel" transform="translate(59.4574,182.803)"><title>idx: 18
dist: 0.596972495123
support: nan
height: 1.72715202503
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">18</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.447,259.006)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.447,236.838)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.447,214.67)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.447,192.502)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.447,170.334)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.447,148.166)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.447,125.998)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.447,103.83)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.447,81.6622)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(224.447,59.4943)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


### Coalescent (``c``)
The ``c`` style shows a tree in the typical form for coalescent trees, with downward facing layout, a scale bar, and small node markers. It is useful for evaluating variation in edge lengths and topology.


```python
tree.draw(tree_style='c');  # coalescent-style
```


<div class="toyplot" id="te97cd90bfd9c43f58c50c440169396b4" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t0350aa469c5f4aa0ae0174a6b7e88228"><g class="toyplot-coordinates-Cartesian" id="tb24bb34738a2440da502b8ef9b2f1d72"><clipPath id="t827d576cfaa14179a8e9c2c480046d0f"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t827d576cfaa14179a8e9c2c480046d0f)"></g><g class="toyplot-coordinates-Axis" id="t304f908bd9914e32a10ce0f3e66b0b20" transform="translate(50.0,250.0)rotate(-90.0)translate(0,-15.0)"><line x1="22.293203075840935" y1="0" x2="195.08267092909813" y2="0" style=""></line><g><line x1="22.293203075840935" y1="0" x2="22.293203075840935" y2="5" style=""></line><line x1="72.31470244267017" y1="0" x2="72.31470244267017" y2="5" style=""></line><line x1="122.33620180949943" y1="0" x2="122.33620180949943" y2="5" style=""></line><line x1="172.35770117632865" y1="0" x2="172.35770117632865" y2="5" style=""></line></g><g><g transform="translate(22.293203075840935,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(72.31470244267017,-6)"><text x="-6.95" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.5</text></g><g transform="translate(122.33620180949943,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(172.35770117632865,-6)"><text x="-6.95" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1.5</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="t0e470174e0ec4304a9eca7d3eb8b2c0b"><clipPath id="t9b93d786c3714b4d88cb17a25a0824b8"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t9b93d786c3714b4d88cb17a25a0824b8)"><g class="toytree-mark-Toytree" id="td76966ee32e24be2a72e481b0ddc3a73"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 72.6 67.5 L 57.2 227.7" id="11,0" style=""></path><path d="M 88.1 208.2 L 77.8 227.7" id="10,1" style=""></path><path d="M 88.1 208.2 L 98.4 227.7" id="10,2" style=""></path><path d="M 129.4 206.3 L 119.1 227.7" id="12,3" style=""></path><path d="M 129.4 206.3 L 139.7 227.7" id="12,4" style=""></path><path d="M 170.6 212.4 L 160.3 227.7" id="13,5" style=""></path><path d="M 170.6 212.4 L 180.9 227.7" id="13,6" style=""></path><path d="M 217.0 149.8 L 201.6 227.7" id="16,7" style=""></path><path d="M 232.5 167.6 L 222.2 227.7" id="15,8" style=""></path><path d="M 232.5 167.6 L 242.8 227.7" id="15,9" style=""></path><path d="M 72.6 67.5 L 88.1 208.2" id="11,10" style=""></path><path d="M 128.1 54.9 L 72.6 67.5" id="18,11" style=""></path><path d="M 150.0 194.8 L 129.4 206.3" id="14,12" style=""></path><path d="M 150.0 194.8 L 170.6 212.4" id="14,13" style=""></path><path d="M 183.5 145.9 L 150.0 194.8" id="17,14" style=""></path><path d="M 217.0 149.8 L 232.5 167.6" id="16,15" style=""></path><path d="M 183.5 145.9 L 217.0 149.8" id="17,16" style=""></path><path d="M 128.1 54.9 L 183.5 145.9" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(57.1653,227.707)"><circle r="3.5"></circle></g><g id="Node-1" transform="translate(77.7953,227.707)"><circle r="3.5"></circle></g><g id="Node-2" transform="translate(98.4252,227.707)"><circle r="3.5"></circle></g><g id="Node-3" transform="translate(119.055,227.707)"><circle r="3.5"></circle></g><g id="Node-4" transform="translate(139.685,227.707)"><circle r="3.5"></circle></g><g id="Node-5" transform="translate(160.315,227.707)"><circle r="3.5"></circle></g><g id="Node-6" transform="translate(180.945,227.707)"><circle r="3.5"></circle></g><g id="Node-7" transform="translate(201.575,227.707)"><circle r="3.5"></circle></g><g id="Node-8" transform="translate(222.205,227.707)"><circle r="3.5"></circle></g><g id="Node-9" transform="translate(242.835,227.707)"><circle r="3.5"></circle></g><g id="Node-10" transform="translate(88.1102,208.173)"><circle r="3.5"></circle></g><g id="Node-11" transform="translate(72.6378,67.5125)"><circle r="3.5"></circle></g><g id="Node-12" transform="translate(129.37,206.344)"><circle r="3.5"></circle></g><g id="Node-13" transform="translate(170.63,212.376)"><circle r="3.5"></circle></g><g id="Node-14" transform="translate(150,194.78)"><circle r="3.5"></circle></g><g id="Node-15" transform="translate(232.52,167.596)"><circle r="3.5"></circle></g><g id="Node-16" transform="translate(217.047,149.801)"><circle r="3.5"></circle></g><g id="Node-17" transform="translate(183.524,145.934)"><circle r="3.5"></circle></g><g id="Node-18" transform="translate(128.081,54.9173)"><circle r="3.5"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(57.1653,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(77.7953,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(98.4252,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(119.055,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(139.685,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(160.315,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(180.945,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(201.575,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(222.205,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(242.835,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t0350aa469c5f4aa0ae0174a6b7e88228";
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
        })(modules["toyplot.coordinates.Axis"],"t304f908bd9914e32a10ce0f3e66b0b20",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 1.7763041809378648, "min": -0.2228362140082533}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


### R-style (``r``)
The ``r`` style is meant to look similar to the classic trees in the R package ape. Light grey rectangle markers are shown on internal nodes with the 'name' feature shown on node labels. The example below assigns a name to one internal node to demonstrate.


```python
tree.set_node_data("name", {17: "XXX"}).draw(tree_style='r');  # R-style
```


<div class="toyplot" id="t014770e1079a47c98ace8eb17a57249f" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="318.5px" viewBox="0 0 300.0 318.5" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t3251dbd0375742e08e811b2af5278165"><g class="toyplot-coordinates-Cartesian" id="tf0590ab53de4430da6a017ac0c8297d5"><clipPath id="t62bed074a2354b4c8e9aa484d4e0c73f"><rect x="35.0" y="35.0" width="230.0" height="248.5"></rect></clipPath><g clip-path="url(#t62bed074a2354b4c8e9aa484d4e0c73f)"></g></g><g class="toyplot-coordinates-Cartesian" id="t83c7489ae58646d798371aab5d5ce9e0"><clipPath id="t8133a2ef1b504b77880acdf26e7687ed"><rect x="35.0" y="35.0" width="230.0" height="248.5"></rect></clipPath><g clip-path="url(#t8133a2ef1b504b77880acdf26e7687ed)"><g class="toytree-mark-Toytree" id="td77ee713a7e24aeda40cf1075a1d4de7"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 78.7 242.4 L 78.7 259.0 L 222.8 259.0" id="11,0" style=""></path><path d="M 205.2 225.8 L 205.2 236.8 L 222.8 236.8" id="10,1" style=""></path><path d="M 205.2 225.8 L 205.2 214.7 L 222.8 214.7" id="10,2" style=""></path><path d="M 203.6 181.4 L 203.6 192.5 L 222.8 192.5" id="12,3" style=""></path><path d="M 203.6 181.4 L 203.6 170.3 L 222.8 170.3" id="12,4" style=""></path><path d="M 209.0 137.1 L 209.0 148.2 L 222.8 148.2" id="13,5" style=""></path><path d="M 209.0 137.1 L 209.0 126.0 L 222.8 126.0" id="13,6" style=""></path><path d="M 152.7 87.2 L 152.7 103.8 L 222.8 103.8" id="16,7" style=""></path><path d="M 168.7 70.6 L 168.7 81.7 L 222.8 81.7" id="15,8" style=""></path><path d="M 168.7 70.6 L 168.7 59.5 L 222.8 59.5" id="15,9" style=""></path><path d="M 78.7 242.4 L 78.7 225.8 L 205.2 225.8" id="11,10" style=""></path><path d="M 67.3 182.8 L 67.3 242.4 L 78.7 242.4" id="18,11" style=""></path><path d="M 193.2 159.2 L 193.2 181.4 L 203.6 181.4" id="14,12" style=""></path><path d="M 193.2 159.2 L 193.2 137.1 L 209.0 137.1" id="14,13" style=""></path><path d="M 149.2 123.2 L 149.2 159.2 L 193.2 159.2" id="17,14" style=""></path><path d="M 152.7 87.2 L 152.7 70.6 L 168.7 70.6" id="16,15" style=""></path><path d="M 149.2 123.2 L 149.2 87.2 L 152.7 87.2" id="17,16" style=""></path><path d="M 67.3 182.8 L 67.3 123.2 L 149.2 123.2" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-10" transform="translate(205.222,225.754)"><rect x="-16.0" y="-8.0" width="32.0" height="16.0"></rect></g><g id="Node-11" transform="translate(78.6769,242.38)"><rect x="-16.0" y="-8.0" width="32.0" height="16.0"></rect></g><g id="Node-12" transform="translate(203.577,181.418)"><rect x="-16.0" y="-8.0" width="32.0" height="16.0"></rect></g><g id="Node-13" transform="translate(209.004,137.082)"><rect x="-16.0" y="-8.0" width="32.0" height="16.0"></rect></g><g id="Node-14" transform="translate(193.173,159.25)"><rect x="-16.0" y="-8.0" width="32.0" height="16.0"></rect></g><g id="Node-15" transform="translate(168.717,70.5783)"><rect x="-16.0" y="-8.0" width="32.0" height="16.0"></rect></g><g id="Node-16" transform="translate(152.708,87.2042)"><rect x="-16.0" y="-8.0" width="32.0" height="16.0"></rect></g><g id="Node-17" transform="translate(149.229,123.227)"><rect x="-16.0" y="-8.0" width="32.0" height="16.0"></rect></g><g id="Node-18" transform="translate(67.3456,182.803)"><rect x="-16.0" y="-8.0" width="32.0" height="16.0"></rect></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(205.222,225.754)"></g><g class="toytree-NodeLabel" transform="translate(78.6769,242.38)"></g><g class="toytree-NodeLabel" transform="translate(203.577,181.418)"></g><g class="toytree-NodeLabel" transform="translate(209.004,137.082)"></g><g class="toytree-NodeLabel" transform="translate(193.173,159.25)"></g><g class="toytree-NodeLabel" transform="translate(168.717,70.5783)"></g><g class="toytree-NodeLabel" transform="translate(152.708,87.2042)"></g><g class="toytree-NodeLabel" transform="translate(149.229,123.227)"><text x="-9.004499999999998" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">XXX</text></g><g class="toytree-NodeLabel" transform="translate(67.3456,182.803)"></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:14px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(222.796,259.006)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(222.796,236.838)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(222.796,214.67)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(222.796,192.502)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(222.796,170.334)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(222.796,148.166)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(222.796,125.998)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(222.796,103.83)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(222.796,81.6622)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(222.796,59.4943)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


### Population (``p``)
The ``p`` style is used to represent species or population trees in population genetics. It has a similar style to ``ts='c'``, but shows 'idx' labels on nodes. Its main difference is that looks for a data feature named "Ne", and if present, it scales the edge widths to match the relative variation in Ne values. The example below sets Ne on a few nodes to demonstrate.


```python
tree.set_node_data("Ne", {i: 1000 for i in [0, 1, 2, 10]}, default=500).draw(tree_style='p');  # population-style
```


<div class="toyplot" id="t9f457a66aea94196854d64070250eba7" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t90ef3ce3a6944c51bb35c3c46664e7f9"><g class="toyplot-coordinates-Cartesian" id="t49d91ee4a050468eab6251735429ad2c"><clipPath id="tba6075fa59fc437bbc20ba2b836ada2a"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#tba6075fa59fc437bbc20ba2b836ada2a)"></g><g class="toyplot-coordinates-Axis" id="t27a69b2d1f99455f8834283736db10df" transform="translate(50.0,250.0)rotate(-90.0)translate(0,-15.0)"><line x1="25.56178908041747" y1="0" x2="191.53517191898285" y2="0" style=""></line><g><line x1="25.56178908041747" y1="0" x2="25.56178908041747" y2="5" style=""></line><line x1="73.6100733173974" y1="0" x2="73.6100733173974" y2="5" style=""></line><line x1="121.6583575543773" y1="0" x2="121.6583575543773" y2="5" style=""></line><line x1="169.70664179135724" y1="0" x2="169.70664179135724" y2="5" style=""></line></g><g><g transform="translate(25.56178908041747,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(73.6100733173974,-6)"><text x="-6.95" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.5</text></g><g transform="translate(121.6583575543773,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(169.70664179135724,-6)"><text x="-6.95" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1.5</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g><g class="toyplot-coordinates-Cartesian" id="t55790e093ad14008b515aef3c0956776"><clipPath id="t273cf7783d414213846d6c8734b487c1"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#t273cf7783d414213846d6c8734b487c1)"><g class="toytree-mark-Toytree" id="t5403b0d78b3f43cca7d461180ecf6164"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 73.7 70.6 L 58.5 224.4" id="11,0" style="stroke-width:6.0"></path><path d="M 89.0 205.7 L 78.8 224.4" id="10,1" style="stroke-width:6.0"></path><path d="M 89.0 205.7 L 99.2 224.4" id="10,2" style="stroke-width:6.0"></path><path d="M 129.7 203.9 L 119.5 224.4" id="12,3" style="stroke-width:2.0"></path><path d="M 129.7 203.9 L 139.8 224.4" id="12,4" style="stroke-width:2.0"></path><path d="M 170.3 209.7 L 160.2 224.4" id="13,5" style="stroke-width:2.0"></path><path d="M 170.3 209.7 L 180.5 224.4" id="13,6" style="stroke-width:2.0"></path><path d="M 216.1 149.6 L 200.8 224.4" id="16,7" style="stroke-width:2.0"></path><path d="M 231.3 166.7 L 221.2 224.4" id="15,8" style="stroke-width:2.0"></path><path d="M 231.3 166.7 L 241.5 224.4" id="15,9" style="stroke-width:2.0"></path><path d="M 73.7 70.6 L 89.0 205.7" id="11,10" style="stroke-width:6.0"></path><path d="M 128.4 58.5 L 73.7 70.6" id="18,11" style="stroke-width:2.0"></path><path d="M 150.0 192.8 L 129.7 203.9" id="14,12" style="stroke-width:2.0"></path><path d="M 150.0 192.8 L 170.3 209.7" id="14,13" style="stroke-width:2.0"></path><path d="M 183.0 145.9 L 150.0 192.8" id="17,14" style="stroke-width:2.0"></path><path d="M 216.1 149.6 L 231.3 166.7" id="16,15" style="stroke-width:2.0"></path><path d="M 183.0 145.9 L 216.1 149.6" id="17,16" style="stroke-width:2.0"></path><path d="M 128.4 58.5 L 183.0 145.9" id="18,17" style="stroke-width:2.0"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.0"><g id="Node-0" transform="translate(58.4952,224.438)"><circle r="7.5"></circle></g><g id="Node-1" transform="translate(78.8296,224.438)"><circle r="7.5"></circle></g><g id="Node-2" transform="translate(99.164,224.438)"><circle r="7.5"></circle></g><g id="Node-3" transform="translate(119.498,224.438)"><circle r="7.5"></circle></g><g id="Node-4" transform="translate(139.833,224.438)"><circle r="7.5"></circle></g><g id="Node-5" transform="translate(160.167,224.438)"><circle r="7.5"></circle></g><g id="Node-6" transform="translate(180.502,224.438)"><circle r="7.5"></circle></g><g id="Node-7" transform="translate(200.836,224.438)"><circle r="7.5"></circle></g><g id="Node-8" transform="translate(221.17,224.438)"><circle r="7.5"></circle></g><g id="Node-9" transform="translate(241.505,224.438)"><circle r="7.5"></circle></g><g id="Node-10" transform="translate(88.9968,205.675)"><circle r="7.5"></circle></g><g id="Node-11" transform="translate(73.746,70.5631)"><circle r="7.5"></circle></g><g id="Node-12" transform="translate(129.666,203.918)"><circle r="7.5"></circle></g><g id="Node-13" transform="translate(170.334,209.713)"><circle r="7.5"></circle></g><g id="Node-14" transform="translate(150,192.81)"><circle r="7.5"></circle></g><g id="Node-15" transform="translate(231.338,166.699)"><circle r="7.5"></circle></g><g id="Node-16" transform="translate(216.087,149.606)"><circle r="7.5"></circle></g><g id="Node-17" transform="translate(183.043,145.891)"><circle r="7.5"></circle></g><g id="Node-18" transform="translate(128.395,58.4648)"><circle r="7.5"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(58.4952,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(78.8296,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(99.164,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(119.498,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(139.833,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(160.167,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(180.502,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(200.836,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(221.17,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(241.505,224.438)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(88.9968,205.675)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(73.746,70.5631)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(129.666,203.918)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(170.334,209.713)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(150,192.81)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g><g class="toytree-NodeLabel" transform="translate(231.338,166.699)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">15</text></g><g class="toytree-NodeLabel" transform="translate(216.087,149.606)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">16</text></g><g class="toytree-NodeLabel" transform="translate(183.043,145.891)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">17</text></g><g class="toytree-NodeLabel" transform="translate(128.395,58.4648)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">18</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(58.4952,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(78.8296,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(99.164,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(119.498,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(139.833,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(160.167,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(180.502,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(200.836,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(221.17,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(241.505,224.438)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t90ef3ce3a6944c51bb35c3c46664e7f9";
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
        })(modules["toyplot.coordinates.Axis"],"t27a69b2d1f99455f8834283736db10df",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 1.8152387092453948, "min": -0.26600106004143304}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


### Dark (``d``)
The ``d`` style provides a 'dark mode' base tree style is easy to read on dark backgrounds.


```python
tree.draw(tree_style='d');  # dark-style
```


<div class="toyplot" id="te304892e2e8444f09847bb4cff0fc53f" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t2684b9ae8cb6476dbaef41f7f56d637e"><g class="toyplot-coordinates-Cartesian" id="t3a8800c06059458bb07fce0b82acea76"><clipPath id="tf40f6c72d3e34594a72004e490872c1e"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tf40f6c72d3e34594a72004e490872c1e)"></g></g><g class="toyplot-coordinates-Cartesian" id="tbe19cae2243649b4835062aa218a3de7"><clipPath id="tc492070faaf946fdb5405b4d8d5f9ef7"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tc492070faaf946fdb5405b4d8d5f9ef7)"><g class="toytree-mark-Toytree" id="tcf1831f1c237474aae9ad84c11980968"><g class="toytree-Edges" style="stroke:rgb(40.0%,76.1%,64.7%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 64.1 204.5 L 64.1 217.8 L 231.5 217.8" id="11,0" style=""></path><path d="M 211.1 191.1 L 211.1 200.0 L 231.5 200.0" id="10,1" style=""></path><path d="M 211.1 191.1 L 211.1 182.1 L 231.5 182.1" id="10,2" style=""></path><path d="M 209.2 155.4 L 209.2 164.3 L 231.5 164.3" id="12,3" style=""></path><path d="M 209.2 155.4 L 209.2 146.4 L 231.5 146.4" id="12,4" style=""></path><path d="M 215.5 119.6 L 215.5 128.6 L 231.5 128.6" id="13,5" style=""></path><path d="M 215.5 119.6 L 215.5 110.7 L 231.5 110.7" id="13,6" style=""></path><path d="M 150.1 79.5 L 150.1 92.9 L 231.5 92.9" id="16,7" style=""></path><path d="M 168.7 66.1 L 168.7 75.0 L 231.5 75.0" id="15,8" style=""></path><path d="M 168.7 66.1 L 168.7 57.2 L 231.5 57.2" id="15,9" style=""></path><path d="M 64.1 204.5 L 64.1 191.1 L 211.1 191.1" id="11,10" style=""></path><path d="M 51.0 156.5 L 51.0 204.5 L 64.1 204.5" id="18,11" style=""></path><path d="M 197.1 137.5 L 197.1 155.4 L 209.2 155.4" id="14,12" style=""></path><path d="M 197.1 137.5 L 197.1 119.6 L 215.5 119.6" id="14,13" style=""></path><path d="M 146.1 108.5 L 146.1 137.5 L 197.1 137.5" id="17,14" style=""></path><path d="M 150.1 79.5 L 150.1 66.1 L 168.7 66.1" id="16,15" style=""></path><path d="M 146.1 108.5 L 146.1 79.5 L 150.1 79.5" id="17,16" style=""></path><path d="M 51.0 156.5 L 51.0 108.5 L 146.1 108.5" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:none;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(231.495,217.845)"><text x="8.0" y="3.066" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(231.495,199.99)"><text x="8.0" y="3.066" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(231.495,182.136)"><text x="8.0" y="3.066" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(231.495,164.282)"><text x="8.0" y="3.066" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(231.495,146.427)"><text x="8.0" y="3.066" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(231.495,128.573)"><text x="8.0" y="3.066" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(231.495,110.718)"><text x="8.0" y="3.066" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(231.495,92.864)"><text x="8.0" y="3.066" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(231.495,75.0096)"><text x="8.0" y="3.066" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(231.495,57.1552)"><text x="8.0" y="3.066" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


### Bootstrap (``b``)
The bootstrap style uses the 'support' feature to map edge widths to thicker values for higher supported edges.


```python
supports = dict(zip(range(10, 17), [100, 50, 100, 100, 100, 100, 100, ]))
tree.set_node_data('support', supports).draw(tree_style='b');  # boostrap-style
```


<div class="toyplot" id="td8e7757c70c5467b880967b1045c8f4a" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t9651208c962d4c68a22c7f17987fa8cd"><g class="toyplot-coordinates-Cartesian" id="td8ae0e906fcc4b23882ffa606bc45d55"><clipPath id="t3c58b5a1d21a4e4b87b375bb37b672c2"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t3c58b5a1d21a4e4b87b375bb37b672c2)"></g></g><g class="toyplot-coordinates-Cartesian" id="t2f41e7917e02465a9be5ecc2be8dfd57"><clipPath id="t0371180b022c487080c097181565da5c"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t0371180b022c487080c097181565da5c)"><g class="toytree-mark-Toytree" id="t70559e6876864b9d8a4fec92f6ed5851"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 63.4 204.5 L 63.4 217.8 L 224.7 217.8" id="11,0" style="stroke-width:1.5"></path><path d="M 205.1 191.1 L 205.1 200.0 L 224.7 200.0" id="10,1" style="stroke-width:1.5"></path><path d="M 205.1 191.1 L 205.1 182.1 L 224.7 182.1" id="10,2" style="stroke-width:1.5"></path><path d="M 203.2 155.4 L 203.2 164.3 L 224.7 164.3" id="12,3" style="stroke-width:1.5"></path><path d="M 203.2 155.4 L 203.2 146.4 L 224.7 146.4" id="12,4" style="stroke-width:1.5"></path><path d="M 209.3 119.6 L 209.3 128.6 L 224.7 128.6" id="13,5" style="stroke-width:1.5"></path><path d="M 209.3 119.6 L 209.3 110.7 L 224.7 110.7" id="13,6" style="stroke-width:1.5"></path><path d="M 146.3 79.5 L 146.3 92.9 L 224.7 92.9" id="16,7" style="stroke-width:1.5"></path><path d="M 164.2 66.1 L 164.2 75.0 L 224.7 75.0" id="15,8" style="stroke-width:1.5"></path><path d="M 164.2 66.1 L 164.2 57.2 L 224.7 57.2" id="15,9" style="stroke-width:1.5"></path><path d="M 63.4 204.5 L 63.4 191.1 L 205.1 191.1" id="11,10" style="stroke-width:4.0"></path><path d="M 50.7 156.5 L 50.7 204.5 L 63.4 204.5" id="18,11" style="stroke-width:1.5"></path><path d="M 191.6 137.5 L 191.6 155.4 L 203.2 155.4" id="14,12" style="stroke-width:4.0"></path><path d="M 191.6 137.5 L 191.6 119.6 L 209.3 119.6" id="14,13" style="stroke-width:4.0"></path><path d="M 142.4 108.5 L 142.4 137.5 L 191.6 137.5" id="17,14" style="stroke-width:4.0"></path><path d="M 146.3 79.5 L 146.3 66.1 L 164.2 66.1" id="16,15" style="stroke-width:4.0"></path><path d="M 142.4 108.5 L 142.4 79.5 L 146.3 79.5" id="17,16" style="stroke-width:4.0"></path><path d="M 50.7 156.5 L 50.7 108.5 L 142.4 108.5" id="18,17" style="stroke-width:1.5"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.722,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.722,199.99)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.722,182.136)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.722,164.282)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.722,146.427)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.722,128.573)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.722,110.718)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.722,92.864)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.722,75.0096)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(224.722,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


### Umlaut (``u``)
Just a visually interesting style.


```python
tree.draw(tree_style='o');  # umlaut-style
```


<div class="toyplot" id="t32c84b6f00a7473d91f3ed929dcbbaba" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t0e399006ebf04c768a96e50f0dec0c3b"><g class="toyplot-coordinates-Cartesian" id="tad2b4a53e6544d9ea137fbd5625a1e79"><clipPath id="t20dcb94b17c342ac9ff273eb61460825"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t20dcb94b17c342ac9ff273eb61460825)"></g></g><g class="toyplot-coordinates-Cartesian" id="tcc841b401925467585b94f6fce8d5ae6"><clipPath id="tea3bac58d5f6465aa03d716ef472b5c9"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tea3bac58d5f6465aa03d716ef472b5c9)"><g class="toytree-mark-Toytree" id="tb0310273887c48a691723d813c799e55"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 67.8 204.4 L 224.4 217.8" id="11,0" style=""></path><path d="M 205.3 191.0 L 224.4 200.0" id="10,1" style=""></path><path d="M 205.3 191.0 L 224.4 182.1" id="10,2" style=""></path><path d="M 203.5 155.3 L 224.4 164.3" id="12,3" style=""></path><path d="M 203.5 155.3 L 224.4 146.4" id="12,4" style=""></path><path d="M 209.4 119.7 L 224.4 128.6" id="13,5" style=""></path><path d="M 209.4 119.7 L 224.4 110.7" id="13,6" style=""></path><path d="M 148.2 79.5 L 224.4 92.9" id="16,7" style=""></path><path d="M 165.6 66.1 L 224.4 75.0" id="15,8" style=""></path><path d="M 165.6 66.1 L 224.4 57.2" id="15,9" style=""></path><path d="M 67.8 204.4 L 205.3 191.0" id="11,10" style=""></path><path d="M 55.5 156.5 L 67.8 204.4" id="18,11" style=""></path><path d="M 192.2 137.5 L 203.5 155.3" id="14,12" style=""></path><path d="M 192.2 137.5 L 209.4 119.7" id="14,13" style=""></path><path d="M 144.5 108.5 L 192.2 137.5" id="17,14" style=""></path><path d="M 148.2 79.5 L 165.6 66.1" id="16,15" style=""></path><path d="M 144.5 108.5 L 148.2 79.5" id="17,16" style=""></path><path d="M 55.5 156.5 L 144.5 108.5" id="18,17" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 224.4 217.8 L 224.4 217.8"></path><path d="M 224.4 200.0 L 224.4 200.0"></path><path d="M 224.4 182.1 L 224.4 182.1"></path><path d="M 224.4 164.3 L 224.4 164.3"></path><path d="M 224.4 146.4 L 224.4 146.4"></path><path d="M 224.4 128.6 L 224.4 128.6"></path><path d="M 224.4 110.7 L 224.4 110.7"></path><path d="M 224.4 92.9 L 224.4 92.9"></path><path d="M 224.4 75.0 L 224.4 75.0"></path><path d="M 224.4 57.2 L 224.4 57.2"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(10.6%,62.0%,46.7%);fill-opacity:1.0;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-10" transform="translate(205.316,191.036)"><circle r="4.0"></circle></g><g id="Node-11" transform="translate(67.7964,204.42)"><circle r="4.0"></circle></g><g id="Node-12" transform="translate(203.528,155.345)"><circle r="4.0"></circle></g><g id="Node-13" transform="translate(209.426,119.655)"><circle r="4.0"></circle></g><g id="Node-14" transform="translate(192.222,137.5)"><circle r="4.0"></circle></g><g id="Node-15" transform="translate(165.645,66.1189)"><circle r="4.0"></circle></g><g id="Node-16" transform="translate(148.248,79.5029)"><circle r="4.0"></circle></g><g id="Node-17" transform="translate(144.467,108.501)"><circle r="4.0"></circle></g><g id="Node-18" transform="translate(55.4824,156.461)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.414,217.804)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.414,199.958)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.414,182.113)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.414,164.268)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.414,146.423)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.414,128.577)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.414,110.732)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.414,92.8868)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.414,75.0416)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(224.414,57.1963)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Creating Tree Styles
You can create custom re-usable tree styles by passing a dictionary of style arguments to ``draw``. 


```python
# define a re-usable style dictionary
mystyle = {
    "layout": 'd',
    "edge_type": 'p',
    "edge_style": {
        "stroke": "black",
        "stroke-width": 2.5,
    },
    "tip_labels_align": True,
    "tip_labels_colors": "darkcyan",
    "tip_labels_style": {
        "font-size": "15px"
    },
    "node_labels": False,
    "node_sizes": 8,
    "node_colors": "goldenrod",
    "node_mask": False,
}

# apply the custom treestyle dict to a drawing
tree.draw(**mystyle);
```


<div class="toyplot" id="t9e1e4c9057634a0f9ccdcd376c1a2ee6" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="307.0px" height="300.0px" viewBox="0 0 307.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t309aeb111f624ff8925ff5ead7970220"><g class="toyplot-coordinates-Cartesian" id="t93d0f9996c4a46e28461c811e15ec09a"><clipPath id="tce96b39a3e774d7cac0e398a79a76c06"><rect x="35.0" y="35.0" width="237.0" height="230.0"></rect></clipPath><g clip-path="url(#tce96b39a3e774d7cac0e398a79a76c06)"></g></g><g class="toyplot-coordinates-Cartesian" id="t823c23911b304d6388cefda94bdb8713"><clipPath id="t05085878293d457091682934af82a279"><rect x="35.0" y="35.0" width="237.0" height="230.0"></rect></clipPath><g clip-path="url(#t05085878293d457091682934af82a279)"><g class="toytree-mark-Toytree" id="t20a874fc03564d1eaa07ccd2eac00eab"><g class="toytree-Edges" style="stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.5;fill:none"><path d="M 74.7 67.6 L 59.0 67.6 L 59.0 221.8" id="11,0" style=""></path><path d="M 90.5 203.0 L 80.0 203.0 L 80.0 221.8" id="10,1" style=""></path><path d="M 90.5 203.0 L 101.0 203.0 L 101.0 221.8" id="10,2" style=""></path><path d="M 132.5 201.2 L 122.0 201.2 L 122.0 221.8" id="12,3" style=""></path><path d="M 132.5 201.2 L 143.0 201.2 L 143.0 221.8" id="12,4" style=""></path><path d="M 174.5 207.0 L 164.0 207.0 L 164.0 221.8" id="13,5" style=""></path><path d="M 174.5 207.0 L 185.0 207.0 L 185.0 221.8" id="13,6" style=""></path><path d="M 221.8 146.8 L 206.0 146.8 L 206.0 221.8" id="16,7" style=""></path><path d="M 237.5 163.9 L 227.0 163.9 L 227.0 221.8" id="15,8" style=""></path><path d="M 237.5 163.9 L 248.0 163.9 L 248.0 221.8" id="15,9" style=""></path><path d="M 74.7 67.6 L 90.5 67.6 L 90.5 203.0" id="11,10" style=""></path><path d="M 131.2 55.5 L 74.7 55.5 L 74.7 67.6" id="18,11" style=""></path><path d="M 153.5 190.1 L 132.5 190.1 L 132.5 201.2" id="14,12" style=""></path><path d="M 153.5 190.1 L 174.5 190.1 L 174.5 207.0" id="14,13" style=""></path><path d="M 187.6 143.1 L 153.5 143.1 L 153.5 190.1" id="17,14" style=""></path><path d="M 221.8 146.8 L 237.5 146.8 L 237.5 163.9" id="16,15" style=""></path><path d="M 187.6 143.1 L 221.8 143.1 L 221.8 146.8" id="17,16" style=""></path><path d="M 131.2 55.5 L 187.6 55.5 L 187.6 143.1" id="18,17" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 59.0 221.8 L 59.0 221.8"></path><path d="M 80.0 221.8 L 80.0 221.8"></path><path d="M 101.0 221.8 L 101.0 221.8"></path><path d="M 122.0 221.8 L 122.0 221.8"></path><path d="M 143.0 221.8 L 143.0 221.8"></path><path d="M 164.0 221.8 L 164.0 221.8"></path><path d="M 185.0 221.8 L 185.0 221.8"></path><path d="M 206.0 221.8 L 206.0 221.8"></path><path d="M 227.0 221.8 L 227.0 221.8"></path><path d="M 248.0 221.8 L 248.0 221.8"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(85.5%,64.7%,12.5%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(58.9946,221.779)"><circle r="4.0"></circle></g><g id="Node-1" transform="translate(79.9958,221.779)"><circle r="4.0"></circle></g><g id="Node-2" transform="translate(100.997,221.779)"><circle r="4.0"></circle></g><g id="Node-3" transform="translate(121.998,221.779)"><circle r="4.0"></circle></g><g id="Node-4" transform="translate(142.999,221.779)"><circle r="4.0"></circle></g><g id="Node-5" transform="translate(164.001,221.779)"><circle r="4.0"></circle></g><g id="Node-6" transform="translate(185.002,221.779)"><circle r="4.0"></circle></g><g id="Node-7" transform="translate(206.003,221.779)"><circle r="4.0"></circle></g><g id="Node-8" transform="translate(227.004,221.779)"><circle r="4.0"></circle></g><g id="Node-9" transform="translate(248.005,221.779)"><circle r="4.0"></circle></g><g id="Node-10" transform="translate(90.4964,202.979)"><circle r="4.0"></circle></g><g id="Node-11" transform="translate(74.7455,67.6001)"><circle r="4.0"></circle></g><g id="Node-12" transform="translate(132.499,201.218)"><circle r="4.0"></circle></g><g id="Node-13" transform="translate(174.501,207.024)"><circle r="4.0"></circle></g><g id="Node-14" transform="translate(153.5,190.089)"><circle r="4.0"></circle></g><g id="Node-15" transform="translate(237.505,163.925)"><circle r="4.0"></circle></g><g id="Node-16" transform="translate(221.754,146.799)"><circle r="4.0"></circle></g><g id="Node-17" transform="translate(187.627,143.076)"><circle r="4.0"></circle></g><g id="Node-18" transform="translate(131.186,55.4779)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(0.0%,54.5%,54.5%);fill-opacity:1.0;font-family:Helvetica;font-size:15px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(58.9946,221.779)rotate(90)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(0.0%,54.5%,54.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(79.9958,221.779)rotate(90)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(0.0%,54.5%,54.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(100.997,221.779)rotate(90)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(0.0%,54.5%,54.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(121.998,221.779)rotate(90)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(0.0%,54.5%,54.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(142.999,221.779)rotate(90)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(0.0%,54.5%,54.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(164.001,221.779)rotate(90)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(0.0%,54.5%,54.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(185.002,221.779)rotate(90)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(0.0%,54.5%,54.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(206.003,221.779)rotate(90)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(0.0%,54.5%,54.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(227.004,221.779)rotate(90)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(0.0%,54.5%,54.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(248.005,221.779)rotate(90)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(0.0%,54.5%,54.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Persistent style
Finally, another option is to modify the `.style` settings of a `ToyTree` object. This sets a persistent style that will be used as the base each time that tree object calls `.draw`. 

In this example, I first create a copy of our example tree, then modify the object's style settings. As with other tree styles, if you add additional arguments to the draw command they will override this base tree styling.


```python
# set a style that will persist on an individual tree object
stree = tree.copy()
stree.style.edge_colors = "darkcyan"
stree.style.edge_widths = 2.5
stree.style.node_mask = False
stree.style.node_sizes = 16
stree.style.node_markers = "s"
stree.style.node_style.fill_opacity = 0.5
stree.style.node_labels = "idx"
stree.style.tip_labels_style.font_size = 16
stree.style.tip_labels_style.anchor_shift = 25
stree.draw(height=400);
```


<div class="toyplot" id="t11fa4f8a5f0d4152b0caefb9a9409d3d" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="400.0px" viewBox="0 0 300.0 400.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tc3bf7f3da0ab4ba0b0004644dfadfdc4"><g class="toyplot-coordinates-Cartesian" id="t343d996b78bb42a7a1db8a0cdafd6c7a"><clipPath id="t302f886ff63c4048a573f8e394c7bac0"><rect x="35.0" y="35.0" width="230.0" height="330.0"></rect></clipPath><g clip-path="url(#t302f886ff63c4048a573f8e394c7bac0)"></g></g><g class="toyplot-coordinates-Cartesian" id="td075df354453437982e4e64c21e9c342"><clipPath id="tc92483f5d9744b4396b5445464680af0"><rect x="35.0" y="35.0" width="230.0" height="330.0"></rect></clipPath><g clip-path="url(#tc92483f5d9744b4396b5445464680af0)"><g class="toytree-mark-Toytree" id="ted0642b3637d488f96c8879e88d0e576"><g class="toytree-Edges" style="stroke:rgb(0.0%,54.5%,54.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 70.5 317.0 L 70.5 340.4 L 211.2 340.4" id="11,0" style="stroke-width:2.5"></path><path d="M 194.0 293.6 L 194.0 309.2 L 211.2 309.2" id="10,1" style="stroke-width:2.5"></path><path d="M 194.0 293.6 L 194.0 278.0 L 211.2 278.0" id="10,2" style="stroke-width:2.5"></path><path d="M 192.4 231.2 L 192.4 246.8 L 211.2 246.8" id="12,3" style="stroke-width:2.5"></path><path d="M 192.4 231.2 L 192.4 215.6 L 211.2 215.6" id="12,4" style="stroke-width:2.5"></path><path d="M 197.7 168.8 L 197.7 184.4 L 211.2 184.4" id="13,5" style="stroke-width:2.5"></path><path d="M 197.7 168.8 L 197.7 153.2 L 211.2 153.2" id="13,6" style="stroke-width:2.5"></path><path d="M 142.8 98.6 L 142.8 122.0 L 211.2 122.0" id="16,7" style="stroke-width:2.5"></path><path d="M 158.4 75.2 L 158.4 90.8 L 211.2 90.8" id="15,8" style="stroke-width:2.5"></path><path d="M 158.4 75.2 L 158.4 59.6 L 211.2 59.6" id="15,9" style="stroke-width:2.5"></path><path d="M 70.5 317.0 L 70.5 293.6 L 194.0 293.6" id="11,10" style="stroke-width:2.5"></path><path d="M 59.4 233.2 L 59.4 317.0 L 70.5 317.0" id="18,11" style="stroke-width:2.5"></path><path d="M 182.3 200.0 L 182.3 231.2 L 192.4 231.2" id="14,12" style="stroke-width:2.5"></path><path d="M 182.3 200.0 L 182.3 168.8 L 197.7 168.8" id="14,13" style="stroke-width:2.5"></path><path d="M 139.4 149.3 L 139.4 200.0 L 182.3 200.0" id="17,14" style="stroke-width:2.5"></path><path d="M 142.8 98.6 L 142.8 75.2 L 158.4 75.2" id="16,15" style="stroke-width:2.5"></path><path d="M 139.4 149.3 L 139.4 98.6 L 142.8 98.6" id="17,16" style="stroke-width:2.5"></path><path d="M 59.4 233.2 L 59.4 149.3 L 139.4 149.3" id="18,17" style="stroke-width:2.5"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:0.5;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(211.206,340.402)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-1" transform="translate(211.206,309.202)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-2" transform="translate(211.206,278.001)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-3" transform="translate(211.206,246.801)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-4" transform="translate(211.206,215.6)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-5" transform="translate(211.206,184.4)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-6" transform="translate(211.206,153.199)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-7" transform="translate(211.206,121.999)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-8" transform="translate(211.206,90.7982)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-9" transform="translate(211.206,59.5976)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-10" transform="translate(194.044,293.602)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-11" transform="translate(70.4617,317.002)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-12" transform="translate(192.437,231.201)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-13" transform="translate(197.737,168.799)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-14" transform="translate(182.277,200)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-15" transform="translate(158.394,75.1979)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-16" transform="translate(142.759,98.5983)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-17" transform="translate(139.361,149.299)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g><g id="Node-18" transform="translate(59.3957,233.151)"><rect x="-8.0" y="-8.0" width="16" height="16"></rect></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(211.206,340.402)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(211.206,309.202)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(211.206,278.001)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(211.206,246.801)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(211.206,215.6)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(211.206,184.4)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(211.206,153.199)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(211.206,121.999)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(211.206,90.7982)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(211.206,59.5976)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(194.044,293.602)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(70.4617,317.002)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(192.437,231.201)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(197.737,168.799)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(182.277,200)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g><g class="toytree-NodeLabel" transform="translate(158.394,75.1979)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">15</text></g><g class="toytree-NodeLabel" transform="translate(142.759,98.5983)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">16</text></g><g class="toytree-NodeLabel" transform="translate(139.361,149.299)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">17</text></g><g class="toytree-NodeLabel" transform="translate(59.3957,233.151)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">18</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:16px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(211.206,340.402)"><text x="25.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(211.206,309.202)"><text x="25.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(211.206,278.001)"><text x="25.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(211.206,246.801)"><text x="25.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(211.206,215.6)"><text x="25.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(211.206,184.4)"><text x="25.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(211.206,153.199)"><text x="25.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(211.206,121.999)"><text x="25.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(211.206,90.7982)"><text x="25.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(211.206,59.5976)"><text x="25.0" y="4.087999999999999" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:16.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Viewing tree style args

For power users, if you wnat to see the base settings for a particular builtin tree style you can import and view an object like below.


```python
from toytree.style.src.style_types import TreeStyleU
TreeStyleU()
```




    {
    tree_style: 'u',
    height: None,
    width: None,
    layout: 'unrooted',
    edge_type: 'c',
    edge_colors: None,
    edge_widths: None,
    node_mask: None,
    node_colors: 'white',
    node_sizes: 6,
    node_markers: 'o',
    node_hover: None,
    node_labels: 'idx',
    node_as_edge_data: False,
    tip_labels: True,
    tip_labels_colors: None,
    tip_labels_angles: None,
    tip_labels_align: None,
    edge_style: {
        stroke: (0.145, 0.145, 0.145, 1.0),
        stroke_width: 2.0,
        stroke_opacity: None,
        stroke_linecap: 'round',
        stroke_linejoin: 'round',
        stroke_dasharray: None,
        opacity: None,
    },
    node_style: {
        fill: 'white',
        fill_opacity: None,
        stroke: None,
        stroke_width: 1.5,
        stroke_opacity: None,
        stroke_linecap: None,
        stroke_linejoin: None,
        stroke_dasharray: None,
        opacity: None,
    },
    node_labels_style: {
        fill: (0.145, 0.145, 0.145, 1.0),
        fill_opacity: 1.0,
        stroke: None,
        stroke_opacity: None,
        stroke_width: None,
        font_size: 9,
        font_weight: 300,
        font_family: 'Helvetica',
        anchor_shift: 0,
        baseline_shift: 0,
        text_anchor: 'middle',
        opacity: None,
    },
    tip_labels_style: {
        fill: (0.145, 0.145, 0.145, 1.0),
        fill_opacity: None,
        stroke: None,
        stroke_opacity: None,
        stroke_width: None,
        font_size: 12,
        font_weight: 300,
        font_family: 'Helvetica',
        anchor_shift: 15,
        baseline_shift: 0,
        text_anchor: 'start',
        opacity: None,
    },
    edge_align_style: {
        stroke: (0.66, 0.66, 0.66, 1),
        stroke_width: 2,
        stroke_opacity: 0.75,
        stroke_linecap: 'round',
        stroke_linejoin: 'round',
        stroke_dasharray: '2,4',
        opacity: None,
    },
    use_edge_lengths: False,
    scale_bar: False,
    padding: 15.0,
    xbaseline: 0.0,
    ybaseline: 0.0,
    admixture_edges: None,
    }

