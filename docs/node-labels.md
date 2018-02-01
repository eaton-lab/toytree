
# Node labels

Node labels are markers plotted on the nodes (vertices) of a tree and can be highly modified, including the addition of interactive features which are useful not only for producing final production-quality figures but also for exploring metadata on trees. Many common examples are demonstrated below. 


```python
import toytree
import toyplot
import numpy as np
```


```python
## newick tree string with edge lengths and support values
newick = """
((apple:2,orange:4)100:2,(((tomato:2,eggplant:1)
100:2,pepper:3)90:1,tomatillo:2)100:1);
"""

## load toytree
tre = toytree.tree(newick)
```

### Hide/Show node labels
The argument `node_labels` can be entered as a list of names or left as None or *False* in which case the node labels are not shown. If you enter *True* a special feature is applied to the nodes in which case they will become **interactive** and show information for all available *features* (node values stored in the Tree object metadata) in the Tree. Hover your cursor over the green node labels below for an example. 


```python
## no node labels
tre.draw();

## default node labels
tre.draw(node_labels=True);
```


<div class="toyplot" id="t9e6fbd4fdec746d6b02048f0d0f822f7" style="text-align:center"><svg class="toyplot-canvas-Canvas" height="275.0px" id="t894672820db043b7a58ff405ad3e5d90" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 225.0 275.0" width="225.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t60ee07f7410f40a6921aa3c64dcd6b25"><clipPath id="t1234b96a12e14188a82d75c15fd58d9b"><rect height="275.0" width="225.0" x="0.0" y="0.0"></rect></clipPath><g clip-path="url(#t1234b96a12e14188a82d75c15fd58d9b)"><g class="toyplot-mark-Text" id="tea4246994d774ac38fb2b0cb244acce7"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(123.41636783268305,218.34741288278775)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">eggplant</text></g><g class="toyplot-Datum" transform="translate(138.09964139921965,186.00844772967267)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">tomato</text></g><g class="toyplot-Datum" transform="translate(123.41636783268305,153.66948257655756)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">pepper</text></g><g class="toyplot-Datum" transform="translate(94.049820699609825,121.33051742344244)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">tomatillo</text></g><g class="toyplot-Datum" transform="translate(138.09964139921965,88.991552270327347)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">orange</text></g><g class="toyplot-Datum" transform="translate(108.73309426614644,56.652587117212242)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">apple</text></g></g></g><g class="toyplot-mark-Graph" id="t5e5c73e4c3164181918740172c87b60c"><g class="toyplot-Edges"><path d="M 50.0 111.224590813 L 50.0 72.8220696938" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 72.8220696938 L 79.3665471331 72.8220696938" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 111.224590813 L 50.0 149.627111932" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 149.627111932 L 64.6832735665 149.627111932" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 72.8220696938 L 79.3665471331 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 56.6525871172 L 108.733094266 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 72.8220696938 L 79.3665471331 88.9915522703" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 88.9915522703 L 138.099641399 88.9915522703" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.6832735665 149.627111932 L 64.6832735665 121.330517423" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.6832735665 121.330517423 L 94.0498206996 121.330517423" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.6832735665 149.627111932 L 64.6832735665 177.923706441" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.6832735665 177.923706441 L 79.3665471331 177.923706441" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 177.923706441 L 79.3665471331 153.669482577" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 153.669482577 L 123.416367833 153.669482577" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 177.923706441 L 79.3665471331 202.177930306" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 202.177930306 L 108.733094266 202.177930306" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 108.733094266 202.177930306 L 108.733094266 186.00844773" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 108.733094266 186.00844773 L 138.099641399 186.00844773" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 108.733094266 202.177930306 L 108.733094266 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 108.733094266 218.347412883 L 123.416367833 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><g class="toyplot-HeadMarkers"></g><g class="toyplot-MiddleMarkers"></g><g class="toyplot-TailMarkers"></g></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 111.22459081309398)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(64.683273566536613, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 56.652587117212242)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(108.73309426614644, 56.652587117212242)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 88.991552270327347)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(138.09964139921965, 88.991552270327347)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(64.683273566536613, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(64.683273566536613, 121.33051742344244)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(94.049820699609825, 121.33051742344244)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(64.683273566536613, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 153.66948257655756)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(123.41636783268305, 153.66948257655756)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(108.73309426614644, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(108.73309426614644, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(108.73309426614644, 186.00844772967267)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(138.09964139921965, 186.00844772967267)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(108.73309426614644, 218.34741288278775)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(123.41636783268305, 218.34741288278775)"><circle r="0.0"></circle></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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
modules["toyplot/root/id"] = "t9e6fbd4fdec746d6b02048f0d0f822f7";
modules["toyplot/root"] = (function(root_id)
    {
        return document.querySelector("#" + root_id);
    })(modules["toyplot/root/id"]);
modules["toyplot/canvas/id"] = "t894672820db043b7a58ff405ad3e5d90";
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t5e5c73e4c3164181918740172c87b60c","vertex_data","graph vertex data",["x", "y"],[[-6.0, -6.0, -4.0, -6.0, -5.0, -4.0, -4.0, -2.0, -4.0, 0.0, -5.0, -5.0, -3.0, -5.0, -4.0, -4.0, -4.0, -1.0, -4.0, -2.0, -2.0, -2.0, 0.0, -2.0, -1.0], [3.3125, 4.5, 4.5, 2.125, 2.125, 4.5, 5.0, 5.0, 4.0, 4.0, 2.125, 3.0, 3.0, 1.25, 1.25, 1.25, 2.0, 2.0, 0.5, 0.5, 0.5, 1.0, 1.0, 0.0, 0.0]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t5e5c73e4c3164181918740172c87b60c","edge_data","graph edge data",["source", "target"],[[0, 1, 0, 3, 5, 6, 5, 8, 10, 11, 10, 13, 15, 16, 15, 18, 20, 21, 20, 23], [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24]],"toyplot");
})();</script></div></div>



<div class="toyplot" id="td493d448f82e457e8524cbd2ec6b1c1e" style="text-align:center"><svg class="toyplot-canvas-Canvas" height="275.0px" id="t08a66d95f740492dae9042e362b7d4de" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 225.0 275.0" width="225.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="tae9d552607f24c939a595140083d8075"><clipPath id="t4a1be5df796b4cc18100e0a95b3b5199"><rect height="275.0" width="225.0" x="0.0" y="0.0"></rect></clipPath><g clip-path="url(#t4a1be5df796b4cc18100e0a95b3b5199)"><g class="toyplot-mark-Text" id="tcb243dba361344639f0cde1ff03b51f6"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(123.41636783268305,218.34741288278775)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">eggplant</text></g><g class="toyplot-Datum" transform="translate(138.09964139921965,186.00844772967267)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">tomato</text></g><g class="toyplot-Datum" transform="translate(123.41636783268305,153.66948257655756)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">pepper</text></g><g class="toyplot-Datum" transform="translate(94.049820699609825,121.33051742344244)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">tomatillo</text></g><g class="toyplot-Datum" transform="translate(138.09964139921965,88.991552270327347)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">orange</text></g><g class="toyplot-Datum" transform="translate(108.73309426614644,56.652587117212242)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">apple</text></g></g></g><g class="toyplot-mark-Graph" id="t07d26e3ebdb34058affa4264d9cadce0"><g class="toyplot-Edges"><path d="M 50.0 111.224590813 L 50.0 72.8220696938" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 72.8220696938 L 79.3665471331 72.8220696938" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 111.224590813 L 50.0 149.627111932" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 149.627111932 L 64.6832735665 149.627111932" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 72.8220696938 L 79.3665471331 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 56.6525871172 L 108.733094266 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 72.8220696938 L 79.3665471331 88.9915522703" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 88.9915522703 L 138.099641399 88.9915522703" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.6832735665 149.627111932 L 64.6832735665 121.330517423" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.6832735665 121.330517423 L 94.0498206996 121.330517423" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.6832735665 149.627111932 L 64.6832735665 177.923706441" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.6832735665 177.923706441 L 79.3665471331 177.923706441" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 177.923706441 L 79.3665471331 153.669482577" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 153.669482577 L 123.416367833 153.669482577" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 177.923706441 L 79.3665471331 202.177930306" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 202.177930306 L 108.733094266 202.177930306" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 108.733094266 202.177930306 L 108.733094266 186.00844773" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 108.733094266 186.00844773 L 138.099641399 186.00844773" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 108.733094266 202.177930306 L 108.733094266 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 108.733094266 218.347412883 L 123.416367833 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><g class="toyplot-HeadMarkers"></g><g class="toyplot-MiddleMarkers"></g><g class="toyplot-TailMarkers"></g></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 111.22459081309398)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(64.683273566536613, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 56.652587117212242)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(108.73309426614644, 56.652587117212242)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 88.991552270327347)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(138.09964139921965, 88.991552270327347)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(64.683273566536613, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(64.683273566536613, 121.33051742344244)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(94.049820699609825, 121.33051742344244)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(64.683273566536613, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 153.66948257655756)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(123.41636783268305, 153.66948257655756)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(108.73309426614644, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(108.73309426614644, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(108.73309426614644, 186.00844772967267)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(138.09964139921965, 186.00844772967267)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(108.73309426614644, 218.34741288278775)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(123.41636783268305, 218.34741288278775)"><circle r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t2bfdac1fb74e49958f955f1d3f799735"><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(123.41636783268305, 218.34741288278775)"><title>idx: 0
name: eggplant
dist: 1
support: 100
height: 1</title><circle r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(138.09964139921965, 186.00844772967267)"><title>idx: 1
name: tomato
dist: 2
support: 100
height: 0</title><circle r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(123.41636783268305, 153.66948257655756)"><title>idx: 2
name: pepper
dist: 3
support: 100
height: 1</title><circle r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(94.049820699609825, 121.33051742344244)"><title>idx: 3
name: tomatillo
dist: 2
support: 100
height: 3</title><circle r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(138.09964139921965, 88.991552270327347)"><title>idx: 4
name: orange
dist: 4
support: 100
height: 0</title><circle r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(108.73309426614644, 56.652587117212242)"><title>idx: 5
name: apple
dist: 2
support: 100
height: 2</title><circle r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(108.73309426614644, 202.17793030623019)"><title>idx: 6
name: i6
dist: 2
support: 100
height: 2</title><circle r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(79.366547133073226, 177.92370644139388)"><title>idx: 7
name: i7
dist: 1
support: 90
height: 4</title><circle r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(64.683273566536613, 149.62711193241816)"><title>idx: 8
name: i8
dist: 1
support: 100
height: 5</title><circle r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(79.366547133073226, 72.822069693769805)"><title>idx: 9
name: i9
dist: 2
support: 100
height: 4</title><circle r="7.5"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(50.0, 111.22459081309398)"><title>idx: 10
name: i10
dist: 0
support: 100
height: 6</title><circle r="7.5"></circle></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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
modules["toyplot/root/id"] = "td493d448f82e457e8524cbd2ec6b1c1e";
modules["toyplot/root"] = (function(root_id)
    {
        return document.querySelector("#" + root_id);
    })(modules["toyplot/root/id"]);
modules["toyplot/canvas/id"] = "t08a66d95f740492dae9042e362b7d4de";
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t07d26e3ebdb34058affa4264d9cadce0","vertex_data","graph vertex data",["x", "y"],[[-6.0, -6.0, -4.0, -6.0, -5.0, -4.0, -4.0, -2.0, -4.0, 0.0, -5.0, -5.0, -3.0, -5.0, -4.0, -4.0, -4.0, -1.0, -4.0, -2.0, -2.0, -2.0, 0.0, -2.0, -1.0], [3.3125, 4.5, 4.5, 2.125, 2.125, 4.5, 5.0, 5.0, 4.0, 4.0, 2.125, 3.0, 3.0, 1.25, 1.25, 1.25, 2.0, 2.0, 0.5, 0.5, 0.5, 1.0, 1.0, 0.0, 0.0]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t07d26e3ebdb34058affa4264d9cadce0","edge_data","graph edge data",["source", "target"],[[0, 1, 0, 3, 5, 6, 5, 8, 10, 11, 10, 13, 15, 16, 15, 18, 20, 21, 20, 23], [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t2bfdac1fb74e49958f955f1d3f799735","data","scatterplot",["x", "y0"],[[-1.0, 0.0, -1.0, -3.0, 0.0, -2.0, -2.0, -4.0, -5.0, -4.0, -6.0], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 0.5, 1.25, 2.125, 4.5, 3.3125]],"toyplot");
})();</script></div></div>


### The order of nodes
The order in which nodes and node values are plotted can be accessed from two attributes of a Toytree object, either from `.get_node_labels()` which returns a dictionary mapping node indices to node names, or from `.get_node_values()` which returns a list of node values for the given "feature" argument that is provided. All trees will always have the features `["idx", "name", "support", "dist", "height"]` available. Below we grab the 'idx' values and plot them on the nodes of the tree. The `.get_node_values()` function does not return values for the root node or for leaves by default, since these often are not meaningful on trees where the values represent support values or distances (i.e, the values are actually relevant to edges not nodes), but we want those values here, so we enter True for those arguments. 


```python
## get node index (idx) values
idxs = tre.get_node_values("height", show_root=True, show_tips=False)

## plot tree with node values
tre.draw(node_labels=idxs, tip_labels_align=True, orient='down');
```


<div class="toyplot" id="t3014b27eb07c4a088c4f2ca3c065d638" style="text-align:center"><svg class="toyplot-canvas-Canvas" height="225.0px" id="t7f4b251b6ade43c194b5717c24410a91" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 275.0 225.0" width="275.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t6b5cfe8a33c345f7b1445915a5ae2675"><clipPath id="t0b57b7d816ee454b90f1679bf752fdb8"><rect height="225.0" width="275.0" x="0.0" y="0.0"></rect></clipPath><g clip-path="url(#t0b57b7d816ee454b90f1679bf752fdb8)"><g class="toyplot-mark-Text" id="ta15fb6842de44a0c8d7e12e67bdd9a8e"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(56.652587117212249,133.9909262922508)rotate(90.0)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">eggplant</text></g><g class="toyplot-Datum" transform="translate(88.991552270327361,133.9909262922508)rotate(90.0)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">tomato</text></g><g class="toyplot-Datum" transform="translate(121.33051742344246,133.9909262922508)rotate(90.0)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">pepper</text></g><g class="toyplot-Datum" transform="translate(153.66948257655756,133.9909262922508)rotate(90.0)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">tomatillo</text></g><g class="toyplot-Datum" transform="translate(186.00844772967267,133.9909262922508)rotate(90.0)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">orange</text></g><g class="toyplot-Datum" transform="translate(218.34741288278775,133.9909262922508)rotate(90.0)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">apple</text></g></g></g><g class="toyplot-mark-Graph" id="t8b543de71b2c45b3a224857e9a416047"><g class="toyplot-Edges"><path d="M 56.6525871172 133.990926292 L 56.6525871172 119.992438577" style="fill:none;stroke:rgb(66.3%,66.3%,66.3%);stroke-dasharray:2, 4;stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 88.9915522703 133.990926292 L 88.9915522703 133.990926292" style="fill:none;stroke:rgb(66.3%,66.3%,66.3%);stroke-dasharray:2, 4;stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 121.330517423 133.990926292 L 121.330517423 119.992438577" style="fill:none;stroke:rgb(66.3%,66.3%,66.3%);stroke-dasharray:2, 4;stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 153.669482577 133.990926292 L 153.669482577 91.9954631461" style="fill:none;stroke:rgb(66.3%,66.3%,66.3%);stroke-dasharray:2, 4;stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 186.00844773 133.990926292 L 186.00844773 133.990926292" style="fill:none;stroke:rgb(66.3%,66.3%,66.3%);stroke-dasharray:2, 4;stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 218.347412883 133.990926292 L 218.347412883 105.993950862" style="fill:none;stroke:rgb(66.3%,66.3%,66.3%);stroke-dasharray:2, 4;stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><g class="toyplot-HeadMarkers"></g><g class="toyplot-MiddleMarkers"></g><g class="toyplot-TailMarkers"></g></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(56.652587117212249, 133.9909262922508)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(88.991552270327361, 133.9909262922508)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(121.33051742344246, 133.9909262922508)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(153.66948257655756, 133.9909262922508)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(186.00844772967267, 133.9909262922508)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(218.34741288278775, 133.9909262922508)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(56.652587117212249, 119.99243857687566)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(88.991552270327361, 133.9909262922508)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(121.33051742344246, 119.99243857687566)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(153.66948257655756, 91.995463146125402)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(186.00844772967267, 133.9909262922508)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(218.34741288278775, 105.99395086150052)"><circle r="0.0"></circle></g></g></g><g class="toyplot-mark-Graph" id="tff8fabb044d442d28e542fce180894a3"><g class="toyplot-Edges"><path d="M 163.775409187 50.0 L 202.177930306 50.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 202.177930306 50.0 L 202.177930306 77.9969754308" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 163.775409187 50.0 L 125.372888068 50.0" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 125.372888068 50.0 L 125.372888068 63.9984877154" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 202.177930306 77.9969754308 L 218.347412883 77.9969754308" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 218.347412883 77.9969754308 L 218.347412883 105.993950862" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 202.177930306 77.9969754308 L 186.00844773 77.9969754308" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 186.00844773 77.9969754308 L 186.00844773 133.990926292" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 125.372888068 63.9984877154 L 153.669482577 63.9984877154" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 153.669482577 63.9984877154 L 153.669482577 91.9954631461" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 125.372888068 63.9984877154 L 97.0762935586 63.9984877154" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 97.0762935586 63.9984877154 L 97.0762935586 77.9969754308" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 97.0762935586 77.9969754308 L 121.330517423 77.9969754308" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 121.330517423 77.9969754308 L 121.330517423 119.992438577" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 97.0762935586 77.9969754308 L 72.8220696938 77.9969754308" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 72.8220696938 77.9969754308 L 72.8220696938 105.993950862" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 72.8220696938 105.993950862 L 88.9915522703 105.993950862" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 88.9915522703 105.993950862 L 88.9915522703 133.990926292" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 72.8220696938 105.993950862 L 56.6525871172 105.993950862" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 56.6525871172 105.993950862 L 56.6525871172 119.992438577" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><g class="toyplot-HeadMarkers"></g><g class="toyplot-MiddleMarkers"></g><g class="toyplot-TailMarkers"></g></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(163.77540918690602, 50.0)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(202.17793030623019, 50.0)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(202.17793030623019, 77.996975430750268)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(125.37288806758184, 50.0)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(125.37288806758184, 63.998487715375141)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(202.17793030623019, 77.996975430750268)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(218.34741288278775, 77.996975430750268)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(218.34741288278775, 105.99395086150052)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(186.00844772967267, 77.996975430750268)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(186.00844772967267, 133.9909262922508)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(125.37288806758184, 63.998487715375141)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(153.66948257655756, 63.998487715375141)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(153.66948257655756, 91.995463146125402)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(97.076293558606125, 63.998487715375141)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(97.076293558606125, 77.996975430750268)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(97.076293558606125, 77.996975430750268)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(121.33051742344246, 77.996975430750268)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(121.33051742344246, 119.99243857687566)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(72.822069693769805, 77.996975430750268)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(72.822069693769805, 105.99395086150052)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(72.822069693769805, 105.99395086150052)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(88.991552270327361, 105.99395086150052)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(88.991552270327361, 133.9909262922508)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(56.652587117212249, 105.99395086150052)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(98.8%,55.3%,38.4%);fill-opacity:1.0;opacity:1.0;stroke:rgb(98.8%,55.3%,38.4%);stroke-opacity:1.0" transform="translate(56.652587117212249, 119.99243857687566)"><circle r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t1ccf317d4de149a6825dc210fa341b45"><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(72.822069693769805, 105.99395086150052)"><title>idx: 6
name: i6
dist: 2
support: 100
height: 2</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">2</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(97.076293558606125, 77.996975430750268)"><title>idx: 7
name: i7
dist: 1
support: 90
height: 4</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">4</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(125.37288806758184, 63.998487715375141)"><title>idx: 8
name: i8
dist: 1
support: 100
height: 5</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">5</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(202.17793030623019, 77.996975430750268)"><title>idx: 9
name: i9
dist: 2
support: 100
height: 4</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">4</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(163.77540918690602, 50.0)"><title>idx: 10
name: i10
dist: 0
support: 100
height: 6</title><circle r="11.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-2.502" y="2.2995">6</text></g></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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
modules["toyplot/root/id"] = "t3014b27eb07c4a088c4f2ca3c065d638";
modules["toyplot/root"] = (function(root_id)
    {
        return document.querySelector("#" + root_id);
    })(modules["toyplot/root/id"]);
modules["toyplot/canvas/id"] = "t7f4b251b6ade43c194b5717c24410a91";
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t8b543de71b2c45b3a224857e9a416047","vertex_data","graph vertex data",["x", "y"],[[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0], [-6.0, -6.0, -6.0, -6.0, -6.0, -6.0, -5.0, -6.0, -5.0, -3.0, -6.0, -4.0]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t8b543de71b2c45b3a224857e9a416047","edge_data","graph edge data",["source", "target"],[[0, 1, 2, 3, 4, 5], [6, 7, 8, 9, 10, 11]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"tff8fabb044d442d28e542fce180894a3","vertex_data","graph vertex data",["x", "y"],[[3.3125, 4.5, 4.5, 2.125, 2.125, 4.5, 5.0, 5.0, 4.0, 4.0, 2.125, 3.0, 3.0, 1.25, 1.25, 1.25, 2.0, 2.0, 0.5, 0.5, 0.5, 1.0, 1.0, 0.0, 0.0], [0.0, 0.0, -2.0, 0.0, -1.0, -2.0, -2.0, -4.0, -2.0, -6.0, -1.0, -1.0, -3.0, -1.0, -2.0, -2.0, -2.0, -5.0, -2.0, -4.0, -4.0, -4.0, -6.0, -4.0, -5.0]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"tff8fabb044d442d28e542fce180894a3","edge_data","graph edge data",["source", "target"],[[0, 1, 0, 3, 5, 6, 5, 8, 10, 11, 10, 13, 15, 16, 15, 18, 20, 21, 20, 23], [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t1ccf317d4de149a6825dc210fa341b45","data","scatterplot",["x", "y0"],[[0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 0.5, 1.25, 2.125, 4.5, 3.3125], [-5.0, -6.0, -5.0, -3.0, -6.0, -4.0, -4.0, -2.0, -1.0, -2.0, 0.0]],"toyplot");
})();</script></div></div>


### Show specific node features

Similarly, in this case we are plotting support values so we will let the default arguments to `.get_node_values()` hide the values at the tips and root of the tree. 


```python
## plot tree with node values
tre.draw(
    node_labels=tre.get_node_values("support"), 
    node_size=24, 
    node_labels_style={"font-size": "11px"},
    );
```


<div class="toyplot" id="td8ce44598b5e4a4694de3dc91dcdddcd" style="text-align:center"><svg class="toyplot-canvas-Canvas" height="275.0px" id="t1d2e965e5b184ca29ccc2c694257cd88" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 225.0 275.0" width="225.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t6fa3af737b0f44f1a23591e9309899d4"><clipPath id="t7c9514f11d9c4ed2b7fe84c5672b923e"><rect height="275.0" width="225.0" x="0.0" y="0.0"></rect></clipPath><g clip-path="url(#t7c9514f11d9c4ed2b7fe84c5672b923e)"><g class="toyplot-mark-Text" id="t52cb5982892742b6b5d9865033ebd5f9"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(123.41636783268305,218.34741288278775)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">eggplant</text></g><g class="toyplot-Datum" transform="translate(138.09964139921965,186.00844772967267)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">tomato</text></g><g class="toyplot-Datum" transform="translate(123.41636783268305,153.66948257655756)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">pepper</text></g><g class="toyplot-Datum" transform="translate(94.049820699609825,121.33051742344244)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">tomatillo</text></g><g class="toyplot-Datum" transform="translate(138.09964139921965,88.991552270327347)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">orange</text></g><g class="toyplot-Datum" transform="translate(108.73309426614644,56.652587117212242)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">apple</text></g></g></g><g class="toyplot-mark-Graph" id="ta62f6fc73ec44e13a43d5a4fada245ac"><g class="toyplot-Edges"><path d="M 50.0 111.224590813 L 50.0 72.8220696938" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 72.8220696938 L 79.3665471331 72.8220696938" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 111.224590813 L 50.0 149.627111932" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 149.627111932 L 64.6832735665 149.627111932" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 72.8220696938 L 79.3665471331 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 56.6525871172 L 108.733094266 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 72.8220696938 L 79.3665471331 88.9915522703" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 88.9915522703 L 138.099641399 88.9915522703" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.6832735665 149.627111932 L 64.6832735665 121.330517423" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.6832735665 121.330517423 L 94.0498206996 121.330517423" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.6832735665 149.627111932 L 64.6832735665 177.923706441" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 64.6832735665 177.923706441 L 79.3665471331 177.923706441" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 177.923706441 L 79.3665471331 153.669482577" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 153.669482577 L 123.416367833 153.669482577" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 177.923706441 L 79.3665471331 202.177930306" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 79.3665471331 202.177930306 L 108.733094266 202.177930306" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 108.733094266 202.177930306 L 108.733094266 186.00844773" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 108.733094266 186.00844773 L 138.099641399 186.00844773" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 108.733094266 202.177930306 L 108.733094266 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 108.733094266 218.347412883 L 123.416367833 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><g class="toyplot-HeadMarkers"></g><g class="toyplot-MiddleMarkers"></g><g class="toyplot-TailMarkers"></g></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 111.22459081309398)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(64.683273566536613, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 56.652587117212242)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(108.73309426614644, 56.652587117212242)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 88.991552270327347)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(138.09964139921965, 88.991552270327347)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(64.683273566536613, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(64.683273566536613, 121.33051742344244)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(94.049820699609825, 121.33051742344244)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(64.683273566536613, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 153.66948257655756)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(123.41636783268305, 153.66948257655756)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(79.366547133073226, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(108.73309426614644, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(108.73309426614644, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(108.73309426614644, 186.00844772967267)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(138.09964139921965, 186.00844772967267)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(108.73309426614644, 218.34741288278775)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(123.41636783268305, 218.34741288278775)"><circle r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t0674e42a466a41e9a9782b7f01d37c18"><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(108.73309426614644, 202.17793030623019)"><title>idx: 6
name: i6
dist: 2
support: 100
height: 2</title><circle r="12.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:11.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-9.174" y="2.8105">100</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(79.366547133073226, 177.92370644139388)"><title>idx: 7
name: i7
dist: 1
support: 90
height: 4</title><circle r="12.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:11.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-6.116" y="2.8105">90</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(64.683273566536613, 149.62711193241816)"><title>idx: 8
name: i8
dist: 1
support: 100
height: 5</title><circle r="12.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:11.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-9.174" y="2.8105">100</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(79.366547133073226, 72.822069693769805)"><title>idx: 9
name: i9
dist: 2
support: 100
height: 4</title><circle r="12.0"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:11.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-9.174" y="2.8105">100</text></g></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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
modules["toyplot/root/id"] = "td8ce44598b5e4a4694de3dc91dcdddcd";
modules["toyplot/root"] = (function(root_id)
    {
        return document.querySelector("#" + root_id);
    })(modules["toyplot/root/id"]);
modules["toyplot/canvas/id"] = "t1d2e965e5b184ca29ccc2c694257cd88";
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"ta62f6fc73ec44e13a43d5a4fada245ac","vertex_data","graph vertex data",["x", "y"],[[-6.0, -6.0, -4.0, -6.0, -5.0, -4.0, -4.0, -2.0, -4.0, 0.0, -5.0, -5.0, -3.0, -5.0, -4.0, -4.0, -4.0, -1.0, -4.0, -2.0, -2.0, -2.0, 0.0, -2.0, -1.0], [3.3125, 4.5, 4.5, 2.125, 2.125, 4.5, 5.0, 5.0, 4.0, 4.0, 2.125, 3.0, 3.0, 1.25, 1.25, 1.25, 2.0, 2.0, 0.5, 0.5, 0.5, 1.0, 1.0, 0.0, 0.0]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"ta62f6fc73ec44e13a43d5a4fada245ac","edge_data","graph edge data",["source", "target"],[[0, 1, 0, 3, 5, 6, 5, 8, 10, 11, 10, 13, 15, 16, 15, 18, 20, 21, 20, 23], [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t0674e42a466a41e9a9782b7f01d37c18","data","scatterplot",["x", "y0"],[[-1.0, 0.0, -1.0, -3.0, 0.0, -2.0, -2.0, -4.0, -5.0, -4.0, -6.0], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 0.5, 1.25, 2.125, 4.5, 3.3125]],"toyplot");
})();</script></div></div>


### Add/modify/del node features


```python
## traverse tree and add a new feature to each node
for node in tre.tree.traverse():
    if node.dist > 2:
        node.add_feature("is_long_branch", True)
    else:
        node.add_feature("is_long_branch", False)
```


```python
## get new feature in node plot order
feature = tre.get_node_values("is_long_branch", 0, 0)

## plot tree with node values
tre.draw(width=300, 
         node_labels=feature,
         node_size=25,
         use_edge_lengths=True,
         );
```


<div class="toyplot" id="tf075f4d4f30e4398a60bcbb9a87dd6a2" style="text-align:center"><svg class="toyplot-canvas-Canvas" height="275.0px" id="t564452e456854ee7a189de8aed3b9a70" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 300.0 275.0" width="300.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="tcf68bf0abb5143bfb5a5f1392edbf25f"><clipPath id="t4bed8fd5cbcb41ebaea9b614f26f5b34"><rect height="275.0" width="300.0" x="0.0" y="0.0"></rect></clipPath><g clip-path="url(#t4bed8fd5cbcb41ebaea9b614f26f5b34)"><g class="toyplot-mark-Text" id="tde32780409d64f8db442d8758022955e"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(182.08853101702886,218.34741288278775)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">eggplant</text></g><g class="toyplot-Datum" transform="translate(208.50623722043466,186.00844772967267)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">tomato</text></g><g class="toyplot-Datum" transform="translate(182.08853101702886,153.66948257655756)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">pepper</text></g><g class="toyplot-Datum" transform="translate(129.25311861021731,121.33051742344244)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">tomatillo</text></g><g class="toyplot-Datum" transform="translate(208.50623722043466,88.991552270327347)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">orange</text></g><g class="toyplot-Datum" transform="translate(155.67082481362308,56.652587117212242)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">apple</text></g></g></g><g class="toyplot-mark-Graph" id="t7c99b546414d43878e279bbf9a189e36"><g class="toyplot-Edges"><path d="M 50.0 111.224590813 L 50.0 72.8220696938" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 72.8220696938 L 102.835412407 72.8220696938" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 111.224590813 L 50.0 149.627111932" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 149.627111932 L 76.4177062034 149.627111932" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 72.8220696938 L 102.835412407 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 56.6525871172 L 155.670824814 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 72.8220696938 L 102.835412407 88.9915522703" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 88.9915522703 L 208.50623722 88.9915522703" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 76.4177062034 149.627111932 L 76.4177062034 121.330517423" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 76.4177062034 121.330517423 L 129.25311861 121.330517423" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 76.4177062034 149.627111932 L 76.4177062034 177.923706441" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 76.4177062034 177.923706441 L 102.835412407 177.923706441" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 177.923706441 L 102.835412407 153.669482577" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 153.669482577 L 182.088531017 153.669482577" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 177.923706441 L 102.835412407 202.177930306" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 202.177930306 L 155.670824814 202.177930306" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 155.670824814 202.177930306 L 155.670824814 186.00844773" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 155.670824814 186.00844773 L 208.50623722 186.00844773" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 155.670824814 202.177930306 L 155.670824814 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 155.670824814 218.347412883 L 182.088531017 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><g class="toyplot-HeadMarkers"></g><g class="toyplot-MiddleMarkers"></g><g class="toyplot-TailMarkers"></g></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 111.22459081309398)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(76.417706203405771, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 56.652587117212242)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(155.67082481362308, 56.652587117212242)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 88.991552270327347)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(208.50623722043466, 88.991552270327347)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(76.417706203405771, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(76.417706203405771, 121.33051742344244)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(129.25311861021731, 121.33051742344244)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(76.417706203405771, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 153.66948257655756)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(182.08853101702886, 153.66948257655756)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(155.67082481362308, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(155.67082481362308, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(155.67082481362308, 186.00844772967267)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(208.50623722043466, 186.00844772967267)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(155.67082481362308, 218.34741288278775)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(182.08853101702886, 218.34741288278775)"><circle r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t86fca31672dd4ae4a3ee7c5d24429b4a"><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(155.67082481362308, 202.17793030623019)"><title>idx: 6
name: i6
dist: 2
support: 100
is_long_branch: False
height: 2</title><circle r="12.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-11.0025" y="2.2995">False</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(102.83541240681154, 177.92370644139388)"><title>idx: 7
name: i7
dist: 1
support: 90
is_long_branch: False
height: 4</title><circle r="12.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-11.0025" y="2.2995">False</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(76.417706203405771, 149.62711193241816)"><title>idx: 8
name: i8
dist: 1
support: 100
is_long_branch: False
height: 5</title><circle r="12.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-11.0025" y="2.2995">False</text></g></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:none" transform="translate(102.83541240681154, 72.822069693769805)"><title>idx: 9
name: i9
dist: 2
support: 100
is_long_branch: False
height: 4</title><circle r="12.5"></circle><g><text style="fill:rgb(14.9%,14.9%,14.9%);fill-opacity:1.0;font-family:helvetica;font-size:9.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre" x="-11.0025" y="2.2995">False</text></g></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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
modules["toyplot/root/id"] = "tf075f4d4f30e4398a60bcbb9a87dd6a2";
modules["toyplot/root"] = (function(root_id)
    {
        return document.querySelector("#" + root_id);
    })(modules["toyplot/root/id"]);
modules["toyplot/canvas/id"] = "t564452e456854ee7a189de8aed3b9a70";
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t7c99b546414d43878e279bbf9a189e36","vertex_data","graph vertex data",["x", "y"],[[-6.0, -6.0, -4.0, -6.0, -5.0, -4.0, -4.0, -2.0, -4.0, 0.0, -5.0, -5.0, -3.0, -5.0, -4.0, -4.0, -4.0, -1.0, -4.0, -2.0, -2.0, -2.0, 0.0, -2.0, -1.0], [3.3125, 4.5, 4.5, 2.125, 2.125, 4.5, 5.0, 5.0, 4.0, 4.0, 2.125, 3.0, 3.0, 1.25, 1.25, 1.25, 2.0, 2.0, 0.5, 0.5, 0.5, 1.0, 1.0, 0.0, 0.0]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t7c99b546414d43878e279bbf9a189e36","edge_data","graph edge data",["source", "target"],[[0, 1, 0, 3, 5, 6, 5, 8, 10, 11, 10, 13, 15, 16, 15, 18, 20, 21, 20, 23], [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t86fca31672dd4ae4a3ee7c5d24429b4a","data","scatterplot",["x", "y0"],[[-1.0, 0.0, -1.0, -3.0, 0.0, -2.0, -2.0, -4.0, -5.0, -4.0, -6.0], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 0.5, 1.25, 2.125, 4.5, 3.3125]],"toyplot");
})();</script></div></div>


### Node colors
Here we apply different colors to each node based on its value for the feature that we assigned to the nodes above, *is_long_branch*. We also use the *magic* argument `node_labels=True` which assigns interactive information to each node. Hover your cursor over the nodes in the plot below to see how the colors match up with the features of the node. 


```python
## get new feature in node plot order
feature = tre.get_node_values("is_long_branch", 0, 0)
colors = ["#262626" if i else "lightgrey" for i in feature]

## plot tree with node values
tre.draw(width=300, 
         node_labels=True,
         node_size=20,
         node_color=colors,
         node_style={"stroke":"black"},
         use_edge_lengths=True,
         );
```


<div class="toyplot" id="t7310d017877f4119a6d51d83db24c6bf" style="text-align:center"><svg class="toyplot-canvas-Canvas" height="275.0px" id="t7a7ef93374d3417c9653775d9082b7a5" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 300.0 275.0" width="300.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="tc57976bd378a435f8c687f1da756e944"><clipPath id="t7e9d55e4b1fd4968bdb86856f1784590"><rect height="275.0" width="300.0" x="0.0" y="0.0"></rect></clipPath><g clip-path="url(#t7e9d55e4b1fd4968bdb86856f1784590)"><g class="toyplot-mark-Text" id="te708b1f946e647289550935a3ad27331"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(182.08853101702886,218.34741288278775)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">eggplant</text></g><g class="toyplot-Datum" transform="translate(208.50623722043466,186.00844772967267)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">tomato</text></g><g class="toyplot-Datum" transform="translate(182.08853101702886,153.66948257655756)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">pepper</text></g><g class="toyplot-Datum" transform="translate(129.25311861021731,121.33051742344244)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">tomatillo</text></g><g class="toyplot-Datum" transform="translate(208.50623722043466,88.991552270327347)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">orange</text></g><g class="toyplot-Datum" transform="translate(155.67082481362308,56.652587117212242)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">apple</text></g></g></g><g class="toyplot-mark-Graph" id="t392685e22fff4ec0895c4d6d2fd4dfa7"><g class="toyplot-Edges"><path d="M 50.0 111.224590813 L 50.0 72.8220696938" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 72.8220696938 L 102.835412407 72.8220696938" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 111.224590813 L 50.0 149.627111932" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 149.627111932 L 76.4177062034 149.627111932" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 72.8220696938 L 102.835412407 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 56.6525871172 L 155.670824814 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 72.8220696938 L 102.835412407 88.9915522703" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 88.9915522703 L 208.50623722 88.9915522703" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 76.4177062034 149.627111932 L 76.4177062034 121.330517423" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 76.4177062034 121.330517423 L 129.25311861 121.330517423" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 76.4177062034 149.627111932 L 76.4177062034 177.923706441" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 76.4177062034 177.923706441 L 102.835412407 177.923706441" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 177.923706441 L 102.835412407 153.669482577" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 153.669482577 L 182.088531017 153.669482577" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 177.923706441 L 102.835412407 202.177930306" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 202.177930306 L 155.670824814 202.177930306" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 155.670824814 202.177930306 L 155.670824814 186.00844773" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 155.670824814 186.00844773 L 208.50623722 186.00844773" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 155.670824814 202.177930306 L 155.670824814 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 155.670824814 218.347412883 L 182.088531017 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><g class="toyplot-HeadMarkers"></g><g class="toyplot-MiddleMarkers"></g><g class="toyplot-TailMarkers"></g></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 111.22459081309398)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(76.417706203405771, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 56.652587117212242)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(155.67082481362308, 56.652587117212242)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 88.991552270327347)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(208.50623722043466, 88.991552270327347)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(76.417706203405771, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(76.417706203405771, 121.33051742344244)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(129.25311861021731, 121.33051742344244)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(76.417706203405771, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 153.66948257655756)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(182.08853101702886, 153.66948257655756)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(155.67082481362308, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(155.67082481362308, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(155.67082481362308, 186.00844772967267)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(208.50623722043466, 186.00844772967267)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(155.67082481362308, 218.34741288278775)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(182.08853101702886, 218.34741288278775)"><circle r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="te2dc9d8e245840f0ab919e8db528cdf8"><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,0%,0%);stroke-opacity:1.0" transform="translate(182.08853101702886, 218.34741288278775)"><title>idx: 0
name: eggplant
dist: 1
support: 100
is_long_branch: False
height: 1</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,0%,0%);stroke-opacity:1.0" transform="translate(208.50623722043466, 186.00844772967267)"><title>idx: 1
name: tomato
dist: 2
support: 100
is_long_branch: False
height: 0</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,0%,0%);stroke-opacity:1.0" transform="translate(182.08853101702886, 153.66948257655756)"><title>idx: 2
name: pepper
dist: 3
support: 100
is_long_branch: True
height: 1</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,0%,0%);stroke-opacity:1.0" transform="translate(129.25311861021731, 121.33051742344244)"><title>idx: 3
name: tomatillo
dist: 2
support: 100
is_long_branch: False
height: 3</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,0%,0%);stroke-opacity:1.0" transform="translate(208.50623722043466, 88.991552270327347)"><title>idx: 4
name: orange
dist: 4
support: 100
is_long_branch: True
height: 0</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,0%,0%);stroke-opacity:1.0" transform="translate(155.67082481362308, 56.652587117212242)"><title>idx: 5
name: apple
dist: 2
support: 100
is_long_branch: False
height: 2</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,0%,0%);stroke-opacity:1.0" transform="translate(155.67082481362308, 202.17793030623019)"><title>idx: 6
name: i6
dist: 2
support: 100
is_long_branch: False
height: 2</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,0%,0%);stroke-opacity:1.0" transform="translate(102.83541240681154, 177.92370644139388)"><title>idx: 7
name: i7
dist: 1
support: 90
is_long_branch: False
height: 4</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,0%,0%);stroke-opacity:1.0" transform="translate(76.417706203405771, 149.62711193241816)"><title>idx: 8
name: i8
dist: 1
support: 100
is_long_branch: False
height: 5</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,0%,0%);stroke-opacity:1.0" transform="translate(102.83541240681154, 72.822069693769805)"><title>idx: 9
name: i9
dist: 2
support: 100
is_long_branch: False
height: 4</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,0%,0%);stroke-opacity:1.0" transform="translate(50.0, 111.22459081309398)"><title>idx: 10
name: i10
dist: 0
support: 100
is_long_branch: False
height: 6</title><circle r="10.0"></circle></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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
modules["toyplot/root/id"] = "t7310d017877f4119a6d51d83db24c6bf";
modules["toyplot/root"] = (function(root_id)
    {
        return document.querySelector("#" + root_id);
    })(modules["toyplot/root/id"]);
modules["toyplot/canvas/id"] = "t7a7ef93374d3417c9653775d9082b7a5";
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t392685e22fff4ec0895c4d6d2fd4dfa7","vertex_data","graph vertex data",["x", "y"],[[-6.0, -6.0, -4.0, -6.0, -5.0, -4.0, -4.0, -2.0, -4.0, 0.0, -5.0, -5.0, -3.0, -5.0, -4.0, -4.0, -4.0, -1.0, -4.0, -2.0, -2.0, -2.0, 0.0, -2.0, -1.0], [3.3125, 4.5, 4.5, 2.125, 2.125, 4.5, 5.0, 5.0, 4.0, 4.0, 2.125, 3.0, 3.0, 1.25, 1.25, 1.25, 2.0, 2.0, 0.5, 0.5, 0.5, 1.0, 1.0, 0.0, 0.0]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t392685e22fff4ec0895c4d6d2fd4dfa7","edge_data","graph edge data",["source", "target"],[[0, 1, 0, 3, 5, 6, 5, 8, 10, 11, 10, 13, 15, 16, 15, 18, 20, 21, 20, 23], [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"te2dc9d8e245840f0ab919e8db528cdf8","data","scatterplot",["x", "y0"],[[-1.0, 0.0, -1.0, -3.0, 0.0, -2.0, -2.0, -4.0, -5.0, -4.0, -6.0], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 0.5, 1.25, 2.125, 4.5, 3.3125]],"toyplot");
})();</script></div></div>


### Node styling
...


```python
## get new feature in node plot order
feature = tre.get_node_values("is_long_branch", 0, 0)
colors = ["#262626" if i else "lightgrey" for i in feature]

## plot tree with node values
tre.draw(width=300, 
         node_labels=True,
         node_size=20,
         node_color=colors,
         node_style={"stroke":"darkcyan", "stroke-width": "2px"},
         use_edge_lengths=True,
         );
```


<div class="toyplot" id="t373f141f34f94893b61edbcfb6c8c9cb" style="text-align:center"><svg class="toyplot-canvas-Canvas" height="275.0px" id="tbb08219fdf9848b3ad791d7fd47582ea" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" viewBox="0 0 300.0 275.0" width="300.0px" xmlns="http://www.w3.org/2000/svg" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink"><g class="toyplot-coordinates-Cartesian" id="t284f1f1305f24e999e753e56f12ec77f"><clipPath id="tf7e4056d3d404090b421cb112e88e680"><rect height="275.0" width="300.0" x="0.0" y="0.0"></rect></clipPath><g clip-path="url(#tf7e4056d3d404090b421cb112e88e680)"><g class="toyplot-mark-Text" id="t3063972786274e9893e142df53e999a4"><g class="toyplot-Series"><g class="toyplot-Datum" transform="translate(182.08853101702886,218.34741288278775)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">eggplant</text></g><g class="toyplot-Datum" transform="translate(208.50623722043466,186.00844772967267)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">tomato</text></g><g class="toyplot-Datum" transform="translate(182.08853101702886,153.66948257655756)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">pepper</text></g><g class="toyplot-Datum" transform="translate(129.25311861021731,121.33051742344244)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">tomatillo</text></g><g class="toyplot-Datum" transform="translate(208.50623722043466,88.991552270327347)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">orange</text></g><g class="toyplot-Datum" transform="translate(155.67082481362308,56.652587117212242)"><text style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:12.0px;font-weight:normal;opacity:1.0;stroke:none;vertical-align:baseline;white-space:pre" x="15.0" y="3.066">apple</text></g></g></g><g class="toyplot-mark-Graph" id="ta01c8b3c7858431e906204b690585c65"><g class="toyplot-Edges"><path d="M 50.0 111.224590813 L 50.0 72.8220696938" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 72.8220696938 L 102.835412407 72.8220696938" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 111.224590813 L 50.0 149.627111932" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 50.0 149.627111932 L 76.4177062034 149.627111932" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 72.8220696938 L 102.835412407 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 56.6525871172 L 155.670824814 56.6525871172" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 72.8220696938 L 102.835412407 88.9915522703" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 88.9915522703 L 208.50623722 88.9915522703" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 76.4177062034 149.627111932 L 76.4177062034 121.330517423" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 76.4177062034 121.330517423 L 129.25311861 121.330517423" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 76.4177062034 149.627111932 L 76.4177062034 177.923706441" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 76.4177062034 177.923706441 L 102.835412407 177.923706441" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 177.923706441 L 102.835412407 153.669482577" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 153.669482577 L 182.088531017 153.669482577" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 177.923706441 L 102.835412407 202.177930306" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 102.835412407 202.177930306 L 155.670824814 202.177930306" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 155.670824814 202.177930306 L 155.670824814 186.00844773" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 155.670824814 186.00844773 L 208.50623722 186.00844773" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 155.670824814 202.177930306 L 155.670824814 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><path d="M 155.670824814 218.347412883 L 182.088531017 218.347412883" style="fill:none;stroke:rgb(16.1%,15.3%,14.1%);stroke-linecap:round;stroke-opacity:1.0;stroke-width:2"></path><g class="toyplot-HeadMarkers"></g><g class="toyplot-MiddleMarkers"></g><g class="toyplot-TailMarkers"></g></g><g class="toyplot-Vertices"><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 111.22459081309398)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(50.0, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(76.417706203405771, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 72.822069693769805)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 56.652587117212242)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(155.67082481362308, 56.652587117212242)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 88.991552270327347)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(208.50623722043466, 88.991552270327347)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(76.417706203405771, 149.62711193241816)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(76.417706203405771, 121.33051742344244)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(129.25311861021731, 121.33051742344244)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(76.417706203405771, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 177.92370644139388)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 153.66948257655756)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(182.08853101702886, 153.66948257655756)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(102.83541240681154, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(155.67082481362308, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(155.67082481362308, 202.17793030623019)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(155.67082481362308, 186.00844772967267)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(208.50623722043466, 186.00844772967267)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(155.67082481362308, 218.34741288278775)"><circle r="0.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(40%,76.1%,64.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(40%,76.1%,64.7%);stroke-opacity:1.0" transform="translate(182.08853101702886, 218.34741288278775)"><circle r="0.0"></circle></g></g></g><g class="toyplot-mark-Scatterplot" id="t8aa62b39b49e49fbace0692add4d8ea6"><g class="toyplot-Series"><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,54.5%,54.5%);stroke-opacity:1.0;stroke-width:2px" transform="translate(182.08853101702886, 218.34741288278775)"><title>idx: 0
name: eggplant
dist: 1
support: 100
is_long_branch: False
height: 1</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,54.5%,54.5%);stroke-opacity:1.0;stroke-width:2px" transform="translate(208.50623722043466, 186.00844772967267)"><title>idx: 1
name: tomato
dist: 2
support: 100
is_long_branch: False
height: 0</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,54.5%,54.5%);stroke-opacity:1.0;stroke-width:2px" transform="translate(182.08853101702886, 153.66948257655756)"><title>idx: 2
name: pepper
dist: 3
support: 100
is_long_branch: True
height: 1</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,54.5%,54.5%);stroke-opacity:1.0;stroke-width:2px" transform="translate(129.25311861021731, 121.33051742344244)"><title>idx: 3
name: tomatillo
dist: 2
support: 100
is_long_branch: False
height: 3</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,54.5%,54.5%);stroke-opacity:1.0;stroke-width:2px" transform="translate(208.50623722043466, 88.991552270327347)"><title>idx: 4
name: orange
dist: 4
support: 100
is_long_branch: True
height: 0</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,54.5%,54.5%);stroke-opacity:1.0;stroke-width:2px" transform="translate(155.67082481362308, 56.652587117212242)"><title>idx: 5
name: apple
dist: 2
support: 100
is_long_branch: False
height: 2</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,54.5%,54.5%);stroke-opacity:1.0;stroke-width:2px" transform="translate(155.67082481362308, 202.17793030623019)"><title>idx: 6
name: i6
dist: 2
support: 100
is_long_branch: False
height: 2</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,54.5%,54.5%);stroke-opacity:1.0;stroke-width:2px" transform="translate(102.83541240681154, 177.92370644139388)"><title>idx: 7
name: i7
dist: 1
support: 90
is_long_branch: False
height: 4</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,54.5%,54.5%);stroke-opacity:1.0;stroke-width:2px" transform="translate(76.417706203405771, 149.62711193241816)"><title>idx: 8
name: i8
dist: 1
support: 100
is_long_branch: False
height: 5</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,54.5%,54.5%);stroke-opacity:1.0;stroke-width:2px" transform="translate(102.83541240681154, 72.822069693769805)"><title>idx: 9
name: i9
dist: 2
support: 100
is_long_branch: False
height: 4</title><circle r="10.0"></circle></g><g class="toyplot-Datum" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;opacity:1.0;stroke:rgb(0%,54.5%,54.5%);stroke-opacity:1.0;stroke-width:2px" transform="translate(50.0, 111.22459081309398)"><title>idx: 10
name: i10
dist: 0
support: 100
is_long_branch: False
height: 6</title><circle r="10.0"></circle></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
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
modules["toyplot/root/id"] = "t373f141f34f94893b61edbcfb6c8c9cb";
modules["toyplot/root"] = (function(root_id)
    {
        return document.querySelector("#" + root_id);
    })(modules["toyplot/root/id"]);
modules["toyplot/canvas/id"] = "tbb08219fdf9848b3ad791d7fd47582ea";
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"ta01c8b3c7858431e906204b690585c65","vertex_data","graph vertex data",["x", "y"],[[-6.0, -6.0, -4.0, -6.0, -5.0, -4.0, -4.0, -2.0, -4.0, 0.0, -5.0, -5.0, -3.0, -5.0, -4.0, -4.0, -4.0, -1.0, -4.0, -2.0, -2.0, -2.0, 0.0, -2.0, -1.0], [3.3125, 4.5, 4.5, 2.125, 2.125, 4.5, 5.0, 5.0, 4.0, 4.0, 2.125, 3.0, 3.0, 1.25, 1.25, 1.25, 2.0, 2.0, 0.5, 0.5, 0.5, 1.0, 1.0, 0.0, 0.0]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"ta01c8b3c7858431e906204b690585c65","edge_data","graph edge data",["source", "target"],[[0, 1, 0, 3, 5, 6, 5, 8, 10, 11, 10, 13, 15, 16, 15, 18, 20, 21, 20, 23], [1, 2, 3, 4, 6, 7, 8, 9, 11, 12, 13, 14, 16, 17, 18, 19, 21, 22, 23, 24]],"toyplot");
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
        })(modules["toyplot/tables"],modules["toyplot/menus/context"],modules["toyplot/io"],"t8aa62b39b49e49fbace0692add4d8ea6","data","scatterplot",["x", "y0"],[[-1.0, 0.0, -1.0, -3.0, 0.0, -2.0, -2.0, -4.0, -5.0, -4.0, -6.0], [0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 0.5, 1.25, 2.125, 4.5, 3.3125]],"toyplot");
})();</script></div></div>

