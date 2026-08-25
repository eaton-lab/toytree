<div class="nb-md-page-hook" aria-hidden="true"></div>

# Color Mapping

Color mapping projects raw values into colors drawn from a discrete or continuous colormap. This is most useful when you want a tree feature to control node or edge colors without manually building a color array first.

See also [Range Mapping](/drawing-range-mapping/), which projects numeric values into plotting ranges such as marker sizes or edge widths.



```python
import numpy as np
import toyplot

import toytree

# example tree
tree = toytree.rtree.bdtree(10, seed=123)
```

## Quick Example

Color mapping can be applied to either continuous or discrete data.

The two main public helpers are `get_color_mapped_values()` and `get_color_mapped_feature()`. The first maps values you already have in memory. The second extracts a named feature from a tree and returns colors in node idx order so the result can be passed directly into drawing arguments.

### `get_color_mapped_values()`
Here we map the values 0-3 to the BlueRed colormap while extending the domain slightly so the endpoints are not pushed to the darkest colors.



```python
# project values to colors
toytree.data.get_color_mapped_values([0, 1, 2, 3], "BlueRed", domain_min=-1, domain_max=4)
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(26.3%,57.6%,76.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(82.0%,89.8%,94.1%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(99.2%,85.9%,78.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(83.9%,37.6%,30.2%,1.000)"></div></div>



### `get_color_mapped_feature()`
Here we select the `idx` feature from the tree and project it to the BlueRed colormap. The returned colors are in node idx order, which is the order expected by drawing style arguments.



```python
# project values in a stored data feature to colors
toytree.data.get_color_mapped_feature(tree, "idx", "BlueRed", reverse=True)
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(56.7%,5.2%,14.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(71.4%,12.5%,18.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(79.2%,28.2%,25.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(86.5%,43.7%,34.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(93.1%,58.7%,46.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,71.8%,60.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.8%,83.5%,75.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.2%,90.8%,86.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,96.9%,96.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(88.6%,92.9%,95.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(79.2%,88.4%,93.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(65.5%,81.4%,89.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(50.4%,72.9%,84.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(33.2%,62.0%,78.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(21.8%,51.8%,73.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(14.4%,42.0%,68.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(8.1%,30.6%,54.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div></div>



### Use color mapping in a drawing
You can either pass the result of `get_color_mapped_feature()` to any drawing argument that accepts a sequence of colors, or you can use the tuple syntax directly inside the drawing call.



```python
# example: map node height to colors using '(feature, cmap)' syntax
tree.draw(
    node_sizes=10,
    node_mask=False,
    node_colors=("height", "Spectral"),
);
```


<div class="toyplot" id="t6c07f2d480f74f12b759cde0355a22b9" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t247e56d8565a471abb898213cc023c34"><g class="toyplot-coordinates-Cartesian" id="t3fbc4ec51df14d639171079c55487483"><clipPath id="ta81daa0d26a74b5a9018c784b24d919e"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#ta81daa0d26a74b5a9018c784b24d919e)"><g class="toytree-mark-Toytree" id="tc70abe05f4da4e24b326382ceaa6ff2c"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 68.7 204.4 L 68.7 217.8 L 224.4 217.8" id="11,0" style=""></path><path d="M 205.4 191.0 L 205.4 200.0 L 224.4 200.0" id="10,1" style=""></path><path d="M 205.4 191.0 L 205.4 182.1 L 224.4 182.1" id="10,2" style=""></path><path d="M 203.7 155.3 L 203.7 164.3 L 224.4 164.3" id="12,3" style=""></path><path d="M 203.7 155.3 L 203.7 146.4 L 224.4 146.4" id="12,4" style=""></path><path d="M 209.5 119.7 L 209.5 128.6 L 224.4 128.6" id="13,5" style=""></path><path d="M 209.5 119.7 L 209.5 110.7 L 224.4 110.7" id="13,6" style=""></path><path d="M 148.7 79.5 L 148.7 92.9 L 224.4 92.9" id="16,7" style=""></path><path d="M 166.0 66.1 L 166.0 75.0 L 224.4 75.0" id="15,8" style=""></path><path d="M 166.0 66.1 L 166.0 57.2 L 224.4 57.2" id="15,9" style=""></path><path d="M 68.7 204.4 L 68.7 191.0 L 205.4 191.0" id="11,10" style=""></path><path d="M 56.5 156.5 L 56.5 204.4 L 68.7 204.4" id="18,11" style=""></path><path d="M 192.4 137.5 L 192.4 155.3 L 203.7 155.3" id="14,12" style=""></path><path d="M 192.4 137.5 L 192.4 119.7 L 209.5 119.7" id="14,13" style=""></path><path d="M 144.9 108.5 L 144.9 137.5 L 192.4 137.5" id="17,14" style=""></path><path d="M 148.7 79.5 L 148.7 66.1 L 166.0 66.1" id="16,15" style=""></path><path d="M 144.9 108.5 L 144.9 79.5 L 148.7 79.5" id="17,16" style=""></path><path d="M 56.5 156.5 L 56.5 108.5 L 144.9 108.5" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(224.422,217.804)"><circle r="5.0"></circle></g><g id="Node-1" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(224.422,199.958)"><circle r="5.0"></circle></g><g id="Node-2" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(224.422,182.113)"><circle r="5.0"></circle></g><g id="Node-3" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(224.422,164.268)"><circle r="5.0"></circle></g><g id="Node-4" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(224.422,146.423)"><circle r="5.0"></circle></g><g id="Node-5" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(224.422,128.577)"><circle r="5.0"></circle></g><g id="Node-6" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(224.422,110.732)"><circle r="5.0"></circle></g><g id="Node-7" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(224.422,92.8868)"><circle r="5.0"></circle></g><g id="Node-8" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(224.422,75.0416)"><circle r="5.0"></circle></g><g id="Node-9" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(224.422,57.1963)"><circle r="5.0"></circle></g><g id="Node-10" style="fill:rgb(22.3%,56.3%,72.9%)" transform="translate(205.436,191.036)"><circle r="5.0"></circle></g><g id="Node-11" style="fill:rgb(77.7%,17.8%,29.6%)" transform="translate(68.7193,204.42)"><circle r="5.0"></circle></g><g id="Node-12" style="fill:rgb(24.4%,58.7%,71.9%)" transform="translate(203.658,155.345)"><circle r="5.0"></circle></g><g id="Node-13" style="fill:rgb(21.6%,50.8%,72.9%)" transform="translate(209.521,119.655)"><circle r="5.0"></circle></g><g id="Node-14" style="fill:rgb(38.1%,73.9%,65.6%)" transform="translate(192.418,137.5)"><circle r="5.0"></circle></g><g id="Node-15" style="fill:rgb(78.1%,91.2%,62.1%)" transform="translate(165.996,66.1189)"><circle r="5.0"></circle></g><g id="Node-16" style="fill:rgb(95.2%,98.1%,67.4%)" transform="translate(148.7,79.5029)"><circle r="5.0"></circle></g><g id="Node-17" style="fill:rgb(97.4%,99.0%,70.8%)" transform="translate(144.941,108.501)"><circle r="5.0"></circle></g><g id="Node-18" style="fill:rgb(62.0%,0.4%,25.9%)" transform="translate(56.4773,156.461)"><circle r="5.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.422,217.804)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.422,199.958)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.422,182.113)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.422,164.268)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.422,146.423)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.422,128.577)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.422,110.732)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.422,92.8868)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.422,75.0416)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(224.422,57.1963)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


You can also enter the keyword arguments for `get_color_mapped_feature()` directly as a dictionary when calling drawing or annotation functions.



```python
tree.draw(
    node_sizes=10,
    node_mask=False,
    node_colors={'feature': 'idx', 'cmap': 'BlueRed', 'reverse': True, 'domain_min': -1, 'domain_max': 10},
);
```


<div class="toyplot" id="t2994feee8f504d27acd37966ded94d9b" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t29b022d1261f4f789caf3ce06ffae139"><g class="toyplot-coordinates-Cartesian" id="taf45076bd0124dcf85e67ed5f289eff6"><clipPath id="t6920e4e6c0ff41caa52b422fc3ecf9fd"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t6920e4e6c0ff41caa52b422fc3ecf9fd)"><g class="toytree-mark-Toytree" id="t7c0e8e8c1db44f3d975f1a5a966afaf1"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 68.7 204.4 L 68.7 217.8 L 224.4 217.8" id="11,0" style=""></path><path d="M 205.4 191.0 L 205.4 200.0 L 224.4 200.0" id="10,1" style=""></path><path d="M 205.4 191.0 L 205.4 182.1 L 224.4 182.1" id="10,2" style=""></path><path d="M 203.7 155.3 L 203.7 164.3 L 224.4 164.3" id="12,3" style=""></path><path d="M 203.7 155.3 L 203.7 146.4 L 224.4 146.4" id="12,4" style=""></path><path d="M 209.5 119.7 L 209.5 128.6 L 224.4 128.6" id="13,5" style=""></path><path d="M 209.5 119.7 L 209.5 110.7 L 224.4 110.7" id="13,6" style=""></path><path d="M 148.7 79.5 L 148.7 92.9 L 224.4 92.9" id="16,7" style=""></path><path d="M 166.0 66.1 L 166.0 75.0 L 224.4 75.0" id="15,8" style=""></path><path d="M 166.0 66.1 L 166.0 57.2 L 224.4 57.2" id="15,9" style=""></path><path d="M 68.7 204.4 L 68.7 191.0 L 205.4 191.0" id="11,10" style=""></path><path d="M 56.5 156.5 L 56.5 204.4 L 68.7 204.4" id="18,11" style=""></path><path d="M 192.4 137.5 L 192.4 155.3 L 203.7 155.3" id="14,12" style=""></path><path d="M 192.4 137.5 L 192.4 119.7 L 209.5 119.7" id="14,13" style=""></path><path d="M 144.9 108.5 L 144.9 137.5 L 192.4 137.5" id="17,14" style=""></path><path d="M 148.7 79.5 L 148.7 66.1 L 166.0 66.1" id="16,15" style=""></path><path d="M 144.9 108.5 L 144.9 79.5 L 148.7 79.5" id="17,16" style=""></path><path d="M 56.5 156.5 L 56.5 108.5 L 144.9 108.5" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(67.1%,8.6%,16.4%)" transform="translate(224.422,217.804)"><circle r="5.0"></circle></g><g id="Node-1" style="fill:rgb(81.4%,32.5%,27.8%)" transform="translate(224.422,199.958)"><circle r="5.0"></circle></g><g id="Node-2" style="fill:rgb(92.5%,57.3%,45.3%)" transform="translate(224.422,182.113)"><circle r="5.0"></circle></g><g id="Node-3" style="fill:rgb(97.9%,78.2%,68.2%)" transform="translate(224.422,164.268)"><circle r="5.0"></circle></g><g id="Node-4" style="fill:rgb(97.9%,91.9%,88.3%)" transform="translate(224.422,146.423)"><circle r="5.0"></circle></g><g id="Node-5" style="fill:rgb(90.1%,93.7%,95.6%)" transform="translate(224.422,128.577)"><circle r="5.0"></circle></g><g id="Node-6" style="fill:rgb(73.0%,85.2%,91.6%)" transform="translate(224.422,110.732)"><circle r="5.0"></circle></g><g id="Node-7" style="fill:rgb(48.8%,71.9%,84.2%)" transform="translate(224.422,92.8868)"><circle r="5.0"></circle></g><g id="Node-8" style="fill:rgb(23.9%,54.4%,74.8%)" transform="translate(224.422,75.0416)"><circle r="5.0"></circle></g><g id="Node-9" style="fill:rgb(11.9%,38.1%,64.8%)" transform="translate(224.422,57.1963)"><circle r="5.0"></circle></g><g id="Node-10" style="fill:rgb(2.0%,18.8%,38.0%)" transform="translate(205.436,191.036)"><circle r="5.0"></circle></g><g id="Node-11" style="fill:rgb(2.0%,18.8%,38.0%)" transform="translate(68.7193,204.42)"><circle r="5.0"></circle></g><g id="Node-12" style="fill:rgb(2.0%,18.8%,38.0%)" transform="translate(203.658,155.345)"><circle r="5.0"></circle></g><g id="Node-13" style="fill:rgb(2.0%,18.8%,38.0%)" transform="translate(209.521,119.655)"><circle r="5.0"></circle></g><g id="Node-14" style="fill:rgb(2.0%,18.8%,38.0%)" transform="translate(192.418,137.5)"><circle r="5.0"></circle></g><g id="Node-15" style="fill:rgb(2.0%,18.8%,38.0%)" transform="translate(165.996,66.1189)"><circle r="5.0"></circle></g><g id="Node-16" style="fill:rgb(2.0%,18.8%,38.0%)" transform="translate(148.7,79.5029)"><circle r="5.0"></circle></g><g id="Node-17" style="fill:rgb(2.0%,18.8%,38.0%)" transform="translate(144.941,108.501)"><circle r="5.0"></circle></g><g id="Node-18" style="fill:rgb(2.0%,18.8%,38.0%)" transform="translate(56.4773,156.461)"><circle r="5.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.422,217.804)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.422,199.958)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.422,182.113)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.422,164.268)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.422,146.423)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.422,128.577)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.422,110.732)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.422,92.8868)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.422,75.0416)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(224.422,57.1963)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Example Data

To demonstrate color-mapping let's generate a couple types of data features. The first "W" contains random float values between 0-1. The second "X" contains float values in the range (0-100). The third feature contains discrete str values randomly sampled from ("A", "B", "C"). And the final feature contains the same data as feature "X", but with missing values for alternating Nodes.


```python
rng = np.random.default_rng(seed=123)
tree.set_node_data("W", rng.random(tree.nnodes), inplace=True)
tree.set_node_data("X", np.linspace(0, 100, tree.nnodes), inplace=True)
tree.set_node_data("Y", rng.choice(["A", "B", "C"], tree.nnodes), inplace=True)
tree.set_node_data("Z", {i: i.X for i in tree[::2]}, inplace=True);
```


```python
# show data in a table
tree.get_node_data(["W", "X", "Y", "Z"])
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
      <th>W</th>
      <th>X</th>
      <th>Y</th>
      <th>Z</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0.682352</td>
      <td>0.000000</td>
      <td>A</td>
      <td>0.000000</td>
    </tr>
    <tr>
      <th>1</th>
      <td>0.053821</td>
      <td>5.555556</td>
      <td>B</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>0.220360</td>
      <td>11.111111</td>
      <td>C</td>
      <td>11.111111</td>
    </tr>
    <tr>
      <th>3</th>
      <td>0.184372</td>
      <td>16.666667</td>
      <td>A</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>4</th>
      <td>0.175906</td>
      <td>22.222222</td>
      <td>A</td>
      <td>22.222222</td>
    </tr>
    <tr>
      <th>5</th>
      <td>0.812095</td>
      <td>27.777778</td>
      <td>A</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>6</th>
      <td>0.923345</td>
      <td>33.333333</td>
      <td>A</td>
      <td>33.333333</td>
    </tr>
    <tr>
      <th>7</th>
      <td>0.276574</td>
      <td>38.888889</td>
      <td>B</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>8</th>
      <td>0.819755</td>
      <td>44.444444</td>
      <td>A</td>
      <td>44.444444</td>
    </tr>
    <tr>
      <th>9</th>
      <td>0.889893</td>
      <td>50.000000</td>
      <td>B</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>10</th>
      <td>0.512970</td>
      <td>55.555556</td>
      <td>B</td>
      <td>55.555556</td>
    </tr>
    <tr>
      <th>11</th>
      <td>0.244965</td>
      <td>61.111111</td>
      <td>A</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>12</th>
      <td>0.824242</td>
      <td>66.666667</td>
      <td>B</td>
      <td>66.666667</td>
    </tr>
    <tr>
      <th>13</th>
      <td>0.213763</td>
      <td>72.222222</td>
      <td>A</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>14</th>
      <td>0.741467</td>
      <td>77.777778</td>
      <td>A</td>
      <td>77.777778</td>
    </tr>
    <tr>
      <th>15</th>
      <td>0.629940</td>
      <td>83.333333</td>
      <td>B</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>16</th>
      <td>0.927407</td>
      <td>88.888889</td>
      <td>A</td>
      <td>88.888889</td>
    </tr>
    <tr>
      <th>17</th>
      <td>0.231908</td>
      <td>94.444444</td>
      <td>C</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>18</th>
      <td>0.799125</td>
      <td>100.000000</td>
      <td>A</td>
      <td>100.000000</td>
    </tr>
  </tbody>
</table>
</div>



## toyplot Colors
`toytree` relies on `toyplot.color` for parsing color data and defining color maps. Please see the incredibly good [color module documentation of toyplot](https://toyplot.readthedocs.io/en/stable/colors.html) for more details. Here I provide a simple introduction. You can select colors in three main ways: (1) CSS color name; (2) rgb tuple; or (3) rgba tuple. 


```python
# define colors by name, rgb, or rgba
color1 = "teal"
color2 = (0.1, 0.5, 0.5)
color3 = (0.1, 0.5, 0.5, 0.3)
```

Here I pass the three objects above to `toyplot.color.Palette`, which is an object that can parse multiple different types of color inputs and store the results as an array. A palette represents the simplest form of ColorMap, containing a discrete collection of colors. This object has a nice property for displaying a color palette in the notebook, like below.


```python
# create a Palette object to easily visualize
colors = toyplot.color.Palette([color1, color2, color3])
colors
```




<div class="toyplot-color-Palette" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(0.0%,50.2%,50.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(10.0%,50.0%,50.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(10.0%,50.0%,50.0%,0.300)"></div></div>



### Color array dtype
Colors in a `toyplot.color` array are stored in a complex data format that allows for performing mathematical operations on colors, which allows for blending colors from a palette together to create gradients in colormaps. In most cases, this is an advanced feature you do not need to worry about. It is simplest to select colors by name, or by selecting them from a pre-defined palette or colormap, as described in the next section.


```python
# the dtype of numpy array based colors in toyplot
colors[0].dtype
```




    dtype([('r', '<f8'), ('g', '<f8'), ('b', '<f8'), ('a', '<f8')])



### Color Palettes
There are a number of pre-defined color palettes that can be selected by name from the `toyplot.color` subpackage named `brewer`, which contains the popular "brewer2" color sets. The default color palette in `toyplot` is called Set2, and can be selected like below. A number of "diverging" color palettes (see more below) can also be selected and discretized into a palette by using the `count` argument to maximize divergence among the colors for the number of discrete states in a set of data. 


```python
# select a pre-defined discrete color palette
toyplot.color.brewer.palette("Set2")
```




<div class="toyplot-color-Palette" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(98.8%,55.3%,38.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(55.3%,62.7%,79.6%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(90.6%,54.1%,76.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(65.1%,84.7%,32.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(100.0%,85.1%,18.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(89.8%,76.9%,58.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(70.2%,70.2%,70.2%,1.000)"></div></div>




```python
# select a pre-defined diverging color palette
toyplot.color.brewer.palette("BlueRed", count=8)
```




<div class="toyplot-color-Palette" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(12.9%,40.0%,67.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(26.3%,57.6%,76.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(57.3%,77.3%,87.1%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(82.0%,89.8%,94.1%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(99.2%,85.9%,78.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(95.7%,64.7%,51.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(83.9%,37.6%,30.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(69.8%,9.4%,16.9%,1.000)"></div></div>




```python
# define a color palette manually
toyplot.color.Palette(["darkcyan", "darkmagenta", "goldenrod"])
```




<div class="toyplot-color-Palette" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(0.0%,54.5%,54.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(54.5%,0.0%,54.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:0px;background-color:rgba(85.5%,64.7%,12.5%,1.000)"></div></div>



## ColorMaps
A colormap (`toyplot.color.Map`) is a more advanced container for describing a distribution of colors. 
There are two main types of colormaps, discrete and continous. A discrete map contains a small number of colors that are typically grouped together by a shared design palette with the goal of being maximally divergent from each other. By contrast, a continuous colormap represents colors sampled along a continuous range of RGBA values such that a gradient can be easily observed spanning from minimum to maximum values in the map. The default colormaps used by `toytree` are "Spectral" for continous data and "Set2" for categorical.


```python
# select a pre-defined diverging or linear colormap
toyplot.color.brewer.map("Spectral")
```




<div class="toyplot-color-LinearMap" style="overflow:hidden; height:auto"><div style="float:left;width:200px;height:20px;background:linear-gradient(to right,rgba(36.9%,31.0%,63.5%,1.000) 0.0%,rgba(34.1%,34.5%,65.2%,1.000) 1.6%,rgba(31.4%,38.1%,66.9%,1.000) 3.2%,rgba(28.6%,41.6%,68.6%,1.000) 4.8%,rgba(25.9%,45.2%,70.3%,1.000) 6.3%,rgba(23.2%,48.7%,71.9%,1.000) 7.9%,rgba(20.4%,52.3%,73.6%,1.000) 9.5%,rgba(21.9%,55.9%,73.1%,1.000) 11.1%,rgba(25.1%,59.5%,71.6%,1.000) 12.7%,rgba(28.3%,63.1%,70.1%,1.000) 14.3%,rgba(31.6%,66.7%,68.6%,1.000) 15.9%,rgba(34.8%,70.3%,67.1%,1.000) 17.5%,rgba(38.1%,73.9%,65.6%,1.000) 19.0%,rgba(41.7%,76.8%,64.7%,1.000) 20.6%,rgba(46.0%,78.4%,64.6%,1.000) 22.2%,rgba(50.3%,80.1%,64.6%,1.000) 23.8%,rgba(54.6%,81.8%,64.5%,1.000) 25.4%,rgba(58.9%,83.5%,64.4%,1.000) 27.0%,rgba(63.2%,85.2%,64.4%,1.000) 28.6%,rgba(67.4%,86.8%,64.2%,1.000) 30.2%,rgba(71.1%,88.3%,63.5%,1.000) 31.7%,rgba(74.8%,89.8%,62.7%,1.000) 33.3%,rgba(78.4%,91.3%,62.0%,1.000) 34.9%,rgba(82.1%,92.8%,61.3%,1.000) 36.5%,rgba(85.8%,94.3%,60.5%,1.000) 38.1%,rgba(89.5%,95.8%,59.8%,1.000) 39.7%,rgba(91.4%,96.6%,61.5%,1.000) 41.3%,rgba(93.0%,97.2%,64.0%,1.000) 42.9%,rgba(94.6%,97.8%,66.4%,1.000) 44.4%,rgba(96.1%,98.4%,68.8%,1.000) 46.0%,rgba(97.7%,99.1%,71.3%,1.000) 47.6%,rgba(99.2%,99.7%,73.7%,1.000) 49.2%,rgba(100.0%,99.0%,73.3%,1.000) 50.8%,rgba(99.9%,97.1%,70.0%,1.000) 52.4%,rgba(99.8%,95.2%,66.8%,1.000) 54.0%,rgba(99.8%,93.2%,63.6%,1.000) 55.6%,rgba(99.7%,91.3%,60.3%,1.000) 57.1%,rgba(99.7%,89.4%,57.1%,1.000) 58.7%,rgba(99.6%,87.2%,54.0%,1.000) 60.3%,rgba(99.5%,84.1%,51.4%,1.000) 61.9%,rgba(99.5%,81.0%,48.8%,1.000) 63.5%,rgba(99.4%,77.9%,46.1%,1.000) 65.1%,rgba(99.3%,74.8%,43.5%,1.000) 66.7%,rgba(99.3%,71.7%,40.9%,1.000) 68.3%,rgba(99.2%,68.5%,38.3%,1.000) 69.8%,rgba(98.7%,64.6%,36.4%,1.000) 71.4%,rgba(98.2%,60.5%,34.5%,1.000) 73.0%,rgba(97.6%,56.5%,32.6%,1.000) 74.6%,rgba(97.0%,52.5%,30.8%,1.000) 76.2%,rgba(96.5%,48.4%,28.9%,1.000) 77.8%,rgba(95.9%,44.4%,27.0%,1.000) 79.4%,rgba(94.5%,41.0%,26.7%,1.000) 81.0%,rgba(92.6%,38.1%,27.5%,1.000) 82.5%,rgba(90.7%,35.1%,28.2%,1.000) 84.1%,rgba(88.7%,32.2%,29.0%,1.000) 85.7%,rgba(86.8%,29.3%,29.7%,1.000) 87.3%,rgba(84.9%,26.4%,30.5%,1.000) 88.9%,rgba(82.5%,23.2%,30.7%,1.000) 90.5%,rgba(79.1%,19.4%,29.9%,1.000) 92.1%,rgba(75.7%,15.6%,29.1%,1.000) 93.7%,rgba(72.2%,11.8%,28.3%,1.000) 95.2%,rgba(68.8%,8.0%,27.5%,1.000) 96.8%,rgba(65.4%,4.2%,26.7%,1.000) 98.4%,rgba(62.0%,0.4%,25.9%,1.000) 100.0%)"></div></div>



### `get_color_mapped_feature()`
This helper is the public function used under the hood by tuple-format color mapping in drawing calls. It accepts a tree, a feature name, and a colormap, plus options such as `domain_min`, `domain_max`, `nan_value`, and `reverse`. That makes it useful both for direct inspection and for reusing one mapped color vector across multiple figures.



```python
# project data 'X' to colors from a colormap
toytree.data.get_color_mapped_feature(tree, feature="X", cmap="Spectral")
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(36.9%,31.0%,63.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(27.3%,43.4%,69.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(21.9%,55.9%,73.1%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(33.2%,68.5%,67.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(46.0%,78.4%,64.6%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(61.0%,84.3%,64.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(74.8%,89.8%,62.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(87.6%,95.0%,60.1%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(94.6%,97.8%,66.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(100.0%,100.0%,74.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(99.8%,93.2%,63.6%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(99.6%,85.7%,52.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(99.3%,74.8%,43.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.4%,62.6%,35.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.5%,48.4%,28.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(91.6%,36.6%,27.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(84.9%,26.4%,30.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(73.9%,13.7%,28.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(62.0%,0.4%,25.9%,1.000)"></div></div>



### Continuous map examples
Here the data are extracted from the "X" feature on the tree, which contians values equally spaced between 0-100 assigned in order to the 18 Nodes in the tree. Thus, the colors assigned to each Node match the gradient of the colormap. In the next example, the feature "W" is mapped to the same colormap, which yields a very different distribution of colors, since Nodes 0-17 contain random values for this feature. 


```python
# project data "X" to a named colormap
toytree.data.get_color_mapped_feature(tree, "X", "BlueRed")
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(8.1%,30.6%,54.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(14.4%,42.0%,68.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(21.8%,51.8%,73.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(33.2%,62.0%,78.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(50.4%,72.9%,84.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(65.5%,81.4%,89.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(79.2%,88.4%,93.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(88.6%,92.9%,95.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,96.9%,96.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.2%,90.8%,86.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.8%,83.5%,75.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,71.8%,60.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(93.1%,58.7%,46.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(86.5%,43.7%,34.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(79.2%,28.2%,25.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(71.4%,12.5%,18.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(56.7%,5.2%,14.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div></div>




```python
# project data "W" to a named colormap
toytree.data.get_color_mapped_feature(tree, "W", "BlueRed")
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(93.4%,59.4%,46.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(25.0%,56.0%,75.6%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(19.5%,48.7%,71.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(18.2%,47.0%,71.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(74.3%,18.4%,21.1%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(41.8%,0.4%,12.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(43.3%,68.4%,82.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(73.1%,16.0%,20.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(53.0%,4.0%,14.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(97.5%,94.1%,92.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(32.1%,61.3%,78.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(72.4%,14.5%,19.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(24.0%,54.7%,74.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(85.4%,41.1%,32.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(97.1%,73.3%,61.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(27.5%,58.4%,76.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(76.4%,22.6%,23.1%,1.000)"></div></div>



The domain min or max can be set to limit the range of colors such that multiple values at the upper or lower end of the data map to the same color. For example, here we set the max to 50 even though the max of the data we are mapping ("X") is 100. Consequently, the color map range is concentrated between 0-50 and all values above 50 are assigned the max color. If min and max values are not set on a colormap then it will by default use the min and max values of the data being projected. Thus, it is only relevant to set these values if you wish to condense colors at one end or the other.


```python
# create a ColorMap with a restricted range
toytree.data.get_color_mapped_feature(
    tree, "X", "BlueRed", domain_min=0, domain_max=50
)
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(14.4%,42.0%,68.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(33.2%,62.0%,78.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(65.5%,81.4%,89.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(88.6%,92.9%,95.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.2%,90.8%,86.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,71.8%,60.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(86.5%,43.7%,34.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(71.4%,12.5%,18.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div></div>



The order in which values are mapped to colors in a colomap can be reversed using the `reverse` argument.


```python
# create a reversed ColorMap by name
toytree.data.get_color_mapped_feature(tree, "X", "BlueRed", reverse=True)
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(56.7%,5.2%,14.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(71.4%,12.5%,18.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(79.2%,28.2%,25.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(86.5%,43.7%,34.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(93.1%,58.7%,46.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,71.8%,60.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.8%,83.5%,75.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.2%,90.8%,86.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,96.9%,96.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(88.6%,92.9%,95.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(79.2%,88.4%,93.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(65.5%,81.4%,89.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(50.4%,72.9%,84.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(33.2%,62.0%,78.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(21.8%,51.8%,73.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(14.4%,42.0%,68.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(8.1%,30.6%,54.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div></div>



The center of the colormap can be skewed towards one end or the other. Here it is set at 25, closer to the min value. This compresses the range of colors to the left of 25, and expands the range to right of 25. This can be useful if the variation among the larger values is of greater interest than among the lower values. 


```python
# create a ColorMap with a skewed center
cmap = toyplot.color.brewer.map("BlueRed", domain_min=0, domain_max=100, center=25)

# ...
toytree.data.get_color_mapped_feature(tree, "X", cmap)
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(14.4%,42.0%,68.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(33.2%,62.0%,78.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(65.5%,81.4%,89.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(88.6%,92.9%,95.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(97.3%,94.8%,93.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.2%,90.8%,86.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(99.0%,86.7%,79.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.2%,79.6%,70.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,71.8%,60.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(95.3%,63.7%,50.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(90.9%,53.7%,42.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(86.5%,43.7%,34.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(81.8%,33.5%,28.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(76.6%,23.0%,23.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(71.4%,12.5%,18.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(62.2%,7.0%,15.6%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(51.3%,3.5%,13.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div></div>



By default, color mapping in `toytree` assigns `transparent` to missing values. You can override that behavior with `nan_value` if you want missing observations to remain visible or to map to the same color as a chosen numeric value.



```python
# default behavior sets 'transparent' to missing/NaN values
toytree.data.get_color_mapped_feature(tree, "Z", "BlueRed")
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,0.0%,0.0%,0.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(14.4%,42.0%,68.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,0.0%,0.0%,0.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(33.2%,62.0%,78.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,0.0%,0.0%,0.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(65.5%,81.4%,89.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,0.0%,0.0%,0.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(88.6%,92.9%,95.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,0.0%,0.0%,0.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.2%,90.8%,86.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,0.0%,0.0%,0.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,71.8%,60.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,0.0%,0.0%,0.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(86.5%,43.7%,34.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,0.0%,0.0%,0.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(71.4%,12.5%,18.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,0.0%,0.0%,0.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div></div>




```python
# setting 'nan_value' imputes a data value to be colormapped for missing
toytree.data.get_color_mapped_feature(tree, "Z", "BlueRed", nan_value=0)
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(14.4%,42.0%,68.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(33.2%,62.0%,78.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(65.5%,81.4%,89.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(88.6%,92.9%,95.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.2%,90.8%,86.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,71.8%,60.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(86.5%,43.7%,34.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(71.4%,12.5%,18.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div></div>



### Discrete map example
You can similarly map discrete/categorical data to colormaps. For this you can enter either a Categorical or Linear ColorMap, which in the latter case will reduce the linear map into equally spaced discrete colors. Like before you can either enter the name of a colormap, or create a `ColorMap` object. As an even simpler option, you can simply enter a list of color names that is of the same length as the number of discrete states in the data, as shown below. Here the data are extracted from the "Y" feature on the tree which represents random discrete states of "A", "B" or "C".


```python
# map a discrete feature to a list/Palette of color names
toytree.data.get_color_mapped_feature(tree, "Y", ["red", "blue", "green"])
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(100.0%,0.0%,0.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,0.0%,100.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,50.2%,0.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(100.0%,0.0%,0.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(100.0%,0.0%,0.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(100.0%,0.0%,0.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(100.0%,0.0%,0.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,0.0%,100.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(100.0%,0.0%,0.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,0.0%,100.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,0.0%,100.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(100.0%,0.0%,0.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,0.0%,100.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(100.0%,0.0%,0.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(100.0%,0.0%,0.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,0.0%,100.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(100.0%,0.0%,0.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,50.2%,0.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(100.0%,0.0%,0.0%,1.000)"></div></div>




```python
# map a discrete feature to a discrete colormap
toytree.data.get_color_mapped_feature(tree, "Y", "Set2")
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.8%,55.3%,38.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(55.3%,62.7%,79.6%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.8%,55.3%,38.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.8%,55.3%,38.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.8%,55.3%,38.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.8%,55.3%,38.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.8%,55.3%,38.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(55.3%,62.7%,79.6%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div></div>




```python
# map a discrete feature to a continuous colormap
toytree.data.get_color_mapped_feature(tree, "Y", "BlueRed")
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,66.3%,81.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,96.9%,96.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(93.7%,54.1%,38.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,66.3%,81.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,66.3%,81.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,66.3%,81.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,66.3%,81.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,96.9%,96.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,66.3%,81.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,96.9%,96.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,96.9%,96.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,66.3%,81.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,96.9%,96.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,66.3%,81.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,66.3%,81.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,96.9%,96.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,66.3%,81.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(93.7%,54.1%,38.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,66.3%,81.2%,1.000)"></div></div>



By creating the ColorMap manually you can set more additional arguments, such as the number of states, which can be used to  discretize colors at a more fine or coarse scale.


```python
# enter a colormap object
cmap = toyplot.color.brewer.map("BlueRed", count=8)
toytree.data.get_color_mapped_feature(tree, "Y", cmap)
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(12.9%,40.0%,67.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(90.6%,87.8%,86.1%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(69.8%,9.4%,16.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(12.9%,40.0%,67.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(12.9%,40.0%,67.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(12.9%,40.0%,67.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(12.9%,40.0%,67.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(90.6%,87.8%,86.1%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(12.9%,40.0%,67.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(90.6%,87.8%,86.1%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(90.6%,87.8%,86.1%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(12.9%,40.0%,67.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(90.6%,87.8%,86.1%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(12.9%,40.0%,67.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(12.9%,40.0%,67.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(90.6%,87.8%,86.1%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(12.9%,40.0%,67.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(69.8%,9.4%,16.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(12.9%,40.0%,67.5%,1.000)"></div></div>



## Recommended ColorMaps
These are are a few of my favorites:


```python
toytree.data.get_color_mapped_feature(tree, "X", "BlueRed")
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(2.0%,18.8%,38.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(8.1%,30.6%,54.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(14.4%,42.0%,68.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(21.8%,51.8%,73.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(33.2%,62.0%,78.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(50.4%,72.9%,84.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(65.5%,81.4%,89.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(79.2%,88.4%,93.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(88.6%,92.9%,95.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,96.9%,96.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.2%,90.8%,86.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.8%,83.5%,75.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.9%,71.8%,60.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(93.1%,58.7%,46.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(86.5%,43.7%,34.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(79.2%,28.2%,25.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(71.4%,12.5%,18.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(56.7%,5.2%,14.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.4%,0.0%,12.2%,1.000)"></div></div>




```python
toytree.data.get_color_mapped_feature(tree, "X", "Spectral")
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(36.9%,31.0%,63.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(27.3%,43.4%,69.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(21.9%,55.9%,73.1%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(33.2%,68.5%,67.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(46.0%,78.4%,64.6%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(61.0%,84.3%,64.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(74.8%,89.8%,62.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(87.6%,95.0%,60.1%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(94.6%,97.8%,66.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(100.0%,100.0%,74.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(99.8%,93.2%,63.6%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(99.6%,85.7%,52.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(99.3%,74.8%,43.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.4%,62.6%,35.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(96.5%,48.4%,28.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(91.6%,36.6%,27.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(84.9%,26.4%,30.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(73.9%,13.7%,28.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(62.0%,0.4%,25.9%,1.000)"></div></div>




```python
toytree.data.get_color_mapped_feature(tree, "X", "Blackbody")
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,0.0%,0.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(12.1%,5.2%,3.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(20.2%,7.8%,5.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(29.0%,9.5%,7.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(38.3%,10.9%,9.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(47.9%,12.0%,10.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(57.9%,12.7%,12.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(67.9%,13.6%,13.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(73.7%,22.2%,12.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(79.0%,30.2%,10.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(84.2%,37.6%,5.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(87.6%,46.1%,1.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(88.7%,55.5%,1.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(89.5%,64.4%,1.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(89.8%,73.1%,1.6%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(89.7%,81.7%,2.3%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(94.4%,87.9%,42.5%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.3%,93.8%,71.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(100.0%,100.0%,100.0%,1.000)"></div></div>




```python
toytree.data.get_color_mapped_feature(tree, "X", "Greys")
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(0.0%,0.0%,0.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(6.4%,6.4%,6.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(12.9%,12.9%,12.9%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(20.4%,20.4%,20.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(28.2%,28.2%,28.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(35.0%,35.0%,35.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.8%,40.8%,40.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(46.6%,46.6%,46.6%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(52.7%,52.7%,52.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(58.8%,58.8%,58.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(65.6%,65.6%,65.6%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(72.4%,72.4%,72.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(77.8%,77.8%,77.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(82.7%,82.7%,82.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(87.1%,87.1%,87.1%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(91.1%,91.1%,91.1%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(94.8%,94.8%,94.8%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(97.4%,97.4%,97.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(100.0%,100.0%,100.0%,1.000)"></div></div>




```python
toytree.data.get_color_mapped_feature(tree, "Y", "Set1")
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(89.4%,10.2%,11.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(21.6%,49.4%,72.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(30.2%,68.6%,29.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(89.4%,10.2%,11.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(89.4%,10.2%,11.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(89.4%,10.2%,11.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(89.4%,10.2%,11.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(21.6%,49.4%,72.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(89.4%,10.2%,11.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(21.6%,49.4%,72.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(21.6%,49.4%,72.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(89.4%,10.2%,11.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(21.6%,49.4%,72.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(89.4%,10.2%,11.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(89.4%,10.2%,11.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(21.6%,49.4%,72.2%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(89.4%,10.2%,11.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(30.2%,68.6%,29.0%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(89.4%,10.2%,11.0%,1.000)"></div></div>




```python
toytree.data.get_color_mapped_feature(tree, "Y", "Set2")
```




<div class="toyplot-color-Swatches" style="overflow:hidden; height:auto"><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.8%,55.3%,38.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(55.3%,62.7%,79.6%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.8%,55.3%,38.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.8%,55.3%,38.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.8%,55.3%,38.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.8%,55.3%,38.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(98.8%,55.3%,38.4%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(55.3%,62.7%,79.6%,1.000)"></div><div style="float:left;width:20px;height:20px;margin-right:5px;background-color:rgba(40.0%,76.1%,64.7%,1.000)"></div></div>



## Using Color Mapping
For convenience you can perform color mapping directly inside `toytree` drawing functions using tuple syntax instead of calling `get_color_mapped_feature()` yourself. The minimal form is `(feature,)`, which uses the default colormap for the data. You can add additional arguments in order to control the colormap and domain used during mapping.

### Tuple Syntax
Color-mapping tuples use the form `(feature, cmap, domain_min, domain_max, nan_value)`. Common variants are:

- `(feature,)`
- `(feature, cmap)`
- `(feature, cmap, domain_min, domain_max)`
- `(feature, cmap, domain_min, domain_max, nan_value)`
- `(feature, None, None, None, 10)`

When `cmap` is omitted, the helper defaults to `Spectral`. Missing values default to `transparent` unless `nan_value` is provided.



```python
# project "W" values to default 'Spectral' colormap
tree.draw(node_colors=("W",), node_sizes=10, node_mask=False);
```


<div class="toyplot" id="t7d47b6d8d2d94dd0977613e6f30b422d" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tc45bb8426a20476dab7e59f6a3dd5b42"><g class="toyplot-coordinates-Cartesian" id="te303b800f22b47f49210b26a7dd3e826"><clipPath id="t2e451e278cd149e9b1d242b802dd9770"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t2e451e278cd149e9b1d242b802dd9770)"><g class="toytree-mark-Toytree" id="t17bf667d5a8d4cd99f2f0a170beb4000"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 68.7 204.4 L 68.7 217.8 L 224.4 217.8" id="11,0" style=""></path><path d="M 205.4 191.0 L 205.4 200.0 L 224.4 200.0" id="10,1" style=""></path><path d="M 205.4 191.0 L 205.4 182.1 L 224.4 182.1" id="10,2" style=""></path><path d="M 203.7 155.3 L 203.7 164.3 L 224.4 164.3" id="12,3" style=""></path><path d="M 203.7 155.3 L 203.7 146.4 L 224.4 146.4" id="12,4" style=""></path><path d="M 209.5 119.7 L 209.5 128.6 L 224.4 128.6" id="13,5" style=""></path><path d="M 209.5 119.7 L 209.5 110.7 L 224.4 110.7" id="13,6" style=""></path><path d="M 148.7 79.5 L 148.7 92.9 L 224.4 92.9" id="16,7" style=""></path><path d="M 166.0 66.1 L 166.0 75.0 L 224.4 75.0" id="15,8" style=""></path><path d="M 166.0 66.1 L 166.0 57.2 L 224.4 57.2" id="15,9" style=""></path><path d="M 68.7 204.4 L 68.7 191.0 L 205.4 191.0" id="11,10" style=""></path><path d="M 56.5 156.5 L 56.5 204.4 L 68.7 204.4" id="18,11" style=""></path><path d="M 192.4 137.5 L 192.4 155.3 L 203.7 155.3" id="14,12" style=""></path><path d="M 192.4 137.5 L 192.4 119.7 L 209.5 119.7" id="14,13" style=""></path><path d="M 144.9 108.5 L 144.9 137.5 L 192.4 137.5" id="17,14" style=""></path><path d="M 148.7 79.5 L 148.7 66.1 L 166.0 66.1" id="16,15" style=""></path><path d="M 144.9 108.5 L 144.9 79.5 L 148.7 79.5" id="17,16" style=""></path><path d="M 56.5 156.5 L 56.5 108.5 L 144.9 108.5" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(98.5%,63.3%,35.7%)" transform="translate(224.422,217.804)"><circle r="5.0"></circle></g><g id="Node-1" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(224.422,199.958)"><circle r="5.0"></circle></g><g id="Node-2" style="fill:rgb(38.1%,73.9%,65.6%)" transform="translate(224.422,182.113)"><circle r="5.0"></circle></g><g id="Node-3" style="fill:rgb(29.7%,64.6%,69.5%)" transform="translate(224.422,164.268)"><circle r="5.0"></circle></g><g id="Node-4" style="fill:rgb(27.7%,62.4%,70.4%)" transform="translate(224.422,146.423)"><circle r="5.0"></circle></g><g id="Node-5" style="fill:rgb(87.4%,30.2%,29.5%)" transform="translate(224.422,128.577)"><circle r="5.0"></circle></g><g id="Node-6" style="fill:rgb(63.0%,1.5%,26.1%)" transform="translate(224.422,110.732)"><circle r="5.0"></circle></g><g id="Node-7" style="fill:rgb(54.9%,81.9%,64.5%)" transform="translate(224.422,92.8868)"><circle r="5.0"></circle></g><g id="Node-8" style="fill:rgb(86.4%,28.6%,29.9%)" transform="translate(224.422,75.0416)"><circle r="5.0"></circle></g><g id="Node-9" style="fill:rgb(71.2%,10.7%,28.1%)" transform="translate(224.422,57.1963)"><circle r="5.0"></circle></g><g id="Node-10" style="fill:rgb(99.9%,96.9%,69.7%)" transform="translate(205.436,191.036)"><circle r="5.0"></circle></g><g id="Node-11" style="fill:rgb(45.1%,78.1%,64.6%)" transform="translate(68.7193,204.42)"><circle r="5.0"></circle></g><g id="Node-12" style="fill:rgb(85.7%,27.6%,30.1%)" transform="translate(203.658,155.345)"><circle r="5.0"></circle></g><g id="Node-13" style="fill:rgb(36.6%,72.2%,66.3%)" transform="translate(209.521,119.655)"><circle r="5.0"></circle></g><g id="Node-14" style="fill:rgb(96.1%,46.0%,27.8%)" transform="translate(192.418,137.5)"><circle r="5.0"></circle></g><g id="Node-15" style="fill:rgb(99.4%,76.2%,44.7%)" transform="translate(165.996,66.1189)"><circle r="5.0"></circle></g><g id="Node-16" style="fill:rgb(62.0%,0.4%,25.9%)" transform="translate(148.7,79.5029)"><circle r="5.0"></circle></g><g id="Node-17" style="fill:rgb(41.0%,76.5%,64.7%)" transform="translate(144.941,108.501)"><circle r="5.0"></circle></g><g id="Node-18" style="fill:rgb(89.2%,32.9%,28.8%)" transform="translate(56.4773,156.461)"><circle r="5.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.422,217.804)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.422,199.958)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.422,182.113)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.422,164.268)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.422,146.423)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.422,128.577)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.422,110.732)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.422,92.8868)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.422,75.0416)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(224.422,57.1963)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# project "Y" values to discrete colors
tree.draw(node_colors=("Y", "BlueRed"), node_sizes=10, node_mask=False);
```


<div class="toyplot" id="tf381657c751c4695a1450e7d7bd39a2d" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t9b9d2a50ea4b49849194e5faa1641c53"><g class="toyplot-coordinates-Cartesian" id="t389a6984e0c24e52a6d3a2c2383e4dad"><clipPath id="td21979410f9142d7a56886fbd42533dc"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#td21979410f9142d7a56886fbd42533dc)"><g class="toytree-mark-Toytree" id="t5c93e1333f2e42c880bbd82b846ea7a3"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 68.7 204.4 L 68.7 217.8 L 224.4 217.8" id="11,0" style=""></path><path d="M 205.4 191.0 L 205.4 200.0 L 224.4 200.0" id="10,1" style=""></path><path d="M 205.4 191.0 L 205.4 182.1 L 224.4 182.1" id="10,2" style=""></path><path d="M 203.7 155.3 L 203.7 164.3 L 224.4 164.3" id="12,3" style=""></path><path d="M 203.7 155.3 L 203.7 146.4 L 224.4 146.4" id="12,4" style=""></path><path d="M 209.5 119.7 L 209.5 128.6 L 224.4 128.6" id="13,5" style=""></path><path d="M 209.5 119.7 L 209.5 110.7 L 224.4 110.7" id="13,6" style=""></path><path d="M 148.7 79.5 L 148.7 92.9 L 224.4 92.9" id="16,7" style=""></path><path d="M 166.0 66.1 L 166.0 75.0 L 224.4 75.0" id="15,8" style=""></path><path d="M 166.0 66.1 L 166.0 57.2 L 224.4 57.2" id="15,9" style=""></path><path d="M 68.7 204.4 L 68.7 191.0 L 205.4 191.0" id="11,10" style=""></path><path d="M 56.5 156.5 L 56.5 204.4 L 68.7 204.4" id="18,11" style=""></path><path d="M 192.4 137.5 L 192.4 155.3 L 203.7 155.3" id="14,12" style=""></path><path d="M 192.4 137.5 L 192.4 119.7 L 209.5 119.7" id="14,13" style=""></path><path d="M 144.9 108.5 L 144.9 137.5 L 192.4 137.5" id="17,14" style=""></path><path d="M 148.7 79.5 L 148.7 66.1 L 166.0 66.1" id="16,15" style=""></path><path d="M 144.9 108.5 L 144.9 79.5 L 148.7 79.5" id="17,16" style=""></path><path d="M 56.5 156.5 L 56.5 108.5 L 144.9 108.5" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(40.4%,66.3%,81.2%)" transform="translate(224.422,217.804)"><circle r="5.0"></circle></g><g id="Node-1" style="fill:rgb(96.9%,96.9%,96.9%)" transform="translate(224.422,199.958)"><circle r="5.0"></circle></g><g id="Node-2" style="fill:rgb(93.7%,54.1%,38.4%)" transform="translate(224.422,182.113)"><circle r="5.0"></circle></g><g id="Node-3" style="fill:rgb(40.4%,66.3%,81.2%)" transform="translate(224.422,164.268)"><circle r="5.0"></circle></g><g id="Node-4" style="fill:rgb(40.4%,66.3%,81.2%)" transform="translate(224.422,146.423)"><circle r="5.0"></circle></g><g id="Node-5" style="fill:rgb(40.4%,66.3%,81.2%)" transform="translate(224.422,128.577)"><circle r="5.0"></circle></g><g id="Node-6" style="fill:rgb(40.4%,66.3%,81.2%)" transform="translate(224.422,110.732)"><circle r="5.0"></circle></g><g id="Node-7" style="fill:rgb(96.9%,96.9%,96.9%)" transform="translate(224.422,92.8868)"><circle r="5.0"></circle></g><g id="Node-8" style="fill:rgb(40.4%,66.3%,81.2%)" transform="translate(224.422,75.0416)"><circle r="5.0"></circle></g><g id="Node-9" style="fill:rgb(96.9%,96.9%,96.9%)" transform="translate(224.422,57.1963)"><circle r="5.0"></circle></g><g id="Node-10" style="fill:rgb(96.9%,96.9%,96.9%)" transform="translate(205.436,191.036)"><circle r="5.0"></circle></g><g id="Node-11" style="fill:rgb(40.4%,66.3%,81.2%)" transform="translate(68.7193,204.42)"><circle r="5.0"></circle></g><g id="Node-12" style="fill:rgb(96.9%,96.9%,96.9%)" transform="translate(203.658,155.345)"><circle r="5.0"></circle></g><g id="Node-13" style="fill:rgb(40.4%,66.3%,81.2%)" transform="translate(209.521,119.655)"><circle r="5.0"></circle></g><g id="Node-14" style="fill:rgb(40.4%,66.3%,81.2%)" transform="translate(192.418,137.5)"><circle r="5.0"></circle></g><g id="Node-15" style="fill:rgb(96.9%,96.9%,96.9%)" transform="translate(165.996,66.1189)"><circle r="5.0"></circle></g><g id="Node-16" style="fill:rgb(40.4%,66.3%,81.2%)" transform="translate(148.7,79.5029)"><circle r="5.0"></circle></g><g id="Node-17" style="fill:rgb(93.7%,54.1%,38.4%)" transform="translate(144.941,108.501)"><circle r="5.0"></circle></g><g id="Node-18" style="fill:rgb(40.4%,66.3%,81.2%)" transform="translate(56.4773,156.461)"><circle r="5.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.422,217.804)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.422,199.958)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.422,182.113)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.422,164.268)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.422,146.423)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.422,128.577)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.422,110.732)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.422,92.8868)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.422,75.0416)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(224.422,57.1963)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# project "X" in minmax range 0-50 using the default colormap
tree.draw(node_colors=("X", None, 0, 50), node_sizes=10, node_mask=False);
```


<div class="toyplot" id="t537dd816a25d48e1a97ecf58956ef224" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t33bd7534e7194716a301872e4f337efb"><g class="toyplot-coordinates-Cartesian" id="te537495c10b54799baf279ce32fd124e"><clipPath id="t687a4f48a3204b3b86fef88e80fae316"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t687a4f48a3204b3b86fef88e80fae316)"><g class="toytree-mark-Toytree" id="tc71df943e5774175b3c8554a3cfa0ac4"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 68.7 204.4 L 68.7 217.8 L 224.4 217.8" id="11,0" style=""></path><path d="M 205.4 191.0 L 205.4 200.0 L 224.4 200.0" id="10,1" style=""></path><path d="M 205.4 191.0 L 205.4 182.1 L 224.4 182.1" id="10,2" style=""></path><path d="M 203.7 155.3 L 203.7 164.3 L 224.4 164.3" id="12,3" style=""></path><path d="M 203.7 155.3 L 203.7 146.4 L 224.4 146.4" id="12,4" style=""></path><path d="M 209.5 119.7 L 209.5 128.6 L 224.4 128.6" id="13,5" style=""></path><path d="M 209.5 119.7 L 209.5 110.7 L 224.4 110.7" id="13,6" style=""></path><path d="M 148.7 79.5 L 148.7 92.9 L 224.4 92.9" id="16,7" style=""></path><path d="M 166.0 66.1 L 166.0 75.0 L 224.4 75.0" id="15,8" style=""></path><path d="M 166.0 66.1 L 166.0 57.2 L 224.4 57.2" id="15,9" style=""></path><path d="M 68.7 204.4 L 68.7 191.0 L 205.4 191.0" id="11,10" style=""></path><path d="M 56.5 156.5 L 56.5 204.4 L 68.7 204.4" id="18,11" style=""></path><path d="M 192.4 137.5 L 192.4 155.3 L 203.7 155.3" id="14,12" style=""></path><path d="M 192.4 137.5 L 192.4 119.7 L 209.5 119.7" id="14,13" style=""></path><path d="M 144.9 108.5 L 144.9 137.5 L 192.4 137.5" id="17,14" style=""></path><path d="M 148.7 79.5 L 148.7 66.1 L 166.0 66.1" id="16,15" style=""></path><path d="M 144.9 108.5 L 144.9 79.5 L 148.7 79.5" id="17,16" style=""></path><path d="M 56.5 156.5 L 56.5 108.5 L 144.9 108.5" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(224.422,217.804)"><circle r="5.0"></circle></g><g id="Node-1" style="fill:rgb(21.9%,55.9%,73.1%)" transform="translate(224.422,199.958)"><circle r="5.0"></circle></g><g id="Node-2" style="fill:rgb(46.0%,78.4%,64.6%)" transform="translate(224.422,182.113)"><circle r="5.0"></circle></g><g id="Node-3" style="fill:rgb(74.8%,89.8%,62.7%)" transform="translate(224.422,164.268)"><circle r="5.0"></circle></g><g id="Node-4" style="fill:rgb(94.6%,97.8%,66.4%)" transform="translate(224.422,146.423)"><circle r="5.0"></circle></g><g id="Node-5" style="fill:rgb(99.8%,93.2%,63.6%)" transform="translate(224.422,128.577)"><circle r="5.0"></circle></g><g id="Node-6" style="fill:rgb(99.3%,74.8%,43.5%)" transform="translate(224.422,110.732)"><circle r="5.0"></circle></g><g id="Node-7" style="fill:rgb(96.5%,48.4%,28.9%)" transform="translate(224.422,92.8868)"><circle r="5.0"></circle></g><g id="Node-8" style="fill:rgb(84.9%,26.4%,30.5%)" transform="translate(224.422,75.0416)"><circle r="5.0"></circle></g><g id="Node-9" style="fill:rgb(62.0%,0.4%,25.9%)" transform="translate(224.422,57.1963)"><circle r="5.0"></circle></g><g id="Node-10" style="fill:rgb(62.0%,0.4%,25.9%)" transform="translate(205.436,191.036)"><circle r="5.0"></circle></g><g id="Node-11" style="fill:rgb(62.0%,0.4%,25.9%)" transform="translate(68.7193,204.42)"><circle r="5.0"></circle></g><g id="Node-12" style="fill:rgb(62.0%,0.4%,25.9%)" transform="translate(203.658,155.345)"><circle r="5.0"></circle></g><g id="Node-13" style="fill:rgb(62.0%,0.4%,25.9%)" transform="translate(209.521,119.655)"><circle r="5.0"></circle></g><g id="Node-14" style="fill:rgb(62.0%,0.4%,25.9%)" transform="translate(192.418,137.5)"><circle r="5.0"></circle></g><g id="Node-15" style="fill:rgb(62.0%,0.4%,25.9%)" transform="translate(165.996,66.1189)"><circle r="5.0"></circle></g><g id="Node-16" style="fill:rgb(62.0%,0.4%,25.9%)" transform="translate(148.7,79.5029)"><circle r="5.0"></circle></g><g id="Node-17" style="fill:rgb(62.0%,0.4%,25.9%)" transform="translate(144.941,108.501)"><circle r="5.0"></circle></g><g id="Node-18" style="fill:rgb(62.0%,0.4%,25.9%)" transform="translate(56.4773,156.461)"><circle r="5.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.422,217.804)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.422,199.958)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.422,182.113)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.422,164.268)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.422,146.423)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.422,128.577)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.422,110.732)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.422,92.8868)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.422,75.0416)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(224.422,57.1963)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# project "Z" to "Greys" colormap with nan_values set to 0 (black)
tree.draw(node_colors=("Z", "Greys", None, None, 0), node_sizes=10, node_mask=False);
```


<div class="toyplot" id="t15ccbaa951be4c1da7f97be780213ad4" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="td2e8303f5ece46a9bac0057d6708e73e"><g class="toyplot-coordinates-Cartesian" id="t2dbd55cad3af43b0a00c67c08b3f1ab4"><clipPath id="tb565a00345ba4fb1bc45eda7720d877f"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tb565a00345ba4fb1bc45eda7720d877f)"><g class="toytree-mark-Toytree" id="teff433b0a9564356acf1556efcd7bfe0"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 68.7 204.4 L 68.7 217.8 L 224.4 217.8" id="11,0" style=""></path><path d="M 205.4 191.0 L 205.4 200.0 L 224.4 200.0" id="10,1" style=""></path><path d="M 205.4 191.0 L 205.4 182.1 L 224.4 182.1" id="10,2" style=""></path><path d="M 203.7 155.3 L 203.7 164.3 L 224.4 164.3" id="12,3" style=""></path><path d="M 203.7 155.3 L 203.7 146.4 L 224.4 146.4" id="12,4" style=""></path><path d="M 209.5 119.7 L 209.5 128.6 L 224.4 128.6" id="13,5" style=""></path><path d="M 209.5 119.7 L 209.5 110.7 L 224.4 110.7" id="13,6" style=""></path><path d="M 148.7 79.5 L 148.7 92.9 L 224.4 92.9" id="16,7" style=""></path><path d="M 166.0 66.1 L 166.0 75.0 L 224.4 75.0" id="15,8" style=""></path><path d="M 166.0 66.1 L 166.0 57.2 L 224.4 57.2" id="15,9" style=""></path><path d="M 68.7 204.4 L 68.7 191.0 L 205.4 191.0" id="11,10" style=""></path><path d="M 56.5 156.5 L 56.5 204.4 L 68.7 204.4" id="18,11" style=""></path><path d="M 192.4 137.5 L 192.4 155.3 L 203.7 155.3" id="14,12" style=""></path><path d="M 192.4 137.5 L 192.4 119.7 L 209.5 119.7" id="14,13" style=""></path><path d="M 144.9 108.5 L 144.9 137.5 L 192.4 137.5" id="17,14" style=""></path><path d="M 148.7 79.5 L 148.7 66.1 L 166.0 66.1" id="16,15" style=""></path><path d="M 144.9 108.5 L 144.9 79.5 L 148.7 79.5" id="17,16" style=""></path><path d="M 56.5 156.5 L 56.5 108.5 L 144.9 108.5" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(0.0%,0.0%,0.0%)" transform="translate(224.422,217.804)"><circle r="5.0"></circle></g><g id="Node-1" style="fill:rgb(0.0%,0.0%,0.0%)" transform="translate(224.422,199.958)"><circle r="5.0"></circle></g><g id="Node-2" style="fill:rgb(12.9%,12.9%,12.9%)" transform="translate(224.422,182.113)"><circle r="5.0"></circle></g><g id="Node-3" style="fill:rgb(0.0%,0.0%,0.0%)" transform="translate(224.422,164.268)"><circle r="5.0"></circle></g><g id="Node-4" style="fill:rgb(28.2%,28.2%,28.2%)" transform="translate(224.422,146.423)"><circle r="5.0"></circle></g><g id="Node-5" style="fill:rgb(0.0%,0.0%,0.0%)" transform="translate(224.422,128.577)"><circle r="5.0"></circle></g><g id="Node-6" style="fill:rgb(40.8%,40.8%,40.8%)" transform="translate(224.422,110.732)"><circle r="5.0"></circle></g><g id="Node-7" style="fill:rgb(0.0%,0.0%,0.0%)" transform="translate(224.422,92.8868)"><circle r="5.0"></circle></g><g id="Node-8" style="fill:rgb(52.7%,52.7%,52.7%)" transform="translate(224.422,75.0416)"><circle r="5.0"></circle></g><g id="Node-9" style="fill:rgb(0.0%,0.0%,0.0%)" transform="translate(224.422,57.1963)"><circle r="5.0"></circle></g><g id="Node-10" style="fill:rgb(65.6%,65.6%,65.6%)" transform="translate(205.436,191.036)"><circle r="5.0"></circle></g><g id="Node-11" style="fill:rgb(0.0%,0.0%,0.0%)" transform="translate(68.7193,204.42)"><circle r="5.0"></circle></g><g id="Node-12" style="fill:rgb(77.8%,77.8%,77.8%)" transform="translate(203.658,155.345)"><circle r="5.0"></circle></g><g id="Node-13" style="fill:rgb(0.0%,0.0%,0.0%)" transform="translate(209.521,119.655)"><circle r="5.0"></circle></g><g id="Node-14" style="fill:rgb(87.1%,87.1%,87.1%)" transform="translate(192.418,137.5)"><circle r="5.0"></circle></g><g id="Node-15" style="fill:rgb(0.0%,0.0%,0.0%)" transform="translate(165.996,66.1189)"><circle r="5.0"></circle></g><g id="Node-16" style="fill:rgb(94.8%,94.8%,94.8%)" transform="translate(148.7,79.5029)"><circle r="5.0"></circle></g><g id="Node-17" style="fill:rgb(0.0%,0.0%,0.0%)" transform="translate(144.941,108.501)"><circle r="5.0"></circle></g><g id="Node-18" style="fill:rgb(100.0%,100.0%,100.0%)" transform="translate(56.4773,156.461)"><circle r="5.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.422,217.804)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.422,199.958)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.422,182.113)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.422,164.268)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.422,146.423)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.422,128.577)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.422,110.732)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.422,92.8868)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.422,75.0416)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(224.422,57.1963)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


Tuple-format color mapping is also supported by the `annotate` subpackage, so you can add mapped colors after a drawing has already been created.



```python
# draw a tree and add node marker annotations w/ colormapped "X"
canvas, axes, mark = tree.draw()
tree.annotate.add_node_markers(axes, color=("X", "BlueRed"), mask=False);
```


<div class="toyplot" id="tc85b715b093a4c18ab62413135abb6e6" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t1c71f6173d984169bdcb66ec4af82a18"><g class="toyplot-coordinates-Cartesian" id="te28d3b5fa85d4226a79220e173ebe555"><clipPath id="t533be6dce5e44894ab484b4e7b5bef04"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t533be6dce5e44894ab484b4e7b5bef04)"><g class="toytree-mark-Toytree" id="tc26cf69e123f44d1b691c4c2ecc81df8"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 67.8 204.4 L 67.8 217.8 L 224.4 217.8" id="11,0" style=""></path><path d="M 205.3 191.0 L 205.3 200.0 L 224.4 200.0" id="10,1" style=""></path><path d="M 205.3 191.0 L 205.3 182.1 L 224.4 182.1" id="10,2" style=""></path><path d="M 203.5 155.3 L 203.5 164.3 L 224.4 164.3" id="12,3" style=""></path><path d="M 203.5 155.3 L 203.5 146.4 L 224.4 146.4" id="12,4" style=""></path><path d="M 209.4 119.7 L 209.4 128.6 L 224.4 128.6" id="13,5" style=""></path><path d="M 209.4 119.7 L 209.4 110.7 L 224.4 110.7" id="13,6" style=""></path><path d="M 148.2 79.5 L 148.2 92.9 L 224.4 92.9" id="16,7" style=""></path><path d="M 165.6 66.1 L 165.6 75.0 L 224.4 75.0" id="15,8" style=""></path><path d="M 165.6 66.1 L 165.6 57.2 L 224.4 57.2" id="15,9" style=""></path><path d="M 67.8 204.4 L 67.8 191.0 L 205.3 191.0" id="11,10" style=""></path><path d="M 55.5 156.5 L 55.5 204.4 L 67.8 204.4" id="18,11" style=""></path><path d="M 192.2 137.5 L 192.2 155.3 L 203.5 155.3" id="14,12" style=""></path><path d="M 192.2 137.5 L 192.2 119.7 L 209.4 119.7" id="14,13" style=""></path><path d="M 144.5 108.5 L 144.5 137.5 L 192.2 137.5" id="17,14" style=""></path><path d="M 148.2 79.5 L 148.2 66.1 L 165.6 66.1" id="16,15" style=""></path><path d="M 144.5 108.5 L 144.5 79.5 L 148.2 79.5" id="17,16" style=""></path><path d="M 55.5 156.5 L 55.5 108.5 L 144.5 108.5" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.414,217.804)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.414,199.958)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.414,182.113)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.414,164.268)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.414,146.423)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.414,128.577)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.414,110.732)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.414,92.8868)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.414,75.0416)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(224.414,57.1963)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g><g class="toytree-Annotation-Markers" id="t61d9622608af430f8e994e9a79edc5a4" style="stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Mark-0" style="fill:rgb(2.0%,18.8%,38.0%);fill-opacity:1.0" transform="translate(224.414,217.804)"><circle r="4.0"></circle></g><g id="Mark-1" style="fill:rgb(8.1%,30.6%,54.4%);fill-opacity:1.0" transform="translate(224.414,199.958)"><circle r="4.0"></circle></g><g id="Mark-2" style="fill:rgb(14.4%,42.0%,68.5%);fill-opacity:1.0" transform="translate(224.414,182.113)"><circle r="4.0"></circle></g><g id="Mark-3" style="fill:rgb(21.8%,51.8%,73.5%);fill-opacity:1.0" transform="translate(224.414,164.268)"><circle r="4.0"></circle></g><g id="Mark-4" style="fill:rgb(33.2%,62.0%,78.8%);fill-opacity:1.0" transform="translate(224.414,146.423)"><circle r="4.0"></circle></g><g id="Mark-5" style="fill:rgb(50.4%,72.9%,84.7%);fill-opacity:1.0" transform="translate(224.414,128.577)"><circle r="4.0"></circle></g><g id="Mark-6" style="fill:rgb(65.5%,81.4%,89.4%);fill-opacity:1.0" transform="translate(224.414,110.732)"><circle r="4.0"></circle></g><g id="Mark-7" style="fill:rgb(79.2%,88.4%,93.3%);fill-opacity:1.0" transform="translate(224.414,92.8868)"><circle r="4.0"></circle></g><g id="Mark-8" style="fill:rgb(88.6%,92.9%,95.3%);fill-opacity:1.0" transform="translate(224.414,75.0416)"><circle r="4.0"></circle></g><g id="Mark-9" style="fill:rgb(96.9%,96.9%,96.9%);fill-opacity:1.0" transform="translate(224.414,57.1963)"><circle r="4.0"></circle></g><g id="Mark-10" style="fill:rgb(98.2%,90.8%,86.4%);fill-opacity:1.0" transform="translate(205.316,191.036)"><circle r="4.0"></circle></g><g id="Mark-11" style="fill:rgb(98.8%,83.5%,75.0%);fill-opacity:1.0" transform="translate(67.7964,204.42)"><circle r="4.0"></circle></g><g id="Mark-12" style="fill:rgb(96.9%,71.8%,60.0%);fill-opacity:1.0" transform="translate(203.528,155.345)"><circle r="4.0"></circle></g><g id="Mark-13" style="fill:rgb(93.1%,58.7%,46.4%);fill-opacity:1.0" transform="translate(209.426,119.655)"><circle r="4.0"></circle></g><g id="Mark-14" style="fill:rgb(86.5%,43.7%,34.8%);fill-opacity:1.0" transform="translate(192.222,137.5)"><circle r="4.0"></circle></g><g id="Mark-15" style="fill:rgb(79.2%,28.2%,25.8%);fill-opacity:1.0" transform="translate(165.645,66.1189)"><circle r="4.0"></circle></g><g id="Mark-16" style="fill:rgb(71.4%,12.5%,18.3%);fill-opacity:1.0" transform="translate(148.248,79.5029)"><circle r="4.0"></circle></g><g id="Mark-17" style="fill:rgb(56.7%,5.2%,14.8%);fill-opacity:1.0" transform="translate(144.467,108.501)"><circle r="4.0"></circle></g><g id="Mark-18" style="fill:rgb(40.4%,0.0%,12.2%);fill-opacity:1.0" transform="translate(55.4824,156.461)"><circle r="4.0"></circle></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Using `toyplot.color.Map` Objects
`get_color_mapped_feature()` provides the most convenient public entry point for common workflows, but advanced users can also pass a `toyplot.color.Map` object directly instead of a named colormap. This makes it possible to reuse custom toyplot colormaps inside `toytree` drawing code.



```python
# create a custom Diverging colormap
col0 = toyplot.color.css("goldenrod")
col1 = toyplot.color.css("darkcyan")
custom_map = toyplot.color.DivergingMap(low=col0, high=col1, domain_min=0, domain_max=1)
custom_map
```




<div class="toyplot-color-DivergingMap" style="overflow:hidden; height:auto"><div style="float:left;width:200px;height:20px;background:linear-gradient(to right,rgba(85.5%,64.7%,12.6%,1.000) 0.0%,rgba(86.9%,66.3%,17.0%,1.000) 1.6%,rgba(88.2%,67.8%,20.9%,1.000) 3.2%,rgba(89.5%,69.3%,24.4%,1.000) 4.8%,rgba(90.6%,70.7%,27.7%,1.000) 6.3%,rgba(91.7%,72.0%,30.8%,1.000) 7.9%,rgba(92.6%,73.4%,33.8%,1.000) 9.5%,rgba(93.5%,74.6%,36.7%,1.000) 11.1%,rgba(94.3%,75.8%,39.5%,1.000) 12.7%,rgba(95.0%,77.0%,42.3%,1.000) 14.3%,rgba(95.6%,78.0%,44.9%,1.000) 15.9%,rgba(96.1%,79.1%,47.5%,1.000) 17.5%,rgba(96.5%,80.0%,50.1%,1.000) 19.0%,rgba(96.8%,80.9%,52.6%,1.000) 20.6%,rgba(97.0%,81.8%,55.0%,1.000) 22.2%,rgba(97.2%,82.6%,57.3%,1.000) 23.8%,rgba(97.2%,83.3%,59.6%,1.000) 25.4%,rgba(97.2%,84.0%,61.8%,1.000) 27.0%,rgba(97.0%,84.6%,64.0%,1.000) 28.6%,rgba(96.8%,85.1%,66.1%,1.000) 30.2%,rgba(96.5%,85.6%,68.1%,1.000) 31.7%,rgba(96.1%,86.0%,70.1%,1.000) 33.3%,rgba(95.6%,86.3%,72.0%,1.000) 34.9%,rgba(95.0%,86.6%,73.8%,1.000) 36.5%,rgba(94.3%,86.8%,75.5%,1.000) 38.1%,rgba(93.6%,87.0%,77.2%,1.000) 39.7%,rgba(92.7%,87.1%,78.9%,1.000) 41.3%,rgba(91.8%,87.1%,80.4%,1.000) 42.9%,rgba(90.8%,87.1%,81.9%,1.000) 44.4%,rgba(89.7%,87.0%,83.3%,1.000) 46.0%,rgba(88.5%,86.9%,84.7%,1.000) 47.6%,rgba(87.2%,86.7%,85.9%,1.000) 49.2%,rgba(85.8%,86.2%,85.7%,1.000) 50.8%,rgba(84.3%,85.4%,83.9%,1.000) 52.4%,rgba(82.7%,84.7%,82.3%,1.000) 54.0%,rgba(81.0%,83.9%,80.6%,1.000) 55.6%,rgba(79.2%,83.1%,79.1%,1.000) 57.1%,rgba(77.4%,82.3%,77.5%,1.000) 58.7%,rgba(75.4%,81.5%,76.1%,1.000) 60.3%,rgba(73.4%,80.7%,74.7%,1.000) 61.9%,rgba(71.4%,79.8%,73.3%,1.000) 63.5%,rgba(69.2%,78.9%,72.0%,1.000) 65.1%,rgba(67.0%,78.0%,70.8%,1.000) 66.7%,rgba(64.8%,77.1%,69.6%,1.000) 68.3%,rgba(62.5%,76.1%,68.4%,1.000) 69.8%,rgba(60.2%,75.2%,67.3%,1.000) 71.4%,rgba(57.8%,74.2%,66.3%,1.000) 73.0%,rgba(55.3%,73.2%,65.3%,1.000) 74.6%,rgba(52.9%,72.1%,64.4%,1.000) 76.2%,rgba(50.4%,71.1%,63.5%,1.000) 77.8%,rgba(47.8%,70.0%,62.6%,1.000) 79.4%,rgba(45.2%,68.9%,61.8%,1.000) 81.0%,rgba(42.6%,67.8%,61.1%,1.000) 82.5%,rgba(39.9%,66.7%,60.3%,1.000) 84.1%,rgba(37.2%,65.5%,59.7%,1.000) 85.7%,rgba(34.4%,64.3%,59.0%,1.000) 87.3%,rgba(31.5%,63.2%,58.4%,1.000) 88.9%,rgba(28.5%,62.0%,57.8%,1.000) 90.5%,rgba(25.4%,60.7%,57.2%,1.000) 92.1%,rgba(22.1%,59.5%,56.6%,1.000) 93.7%,rgba(18.5%,58.3%,56.1%,1.000) 95.2%,rgba(14.3%,57.0%,55.5%,1.000) 96.8%,rgba(9.0%,55.8%,55.0%,1.000) 98.4%,rgba(0.0%,54.5%,54.5%,1.000) 100.0%)"></div></div>




```python
tree.draw(node_sizes=10, node_colors=("W", custom_map), node_mask=False);
```


<div class="toyplot" id="t31d106a17b8c4592b9777bfe4021d1a9" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t28130771a08b4d05831a2b1aa9535697"><g class="toyplot-coordinates-Cartesian" id="t2fb344bc3aef41bca8b30e8457ac6068"><clipPath id="t391bf50512da4c0e845f1908bfef11b8"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t391bf50512da4c0e845f1908bfef11b8)"><g class="toytree-mark-Toytree" id="t9b977ddbc36d48cc8bc3d3ebb7fa00b9"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 68.7 204.4 L 68.7 217.8 L 224.4 217.8" id="11,0" style=""></path><path d="M 205.4 191.0 L 205.4 200.0 L 224.4 200.0" id="10,1" style=""></path><path d="M 205.4 191.0 L 205.4 182.1 L 224.4 182.1" id="10,2" style=""></path><path d="M 203.7 155.3 L 203.7 164.3 L 224.4 164.3" id="12,3" style=""></path><path d="M 203.7 155.3 L 203.7 146.4 L 224.4 146.4" id="12,4" style=""></path><path d="M 209.5 119.7 L 209.5 128.6 L 224.4 128.6" id="13,5" style=""></path><path d="M 209.5 119.7 L 209.5 110.7 L 224.4 110.7" id="13,6" style=""></path><path d="M 148.7 79.5 L 148.7 92.9 L 224.4 92.9" id="16,7" style=""></path><path d="M 166.0 66.1 L 166.0 75.0 L 224.4 75.0" id="15,8" style=""></path><path d="M 166.0 66.1 L 166.0 57.2 L 224.4 57.2" id="15,9" style=""></path><path d="M 68.7 204.4 L 68.7 191.0 L 205.4 191.0" id="11,10" style=""></path><path d="M 56.5 156.5 L 56.5 204.4 L 68.7 204.4" id="18,11" style=""></path><path d="M 192.4 137.5 L 192.4 155.3 L 203.7 155.3" id="14,12" style=""></path><path d="M 192.4 137.5 L 192.4 119.7 L 209.5 119.7" id="14,13" style=""></path><path d="M 144.9 108.5 L 144.9 137.5 L 192.4 137.5" id="17,14" style=""></path><path d="M 148.7 79.5 L 148.7 66.1 L 166.0 66.1" id="16,15" style=""></path><path d="M 144.9 108.5 L 144.9 79.5 L 148.7 79.5" id="17,16" style=""></path><path d="M 56.5 156.5 L 56.5 108.5 L 144.9 108.5" id="18,17" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(64.8%,77.1%,69.6%)" transform="translate(224.422,217.804)"><circle r="5.0"></circle></g><g id="Node-1" style="fill:rgb(89.9%,69.8%,25.7%)" transform="translate(224.422,199.958)"><circle r="5.0"></circle></g><g id="Node-2" style="fill:rgb(97.0%,81.7%,54.7%)" transform="translate(224.422,182.113)"><circle r="5.0"></circle></g><g id="Node-3" style="fill:rgb(96.3%,79.7%,49.1%)" transform="translate(224.422,164.268)"><circle r="5.0"></circle></g><g id="Node-4" style="fill:rgb(96.1%,79.2%,47.8%)" transform="translate(224.422,146.423)"><circle r="5.0"></circle></g><g id="Node-5" style="fill:rgb(44.8%,68.7%,61.7%)" transform="translate(224.422,128.577)"><circle r="5.0"></circle></g><g id="Node-6" style="fill:rgb(24.9%,60.5%,57.1%)" transform="translate(224.422,110.732)"><circle r="5.0"></circle></g><g id="Node-7" style="fill:rgb(97.1%,84.2%,62.7%)" transform="translate(224.422,92.8868)"><circle r="5.0"></circle></g><g id="Node-8" style="fill:rgb(43.6%,68.2%,61.3%)" transform="translate(224.422,75.0416)"><circle r="5.0"></circle></g><g id="Node-9" style="fill:rgb(31.3%,63.1%,58.3%)" transform="translate(224.422,57.1963)"><circle r="5.0"></circle></g><g id="Node-10" style="fill:rgb(85.4%,85.9%,85.1%)" transform="translate(205.436,191.036)"><circle r="5.0"></circle></g><g id="Node-11" style="fill:rgb(97.2%,82.9%,58.3%)" transform="translate(68.7193,204.42)"><circle r="5.0"></circle></g><g id="Node-12" style="fill:rgb(42.8%,67.9%,61.1%)" transform="translate(203.658,155.345)"><circle r="5.0"></circle></g><g id="Node-13" style="fill:rgb(96.9%,81.3%,53.7%)" transform="translate(209.521,119.655)"><circle r="5.0"></circle></g><g id="Node-14" style="fill:rgb(56.0%,73.5%,65.6%)" transform="translate(192.418,137.5)"><circle r="5.0"></circle></g><g id="Node-15" style="fill:rgb(72.0%,80.1%,73.7%)" transform="translate(165.996,66.1189)"><circle r="5.0"></circle></g><g id="Node-16" style="fill:rgb(24.0%,60.2%,56.9%)" transform="translate(148.7,79.5029)"><circle r="5.0"></circle></g><g id="Node-17" style="fill:rgb(97.1%,82.3%,56.4%)" transform="translate(144.941,108.501)"><circle r="5.0"></circle></g><g id="Node-18" style="fill:rgb(46.9%,69.6%,62.4%)" transform="translate(56.4773,156.461)"><circle r="5.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.422,217.804)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.422,199.958)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.422,182.113)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.422,164.268)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.422,146.423)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.422,128.577)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(224.422,110.732)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(224.422,92.8868)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(224.422,75.0416)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(224.422,57.1963)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>

