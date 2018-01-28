
## Toytree objects
The basic object in toytree is the `Toytree` object. This object has a number of useful attributes and functions to interact with the underlying `tree` object which hold the tree structure in memory. In this section we will describe how the tree is stored and how to modify and interact with it. 


```python
import toytree
import toyplot
import random
```


```python
#### Generate a random toytree
random.seed(123)
tre = toytree.rtree(ntips=8)
```

All of the information that is used to draw a tree is extracted from the toytree object, and so the more you know about how to access that data the more you will know about how to modify it. In the example below we extract the node colors from a list of colors available from the tree, and get the node labels from the tree features, and we get the tip labels from the tree object. 


```python
## draw the tree
tre.draw(
    node_color=tre.colors[3],
    orient='right',
    node_labels='height',
    node_size=15,
    tip_labels_align=True,
    );
```


<div class="toyplot" id="t85ae6c5b1cc84538bf43fb12cfdff4e7" style="text-align:center"><svg class="toyplot-canvas-Canvas" height="275.0px" id="t4db9cb876d69475395a93baea535ee6b" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 225.0 275.0" width="225.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t4f808d82842b4102b3d61bb7552378ed"><clipPath id="t978134186a8c458593a599ff18f1c62a"><rect height="275.0" width="225.0" x="0.0" y="0.0"></rect></clipPath><g clip-path="url(#t978134186a8c458593a599ff18f1c62a)"><g class="toyplot-mark-Text" id="te1827c7c4bcd4f3f9cc6a27e51e01c2e"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(151.45840367782654,218.34741288278775)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-7</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,195.24815205913413)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-6</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,172.14889123548048)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-5</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,149.04963041182683)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-4</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,125.95036958817319)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-3</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,102.85110876451954)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-2</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,79.7518479408659)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-1</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,56.652587117212263)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-0</text></g></g></g><g class="toyplot-mark-Graph" id="t1c7310cbb356476a99e95322502a91cc"><g class="toyplot-Edges"><path d="M 151.458403678 218.347412883 L 151.458403678 218.347412883" style="fill:none;stroke:rgb(66.3%,66.3%,66.3%);stroke-dasharray:2, 4;stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 151.458403678 195.248152059 L 151.458403678 195.248152059" style="fill:none;stroke:rgb(66.3%,66.3%,66.3%);stroke-dasharray:2, 4;stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 151.458403678 172.148891235 L 126.093802758 172.148891235" style="fill:none;stroke:rgb(66.3%,66.3%,66.3%);stroke-dasharray:2, 4;stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 151.458403678 149.049630412 L 151.458403678 149.049630412" style="fill:none;stroke:rgb(66.3%,66.3%,66.3%);stroke-dasharray:2, 4;stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 151.458403678 125.950369588 L 151.458403678 125.950369588" style="fill:none;stroke:rgb(66.3%,66.3%,66.3%);stroke-dasharray:2, 4;stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 151.458403678 102.851108765 L 126.093802758 102.851108765" style="fill:none;stroke:rgb(66.3%,66.3%,66.3%);stroke-dasharray:2, 4;stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 151.458403678 79.7518479409 L 100.729201839 79.7518479409" style="fill:none;stroke:rgb(66.3%,66.3%,66.3%);stroke-dasharray:2, 4;stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 151.458403678 56.6525871172 L 100.729201839 56.6525871172" style="fill:none;stroke:rgb(66.3%,66.3%,66.3%);stroke-dasharray:2, 4;stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><g class="toyplot-HeadMarkers"></g><g class="toyplot-MiddleMarkers"></g><g class="toyplot-TailMarkers"></g></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 218.34741288278775)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 195.24815205913413)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 172.14889123548048)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 149.04963041182683)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 125.95036958817319)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 102.85110876451954)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 79.7518479408659)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 56.652587117212263)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 218.34741288278775)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 195.24815205913413)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 172.14889123548048)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 149.04963041182683)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 125.95036958817319)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 102.85110876451954)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 79.7518479408659)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 56.652587117212263)"><circle r="0.0"></circle></g></g></g><g class="toyplot-mark-Graph" id="t1f568ebd8a5f4cdb959c33c697371308"><g class="toyplot-Edges"><path d="M 50.0 111.513331573 L 50.0 68.202217529" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 68.202217529 L 75.3646009195 68.202217529" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 111.513331573 L 50.0 154.824445618" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 154.824445618 L 75.3646009195 154.824445618" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 68.202217529 L 75.3646009195 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 56.6525871172 L 100.729201839 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 68.202217529 L 75.3646009195 79.7518479409" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 79.7518479409 L 100.729201839 79.7518479409" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 154.824445618 L 75.3646009195 120.175554382" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 120.175554382 L 100.729201839 120.175554382" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 154.824445618 L 75.3646009195 189.473336853" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 189.473336853 L 100.729201839 189.473336853" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 120.175554382 L 100.729201839 102.851108765" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 102.851108765 L 126.093802758 102.851108765" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 120.175554382 L 100.729201839 137.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 137.5 L 126.093802758 137.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 189.473336853 L 100.729201839 172.148891235" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 172.148891235 L 126.093802758 172.148891235" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 189.473336853 L 100.729201839 206.797782471" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 206.797782471 L 126.093802758 206.797782471" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 137.5 L 126.093802758 125.950369588" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 125.950369588 L 151.458403678 125.950369588" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 137.5 L 126.093802758 149.049630412" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 149.049630412 L 151.458403678 149.049630412" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 206.797782471 L 126.093802758 195.248152059" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 195.248152059 L 151.458403678 195.248152059" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 206.797782471 L 126.093802758 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 218.347412883 L 151.458403678 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><g class="toyplot-HeadMarkers"></g><g class="toyplot-MiddleMarkers"></g><g class="toyplot-TailMarkers"></g></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(50.0, 111.51333157338966)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(50.0, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(75.364600919456635, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(50.0, 154.82444561774025)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(75.364600919456635, 154.82444561774025)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(75.364600919456635, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(75.364600919456635, 56.652587117212263)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(100.72920183891327, 56.652587117212263)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(75.364600919456635, 79.7518479408659)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(100.72920183891327, 79.7518479408659)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(75.364600919456635, 154.82444561774025)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(75.364600919456635, 120.17555438225978)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(100.72920183891327, 120.17555438225978)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(75.364600919456635, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(100.72920183891327, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(100.72920183891327, 120.17555438225978)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(100.72920183891327, 102.85110876451954)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(126.09380275836992, 102.85110876451954)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(100.72920183891327, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(126.09380275836992, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(100.72920183891327, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(100.72920183891327, 172.14889123548048)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(126.09380275836992, 172.14889123548048)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(100.72920183891327, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(126.09380275836992, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(126.09380275836992, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(126.09380275836992, 125.95036958817319)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(151.45840367782654, 125.95036958817319)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(126.09380275836992, 149.04963041182683)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(151.45840367782654, 149.04963041182683)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(126.09380275836992, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(126.09380275836992, 195.24815205913413)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(151.45840367782654, 195.24815205913413)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(126.09380275836992, 218.34741288278775)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(151.45840367782654, 218.34741288278775)"><circle r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t015f414ad84d4f22a1817bfa4b6431f9"><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 218.34741288278775)"><title>idx: 0
name: t-7
dist: 1
support: 100
height: 0</title><circle r="7.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">0</text></g></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 195.24815205913413)"><title>idx: 1
name: t-6
dist: 1
support: 100
height: 0</title><circle r="7.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">0</text></g></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(126.09380275836992, 172.14889123548048)"><title>idx: 2
name: t-5
dist: 1
support: 100
height: 1</title><circle r="7.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">1</text></g></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 149.04963041182683)"><title>idx: 3
name: t-4
dist: 1
support: 100
height: 0</title><circle r="7.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">0</text></g></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 125.95036958817319)"><title>idx: 4
name: t-3
dist: 1
support: 100
height: 0</title><circle r="7.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">0</text></g></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(126.09380275836992, 102.85110876451954)"><title>idx: 5
name: t-2
dist: 1
support: 100
height: 1</title><circle r="7.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">1</text></g></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(100.72920183891327, 79.7518479408659)"><title>idx: 6
name: t-1
dist: 1
support: 100
height: 2</title><circle r="7.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">2</text></g></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(100.72920183891327, 56.652587117212263)"><title>idx: 7
name: t-0
dist: 1
support: 100
height: 2</title><circle r="7.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">2</text></g></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(126.09380275836992, 206.79778247096093)"><title>idx: 8
name: i8
dist: 1
support: 1
height: 1</title><circle r="7.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">1</text></g></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(126.09380275836992, 137.5)"><title>idx: 10
name: i10
dist: 1
support: 1
height: 2</title><circle r="7.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">1</text></g></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(100.72920183891327, 189.4733368532207)"><title>idx: 9
name: i9
dist: 1
support: 1
height: 1</title><circle r="7.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">2</text></g></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(100.72920183891327, 120.17555438225978)"><title>idx: 11
name: i11
dist: 1
support: 1
height: 2</title><circle r="7.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">2</text></g></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(75.364600919456635, 154.82444561774025)"><title>idx: 12
name: i12
dist: 1
support: 1
height: 3</title><circle r="7.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">3</text></g></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(75.364600919456635, 68.202217529039075)"><title>idx: 13
name: i13
dist: 1
support: 1
height: 3</title><circle r="7.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">3</text></g></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(50.0, 111.51333157338966)"><title>idx: 14
name: i14
dist: 0
support: 100
height: 4</title><circle r="7.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">4</text></g></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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
modules["toyplot/root/id"] = "t85ae6c5b1cc84538bf43fb12cfdff4e7";
modules["toyplot/root"] = (function(root_id)
    {
        return document.querySelector("#" + root_id);
    })(modules["toyplot/root/id"]);
modules["toyplot/canvas/id"] = "t4db9cb876d69475395a93baea535ee6b";
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t1c7310cbb356476a99e95322502a91cc","vertex_data","graph vertex data",["x", "y"],[[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0, 0.0, 0.0, -1.0, -2.0, -2.0], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t1c7310cbb356476a99e95322502a91cc","edge_data","graph edge data",["source", "target"],[[0, 1, 2, 3, 4, 5, 6, 7], [8, 9, 10, 11, 12, 13, 14, 15]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t1f568ebd8a5f4cdb959c33c697371308","vertex_data","graph vertex data",["x", "y"],[[-4.0, -4.0, -3.0, -4.0, -3.0, -3.0, -3.0, -2.0, -3.0, -2.0, -3.0, -3.0, -2.0, -3.0, -2.0, -2.0, -2.0, -1.0, -2.0, -1.0, -2.0, -2.0, -1.0, -2.0, -1.0, -1.0, -1.0, 0.0, -1.0, 0.0, -1.0, -1.0, 0.0, -1.0, 0.0], [4.625, 6.5, 6.5, 2.75, 2.75, 6.5, 7.0, 7.0, 6.0, 6.0, 2.75, 4.25, 4.25, 1.25, 1.25, 4.25, 5.0, 5.0, 3.5, 3.5, 1.25, 2.0, 2.0, 0.5, 0.5, 3.5, 4.0, 4.0, 3.0, 3.0, 0.5, 1.0, 1.0, 0.0, 0.0]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t1f568ebd8a5f4cdb959c33c697371308","edge_data","graph edge data",["source", "target"],[[0, 1, 0, 3, 5, 6, 5, 8, 10, 11, 10, 13, 15, 16, 15, 18, 20, 21, 20, 23, 25, 26, 25, 28, 30, 31, 30, 33], [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t015f414ad84d4f22a1817bfa4b6431f9","data","scatterplot",["x", "y0"],[[0.0, 0.0, -1.0, 0.0, 0.0, -1.0, -2.0, -2.0, -1.0, -1.0, -2.0, -2.0, -3.0, -3.0, -4.0], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 0.5, 3.5, 1.25, 4.25, 2.75, 6.5, 4.625]],"toyplot");
})();</script></div></div>


### toytree.tree (ete3mini.Tree)
The toytree.tree object is an `ete3mini.Tree` object which has nearly all of the same functionality as a standard ete tree. Thus, you can read the very detailed [ete documentation](http://etetoolkit.org) if you want a very detailed understanding of the object. Most users will not need to interact with this object, however, if you want to annotate your tree with extendable meta-data knowing how to do that can be very useful. 


```python
## the .tree attribute is the tree structure in memory
## which accesses the root node initially
tre.tree
```




    Tree node 'i14' (0x7fed620fbd5)



### Traversing/modifying the tree


```python
## traverse the tree and access node attributes
for node in tre.tree.traverse(strategy="levelorder"):
    print "{:<5} {:<5} {:<5} {:<5}"\
          .format(node.idx, node.name, node.is_leaf(), node.is_root())
```

    14    i14   0     1    
    13    i13   0     0    
    12    i12   0     0    
    7     t-0   1     0    
    6     t-1   1     0    
    11    i11   0     0    
    10    i10   0     0    
    5     t-2   1     0    
    9     i9    0     0    
    2     t-5   1     0    
    8     i8    0     0    
    4     t-3   1     0    
    3     t-4   1     0    
    1     t-6   1     0    
    0     t-7   1     0    



```python
## traverse the tree and modify nodes (add new 'color' feature)
for node in tre.tree.traverse():
    if node.is_leaf():
        node.color=tre.colors[1]
    else:
        node.color=tre.colors[2]
        
## draw tree using new 'color' attribute
colors = tre.get_node_values('color', show_root=1, show_tips=1)
tre.draw(node_labels=True, node_color=colors, node_size=12);
```


<div class="toyplot" id="t8fd56753e4434d24a4fdf33b2d2fab2e" style="text-align:center"><svg class="toyplot-canvas-Canvas" height="275.0px" id="td7c2753c3b3f4ad293262d6644f3ff43" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 225.0 275.0" width="225.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="tf35c781731f44624be89e13f428ce8bc"><clipPath id="t1fe22ed83388489bb5d4adac7390ddda"><rect height="275.0" width="225.0" x="0.0" y="0.0"></rect></clipPath><g clip-path="url(#t1fe22ed83388489bb5d4adac7390ddda)"><g class="toyplot-mark-Text" id="t6015f6e243324f06b971ce911bc91618"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(151.45840367782654,218.34741288278775)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-7</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,195.24815205913413)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-6</text></g><g class="toyplot-Datum" transform="translate(126.09380275836992,172.14889123548048)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-5</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,149.04963041182683)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-4</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,125.95036958817319)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-3</text></g><g class="toyplot-Datum" transform="translate(126.09380275836992,102.85110876451954)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-2</text></g><g class="toyplot-Datum" transform="translate(100.72920183891327,79.7518479408659)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-1</text></g><g class="toyplot-Datum" transform="translate(100.72920183891327,56.652587117212263)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-0</text></g></g></g><g class="toyplot-mark-Graph" id="t4fa7f90563324b858224c58f639ddc4f"><g class="toyplot-Edges"><path d="M 50.0 111.513331573 L 50.0 68.202217529" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 68.202217529 L 75.3646009195 68.202217529" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 111.513331573 L 50.0 154.824445618" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 154.824445618 L 75.3646009195 154.824445618" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 68.202217529 L 75.3646009195 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 56.6525871172 L 100.729201839 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 68.202217529 L 75.3646009195 79.7518479409" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 79.7518479409 L 100.729201839 79.7518479409" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 154.824445618 L 75.3646009195 120.175554382" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 120.175554382 L 100.729201839 120.175554382" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 154.824445618 L 75.3646009195 189.473336853" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 189.473336853 L 100.729201839 189.473336853" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 120.175554382 L 100.729201839 102.851108765" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 102.851108765 L 126.093802758 102.851108765" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 120.175554382 L 100.729201839 137.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 137.5 L 126.093802758 137.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 189.473336853 L 100.729201839 172.148891235" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 172.148891235 L 126.093802758 172.148891235" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 189.473336853 L 100.729201839 206.797782471" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 206.797782471 L 126.093802758 206.797782471" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 137.5 L 126.093802758 125.950369588" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 125.950369588 L 151.458403678 125.950369588" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 137.5 L 126.093802758 149.049630412" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 149.049630412 L 151.458403678 149.049630412" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 206.797782471 L 126.093802758 195.248152059" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 195.248152059 L 151.458403678 195.248152059" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 206.797782471 L 126.093802758 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 218.347412883 L 151.458403678 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><g class="toyplot-HeadMarkers"></g><g class="toyplot-MiddleMarkers"></g><g class="toyplot-TailMarkers"></g></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 111.51333157338966)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 154.82444561774025)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 154.82444561774025)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 56.652587117212263)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 56.652587117212263)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 79.7518479408659)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 79.7518479408659)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 154.82444561774025)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 120.17555438225978)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 120.17555438225978)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 120.17555438225978)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 102.85110876451954)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 102.85110876451954)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 172.14889123548048)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 172.14889123548048)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 125.95036958817319)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 125.95036958817319)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 149.04963041182683)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 149.04963041182683)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 195.24815205913413)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 195.24815205913413)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 218.34741288278775)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 218.34741288278775)"><circle r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t03da70b4014547ea8b9f7228cfcd0b22"><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 218.34741288278775)"><title>idx: 0
name: t-7
dist: 1
support: 100
height: 0</title><circle r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 195.24815205913413)"><title>idx: 1
name: t-6
dist: 1
support: 100
height: 0</title><circle r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(126.09380275836992, 172.14889123548048)"><title>idx: 2
name: t-5
dist: 1
support: 100
height: 1</title><circle r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 149.04963041182683)"><title>idx: 3
name: t-4
dist: 1
support: 100
height: 0</title><circle r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 125.95036958817319)"><title>idx: 4
name: t-3
dist: 1
support: 100
height: 0</title><circle r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(126.09380275836992, 102.85110876451954)"><title>idx: 5
name: t-2
dist: 1
support: 100
height: 1</title><circle r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(100.72920183891327, 79.7518479408659)"><title>idx: 6
name: t-1
dist: 1
support: 100
height: 2</title><circle r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(100.72920183891327, 56.652587117212263)"><title>idx: 7
name: t-0
dist: 1
support: 100
height: 2</title><circle r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(126.09380275836992, 206.79778247096093)"><title>idx: 8
name: i8
dist: 1
support: 1
height: 1</title><circle r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(126.09380275836992, 137.5)"><title>idx: 10
name: i10
dist: 1
support: 1
height: 2</title><circle r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(100.72920183891327, 189.4733368532207)"><title>idx: 9
name: i9
dist: 1
support: 1
height: 1</title><circle r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(100.72920183891327, 120.17555438225978)"><title>idx: 11
name: i11
dist: 1
support: 1
height: 2</title><circle r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(75.364600919456635, 154.82444561774025)"><title>idx: 12
name: i12
dist: 1
support: 1
height: 3</title><circle r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(75.364600919456635, 68.202217529039075)"><title>idx: 13
name: i13
dist: 1
support: 1
height: 3</title><circle r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(50.0, 111.51333157338966)"><title>idx: 14
name: i14
dist: 0
support: 100
height: 4</title><circle r="6.0"></circle></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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
modules["toyplot/root/id"] = "t8fd56753e4434d24a4fdf33b2d2fab2e";
modules["toyplot/root"] = (function(root_id)
    {
        return document.querySelector("#" + root_id);
    })(modules["toyplot/root/id"]);
modules["toyplot/canvas/id"] = "td7c2753c3b3f4ad293262d6644f3ff43";
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t4fa7f90563324b858224c58f639ddc4f","vertex_data","graph vertex data",["x", "y"],[[-4.0, -4.0, -3.0, -4.0, -3.0, -3.0, -3.0, -2.0, -3.0, -2.0, -3.0, -3.0, -2.0, -3.0, -2.0, -2.0, -2.0, -1.0, -2.0, -1.0, -2.0, -2.0, -1.0, -2.0, -1.0, -1.0, -1.0, 0.0, -1.0, 0.0, -1.0, -1.0, 0.0, -1.0, 0.0], [4.625, 6.5, 6.5, 2.75, 2.75, 6.5, 7.0, 7.0, 6.0, 6.0, 2.75, 4.25, 4.25, 1.25, 1.25, 4.25, 5.0, 5.0, 3.5, 3.5, 1.25, 2.0, 2.0, 0.5, 0.5, 3.5, 4.0, 4.0, 3.0, 3.0, 0.5, 1.0, 1.0, 0.0, 0.0]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t4fa7f90563324b858224c58f639ddc4f","edge_data","graph edge data",["source", "target"],[[0, 1, 0, 3, 5, 6, 5, 8, 10, 11, 10, 13, 15, 16, 15, 18, 20, 21, 20, 23, 25, 26, 25, 28, 30, 31, 30, 33], [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t03da70b4014547ea8b9f7228cfcd0b22","data","scatterplot",["x", "y0"],[[0.0, 0.0, -1.0, 0.0, 0.0, -1.0, -2.0, -2.0, -1.0, -1.0, -2.0, -2.0, -3.0, -3.0, -4.0], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 0.5, 3.5, 1.25, 4.25, 2.75, 6.5, 4.625]],"toyplot");
})();</script></div></div>


### toytree.edges
This is an array of edges connecting nodes. For example, node 1 connects to node 9, and node 1 connects to node 10. This is used to draw the tree and should generally not be modified by a user.


```python
tre.edges
```




    array([[13,  7],
           [13,  6],
           [14, 13],
           [11,  5],
           [ 9,  4],
           [ 9,  3],
           [11,  9],
           [12, 11],
           [10,  2],
           [ 8,  1],
           [ 8,  0],
           [10,  8],
           [12, 10],
           [14, 12]])



### toytree.verts
This is an array with the coordinate locations of the vertices (nodes) of the tree. This is used to draw the tree, however, it can also be useful to the user. For example, you can enter in the vertex coordinates to add additional points to the tree after plotting. Below is an example. 


```python
## show the verts array
tre.verts
```




    array([[ 0.   ,  0.   ],
           [ 0.   ,  1.   ],
           [-1.   ,  2.   ],
           [ 0.   ,  3.   ],
           [ 0.   ,  4.   ],
           [-1.   ,  5.   ],
           [-2.   ,  6.   ],
           [-2.   ,  7.   ],
           [-1.   ,  0.5  ],
           [-1.   ,  3.5  ],
           [-2.   ,  1.25 ],
           [-2.   ,  4.25 ],
           [-3.   ,  2.75 ],
           [-3.   ,  6.5  ],
           [-4.   ,  4.625]])




```python
## draw a tree
canvas, axes = tre.draw();

## add scatterplot points to the axes (standard toyplot plotting)
axes.scatterplot(
    a=tre.verts[:, 0],
    b=tre.verts[:, 1],
    size=12,
    marker='>'
    );
```


<div class="toyplot" id="t9f83abdfde1445f89493002fccb44567" style="text-align:center"><svg class="toyplot-canvas-Canvas" height="275.0px" id="t1f53eb41f104444a8297e4cbbd7f97b3" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 225.0 275.0" width="225.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t8465bef542224df386fa7a8d8452f8dc"><clipPath id="t4508cb7992fc413abdae854f321db99d"><rect height="275.0" width="225.0" x="0.0" y="0.0"></rect></clipPath><g clip-path="url(#t4508cb7992fc413abdae854f321db99d)"><g class="toyplot-mark-Text" id="t394bedef28db43318277e48129674e81"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(151.45840367782654,218.34741288278775)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-7</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,195.24815205913413)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-6</text></g><g class="toyplot-Datum" transform="translate(126.09380275836992,172.14889123548048)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-5</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,149.04963041182683)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-4</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,125.95036958817319)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-3</text></g><g class="toyplot-Datum" transform="translate(126.09380275836992,102.85110876451954)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-2</text></g><g class="toyplot-Datum" transform="translate(100.72920183891327,79.7518479408659)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-1</text></g><g class="toyplot-Datum" transform="translate(100.72920183891327,56.652587117212263)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-0</text></g></g></g><g class="toyplot-mark-Graph" id="tb7226ea2cbbb44a193ba2a59703ccfc5"><g class="toyplot-Edges"><path d="M 50.0 111.513331573 L 50.0 68.202217529" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 68.202217529 L 75.3646009195 68.202217529" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 111.513331573 L 50.0 154.824445618" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 154.824445618 L 75.3646009195 154.824445618" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 68.202217529 L 75.3646009195 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 56.6525871172 L 100.729201839 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 68.202217529 L 75.3646009195 79.7518479409" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 79.7518479409 L 100.729201839 79.7518479409" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 154.824445618 L 75.3646009195 120.175554382" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 120.175554382 L 100.729201839 120.175554382" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 154.824445618 L 75.3646009195 189.473336853" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 75.3646009195 189.473336853 L 100.729201839 189.473336853" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 120.175554382 L 100.729201839 102.851108765" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 102.851108765 L 126.093802758 102.851108765" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 120.175554382 L 100.729201839 137.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 137.5 L 126.093802758 137.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 189.473336853 L 100.729201839 172.148891235" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 172.148891235 L 126.093802758 172.148891235" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 189.473336853 L 100.729201839 206.797782471" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 100.729201839 206.797782471 L 126.093802758 206.797782471" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 137.5 L 126.093802758 125.950369588" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 125.950369588 L 151.458403678 125.950369588" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 137.5 L 126.093802758 149.049630412" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 149.049630412 L 151.458403678 149.049630412" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 206.797782471 L 126.093802758 195.248152059" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 195.248152059 L 151.458403678 195.248152059" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 206.797782471 L 126.093802758 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 126.093802758 218.347412883 L 151.458403678 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><g class="toyplot-HeadMarkers"></g><g class="toyplot-MiddleMarkers"></g><g class="toyplot-TailMarkers"></g></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 111.51333157338966)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 154.82444561774025)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 154.82444561774025)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 56.652587117212263)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 56.652587117212263)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 79.7518479408659)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 79.7518479408659)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 154.82444561774025)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 120.17555438225978)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 120.17555438225978)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 120.17555438225978)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 102.85110876451954)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 102.85110876451954)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 172.14889123548048)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 172.14889123548048)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 125.95036958817319)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 125.95036958817319)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 149.04963041182683)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 149.04963041182683)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 195.24815205913413)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 195.24815205913413)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 218.34741288278775)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 218.34741288278775)"><circle r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="tb6e5ef5f81494e27b133e4c0b4b5e575"><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 218.34741288278775)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(90)"></polygon></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 195.24815205913413)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(90)"></polygon></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 172.14889123548048)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(90)"></polygon></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 149.04963041182683)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(90)"></polygon></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 125.95036958817319)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(90)"></polygon></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 102.85110876451954)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(90)"></polygon></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 79.7518479408659)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(90)"></polygon></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 56.652587117212263)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(90)"></polygon></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 206.79778247096093)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(90)"></polygon></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(126.09380275836992, 137.5)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(90)"></polygon></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 189.4733368532207)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(90)"></polygon></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(100.72920183891327, 120.17555438225978)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(90)"></polygon></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 154.82444561774025)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(90)"></polygon></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(75.364600919456635, 68.202217529039075)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(90)"></polygon></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 111.51333157338966)"><polygon points="-6.0,6.0 0,-6.0 6.0,6.0" transform="rotate(90)"></polygon></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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
modules["toyplot/root/id"] = "t9f83abdfde1445f89493002fccb44567";
modules["toyplot/root"] = (function(root_id)
    {
        return document.querySelector("#" + root_id);
    })(modules["toyplot/root/id"]);
modules["toyplot/canvas/id"] = "t1f53eb41f104444a8297e4cbbd7f97b3";
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"tb7226ea2cbbb44a193ba2a59703ccfc5","vertex_data","graph vertex data",["x", "y"],[[-4.0, -4.0, -3.0, -4.0, -3.0, -3.0, -3.0, -2.0, -3.0, -2.0, -3.0, -3.0, -2.0, -3.0, -2.0, -2.0, -2.0, -1.0, -2.0, -1.0, -2.0, -2.0, -1.0, -2.0, -1.0, -1.0, -1.0, 0.0, -1.0, 0.0, -1.0, -1.0, 0.0, -1.0, 0.0], [4.625, 6.5, 6.5, 2.75, 2.75, 6.5, 7.0, 7.0, 6.0, 6.0, 2.75, 4.25, 4.25, 1.25, 1.25, 4.25, 5.0, 5.0, 3.5, 3.5, 1.25, 2.0, 2.0, 0.5, 0.5, 3.5, 4.0, 4.0, 3.0, 3.0, 0.5, 1.0, 1.0, 0.0, 0.0]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"tb7226ea2cbbb44a193ba2a59703ccfc5","edge_data","graph edge data",["source", "target"],[[0, 1, 0, 3, 5, 6, 5, 8, 10, 11, 10, 13, 15, 16, 15, 18, 20, 21, 20, 23, 25, 26, 25, 28, 30, 31, 30, 33], [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"tb6e5ef5f81494e27b133e4c0b4b5e575","data","scatterplot",["x", "y0"],[[0.0, 0.0, -1.0, 0.0, 0.0, -1.0, -2.0, -2.0, -1.0, -1.0, -2.0, -2.0, -3.0, -3.0, -4.0], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 0.5, 3.5, 1.25, 4.25, 2.75, 6.5, 4.625]],"toyplot");
})();</script></div></div>


### toytree.root
The root function can be used to re-root a tree. 


```python
## root on a list of names
rtre = tre.root(["t-0", "t-1"])

## or root on a regex selector (here all matches in 7-9)
rtre = tre.root(regex="t-[6-7]")
```


```python
rtre.draw();
```


<div class="toyplot" id="t485ac6e1e7a344a6a859a840680d6e32" style="text-align:center"><svg class="toyplot-canvas-Canvas" height="275.0px" id="t0d6632d98e1e4c9bbbb2314cb09934d8" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 225.0 275.0" width="225.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="tb224f6816d7d4b809daf5ea175382e11"><clipPath id="t6e2d49fa35684727b554524dcb67f8ea"><rect height="275.0" width="225.0" x="0.0" y="0.0"></rect></clipPath><g clip-path="url(#t6e2d49fa35684727b554524dcb67f8ea)"><g class="toyplot-mark-Text" id="t8e2dfe2437bc4552943c9343d1f13390"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(151.45840367782654,218.34741288278775)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-4</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,195.24815205913413)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-3</text></g><g class="toyplot-Datum" transform="translate(128.91209174942065,172.14889123548048)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-2</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,149.04963041182683)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-1</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,125.95036958817319)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-0</text></g><g class="toyplot-Datum" transform="translate(83.819467892608856,102.85110876451954)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-5</text></g><g class="toyplot-Datum" transform="translate(83.819467892608856,79.7518479408659)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-7</text></g><g class="toyplot-Datum" transform="translate(83.819467892608856,56.652587117212263)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-6</text></g></g></g><g class="toyplot-mark-Graph" id="t13bb6781377142e1b335a67aeba9e25f"><g class="toyplot-Edges"><path d="M 50.0 100.685553062 L 50.0 68.202217529" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 68.202217529 L 61.2731559642 68.202217529" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 100.685553062 L 50.0 133.168888596" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 133.168888596 L 61.2731559642 133.168888596" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 68.202217529 L 61.2731559642 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 56.6525871172 L 83.8194678926 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 68.202217529 L 61.2731559642 79.7518479409" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 79.7518479409 L 83.8194678926 79.7518479409" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 133.168888596 L 61.2731559642 102.851108765" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 102.851108765 L 83.8194678926 102.851108765" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 133.168888596 L 61.2731559642 163.486668427" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 163.486668427 L 83.8194678926 163.486668427" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 83.8194678926 163.486668427 L 83.8194678926 137.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 83.8194678926 137.5 L 128.912091749 137.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 83.8194678926 163.486668427 L 83.8194678926 189.473336853" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 83.8194678926 189.473336853 L 106.365779821 189.473336853" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 137.5 L 128.912091749 125.950369588" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 125.950369588 L 151.458403678 125.950369588" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 137.5 L 128.912091749 149.049630412" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 149.049630412 L 151.458403678 149.049630412" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 106.365779821 189.473336853 L 106.365779821 172.148891235" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 106.365779821 172.148891235 L 128.912091749 172.148891235" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 106.365779821 189.473336853 L 106.365779821 206.797782471" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 106.365779821 206.797782471 L 128.912091749 206.797782471" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 206.797782471 L 128.912091749 195.248152059" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 195.248152059 L 151.458403678 195.248152059" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 206.797782471 L 128.912091749 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 218.347412883 L 151.458403678 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><g class="toyplot-HeadMarkers"></g><g class="toyplot-MiddleMarkers"></g><g class="toyplot-TailMarkers"></g></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 100.68555306230201)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 133.16888859556497)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 133.16888859556497)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 56.652587117212263)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 56.652587117212263)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 79.7518479408659)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 79.7518479408659)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 133.16888859556497)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 102.85110876451954)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 102.85110876451954)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 163.48666842661035)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 163.48666842661035)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 163.48666842661035)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(106.36577982101474, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 125.95036958817319)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 125.95036958817319)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 149.04963041182683)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 149.04963041182683)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(106.36577982101474, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(106.36577982101474, 172.14889123548048)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 172.14889123548048)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(106.36577982101474, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 195.24815205913413)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 195.24815205913413)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 218.34741288278775)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 218.34741288278775)"><circle r="0.0"></circle></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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
modules["toyplot/root/id"] = "t485ac6e1e7a344a6a859a840680d6e32";
modules["toyplot/root"] = (function(root_id)
    {
        return document.querySelector("#" + root_id);
    })(modules["toyplot/root/id"]);
modules["toyplot/canvas/id"] = "t0d6632d98e1e4c9bbbb2314cb09934d8";
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t13bb6781377142e1b335a67aeba9e25f","vertex_data","graph vertex data",["x", "y"],[[-4.5, -4.5, -4.0, -4.5, -4.0, -4.0, -4.0, -3.0, -4.0, -3.0, -4.0, -4.0, -3.0, -4.0, -3.0, -3.0, -3.0, -1.0, -3.0, -2.0, -1.0, -1.0, 0.0, -1.0, 0.0, -2.0, -2.0, -1.0, -2.0, -1.0, -1.0, -1.0, 0.0, -1.0, 0.0], [5.09375, 6.5, 6.5, 3.6875, 3.6875, 6.5, 7.0, 7.0, 6.0, 6.0, 3.6875, 5.0, 5.0, 2.375, 2.375, 2.375, 3.5, 3.5, 1.25, 1.25, 3.5, 4.0, 4.0, 3.0, 3.0, 1.25, 2.0, 2.0, 0.5, 0.5, 0.5, 1.0, 1.0, 0.0, 0.0]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t13bb6781377142e1b335a67aeba9e25f","edge_data","graph edge data",["source", "target"],[[0, 1, 0, 3, 5, 6, 5, 8, 10, 11, 10, 13, 15, 16, 15, 18, 20, 21, 20, 23, 25, 26, 25, 28, 30, 31, 30, 33], [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34]],"toyplot");
})();</script></div></div>



```python
## root (pinches an edge to create a new node)
rtre = tre.root(regex="t-[6-7]")
rtre.draw(node_labels="name")

## unroot (erases a node)
utre = rtre.unroot()
utre.draw(node_labels="name")

## re-root (adds new node with name 'rerooted')
ntre = utre.root(regex="t-[6-7]")
ntre.tree.ladderize()
ntre.draw(node_labels="name");
```


<div class="toyplot" id="t6db0e0ef51824913b9b5081db2e9cdb6" style="text-align:center"><svg class="toyplot-canvas-Canvas" height="275.0px" id="tb28b7e30f8464f508bdb5e7fe546b5e4" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 225.0 275.0" width="225.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t9f760d9d95344d4eb2e296b078749587"><clipPath id="tac90e8f5d4914ef08fc27a583827bf2c"><rect height="275.0" width="225.0" x="0.0" y="0.0"></rect></clipPath><g clip-path="url(#tac90e8f5d4914ef08fc27a583827bf2c)"><g class="toyplot-mark-Text" id="t40128fb2ba1a4f818dac05aba119e140"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(151.45840367782654,218.34741288278775)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-4</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,195.24815205913413)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-3</text></g><g class="toyplot-Datum" transform="translate(128.91209174942065,172.14889123548048)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-2</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,149.04963041182683)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-1</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,125.95036958817319)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-0</text></g><g class="toyplot-Datum" transform="translate(83.819467892608856,102.85110876451954)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-5</text></g><g class="toyplot-Datum" transform="translate(83.819467892608856,79.7518479408659)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-7</text></g><g class="toyplot-Datum" transform="translate(83.819467892608856,56.652587117212263)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-6</text></g></g></g><g class="toyplot-mark-Graph" id="t9ec9869be401486c9daf0449dd648313"><g class="toyplot-Edges"><path d="M 50.0 100.685553062 L 50.0 68.202217529" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 68.202217529 L 61.2731559642 68.202217529" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 100.685553062 L 50.0 133.168888596" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 133.168888596 L 61.2731559642 133.168888596" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 68.202217529 L 61.2731559642 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 56.6525871172 L 83.8194678926 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 68.202217529 L 61.2731559642 79.7518479409" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 79.7518479409 L 83.8194678926 79.7518479409" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 133.168888596 L 61.2731559642 102.851108765" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 102.851108765 L 83.8194678926 102.851108765" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 133.168888596 L 61.2731559642 163.486668427" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 163.486668427 L 83.8194678926 163.486668427" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 83.8194678926 163.486668427 L 83.8194678926 137.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 83.8194678926 137.5 L 128.912091749 137.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 83.8194678926 163.486668427 L 83.8194678926 189.473336853" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 83.8194678926 189.473336853 L 106.365779821 189.473336853" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 137.5 L 128.912091749 125.950369588" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 125.950369588 L 151.458403678 125.950369588" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 137.5 L 128.912091749 149.049630412" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 149.049630412 L 151.458403678 149.049630412" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 106.365779821 189.473336853 L 106.365779821 172.148891235" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 106.365779821 172.148891235 L 128.912091749 172.148891235" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 106.365779821 189.473336853 L 106.365779821 206.797782471" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 106.365779821 206.797782471 L 128.912091749 206.797782471" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 206.797782471 L 128.912091749 195.248152059" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 195.248152059 L 151.458403678 195.248152059" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 206.797782471 L 128.912091749 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 218.347412883 L 151.458403678 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><g class="toyplot-HeadMarkers"></g><g class="toyplot-MiddleMarkers"></g><g class="toyplot-TailMarkers"></g></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 100.68555306230201)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 133.16888859556497)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 133.16888859556497)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 56.652587117212263)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 56.652587117212263)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 79.7518479408659)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 79.7518479408659)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 133.16888859556497)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 102.85110876451954)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 102.85110876451954)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 163.48666842661035)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 163.48666842661035)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 163.48666842661035)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(106.36577982101474, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 125.95036958817319)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 125.95036958817319)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 149.04963041182683)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 149.04963041182683)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(106.36577982101474, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(106.36577982101474, 172.14889123548048)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 172.14889123548048)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(106.36577982101474, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 195.24815205913413)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 195.24815205913413)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 218.34741288278775)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 218.34741288278775)"><circle r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t36d96d20aefb40208020551b0e6da65b"><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 218.34741288278775)"><title>idx: 0
name: t-4
dist: 1.0
support: 100
height: 0.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-4</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 195.24815205913413)"><title>idx: 1
name: t-3
dist: 1.0
support: 100
height: 0.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-3</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(128.91209174942065, 172.14889123548048)"><title>idx: 2
name: t-2
dist: 1.0
support: 100
height: 1.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-2</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 149.04963041182683)"><title>idx: 3
name: t-1
dist: 1.0
support: 100
height: 0.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-1</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 125.95036958817319)"><title>idx: 4
name: t-0
dist: 1.0
support: 100
height: 0.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-0</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(83.819467892608856, 102.85110876451954)"><title>idx: 5
name: t-5
dist: 1.0
support: 100
height: 3.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-5</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(83.819467892608856, 79.7518479408659)"><title>idx: 6
name: t-7
dist: 1.0
support: 100
height: 3.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-7</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(83.819467892608856, 56.652587117212263)"><title>idx: 7
name: t-6
dist: 1.0
support: 100
height: 3.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-6</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(128.91209174942065, 206.79778247096093)"><title>idx: 8
name: i9
dist: 1.0
support: 1
height: 1.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-3.501" y="2.2995">i9</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(106.36577982101474, 189.4733368532207)"><title>idx: 9
name: i11
dist: 1.0
support: 1
height: 2.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-6.003" y="2.2995">i11</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(128.91209174942065, 137.5)"><title>idx: 10
name: i13
dist: 2.0
support: 1
height: 1.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-6.003" y="2.2995">i13</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(83.819467892608856, 163.48666842661035)"><title>idx: 11
name: i12
dist: 1.0
support: 1
height: 3.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-6.003" y="2.2995">i12</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(61.273155964202957, 133.16888859556497)"><title>idx: 12
name: i10
dist: 0.5
support: 1
height: 4.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-6.003" y="2.2995">i10</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(61.273155964202957, 68.202217529039075)"><title>idx: 13
name: i8
dist: 0.5
support: 1
height: 4.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-3.501" y="2.2995">i8</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(50.0, 100.68555306230201)"><title>idx: 14
name: i14
dist: 0.0
support: 100
height: 4.5</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-6.003" y="2.2995">i14</text></g></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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
modules["toyplot/root/id"] = "t6db0e0ef51824913b9b5081db2e9cdb6";
modules["toyplot/root"] = (function(root_id)
    {
        return document.querySelector("#" + root_id);
    })(modules["toyplot/root/id"]);
modules["toyplot/canvas/id"] = "tb28b7e30f8464f508bdb5e7fe546b5e4";
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t9ec9869be401486c9daf0449dd648313","vertex_data","graph vertex data",["x", "y"],[[-4.5, -4.5, -4.0, -4.5, -4.0, -4.0, -4.0, -3.0, -4.0, -3.0, -4.0, -4.0, -3.0, -4.0, -3.0, -3.0, -3.0, -1.0, -3.0, -2.0, -1.0, -1.0, 0.0, -1.0, 0.0, -2.0, -2.0, -1.0, -2.0, -1.0, -1.0, -1.0, 0.0, -1.0, 0.0], [5.09375, 6.5, 6.5, 3.6875, 3.6875, 6.5, 7.0, 7.0, 6.0, 6.0, 3.6875, 5.0, 5.0, 2.375, 2.375, 2.375, 3.5, 3.5, 1.25, 1.25, 3.5, 4.0, 4.0, 3.0, 3.0, 1.25, 2.0, 2.0, 0.5, 0.5, 0.5, 1.0, 1.0, 0.0, 0.0]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t9ec9869be401486c9daf0449dd648313","edge_data","graph edge data",["source", "target"],[[0, 1, 0, 3, 5, 6, 5, 8, 10, 11, 10, 13, 15, 16, 15, 18, 20, 21, 20, 23, 25, 26, 25, 28, 30, 31, 30, 33], [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t36d96d20aefb40208020551b0e6da65b","data","scatterplot",["x", "y0"],[[0.0, 0.0, -1.0, 0.0, 0.0, -3.0, -3.0, -3.0, -1.0, -2.0, -1.0, -3.0, -4.0, -4.0, -4.5], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 0.5, 1.25, 3.5, 2.375, 3.6875, 6.5, 5.09375]],"toyplot");
})();</script></div></div>



<div class="toyplot" id="tc72c6a145944490a9275e0b3f889631e" style="text-align:center"><svg class="toyplot-canvas-Canvas" height="275.0px" id="tc0fb515c05114b929d3b0c2e9d3d2e34" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 225.0 275.0" width="225.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t7ec8d038633c44f2851e59c40153be3c"><clipPath id="t7737b371b41641908a9573ada5967183"><rect height="275.0" width="225.0" x="0.0" y="0.0"></rect></clipPath><g clip-path="url(#t7737b371b41641908a9573ada5967183)"><g class="toyplot-mark-Text" id="tc44c4bcb4fed434c89caf4c797738a20"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(151.45840367782654,218.34741288278775)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-4</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,195.24815205913413)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-3</text></g><g class="toyplot-Datum" transform="translate(128.91209174942065,172.14889123548048)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-2</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,149.04963041182683)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-1</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,125.95036958817319)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-0</text></g><g class="toyplot-Datum" transform="translate(83.819467892608856,102.85110876451954)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-5</text></g><g class="toyplot-Datum" transform="translate(72.546311928405899,79.7518479408659)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-7</text></g><g class="toyplot-Datum" transform="translate(72.546311928405899,56.652587117212263)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-6</text></g></g></g><g class="toyplot-mark-Graph" id="t18e9f1ff6d604c9e93b3609ea591268c"><g class="toyplot-Edges"><path d="M 50.0 89.8577745512 L 50.0 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 56.6525871172 L 72.5463119284 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 89.8577745512 L 50.0 79.7518479409" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 79.7518479409 L 72.5463119284 79.7518479409" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 89.8577745512 L 50.0 133.168888596" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 133.168888596 L 61.2731559642 133.168888596" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 133.168888596 L 61.2731559642 102.851108765" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 102.851108765 L 83.8194678926 102.851108765" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 133.168888596 L 61.2731559642 163.486668427" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 163.486668427 L 83.8194678926 163.486668427" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 83.8194678926 163.486668427 L 83.8194678926 137.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 83.8194678926 137.5 L 128.912091749 137.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 83.8194678926 163.486668427 L 83.8194678926 189.473336853" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 83.8194678926 189.473336853 L 106.365779821 189.473336853" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 137.5 L 128.912091749 125.950369588" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 125.950369588 L 151.458403678 125.950369588" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 137.5 L 128.912091749 149.049630412" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 149.049630412 L 151.458403678 149.049630412" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 106.365779821 189.473336853 L 106.365779821 172.148891235" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 106.365779821 172.148891235 L 128.912091749 172.148891235" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 106.365779821 189.473336853 L 106.365779821 206.797782471" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 106.365779821 206.797782471 L 128.912091749 206.797782471" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 206.797782471 L 128.912091749 195.248152059" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 195.248152059 L 151.458403678 195.248152059" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 206.797782471 L 128.912091749 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 218.347412883 L 151.458403678 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><g class="toyplot-HeadMarkers"></g><g class="toyplot-MiddleMarkers"></g><g class="toyplot-TailMarkers"></g></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 89.857774551214362)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 56.652587117212263)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(72.546311928405899, 56.652587117212263)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 79.7518479408659)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(72.546311928405899, 79.7518479408659)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 133.16888859556497)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 133.16888859556497)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 133.16888859556497)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 102.85110876451954)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 102.85110876451954)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 163.48666842661035)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 163.48666842661035)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 163.48666842661035)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(106.36577982101474, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 125.95036958817319)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 125.95036958817319)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 149.04963041182683)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 149.04963041182683)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(106.36577982101474, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(106.36577982101474, 172.14889123548048)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 172.14889123548048)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(106.36577982101474, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 195.24815205913413)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 195.24815205913413)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 218.34741288278775)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 218.34741288278775)"><circle r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t71607744e80a4f3f8432598c824909b2"><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 218.34741288278775)"><title>idx: 0
name: t-4
dist: 1.0
support: 100
height: 0.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-4</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 195.24815205913413)"><title>idx: 1
name: t-3
dist: 1.0
support: 100
height: 0.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-3</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(128.91209174942065, 172.14889123548048)"><title>idx: 2
name: t-2
dist: 1.0
support: 100
height: 1.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-2</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 149.04963041182683)"><title>idx: 3
name: t-1
dist: 1.0
support: 100
height: 0.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-1</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 125.95036958817319)"><title>idx: 4
name: t-0
dist: 1.0
support: 100
height: 0.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-0</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(83.819467892608856, 102.85110876451954)"><title>idx: 5
name: t-5
dist: 1.0
support: 100
height: 3.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-5</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(72.546311928405899, 79.7518479408659)"><title>idx: 6
name: t-7
dist: 1.0
support: 100
height: 3.5</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-7</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(72.546311928405899, 56.652587117212263)"><title>idx: 7
name: t-6
dist: 1.0
support: 100
height: 3.5</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-6</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(128.91209174942065, 206.79778247096093)"><title>idx: 8
name: i9
dist: 1.0
support: 1
height: 1.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-3.501" y="2.2995">i9</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(106.36577982101474, 189.4733368532207)"><title>idx: 9
name: i11
dist: 1.0
support: 1
height: 2.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-6.003" y="2.2995">i11</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(128.91209174942065, 137.5)"><title>idx: 10
name: i13
dist: 2.0
support: 1
height: 1.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-6.003" y="2.2995">i13</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(83.819467892608856, 163.48666842661035)"><title>idx: 11
name: i12
dist: 1.0
support: 1
height: 3.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-6.003" y="2.2995">i12</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(61.273155964202957, 133.16888859556497)"><title>idx: 12
name: i10
dist: 0.5
support: 1
height: 4.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-6.003" y="2.2995">i10</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(50.0, 89.857774551214362)"><title>idx: 13
name: i14
dist: 0.0
support: 100
height: 4.5</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-6.003" y="2.2995">i14</text></g></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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
modules["toyplot/root/id"] = "tc72c6a145944490a9275e0b3f889631e";
modules["toyplot/root"] = (function(root_id)
    {
        return document.querySelector("#" + root_id);
    })(modules["toyplot/root/id"]);
modules["toyplot/canvas/id"] = "tc0fb515c05114b929d3b0c2e9d3d2e34";
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t18e9f1ff6d604c9e93b3609ea591268c","vertex_data","graph vertex data",["x", "y"],[[-4.5, -4.5, -3.5, -4.5, -3.5, -4.5, -4.0, -4.0, -4.0, -3.0, -4.0, -3.0, -3.0, -3.0, -1.0, -3.0, -2.0, -1.0, -1.0, 0.0, -1.0, 0.0, -2.0, -2.0, -1.0, -2.0, -1.0, -1.0, -1.0, 0.0, -1.0, 0.0], [5.5625, 7.0, 7.0, 6.0, 6.0, 3.6875, 3.6875, 3.6875, 5.0, 5.0, 2.375, 2.375, 2.375, 3.5, 3.5, 1.25, 1.25, 3.5, 4.0, 4.0, 3.0, 3.0, 1.25, 2.0, 2.0, 0.5, 0.5, 0.5, 1.0, 1.0, 0.0, 0.0]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t18e9f1ff6d604c9e93b3609ea591268c","edge_data","graph edge data",["source", "target"],[[0, 1, 0, 3, 0, 5, 7, 8, 7, 10, 12, 13, 12, 15, 17, 18, 17, 20, 22, 23, 22, 25, 27, 28, 27, 30], [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 13, 14, 15, 16, 18, 19, 20, 21, 23, 24, 25, 26, 28, 29, 30, 31]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t71607744e80a4f3f8432598c824909b2","data","scatterplot",["x", "y0"],[[0.0, 0.0, -1.0, 0.0, 0.0, -3.0, -3.5, -3.5, -1.0, -2.0, -1.0, -3.0, -4.0, -4.5], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 0.5, 1.25, 3.5, 2.375, 3.6875, 5.5625]],"toyplot");
})();</script></div></div>



<div class="toyplot" id="ta2e4171b8ad349eba34357e92f351b48" style="text-align:center"><svg class="toyplot-canvas-Canvas" height="275.0px" id="tfacbb0d6868e41e8a79299244e653441" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 225.0 275.0" width="225.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="tc86c6f338ab5445ab8d8c509aec7abc1"><clipPath id="tcaaa8c90151547028bbf71ff09053d01"><rect height="275.0" width="225.0" x="0.0" y="0.0"></rect></clipPath><g clip-path="url(#tcaaa8c90151547028bbf71ff09053d01)"><g class="toyplot-mark-Text" id="tefb592770b81470c9fcd17a4dfeb9667"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(151.45840367782654,218.34741288278775)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-4</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,195.24815205913413)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-3</text></g><g class="toyplot-Datum" transform="translate(128.91209174942065,172.14889123548048)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-2</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,149.04963041182683)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-1</text></g><g class="toyplot-Datum" transform="translate(151.45840367782654,125.95036958817319)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-0</text></g><g class="toyplot-Datum" transform="translate(83.819467892608856,102.85110876451954)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-5</text></g><g class="toyplot-Datum" transform="translate(83.819467892608856,79.7518479408659)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-6</text></g><g class="toyplot-Datum" transform="translate(83.819467892608856,56.652587117212263)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">t-7</text></g></g></g><g class="toyplot-mark-Graph" id="t298257e417894971bdd41046c7313481"><g class="toyplot-Edges"><path d="M 50.0 100.685553062 L 50.0 68.202217529" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 68.202217529 L 61.2731559642 68.202217529" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 100.685553062 L 50.0 133.168888596" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 133.168888596 L 61.2731559642 133.168888596" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 68.202217529 L 61.2731559642 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 56.6525871172 L 83.8194678926 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 68.202217529 L 61.2731559642 79.7518479409" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 79.7518479409 L 83.8194678926 79.7518479409" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 133.168888596 L 61.2731559642 102.851108765" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 102.851108765 L 83.8194678926 102.851108765" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 133.168888596 L 61.2731559642 163.486668427" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 61.2731559642 163.486668427 L 83.8194678926 163.486668427" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 83.8194678926 163.486668427 L 83.8194678926 137.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 83.8194678926 137.5 L 128.912091749 137.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 83.8194678926 163.486668427 L 83.8194678926 189.473336853" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 83.8194678926 189.473336853 L 106.365779821 189.473336853" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 137.5 L 128.912091749 125.950369588" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 125.950369588 L 151.458403678 125.950369588" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 137.5 L 128.912091749 149.049630412" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 149.049630412 L 151.458403678 149.049630412" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 106.365779821 189.473336853 L 106.365779821 172.148891235" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 106.365779821 172.148891235 L 128.912091749 172.148891235" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 106.365779821 189.473336853 L 106.365779821 206.797782471" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 106.365779821 206.797782471 L 128.912091749 206.797782471" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 206.797782471 L 128.912091749 195.248152059" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 195.248152059 L 151.458403678 195.248152059" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 206.797782471 L 128.912091749 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 128.912091749 218.347412883 L 151.458403678 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><g class="toyplot-HeadMarkers"></g><g class="toyplot-MiddleMarkers"></g><g class="toyplot-TailMarkers"></g></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 100.68555306230201)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 133.16888859556497)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 133.16888859556497)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 68.202217529039075)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 56.652587117212263)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 56.652587117212263)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 79.7518479408659)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 79.7518479408659)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 133.16888859556497)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 102.85110876451954)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 102.85110876451954)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(61.273155964202957, 163.48666842661035)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 163.48666842661035)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 163.48666842661035)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(83.819467892608856, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(106.36577982101474, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 137.5)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 125.95036958817319)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 125.95036958817319)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 149.04963041182683)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 149.04963041182683)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(106.36577982101474, 189.4733368532207)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(106.36577982101474, 172.14889123548048)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 172.14889123548048)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(106.36577982101474, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 206.79778247096093)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 195.24815205913413)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 195.24815205913413)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(128.91209174942065, 218.34741288278775)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(151.45840367782654, 218.34741288278775)"><circle r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t03da6cdd4ed5446caee09fc7cabf6223"><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 218.34741288278775)"><title>idx: 0
name: t-4
dist: 1.0
support: 100
height: 0.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-4</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 195.24815205913413)"><title>idx: 1
name: t-3
dist: 1.0
support: 100
height: 0.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-3</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(128.91209174942065, 172.14889123548048)"><title>idx: 2
name: t-2
dist: 1.0
support: 100
height: 1.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-2</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 149.04963041182683)"><title>idx: 3
name: t-1
dist: 1.0
support: 100
height: 0.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-1</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(151.45840367782654, 125.95036958817319)"><title>idx: 4
name: t-0
dist: 1.0
support: 100
height: 0.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-0</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(83.819467892608856, 102.85110876451954)"><title>idx: 5
name: t-5
dist: 1.0
support: 100
height: 3.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-5</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(83.819467892608856, 79.7518479408659)"><title>idx: 6
name: t-6
dist: 1.0
support: 100
height: 3.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-6</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(83.819467892608856, 56.652587117212263)"><title>idx: 7
name: t-7
dist: 1.0
support: 100
height: 3.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-5.2515" y="2.2995">t-7</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(128.91209174942065, 206.79778247096093)"><title>idx: 8
name: i9
dist: 1.0
support: 1
height: 1.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-3.501" y="2.2995">i9</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(106.36577982101474, 189.4733368532207)"><title>idx: 9
name: i11
dist: 1.0
support: 1
height: 2.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-6.003" y="2.2995">i11</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(128.91209174942065, 137.5)"><title>idx: 10
name: i13
dist: 2.0
support: 1
height: 1.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-6.003" y="2.2995">i13</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(83.819467892608856, 163.48666842661035)"><title>idx: 11
name: i12
dist: 1.0
support: 1
height: 3.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-6.003" y="2.2995">i12</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(61.273155964202957, 133.16888859556497)"><title>idx: 12
name: i10
dist: 0.5
support: 1
height: 4.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-6.003" y="2.2995">i10</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(61.273155964202957, 68.202217529039075)"><title>idx: 13
name: rerooted
dist: 0.5
support: 100
height: 4.0</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-16.758" y="2.2995">rerooted</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(50.0, 100.68555306230201)"><title>idx: 14
name: i14
dist: 0.0
support: 100
height: 4.5</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-6.003" y="2.2995">i14</text></g></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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
modules["toyplot/root/id"] = "ta2e4171b8ad349eba34357e92f351b48";
modules["toyplot/root"] = (function(root_id)
    {
        return document.querySelector("#" + root_id);
    })(modules["toyplot/root/id"]);
modules["toyplot/canvas/id"] = "tfacbb0d6868e41e8a79299244e653441";
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t298257e417894971bdd41046c7313481","vertex_data","graph vertex data",["x", "y"],[[-4.5, -4.5, -4.0, -4.5, -4.0, -4.0, -4.0, -3.0, -4.0, -3.0, -4.0, -4.0, -3.0, -4.0, -3.0, -3.0, -3.0, -1.0, -3.0, -2.0, -1.0, -1.0, 0.0, -1.0, 0.0, -2.0, -2.0, -1.0, -2.0, -1.0, -1.0, -1.0, 0.0, -1.0, 0.0], [5.09375, 6.5, 6.5, 3.6875, 3.6875, 6.5, 7.0, 7.0, 6.0, 6.0, 3.6875, 5.0, 5.0, 2.375, 2.375, 2.375, 3.5, 3.5, 1.25, 1.25, 3.5, 4.0, 4.0, 3.0, 3.0, 1.25, 2.0, 2.0, 0.5, 0.5, 0.5, 1.0, 1.0, 0.0, 0.0]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t298257e417894971bdd41046c7313481","edge_data","graph edge data",["source", "target"],[[0, 1, 0, 3, 5, 6, 5, 8, 10, 11, 10, 13, 15, 16, 15, 18, 20, 21, 20, 23, 25, 26, 25, 28, 30, 31, 30, 33], [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24, 26, 27, 28, 29, 31, 32, 33, 34]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t03da6cdd4ed5446caee09fc7cabf6223","data","scatterplot",["x", "y0"],[[0.0, 0.0, -1.0, 0.0, 0.0, -3.0, -3.0, -3.0, -1.0, -2.0, -1.0, -3.0, -4.0, -4.0, -4.5], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 0.5, 1.25, 3.5, 2.375, 3.6875, 6.5, 5.09375]],"toyplot");
})();</script></div></div>


### toytree.get_node_values
This is explained in great detail in the [node-labels](node-labels.md) section. This can be used to return a list of node values that are extracted directly from the tree object and will always be in the correct order for plotting. 


```python
tre.get_node_values(feature='dist', show_root=True, show_tips=True)
```




    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]



### toytree.get_edge_lengths
This is simply another way of requesting `tre.get_node_values('dist')`. You can use this to modify edges of the tree. 


```python
tre.get_edge_lengths()
```




    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]



### toytree.colors


```python
## an easily accessible list of 
tre.colors
```




    ['rgba(40.0%,76.1%,64.7%,1.000)',
     'rgba(98.8%,55.3%,38.4%,1.000)',
     'rgba(55.3%,62.7%,79.6%,1.000)',
     'rgba(90.6%,54.1%,76.5%,1.000)',
     'rgba(65.1%,84.7%,32.9%,1.000)',
     'rgba(100.0%,85.1%,18.4%,1.000)',
     'rgba(89.8%,76.9%,58.0%,1.000)',
     'rgba(70.2%,70.2%,70.2%,1.000)']


