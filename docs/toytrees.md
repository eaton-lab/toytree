
## Toytree objects
The basic object in toytree is the `Toytree` object. This object has a number of useful attributes and functions to interact with the underlying `tree` object which hold the tree structure in memory. In this section we will describe how the tree is stored and how to modify and interact with it. 


```python
import toytree
import toyplot
import numpy as np
```


```python
#### Generate a random toytree
tre = toytree.rtree(ntips=10)
```

All of the information that is used to draw a tree is extracted from the toytree object, and so the more you know about how to access that data the more you will know about how to modify it. In the example below we extract the node colors from a list of colors available from the tree, and get the node labels from the tree features, and we get the tip labels from the tree object. 


```python
## draw the tree
tre.draw(
    node_color=tre.colors[3],
    node_labels=tre.get_node_values("support"),
    tip_labels=tre.get_tip_labels(),
    );
```


<div align="center" class="toyplot" id="ta076e70ab9a04b5e90b6c9ef26d0c9a8"><svg class="toyplot-canvas-Canvas" height="250.0px" id="t1cf5aefc97bb48a7baa14780e399f598" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 250.0 250.0" width="250.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t2b5adc64f95d4fa6b458bfa3ba2870e8"><clipPath id="tf5ddd81e71a1450facbcc6eded29354e"><rect height="220.0" width="220.0" x="15.0" y="15.0"></rect></clipPath><g clip-path="url(#tf5ddd81e71a1450facbcc6eded29354e)"><g class="toyplot-mark-Text" id="t4c18187e135547389b88f5d192e5e8ae" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,30.660377358490564)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-0</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,51.624737945492647)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-1</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,72.589098532494759)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-2</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,93.553459119496864)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-3</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,114.51781970649895)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-4</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,135.48218029350105)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-5</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,156.44654088050314)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-6</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,177.41090146750525)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-7</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,198.37526205450732)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-8</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,219.33962264150944)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-9</tspan></text></g></g><g class="toyplot-mark-Graph" id="tfc1b5123c31341119e604511389ec6a3"><g class="toyplot-Edges"><path d="M 25.0 91.5880503145 L 25.0 46.3836477987" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 25.0 46.3836477987 L 120.61752988 46.3836477987" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 25.0 91.5880503145 L 25.0 136.79245283" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 25.0 136.79245283 L 56.8725099602 136.79245283" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 46.3836477987 L 120.61752988 30.6603773585" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 30.6603773585 L 184.362549801 30.6603773585" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 46.3836477987 L 120.61752988 62.106918239" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 62.106918239 L 152.490039841 62.106918239" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 56.8725099602 136.79245283 L 56.8725099602 104.035639413" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 56.8725099602 104.035639413 L 152.490039841 104.035639413" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 56.8725099602 136.79245283 L 56.8725099602 169.549266247" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 56.8725099602 169.549266247 L 88.7450199203 169.549266247" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 62.106918239 L 152.490039841 51.6247379455" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 51.6247379455 L 184.362549801 51.6247379455" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 62.106918239 L 152.490039841 72.5890985325" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 72.5890985325 L 184.362549801 72.5890985325" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 104.035639413 L 152.490039841 93.5534591195" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 93.5534591195 L 184.362549801 93.5534591195" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 104.035639413 L 152.490039841 114.517819706" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 114.517819706 L 184.362549801 114.517819706" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 88.7450199203 169.549266247 L 88.7450199203 145.964360587" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 88.7450199203 145.964360587 L 152.490039841 145.964360587" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 88.7450199203 169.549266247 L 88.7450199203 193.134171908" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 88.7450199203 193.134171908 L 120.61752988 193.134171908" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 145.964360587 L 152.490039841 135.482180294" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 135.482180294 L 184.362549801 135.482180294" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 145.964360587 L 152.490039841 156.446540881" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 156.446540881 L 184.362549801 156.446540881" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 193.134171908 L 120.61752988 177.410901468" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 177.410901468 L 184.362549801 177.410901468" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 193.134171908 L 120.61752988 208.857442348" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 208.857442348 L 152.490039841 208.857442348" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 208.857442348 L 152.490039841 198.375262055" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 198.375262055 L 184.362549801 198.375262055" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 208.857442348 L 152.490039841 219.339622642" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 219.339622642 L 184.362549801 219.339622642" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="25.0" cy="91.588050314465406" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="25.0" cy="46.383647798742132" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="46.383647798742132" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="25.0" cy="136.79245283018869" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="56.872509960159363" cy="136.79245283018869" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="46.383647798742132" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="30.660377358490564" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="30.660377358490564" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="62.1069182389937" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="62.1069182389937" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="56.872509960159363" cy="136.79245283018869" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="56.872509960159363" cy="104.0356394129979" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="104.0356394129979" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="56.872509960159363" cy="169.54926624737945" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="88.745019920318725" cy="169.54926624737945" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="62.1069182389937" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="51.624737945492647" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="51.624737945492647" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="72.589098532494759" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="72.589098532494759" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="104.0356394129979" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="93.553459119496864" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="93.553459119496864" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="114.51781970649895" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="114.51781970649895" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="88.745019920318725" cy="169.54926624737945" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="88.745019920318725" cy="145.96436058700209" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="145.96436058700209" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="88.745019920318725" cy="193.13417190775681" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="193.13417190775681" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="145.96436058700209" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="135.48218029350105" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="135.48218029350105" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="156.44654088050314" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="156.44654088050314" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="193.13417190775681" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="177.41090146750525" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="177.41090146750525" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="208.85744234800839" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="208.85744234800839" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="208.85744234800839" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="198.37526205450732" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="198.37526205450732" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="219.33962264150944" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="219.33962264150944" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="td37a99ba135a4b32b2a0b8215f25ef4b" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="25.0" cy="91.588050314465406" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="120.6175298804781" cy="46.383647798742132" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="152.49003984063745" cy="62.1069182389937" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="56.872509960159363" cy="136.79245283018869" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="152.49003984063745" cy="104.0356394129979" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="88.745019920318725" cy="169.54926624737945" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="152.49003984063745" cy="145.96436058700209" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="120.6175298804781" cy="193.13417190775681" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="152.49003984063745" cy="208.85744234800839" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="30.660377358490564" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="51.624737945492647" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="72.589098532494759" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="93.553459119496864" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="114.51781970649895" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="135.48218029350105" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="156.44654088050314" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="177.41090146750525" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="198.37526205450732" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(90.6%,54.1%,76.5%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="219.33962264150944" r="0.0"></circle></g></g></g><g class="toyplot-mark-Text" id="tef7ee5eed8ea44d69afbafe7ff1e839d" style="alignment-baseline:middle;fill:262626;font-size:9px;font-weight:normal;stroke:none;text-anchor:middle"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(120.6175298804781,46.383647798742132)translate(0,2.53125)"><tspan style="font-size:9.0px">1</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(152.49003984063745,62.1069182389937)translate(0,2.53125)"><tspan style="font-size:9.0px">1</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(56.872509960159363,136.79245283018869)translate(0,2.53125)"><tspan style="font-size:9.0px">1</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(152.49003984063745,104.0356394129979)translate(0,2.53125)"><tspan style="font-size:9.0px">1</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(88.745019920318725,169.54926624737945)translate(0,2.53125)"><tspan style="font-size:9.0px">1</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(152.49003984063745,145.96436058700209)translate(0,2.53125)"><tspan style="font-size:9.0px">1</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(120.6175298804781,193.13417190775681)translate(0,2.53125)"><tspan style="font-size:9.0px">1</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(152.49003984063745,208.85744234800839)translate(0,2.53125)"><tspan style="font-size:9.0px">1</tspan></text></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "td37a99ba135a4b32b2a0b8215f25ef4b", "columns": [[-5.0, -2.0, -1.0, -4.0, -1.0, -3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [6.09375, 8.25, 7.5, 3.9375, 5.5, 2.375, 3.5, 1.25, 0.5, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

          function save_csv(data_table)
          {
            var uri = "data:text/csv;charset=utf-8,";
            uri += data_table.names.join(",") + "\n";
            for(var i = 0; i != data_table.columns[0].length; ++i)
            {
              for(var j = 0; j != data_table.columns.length; ++j)
              {
                if(j)
                  uri += ",";
                uri += data_table.columns[j][i];
              }
              uri += "\n";
            }
            uri = encodeURI(uri);

            var link = document.createElement("a");
            if(typeof link.download != "undefined")
            {
              link.href = uri;
              link.style = "visibility:hidden";
              link.download = data_table.filename + ".csv";

              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
            }
            else
            {
              window.open(uri);
            }
          }

          function open_popup(data_table)
          {
            return function(e)
            {
              var popup = document.querySelector("#ta076e70ab9a04b5e90b6c9ef26d0c9a8 .toyplot-mark-popup");
              popup.querySelector(".toyplot-mark-popup-title").innerHTML = data_table.title;
              popup.querySelector(".toyplot-mark-popup-save-csv").onclick = function() { popup.style.visibility = "hidden"; save_csv(data_table); }
              popup.style.left = (e.clientX - 50) + "px";
              popup.style.top = (e.clientY - 20) + "px";
              popup.style.visibility = "visible";
              e.stopPropagation();
              e.preventDefault();
            }

          }

          for(var i = 0; i != data_tables.length; ++i)
          {
            var data_table = data_tables[i];
            var event_target = document.querySelector("#" + data_table.id);
            event_target.oncontextmenu = open_popup(data_table);
          }
        })();
        </script></div></div>


### toytree.tree (ete3mini.Tree)
The toytree.tree object is an `ete3mini.Tree` object which has nearly all of the same functionality as a standard ete tree. Thus, you can read the very detailed [ete documentation](http://etetoolkit.org) if you want a very detailed understanding of the object. Most users will not need to interact with this object, however, if you want to annotate your tree with extendable meta-data knowing how to do that can be very useful. 


```python
## the .tree attribute is the tree structure in memory
## which accesses the root node initially
tre.tree
```




    Tree node '0' (0x7f8e02e8739)



### Traversing/modifying the tree


```python
## traverse the tree and access node attributes
for node in tre.tree.traverse(strategy="levelorder"):
    print "{:<5} {:<5} {:<5} {:<5}"\
          .format(node.idx, node.name, node.is_leaf(), node.is_root())
```

    0     0     0     1    
    1     1     0     0    
    3     3     0     0    
    9     t-0   1     0    
    2     2     0     0    
    4     4     0     0    
    5     5     0     0    
    10    t-1   1     0    
    11    t-2   1     0    
    12    t-3   1     0    
    13    t-4   1     0    
    6     6     0     0    
    7     7     0     0    
    14    t-5   1     0    
    15    t-6   1     0    
    16    t-7   1     0    
    8     8     0     0    
    17    t-8   1     0    
    18    t-9   1     0    



```python
## traverse the tree and modify nodes (add new 'color' feature)
for node in tre.tree.traverse():
    if node.is_leaf():
        node.color=tre.colors[1]
    else:
        node.color=tre.colors[2]
        
## draw tree using new 'color' attribute
colors = tre.get_node_values('color', show_root=1, show_tips=1)
tre.draw(node_labels=True, node_color=colors);
```


<div align="center" class="toyplot" id="t02c7a2aa78de4d9fbc2d0d155d2a3302"><svg class="toyplot-canvas-Canvas" height="250.0px" id="te7522d01f9b8479895d492e02aa59ce4" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 250.0 250.0" width="250.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="td3f8a703ed584b77a1d0319ac6849a2a"><clipPath id="t0eaf1be6cfa14c38828c201b3a0dae51"><rect height="220.0" width="220.0" x="15.0" y="15.0"></rect></clipPath><g clip-path="url(#t0eaf1be6cfa14c38828c201b3a0dae51)"><g class="toyplot-mark-Text" id="t1b178cc62e394f1a80a546423b8d969e" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,30.660377358490564)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-0</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,51.624737945492647)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-1</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,72.589098532494759)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-2</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,93.553459119496864)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-3</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,114.51781970649895)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-4</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,135.48218029350105)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-5</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,156.44654088050314)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-6</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,177.41090146750525)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-7</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,198.37526205450732)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-8</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,219.33962264150944)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-9</tspan></text></g></g><g class="toyplot-mark-Graph" id="tb369dcc9e4f2485ba006fb742ce44559"><g class="toyplot-Edges"><path d="M 25.0 91.5880503145 L 25.0 46.3836477987" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 25.0 46.3836477987 L 120.61752988 46.3836477987" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 25.0 91.5880503145 L 25.0 136.79245283" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 25.0 136.79245283 L 56.8725099602 136.79245283" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 46.3836477987 L 120.61752988 30.6603773585" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 30.6603773585 L 184.362549801 30.6603773585" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 46.3836477987 L 120.61752988 62.106918239" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 62.106918239 L 152.490039841 62.106918239" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 56.8725099602 136.79245283 L 56.8725099602 104.035639413" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 56.8725099602 104.035639413 L 152.490039841 104.035639413" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 56.8725099602 136.79245283 L 56.8725099602 169.549266247" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 56.8725099602 169.549266247 L 88.7450199203 169.549266247" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 62.106918239 L 152.490039841 51.6247379455" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 51.6247379455 L 184.362549801 51.6247379455" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 62.106918239 L 152.490039841 72.5890985325" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 72.5890985325 L 184.362549801 72.5890985325" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 104.035639413 L 152.490039841 93.5534591195" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 93.5534591195 L 184.362549801 93.5534591195" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 104.035639413 L 152.490039841 114.517819706" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 114.517819706 L 184.362549801 114.517819706" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 88.7450199203 169.549266247 L 88.7450199203 145.964360587" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 88.7450199203 145.964360587 L 152.490039841 145.964360587" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 88.7450199203 169.549266247 L 88.7450199203 193.134171908" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 88.7450199203 193.134171908 L 120.61752988 193.134171908" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 145.964360587 L 152.490039841 135.482180294" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 135.482180294 L 184.362549801 135.482180294" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 145.964360587 L 152.490039841 156.446540881" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 156.446540881 L 184.362549801 156.446540881" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 193.134171908 L 120.61752988 177.410901468" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 177.410901468 L 184.362549801 177.410901468" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 193.134171908 L 120.61752988 208.857442348" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 208.857442348 L 152.490039841 208.857442348" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 208.857442348 L 152.490039841 198.375262055" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 198.375262055 L 184.362549801 198.375262055" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 208.857442348 L 152.490039841 219.339622642" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 219.339622642 L 184.362549801 219.339622642" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="25.0" cy="91.588050314465406" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="25.0" cy="46.383647798742132" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="46.383647798742132" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="25.0" cy="136.79245283018869" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="56.872509960159363" cy="136.79245283018869" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="46.383647798742132" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="30.660377358490564" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="30.660377358490564" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="62.1069182389937" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="62.1069182389937" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="56.872509960159363" cy="136.79245283018869" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="56.872509960159363" cy="104.0356394129979" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="104.0356394129979" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="56.872509960159363" cy="169.54926624737945" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="88.745019920318725" cy="169.54926624737945" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="62.1069182389937" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="51.624737945492647" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="51.624737945492647" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="72.589098532494759" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="72.589098532494759" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="104.0356394129979" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="93.553459119496864" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="93.553459119496864" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="114.51781970649895" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="114.51781970649895" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="88.745019920318725" cy="169.54926624737945" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="88.745019920318725" cy="145.96436058700209" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="145.96436058700209" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="88.745019920318725" cy="193.13417190775681" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="193.13417190775681" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="145.96436058700209" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="135.48218029350105" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="135.48218029350105" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="156.44654088050314" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="156.44654088050314" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="193.13417190775681" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="177.41090146750525" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="177.41090146750525" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="208.85744234800839" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="208.85744234800839" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="208.85744234800839" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="198.37526205450732" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="198.37526205450732" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="219.33962264150944" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="219.33962264150944" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t31684c1b4ccc418890f7d299999e9afa" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 0
name: 0
dist: 0
support: 100</title><circle cx="25.0" cy="91.588050314465406" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 1
name: 1
dist: 1
support: 1</title><circle cx="120.6175298804781" cy="46.383647798742132" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 2
name: 2
dist: 1
support: 1</title><circle cx="152.49003984063745" cy="62.1069182389937" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 3
name: 3
dist: 1
support: 1</title><circle cx="56.872509960159363" cy="136.79245283018869" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 4
name: 4
dist: 1
support: 1</title><circle cx="152.49003984063745" cy="104.0356394129979" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 5
name: 5
dist: 1
support: 1</title><circle cx="88.745019920318725" cy="169.54926624737945" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 6
name: 6
dist: 1
support: 1</title><circle cx="152.49003984063745" cy="145.96436058700209" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 7
name: 7
dist: 1
support: 1</title><circle cx="120.6175298804781" cy="193.13417190775681" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(55.3%,62.7%,79.6%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 8
name: 8
dist: 1
support: 1</title><circle cx="152.49003984063745" cy="208.85744234800839" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 9
name: t-0
dist: 1
support: 100</title><circle cx="184.36254980079681" cy="30.660377358490564" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 10
name: t-1
dist: 1
support: 100</title><circle cx="184.36254980079681" cy="51.624737945492647" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 11
name: t-2
dist: 1
support: 100</title><circle cx="184.36254980079681" cy="72.589098532494759" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 12
name: t-3
dist: 1
support: 100</title><circle cx="184.36254980079681" cy="93.553459119496864" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 13
name: t-4
dist: 1
support: 100</title><circle cx="184.36254980079681" cy="114.51781970649895" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 14
name: t-5
dist: 1
support: 100</title><circle cx="184.36254980079681" cy="135.48218029350105" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 15
name: t-6
dist: 1
support: 100</title><circle cx="184.36254980079681" cy="156.44654088050314" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 16
name: t-7
dist: 1
support: 100</title><circle cx="184.36254980079681" cy="177.41090146750525" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 17
name: t-8
dist: 1
support: 100</title><circle cx="184.36254980079681" cy="198.37526205450732" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 18
name: t-9
dist: 1
support: 100</title><circle cx="184.36254980079681" cy="219.33962264150944" r="7.5"></circle></g></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "t31684c1b4ccc418890f7d299999e9afa", "columns": [[-5.0, -2.0, -1.0, -4.0, -1.0, -3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [6.09375, 8.25, 7.5, 3.9375, 5.5, 2.375, 3.5, 1.25, 0.5, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

          function save_csv(data_table)
          {
            var uri = "data:text/csv;charset=utf-8,";
            uri += data_table.names.join(",") + "\n";
            for(var i = 0; i != data_table.columns[0].length; ++i)
            {
              for(var j = 0; j != data_table.columns.length; ++j)
              {
                if(j)
                  uri += ",";
                uri += data_table.columns[j][i];
              }
              uri += "\n";
            }
            uri = encodeURI(uri);

            var link = document.createElement("a");
            if(typeof link.download != "undefined")
            {
              link.href = uri;
              link.style = "visibility:hidden";
              link.download = data_table.filename + ".csv";

              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
            }
            else
            {
              window.open(uri);
            }
          }

          function open_popup(data_table)
          {
            return function(e)
            {
              var popup = document.querySelector("#t02c7a2aa78de4d9fbc2d0d155d2a3302 .toyplot-mark-popup");
              popup.querySelector(".toyplot-mark-popup-title").innerHTML = data_table.title;
              popup.querySelector(".toyplot-mark-popup-save-csv").onclick = function() { popup.style.visibility = "hidden"; save_csv(data_table); }
              popup.style.left = (e.clientX - 50) + "px";
              popup.style.top = (e.clientY - 20) + "px";
              popup.style.visibility = "visible";
              e.stopPropagation();
              e.preventDefault();
            }

          }

          for(var i = 0; i != data_tables.length; ++i)
          {
            var data_table = data_tables[i];
            var event_target = document.querySelector("#" + data_table.id);
            event_target.oncontextmenu = open_popup(data_table);
          }
        })();
        </script></div></div>


### toytree.edges
This is an array of edges connecting nodes. For example, node 1 connects to node 9, and node 1 connects to node 10. This is used to draw the tree and should generally not be modified by a user.


```python
tre.edges
```




    array([[ 1,  9],
           [ 2, 10],
           [ 2, 11],
           [ 1,  2],
           [ 0,  1],
           [ 4, 12],
           [ 4, 13],
           [ 3,  4],
           [ 6, 14],
           [ 6, 15],
           [ 5,  6],
           [ 7, 16],
           [ 8, 17],
           [ 8, 18],
           [ 7,  8],
           [ 5,  7],
           [ 3,  5],
           [ 0,  3]])



### toytree.verts
This is an array with the coordinate locations of the vertices (nodes) of the tree. This is used to draw the tree, however, it can also be useful to the user. For example, you can enter in the vertex coordinates to add additional points to the tree after plotting. Below is an example. 


```python
## show the verts array
tre.verts
```




    array([[-5.     ,  6.09375],
           [-2.     ,  8.25   ],
           [-1.     ,  7.5    ],
           [-4.     ,  3.9375 ],
           [-1.     ,  5.5    ],
           [-3.     ,  2.375  ],
           [-1.     ,  3.5    ],
           [-2.     ,  1.25   ],
           [-1.     ,  0.5    ],
           [ 0.     ,  9.     ],
           [ 0.     ,  8.     ],
           [ 0.     ,  7.     ],
           [ 0.     ,  6.     ],
           [ 0.     ,  5.     ],
           [ 0.     ,  4.     ],
           [ 0.     ,  3.     ],
           [ 0.     ,  2.     ],
           [ 0.     ,  1.     ],
           [ 0.     ,  0.     ]])




```python
## draw a tree
canvas, axes = tre.draw();

## add scatterplot points to the axes (standard toyplot plotting)
axes.scatterplot(
    a=tre.verts[:, 0],
    b=tre.verts[:, 1],
    size=10,
    marker='o'
    );
```


<div align="center" class="toyplot" id="t012a16e9c12b4996a7e386f092a3fb79"><svg class="toyplot-canvas-Canvas" height="250.0px" id="t74e0e21bf3eb47a09c7dd9c31e95fdf6" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 250.0 250.0" width="250.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t7e334ec2bfdb4a92be7590a3a1c643e1"><clipPath id="t47031f7105ec4996bde0c40b1e1c74e8"><rect height="220.0" width="220.0" x="15.0" y="15.0"></rect></clipPath><g clip-path="url(#t47031f7105ec4996bde0c40b1e1c74e8)"><g class="toyplot-mark-Text" id="tbf96b0d7fe7c4048af88b1415b05aabe" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,30.660377358490564)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-0</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,51.624737945492647)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-1</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,72.589098532494759)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-2</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,93.553459119496864)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-3</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,114.51781970649895)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-4</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,135.48218029350105)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-5</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,156.44654088050314)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-6</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,177.41090146750525)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-7</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,198.37526205450732)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-8</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(184.36254980079681,219.33962264150944)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-9</tspan></text></g></g><g class="toyplot-mark-Graph" id="tf832f7b4c5a24db188556daf7d0394ad"><g class="toyplot-Edges"><path d="M 25.0 91.5880503145 L 25.0 46.3836477987" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 25.0 46.3836477987 L 120.61752988 46.3836477987" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 25.0 91.5880503145 L 25.0 136.79245283" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 25.0 136.79245283 L 56.8725099602 136.79245283" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 46.3836477987 L 120.61752988 30.6603773585" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 30.6603773585 L 184.362549801 30.6603773585" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 46.3836477987 L 120.61752988 62.106918239" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 62.106918239 L 152.490039841 62.106918239" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 56.8725099602 136.79245283 L 56.8725099602 104.035639413" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 56.8725099602 104.035639413 L 152.490039841 104.035639413" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 56.8725099602 136.79245283 L 56.8725099602 169.549266247" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 56.8725099602 169.549266247 L 88.7450199203 169.549266247" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 62.106918239 L 152.490039841 51.6247379455" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 51.6247379455 L 184.362549801 51.6247379455" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 62.106918239 L 152.490039841 72.5890985325" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 72.5890985325 L 184.362549801 72.5890985325" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 104.035639413 L 152.490039841 93.5534591195" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 93.5534591195 L 184.362549801 93.5534591195" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 104.035639413 L 152.490039841 114.517819706" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 114.517819706 L 184.362549801 114.517819706" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 88.7450199203 169.549266247 L 88.7450199203 145.964360587" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 88.7450199203 145.964360587 L 152.490039841 145.964360587" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 88.7450199203 169.549266247 L 88.7450199203 193.134171908" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 88.7450199203 193.134171908 L 120.61752988 193.134171908" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 145.964360587 L 152.490039841 135.482180294" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 135.482180294 L 184.362549801 135.482180294" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 145.964360587 L 152.490039841 156.446540881" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 156.446540881 L 184.362549801 156.446540881" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 193.134171908 L 120.61752988 177.410901468" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 177.410901468 L 184.362549801 177.410901468" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 193.134171908 L 120.61752988 208.857442348" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 120.61752988 208.857442348 L 152.490039841 208.857442348" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 208.857442348 L 152.490039841 198.375262055" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 198.375262055 L 184.362549801 198.375262055" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 208.857442348 L 152.490039841 219.339622642" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 152.490039841 219.339622642 L 184.362549801 219.339622642" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="25.0" cy="91.588050314465406" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="25.0" cy="46.383647798742132" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="46.383647798742132" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="25.0" cy="136.79245283018869" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="56.872509960159363" cy="136.79245283018869" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="46.383647798742132" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="30.660377358490564" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="30.660377358490564" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="62.1069182389937" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="62.1069182389937" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="56.872509960159363" cy="136.79245283018869" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="56.872509960159363" cy="104.0356394129979" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="104.0356394129979" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="56.872509960159363" cy="169.54926624737945" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="88.745019920318725" cy="169.54926624737945" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="62.1069182389937" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="51.624737945492647" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="51.624737945492647" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="72.589098532494759" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="72.589098532494759" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="104.0356394129979" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="93.553459119496864" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="93.553459119496864" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="114.51781970649895" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="114.51781970649895" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="88.745019920318725" cy="169.54926624737945" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="88.745019920318725" cy="145.96436058700209" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="145.96436058700209" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="88.745019920318725" cy="193.13417190775681" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="193.13417190775681" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="145.96436058700209" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="135.48218029350105" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="135.48218029350105" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="156.44654088050314" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="156.44654088050314" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="193.13417190775681" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="177.41090146750525" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="177.41090146750525" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="208.85744234800839" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="208.85744234800839" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="208.85744234800839" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="198.37526205450732" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="198.37526205450732" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="219.33962264150944" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="219.33962264150944" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t71a8c3b7679241fca0b736af0750b66b" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="25.0" cy="91.588050314465406" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="120.6175298804781" cy="46.383647798742132" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="152.49003984063745" cy="62.1069182389937" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="56.872509960159363" cy="136.79245283018869" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="152.49003984063745" cy="104.0356394129979" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="88.745019920318725" cy="169.54926624737945" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="152.49003984063745" cy="145.96436058700209" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="120.6175298804781" cy="193.13417190775681" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="152.49003984063745" cy="208.85744234800839" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="30.660377358490564" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="51.624737945492647" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="72.589098532494759" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="93.553459119496864" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="114.51781970649895" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="135.48218029350105" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="156.44654088050314" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="177.41090146750525" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="198.37526205450732" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="184.36254980079681" cy="219.33962264150944" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t007a84fe38d047b698802a8bdb431518" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="25.0" cy="91.588050314465406" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="46.383647798742132" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="62.1069182389937" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="56.872509960159363" cy="136.79245283018869" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="104.0356394129979" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="88.745019920318725" cy="169.54926624737945" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="145.96436058700209" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="120.6175298804781" cy="193.13417190775681" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="152.49003984063745" cy="208.85744234800839" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="30.660377358490564" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="51.624737945492647" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="72.589098532494759" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="93.553459119496864" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="114.51781970649895" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="135.48218029350105" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="156.44654088050314" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="177.41090146750525" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="198.37526205450732" r="5.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0"><circle cx="184.36254980079681" cy="219.33962264150944" r="5.0"></circle></g></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "t71a8c3b7679241fca0b736af0750b66b", "columns": [[-5.0, -2.0, -1.0, -4.0, -1.0, -3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [6.09375, 8.25, 7.5, 3.9375, 5.5, 2.375, 3.5, 1.25, 0.5, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}, {"title": "Scatterplot Data", "names": ["x", "y0"], "id": "t007a84fe38d047b698802a8bdb431518", "columns": [[-5.0, -2.0, -1.0, -4.0, -1.0, -3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [6.09375, 8.25, 7.5, 3.9375, 5.5, 2.375, 3.5, 1.25, 0.5, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

          function save_csv(data_table)
          {
            var uri = "data:text/csv;charset=utf-8,";
            uri += data_table.names.join(",") + "\n";
            for(var i = 0; i != data_table.columns[0].length; ++i)
            {
              for(var j = 0; j != data_table.columns.length; ++j)
              {
                if(j)
                  uri += ",";
                uri += data_table.columns[j][i];
              }
              uri += "\n";
            }
            uri = encodeURI(uri);

            var link = document.createElement("a");
            if(typeof link.download != "undefined")
            {
              link.href = uri;
              link.style = "visibility:hidden";
              link.download = data_table.filename + ".csv";

              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
            }
            else
            {
              window.open(uri);
            }
          }

          function open_popup(data_table)
          {
            return function(e)
            {
              var popup = document.querySelector("#t012a16e9c12b4996a7e386f092a3fb79 .toyplot-mark-popup");
              popup.querySelector(".toyplot-mark-popup-title").innerHTML = data_table.title;
              popup.querySelector(".toyplot-mark-popup-save-csv").onclick = function() { popup.style.visibility = "hidden"; save_csv(data_table); }
              popup.style.left = (e.clientX - 50) + "px";
              popup.style.top = (e.clientY - 20) + "px";
              popup.style.visibility = "visible";
              e.stopPropagation();
              e.preventDefault();
            }

          }

          for(var i = 0; i != data_tables.length; ++i)
          {
            var data_table = data_tables[i];
            var event_target = document.querySelector("#" + data_table.id);
            event_target.oncontextmenu = open_popup(data_table);
          }
        })();
        </script></div></div>


### toytree.root
The root function can be used to re-root a tree. 


```python
## root on a list of names
tre.root(["t-1", "t-2"])

## or root on a wildcard selector (here all matches in 7-9)
tre.root(wildcard="t-[7-9]")
```


```python
tre.draw(width=200);
```


<div align="center" class="toyplot" id="tf147696a58f342c3a2d6612e90fe7f17"><svg class="toyplot-canvas-Canvas" height="200.0px" id="t6392198ecbb440e7a3fedc6a3e8b1a8d" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 200.0 200.0" width="200.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="tc9aa4880669442ff9386eb1d4f4dbbb6"><clipPath id="t9df96c4e886f41ff8d4e4b1b489e3084"><rect height="180.0" width="180.0" x="10.0" y="10.0"></rect></clipPath><g clip-path="url(#t9df96c4e886f41ff8d4e4b1b489e3084)"><g class="toyplot-mark-Text" id="t8b4c023c550a4bb9bd7abe0e533b85fa" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(141.32701421800948,25.581395348837219)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-7</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(141.32701421800948,42.118863049095609)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-8</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(141.32701421800948,58.656330749354005)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-9</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(141.32701421800948,75.193798449612416)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-5</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(141.32701421800948,91.731266149870805)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-6</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(141.32701421800948,108.26873385012919)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-3</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(141.32701421800948,124.8062015503876)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-4</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(141.32701421800948,141.34366925064603)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-0</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(141.32701421800948,157.88113695090439)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-1</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(141.32701421800948,174.41860465116281)translate(15.0,3.375)"><tspan style="font-size:12.0px">t-2</tspan></text></g></g><g class="toyplot-mark-Graph" id="tfbf37aeb582440c09600ed60198dc579"><g class="toyplot-Edges"><path d="M 20.0 73.6434108527 L 20.0 37.984496124" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 20.0 37.984496124 L 92.7962085308 37.984496124" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 20.0 73.6434108527 L 20.0 109.302325581" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 20.0 109.302325581 L 44.2654028436 109.302325581" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 92.7962085308 37.984496124 L 92.7962085308 25.5813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 92.7962085308 25.5813953488 L 141.327014218 25.5813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 92.7962085308 37.984496124 L 92.7962085308 50.3875968992" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 92.7962085308 50.3875968992 L 117.061611374 50.3875968992" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 44.2654028436 109.302325581 L 44.2654028436 83.4625322997" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 44.2654028436 83.4625322997 L 117.061611374 83.4625322997" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 44.2654028436 109.302325581 L 44.2654028436 135.142118863" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 44.2654028436 135.142118863 L 68.5308056872 135.142118863" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 117.061611374 50.3875968992 L 117.061611374 42.1188630491" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 117.061611374 42.1188630491 L 141.327014218 42.1188630491" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 117.061611374 50.3875968992 L 117.061611374 58.6563307494" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 117.061611374 58.6563307494 L 141.327014218 58.6563307494" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 117.061611374 83.4625322997 L 117.061611374 75.1937984496" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 117.061611374 75.1937984496 L 141.327014218 75.1937984496" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 117.061611374 83.4625322997 L 117.061611374 91.7312661499" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 117.061611374 91.7312661499 L 141.327014218 91.7312661499" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 68.5308056872 135.142118863 L 68.5308056872 116.5374677" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 68.5308056872 116.5374677 L 117.061611374 116.5374677" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 68.5308056872 135.142118863 L 68.5308056872 153.746770026" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 68.5308056872 153.746770026 L 92.7962085308 153.746770026" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 117.061611374 116.5374677 L 117.061611374 108.26873385" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 117.061611374 108.26873385 L 141.327014218 108.26873385" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 117.061611374 116.5374677 L 117.061611374 124.80620155" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 117.061611374 124.80620155 L 141.327014218 124.80620155" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 92.7962085308 153.746770026 L 92.7962085308 141.343669251" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 92.7962085308 141.343669251 L 141.327014218 141.343669251" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 92.7962085308 153.746770026 L 92.7962085308 166.149870801" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 92.7962085308 166.149870801 L 117.061611374 166.149870801" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 117.061611374 166.149870801 L 117.061611374 157.881136951" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 117.061611374 157.881136951 L 141.327014218 157.881136951" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 117.061611374 166.149870801 L 117.061611374 174.418604651" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 117.061611374 174.418604651 L 141.327014218 174.418604651" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="20.0" cy="73.643410852713188" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="20.0" cy="37.984496124031004" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="92.796208530805671" cy="37.984496124031004" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="20.0" cy="109.30232558139534" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="44.265402843601898" cy="109.30232558139534" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="92.796208530805671" cy="37.984496124031004" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="92.796208530805671" cy="25.581395348837219" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="141.32701421800948" cy="25.581395348837219" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="92.796208530805671" cy="50.387596899224803" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="117.06161137440759" cy="50.387596899224803" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="44.265402843601898" cy="109.30232558139534" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="44.265402843601898" cy="83.462532299741596" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="117.06161137440759" cy="83.462532299741596" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="44.265402843601898" cy="135.14211886304909" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="68.530805687203795" cy="135.14211886304909" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="117.06161137440759" cy="50.387596899224803" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="117.06161137440759" cy="42.118863049095609" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="141.32701421800948" cy="42.118863049095609" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="117.06161137440759" cy="58.656330749354005" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="141.32701421800948" cy="58.656330749354005" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="117.06161137440759" cy="83.462532299741596" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="117.06161137440759" cy="75.193798449612416" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="141.32701421800948" cy="75.193798449612416" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="117.06161137440759" cy="91.731266149870805" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="141.32701421800948" cy="91.731266149870805" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="68.530805687203795" cy="135.14211886304909" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="68.530805687203795" cy="116.5374677002584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="117.06161137440759" cy="116.5374677002584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="68.530805687203795" cy="153.74677002583979" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="92.796208530805671" cy="153.74677002583979" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="117.06161137440759" cy="116.5374677002584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="117.06161137440759" cy="108.26873385012919" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="141.32701421800948" cy="108.26873385012919" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="117.06161137440759" cy="124.8062015503876" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="141.32701421800948" cy="124.8062015503876" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="92.796208530805671" cy="153.74677002583979" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="92.796208530805671" cy="141.34366925064603" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="141.32701421800948" cy="141.34366925064603" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="92.796208530805671" cy="166.14987080103361" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="117.06161137440759" cy="166.14987080103361" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="117.06161137440759" cy="166.14987080103361" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="117.06161137440759" cy="157.88113695090439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="141.32701421800948" cy="157.88113695090439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="117.06161137440759" cy="174.41860465116281" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="141.32701421800948" cy="174.41860465116281" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="tf25068d06d5c4aa3a808ce68ee5eaa4a" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="20.0" cy="73.643410852713188" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="92.796208530805671" cy="37.984496124031004" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="117.06161137440759" cy="50.387596899224803" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="44.265402843601898" cy="109.30232558139534" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="117.06161137440759" cy="83.462532299741596" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="68.530805687203795" cy="135.14211886304909" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="117.06161137440759" cy="116.5374677002584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="92.796208530805671" cy="153.74677002583979" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="117.06161137440759" cy="166.14987080103361" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="141.32701421800948" cy="25.581395348837219" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="141.32701421800948" cy="42.118863049095609" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="141.32701421800948" cy="58.656330749354005" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="141.32701421800948" cy="75.193798449612416" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="141.32701421800948" cy="91.731266149870805" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="141.32701421800948" cy="108.26873385012919" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="141.32701421800948" cy="124.8062015503876" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="141.32701421800948" cy="141.34366925064603" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="141.32701421800948" cy="157.88113695090439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="141.32701421800948" cy="174.41860465116281" r="0.0"></circle></g></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "tf25068d06d5c4aa3a808ce68ee5eaa4a", "columns": [[-5.0, -2.0, -1.0, -4.0, -1.0, -3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], [6.09375, 8.25, 7.5, 3.9375, 5.5, 2.375, 3.5, 1.25, 0.5, 9.0, 8.0, 7.0, 6.0, 5.0, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

          function save_csv(data_table)
          {
            var uri = "data:text/csv;charset=utf-8,";
            uri += data_table.names.join(",") + "\n";
            for(var i = 0; i != data_table.columns[0].length; ++i)
            {
              for(var j = 0; j != data_table.columns.length; ++j)
              {
                if(j)
                  uri += ",";
                uri += data_table.columns[j][i];
              }
              uri += "\n";
            }
            uri = encodeURI(uri);

            var link = document.createElement("a");
            if(typeof link.download != "undefined")
            {
              link.href = uri;
              link.style = "visibility:hidden";
              link.download = data_table.filename + ".csv";

              document.body.appendChild(link);
              link.click();
              document.body.removeChild(link);
            }
            else
            {
              window.open(uri);
            }
          }

          function open_popup(data_table)
          {
            return function(e)
            {
              var popup = document.querySelector("#tf147696a58f342c3a2d6612e90fe7f17 .toyplot-mark-popup");
              popup.querySelector(".toyplot-mark-popup-title").innerHTML = data_table.title;
              popup.querySelector(".toyplot-mark-popup-save-csv").onclick = function() { popup.style.visibility = "hidden"; save_csv(data_table); }
              popup.style.left = (e.clientX - 50) + "px";
              popup.style.top = (e.clientY - 20) + "px";
              popup.style.visibility = "visible";
              e.stopPropagation();
              e.preventDefault();
            }

          }

          for(var i = 0; i != data_tables.length; ++i)
          {
            var data_table = data_tables[i];
            var event_target = document.querySelector("#" + data_table.id);
            event_target.oncontextmenu = open_popup(data_table);
          }
        })();
        </script></div></div>


### toytree.get_node_values
This is explained in great detail in the [node-labels](node-labels.md) section. This can be used to return a list of node values that are extracted directly from the tree object and will always be in the correct order for plotting. 


```python
tre.get_node_values(feature='dist', show_root=True, show_tips=True)
```




    [0.0,
     0.5,
     1.0,
     0.5,
     1.0,
     1.0,
     1.0,
     2.0,
     1.0,
     1.0,
     1.0,
     1.0,
     1.0,
     1.0,
     1.0,
     1.0,
     1.0,
     1.0,
     1.0]



### toytree.get_edge_lengths
This is simply another way of requesting `tre.get_node_values('dist')`. You can use this to modify edges of the tree. 


```python
tre.get_edge_lengths()
```




    [0.0,
     0.5,
     1.0,
     0.5,
     1.0,
     1.0,
     1.0,
     2.0,
     1.0,
     1.0,
     1.0,
     1.0,
     1.0,
     1.0,
     1.0,
     1.0,
     1.0,
     1.0,
     1.0]



### tre.get_node_labels
This function returns a dictionary mapping node indices ('idx' numbers) to node names. It is not generally useful for the user. 


```python
tre.get_node_labels()
```




    {0: '0',
     1: '7',
     2: '8',
     3: '5',
     4: '6',
     5: '3',
     6: '4',
     7: '1',
     8: '2',
     9: 't-7',
     10: 't-8',
     11: 't-9',
     12: 't-5',
     13: 't-6',
     14: 't-3',
     15: 't-4',
     16: 't-0',
     17: 't-1',
     18: 't-2'}



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


