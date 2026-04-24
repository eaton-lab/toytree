<div class="nb-md-page-hook" aria-hidden="true"></div>

# Node query/selection
Many methods in `toytree` require selecting one or more nodes from a tree to operate on. This can often be challenging since most nodes in a tree usually do not have unique names assigned to them, and selecting nodes by a numeric indexing method can be error-prone if the indices change. We have tried to design the node query and selection methods in `toytree` to be maximally flexible to allow for ease-of-use when selecting nodes while also trying to prevent users from making simple and common mistakes.


```python
import toytree
```


```python
# load a toytree from a newick string at a URL and root it
tree = toytree.tree("https://eaton-lab.org/data/Cyathophora.tre").root("~prz")
```

## Select Nodes by index (idx)
The simplest and fastest approach to get `Node` objects from a ToyTree is to select them by their `idx` label. In fact, the storage of Nodes in a cached traversal order for fast recall is one of the main advantages of the ToyTree class. The tip nodes are intuitively labeled from left to right (or bottom to top, depending on the tree orientation) as idx labels from 0 to ntips - 1, and the root node is at idx label nnodes - 1.


```python
# draw tree showing the idx labels representing the cached idxorder traversal
tree.draw('s');
```


<div class="toyplot" id="t0a751dc771fc41c98783ba13e6908cbb" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="353.23600000000005px" height="384.04999999999995px" viewBox="0 0 353.23600000000005 384.04999999999995" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t1e005854648e4f9ca0c7b154d20c9148"><g class="toyplot-coordinates-Cartesian" id="t8dacbc7f5a894ba2a5952ea9eb43e97d"><clipPath id="t559b2d2488e0459b91f35157be3d87ee"><rect x="35.0" y="35.0" width="283.23600000000005" height="314.04999999999995"></rect></clipPath><g clip-path="url(#t559b2d2488e0459b91f35157be3d87ee)"></g></g><g class="toyplot-coordinates-Cartesian" id="tffe35c46b2b84d5a8f8b25b7feaf7b7e"><clipPath id="t57c5ddac682a4354a6a9d7ce9fbbe4c4"><rect x="35.0" y="35.0" width="283.23600000000005" height="314.04999999999995"></rect></clipPath><g clip-path="url(#t57c5ddac682a4354a6a9d7ce9fbbe4c4)"><g class="toytree-mark-Toytree" id="t0670550c744b46c1911397e054012868"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 147.6 313.5 L 147.6 324.6 L 162.4 324.6" id="13,0" style=""></path><path d="M 147.6 313.5 L 147.6 302.5 L 162.4 302.5" id="13,1" style=""></path><path d="M 88.8 254.8 L 88.8 280.4 L 162.4 280.4" id="19,2" style=""></path><path d="M 103.5 229.3 L 103.5 258.3 L 162.4 258.3" id="18,3" style=""></path><path d="M 147.6 225.2 L 147.6 236.2 L 162.4 236.2" id="14,4" style=""></path><path d="M 147.6 225.2 L 147.6 214.1 L 162.4 214.1" id="14,5" style=""></path><path d="M 132.9 175.5 L 132.9 192.0 L 162.4 192.0" id="16,6" style=""></path><path d="M 147.6 158.9 L 147.6 169.9 L 162.4 169.9" id="15,7" style=""></path><path d="M 147.6 158.9 L 147.6 147.8 L 162.4 147.8" id="15,8" style=""></path><path d="M 147.6 114.7 L 147.6 125.8 L 162.4 125.8" id="20,9" style=""></path><path d="M 147.6 114.7 L 147.6 103.7 L 162.4 103.7" id="20,10" style=""></path><path d="M 147.6 70.5 L 147.6 81.6 L 162.4 81.6" id="21,11" style=""></path><path d="M 147.6 70.5 L 147.6 59.5 L 162.4 59.5" id="21,12" style=""></path><path d="M 59.3 243.6 L 59.3 313.5 L 147.6 313.5" id="24,13" style=""></path><path d="M 118.2 200.3 L 118.2 225.2 L 147.6 225.2" id="17,14" style=""></path><path d="M 132.9 175.5 L 132.9 158.9 L 147.6 158.9" id="16,15" style=""></path><path d="M 118.2 200.3 L 118.2 175.5 L 132.9 175.5" id="17,16" style=""></path><path d="M 103.5 229.3 L 103.5 200.3 L 118.2 200.3" id="18,17" style=""></path><path d="M 88.8 254.8 L 88.8 229.3 L 103.5 229.3" id="19,18" style=""></path><path d="M 74.0 173.7 L 74.0 254.8 L 88.8 254.8" id="23,19" style=""></path><path d="M 132.9 92.6 L 132.9 114.7 L 147.6 114.7" id="22,20" style=""></path><path d="M 132.9 92.6 L 132.9 70.5 L 147.6 70.5" id="22,21" style=""></path><path d="M 74.0 173.7 L 74.0 92.6 L 132.9 92.6" id="23,22" style=""></path><path d="M 59.3 243.6 L 59.3 173.7 L 74.0 173.7" id="24,23" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(162.372,324.55)"><circle r="8.0"></circle></g><g id="Node-1" transform="translate(162.372,302.463)"><circle r="8.0"></circle></g><g id="Node-2" transform="translate(162.372,280.375)"><circle r="8.0"></circle></g><g id="Node-3" transform="translate(162.372,258.288)"><circle r="8.0"></circle></g><g id="Node-4" transform="translate(162.372,236.2)"><circle r="8.0"></circle></g><g id="Node-5" transform="translate(162.372,214.113)"><circle r="8.0"></circle></g><g id="Node-6" transform="translate(162.372,192.025)"><circle r="8.0"></circle></g><g id="Node-7" transform="translate(162.372,169.937)"><circle r="8.0"></circle></g><g id="Node-8" transform="translate(162.372,147.85)"><circle r="8.0"></circle></g><g id="Node-9" transform="translate(162.372,125.762)"><circle r="8.0"></circle></g><g id="Node-10" transform="translate(162.372,103.675)"><circle r="8.0"></circle></g><g id="Node-11" transform="translate(162.372,81.5875)"><circle r="8.0"></circle></g><g id="Node-12" transform="translate(162.372,59.5)"><circle r="8.0"></circle></g><g id="Node-13" transform="translate(147.649,313.506)"><circle r="8.0"></circle></g><g id="Node-14" transform="translate(147.649,225.156)"><circle r="8.0"></circle></g><g id="Node-15" transform="translate(147.649,158.894)"><circle r="8.0"></circle></g><g id="Node-16" transform="translate(132.926,175.459)"><circle r="8.0"></circle></g><g id="Node-17" transform="translate(118.203,200.308)"><circle r="8.0"></circle></g><g id="Node-18" transform="translate(103.479,229.298)"><circle r="8.0"></circle></g><g id="Node-19" transform="translate(88.7564,254.836)"><circle r="8.0"></circle></g><g id="Node-20" transform="translate(147.649,114.719)"><circle r="8.0"></circle></g><g id="Node-21" transform="translate(147.649,70.5437)"><circle r="8.0"></circle></g><g id="Node-22" transform="translate(132.926,92.6312)"><circle r="8.0"></circle></g><g id="Node-23" transform="translate(74.0333,173.734)"><circle r="8.0"></circle></g><g id="Node-24" transform="translate(59.3102,243.62)"><circle r="8.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(162.372,324.55)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(162.372,302.463)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(162.372,280.375)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(162.372,258.288)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(162.372,236.2)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(162.372,214.113)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(162.372,192.025)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(162.372,169.937)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(162.372,147.85)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(162.372,125.762)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(162.372,103.675)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(162.372,81.5875)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(162.372,59.5)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(147.649,313.506)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(147.649,225.156)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g><g class="toytree-NodeLabel" transform="translate(147.649,158.894)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">15</text></g><g class="toytree-NodeLabel" transform="translate(132.926,175.459)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">16</text></g><g class="toytree-NodeLabel" transform="translate(118.203,200.308)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">17</text></g><g class="toytree-NodeLabel" transform="translate(103.479,229.298)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">18</text></g><g class="toytree-NodeLabel" transform="translate(88.7564,254.836)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">19</text></g><g class="toytree-NodeLabel" transform="translate(147.649,114.719)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">20</text></g><g class="toytree-NodeLabel" transform="translate(147.649,70.5437)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">21</text></g><g class="toytree-NodeLabel" transform="translate(132.926,92.6312)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">22</text></g><g class="toytree-NodeLabel" transform="translate(74.0333,173.734)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">23</text></g><g class="toytree-NodeLabel" transform="translate(59.3102,243.62)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">24</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(162.372,324.55)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">32082_przewalskii</text></g><g class="toytree-TipLabel" transform="translate(162.372,302.463)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">33588_przewalskii</text></g><g class="toytree-TipLabel" transform="translate(162.372,280.375)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">33413_thamno</text></g><g class="toytree-TipLabel" transform="translate(162.372,258.288)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">30556_thamno</text></g><g class="toytree-TipLabel" transform="translate(162.372,236.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">40578_rex</text></g><g class="toytree-TipLabel" transform="translate(162.372,214.113)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">35855_rex</text></g><g class="toytree-TipLabel" transform="translate(162.372,192.025)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">35236_rex</text></g><g class="toytree-TipLabel" transform="translate(162.372,169.937)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">39618_rex</text></g><g class="toytree-TipLabel" transform="translate(162.372,147.85)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">38362_rex</text></g><g class="toytree-TipLabel" transform="translate(162.372,125.762)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">29154_superba</text></g><g class="toytree-TipLabel" transform="translate(162.372,103.675)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">30686_cyathophylla</text></g><g class="toytree-TipLabel" transform="translate(162.372,81.5875)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">41954_cyathophylloides</text></g><g class="toytree-TipLabel" transform="translate(162.372,59.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">41478_cyathophylloides</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


Nodes can selected from a `ToyTree` by indexing, slicing by idx label.


```python
# select a single node by idx
tree[1]
```




    <Node(idx=1, name='33588_przewalskii')>




```python
# select a slice of nodes by idx
tree[3:5]
```




    [<Node(idx=3, name='30556_thamno')>, <Node(idx=4, name='40578_rex')>]




```python
# select a list of nodes by idx
tree[[3, 4, 8, 9]]
```




    [<Node(idx=3, name='30556_thamno')>,
     <Node(idx=4, name='40578_rex')>,
     <Node(idx=8, name='38362_rex')>,
     <Node(idx=9, name='29154_superba')>]




```python
# select all tip (leaf) nodes by slicing
tree[:tree.ntips]
```




    [<Node(idx=0, name='32082_przewalskii')>,
     <Node(idx=1, name='33588_przewalskii')>,
     <Node(idx=2, name='33413_thamno')>,
     <Node(idx=3, name='30556_thamno')>,
     <Node(idx=4, name='40578_rex')>,
     <Node(idx=5, name='35855_rex')>,
     <Node(idx=6, name='35236_rex')>,
     <Node(idx=7, name='39618_rex')>,
     <Node(idx=8, name='38362_rex')>,
     <Node(idx=9, name='29154_superba')>,
     <Node(idx=10, name='30686_cyathophylla')>,
     <Node(idx=11, name='41954_cyathophylloides')>,
     <Node(idx=12, name='41478_cyathophylloides')>]




```python
# select all internal nodes by slicing
tree[tree.ntips:tree.nnodes]
```




    [<Node(idx=13)>,
     <Node(idx=14)>,
     <Node(idx=15)>,
     <Node(idx=16)>,
     <Node(idx=17)>,
     <Node(idx=18)>,
     <Node(idx=19)>,
     <Node(idx=20)>,
     <Node(idx=21)>,
     <Node(idx=22)>,
     <Node(idx=23)>,
     <Node(idx=24, name='root')>]




```python
# select the root node
tree[-1]
```




    <Node(idx=24, name='root')>



## Select Nodes by name
To select nodes by name you can use the `get_nodes` function. This is most useful for selecting tip nodes, since these are often the only nodes that have unique names, whereas internal nodes usually have empty name attributes. Internal nodes can be queried by using their idx labels, or, as demonstrated below, they can be selected based on tip names by using the function `get_mrca_node`.


```python
# select one node by name
tree.get_nodes("40578_rex")
```




    [<Node(idx=4, name='40578_rex')>]




```python
# select multiple nodes by name
tree.get_nodes("40578_rex", "38362_rex")
```




    [<Node(idx=4, name='40578_rex')>, <Node(idx=8, name='38362_rex')>]



## Using regular expressions ~
Regular expressions are a sequence of characters that match a pattern, and are often used in search algorithms. In `toytree` there are many functions which optionally accept regular expressions as an input to allow for easily selecting multiple nodes. This can be used because the operation is intended to operate on each of these nodes individually (e.g., `toytree.mod.drop_tips`) or because the operation will find the most recent common ancestor of the input nodes and operate on that edge or subtree (e.g., `toytree.mod.root`, or `toytree.mod.extract_subtree`; see below).

All of these functions that accept name strings as input use the `get_nodes` function under the hood to find the matched nodes, and so our demonstrations below will use this function. In addition to accepting one or more individual name strings this function can also accept regular expressions as input. 

**To indicate that an entry should be treated as a regular expression use the `~` prefix.** It will then use the Python standard library regular expression function `re.search()` to find any nodes that match this query.


```python
# match any node name containing 'prz'
tree.get_nodes("~prz")
```




    [<Node(idx=1, name='33588_przewalskii')>,
     <Node(idx=0, name='32082_przewalskii')>]




```python
# match any node name containing 855
tree.get_nodes("~855")
```




    [<Node(idx=5, name='35855_rex')>]




```python
# match any node name starting with a 4
tree.get_nodes("~^4")
```




    [<Node(idx=4, name='40578_rex')>,
     <Node(idx=11, name='41954_cyathophylloides')>,
     <Node(idx=12, name='41478_cyathophylloides')>]




```python
# match any node name ending with an 'a'
tree.get_nodes("~a$")
```




    [<Node(idx=10, name='30686_cyathophylla')>,
     <Node(idx=9, name='29154_superba')>]




```python
# match name containing a 3 followed by 8 or 9 then any chars followed by 'rex'
tree.get_nodes("~3[8,9].+rex")
```




    [<Node(idx=8, name='38362_rex')>, <Node(idx=7, name='39618_rex')>]



## Node queries
We define a **query** as a flexible type of input used to match one or more nodes. For functions which accept a *query* as input, an `int` will be treated as a Node idx label, whereas a `str` will be treated as a Node `name`, and a `str` starting with a `~` will be treated as a regular expression. These functions can also accept a `Node` object as an input. You can even mix these arguments to select multiple nodes.

### `get_nodes()`
The function `get_nodes` is used widely both by users as well as internally by other functions. It takes `*query` as input meaning that it accepts any number of queries as input.


```python
# select nodes by int idx labels, or by str names, or multiple by ~regex, or Node
tree.get_nodes(0, 1, '40578_rex', tree[8])
```




    [<Node(idx=1, name='33588_przewalskii')>,
     <Node(idx=4, name='40578_rex')>,
     <Node(idx=8, name='38362_rex')>,
     <Node(idx=0, name='32082_przewalskii')>]



### `get_mrca_node()`
Many tree operations require selecting an internal node to operate on. For example, rooting a tree on a clade. This is easiest done by selecting two tip nodes by name for which the internal node target is the **most recent common ancestor (mrca)**, and providing these as entries to the `get_mrca_node` function. This function accepts query arguments the same way as `get_nodes`, accepting int, str, or `~`regex entries.

Consider the example below where wish to find the internal node that is the mrca of the five tip nodes in the example tree forming the "rex" clade. We can select this node in several ways:


```python
# if you already know its idx (e.g., by tree visualization) you can index it
tree[17]
```




    <Node(idx=17)>




```python
# or, you can find the mrca by knowing the tip node idxs
tree.get_mrca_node(4, 5, 6, 7, 8)
```




    <Node(idx=17)>




```python
# you actually only need to provide the minimal spanning nodes
tree.get_mrca_node(4, 8)
```




    <Node(idx=17)>




```python
# safer, however, is to enter node names, since these never change
tree.get_mrca_node("35855_rex", "40578_rex", "39618_rex", "35236_rex", "38362_rex")
```




    <Node(idx=17)>




```python
# again, you only need to enter the minimal required
tree.get_mrca_node("35855_rex", "38362_rex")
```




    <Node(idx=17)>




```python
# simpler, use a regular expression to match all names with 'rex'
tree.get_mrca_node("~rex")
```




    <Node(idx=17)>



## Efficiency/speed
Because matching nodes by name requires traversing over all nodes in the tree to find matches it is much slower than selecting nodes by indexing with idx labels. All of the methods are still pretty fast, the time difference only matters when writing very time-intensive code. This is demonstrated simply below.


```python
%%timeit
# time to select a tip node by its idx (superfast)
tree[7]
```

    115 ns ± 2.82 ns per loop (mean ± std. dev. of 7 runs, 10,000,000 loops each)



```python
%%timeit
# time to select a tip node by its name
tree.get_nodes("39618_rex")
```

    9.81 μs ± 289 ns per loop (mean ± std. dev. of 7 runs, 100,000 loops each)



```python
%%timeit
# time to select an internal node (17) by its known index
tree[17]
```

    116 ns ± 3.13 ns per loop (mean ± std. dev. of 7 runs, 10,000,000 loops each)



```python
%%timeit
# time to find mrca (17) by mrca of idx labels
tree.get_mrca_node(4, 8)
```

    25.1 μs ± 754 ns per loop (mean ± std. dev. of 7 runs, 10,000 loops each)



```python
%%timeit
# time to find mrca (17) by mrca of name labels
tree.get_mrca_node("~rex")
```

    63 μs ± 5.29 μs per loop (mean ± std. dev. of 7 runs, 10,000 loops each)


## Best practices

There are many situations in which you know the tree structure will not change, and thus indexing by node idx is faster and much preferred to slower name selection. Especially when you are selecting the tip or root nodes, which have obvious numeric labels. However, in other cases it is preferable to use names when selecting nodes, such as when adding traits or labels to internal nodes for tree drawings, since it makes your code more readable and explicit.

## Node Queries are everywhere
You will find that many functions in `toytree` accept *query* type inputs that are used to match nodes following the node query methods described above. These are especially common in the `toytree.mod` subpackage.


```python
tree.mod.root("~prz").draw();
```


<div class="toyplot" id="td4a6cb9a9451418986dec939cdead03f" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="344.73600000000005px" height="315.28px" viewBox="0 0 344.73600000000005 315.28" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t48e97efe35d242adb62af1e1b69abf4c"><g class="toyplot-coordinates-Cartesian" id="t32402e6381d74c34a28a7076a36f671f"><clipPath id="t8a282a19d6974806986455dc9c2b2b0d"><rect x="35.0" y="35.0" width="274.73600000000005" height="245.27999999999997"></rect></clipPath><g clip-path="url(#t8a282a19d6974806986455dc9c2b2b0d)"></g></g><g class="toyplot-coordinates-Cartesian" id="ta0ab2c53d03446238e0bb986f65364dc"><clipPath id="t5acaee92def6441abb411ca5a3dec624"><rect x="35.0" y="35.0" width="274.73600000000005" height="245.27999999999997"></rect></clipPath><g clip-path="url(#t5acaee92def6441abb411ca5a3dec624)"><g class="toytree-mark-Toytree" id="tc2e6830296b047d58cc6da283683ae19"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 111.4 249.7 L 111.4 258.1 L 120.1 258.1" id="13,0" style=""></path><path d="M 111.4 249.7 L 111.4 241.3 L 119.7 241.3" id="13,1" style=""></path><path d="M 129.5 205.2 L 129.5 224.6 L 148.6 224.6" id="19,2" style=""></path><path d="M 133.0 185.9 L 133.0 207.9 L 155.0 207.9" id="18,3" style=""></path><path d="M 143.2 182.8 L 143.2 191.1 L 154.5 191.1" id="14,4" style=""></path><path d="M 143.2 182.8 L 143.2 174.4 L 154.6 174.4" id="14,5" style=""></path><path d="M 138.1 145.1 L 138.1 157.6 L 157.7 157.6" id="16,6" style=""></path><path d="M 158.9 132.5 L 158.9 140.9 L 162.2 140.9" id="15,7" style=""></path><path d="M 158.9 132.5 L 158.9 124.2 L 162.6 124.2" id="15,8" style=""></path><path d="M 129.4 99.0 L 129.4 107.4 L 150.8 107.4" id="20,9" style=""></path><path d="M 129.4 99.0 L 129.4 90.7 L 152.0 90.7" id="20,10" style=""></path><path d="M 153.1 65.6 L 153.1 73.9 L 153.4 73.9" id="21,11" style=""></path><path d="M 153.1 65.6 L 153.1 57.2 L 153.3 57.2" id="21,12" style=""></path><path d="M 51.0 196.7 L 51.0 249.7 L 111.4 249.7" id="24,13" style=""></path><path d="M 135.7 163.9 L 135.7 182.8 L 143.2 182.8" id="17,14" style=""></path><path d="M 138.1 145.1 L 138.1 132.5 L 158.9 132.5" id="16,15" style=""></path><path d="M 135.7 163.9 L 135.7 145.1 L 138.1 145.1" id="17,16" style=""></path><path d="M 133.0 185.9 L 133.0 163.9 L 135.7 163.9" id="18,17" style=""></path><path d="M 129.5 205.2 L 129.5 185.9 L 133.0 185.9" id="19,18" style=""></path><path d="M 111.4 143.8 L 111.4 205.2 L 129.5 205.2" id="23,19" style=""></path><path d="M 121.4 82.3 L 121.4 99.0 L 129.4 99.0" id="22,20" style=""></path><path d="M 121.4 82.3 L 121.4 65.6 L 153.1 65.6" id="22,21" style=""></path><path d="M 111.4 143.8 L 111.4 82.3 L 121.4 82.3" id="23,22" style=""></path><path d="M 51.0 196.7 L 51.0 143.8 L 111.4 143.8" id="24,23" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(120.13,258.08)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">32082_przewalskii</text></g><g class="toytree-TipLabel" transform="translate(119.72,241.34)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">33588_przewalskii</text></g><g class="toytree-TipLabel" transform="translate(148.582,224.6)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">33413_thamno</text></g><g class="toytree-TipLabel" transform="translate(155.023,207.86)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">30556_thamno</text></g><g class="toytree-TipLabel" transform="translate(154.468,191.12)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">40578_rex</text></g><g class="toytree-TipLabel" transform="translate(154.622,174.38)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">35855_rex</text></g><g class="toytree-TipLabel" transform="translate(157.702,157.64)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">35236_rex</text></g><g class="toytree-TipLabel" transform="translate(162.189,140.9)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">39618_rex</text></g><g class="toytree-TipLabel" transform="translate(162.627,124.16)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">38362_rex</text></g><g class="toytree-TipLabel" transform="translate(150.798,107.42)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">29154_superba</text></g><g class="toytree-TipLabel" transform="translate(152,90.68)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">30686_cyathophylla</text></g><g class="toytree-TipLabel" transform="translate(153.414,73.94)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">41954_cyathophylloides</text></g><g class="toytree-TipLabel" transform="translate(153.292,57.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">41478_cyathophylloides</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# drop all 'rex' samples
tree.mod.drop_tips("~rex*").draw();
```


<div class="toyplot" id="tb661a04b97284e0093fb5341a453b39f" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="344.73600000000005px" height="275.0px" viewBox="0 0 344.73600000000005 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t45e716898869470c9d6ee74e6a8bd7a2"><g class="toyplot-coordinates-Cartesian" id="ta35bd231773349aba9d9ab9c219ff2b7"><clipPath id="t704488fa6bff4eecb793172286ddb9c5"><rect x="35.0" y="35.0" width="274.73600000000005" height="205.0"></rect></clipPath><g clip-path="url(#t704488fa6bff4eecb793172286ddb9c5)"></g></g><g class="toyplot-coordinates-Cartesian" id="tcd967867f8b24c6abaf649ce3c946a1c"><clipPath id="tb0fa1782dc7b4c4f8424c4552f25ebed"><rect x="35.0" y="35.0" width="274.73600000000005" height="205.0"></rect></clipPath><g clip-path="url(#tb0fa1782dc7b4c4f8424c4552f25ebed)"><g class="toytree-mark-Toytree" id="t76d7b202de484de69cd3f664add61513"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 111.5 206.3 L 111.5 217.8 L 120.2 217.8" id="8,0" style=""></path><path d="M 111.5 206.3 L 111.5 194.9 L 119.8 194.9" id="8,1" style=""></path><path d="M 129.6 160.4 L 129.6 171.9 L 148.7 171.9" id="9,2" style=""></path><path d="M 129.6 160.4 L 129.6 149.0 L 155.2 149.0" id="9,3" style=""></path><path d="M 129.5 114.6 L 129.5 126.0 L 150.9 126.0" id="10,4" style=""></path><path d="M 129.5 114.6 L 129.5 103.1 L 152.1 103.1" id="10,5" style=""></path><path d="M 153.2 68.7 L 153.2 80.1 L 153.5 80.1" id="11,6" style=""></path><path d="M 153.2 68.7 L 153.2 57.2 L 153.4 57.2" id="11,7" style=""></path><path d="M 51.0 166.2 L 51.0 206.3 L 111.5 206.3" id="14,8" style=""></path><path d="M 111.5 126.0 L 111.5 160.4 L 129.6 160.4" id="13,9" style=""></path><path d="M 121.5 91.6 L 121.5 114.6 L 129.5 114.6" id="12,10" style=""></path><path d="M 121.5 91.6 L 121.5 68.7 L 153.2 68.7" id="12,11" style=""></path><path d="M 111.5 126.0 L 111.5 91.6 L 121.5 91.6" id="13,12" style=""></path><path d="M 51.0 166.2 L 51.0 126.0 L 111.5 126.0" id="14,13" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(120.222,217.8)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">32082_przewalskii</text></g><g class="toytree-TipLabel" transform="translate(119.81,194.857)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">33588_przewalskii</text></g><g class="toytree-TipLabel" transform="translate(148.711,171.914)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">33413_thamno</text></g><g class="toytree-TipLabel" transform="translate(155.161,148.971)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">30556_thamno</text></g><g class="toytree-TipLabel" transform="translate(150.93,126.029)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">29154_superba</text></g><g class="toytree-TipLabel" transform="translate(152.134,103.086)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">30686_cyathophylla</text></g><g class="toytree-TipLabel" transform="translate(153.549,80.1429)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">41954_cyathophylloides</text></g><g class="toytree-TipLabel" transform="translate(153.428,57.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">41478_cyathophylloides</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# keep only the subtree connecting 'rex' samples
tree.mod.prune("~rex*").draw();
```


<div class="toyplot" id="t5d1318dd608d49a79020e5a30fb9c676" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t5682936820494d81870b2cd26b25e93e"><g class="toyplot-coordinates-Cartesian" id="t421986fbdc1a49abad767a77398bb45d"><clipPath id="t19a2db72936847849cb47e03f61b0dd5"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t19a2db72936847849cb47e03f61b0dd5)"></g></g><g class="toyplot-coordinates-Cartesian" id="t535e9e55d0d14a0c88c0c7290522faaf"><clipPath id="t6a591779250145a2b8cf9b9c805e5a95"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t6a591779250145a2b8cf9b9c805e5a95)"><g class="toytree-mark-Toytree" id="te785a40571ce439685e6f5e279903299"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 86.5 197.7 L 86.5 217.8 L 140.0 217.8" id="5,0" style=""></path><path d="M 86.5 197.7 L 86.5 177.7 L 140.7 177.7" id="5,1" style=""></path><path d="M 62.8 107.4 L 62.8 137.5 L 155.3 137.5" id="7,2" style=""></path><path d="M 161.2 77.3 L 161.2 97.3 L 176.5 97.3" id="6,3" style=""></path><path d="M 161.2 77.3 L 161.2 57.2 L 178.6 57.2" id="6,4" style=""></path><path d="M 51.0 152.6 L 51.0 197.7 L 86.5 197.7" id="8,5" style=""></path><path d="M 62.8 107.4 L 62.8 77.3 L 161.2 77.3" id="7,6" style=""></path><path d="M 51.0 152.6 L 51.0 107.4 L 62.8 107.4" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(139.987,217.8)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">40578_rex</text></g><g class="toytree-TipLabel" transform="translate(140.713,177.65)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">35855_rex</text></g><g class="toytree-TipLabel" transform="translate(155.288,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">35236_rex</text></g><g class="toytree-TipLabel" transform="translate(176.517,97.35)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">39618_rex</text></g><g class="toytree-TipLabel" transform="translate(178.59,57.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">38362_rex</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>

