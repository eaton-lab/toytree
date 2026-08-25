<div class="nb-md-page-hook" aria-hidden="true"></div>

# Tree Drawing basics
Tree visualization is a fundamental feature of `toytree`. Following our minimalist ethos, it is possible to generate a beautiful tree drawing easily, while also being able to create complex and data rich visualizations by using many available styling options.


```python
import numpy as np

import toytree

# an example tree
tree = toytree.rtree.bdtree(ntips=6, seed=123)
```

## Drawing class objects
When you call `.draw()` on a tree it returns three objects, a `Canvas`, a `Cartesian` axes, and a `Mark`. 

This follows the design principle of the `toyplot` plotting library on which toytree is based. The `Canvas` describes the plot space, and the `Cartesian` defines the coordinate space in data units, and `Marks` contain SVG markers/shapes to represent data. One canvas can have multiple cartesian axes, and each cartesian can contain multiple marks.

It is often useful to capture the returned (``Canvas``, ``Cartesian``, ``Mark``) objects as stored variables which allows you to optionally edit them further or save them to a file. If you are working in a jupyter notebook drawings are autorendered as HTML in output cells. This behavior can be toggled in the toyplot [Global config](#global-config).

Throughout this documentation you will see many `toytree` drawing commands end with a semicolon (;), which is a simple method to hide the returned objects from being displayed in the output cell.


```python
# store the returned drawing objects
canvas, axes, mark = tree.draw()
```


<div class="toyplot" id="t47989a3287af44a081bcf8dbd184f2a3" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t6daf436b5f1c4430b768c81de1ed103d"><g class="toyplot-coordinates-Cartesian" id="t732913279aed4598a8a98cc4040e2db8"><clipPath id="t9f489014e3854813b9c08be2183e9d91"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t9f489014e3854813b9c08be2183e9d91)"><g class="toytree-mark-Toytree" id="ta1c4b5ed8bda43de9bc3f452a67177d6"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 66.6 201.8 L 66.6 217.8 L 224.7 217.8" id="6,0" style=""></path><path d="M 66.6 201.8 L 66.6 185.7 L 224.7 185.7" id="6,1" style=""></path><path d="M 164.0 125.4 L 164.0 153.6 L 224.7 153.6" id="9,2" style=""></path><path d="M 168.9 97.3 L 168.9 121.4 L 224.7 121.4" id="8,3" style=""></path><path d="M 191.0 73.2 L 191.0 89.3 L 224.7 89.3" id="7,4" style=""></path><path d="M 191.0 73.2 L 191.0 57.2 L 224.7 57.2" id="7,5" style=""></path><path d="M 51.0 163.6 L 51.0 201.8 L 66.6 201.8" id="10,6" style=""></path><path d="M 168.9 97.3 L 168.9 73.2 L 191.0 73.2" id="8,7" style=""></path><path d="M 164.0 125.4 L 164.0 97.3 L 168.9 97.3" id="9,8" style=""></path><path d="M 51.0 163.6 L 51.0 125.4 L 164.0 125.4" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.728,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.728,185.707)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.728,153.569)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.728,121.431)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.728,89.2931)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.728,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Saving drawings
You can [save/export drawings](drawing-save) in a number of formats to use in professional publications or for further editing in tools like Inkscape or Illustrator. The SVG format output is best for this, while the PDF and PNG are convenient for sharing. The HTML output retains interactive features such as hover tooltip info. To save a drawing pass the canvas and filename to `toytree.save`, the file type is inferred from the suffix.


```python
toytree.save(canvas, "/tmp/drawing.svg")
toytree.save(canvas, "/tmp/drawing.html")
toytree.save(canvas, "/tmp/drawing.pdf")
```

## Tree Styles
A good way to think about ``draw()`` is that ``tree_style`` chooses a starting look, and the other arguments adjust specific parts of that look. The shorter alias ``ts`` is convenient when you are experimenting in a notebook. Built-in styles include ``n``, ``s``, ``p``, ``o``, ``c``, ``d``, ``b``, ``u`` and ``r``. See [Tree Styles](drawing-tree-styles). 


```python
# drawing with pre-built 'c' (coalescent) style
tree.draw(tree_style="c")

# drawing with 'c' style and additional modifications applied on top
tree.draw(
    tree_style="c", node_markers="s", node_sizes=10, node_colors="salmon", height=250
);
```


<div class="toyplot" id="t46c6702c451c43b1abfe2fa9ad8e7de1" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="300.0px" viewBox="0 0 300.0 300.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t824e144d4fbb46ce944a4acac0835897"><g class="toyplot-coordinates-Cartesian" id="td5708c85597f4be5a2193c2601c60f18"><clipPath id="t0e19b9f20a6a43e88509447a5a900013"><rect x="34.965349652427065" y="50.0" width="200.0" height="200.0"></rect></clipPath><g clip-path="url(#t0e19b9f20a6a43e88509447a5a900013)"></g><g class="toyplot-coordinates-Axis" id="t5891fb319432475ab71e107626a7d432" transform="translate(34.965349652427065,250.0)rotate(-90.0)"><line x1="22.293203075840925" y1="0" x2="195.08267092909804" y2="0" style=""></line><g><line x1="22.293203075840925" y1="0" x2="22.293203075840925" y2="5.0" style=""></line><line x1="71.73141036404398" y1="0" x2="71.73141036404398" y2="5.0" style=""></line><line x1="121.16961765224703" y1="0" x2="121.16961765224703" y2="5.0" style=""></line><line x1="170.6078249404501" y1="0" x2="170.6078249404501" y2="5.0" style=""></line></g><g><g transform="translate(22.293203075840925,-6.0)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(71.73141036404398,-6.0)"><text x="-6.95" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.4</text></g><g transform="translate(121.16961765224703,-6.0)"><text x="-6.95" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.8</text></g><g transform="translate(170.6078249404501,-6.0)"><text x="-6.95" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1.2</text></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t004766f42b2044a88914ab621606ef52"><clipPath id="ta25f80306b294b8599f4b4f0450c7a54"><rect x="35.0" y="35.0" width="230.0" height="230.0"></rect></clipPath><g clip-path="url(#ta25f80306b294b8599f4b4f0450c7a54)"><g class="toytree-mark-Toytree" id="tb63237536a4141178431a60e09d043e5"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 75.7 70.5 L 57.2 227.7" id="6,0" style=""></path><path d="M 75.7 70.5 L 94.3 227.7" id="6,1" style=""></path><path d="M 163.9 167.4 L 131.4 227.7" id="9,2" style=""></path><path d="M 196.4 172.1 L 168.6 227.7" id="8,3" style=""></path><path d="M 224.3 194.1 L 205.7 227.7" id="7,4" style=""></path><path d="M 224.3 194.1 L 242.8 227.7" id="7,5" style=""></path><path d="M 119.8 54.9 L 75.7 70.5" id="10,6" style=""></path><path d="M 196.4 172.1 L 224.3 194.1" id="8,7" style=""></path><path d="M 163.9 167.4 L 196.4 172.1" id="9,8" style=""></path><path d="M 119.8 54.9 L 163.9 167.4" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(57.1653,227.707)"><circle r="3.5"></circle></g><g id="Node-1" transform="translate(94.2992,227.707)"><circle r="3.5"></circle></g><g id="Node-2" transform="translate(131.433,227.707)"><circle r="3.5"></circle></g><g id="Node-3" transform="translate(168.567,227.707)"><circle r="3.5"></circle></g><g id="Node-4" transform="translate(205.701,227.707)"><circle r="3.5"></circle></g><g id="Node-5" transform="translate(242.835,227.707)"><circle r="3.5"></circle></g><g id="Node-6" transform="translate(75.7323,70.4777)"><circle r="3.5"></circle></g><g id="Node-7" transform="translate(224.268,194.123)"><circle r="3.5"></circle></g><g id="Node-8" transform="translate(196.417,172.139)"><circle r="3.5"></circle></g><g id="Node-9" transform="translate(163.925,167.361)"><circle r="3.5"></circle></g><g id="Node-10" transform="translate(119.829,54.9173)"><circle r="3.5"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(57.1653,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(94.2992,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(131.433,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(168.567,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(205.701,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(242.835,227.707)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t824e144d4fbb46ce944a4acac0835897";
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
        })(modules["toyplot.coordinates.Axis"],"t5891fb319432475ab71e107626a7d432",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 1.4378093921424493, "min": -0.18037226103997936}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>



<div class="toyplot" id="t55fa1c35aa6e45b29a04500bfde7ae48" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="250.0px" viewBox="0 0 300.0 250.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="td7670129d8834ea898d6c8d6c59f5ab1"><g class="toyplot-coordinates-Cartesian" id="t5e425c844afb4f08b0639eb9a6d81363"><clipPath id="tb17d78b88d1347ae8835db9219421313"><rect x="34.99750603914086" y="50.0" width="200.0" height="150.0"></rect></clipPath><g clip-path="url(#tb17d78b88d1347ae8835db9219421313)"></g><g class="toyplot-coordinates-Axis" id="t29cea5d7f4264481b29dba01c864c490" transform="translate(34.99750603914086,200.0)rotate(-90.0)"><line x1="22.533546700425404" y1="0" x2="143.53855419301374" y2="0" style=""></line><g><line x1="22.533546700425404" y1="0" x2="22.533546700425404" y2="5.0" style=""></line><line x1="57.15527867085799" y1="0" x2="57.15527867085799" y2="5.0" style=""></line><line x1="91.77701064129056" y1="0" x2="91.77701064129056" y2="5.0" style=""></line><line x1="126.39874261172318" y1="0" x2="126.39874261172318" y2="5.0" style=""></line></g><g><g transform="translate(22.533546700425404,-6.0)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(57.15527867085799,-6.0)"><text x="-6.95" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.4</text></g><g transform="translate(91.77701064129056,-6.0)"><text x="-6.95" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.8</text></g><g transform="translate(126.39874261172318,-6.0)"><text x="-6.95" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1.2</text></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t41ea9b9f81fd46dd86ff3d778cadd2b1"><clipPath id="t2d191d405d11498fb9b7b0c03263d974"><rect x="35.0" y="35.0" width="230.0" height="180.0"></rect></clipPath><g clip-path="url(#t2d191d405d11498fb9b7b0c03263d974)"><g class="toytree-mark-Toytree" id="t2f2d101c370e4fddbcfa119c5baf7569"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2;fill:none"><path d="M 75.8 67.4 L 57.2 177.5" id="6,0" style=""></path><path d="M 75.8 67.4 L 94.3 177.5" id="6,1" style=""></path><path d="M 163.9 135.2 L 131.4 177.5" id="9,2" style=""></path><path d="M 196.4 138.6 L 168.6 177.5" id="8,3" style=""></path><path d="M 224.2 153.9 L 205.7 177.5" id="7,4" style=""></path><path d="M 224.2 153.9 L 242.8 177.5" id="7,5" style=""></path><path d="M 119.8 56.5 L 75.8 67.4" id="10,6" style=""></path><path d="M 196.4 138.6 L 224.2 153.9" id="8,7" style=""></path><path d="M 163.9 135.2 L 196.4 138.6" id="9,8" style=""></path><path d="M 119.8 56.5 L 163.9 135.2" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(98.0%,50.2%,44.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(57.1975,177.466)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g><g id="Node-1" transform="translate(94.3185,177.466)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g><g id="Node-2" transform="translate(131.44,177.466)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g><g id="Node-3" transform="translate(168.56,177.466)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g><g id="Node-4" transform="translate(205.681,177.466)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g><g id="Node-5" transform="translate(242.802,177.466)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g><g id="Node-6" transform="translate(75.758,67.3584)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g><g id="Node-7" transform="translate(224.242,153.948)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g><g id="Node-8" transform="translate(196.401,138.552)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g><g id="Node-9" transform="translate(163.92,135.206)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g><g id="Node-10" transform="translate(119.839,56.4614)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(57.1975,177.466)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(94.3185,177.466)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(131.44,177.466)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(168.56,177.466)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(205.681,177.466)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(242.802,177.466)rotate(90)"><text x="12.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "td7670129d8834ea898d6c8d6c59f5ab1";
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
        })(modules["toyplot.coordinates.Axis"],"t29cea5d7f4264481b29dba01c864c490",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 1.4726756409348052, "min": -0.26033991274231283}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 150.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


## Drawing nodes and edges

Plotting node values is a useful way of representing data stored to a tree (see [Data/Features](core-feature-data)). The ``draw()`` command includes many options to apply styles to nodes or edges. These should be considered *convenience* options, as they provide only a subset of the styling options that can be accomplished using the [annotation](anno-introduction)`. 

Nodes are often used to show labels, support values, or trait data. They can convey information through variation in their marker shapes (e.g., circles, rectangles, pie-charts), colors, and sizes. Node markers in `toytree` are represented by SVG shape objects for which a fill (color), fill-opacity, stroke (outline color), stroke-opacity, and stroke-width can be set. Node labels can be added on top of nodes as formatted strings, and hover tooltip info can be added to display in the HTML/notebook rendering.


```python
# hover over nodes to see pop-up elements
tree.draw(
    node_sizes=18,
    node_style={"fill-opacity": 0.75, "stroke": "white", "stroke-width": 2.5},
    node_labels="idx",
    node_labels_style={"font-size": 14, "fill": "white"},
    node_colors=("idx", "BlueRed", 6, 9),
    node_markers="s",
    node_mask=False,
    node_hover=True,
);
```


<div class="toyplot" id="tf282fb0afd114570899d18f18593d9d6" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t031be4aa946849a3b3be4a5bcb13ae94"><g class="toyplot-coordinates-Cartesian" id="tb383eec323ad41ef84dddf2324e53cc7"><clipPath id="t9f5ef027e6bb48199d49a4a2762cdced"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t9f5ef027e6bb48199d49a4a2762cdced)"><g class="toytree-mark-Toytree" id="td447b53070de46898334e43a3a3be850"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 76.1 198.3 L 76.1 213.5 L 224.5 213.5" id="6,0" style=""></path><path d="M 76.1 198.3 L 76.1 183.1 L 224.5 183.1" id="6,1" style=""></path><path d="M 167.5 126.1 L 167.5 152.7 L 224.5 152.7" id="9,2" style=""></path><path d="M 172.0 99.5 L 172.0 122.3 L 224.5 122.3" id="8,3" style=""></path><path d="M 192.8 76.7 L 192.8 91.9 L 224.5 91.9" id="7,4" style=""></path><path d="M 192.8 76.7 L 192.8 61.5 L 224.5 61.5" id="7,5" style=""></path><path d="M 61.4 162.2 L 61.4 198.3 L 76.1 198.3" id="10,6" style=""></path><path d="M 172.0 99.5 L 172.0 76.7 L 192.8 76.7" id="8,7" style=""></path><path d="M 167.5 126.1 L 167.5 99.5 L 172.0 99.5" id="9,8" style=""></path><path d="M 61.4 162.2 L 61.4 126.1 L 167.5 126.1" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:0.75;stroke:rgb(100.0%,100.0%,100.0%);stroke-opacity:1.0;stroke-width:2.5"><g id="Node-0" style="fill:rgb(2.0%,18.8%,38.0%)" transform="translate(224.466,213.523)"><rect x="-9.0" y="-9.0" width="18" height="18"></rect></g><g id="Node-1" style="fill:rgb(2.0%,18.8%,38.0%)" transform="translate(224.466,183.114)"><rect x="-9.0" y="-9.0" width="18" height="18"></rect></g><g id="Node-2" style="fill:rgb(2.0%,18.8%,38.0%)" transform="translate(224.466,152.705)"><rect x="-9.0" y="-9.0" width="18" height="18"></rect></g><g id="Node-3" style="fill:rgb(2.0%,18.8%,38.0%)" transform="translate(224.466,122.295)"><rect x="-9.0" y="-9.0" width="18" height="18"></rect></g><g id="Node-4" style="fill:rgb(2.0%,18.8%,38.0%)" transform="translate(224.466,91.8864)"><rect x="-9.0" y="-9.0" width="18" height="18"></rect></g><g id="Node-5" style="fill:rgb(2.0%,18.8%,38.0%)" transform="translate(224.466,61.4773)"><rect x="-9.0" y="-9.0" width="18" height="18"></rect></g><g id="Node-6" style="fill:rgb(2.0%,18.8%,38.0%)" transform="translate(76.121,198.318)"><rect x="-9.0" y="-9.0" width="18" height="18"></rect></g><g id="Node-7" style="fill:rgb(65.5%,81.4%,89.4%)" transform="translate(192.78,76.6819)"><rect x="-9.0" y="-9.0" width="18" height="18"></rect></g><g id="Node-8" style="fill:rgb(96.9%,71.8%,60.0%)" transform="translate(172.038,99.4887)"><rect x="-9.0" y="-9.0" width="18" height="18"></rect></g><g id="Node-9" style="fill:rgb(40.4%,0.0%,12.2%)" transform="translate(167.53,126.097)"><rect x="-9.0" y="-9.0" width="18" height="18"></rect></g><g id="Node-10" style="fill:rgb(40.4%,0.0%,12.2%)" transform="translate(61.4398,162.207)"><rect x="-9.0" y="-9.0" width="18" height="18"></rect></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:14px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(224.466,213.523)"><title>idx: 0
dist: 1.27212638397
support: nan
height: 0
name: r0</title><text x="-3.892000000000001" y="3.577" style="fill:rgb(100.0%,100.0%,100.0%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(224.466,183.114)"><title>idx: 1
dist: 1.27212638397
support: nan
height: 0
name: r1</title><text x="-3.892000000000001" y="3.577" style="fill:rgb(100.0%,100.0%,100.0%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(224.466,152.705)"><title>idx: 2
dist: 0.488252765456
support: nan
height: 0
name: r2</title><text x="-3.892000000000001" y="3.577" style="fill:rgb(100.0%,100.0%,100.0%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(224.466,122.295)"><title>idx: 3
dist: 0.44959453852
support: nan
height: 0
name: r3</title><text x="-3.892000000000001" y="3.577" style="fill:rgb(100.0%,100.0%,100.0%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(224.466,91.8864)"><title>idx: 4
dist: 0.271721229346
support: nan
height: 0
name: r4</title><text x="-3.892000000000001" y="3.577" style="fill:rgb(100.0%,100.0%,100.0%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(224.466,61.4773)"><title>idx: 5
dist: 0.271721229346
support: nan
height: 0
name: r5</title><text x="-3.892000000000001" y="3.577" style="fill:rgb(100.0%,100.0%,100.0%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(76.121,198.318)"><title>idx: 6
dist: 0.125897349747
support: nan
height: 1.27212638397
name: </title><text x="-3.892000000000001" y="3.577" style="fill:rgb(100.0%,100.0%,100.0%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(192.78,76.6819)"><title>idx: 7
dist: 0.177873309174
support: nan
height: 0.271721229346
name: </title><text x="-3.892000000000001" y="3.577" style="fill:rgb(100.0%,100.0%,100.0%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(172.038,99.4887)"><title>idx: 8
dist: 0.0386582269365
support: nan
height: 0.44959453852
name: </title><text x="-3.892000000000001" y="3.577" style="fill:rgb(100.0%,100.0%,100.0%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(167.53,126.097)"><title>idx: 9
dist: 0.90977096826
support: nan
height: 0.488252765456
name: </title><text x="-3.892000000000001" y="3.577" style="fill:rgb(100.0%,100.0%,100.0%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(61.4398,162.207)"><title>idx: 10
dist: 0.596972495123
support: nan
height: 1.39802373372
name: </title><text x="-7.784000000000002" y="3.577" style="fill:rgb(100.0%,100.0%,100.0%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(224.466,213.523)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(224.466,183.114)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(224.466,152.705)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(224.466,122.295)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(224.466,91.8864)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(224.466,61.4773)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>





```python

```


<div class="toyplot" id="t864b43b9b7cf4855beb1c9da9ed213dc" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="teca6b352806c443282a91515c36283e7"><g class="toyplot-coordinates-Cartesian" id="ta569a51bd06242e4b12000529071c6c3"><clipPath id="t1922008aed2d4c6583e64f05360d5426"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t1922008aed2d4c6583e64f05360d5426)"><g class="toytree-mark-Toytree" id="tdaaa6fd0377943e5a9b6733ed1010adf"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 109.3 202.0 L 109.3 218.1 L 210.3 218.1" id="6,0" style=""></path><path d="M 109.3 202.0 L 109.3 185.9 L 210.3 185.9" id="6,1" style=""></path><path d="M 120.6 125.4 L 120.6 153.6 L 210.3 153.6" id="9,2" style=""></path><path d="M 190.9 97.2 L 190.9 121.4 L 210.3 121.4" id="8,3" style=""></path><path d="M 194.4 73.0 L 194.4 89.1 L 210.3 89.1" id="7,4" style=""></path><path d="M 194.4 73.0 L 194.4 56.9 L 210.3 56.9" id="7,5" style=""></path><path d="M 55.8 163.7 L 55.8 202.0 L 109.3 202.0" id="10,6" style=""></path><path d="M 190.9 97.2 L 190.9 73.0 L 194.4 73.0" id="8,7" style=""></path><path d="M 120.6 125.4 L 120.6 97.2 L 190.9 97.2" id="9,8" style=""></path><path d="M 55.8 163.7 L 55.8 125.4 L 120.6 125.4" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(210.333,218.092)"><circle r="6.0"></circle></g><g id="Node-1" transform="translate(210.333,185.855)"><circle r="6.0"></circle></g><g id="Node-2" transform="translate(210.333,153.618)"><circle r="6.0"></circle></g><g id="Node-3" transform="translate(210.333,121.382)"><circle r="6.0"></circle></g><g id="Node-4" transform="translate(210.333,89.1447)"><circle r="6.0"></circle></g><g id="Node-5" transform="translate(210.333,56.9079)"><circle r="6.0"></circle></g><g id="Node-6" transform="translate(109.33,201.974)"><circle r="6.0"></circle></g><g id="Node-7" transform="translate(194.382,73.0263)"><circle r="6.0"></circle></g><g id="Node-8" transform="translate(190.915,97.2039)"><circle r="6.0"></circle></g><g id="Node-9" transform="translate(120.62,125.411)"><circle r="6.0"></circle></g><g id="Node-10" transform="translate(55.7952,163.692)"><circle r="6.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(210.333,218.092)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r0</text></g><g class="toytree-TipLabel" transform="translate(210.333,185.855)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r1</text></g><g class="toytree-TipLabel" transform="translate(210.333,153.618)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r2</text></g><g class="toytree-TipLabel" transform="translate(210.333,121.382)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r3</text></g><g class="toytree-TipLabel" transform="translate(210.333,89.1447)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r4</text></g><g class="toytree-TipLabel" transform="translate(210.333,56.9079)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# mask=True masks all nodes
tree.draw(node_mask=True, node_sizes=12);
```


<div class="toyplot" id="t66bb77e3bad542eba3b68d9e79c62558" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="teb935070ab914115b43de8dc905767fd"><g class="toyplot-coordinates-Cartesian" id="t0b59dd78afbc49ec99b3dc7799f679d2"><clipPath id="t51b210f8b06d4b9eb757907983323e82"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t51b210f8b06d4b9eb757907983323e82)"><g class="toytree-mark-Toytree" id="t00c815dbefc446f1a5e36e2350383cd2"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 109.3 202.0 L 109.3 218.1 L 210.3 218.1" id="6,0" style=""></path><path d="M 109.3 202.0 L 109.3 185.9 L 210.3 185.9" id="6,1" style=""></path><path d="M 120.6 125.4 L 120.6 153.6 L 210.3 153.6" id="9,2" style=""></path><path d="M 190.9 97.2 L 190.9 121.4 L 210.3 121.4" id="8,3" style=""></path><path d="M 194.4 73.0 L 194.4 89.1 L 210.3 89.1" id="7,4" style=""></path><path d="M 194.4 73.0 L 194.4 56.9 L 210.3 56.9" id="7,5" style=""></path><path d="M 55.8 163.7 L 55.8 202.0 L 109.3 202.0" id="10,6" style=""></path><path d="M 190.9 97.2 L 190.9 73.0 L 194.4 73.0" id="8,7" style=""></path><path d="M 120.6 125.4 L 120.6 97.2 L 190.9 97.2" id="9,8" style=""></path><path d="M 55.8 163.7 L 55.8 125.4 L 120.6 125.4" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(210.333,218.092)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r0</text></g><g class="toytree-TipLabel" transform="translate(210.333,185.855)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r1</text></g><g class="toytree-TipLabel" transform="translate(210.333,153.618)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r2</text></g><g class="toytree-TipLabel" transform="translate(210.333,121.382)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r3</text></g><g class="toytree-TipLabel" transform="translate(210.333,89.1447)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r4</text></g><g class="toytree-TipLabel" transform="translate(210.333,56.9079)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# mask=[True, False, True, ...] shows Nodes with True
mask = tree.get_node_mask(show_tips=True, show_root=True, show_internal=False)
print(mask)
tree.draw(node_mask=mask, node_sizes=12);
```

    [ True  True  True  True  True  True False False False False  True]



<div class="toyplot" id="t52f94336cbb04f43b2a546e81fc19adb" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t21bc8f3638e04c37acc64234528ec301"><g class="toyplot-coordinates-Cartesian" id="tc6eb318810584329a0f92803dafbaf08"><clipPath id="tad0286edddd7414d8002b02cc4ba8816"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tad0286edddd7414d8002b02cc4ba8816)"><g class="toytree-mark-Toytree" id="t3b92e468b15d42cfbfbda60885770003"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 109.3 202.0 L 109.3 218.1 L 210.3 218.1" id="6,0" style=""></path><path d="M 109.3 202.0 L 109.3 185.9 L 210.3 185.9" id="6,1" style=""></path><path d="M 120.6 125.4 L 120.6 153.6 L 210.3 153.6" id="9,2" style=""></path><path d="M 190.9 97.2 L 190.9 121.4 L 210.3 121.4" id="8,3" style=""></path><path d="M 194.4 73.0 L 194.4 89.1 L 210.3 89.1" id="7,4" style=""></path><path d="M 194.4 73.0 L 194.4 56.9 L 210.3 56.9" id="7,5" style=""></path><path d="M 55.8 163.7 L 55.8 202.0 L 109.3 202.0" id="10,6" style=""></path><path d="M 190.9 97.2 L 190.9 73.0 L 194.4 73.0" id="8,7" style=""></path><path d="M 120.6 125.4 L 120.6 97.2 L 190.9 97.2" id="9,8" style=""></path><path d="M 55.8 163.7 L 55.8 125.4 L 120.6 125.4" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(210.333,218.092)"><circle r="6.0"></circle></g><g id="Node-1" transform="translate(210.333,185.855)"><circle r="6.0"></circle></g><g id="Node-2" transform="translate(210.333,153.618)"><circle r="6.0"></circle></g><g id="Node-3" transform="translate(210.333,121.382)"><circle r="6.0"></circle></g><g id="Node-4" transform="translate(210.333,89.1447)"><circle r="6.0"></circle></g><g id="Node-5" transform="translate(210.333,56.9079)"><circle r="6.0"></circle></g><g id="Node-10" transform="translate(55.7952,163.692)"><circle r="6.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(210.333,218.092)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r0</text></g><g class="toytree-TipLabel" transform="translate(210.333,185.855)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r1</text></g><g class="toytree-TipLabel" transform="translate(210.333,153.618)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r2</text></g><g class="toytree-TipLabel" transform="translate(210.333,121.382)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r3</text></g><g class="toytree-TipLabel" transform="translate(210.333,89.1447)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r4</text></g><g class="toytree-TipLabel" transform="translate(210.333,56.9079)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# mask=[True, False, True, ...] shows Nodes with True
mask = tree.get_node_mask("~r[0-5]")
print(mask)
tree.draw(node_mask=mask, node_sizes=12);
```

    [ True  True  True  True  True  True False False False False False]



<div class="toyplot" id="te57e411ae04d410c91cf083b32ec7bd3" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tb6f90d6848964ce4b7f4d5ee2108a4a5"><g class="toyplot-coordinates-Cartesian" id="tbeeef1c88cc94aa99cd37271e4ea15a9"><clipPath id="t1aeedaf4a2a44809b740a778e9680d0b"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t1aeedaf4a2a44809b740a778e9680d0b)"><g class="toytree-mark-Toytree" id="t289e5e527cf64f7bad82e5b498584e14"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 109.3 202.0 L 109.3 218.1 L 210.3 218.1" id="6,0" style=""></path><path d="M 109.3 202.0 L 109.3 185.9 L 210.3 185.9" id="6,1" style=""></path><path d="M 120.6 125.4 L 120.6 153.6 L 210.3 153.6" id="9,2" style=""></path><path d="M 190.9 97.2 L 190.9 121.4 L 210.3 121.4" id="8,3" style=""></path><path d="M 194.4 73.0 L 194.4 89.1 L 210.3 89.1" id="7,4" style=""></path><path d="M 194.4 73.0 L 194.4 56.9 L 210.3 56.9" id="7,5" style=""></path><path d="M 55.8 163.7 L 55.8 202.0 L 109.3 202.0" id="10,6" style=""></path><path d="M 190.9 97.2 L 190.9 73.0 L 194.4 73.0" id="8,7" style=""></path><path d="M 120.6 125.4 L 120.6 97.2 L 190.9 97.2" id="9,8" style=""></path><path d="M 55.8 163.7 L 55.8 125.4 L 120.6 125.4" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(210.333,218.092)"><circle r="6.0"></circle></g><g id="Node-1" transform="translate(210.333,185.855)"><circle r="6.0"></circle></g><g id="Node-2" transform="translate(210.333,153.618)"><circle r="6.0"></circle></g><g id="Node-3" transform="translate(210.333,121.382)"><circle r="6.0"></circle></g><g id="Node-4" transform="translate(210.333,89.1447)"><circle r="6.0"></circle></g><g id="Node-5" transform="translate(210.333,56.9079)"><circle r="6.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(210.333,218.092)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r0</text></g><g class="toytree-TipLabel" transform="translate(210.333,185.855)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r1</text></g><g class="toytree-TipLabel" transform="translate(210.333,153.618)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r2</text></g><g class="toytree-TipLabel" transform="translate(210.333,121.382)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r3</text></g><g class="toytree-TipLabel" transform="translate(210.333,89.1447)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r4</text></g><g class="toytree-TipLabel" transform="translate(210.333,56.9079)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# mask=[True, False, True, ...] shows a subset of Nodes
mask = tree.get_node_mask(2, 3, 7, 8)
print(mask)
tree.draw(node_mask=mask, node_sizes=15, node_labels="idx");
```


<div class="toyplot" id="t459da7dbaa424ce6b30665c40d8c4c39" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t201bf63172df43cd8c48a11482ea2174"><g class="toyplot-coordinates-Cartesian" id="tb1734c79ee2c438392327019a2894e28"><clipPath id="t28e602472bf6445ea7190a99129f242d"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t28e602472bf6445ea7190a99129f242d)"><g class="toytree-mark-Toytree" id="tff4499fd837b423e81356d396c8e0ef9"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 110.1 201.0 L 110.1 216.8 L 210.6 216.8" id="6,0" style=""></path><path d="M 110.1 201.0 L 110.1 185.1 L 210.6 185.1" id="6,1" style=""></path><path d="M 121.4 125.6 L 121.4 153.4 L 210.6 153.4" id="9,2" style=""></path><path d="M 191.3 97.8 L 191.3 121.6 L 210.6 121.6" id="8,3" style=""></path><path d="M 194.7 74.0 L 194.7 89.9 L 210.6 89.9" id="7,4" style=""></path><path d="M 194.7 74.0 L 194.7 58.2 L 210.6 58.2" id="7,5" style=""></path><path d="M 56.9 163.3 L 56.9 201.0 L 110.1 201.0" id="10,6" style=""></path><path d="M 191.3 97.8 L 191.3 74.0 L 194.7 74.0" id="8,7" style=""></path><path d="M 121.4 125.6 L 121.4 97.8 L 191.3 97.8" id="9,8" style=""></path><path d="M 56.9 163.3 L 56.9 125.6 L 121.4 125.6" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-2" transform="translate(210.562,153.368)"><circle r="7.5"></circle></g><g id="Node-3" transform="translate(210.562,121.632)"><circle r="7.5"></circle></g><g id="Node-7" transform="translate(194.703,74.0285)"><circle r="7.5"></circle></g><g id="Node-8" transform="translate(191.256,97.8303)"><circle r="7.5"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(210.562,153.368)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">2</text></g><g class="toytree-NodeLabel" transform="translate(210.562,121.632)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">3</text></g><g class="toytree-NodeLabel" transform="translate(194.703,74.0285)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">7</text></g><g class="toytree-NodeLabel" transform="translate(191.256,97.8303)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">8</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(210.562,216.839)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r0</text></g><g class="toytree-TipLabel" transform="translate(210.562,185.104)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r1</text></g><g class="toytree-TipLabel" transform="translate(210.562,153.368)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r2</text></g><g class="toytree-TipLabel" transform="translate(210.562,121.632)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r3</text></g><g class="toytree-TipLabel" transform="translate(210.562,89.8964)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r4</text></g><g class="toytree-TipLabel" transform="translate(210.562,58.1606)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


### node_markers
Node markers are the shapes of the mark objects plotted on nodes. The default shape is a circle, but a variety of marker shapes are available and can be selected by the shorthand str names used for [toyplot markers](https://toyplot.readthedocs.io/en/stable/markers.html). For example, 's' for a square, 'o' for a circle, 'r1x5' for a rectangle that is 5 times taller than wide. Each marker shape is still scaled to a particular pixel size using the `node_sizes` argument, and optionally shown or hidden using `node_mask`. You can enter a single node marker argument to apply to all nodes uniformly, or a series of node markers of length nnodes to apply different markers shapes to different nodes.


```python
# apply square markers to all nodes
tree.draw(node_sizes=10, node_markers="s");
```


<div class="toyplot" id="t54d8507ea0f14d8283b522308c7bad44" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="td10016f7de4f46b592a00175b620889b"><g class="toyplot-coordinates-Cartesian" id="t7bfe9a1af9d1460fa0363bbb7218c861"><clipPath id="td38f6e6aeb3d4737a389a820f3423d33"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#td38f6e6aeb3d4737a389a820f3423d33)"><g class="toytree-mark-Toytree" id="t7c1ffcfa4c144ddbae2cb268692aac21"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 108.8 202.2 L 108.8 218.3 L 210.2 218.3" id="6,0" style=""></path><path d="M 108.8 202.2 L 108.8 186.0 L 210.2 186.0" id="6,1" style=""></path><path d="M 120.1 125.4 L 120.1 153.7 L 210.2 153.7" id="9,2" style=""></path><path d="M 190.7 97.1 L 190.7 121.3 L 210.2 121.3" id="8,3" style=""></path><path d="M 194.2 72.8 L 194.2 89.0 L 210.2 89.0" id="7,4" style=""></path><path d="M 194.2 72.8 L 194.2 56.7 L 210.2 56.7" id="7,5" style=""></path><path d="M 55.0 163.8 L 55.0 202.2 L 108.8 202.2" id="10,6" style=""></path><path d="M 190.7 97.1 L 190.7 72.8 L 194.2 72.8" id="8,7" style=""></path><path d="M 120.1 125.4 L 120.1 97.1 L 190.7 97.1" id="9,8" style=""></path><path d="M 55.0 163.8 L 55.0 125.4 L 120.1 125.4" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-6" transform="translate(108.784,202.178)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g><g id="Node-7" transform="translate(194.166,72.8221)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g><g id="Node-8" transform="translate(190.686,97.0763)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g><g id="Node-9" transform="translate(120.118,125.373)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g><g id="Node-10" transform="translate(55.042,163.775)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(210.179,218.347)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r0</text></g><g class="toytree-TipLabel" transform="translate(210.179,186.008)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r1</text></g><g class="toytree-TipLabel" transform="translate(210.179,153.669)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r2</text></g><g class="toytree-TipLabel" transform="translate(210.179,121.331)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r3</text></g><g class="toytree-TipLabel" transform="translate(210.179,88.9916)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r4</text></g><g class="toytree-TipLabel" transform="translate(210.179,56.6526)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# apply rectangle markers to each node
tree.draw(node_sizes=15, node_markers="r2x1");
```


<div class="toyplot" id="t0d211d3e482146299953a9fae97bf008" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t45888802714d4a9da23eb2300046ef2b"><g class="toyplot-coordinates-Cartesian" id="t0143f1189ec24380957360266d436a42"><clipPath id="t6210139cb8ed4072be77330204cc8191"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t6210139cb8ed4072be77330204cc8191)"><g class="toytree-mark-Toytree" id="tdcf26df3f7f248888ef7cd75a17f5243"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 114.1 201.0 L 114.1 216.8 L 211.7 216.8" id="6,0" style=""></path><path d="M 114.1 201.0 L 114.1 185.1 L 211.7 185.1" id="6,1" style=""></path><path d="M 125.0 125.6 L 125.0 153.4 L 211.7 153.4" id="9,2" style=""></path><path d="M 192.9 97.8 L 192.9 121.6 L 211.7 121.6" id="8,3" style=""></path><path d="M 196.3 74.0 L 196.3 89.9 L 211.7 89.9" id="7,4" style=""></path><path d="M 196.3 74.0 L 196.3 58.2 L 211.7 58.2" id="7,5" style=""></path><path d="M 62.3 163.3 L 62.3 201.0 L 114.1 201.0" id="10,6" style=""></path><path d="M 192.9 97.8 L 192.9 74.0 L 196.3 74.0" id="8,7" style=""></path><path d="M 125.0 125.6 L 125.0 97.8 L 192.9 97.8" id="9,8" style=""></path><path d="M 62.3 163.3 L 62.3 125.6 L 125.0 125.6" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-6" transform="translate(114.057,200.972)"><rect x="-15.0" y="-7.5" width="30.0" height="15.0"></rect></g><g id="Node-7" transform="translate(196.251,74.0285)"><rect x="-15.0" y="-7.5" width="30.0" height="15.0"></rect></g><g id="Node-8" transform="translate(192.901,97.8303)"><rect x="-15.0" y="-7.5" width="30.0" height="15.0"></rect></g><g id="Node-9" transform="translate(124.967,125.599)"><rect x="-15.0" y="-7.5" width="30.0" height="15.0"></rect></g><g id="Node-10" transform="translate(62.321,163.285)"><rect x="-15.0" y="-7.5" width="30.0" height="15.0"></rect></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(211.666,216.839)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r0</text></g><g class="toytree-TipLabel" transform="translate(211.666,185.104)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r1</text></g><g class="toytree-TipLabel" transform="translate(211.666,153.368)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r2</text></g><g class="toytree-TipLabel" transform="translate(211.666,121.632)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r3</text></g><g class="toytree-TipLabel" transform="translate(211.666,89.8964)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r4</text></g><g class="toytree-TipLabel" transform="translate(211.666,58.1606)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# apply a rectangle marker with width scaled to n digits in data
rects = [f"r{len(str(i))}x1" for i in tree.get_node_data("idx")]
tree.draw(node_sizes=15, node_markers=rects, node_labels="idx");
```


<div class="toyplot" id="t6c44d4f91fb84b37892168727e65403b" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="ta4ac72b7bbda48ecb0fba04558155dab"><g class="toyplot-coordinates-Cartesian" id="tb185db3756fe4cc58525e7c294193b5a"><clipPath id="t850b734694304df4b1240cdfdb01a526"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t850b734694304df4b1240cdfdb01a526)"><g class="toytree-mark-Toytree" id="t2da2149a95964d158698266599ee4894"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 114.1 201.0 L 114.1 216.8 L 211.7 216.8" id="6,0" style=""></path><path d="M 114.1 201.0 L 114.1 185.1 L 211.7 185.1" id="6,1" style=""></path><path d="M 125.0 125.6 L 125.0 153.4 L 211.7 153.4" id="9,2" style=""></path><path d="M 192.9 97.8 L 192.9 121.6 L 211.7 121.6" id="8,3" style=""></path><path d="M 196.3 74.0 L 196.3 89.9 L 211.7 89.9" id="7,4" style=""></path><path d="M 196.3 74.0 L 196.3 58.2 L 211.7 58.2" id="7,5" style=""></path><path d="M 62.3 163.3 L 62.3 201.0 L 114.1 201.0" id="10,6" style=""></path><path d="M 192.9 97.8 L 192.9 74.0 L 196.3 74.0" id="8,7" style=""></path><path d="M 125.0 125.6 L 125.0 97.8 L 192.9 97.8" id="9,8" style=""></path><path d="M 62.3 163.3 L 62.3 125.6 L 125.0 125.6" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-6" transform="translate(114.057,200.972)"><rect x="-7.5" y="-7.5" width="15.0" height="15.0"></rect></g><g id="Node-7" transform="translate(196.251,74.0285)"><rect x="-7.5" y="-7.5" width="15.0" height="15.0"></rect></g><g id="Node-8" transform="translate(192.901,97.8303)"><rect x="-7.5" y="-7.5" width="15.0" height="15.0"></rect></g><g id="Node-9" transform="translate(124.967,125.599)"><rect x="-7.5" y="-7.5" width="15.0" height="15.0"></rect></g><g id="Node-10" transform="translate(62.321,163.285)"><rect x="-15.0" y="-7.5" width="30.0" height="15.0"></rect></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(114.057,200.972)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">6</text></g><g class="toytree-NodeLabel" transform="translate(196.251,74.0285)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">7</text></g><g class="toytree-NodeLabel" transform="translate(192.901,97.8303)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">8</text></g><g class="toytree-NodeLabel" transform="translate(124.967,125.599)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">9</text></g><g class="toytree-NodeLabel" transform="translate(62.321,163.285)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">10</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(211.666,216.839)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r0</text></g><g class="toytree-TipLabel" transform="translate(211.666,185.104)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r1</text></g><g class="toytree-TipLabel" transform="translate(211.666,153.368)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r2</text></g><g class="toytree-TipLabel" transform="translate(211.666,121.632)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r3</text></g><g class="toytree-TipLabel" transform="translate(211.666,89.8964)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r4</text></g><g class="toytree-TipLabel" transform="translate(211.666,58.1606)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# show
tree = tree.set_node_data("support", default=100)
tree[-1].support = np.nan
tree.draw(node_labels="support", node_sizes=18, node_markers="r2x1");
```


<div class="toyplot" id="t7c97392d65d54e2388ad007294424d8f" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tcf1b5d5874bb48a9b218788d3c8d9f09"><g class="toyplot-coordinates-Cartesian" id="tc75017ddb0554744a5a336376fd20c2b"><clipPath id="t1025cb69f58343c695473a913b1cc791"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t1025cb69f58343c695473a913b1cc791)"><g class="toytree-mark-Toytree" id="t84d73ecab3d64053a38f0eddd20f6f4d"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 115.6 200.0 L 115.6 215.6 L 212.1 215.6" id="6,0" style=""></path><path d="M 115.6 200.0 L 115.6 184.4 L 212.1 184.4" id="6,1" style=""></path><path d="M 126.4 125.8 L 126.4 153.1 L 212.1 153.1" id="9,2" style=""></path><path d="M 193.5 98.4 L 193.5 121.9 L 212.1 121.9" id="8,3" style=""></path><path d="M 196.8 75.0 L 196.8 90.6 L 212.1 90.6" id="7,4" style=""></path><path d="M 196.8 75.0 L 196.8 59.4 L 212.1 59.4" id="7,5" style=""></path><path d="M 64.4 162.9 L 64.4 200.0 L 115.6 200.0" id="10,6" style=""></path><path d="M 193.5 98.4 L 193.5 75.0 L 196.8 75.0" id="8,7" style=""></path><path d="M 126.4 125.8 L 126.4 98.4 L 193.5 98.4" id="9,8" style=""></path><path d="M 64.4 162.9 L 64.4 125.8 L 126.4 125.8" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-6" transform="translate(115.563,200)"><rect x="-18.0" y="-9.0" width="36.0" height="18.0"></rect></g><g id="Node-7" transform="translate(196.846,75)"><rect x="-18.0" y="-9.0" width="36.0" height="18.0"></rect></g><g id="Node-8" transform="translate(193.533,98.4375)"><rect x="-18.0" y="-9.0" width="36.0" height="18.0"></rect></g><g id="Node-9" transform="translate(126.352,125.781)"><rect x="-18.0" y="-9.0" width="36.0" height="18.0"></rect></g><g id="Node-10" transform="translate(64.3999,162.891)"><rect x="-18.0" y="-9.0" width="36.0" height="18.0"></rect></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(115.563,200)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">100</text></g><g class="toytree-NodeLabel" transform="translate(196.846,75)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">100</text></g><g class="toytree-NodeLabel" transform="translate(193.533,98.4375)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">100</text></g><g class="toytree-NodeLabel" transform="translate(126.352,125.781)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">100</text></g><g class="toytree-NodeLabel" transform="translate(64.3999,162.891)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">nan</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(212.091,215.625)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r0</text></g><g class="toytree-TipLabel" transform="translate(212.091,184.375)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r1</text></g><g class="toytree-TipLabel" transform="translate(212.091,153.125)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r2</text></g><g class="toytree-TipLabel" transform="translate(212.091,121.875)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r3</text></g><g class="toytree-TipLabel" transform="translate(212.091,90.625)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r4</text></g><g class="toytree-TipLabel" transform="translate(212.091,59.375)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# ...
mask = tree.get_node_mask(2, 9, 10)
canvas, axes, mark = tree.draw()
tree.annotate.add_node_markers(axes=axes, marker="s", size=10, mask=mask);
```


<div class="toyplot" id="t9aded22a3a7745b7bd7950f09b6f8f50" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t3f061bf302d64ef087a0edf7fcb7226d"><g class="toyplot-coordinates-Cartesian" id="t7c307b64503e4097b48255bf7770e4a3"><clipPath id="tad25278dfc974abd96c441ded4d00f3b"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tad25278dfc974abd96c441ded4d00f3b)"><g class="toytree-mark-Toytree" id="t91ca00b97e6c4fdc9f1977fb38440a0c"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 108.8 202.2 L 108.8 218.3 L 210.2 218.3" id="6,0" style=""></path><path d="M 108.8 202.2 L 108.8 186.0 L 210.2 186.0" id="6,1" style=""></path><path d="M 120.1 125.4 L 120.1 153.7 L 210.2 153.7" id="9,2" style=""></path><path d="M 190.7 97.1 L 190.7 121.3 L 210.2 121.3" id="8,3" style=""></path><path d="M 194.2 72.8 L 194.2 89.0 L 210.2 89.0" id="7,4" style=""></path><path d="M 194.2 72.8 L 194.2 56.7 L 210.2 56.7" id="7,5" style=""></path><path d="M 55.0 163.8 L 55.0 202.2 L 108.8 202.2" id="10,6" style=""></path><path d="M 190.7 97.1 L 190.7 72.8 L 194.2 72.8" id="8,7" style=""></path><path d="M 120.1 125.4 L 120.1 97.1 L 190.7 97.1" id="9,8" style=""></path><path d="M 55.0 163.8 L 55.0 125.4 L 120.1 125.4" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(210.179,218.347)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r0</text></g><g class="toytree-TipLabel" transform="translate(210.179,186.008)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r1</text></g><g class="toytree-TipLabel" transform="translate(210.179,153.669)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r2</text></g><g class="toytree-TipLabel" transform="translate(210.179,121.331)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r3</text></g><g class="toytree-TipLabel" transform="translate(210.179,88.9916)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r4</text></g><g class="toytree-TipLabel" transform="translate(210.179,56.6526)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r5</text></g></g></g><g class="toytree-Annotation-Markers" id="te8312305f6d648dea53bb9cecbc47f3f" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Mark-0" transform="translate(210.179,153.669)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g><g id="Mark-1" transform="translate(120.118,125.373)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g><g id="Mark-2" transform="translate(55.042,163.775)"><rect x="-5.0" y="-5.0" width="10" height="10"></rect></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


### node_colors
The fill color of nodes can be set in a variety of ways. The node_colors option can be used to set a single color to all nodes, or different colors to nodes. The colors can be entered manually, or they can be automatically projected from color map to data values. There is another option for setting a single color to all nodes, using node_style.fill. The node_colors argument overrides node_style.fill.


```python
# set a single color to all nodes
tree.draw(node_colors="red", node_sizes=10);
```


<div class="toyplot" id="t0747cf8ee8404570b96872703af3f203" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t0aa5294e87704f9ea9396e7afa9fc8c3"><g class="toyplot-coordinates-Cartesian" id="t46d47ca0c1334f7b87d6f7177b37d3b0"><clipPath id="t3f535cc83b894f0d80f1bb04c71148c3"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t3f535cc83b894f0d80f1bb04c71148c3)"><g class="toytree-mark-Toytree" id="tc0a38f04302e422680dba112f193fde7"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 108.8 202.2 L 108.8 218.3 L 210.2 218.3" id="6,0" style=""></path><path d="M 108.8 202.2 L 108.8 186.0 L 210.2 186.0" id="6,1" style=""></path><path d="M 120.1 125.4 L 120.1 153.7 L 210.2 153.7" id="9,2" style=""></path><path d="M 190.7 97.1 L 190.7 121.3 L 210.2 121.3" id="8,3" style=""></path><path d="M 194.2 72.8 L 194.2 89.0 L 210.2 89.0" id="7,4" style=""></path><path d="M 194.2 72.8 L 194.2 56.7 L 210.2 56.7" id="7,5" style=""></path><path d="M 55.0 163.8 L 55.0 202.2 L 108.8 202.2" id="10,6" style=""></path><path d="M 190.7 97.1 L 190.7 72.8 L 194.2 72.8" id="8,7" style=""></path><path d="M 120.1 125.4 L 120.1 97.1 L 190.7 97.1" id="9,8" style=""></path><path d="M 55.0 163.8 L 55.0 125.4 L 120.1 125.4" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(100.0%,0.0%,0.0%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-6" transform="translate(108.784,202.178)"><circle r="5.0"></circle></g><g id="Node-7" transform="translate(194.166,72.8221)"><circle r="5.0"></circle></g><g id="Node-8" transform="translate(190.686,97.0763)"><circle r="5.0"></circle></g><g id="Node-9" transform="translate(120.118,125.373)"><circle r="5.0"></circle></g><g id="Node-10" transform="translate(55.042,163.775)"><circle r="5.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(210.179,218.347)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r0</text></g><g class="toytree-TipLabel" transform="translate(210.179,186.008)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r1</text></g><g class="toytree-TipLabel" transform="translate(210.179,153.669)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r2</text></g><g class="toytree-TipLabel" transform="translate(210.179,121.331)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r3</text></g><g class="toytree-TipLabel" transform="translate(210.179,88.9916)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r4</text></g><g class="toytree-TipLabel" transform="translate(210.179,56.6526)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
# list of colors of length nnodes
colors = ["darkcyan"] * 6 + ["goldenrod"] * 5
tree.draw(node_colors=colors, node_sizes=10, node_mask=False);
```


<div class="toyplot" id="t93e36fdef3284961b6d477b464edea27" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t0d7181b1338f48f8a5602dbf287ec1fa"><g class="toyplot-coordinates-Cartesian" id="tc3b2d44dfd61464fbb356ebe38c8ecbe"><clipPath id="t07e137bedef7470ba1e70b4749cf4944"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t07e137bedef7470ba1e70b4749cf4944)"><g class="toytree-mark-Toytree" id="t708e92f74d874b108b8670129d889195"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 108.8 202.2 L 108.8 218.3 L 210.2 218.3" id="6,0" style=""></path><path d="M 108.8 202.2 L 108.8 186.0 L 210.2 186.0" id="6,1" style=""></path><path d="M 120.1 125.4 L 120.1 153.7 L 210.2 153.7" id="9,2" style=""></path><path d="M 190.7 97.1 L 190.7 121.3 L 210.2 121.3" id="8,3" style=""></path><path d="M 194.2 72.8 L 194.2 89.0 L 210.2 89.0" id="7,4" style=""></path><path d="M 194.2 72.8 L 194.2 56.7 L 210.2 56.7" id="7,5" style=""></path><path d="M 55.0 163.8 L 55.0 202.2 L 108.8 202.2" id="10,6" style=""></path><path d="M 190.7 97.1 L 190.7 72.8 L 194.2 72.8" id="8,7" style=""></path><path d="M 120.1 125.4 L 120.1 97.1 L 190.7 97.1" id="9,8" style=""></path><path d="M 55.0 163.8 L 55.0 125.4 L 120.1 125.4" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(0.0%,54.5%,54.5%)" transform="translate(210.179,218.347)"><circle r="5.0"></circle></g><g id="Node-1" style="fill:rgb(0.0%,54.5%,54.5%)" transform="translate(210.179,186.008)"><circle r="5.0"></circle></g><g id="Node-2" style="fill:rgb(0.0%,54.5%,54.5%)" transform="translate(210.179,153.669)"><circle r="5.0"></circle></g><g id="Node-3" style="fill:rgb(0.0%,54.5%,54.5%)" transform="translate(210.179,121.331)"><circle r="5.0"></circle></g><g id="Node-4" style="fill:rgb(0.0%,54.5%,54.5%)" transform="translate(210.179,88.9916)"><circle r="5.0"></circle></g><g id="Node-5" style="fill:rgb(0.0%,54.5%,54.5%)" transform="translate(210.179,56.6526)"><circle r="5.0"></circle></g><g id="Node-6" style="fill:rgb(85.5%,64.7%,12.5%)" transform="translate(108.784,202.178)"><circle r="5.0"></circle></g><g id="Node-7" style="fill:rgb(85.5%,64.7%,12.5%)" transform="translate(194.166,72.8221)"><circle r="5.0"></circle></g><g id="Node-8" style="fill:rgb(85.5%,64.7%,12.5%)" transform="translate(190.686,97.0763)"><circle r="5.0"></circle></g><g id="Node-9" style="fill:rgb(85.5%,64.7%,12.5%)" transform="translate(120.118,125.373)"><circle r="5.0"></circle></g><g id="Node-10" style="fill:rgb(85.5%,64.7%,12.5%)" transform="translate(55.042,163.775)"><circle r="5.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(210.179,218.347)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r0</text></g><g class="toytree-TipLabel" transform="translate(210.179,186.008)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r1</text></g><g class="toytree-TipLabel" transform="translate(210.179,153.669)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r2</text></g><g class="toytree-TipLabel" transform="translate(210.179,121.331)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r3</text></g><g class="toytree-TipLabel" transform="translate(210.179,88.9916)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r4</text></g><g class="toytree-TipLabel" transform="translate(210.179,56.6526)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


Automatically color nodes by projecting a data feature that is saved to tree object, such as the node heights, using [color-mapping](/drawing-color-mapping/).


```python
# colormapping the 'height' feature
tree.draw(node_colors="height", node_sizes=10, node_mask=False);
```


<div class="toyplot" id="t3f409081b1d7451aa8e9273b5ab2b376" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tae0404a31ecb4193bcbb03a74d42c395"><g class="toyplot-coordinates-Cartesian" id="t8e4f71a1dafd4dbbbdc659a44263ebc1"><clipPath id="tbd443ff8cf1d4facbbc726a8ba5f8915"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tbd443ff8cf1d4facbbc726a8ba5f8915)"><g class="toytree-mark-Toytree" id="t43d51176120e4f8c93f7ebe574ba45c5"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 108.8 202.2 L 108.8 218.3 L 210.2 218.3" id="6,0" style=""></path><path d="M 108.8 202.2 L 108.8 186.0 L 210.2 186.0" id="6,1" style=""></path><path d="M 120.1 125.4 L 120.1 153.7 L 210.2 153.7" id="9,2" style=""></path><path d="M 190.7 97.1 L 190.7 121.3 L 210.2 121.3" id="8,3" style=""></path><path d="M 194.2 72.8 L 194.2 89.0 L 210.2 89.0" id="7,4" style=""></path><path d="M 194.2 72.8 L 194.2 56.7 L 210.2 56.7" id="7,5" style=""></path><path d="M 55.0 163.8 L 55.0 202.2 L 108.8 202.2" id="10,6" style=""></path><path d="M 190.7 97.1 L 190.7 72.8 L 194.2 72.8" id="8,7" style=""></path><path d="M 120.1 125.4 L 120.1 97.1 L 190.7 97.1" id="9,8" style=""></path><path d="M 55.0 163.8 L 55.0 125.4 L 120.1 125.4" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(210.179,218.347)"><circle r="5.0"></circle></g><g id="Node-1" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(210.179,186.008)"><circle r="5.0"></circle></g><g id="Node-2" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(210.179,153.669)"><circle r="5.0"></circle></g><g id="Node-3" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(210.179,121.331)"><circle r="5.0"></circle></g><g id="Node-4" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(210.179,88.9916)"><circle r="5.0"></circle></g><g id="Node-5" style="fill:rgb(36.9%,31.0%,63.5%)" transform="translate(210.179,56.6526)"><circle r="5.0"></circle></g><g id="Node-6" style="fill:rgb(99.4%,77.3%,45.7%)" transform="translate(108.784,202.178)"><circle r="5.0"></circle></g><g id="Node-7" style="fill:rgb(20.3%,54.1%,73.8%)" transform="translate(194.166,72.8221)"><circle r="5.0"></circle></g><g id="Node-8" style="fill:rgb(24.8%,59.2%,71.7%)" transform="translate(190.686,97.0763)"><circle r="5.0"></circle></g><g id="Node-9" style="fill:rgb(99.7%,90.2%,58.5%)" transform="translate(120.118,125.373)"><circle r="5.0"></circle></g><g id="Node-10" style="fill:rgb(62.0%,0.4%,25.9%)" transform="translate(55.042,163.775)"><circle r="5.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(210.179,218.347)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r0</text></g><g class="toytree-TipLabel" transform="translate(210.179,186.008)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r1</text></g><g class="toytree-TipLabel" transform="translate(210.179,153.669)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r2</text></g><g class="toytree-TipLabel" transform="translate(210.179,121.331)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r3</text></g><g class="toytree-TipLabel" transform="translate(210.179,88.9916)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r4</text></g><g class="toytree-TipLabel" transform="translate(210.179,56.6526)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Global config
The default visualization settings in toytree are inherited from toyplot. This includes the default usage of html format for displaying plots in a notebook, and the default behavior of automatically rendering Canvas objects in a notebook cell when they are created. Both of these options can be changed in the `config` settings of the toyplot library.


```python
import toyplot

# set config options to new settings
toyplot.config.autoformat = "png"
toyplot.config.autorender = False
```


```python
# embed a PNG drawing in the notebook
canvas, axes, mark = tree.draw()

# it will only display here b/c we return the Canvas
canvas
```




<div class="toyplot" id="tb0e4d64da50947ac9e0ed361bb29c037" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t7c60c99735764514826c0c083ec18bb8"><g class="toyplot-coordinates-Cartesian" id="t71d12179c66d4d449d857da5941cd5f2"><clipPath id="tafd9f42e66cf4ec2a7374d52fddd9142"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tafd9f42e66cf4ec2a7374d52fddd9142)"><g class="toytree-mark-Toytree" id="t9094f0d6ccd544a9a56fc3cdffb513c1"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 105.7 202.2 L 105.7 218.3 L 209.3 218.3" id="6,0" style=""></path><path d="M 105.7 202.2 L 105.7 186.0 L 209.3 186.0" id="6,1" style=""></path><path d="M 117.3 125.4 L 117.3 153.7 L 209.3 153.7" id="9,2" style=""></path><path d="M 189.4 97.1 L 189.4 121.3 L 209.3 121.3" id="8,3" style=""></path><path d="M 192.9 72.8 L 192.9 89.0 L 209.3 89.0" id="7,4" style=""></path><path d="M 192.9 72.8 L 192.9 56.7 L 209.3 56.7" id="7,5" style=""></path><path d="M 50.8 163.8 L 50.8 202.2 L 105.7 202.2" id="10,6" style=""></path><path d="M 189.4 97.1 L 189.4 72.8 L 192.9 72.8" id="8,7" style=""></path><path d="M 117.3 125.4 L 117.3 97.1 L 189.4 97.1" id="9,8" style=""></path><path d="M 50.8 163.8 L 50.8 125.4 L 117.3 125.4" id="10,9" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(209.311,218.347)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r0</text></g><g class="toytree-TipLabel" transform="translate(209.311,186.008)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r1</text></g><g class="toytree-TipLabel" transform="translate(209.311,153.669)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r2</text></g><g class="toytree-TipLabel" transform="translate(209.311,121.331)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r3</text></g><g class="toytree-TipLabel" transform="translate(209.311,88.9916)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r4</text></g><g class="toytree-TipLabel" transform="translate(209.311,56.6526)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r5</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>




```python
# set config options back to their defaults
toyplot.config.autoformat = "html"
toyplot.config.autorender = True
```
