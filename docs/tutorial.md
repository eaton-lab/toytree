
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
Below are two simple trees in newick format and a third in extended newick format (NHX). The first has edge lengths and support values, the second has edge-lengths and node-labels. These are two different ways of writing tree data in a serialized format. To parse either format you must tell toytree the format of the data following the [tree parsing formats in ete](http://etetoolkit.org/docs/latest/tutorial/tutorial_trees.html#reading-and-writing-newick-trees). The most commonly used format, and the default, is `format=0`. 


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


<div align="center" class="toyplot" id="t3a2343126a60486ebf1d58085c153892"><svg class="toyplot-canvas-Canvas" height="125.0px" id="ta9f97a39639d4c4f89a8e34747a4d1c3" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 125.0 125.0" width="125.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t113f464a108d4a4dbe0c3205a001d029"><clipPath id="t86faf4b6eff545f397336d4c1d514bba"><rect height="120.0" width="120.0" x="2.5" y="2.5"></rect></clipPath><g clip-path="url(#t86faf4b6eff545f397336d4c1d514bba)"><g class="toyplot-mark-Text" id="t553430e129bf4793ab86b8822f83cff4" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,17.857142857142861)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,40.178571428571431)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,62.5)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,84.821428571428584)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,107.14285714285714)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="taa719cd01bab459a956cde323d502b94"><g class="toyplot-Edges"><path d="M 12.5 54.1294642857 L 12.5 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 29.0178571429 L 64.9934383202 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 54.1294642857 L 12.5 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 79.2410714286 L 38.7467191601 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 29.0178571429 L 64.9934383202 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 17.8571428571 L 91.2401574803 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 29.0178571429 L 64.9934383202 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 40.1785714286 L 91.2401574803 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 79.2410714286 L 38.7467191601 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 62.5 L 91.2401574803 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 79.2410714286 L 38.7467191601 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 95.9821428571 L 64.9934383202 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 95.9821428571 L 64.9934383202 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 84.8214285714 L 91.2401574803 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 95.9821428571 L 64.9934383202 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 107.142857143 L 91.2401574803 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="54.129464285714292" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="107.14285714285714" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="107.14285714285714" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t7eacf8f132974b05a530a3589c41e793" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="12.5" cy="54.129464285714292" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="107.14285714285714" r="0.0"></circle></g></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "t7eacf8f132974b05a530a3589c41e793", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#t3a2343126a60486ebf1d58085c153892 .toyplot-mark-popup");
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


<div align="center" class="toyplot" id="t421f7f3586ed40788920d3f43d84cd9e"><svg class="toyplot-canvas-Canvas" height="125.0px" id="te2043f894fb64b9bb0267dc1236b1191" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 125.0 125.0" width="125.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t9e3483fb16b14b329e08264a9fbb74cf"><clipPath id="t4d3041512d394df6a8280caa8ccc0ff0"><rect height="120.0" width="120.0" x="2.5" y="2.5"></rect></clipPath><g clip-path="url(#t4d3041512d394df6a8280caa8ccc0ff0)"><g class="toyplot-mark-Text" id="t99750ce614ac420cb802abb0d67677f0" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,17.857142857142861)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,40.178571428571431)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,62.5)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,84.821428571428584)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,107.14285714285714)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="t890179afa0804fe29e563434f8abe4db"><g class="toyplot-Edges"><path d="M 12.5 54.1294642857 L 12.5 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 29.0178571429 L 64.9934383202 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 54.1294642857 L 12.5 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 79.2410714286 L 38.7467191601 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 29.0178571429 L 64.9934383202 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 17.8571428571 L 91.2401574803 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 29.0178571429 L 64.9934383202 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 40.1785714286 L 91.2401574803 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 79.2410714286 L 38.7467191601 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 62.5 L 91.2401574803 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 79.2410714286 L 38.7467191601 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 95.9821428571 L 64.9934383202 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 95.9821428571 L 64.9934383202 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 84.8214285714 L 91.2401574803 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 95.9821428571 L 64.9934383202 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 107.142857143 L 91.2401574803 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="54.129464285714292" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="107.14285714285714" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="107.14285714285714" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t67840631b5584c3b893f22d16c1e77f6" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="12.5" cy="54.129464285714292" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="107.14285714285714" r="0.0"></circle></g></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "t67840631b5584c3b893f22d16c1e77f6", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#t421f7f3586ed40788920d3f43d84cd9e .toyplot-mark-popup");
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



<div align="center" class="toyplot" id="tbc54de10e31e461a8c8e7d8df1491f59"><svg class="toyplot-canvas-Canvas" height="125.0px" id="t29e278bb5cec4481b04db5e71564954e" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 125.0 125.0" width="125.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t02f0b135f8e643e7b05727f200aad440"><clipPath id="td1633509f2f84f17827d7e30eb077f03"><rect height="120.0" width="120.0" x="2.5" y="2.5"></rect></clipPath><g clip-path="url(#td1633509f2f84f17827d7e30eb077f03)"><g class="toyplot-mark-Text" id="t83a8c1cbaa4f412ab4dfe9aeb387b695" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,17.857142857142861)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,40.178571428571431)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,62.5)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,84.821428571428584)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(91.240157480314963,107.14285714285714)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="t15e1dd6fdb684e6caeb16471676cf51b"><g class="toyplot-Edges"><path d="M 12.5 54.1294642857 L 12.5 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 29.0178571429 L 64.9934383202 29.0178571429" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 54.1294642857 L 12.5 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 12.5 79.2410714286 L 38.7467191601 79.2410714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 29.0178571429 L 64.9934383202 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 17.8571428571 L 91.2401574803 17.8571428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 29.0178571429 L 64.9934383202 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 40.1785714286 L 91.2401574803 40.1785714286" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 79.2410714286 L 38.7467191601 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 62.5 L 91.2401574803 62.5" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 79.2410714286 L 38.7467191601 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 38.7467191601 95.9821428571 L 64.9934383202 95.9821428571" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 95.9821428571 L 64.9934383202 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 84.8214285714 L 91.2401574803 84.8214285714" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 95.9821428571 L 64.9934383202 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.9934383202 107.142857143 L 91.2401574803 107.142857143" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="54.129464285714292" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="12.5" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="38.746719160104988" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="64.993438320209975" cy="107.14285714285714" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="91.240157480314963" cy="107.14285714285714" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="tf4c5e969186841109613f6ca1603c9a3" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="12.5" cy="54.129464285714292" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="64.993438320209975" cy="29.017857142857153" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="38.746719160104988" cy="79.241071428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="64.993438320209975" cy="95.982142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="17.857142857142861" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="40.178571428571431" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="62.5" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="84.821428571428584" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="91.240157480314963" cy="107.14285714285714" r="0.0"></circle></g></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "tf4c5e969186841109613f6ca1603c9a3", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#tbc54de10e31e461a8c8e7d8df1491f59 .toyplot-mark-popup");
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


<div align="center" class="toyplot" id="t94e7d06966a64634861ea471a5dbc9b5"><svg class="toyplot-canvas-Canvas" height="200.0px" id="t7801a4c49fa9440bbdd2a5b7dea22e53" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 400.0 200.0" width="400.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t1cbac8c017664ce5baeaef2b92bc5dd4"><clipPath id="t44708261e4494d589f4434bc4330ce35"><rect height="180.0" width="140.0" x="30.0" y="10.0"></rect></clipPath><g clip-path="url(#t44708261e4494d589f4434bc4330ce35)"><g class="toyplot-mark-Text" id="t2664b8f31e19488c86abe431480d7d4e" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(137.95918367346937,25.581395348837219)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(137.95918367346937,62.790697674418624)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(137.95918367346937,100.00000000000001)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(137.95918367346937,137.2093023255814)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(137.95918367346937,174.41860465116281)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="tfaf1ea2a31864148b456a47457e45ff6"><g class="toyplot-Edges"><path d="M 40.0 86.0465116279 L 40.0 44.1860465116" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 40.0 44.1860465116 L 105.306122449 44.1860465116" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 40.0 86.0465116279 L 40.0 127.906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 40.0 127.906976744 L 72.6530612245 127.906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 105.306122449 44.1860465116 L 105.306122449 25.5813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 105.306122449 25.5813953488 L 137.959183673 25.5813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 105.306122449 44.1860465116 L 105.306122449 62.7906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 105.306122449 62.7906976744 L 137.959183673 62.7906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 72.6530612245 127.906976744 L 72.6530612245 100.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 72.6530612245 100.0 L 137.959183673 100.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 72.6530612245 127.906976744 L 72.6530612245 155.813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 72.6530612245 155.813953488 L 105.306122449 155.813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 105.306122449 155.813953488 L 105.306122449 137.209302326" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 105.306122449 137.209302326 L 137.959183673 137.209302326" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 105.306122449 155.813953488 L 105.306122449 174.418604651" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 105.306122449 174.418604651 L 137.959183673 174.418604651" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="40.0" cy="86.046511627906995" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="40.0" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="105.30612244897958" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="40.0" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="72.65306122448979" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="105.30612244897958" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="105.30612244897958" cy="25.581395348837219" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="137.95918367346937" cy="25.581395348837219" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="105.30612244897958" cy="62.790697674418624" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="137.95918367346937" cy="62.790697674418624" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="72.65306122448979" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="72.65306122448979" cy="100.00000000000001" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="137.95918367346937" cy="100.00000000000001" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="72.65306122448979" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="105.30612244897958" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="105.30612244897958" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="105.30612244897958" cy="137.2093023255814" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="137.95918367346937" cy="137.2093023255814" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="105.30612244897958" cy="174.41860465116281" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="137.95918367346937" cy="174.41860465116281" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="tff8c3e5fcd514b448f4bd49f2c0565b7" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="40.0" cy="86.046511627906995" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="105.30612244897958" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="72.65306122448979" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="105.30612244897958" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="137.95918367346937" cy="25.581395348837219" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="137.95918367346937" cy="62.790697674418624" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="137.95918367346937" cy="100.00000000000001" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="137.95918367346937" cy="137.2093023255814" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="137.95918367346937" cy="174.41860465116281" r="0.0"></circle></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="te5f7555b930741e4ae6f1265904d122c"><clipPath id="t875f52e48daa45c68a7ed9116352613a"><rect height="180.0" width="140.0" x="230.0" y="10.0"></rect></clipPath><g clip-path="url(#t875f52e48daa45c68a7ed9116352613a)"><g class="toyplot-mark-Text" id="t447bb27b2c464bf7849b55f92fd8d8c9" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(337.9591836734694,25.581395348837219)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(337.9591836734694,62.790697674418624)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(337.9591836734694,100.00000000000001)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(337.9591836734694,137.2093023255814)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(337.9591836734694,174.41860465116281)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="t81b578d0ffc444f98ce5ef4b65458e50"><g class="toyplot-Edges"><path d="M 240.0 86.0465116279 L 240.0 44.1860465116" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 240.0 44.1860465116 L 305.306122449 44.1860465116" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 240.0 86.0465116279 L 240.0 127.906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 240.0 127.906976744 L 272.653061224 127.906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 305.306122449 44.1860465116 L 305.306122449 25.5813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 305.306122449 25.5813953488 L 337.959183673 25.5813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 305.306122449 44.1860465116 L 305.306122449 62.7906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 305.306122449 62.7906976744 L 337.959183673 62.7906976744" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 272.653061224 127.906976744 L 272.653061224 100.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 272.653061224 100.0 L 337.959183673 100.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 272.653061224 127.906976744 L 272.653061224 155.813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 272.653061224 155.813953488 L 305.306122449 155.813953488" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 305.306122449 155.813953488 L 305.306122449 137.209302326" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 305.306122449 137.209302326 L 337.959183673 137.209302326" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 305.306122449 155.813953488 L 305.306122449 174.418604651" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 305.306122449 174.418604651 L 337.959183673 174.418604651" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="240.0" cy="86.046511627906995" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="240.0" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="305.30612244897958" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="240.0" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="272.65306122448982" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="305.30612244897958" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="305.30612244897958" cy="25.581395348837219" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="337.9591836734694" cy="25.581395348837219" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="305.30612244897958" cy="62.790697674418624" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="337.9591836734694" cy="62.790697674418624" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="272.65306122448982" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="272.65306122448982" cy="100.00000000000001" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="337.9591836734694" cy="100.00000000000001" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="272.65306122448982" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="305.30612244897958" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="305.30612244897958" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="305.30612244897958" cy="137.2093023255814" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="337.9591836734694" cy="137.2093023255814" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="305.30612244897958" cy="174.41860465116281" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="337.9591836734694" cy="174.41860465116281" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t4b2de882b14045fe8c1ecb45e1b9f92c" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="240.0" cy="86.046511627906995" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="305.30612244897958" cy="44.186046511627936" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="272.65306122448982" cy="127.90697674418605" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="305.30612244897958" cy="155.81395348837208" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="337.9591836734694" cy="25.581395348837219" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="337.9591836734694" cy="62.790697674418624" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="337.9591836734694" cy="100.00000000000001" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="337.9591836734694" cy="137.2093023255814" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="337.9591836734694" cy="174.41860465116281" r="0.0"></circle></g></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "tff8c3e5fcd514b448f4bd49f2c0565b7", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}, {"title": "Scatterplot Data", "names": ["x", "y0"], "id": "t4b2de882b14045fe8c1ecb45e1b9f92c", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#t94e7d06966a64634861ea471a5dbc9b5 .toyplot-mark-popup");
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


Or, instead of catching the canvas and axes auto-generated by the `toytree.draw()` function you can instead generate the canvas and axes yourself using Toyplot and embed the tree plot in the canvas. 


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


<div align="center" class="toyplot" id="t7440ca8fc3cc442889f8c1ab97df43c1"><svg class="toyplot-canvas-Canvas" height="250.0px" id="td6f8a3d07dcd4c3790f414ef9a87a366" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 250.0 250.0" width="250.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t5345799381af4f9180559b3807164edd"><clipPath id="tb5670b2f725d453493f70bec0f53aa48"><rect height="170.0" width="170.0" x="40.0" y="40.0"></rect></clipPath><g clip-path="url(#tb5670b2f725d453493f70bec0f53aa48)"><g class="toyplot-mark-Text" id="t9b382e8d2b154154834e50a698adec62" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(177.11864406779659,55.555555555555564)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(177.11864406779659,90.277777777777771)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(177.11864406779659,125.0)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(177.11864406779659,159.72222222222223)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(177.11864406779659,194.44444444444446)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="t5426f93c9d8546939b1c4dc8f4bfbcca"><g class="toyplot-Edges"><path d="M 50.0 111.979166667 L 50.0 72.9166666667" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 72.9166666667 L 134.745762712 72.9166666667" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 111.979166667 L 50.0 151.041666667" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 151.041666667 L 92.3728813559 151.041666667" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 134.745762712 72.9166666667 L 134.745762712 55.5555555556" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 134.745762712 55.5555555556 L 177.118644068 55.5555555556" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 134.745762712 72.9166666667 L 134.745762712 90.2777777778" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 134.745762712 90.2777777778 L 177.118644068 90.2777777778" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 92.3728813559 151.041666667 L 92.3728813559 125.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 92.3728813559 125.0 L 177.118644068 125.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 92.3728813559 151.041666667 L 92.3728813559 177.083333333" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 92.3728813559 177.083333333 L 134.745762712 177.083333333" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 134.745762712 177.083333333 L 134.745762712 159.722222222" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 134.745762712 159.722222222 L 177.118644068 159.722222222" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 134.745762712 177.083333333 L 134.745762712 194.444444444" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 134.745762712 194.444444444 L 177.118644068 194.444444444" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="50.0" cy="111.97916666666666" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="50.0" cy="72.916666666666657" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="134.74576271186442" cy="72.916666666666657" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="50.0" cy="151.04166666666669" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="92.372881355932208" cy="151.04166666666669" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="134.74576271186442" cy="72.916666666666657" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="134.74576271186442" cy="55.555555555555564" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="177.11864406779659" cy="55.555555555555564" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="134.74576271186442" cy="90.277777777777771" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="177.11864406779659" cy="90.277777777777771" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="92.372881355932208" cy="151.04166666666669" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="92.372881355932208" cy="125.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="177.11864406779659" cy="125.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="92.372881355932208" cy="177.08333333333331" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="134.74576271186442" cy="177.08333333333331" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="134.74576271186442" cy="177.08333333333331" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="134.74576271186442" cy="159.72222222222223" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="177.11864406779659" cy="159.72222222222223" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="134.74576271186442" cy="194.44444444444446" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="177.11864406779659" cy="194.44444444444446" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="tde587765b48140389eb56a9ca4a79d53" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="50.0" cy="111.97916666666666" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="134.74576271186442" cy="72.916666666666657" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="92.372881355932208" cy="151.04166666666669" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="134.74576271186442" cy="177.08333333333331" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="177.11864406779659" cy="55.555555555555564" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="177.11864406779659" cy="90.277777777777771" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="177.11864406779659" cy="125.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="177.11864406779659" cy="159.72222222222223" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="177.11864406779659" cy="194.44444444444446" r="0.0"></circle></g></g></g></g><g class="toyplot-coordinates-Axis" id="tb8d0a5ad43f346288b4df9559adb1d89" transform="translate(50.0,200.0)translate(0,10.0)"><line style="" x1="0" x2="127.11864406779661" y1="0" y2="0"></line><g><line style="" x1="0.0" x2="0.0" y1="0" y2="-5"></line><line style="" x1="42.37288135593221" x2="42.37288135593221" y1="0" y2="-5"></line><line style="" x1="84.74576271186442" x2="84.74576271186442" y1="0" y2="-5"></line><line style="" x1="127.11864406779661" x2="127.11864406779661" y1="0" y2="-5"></line></g><g><text style="font-weight:normal;stroke:none;text-anchor:middle" transform="translate(0.0,6)translate(0,7.5)"><tspan style="font-size:10.0px">-3</tspan></text><text style="font-weight:normal;stroke:none;text-anchor:middle" transform="translate(42.37288135593221,6)translate(0,7.5)"><tspan style="font-size:10.0px">-2</tspan></text><text style="font-weight:normal;stroke:none;text-anchor:middle" transform="translate(84.74576271186442,6)translate(0,7.5)"><tspan style="font-size:10.0px">-1</tspan></text><text style="font-weight:normal;stroke:none;text-anchor:middle" transform="translate(127.11864406779661,6)translate(0,7.5)"><tspan style="font-size:10.0px">0</tspan></text></g><text style="font-weight:bold;stroke:none;text-anchor:middle" transform="translate(75.0,22)translate(0,9.0)"><tspan style="font-size:12.0px">Divergence time (Ma)</tspan></text><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0" x1="0" x2="0" y1="-3.0" y2="4.5"></line><text style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle" x="0" y="-6"></text></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "tde587765b48140389eb56a9ca4a79d53", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#t7440ca8fc3cc442889f8c1ab97df43c1 .toyplot-mark-popup");
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

            var root_id = "t7440ca8fc3cc442889f8c1ab97df43c1";
            var axes = {"tb8d0a5ad43f346288b4df9559adb1d89": [{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.5399999999999998, "min": -3.0}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 150.0, "min": 0.0}, "scale": "linear"}]};

            var svg = document.querySelector("#" + root_id + " svg");
            svg.addEventListener("click", display_coordinates);
        })();
        </script></div></div>


### Drawing trees (advanced)
See the sections on [node-labels](node-labels.md) and [tip-labels](tip-labels.md) for detailed instructions on how to modify these features. Here I will concentrate on how Toytree works to ensure that users display the proper data on the tree and avoid mistakes. First off, we provide the *magic command* `node_labels=True` which embeds interactive features into the plot so that if you hover over any node with your cursor you can see all of the information available for that node that is extracted from the tree.  


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


<div align="center" class="toyplot" id="t863bf7f304b94e1ea1522826dfa3031e"><svg class="toyplot-canvas-Canvas" height="150.0px" id="t0869c2d3412a4b9cad5c1056ce18b546" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 150.0 150.0" width="150.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t35b2e9d5ef4643f4b1837897bb80305f"><clipPath id="t3bf9808b11734d67b5d60b10e218b108"><rect height="140.0" width="140.0" x="5.0" y="5.0"></rect></clipPath><g clip-path="url(#t3bf9808b11734d67b5d60b10e218b108)"><g class="toyplot-mark-Text" id="ta7a8d8f054b047628f81e4f6251c66b5" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,20.45454545454546)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,47.72727272727272)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,75.0)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,102.27272727272728)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,129.54545454545456)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="td79b1d4f8f0147408caac96abc8906e4"><g class="toyplot-Edges"><path d="M 15.0 64.7727272727 L 15.0 34.0909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 34.0909090909 L 80.306122449 34.0909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 64.7727272727 L 15.0 95.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 95.4545454545 L 47.6530612245 95.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 34.0909090909 L 80.306122449 20.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 20.4545454545 L 112.959183673 20.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 34.0909090909 L 80.306122449 47.7272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 47.7272727273 L 112.959183673 47.7272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 95.4545454545 L 47.6530612245 75.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 75.0 L 112.959183673 75.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 95.4545454545 L 47.6530612245 115.909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 115.909090909 L 80.306122449 115.909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 115.909090909 L 80.306122449 102.272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 102.272727273 L 112.959183673 102.272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 115.909090909 L 80.306122449 129.545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 129.545454545 L 112.959183673 129.545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="64.77272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="20.45454545454546" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="20.45454545454546" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="47.72727272727272" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="47.72727272727272" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="75.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="75.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="102.27272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="102.27272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="129.54545454545456" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="129.54545454545456" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t85dd915f630744ff9f13ab93cee7394e" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="15.0" cy="64.77272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="80.306122448979579" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="47.65306122448979" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="80.306122448979579" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="20.45454545454546" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="47.72727272727272" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="75.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="102.27272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="129.54545454545456" r="0.0"></circle></g></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "t85dd915f630744ff9f13ab93cee7394e", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#t863bf7f304b94e1ea1522826dfa3031e .toyplot-mark-popup");
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



<div align="center" class="toyplot" id="t232eda762d1f4f93bb48517c667c3005"><svg class="toyplot-canvas-Canvas" height="150.0px" id="t06847af895ec4795b7f41e7e62fa0c68" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 150.0 150.0" width="150.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t8adb2c9363a547898500a84cfb984397"><clipPath id="te6b5621fbbad40a8b61403a9b5a4398c"><rect height="140.0" width="140.0" x="5.0" y="5.0"></rect></clipPath><g clip-path="url(#te6b5621fbbad40a8b61403a9b5a4398c)"><g class="toyplot-mark-Text" id="tf5c0f99b87384f118a92d715127661d8" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,20.45454545454546)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,47.72727272727272)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,75.0)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,102.27272727272728)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,129.54545454545456)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="t9707bc7d7cc1496ca622b3219175e949"><g class="toyplot-Edges"><path d="M 15.0 64.7727272727 L 15.0 34.0909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 34.0909090909 L 80.306122449 34.0909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 64.7727272727 L 15.0 95.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 95.4545454545 L 47.6530612245 95.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 34.0909090909 L 80.306122449 20.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 20.4545454545 L 112.959183673 20.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 34.0909090909 L 80.306122449 47.7272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 47.7272727273 L 112.959183673 47.7272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 95.4545454545 L 47.6530612245 75.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 75.0 L 112.959183673 75.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 95.4545454545 L 47.6530612245 115.909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 115.909090909 L 80.306122449 115.909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 115.909090909 L 80.306122449 102.272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 102.272727273 L 112.959183673 102.272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 115.909090909 L 80.306122449 129.545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 129.545454545 L 112.959183673 129.545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="64.77272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="20.45454545454546" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="20.45454545454546" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="47.72727272727272" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="47.72727272727272" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="75.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="75.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="102.27272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="102.27272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="129.54545454545456" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="129.54545454545456" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="ta34d1d0fe6f146159ffe00dce77b32ac" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="15.0" cy="64.77272727272728" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="80.306122448979579" cy="34.090909090909101" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="47.65306122448979" cy="95.454545454545439" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="80.306122448979579" cy="115.90909090909092" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="20.45454545454546" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="47.72727272727272" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="75.0" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="102.27272727272728" r="6.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(50.2%,50.2%,50.2%);fill-opacity:1.0;opacity:1.0;stroke:none"><circle cx="112.95918367346937" cy="129.54545454545456" r="6.0"></circle></g></g></g></g></g></svg><div class="toyplot-interactive"><ul class="toyplot-mark-popup" onmouseleave="this.style.visibility='hidden'" style="background:rgba(0%,0%,0%,0.75);border:0;border-radius:6px;color:white;cursor:default;list-style:none;margin:0;padding:5px;position:fixed;visibility:hidden">
            <li class="toyplot-mark-popup-title" style="color:lightgray;cursor:default;padding:5px;list-style:none;margin:0"></li>
            <li class="toyplot-mark-popup-save-csv" onmouseout="this.style.color='white';this.style.background='steelblue'" onmouseover="this.style.color='steelblue';this.style.background='white'" style="border-radius:3px;padding:5px;list-style:none;margin:0">
                Save as .csv
            </li>
        </ul><script>
        (function()
        {
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "ta34d1d0fe6f146159ffe00dce77b32ac", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#t232eda762d1f4f93bb48517c667c3005 .toyplot-mark-popup");
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



<div align="center" class="toyplot" id="tda07a38d0e0c4fce97b3db8aca17d340"><svg class="toyplot-canvas-Canvas" height="150.0px" id="t8d4a96b8e264479a834d8439ecfc7352" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 150.0 150.0" width="150.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t928ed44c4ade427bb0c1a8c1be57a7c7"><clipPath id="tcc8bcb36fe1c49509e91df788b26a8f0"><rect height="140.0" width="140.0" x="5.0" y="5.0"></rect></clipPath><g clip-path="url(#tcc8bcb36fe1c49509e91df788b26a8f0)"><g class="toyplot-mark-Text" id="t0c16d42dd6f348b6811c778ab40037f4" style="-toyplot-anchor-shift:15px;alignment-baseline:middle;font-size:12px;font-weight:normal;stroke:none;text-anchor:start"><g class="toyplot-Series"><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,20.45454545454546)translate(15.0,3.375)"><tspan style="font-size:12.0px">a</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,47.72727272727272)translate(15.0,3.375)"><tspan style="font-size:12.0px">b</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,75.0)translate(15.0,3.375)"><tspan style="font-size:12.0px">c</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,102.27272727272728)translate(15.0,3.375)"><tspan style="font-size:12.0px">d</tspan></text><text class="toyplot-Datum" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-weight:normal;opacity:1.0;stroke:none;text-anchor:start" transform="translate(112.95918367346937,129.54545454545456)translate(15.0,3.375)"><tspan style="font-size:12.0px">e</tspan></text></g></g><g class="toyplot-mark-Graph" id="t70e8781e17c24e31ad3019ff7fc9442a"><g class="toyplot-Edges"><path d="M 15.0 64.7727272727 L 15.0 34.0909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 34.0909090909 L 80.306122449 34.0909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 64.7727272727 L 15.0 95.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 15.0 95.4545454545 L 47.6530612245 95.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 34.0909090909 L 80.306122449 20.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 20.4545454545 L 112.959183673 20.4545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 34.0909090909 L 80.306122449 47.7272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 47.7272727273 L 112.959183673 47.7272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 95.4545454545 L 47.6530612245 75.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 75.0 L 112.959183673 75.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 95.4545454545 L 47.6530612245 115.909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 47.6530612245 115.909090909 L 80.306122449 115.909090909" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 115.909090909 L 80.306122449 102.272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 102.272727273 L 112.959183673 102.272727273" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 115.909090909 L 80.306122449 129.545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 80.306122449 129.545454545 L 112.959183673 129.545454545" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="64.77272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="15.0" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="34.090909090909101" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="20.45454545454546" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="20.45454545454546" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="47.72727272727272" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="47.72727272727272" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="95.454545454545439" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="75.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="75.0" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="47.65306122448979" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="115.90909090909092" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="102.27272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="102.27272727272728" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="80.306122448979579" cy="129.54545454545456" r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0"><circle cx="112.95918367346937" cy="129.54545454545456" r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t0887e6d53bad4c5f940befc8ec152092" style=""><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none"><title>idx: 0
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
          var data_tables = [{"title": "Scatterplot Data", "names": ["x", "y0"], "id": "t0887e6d53bad4c5f940befc8ec152092", "columns": [[-3.0, -1.0, -2.0, -1.0, 0.0, 0.0, 0.0, 0.0, 0.0], [2.375, 3.5, 1.25, 0.5, 4.0, 3.0, 2.0, 1.0, 0.0]], "filename": "toyplot"}];

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
              var popup = document.querySelector("#tda07a38d0e0c4fce97b3db8aca17d340 .toyplot-mark-popup");
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

