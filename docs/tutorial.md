
### Introduction

**Toytree** is a Python tree plotting library designed for use inside 
[jupyter notebooks](http://jupyter.org). In fact, this tutorial was created in a Jupyter notebook and assumes that you are following-along in a notebook of your own. Before getting started with **Toytree** it may be helpful to read some background on [**Toyplot**](http://toyplot.rtfd.io) to understand how figures are generated and displayed. If you aren’t using a notebook, you should read Toyplot's user guide section on [rendering](http://toyplot.readthedocs.io/en/stable/rendering.html#rendering) for some important information on how to display your figures.


To begin, import toyplot, toytree, and numpy. 


```python
import toytree     ## a tree plotting library
import toyplot     ## a general plotting library
import numpy       ## data generation 
```

### Toytree Class objects

Toytree has only two Python Class objects, the 
<span style="text-decoration:underline;">Toytree</span> object
that is used to represent a single tree, and the 
<span style="text-decoration:underline;">Multitree</span> object
that is used to represent a list of trees. 

To create a Toytree instance you must load in a tree representation from a newick string or file using the tree parsing function `toytree.tree`. This will parse the newick data to return a Toytree Object with the tree structure stored in memory. To do this, Toytree uses a stripped-down version of the [ete](http://etetoolkit.org) module (which we call ete3mini) for newick parsing and tree representation. Therefore, nearly all of the machinery that is available in [ete](http://etetoolkit.org) to modify and traverse trees is also available to Toytree objects. See the [Tree traversal/modification](toytrees.md) section for more details. 

### Reading/Parsing trees
Below are two trees in newick format. The first has edge lengths and support values, the second has edge-lengths and node-labels. These are two different ways of writing tree data in a serialized format. To parse either format you must tell toytree the format of the newick string following the [tree parsing formats in ete](http://etetoolkit.org/docs/latest/tutorial/tutorial_trees.html#reading-and-writing-newick-trees). The most commonly used format is 0, which is also the default. Toytree can also parse extended newick format files in which many types of metadata can be appended to a single tree.  


```python
## newick with edge-lengths & support values
newick = "((a:1,b:1)90:2,(c:3,(d:1, e:1)100:2)100:1)100;"
tre0 = toytree.tree(newick, format=0)

## newick with edge-lengths & string node-labels
newick = "((a:1,b:1)A:2,(c:3,(d:1, e:1)B:2)C:1)root;"
tre1 = toytree.tree(newick, format=1)
```

### Drawing trees (basics)


```python
## draw one tree
tre0.draw();
```


<div align="center" class="toyplot" id="t85fd3a7424564679ba4b08f419b09259"><svg class="toyplot-canvas-Canvas" height="125.0px" id="tec2427a4993e4b2a8f3e1962f3463a02" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 125.0 125.0" width="125.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t49dc658a73444b1492e4cb21d478d3c3"><clipPath id="t71df51357dc84fbe8a5694f0f1088a49"><rect height="120.0" width="120.0" x="2.5" y="2.5"></rect></clipPath><g clip-path="url(#t71df51357dc84fbe8a5694f0f1088a49)"><g class="toyplot-mark-Text" id="t5ebc2c13872f479e81e79f0017094485" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,17.857142857142861)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,40.178571428571431)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,62.5)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,84.821428571428584)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,107.14285714285714)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="t9ebde9cac3f04f98b0aad42a387681ee"><g class="toyplot-Edges"><path d="M 12.5 54.1294642857 L 12.5 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 29.0178571429 L 64.9934383202 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 54.1294642857 L 12.5 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 79.2410714286 L 38.7467191601 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 29.0178571429 L 64.9934383202 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 17.8571428571 L 91.2401574803 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 29.0178571429 L 64.9934383202 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 40.1785714286 L 91.2401574803 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 79.2410714286 L 38.7467191601 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 62.5 L 91.2401574803 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 79.2410714286 L 38.7467191601 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 95.9821428571 L 64.9934383202 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 95.9821428571 L 64.9934383202 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 84.8214285714 L 91.2401574803 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 95.9821428571 L 64.9934383202 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 107.142857143 L 91.2401574803 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="54.129464285714292" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="107.14285714285714" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="107.14285714285714" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="tb385d885ee774faa847f4353695b2ae7" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="12.5" cy="54.129464285714292" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="107.14285714285714" r="0.0"></circle></g></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "tb385d885ee774faa847f4353695b2ae7", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#t85fd3a7424564679ba4b08f419b09259 .toyplot-mark-popup");
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



```python
## draw multiple trees
tre0.draw();
tre1.draw();
```


<div align="center" class="toyplot" id="tc2cb77567ce74574817dfeac52524b55"><svg class="toyplot-canvas-Canvas" height="125.0px" id="tbddee53fa07c41e1a24c5f8e114dbbee" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 125.0 125.0" width="125.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="ta0e5108983a04ca7b838dd3c8fc7ca56"><clipPath id="t13b82c81ad9c480f96fc5c3d11bf29f9"><rect height="120.0" width="120.0" x="2.5" y="2.5"></rect></clipPath><g clip-path="url(#t13b82c81ad9c480f96fc5c3d11bf29f9)"><g class="toyplot-mark-Text" id="t20cd86edd764446c9522bab4d1fe46df" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,17.857142857142861)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,40.178571428571431)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,62.5)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,84.821428571428584)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,107.14285714285714)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="tfd35127b77044d11bc17314e63dfd115"><g class="toyplot-Edges"><path d="M 12.5 54.1294642857 L 12.5 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 29.0178571429 L 64.9934383202 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 54.1294642857 L 12.5 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 79.2410714286 L 38.7467191601 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 29.0178571429 L 64.9934383202 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 17.8571428571 L 91.2401574803 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 29.0178571429 L 64.9934383202 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 40.1785714286 L 91.2401574803 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 79.2410714286 L 38.7467191601 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 62.5 L 91.2401574803 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 79.2410714286 L 38.7467191601 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 95.9821428571 L 64.9934383202 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 95.9821428571 L 64.9934383202 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 84.8214285714 L 91.2401574803 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 95.9821428571 L 64.9934383202 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 107.142857143 L 91.2401574803 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="54.129464285714292" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="107.14285714285714" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="107.14285714285714" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="te3b75afd34c240dab25127a517ca857e" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="12.5" cy="54.129464285714292" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="107.14285714285714" r="0.0"></circle></g></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "te3b75afd34c240dab25127a517ca857e", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#tc2cb77567ce74574817dfeac52524b55 .toyplot-mark-popup");
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



<div align="center" class="toyplot" id="t1372ac902c014448937c5d19d18ee39f"><svg class="toyplot-canvas-Canvas" height="125.0px" id="tbe2d1f02d2e148d28b7c6dd3909fbaa1" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 125.0 125.0" width="125.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="tfe2cdb3c12be4307876f3d3da945e046"><clipPath id="ta6860d66827a4248911fdb8354ec1ff4"><rect height="120.0" width="120.0" x="2.5" y="2.5"></rect></clipPath><g clip-path="url(#ta6860d66827a4248911fdb8354ec1ff4)"><g class="toyplot-mark-Text" id="t8c3d011071d749aeb982c2d9599d9ee6" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,17.857142857142861)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,40.178571428571431)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,62.5)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,84.821428571428584)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,107.14285714285714)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="taf95be52fac2420793d2fc0ab1825140"><g class="toyplot-Edges"><path d="M 12.5 54.1294642857 L 12.5 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 29.0178571429 L 64.9934383202 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 54.1294642857 L 12.5 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 79.2410714286 L 38.7467191601 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 29.0178571429 L 64.9934383202 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 17.8571428571 L 91.2401574803 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 29.0178571429 L 64.9934383202 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 40.1785714286 L 91.2401574803 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 79.2410714286 L 38.7467191601 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 62.5 L 91.2401574803 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 79.2410714286 L 38.7467191601 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 95.9821428571 L 64.9934383202 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 95.9821428571 L 64.9934383202 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 84.8214285714 L 91.2401574803 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 95.9821428571 L 64.9934383202 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 107.142857143 L 91.2401574803 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="54.129464285714292" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="107.14285714285714" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="107.14285714285714" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t71abd6c17ba3442985e9a5b5b53cb8a5" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="12.5" cy="54.129464285714292" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="107.14285714285714" r="0.0"></circle></g></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "t71abd6c17ba3442985e9a5b5b53cb8a5", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#t1372ac902c014448937c5d19d18ee39f .toyplot-mark-popup");
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



```python
## organize trees on a canvas (more on this later)
canvas = toyplot.Canvas(width=400, height=200)
ax0 = canvas.cartesian(bounds=('10%', '40%', '10%', '90%'))
ax1 = canvas.cartesian(bounds=('60%', '90%', '10%', '90%'))
tre0.draw(axes=ax0);
tre1.draw(axes=ax1);
ax0.show=False
ax1.show=False
```


<div align="center" class="toyplot" id="te31bc75761c44b2cb717618bd567b1e6"><svg class="toyplot-canvas-Canvas" height="200.0px" id="td2d6b7df328f429a917349f7f5a6f6c5" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 400.0 200.0" width="400.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t68688edc17e047b29cceeb51ad543f87"><clipPath id="tdc21b37332324a848db352e97cee4430"><rect height="180.0" width="140.0" x="30.0" y="10.0"></rect></clipPath><g clip-path="url(#tdc21b37332324a848db352e97cee4430)"><g class="toyplot-mark-Text" id="t442f878cc1cd4c9083697c3c750ca662" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(137.95918367346937,25.581395348837219)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(137.95918367346937,62.790697674418624)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(137.95918367346937,100.00000000000001)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(137.95918367346937,137.2093023255814)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(137.95918367346937,174.41860465116281)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="t50a4c387e50b4ad6bace479dd43758b3"><g class="toyplot-Edges"><path d="M 40.0 86.0465116279 L 40.0 44.1860465116" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 40.0 44.1860465116 L 105.306122449 44.1860465116" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 40.0 86.0465116279 L 40.0 127.906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 40.0 127.906976744 L 72.6530612245 127.906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 105.306122449 44.1860465116 L 105.306122449 25.5813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 105.306122449 25.5813953488 L 137.959183673 25.5813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 105.306122449 44.1860465116 L 105.306122449 62.7906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 105.306122449 62.7906976744 L 137.959183673 62.7906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 72.6530612245 127.906976744 L 72.6530612245 100.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 72.6530612245 100.0 L 137.959183673 100.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 72.6530612245 127.906976744 L 72.6530612245 155.813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 72.6530612245 155.813953488 L 105.306122449 155.813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 105.306122449 155.813953488 L 105.306122449 137.209302326" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 105.306122449 137.209302326 L 137.959183673 137.209302326" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 105.306122449 155.813953488 L 105.306122449 174.418604651" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 105.306122449 174.418604651 L 137.959183673 174.418604651" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="40.0" cy="86.046511627906995" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="40.0" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="105.30612244897958" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="40.0" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="72.65306122448979" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="105.30612244897958" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="105.30612244897958" cy="25.581395348837219" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="137.95918367346937" cy="25.581395348837219" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="105.30612244897958" cy="62.790697674418624" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="137.95918367346937" cy="62.790697674418624" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="72.65306122448979" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="72.65306122448979" cy="100.00000000000001" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="137.95918367346937" cy="100.00000000000001" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="72.65306122448979" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="105.30612244897958" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="105.30612244897958" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="105.30612244897958" cy="137.2093023255814" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="137.95918367346937" cy="137.2093023255814" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="105.30612244897958" cy="174.41860465116281" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="137.95918367346937" cy="174.41860465116281" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t1c452af3457d4e02b1a3594f0dfdc481" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="40.0" cy="86.046511627906995" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="105.30612244897958" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="72.65306122448979" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="105.30612244897958" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="137.95918367346937" cy="25.581395348837219" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="137.95918367346937" cy="62.790697674418624" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="137.95918367346937" cy="100.00000000000001" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="137.95918367346937" cy="137.2093023255814" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="137.95918367346937" cy="174.41860465116281" r="0.0"></circle></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="te070728ea90e48a188d929b3eee14207"><clipPath id="tafb55387ed3342b6ac56b72371903378"><rect height="180.0" width="140.0" x="230.0" y="10.0"></rect></clipPath><g clip-path="url(#tafb55387ed3342b6ac56b72371903378)"><g class="toyplot-mark-Text" id="t4d4461a1a2634460b4843a4703ef28e2" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(337.9591836734694,25.581395348837219)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(337.9591836734694,62.790697674418624)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(337.9591836734694,100.00000000000001)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(337.9591836734694,137.2093023255814)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(337.9591836734694,174.41860465116281)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="t30604eaee85a4e8eb6af96a505990595"><g class="toyplot-Edges"><path d="M 240.0 86.0465116279 L 240.0 44.1860465116" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 240.0 44.1860465116 L 305.306122449 44.1860465116" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 240.0 86.0465116279 L 240.0 127.906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 240.0 127.906976744 L 272.653061224 127.906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 305.306122449 44.1860465116 L 305.306122449 25.5813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 305.306122449 25.5813953488 L 337.959183673 25.5813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 305.306122449 44.1860465116 L 305.306122449 62.7906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 305.306122449 62.7906976744 L 337.959183673 62.7906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 272.653061224 127.906976744 L 272.653061224 100.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 272.653061224 100.0 L 337.959183673 100.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 272.653061224 127.906976744 L 272.653061224 155.813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 272.653061224 155.813953488 L 305.306122449 155.813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 305.306122449 155.813953488 L 305.306122449 137.209302326" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 305.306122449 137.209302326 L 337.959183673 137.209302326" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 305.306122449 155.813953488 L 305.306122449 174.418604651" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 305.306122449 174.418604651 L 337.959183673 174.418604651" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="240.0" cy="86.046511627906995" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="240.0" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="305.30612244897958" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="240.0" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="272.65306122448982" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="305.30612244897958" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="305.30612244897958" cy="25.581395348837219" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="337.9591836734694" cy="25.581395348837219" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="305.30612244897958" cy="62.790697674418624" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="337.9591836734694" cy="62.790697674418624" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="272.65306122448982" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="272.65306122448982" cy="100.00000000000001" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="337.9591836734694" cy="100.00000000000001" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="272.65306122448982" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="305.30612244897958" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="305.30612244897958" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="305.30612244897958" cy="137.2093023255814" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="337.9591836734694" cy="137.2093023255814" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="305.30612244897958" cy="174.41860465116281" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="337.9591836734694" cy="174.41860465116281" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="ta1b00c5fe8b443e682d5ec06c72be856" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="240.0" cy="86.046511627906995" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="305.30612244897958" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="272.65306122448982" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="305.30612244897958" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="337.9591836734694" cy="25.581395348837219" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="337.9591836734694" cy="62.790697674418624" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="337.9591836734694" cy="100.00000000000001" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="337.9591836734694" cy="137.2093023255814" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="337.9591836734694" cy="174.41860465116281" r="0.0"></circle></g></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "t1c452af3457d4e02b1a3594f0dfdc481", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}, {"title": "Scatterplot Data", "names": ["x", "y0"], "id": "ta1b00c5fe8b443e682d5ec06c72be856", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#te31bc75761c44b2cb717618bd567b1e6 .toyplot-mark-popup");
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


### The Canvas 
When you call the `toytree.draw()` function it returns two Toyplot objects which are used to display the figure. The first is the Canvas, which is the HTML element that holds the figure, and the second is a Cartesian axes object, which represent the coordinates for the plot. You can catch these objects when they are returned by the `draw()` function to further manipulate the plot. 


```python
## catch canvas and axes from draw()
canvas, axes = tre0.draw(width=200, height=250)

## e.g., turn on or off some axes elements
axes.show = True
axes.y.show = False
axes.x.ticks.show = True
```


<div align="center" class="toyplot" id="t3ee7af439943412f8a83523588896219"><svg class="toyplot-canvas-Canvas" height="250.0px" id="t44fccfd8f4624f649a31ff20a7704281" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 200.0 250.0" width="200.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="tbf3bc0acbc3f47a5b1ec7f12a6bd18ee"><clipPath id="t6c635ddc89234589922bba9c8b79dd69"><rect height="220.0" width="180.0" x="10.0" y="15.0"></rect></clipPath><g clip-path="url(#t6c635ddc89234589922bba9c8b79dd69)"><g class="toyplot-mark-Text" id="t67e90209a7f14d558e446b01975ae7d5" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(156.89839572192514,30.660377358490564)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(156.89839572192514,77.830188679245296)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(156.89839572192514,125.0)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(156.89839572192514,172.16981132075475)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(156.89839572192514,219.33962264150944)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="t1de721b59bd94d648efa951d2c430b69"><g class="toyplot-Edges"><path d="M 20.0 107.311320755 L 20.0 54.2452830189" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 20.0 54.2452830189 L 111.265597148 54.2452830189" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 20.0 107.311320755 L 20.0 160.377358491" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 20.0 160.377358491 L 65.632798574 160.377358491" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 111.265597148 54.2452830189 L 111.265597148 30.6603773585" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 111.265597148 30.6603773585 L 156.898395722 30.6603773585" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 111.265597148 54.2452830189 L 111.265597148 77.8301886792" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 111.265597148 77.8301886792 L 156.898395722 77.8301886792" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 65.632798574 160.377358491 L 65.632798574 125.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 65.632798574 125.0 L 156.898395722 125.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 65.632798574 160.377358491 L 65.632798574 195.754716981" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 65.632798574 195.754716981 L 111.265597148 195.754716981" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 111.265597148 195.754716981 L 111.265597148 172.169811321" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 111.265597148 172.169811321 L 156.898395722 172.169811321" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 111.265597148 195.754716981 L 111.265597148 219.339622642" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 111.265597148 219.339622642 L 156.898395722 219.339622642" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="20.0" cy="107.31132075471699" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="20.0" cy="54.245283018867923" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="111.26559714795009" cy="54.245283018867923" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="20.0" cy="160.37735849056602" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="65.632798573975037" cy="160.37735849056602" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="111.26559714795009" cy="54.245283018867923" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="111.26559714795009" cy="30.660377358490564" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="156.89839572192514" cy="30.660377358490564" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="111.26559714795009" cy="77.830188679245296" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="156.89839572192514" cy="77.830188679245296" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="65.632798573975037" cy="160.37735849056602" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="65.632798573975037" cy="125.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="156.89839572192514" cy="125.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="65.632798573975037" cy="195.75471698113208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="111.26559714795009" cy="195.75471698113208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="111.26559714795009" cy="195.75471698113208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="111.26559714795009" cy="172.16981132075475" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="156.89839572192514" cy="172.16981132075475" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="111.26559714795009" cy="219.33962264150944" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="156.89839572192514" cy="219.33962264150944" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="tb93cc3085fff4dc9b572acfbbb66da21" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="20.0" cy="107.31132075471699" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="111.26559714795009" cy="54.245283018867923" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="65.632798573975037" cy="160.37735849056602" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="111.26559714795009" cy="195.75471698113208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="156.89839572192514" cy="30.660377358490564" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="156.89839572192514" cy="77.830188679245296" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="156.89839572192514" cy="125.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="156.89839572192514" cy="172.16981132075475" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="156.89839572192514" cy="219.33962264150944" r="0.0"></circle></g></g></g></g><g class="toyplot-coordinates-Axis" id="tfddf3ac126594d068b93797ef1e9cfaa" transform="translate(20.0,225.0)translate(0,10.0)"><line style="" x1="0" x2="136.89839572192514" y1="0" y2="0"></line><g><line style="" x1="0.0" x2="0.0" y1="0" y2="-5"></line><line style="" x1="45.632798573975045" x2="45.632798573975045" y1="0" y2="-5"></line><line style="" x1="91.26559714795009" x2="91.26559714795009" y1="0" y2="-5"></line><line style="" x1="136.89839572192514" x2="136.89839572192514" y1="0" y2="-5"></line></g><g><text style="font-weight:normal;stroke:none;text-anchor:middle" transform="translate(0.0,6)translate(0,7.5)"><tspan style="font-size:10.0px">-3</tspan></text><text style="font-weight:normal;stroke:none;text-anchor:middle" transform="translate(45.632798573975045,6)translate(0,7.5)"><tspan style="font-size:10.0px">-2</tspan></text><text style="font-weight:normal;stroke:none;text-anchor:middle" transform="translate(91.26559714795009,6)translate(0,7.5)"><tspan style="font-size:10.0px">-1</tspan></text><text style="font-weight:normal;stroke:none;text-anchor:middle" transform="translate(136.89839572192514,6)translate(0,7.5)"><tspan style="font-size:10.0px">0</tspan></text></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0" x1="0" x2="0" y1="-3.0" y2="4.5"></line><text style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle" x="0" y="-6"></text></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "tb93cc3085fff4dc9b572acfbbb66da21", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#t3ee7af439943412f8a83523588896219 .toyplot-mark-popup");
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
        </script><script>
        (function()
        {
            function _sign(x)
            {
                return x < 0 ? -1 : x > 0 ? 1 : 0;
            }

            function _mix(a, b, amount)
            {
                return ((1.0 - amount) * a) + (amount * b);
            }

            function _log(x, base)
            {
                return Math.log(Math.abs(x)) / Math.log(base);
            }

            function _in_range(a, x, b)
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
                    if(_in_range(segment.range.min, range, segment.range.max))
                        return true;
                }
                return false;
            }

            function to_domain(range, projection)
            {
                for(var i = 0; i != projection.length; ++i)
                {
                    var segment = projection[i];
                    if(_in_range(segment.range.bounds.min, range, segment.range.bounds.max))
                    {
                        if(segment.scale == "linear")
                        {
                            var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                            return _mix(segment.domain.min, segment.domain.max, amount)
                        }
                        else if(segment.scale[0] == "log")
                        {
                            var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                            var base = segment.scale[1];
                            return _sign(segment.domain.min) * Math.pow(base, _mix(_log(segment.domain.min, base), _log(segment.domain.max, base), amount));
                        }
                    }
                }
            }

            function display_coordinates(e)
            {
                var current = svg.createSVGPoint();
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

            var root_id = "t3ee7af439943412f8a83523588896219";
            var axes = {"tfddf3ac126594d068b93797ef1e9cfaa": [{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.5062499999999999, "min": -3.0}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 160.0, "min": 0.0}, "scale": "linear"}]};

            var svg = document.querySelector("#" + root_id + " svg");
            svg.addEventListener("click", display_coordinates);
        })();
        </script></div></div>


Or, instead of catching the canvas and axes auto-generated by the `toytree.draw()` function you can instead generate the canvas and axes yourself using Toyplot and pass the axes object as an argument to `draw()` to embed the tree within the axes coordinates. This is a useful way to combine multiple figures on a single canvas, or to annotate axes.


```python
## create the canvas 
canvas = toyplot.Canvas(width=250, height=250)
axes = canvas.cartesian(gutter=50)

## add tree to existing canvas
canvas, axes = tre0.draw(axes=axes)

## further modify the axes
axes.y.show = False
axes.x.ticks.show = True
axes.x.label.text = "Divergence time (Ma)"
```


<div align="center" class="toyplot" id="t3e21093f15ba49798b904db315211623"><svg class="toyplot-canvas-Canvas" height="250.0px" id="t3960a90807384f32b7949731b70fd0cd" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 250.0 250.0" width="250.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t712c31cfbe7b4220a863abb217efc871"><clipPath id="ta3b065ef6c2446b68a0800b23c05013f"><rect height="170.0" width="170.0" x="40.0" y="40.0"></rect></clipPath><g clip-path="url(#ta3b065ef6c2446b68a0800b23c05013f)"><g class="toyplot-mark-Text" id="tf54fa487005945d7b16f52f91d967330" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(177.11864406779659,55.555555555555564)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(177.11864406779659,90.277777777777771)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(177.11864406779659,125.0)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(177.11864406779659,159.72222222222223)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(177.11864406779659,194.44444444444446)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="ta9657b39668b4bc39c123536ea3eb4cc"><g class="toyplot-Edges"><path d="M 50.0 111.979166667 L 50.0 72.9166666667" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 72.9166666667 L 134.745762712 72.9166666667" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 111.979166667 L 50.0 151.041666667" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 151.041666667 L 92.3728813559 151.041666667" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 134.745762712 72.9166666667 L 134.745762712 55.5555555556" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 134.745762712 55.5555555556 L 177.118644068 55.5555555556" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 134.745762712 72.9166666667 L 134.745762712 90.2777777778" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 134.745762712 90.2777777778 L 177.118644068 90.2777777778" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 92.3728813559 151.041666667 L 92.3728813559 125.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 92.3728813559 125.0 L 177.118644068 125.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 92.3728813559 151.041666667 L 92.3728813559 177.083333333" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 92.3728813559 177.083333333 L 134.745762712 177.083333333" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 134.745762712 177.083333333 L 134.745762712 159.722222222" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 134.745762712 159.722222222 L 177.118644068 159.722222222" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 134.745762712 177.083333333 L 134.745762712 194.444444444" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 134.745762712 194.444444444 L 177.118644068 194.444444444" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="50.0" cy="111.97916666666666" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="50.0" cy="72.916666666666657" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="134.74576271186442" cy="72.916666666666657" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="50.0" cy="151.04166666666669" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="92.372881355932208" cy="151.04166666666669" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="134.74576271186442" cy="72.916666666666657" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="134.74576271186442" cy="55.555555555555564" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="177.11864406779659" cy="55.555555555555564" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="134.74576271186442" cy="90.277777777777771" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="177.11864406779659" cy="90.277777777777771" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="92.372881355932208" cy="151.04166666666669" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="92.372881355932208" cy="125.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="177.11864406779659" cy="125.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="92.372881355932208" cy="177.08333333333331" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="134.74576271186442" cy="177.08333333333331" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="134.74576271186442" cy="177.08333333333331" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="134.74576271186442" cy="159.72222222222223" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="177.11864406779659" cy="159.72222222222223" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="134.74576271186442" cy="194.44444444444446" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="177.11864406779659" cy="194.44444444444446" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="tdd234bb24ed947959cf0ecad31d940dc" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="50.0" cy="111.97916666666666" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="134.74576271186442" cy="72.916666666666657" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="92.372881355932208" cy="151.04166666666669" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="134.74576271186442" cy="177.08333333333331" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="177.11864406779659" cy="55.555555555555564" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="177.11864406779659" cy="90.277777777777771" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="177.11864406779659" cy="125.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="177.11864406779659" cy="159.72222222222223" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="177.11864406779659" cy="194.44444444444446" r="0.0"></circle></g></g></g></g><g class="toyplot-coordinates-Axis" id="t58f2fad5b9d048069979774b01c6082c" transform="translate(50.0,200.0)translate(0,10.0)"><line style="" x1="0" x2="127.11864406779661" y1="0" y2="0"></line><g><line style="" x1="0.0" x2="0.0" y1="0" y2="-5"></line><line style="" x1="42.37288135593221" x2="42.37288135593221" y1="0" y2="-5"></line><line style="" x1="84.74576271186442" x2="84.74576271186442" y1="0" y2="-5"></line><line style="" x1="127.11864406779661" x2="127.11864406779661" y1="0" y2="-5"></line></g><g><text style="font-weight:normal;stroke:none;text-anchor:middle" transform="translate(0.0,6)translate(0,7.5)"><tspan style="font-size:10.0px">-3</tspan></text><text style="font-weight:normal;stroke:none;text-anchor:middle" transform="translate(42.37288135593221,6)translate(0,7.5)"><tspan style="font-size:10.0px">-2</tspan></text><text style="font-weight:normal;stroke:none;text-anchor:middle" transform="translate(84.74576271186442,6)translate(0,7.5)"><tspan style="font-size:10.0px">-1</tspan></text><text style="font-weight:normal;stroke:none;text-anchor:middle" transform="translate(127.11864406779661,6)translate(0,7.5)"><tspan style="font-size:10.0px">0</tspan></text></g><text style="font-weight:bold;stroke:none;text-anchor:middle" transform="translate(75.0,22)translate(0,9.0)"><tspan style="font-size:12.0px">Divergence time (Ma)</tspan></text><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0" x1="0" x2="0" y1="-3.0" y2="4.5"></line><text style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle" x="0" y="-6"></text></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "tdd234bb24ed947959cf0ecad31d940dc", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#t3e21093f15ba49798b904db315211623 .toyplot-mark-popup");
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
        </script><script>
        (function()
        {
            function _sign(x)
            {
                return x < 0 ? -1 : x > 0 ? 1 : 0;
            }

            function _mix(a, b, amount)
            {
                return ((1.0 - amount) * a) + (amount * b);
            }

            function _log(x, base)
            {
                return Math.log(Math.abs(x)) / Math.log(base);
            }

            function _in_range(a, x, b)
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
                    if(_in_range(segment.range.min, range, segment.range.max))
                        return true;
                }
                return false;
            }

            function to_domain(range, projection)
            {
                for(var i = 0; i != projection.length; ++i)
                {
                    var segment = projection[i];
                    if(_in_range(segment.range.bounds.min, range, segment.range.bounds.max))
                    {
                        if(segment.scale == "linear")
                        {
                            var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                            return _mix(segment.domain.min, segment.domain.max, amount)
                        }
                        else if(segment.scale[0] == "log")
                        {
                            var amount = (range - segment.range.min) / (segment.range.max - segment.range.min);
                            var base = segment.scale[1];
                            return _sign(segment.domain.min) * Math.pow(base, _mix(_log(segment.domain.min, base), _log(segment.domain.max, base), amount));
                        }
                    }
                }
            }

            function display_coordinates(e)
            {
                var current = svg.createSVGPoint();
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

            var root_id = "t3e21093f15ba49798b904db315211623";
            var axes = {"t58f2fad5b9d048069979774b01c6082c": [{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.5399999999999998, "min": -3.0}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 150.0, "min": 0.0}, "scale": "linear"}]};

            var svg = document.querySelector("#" + root_id + " svg");
            svg.addEventListener("click", display_coordinates);
        })();
        </script></div></div>


### Drawing trees (advanced)
See the sections on [node-labels](node-labels.md) and [tip-labels](tip-labels.md) for detailed instructions on how to modify these features. Here I will focus on how Toytree helps to ensure that users display the proper data on the tree to avoid mistakes. Toytree provides the *magic command* `node_labels=True`, which embeds interactive features into the plot so that you can hover over nodes with your cursor and can see all of the information that is available for that node extracted from the tree.  


```python
## 'False' blocks node labels
canvas, axes = tre0.draw(
    width=150,
    node_labels=False,
    )

## But, you can still change size and color of nodes
canvas, axes = tre0.draw(
    width=150,
    node_labels=False,
    node_size=12,
    node_color='grey'
    )

## 'True' shows nodes with interactive information when you hover
canvas, axes = tre0.draw(
    width=150,
    node_labels=True,
    node_size=12
    )
```


<div align="center" class="toyplot" id="tf7105130a6bb42bfa71d785a1cf94f0c"><svg class="toyplot-canvas-Canvas" height="150.0px" id="t92013023a8e64bdf9f9a783f0f6d6965" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 150.0 150.0" width="150.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="tac27ca1530a84224aa451a8a657881e8"><clipPath id="te49c51dd9a6649eea8083f0643439587"><rect height="140.0" width="140.0" x="5.0" y="5.0"></rect></clipPath><g clip-path="url(#te49c51dd9a6649eea8083f0643439587)"><g class="toyplot-mark-Text" id="tb89d03892f8f4c5997b873a16ff6533a" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,20.45454545454546)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,47.72727272727272)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,75.0)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,102.27272727272728)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,129.54545454545456)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="t35368f5b3c6c4de7a4caa9baeeaf0131"><g class="toyplot-Edges"><path d="M 15.0 64.7727272727 L 15.0 34.0909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 34.0909090909 L 80.306122449 34.0909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 64.7727272727 L 15.0 95.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 95.4545454545 L 47.6530612245 95.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 34.0909090909 L 80.306122449 20.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 20.4545454545 L 112.959183673 20.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 34.0909090909 L 80.306122449 47.7272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 47.7272727273 L 112.959183673 47.7272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 95.4545454545 L 47.6530612245 75.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 75.0 L 112.959183673 75.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 95.4545454545 L 47.6530612245 115.909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 115.909090909 L 80.306122449 115.909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 115.909090909 L 80.306122449 102.272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 102.272727273 L 112.959183673 102.272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 115.909090909 L 80.306122449 129.545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 129.545454545 L 112.959183673 129.545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="64.77272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="20.45454545454546" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="20.45454545454546" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="47.72727272727272" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="47.72727272727272" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="75.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="75.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="102.27272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="102.27272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="129.54545454545456" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="129.54545454545456" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t87fcde2af2184401b93707d3d8971ba3" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="15.0" cy="64.77272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="80.306122448979579" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="47.65306122448979" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="80.306122448979579" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="20.45454545454546" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="47.72727272727272" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="75.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="102.27272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="129.54545454545456" r="0.0"></circle></g></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "t87fcde2af2184401b93707d3d8971ba3", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#tf7105130a6bb42bfa71d785a1cf94f0c .toyplot-mark-popup");
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



<div align="center" class="toyplot" id="t05b8835c0a1e4737936ade6709f1a4ed"><svg class="toyplot-canvas-Canvas" height="150.0px" id="t96af2f2692fb4334bc065656aacd19d0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 150.0 150.0" width="150.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t6966fbba4a264f7d8b167bc4b95c5487"><clipPath id="t8543e3588aca45f49e47ff6887c54e2f"><rect height="140.0" width="140.0" x="5.0" y="5.0"></rect></clipPath><g clip-path="url(#t8543e3588aca45f49e47ff6887c54e2f)"><g class="toyplot-mark-Text" id="t0960b8ad3bc0479894e9c6e6911375be" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,20.45454545454546)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,47.72727272727272)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,75.0)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,102.27272727272728)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,129.54545454545456)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="t40ac522891204ae1aa87e5f749b96efa"><g class="toyplot-Edges"><path d="M 15.0 64.7727272727 L 15.0 34.0909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 34.0909090909 L 80.306122449 34.0909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 64.7727272727 L 15.0 95.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 95.4545454545 L 47.6530612245 95.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 34.0909090909 L 80.306122449 20.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 20.4545454545 L 112.959183673 20.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 34.0909090909 L 80.306122449 47.7272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 47.7272727273 L 112.959183673 47.7272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 95.4545454545 L 47.6530612245 75.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 75.0 L 112.959183673 75.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 95.4545454545 L 47.6530612245 115.909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 115.909090909 L 80.306122449 115.909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 115.909090909 L 80.306122449 102.272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 102.272727273 L 112.959183673 102.272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 115.909090909 L 80.306122449 129.545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 129.545454545 L 112.959183673 129.545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="64.77272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="20.45454545454546" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="20.45454545454546" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="47.72727272727272" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="47.72727272727272" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="75.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="75.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="102.27272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="102.27272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="129.54545454545456" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="129.54545454545456" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t6d0001ac7cc3403a91c38c75e7ded4af" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="15.0" cy="64.77272727272728" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="80.306122448979579" cy="34.090909090909101" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="47.65306122448979" cy="95.454545454545439" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="80.306122448979579" cy="115.90909090909092" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="20.45454545454546" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="47.72727272727272" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="75.0" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="102.27272727272728" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="129.54545454545456" r="6.0"></circle></g></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "t6d0001ac7cc3403a91c38c75e7ded4af", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#t05b8835c0a1e4737936ade6709f1a4ed .toyplot-mark-popup");
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



<div align="center" class="toyplot" id="t647439e0e40d4271b3c3f71523b8ed77"><svg class="toyplot-canvas-Canvas" height="150.0px" id="ta0fa5c8890e048f8bc6c0c3a75a97b93" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 150.0 150.0" width="150.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t61eedc0b3396482fa894c2fc03914213"><clipPath id="t20c47bb561ab4df7a3e64176436bf9ec"><rect height="140.0" width="140.0" x="5.0" y="5.0"></rect></clipPath><g clip-path="url(#t20c47bb561ab4df7a3e64176436bf9ec)"><g class="toyplot-mark-Text" id="tc059efd69b5a44caac1d8145e54f8176" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,20.45454545454546)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,47.72727272727272)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,75.0)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,102.27272727272728)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,129.54545454545456)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="tcfc09b33c7ec4d45b6df168f154f2819"><g class="toyplot-Edges"><path d="M 15.0 64.7727272727 L 15.0 34.0909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 34.0909090909 L 80.306122449 34.0909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 64.7727272727 L 15.0 95.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 95.4545454545 L 47.6530612245 95.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 34.0909090909 L 80.306122449 20.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 20.4545454545 L 112.959183673 20.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 34.0909090909 L 80.306122449 47.7272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 47.7272727273 L 112.959183673 47.7272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 95.4545454545 L 47.6530612245 75.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 75.0 L 112.959183673 75.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 95.4545454545 L 47.6530612245 115.909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 115.909090909 L 80.306122449 115.909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 115.909090909 L 80.306122449 102.272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 102.272727273 L 112.959183673 102.272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 115.909090909 L 80.306122449 129.545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 129.545454545 L 112.959183673 129.545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="64.77272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="20.45454545454546" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="20.45454545454546" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="47.72727272727272" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="47.72727272727272" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="75.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="75.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="102.27272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="102.27272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="129.54545454545456" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="129.54545454545456" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="tc92b1591ca634656b6860adf950a4863" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 0
name: 0
dist: 0
support: 100</title><circle cx="15.0" cy="64.77272727272728" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 1
name: 1
dist: 2
support: 90</title><circle cx="80.306122448979579" cy="34.090909090909101" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 2
name: 2
dist: 1
support: 100</title><circle cx="47.65306122448979" cy="95.454545454545439" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 3
name: 3
dist: 2
support: 100</title><circle cx="80.306122448979579" cy="115.90909090909092" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 4
name: a
dist: 1
support: 100</title><circle cx="112.95918367346937" cy="20.45454545454546" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 5
name: b
dist: 1
support: 100</title><circle cx="112.95918367346937" cy="47.72727272727272" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 6
name: c
dist: 3
support: 100</title><circle cx="112.95918367346937" cy="75.0" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 7
name: d
dist: 1
support: 100</title><circle cx="112.95918367346937" cy="102.27272727272728" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 8
name: e
dist: 1
support: 100</title><circle cx="112.95918367346937" cy="129.54545454545456" r="6.0"></circle></g></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "tc92b1591ca634656b6860adf950a4863", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#t647439e0e40d4271b3c3f71523b8ed77 .toyplot-mark-popup");
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


### Extracting data from the tree

Although you *can* enter values for the node_labels or tip_labels directly into the draw() function as a list, doing so is frowned upon because it can often lead to errors if the values are entered in the incorrect order, or if the tree is re-oriented, ladderized, or pruned. Instead, Toytree aims to encourage users to *always* extract the data directly from the Tree object itself, such that the data will always be in sync with the tree. The interactive feature `node_label=True` is one example of this, where all of the information for each node is shown, and extracted from the tree, so you know for sure that the data are in sync. 

In addition, we provide convenience functions to extract data from a Toytree object in the order that it will be plotted on the tree. For node values the function `get_node_values()` should be used, and for tip labels the function `get_tip_labels()` should be used. Below we show some example usage of `get_node_values()`. See the section on [node-labels](node-labels.md) and [modifying the tree object](modifying-the-tree.md) for more information. 


```python
## get node values returns a list of values, empty by default
tre0.get_node_values()
```




    ['', ' ', ' ', ' ', '', '', '', '', '']




```python
## it takes up to three arguments
tre0.get_node_values(feature='idx', show_root=False, show_tips=False)
```




    ['', 1, 2, 3, '', '', '', '', '']




```python
## it can access any feature in the tree 
tre0.get_node_values(feature='name', show_root=False, show_tips=False)
```




    ['', '1', '2', '3', '', '', '', '', '']




```python
## and either hide or show the root & tip values
tre0.get_node_values(feature='name', show_root=True, show_tips=True)
```




    ['0', '1', '2', '3', 'a', 'b', 'c', 'd', 'e']




```python
## show the index number (idx) of each node
tre0.draw(node_labels=tre0.get_node_values("idx", True, True));
```


<div align="center" class="toyplot" id="t102f06f4f3b54bf88ec2b64fb9091ca4"><svg class="toyplot-canvas-Canvas" height="125.0px" id="td32fcd6c3e80428b833414cd27080b66" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 125.0 125.0" width="125.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="tf0ed826516bd4dc3a6a30de55c7dba03"><clipPath id="tab3f76ef15a1460d8480ce8763facb49"><rect height="120.0" width="120.0" x="2.5" y="2.5"></rect></clipPath><g clip-path="url(#tab3f76ef15a1460d8480ce8763facb49)"><g class="toyplot-mark-Text" id="td16b2b661138464bbafc6ba9c8e257e8" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.967680608365015,17.857142857142861)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.967680608365015,40.178571428571431)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.967680608365015,62.5)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.967680608365015,84.821428571428584)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.967680608365015,107.14285714285714)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="t439e8c12965d4dd5bcc7c5f1688e570f"><g class="toyplot-Edges"><path d="M 15.9220532319 54.1294642857 L 15.9220532319 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.9220532319 29.0178571429 L 66.6191381496 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.9220532319 54.1294642857 L 15.9220532319 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.9220532319 79.2410714286 L 41.2705956907 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 66.6191381496 29.0178571429 L 66.6191381496 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 66.6191381496 17.8571428571 L 91.9676806084 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 66.6191381496 29.0178571429 L 66.6191381496 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 66.6191381496 40.1785714286 L 91.9676806084 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 41.2705956907 79.2410714286 L 41.2705956907 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 41.2705956907 62.5 L 91.9676806084 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 41.2705956907 79.2410714286 L 41.2705956907 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 41.2705956907 95.9821428571 L 66.6191381496 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 66.6191381496 95.9821428571 L 66.6191381496 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 66.6191381496 84.8214285714 L 91.9676806084 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 66.6191381496 95.9821428571 L 66.6191381496 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 66.6191381496 107.142857143 L 91.9676806084 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.922053231939158" cy="54.129464285714292" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.922053231939158" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="66.619138149556406" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.922053231939158" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="41.270595690747783" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="66.619138149556406" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="66.619138149556406" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.967680608365015" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="66.619138149556406" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.967680608365015" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="41.270595690747783" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="41.270595690747783" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.967680608365015" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="41.270595690747783" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="66.619138149556406" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="66.619138149556406" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="66.619138149556406" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.967680608365015" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="66.619138149556406" cy="107.14285714285714" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.967680608365015" cy="107.14285714285714" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="tfb8bb063503f45a7a43652748e4478e1" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="15.922053231939158" cy="54.129464285714292" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="66.619138149556406" cy="29.017857142857153" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="41.270595690747783" cy="79.241071428571431" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="66.619138149556406" cy="95.982142857142861" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.967680608365015" cy="17.857142857142861" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.967680608365015" cy="40.178571428571431" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.967680608365015" cy="62.5" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.967680608365015" cy="84.821428571428584" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.967680608365015" cy="107.14285714285714" r="7.5"></circle></g></g></g><g class="toyplot-mark-Text" id="tb369ed52f6494941b14de31595ff2c5c" style="alignment-baseline:middle;fill:262626;font-size:9px;font-weight:normal;stroke:none;text-anchor:middle"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(15.922053231939158,54.129464285714292)translate(0,2.53125)"><tspan style="font-size:9.0px">0</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(66.619138149556406,29.017857142857153)translate(0,2.53125)"><tspan style="font-size:9.0px">1</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(41.270595690747783,79.241071428571431)translate(0,2.53125)"><tspan style="font-size:9.0px">2</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(66.619138149556406,95.982142857142861)translate(0,2.53125)"><tspan style="font-size:9.0px">3</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(91.967680608365015,17.857142857142861)translate(0,2.53125)"><tspan style="font-size:9.0px">4</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(91.967680608365015,40.178571428571431)translate(0,2.53125)"><tspan style="font-size:9.0px">5</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(91.967680608365015,62.5)translate(0,2.53125)"><tspan style="font-size:9.0px">6</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(91.967680608365015,84.821428571428584)translate(0,2.53125)"><tspan style="font-size:9.0px">7</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(91.967680608365015,107.14285714285714)translate(0,2.53125)"><tspan style="font-size:9.0px">8</tspan></text></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "tfb8bb063503f45a7a43652748e4478e1", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#t102f06f4f3b54bf88ec2b64fb9091ca4 .toyplot-mark-popup");
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



```python
## show names (if no internal names then idx is shown)
tre0.draw(node_labels=tre0.get_node_values("name", True, True));
```


<div align="center" class="toyplot" id="t3f86361db8db4a718e3b00aeb5051b62"><svg class="toyplot-canvas-Canvas" height="125.0px" id="tef1d600e0e684cfca6426bc3a61bf2ad" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 125.0 125.0" width="125.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t429c723dc6794404961d079fa8c399d1"><clipPath id="t72ec702ba5234b52bfa9d3a69ee2e127"><rect height="120.0" width="120.0" x="2.5" y="2.5"></rect></clipPath><g clip-path="url(#t72ec702ba5234b52bfa9d3a69ee2e127)"><g class="toyplot-mark-Text" id="td5bd12d677bc4e6bbd1dd676b60e3c8d" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.967680608365015,17.857142857142861)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.967680608365015,40.178571428571431)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.967680608365015,62.5)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.967680608365015,84.821428571428584)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.967680608365015,107.14285714285714)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="t2701fe5383a34869b8c3d48bbcb93715"><g class="toyplot-Edges"><path d="M 15.9220532319 54.1294642857 L 15.9220532319 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.9220532319 29.0178571429 L 66.6191381496 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.9220532319 54.1294642857 L 15.9220532319 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.9220532319 79.2410714286 L 41.2705956907 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 66.6191381496 29.0178571429 L 66.6191381496 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 66.6191381496 17.8571428571 L 91.9676806084 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 66.6191381496 29.0178571429 L 66.6191381496 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 66.6191381496 40.1785714286 L 91.9676806084 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 41.2705956907 79.2410714286 L 41.2705956907 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 41.2705956907 62.5 L 91.9676806084 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 41.2705956907 79.2410714286 L 41.2705956907 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 41.2705956907 95.9821428571 L 66.6191381496 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 66.6191381496 95.9821428571 L 66.6191381496 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 66.6191381496 84.8214285714 L 91.9676806084 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 66.6191381496 95.9821428571 L 66.6191381496 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 66.6191381496 107.142857143 L 91.9676806084 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.922053231939158" cy="54.129464285714292" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.922053231939158" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="66.619138149556406" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.922053231939158" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="41.270595690747783" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="66.619138149556406" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="66.619138149556406" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.967680608365015" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="66.619138149556406" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.967680608365015" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="41.270595690747783" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="41.270595690747783" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.967680608365015" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="41.270595690747783" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="66.619138149556406" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="66.619138149556406" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="66.619138149556406" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.967680608365015" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="66.619138149556406" cy="107.14285714285714" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.967680608365015" cy="107.14285714285714" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="taa7a6a9436e2414aa0f58c4ecbc509e1" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="15.922053231939158" cy="54.129464285714292" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="66.619138149556406" cy="29.017857142857153" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="41.270595690747783" cy="79.241071428571431" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="66.619138149556406" cy="95.982142857142861" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.967680608365015" cy="17.857142857142861" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.967680608365015" cy="40.178571428571431" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.967680608365015" cy="62.5" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.967680608365015" cy="84.821428571428584" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.967680608365015" cy="107.14285714285714" r="7.5"></circle></g></g></g><g class="toyplot-mark-Text" id="t66dafbdcbf1648a3bc98e0c37eafbcbf" style="alignment-baseline:middle;fill:262626;font-size:9px;font-weight:normal;stroke:none;text-anchor:middle"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(15.922053231939158,54.129464285714292)translate(0,2.53125)"><tspan style="font-size:9.0px">0</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(66.619138149556406,29.017857142857153)translate(0,2.53125)"><tspan style="font-size:9.0px">1</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(41.270595690747783,79.241071428571431)translate(0,2.53125)"><tspan style="font-size:9.0px">2</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(66.619138149556406,95.982142857142861)translate(0,2.53125)"><tspan style="font-size:9.0px">3</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(91.967680608365015,17.857142857142861)translate(0,2.53125)"><tspan style="font-size:9.0px">a</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(91.967680608365015,40.178571428571431)translate(0,2.53125)"><tspan style="font-size:9.0px">b</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(91.967680608365015,62.5)translate(0,2.53125)"><tspan style="font-size:9.0px">c</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(91.967680608365015,84.821428571428584)translate(0,2.53125)"><tspan style="font-size:9.0px">d</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(91.967680608365015,107.14285714285714)translate(0,2.53125)"><tspan style="font-size:9.0px">e</tspan></text></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "taa7a6a9436e2414aa0f58c4ecbc509e1", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#t3f86361db8db4a718e3b00aeb5051b62 .toyplot-mark-popup");
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



```python
## show support values (hides root & tip values by default)
tre0.draw(node_labels=tre0.get_node_values("support"));
```


<div align="center" class="toyplot" id="te281681e2e9f411bb30daa2e46cbe875"><svg class="toyplot-canvas-Canvas" height="125.0px" id="ta93bf66ca1d64ad1ad00154fcae1abe0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 125.0 125.0" width="125.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="tc588eca99c2d40d6922ac0a100ff4f0c"><clipPath id="tb208d06e7c38410397a06c3fa960b5e8"><rect height="120.0" width="120.0" x="2.5" y="2.5"></rect></clipPath><g clip-path="url(#tb208d06e7c38410397a06c3fa960b5e8)"><g class="toyplot-mark-Text" id="t2078d203b74f4b20a30fb70a4febc5ac" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,17.857142857142861)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,40.178571428571431)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,62.5)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,84.821428571428584)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,107.14285714285714)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="t08c14f2117604c64a8f7f1a21d0b250d"><g class="toyplot-Edges"><path d="M 12.5 54.1294642857 L 12.5 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 29.0178571429 L 64.9934383202 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 54.1294642857 L 12.5 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 79.2410714286 L 38.7467191601 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 29.0178571429 L 64.9934383202 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 17.8571428571 L 91.2401574803 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 29.0178571429 L 64.9934383202 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 40.1785714286 L 91.2401574803 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 79.2410714286 L 38.7467191601 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 62.5 L 91.2401574803 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 79.2410714286 L 38.7467191601 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 95.9821428571 L 64.9934383202 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 95.9821428571 L 64.9934383202 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 84.8214285714 L 91.2401574803 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 95.9821428571 L 64.9934383202 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 107.142857143 L 91.2401574803 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="54.129464285714292" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="107.14285714285714" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="107.14285714285714" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t0e0a5801a5ac495b99229df6a750332b" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="12.5" cy="54.129464285714292" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="64.993438320209975" cy="29.017857142857153" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="38.746719160104988" cy="79.241071428571431" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="64.993438320209975" cy="95.982142857142861" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="107.14285714285714" r="0.0"></circle></g></g></g><g class="toyplot-mark-Text" id="tddeadd6a9f214d1a8813e3ac24f0247f" style="alignment-baseline:middle;fill:262626;font-size:9px;font-weight:normal;stroke:none;text-anchor:middle"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(64.993438320209975,29.017857142857153)translate(0,2.53125)"><tspan style="font-size:9.0px">90</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(38.746719160104988,79.241071428571431)translate(0,2.53125)"><tspan style="font-size:9.0px">100</tspan></text><text class="toyplot-Datum" style="fill:262626;font-weight:normal;opacity:1.0;stroke:none;text-anchor:middle" transform="translate(64.993438320209975,95.982142857142861)translate(0,2.53125)"><tspan style="font-size:9.0px">100</tspan></text></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "t0e0a5801a5ac495b99229df6a750332b", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#te281681e2e9f411bb30daa2e46cbe875 .toyplot-mark-popup");
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



```python
## parse the info and plot as node colors
colors = [tre0.colors[0] if i==100 else tre0.colors[1] \
          for i in tre0.get_node_values("support", True, True)]

## plot node colors and hide stroke color
tre0.draw(
    width=200,
    node_labels=False, 
    node_color=colors,
    node_size=15,
);
```


<div align="center" class="toyplot" id="tc56a4cd74c104bf4bb553315e740af85"><svg class="toyplot-canvas-Canvas" height="200.0px" id="t123a2577c03743eeb768b63fd410ac6d" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 200.0 200.0" width="200.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t4c7923224e394b968be29c9d4a0ad06f"><clipPath id="t2844e1c872ef423e9db99107f390d965"><rect height="180.0" width="180.0" x="10.0" y="10.0"></rect></clipPath><g clip-path="url(#t2844e1c872ef423e9db99107f390d965)"><g class="toyplot-mark-Text" id="tcbca0735f7ee4703a1ea0c8c59556739" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(156.89839572192514,25.581395348837219)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(156.89839572192514,62.790697674418624)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(156.89839572192514,100.00000000000001)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(156.89839572192514,137.2093023255814)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(156.89839572192514,174.41860465116281)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="tb437f664fa854c9092a4a402b102b674"><g class="toyplot-Edges"><path d="M 20.0 86.0465116279 L 20.0 44.1860465116" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 20.0 44.1860465116 L 111.265597148 44.1860465116" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 20.0 86.0465116279 L 20.0 127.906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 20.0 127.906976744 L 65.632798574 127.906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 111.265597148 44.1860465116 L 111.265597148 25.5813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 111.265597148 25.5813953488 L 156.898395722 25.5813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 111.265597148 44.1860465116 L 111.265597148 62.7906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 111.265597148 62.7906976744 L 156.898395722 62.7906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 65.632798574 127.906976744 L 65.632798574 100.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 65.632798574 100.0 L 156.898395722 100.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 65.632798574 127.906976744 L 65.632798574 155.813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 65.632798574 155.813953488 L 111.265597148 155.813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 111.265597148 155.813953488 L 111.265597148 137.209302326" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 111.265597148 137.209302326 L 156.898395722 137.209302326" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 111.265597148 155.813953488 L 111.265597148 174.418604651" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 111.265597148 174.418604651 L 156.898395722 174.418604651" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="20.0" cy="86.046511627906995" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="20.0" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="111.26559714795009" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="20.0" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="65.632798573975037" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="111.26559714795009" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="111.26559714795009" cy="25.581395348837219" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="156.89839572192514" cy="25.581395348837219" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="111.26559714795009" cy="62.790697674418624" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="156.89839572192514" cy="62.790697674418624" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="65.632798573975037" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="65.632798573975037" cy="100.00000000000001" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="156.89839572192514" cy="100.00000000000001" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="65.632798573975037" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="111.26559714795009" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="111.26559714795009" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="111.26559714795009" cy="137.2093023255814" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="156.89839572192514" cy="137.2093023255814" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="111.26559714795009" cy="174.41860465116281" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="156.89839572192514" cy="174.41860465116281" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t4cb85a4b3e4e45a1b15e39645d748a83" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="20.0" cy="86.046511627906995" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="111.26559714795009" cy="44.186046511627936" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="65.632798573975037" cy="127.90697674418605" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="111.26559714795009" cy="155.81395348837208" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="156.89839572192514" cy="25.581395348837219" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="156.89839572192514" cy="62.790697674418624" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="156.89839572192514" cy="100.00000000000001" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="156.89839572192514" cy="137.2093023255814" r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="156.89839572192514" cy="174.41860465116281" r="7.5"></circle></g></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "t4cb85a4b3e4e45a1b15e39645d748a83", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#tc56a4cd74c104bf4bb553315e740af85 .toyplot-mark-popup");
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

