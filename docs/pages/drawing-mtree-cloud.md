<div class="nb-md-page-hook" aria-hidden="true"></div>

# MultiTree Cloud Drawings

`MultiTree.draw_cloud_tree()` overlays many trees on one set of axes so that topological discordance and branch-length variation can be seen as a single cloud of edges. These are often called densitree-style plots. They are most useful when you want one shared view of variation across a tree set instead of a subplot grid.

This page focuses on the public `MultiTree.draw_cloud_tree()` method and keeps the richer draft structure because cloud-tree workflows benefit from side-by-side examples of the main control arguments.



```python
import toytree
```

### Example dataset



```python
# a multi-newick string
NEWICKS = """\
(((a:1,b:1):1,(d:1.5,e:1.5):0.5):1,c:3);
(((a:1,d:1):1,(b:1,e:1):1):1,c:3);
(((a:1.5,b:1.5):1,(d:1,e:1):1.5):1,c:3.5);
(((a:1.25,b:1.25):0.75,(d:1,e:1):1):1,c:3);
(((a:1,b:1):1,(d:1.5,e:1.5):0.5):1,c:3);
(((b:1,a:1):1,(d:1.5,e:1.5):0.5):2,c:4);
(((a:1.5,b:1.5):0.5,(d:1,e:1):1):1,c:3);
(((b:1.5,d:1.5):0.5,(a:1,e:1):1):1,c:3);
"""
```


```python
# create a multitree object
mtree = toytree.mtree(NEWICKS)
```

### Basic cloud-tree drawing
`MultiTree.draw_cloud_tree()` accepts many of the same styling arguments as `ToyTree.draw()`, plus cloud-specific arguments such as `fixed_order`, `jitter`, `idxs`, `interior_algorithm`, and `per_tree`. The first example below shows the standard overlay pattern.



```python
# draw a cloud tree
mtree.draw_cloud_tree(
    scale_bar=True,
    edge_style={"stroke-opacity": 0.1, "stroke-width": 2.5},
);
```


<div class="toyplot" id="te3e95f2c5bec4384862ef679054bac9a" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t8132091f784542519761dc333db37ae2"><g class="toyplot-coordinates-Cartesian" id="t84dc59aacc044f409027e09f4a57addd"><clipPath id="t3461444cc8ae466f8898a31737edb543"><rect x="50.0" y="59.09476420858974" width="200.0" height="175.0"></rect></clipPath><g clip-path="url(#t3461444cc8ae466f8898a31737edb543)"></g><g class="toyplot-coordinates-Axis" id="t5a2ad9e9893d419597934e51b4329ca7" transform="translate(50.0,234.09476420858974)"><line x1="1.2354405840481113" y1="0" x2="178.58042533000787" y2="0" style=""></line><g><line x1="1.2354405840481113" y1="0" x2="1.2354405840481113" y2="-5.0" style=""></line><line x1="45.57168677053805" y1="0" x2="45.57168677053805" y2="-5.0" style=""></line><line x1="89.907932957028" y1="0" x2="89.907932957028" y2="-5.0" style=""></line><line x1="134.24417914351793" y1="0" x2="134.24417914351793" y2="-5.0" style=""></line><line x1="178.58042533000787" y1="0" x2="178.58042533000787" y2="-5.0" style=""></line></g><g><g transform="translate(1.2354405840481113,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(45.57168677053805,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(89.907932957028,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(134.24417914351793,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(178.58042533000787,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t919c21a25d244cfeb0f1e1fab0376b86"><clipPath id="tc2da3837b96e4fd89c99b83d4da9df3e"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tc2da3837b96e4fd89c99b83d4da9df3e)"><g class="toytree-mark-Toytree" id="t06ae67a140ab47938854f47a78a7f341"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.5;fill:none"><path d="M 184.2 197.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 184.2 197.8 L 228.6 177.7" id="5,1" style=""></path><path d="M 162.1 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 162.1 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.6 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 139.9 157.6 L 184.2 197.8" id="7,5" style=""></path><path d="M 139.9 157.6 L 162.1 117.4" id="7,6" style=""></path><path d="M 95.6 137.5 L 139.9 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(228.58,217.845)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(228.58,177.672)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(228.58,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(228.58,97.3276)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(228.58,57.1552)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g><g class="toytree-mark-Toytree" id="tad5d7eaac891400e9382e4aa52e849ab"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.5;fill:none"><path d="M 184.2 177.7 L 228.6 217.8" id="5,0" style=""></path><path d="M 184.2 177.7 L 228.6 137.5" id="5,1" style=""></path><path d="M 184.2 137.5 L 228.6 177.7" id="6,2" style=""></path><path d="M 184.2 137.5 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.6 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 139.9 157.6 L 184.2 177.7" id="7,5" style=""></path><path d="M 139.9 157.6 L 184.2 137.5" id="7,6" style=""></path><path d="M 95.6 137.5 L 139.9 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="td8ebde8e027c443896b425b948b92c56"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.5;fill:none"><path d="M 162.1 197.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 162.1 197.8 L 228.6 177.7" id="5,1" style=""></path><path d="M 184.2 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 184.2 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 73.4 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 117.7 157.6 L 162.1 197.8" id="7,5" style=""></path><path d="M 117.7 157.6 L 184.2 117.4" id="7,6" style=""></path><path d="M 73.4 137.5 L 117.7 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t18e74eb8a8364e24ab70fa373660a0ed"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.5;fill:none"><path d="M 173.2 197.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 173.2 197.8 L 228.6 177.7" id="5,1" style=""></path><path d="M 184.2 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 184.2 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.6 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 139.9 157.6 L 173.2 197.8" id="7,5" style=""></path><path d="M 139.9 157.6 L 184.2 117.4" id="7,6" style=""></path><path d="M 95.6 137.5 L 139.9 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t60e2fd6090c045d4b51df3872d0cfdc7"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.5;fill:none"><path d="M 184.2 197.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 184.2 197.8 L 228.6 177.7" id="5,1" style=""></path><path d="M 162.1 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 162.1 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.6 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 139.9 157.6 L 184.2 197.8" id="7,5" style=""></path><path d="M 139.9 157.6 L 162.1 117.4" id="7,6" style=""></path><path d="M 95.6 137.5 L 139.9 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tabe9479c09e9434a8ab95cdc46bcbf9d"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.5;fill:none"><path d="M 184.2 197.8 L 228.6 177.7" id="5,0" style=""></path><path d="M 184.2 197.8 L 228.6 217.8" id="5,1" style=""></path><path d="M 162.1 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 162.1 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 51.2 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 139.9 157.6 L 184.2 197.8" id="7,5" style=""></path><path d="M 139.9 157.6 L 162.1 117.4" id="7,6" style=""></path><path d="M 51.2 137.5 L 139.9 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t751c8fe24c7347cf9b3319e8e23d6ec3"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.5;fill:none"><path d="M 162.1 197.8 L 228.6 217.8" id="5,0" style=""></path><path d="M 162.1 197.8 L 228.6 177.7" id="5,1" style=""></path><path d="M 184.2 117.4 L 228.6 137.5" id="6,2" style=""></path><path d="M 184.2 117.4 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.6 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 139.9 157.6 L 162.1 197.8" id="7,5" style=""></path><path d="M 139.9 157.6 L 184.2 117.4" id="7,6" style=""></path><path d="M 95.6 137.5 L 139.9 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tbf89570a91c04b0e80faa4ae51a8d977"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.5;fill:none"><path d="M 162.1 157.6 L 228.6 177.7" id="5,0" style=""></path><path d="M 162.1 157.6 L 228.6 137.5" id="5,1" style=""></path><path d="M 184.2 157.6 L 228.6 217.8" id="6,2" style=""></path><path d="M 184.2 157.6 L 228.6 97.3" id="6,3" style=""></path><path d="M 95.6 137.5 L 228.6 57.2" id="8,4" style=""></path><path d="M 139.9 157.6 L 162.1 157.6" id="7,5" style=""></path><path d="M 139.9 157.6 L 184.2 157.6" id="7,6" style=""></path><path d="M 95.6 137.5 L 139.9 157.6" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t8132091f784542519761dc333db37ae2";
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
        })(modules["toyplot.coordinates.Axis"],"t5a2ad9e9893d419597934e51b4329ca7",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.4831165583999999, "min": -4.0278652500000005}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


### Highlight selected trees with `per_tree`
Pass a `per_tree` list of draw-kwargs dictionaries to override shared draw settings for individual rendered trees. This is useful when you want to highlight one topology, color a subset differently, or vary widths / opacity without giving up the shared cloud-tree view.



```python
# build one draw-kwargs dict per rendered tree
utrees = mtree.get_unique_topologies()
per_tree = []

# set color to red if most common topology, else green
for tree in mtree:
    if tree.distance.get_treedist_rf(utrees[0][0]) == 0:
        per_tree.append({"edge_colors": "red"})
    else:
        per_tree.append({"edge_colors": "green"})

mtree.draw_cloud_tree(
    scale_bar=True,
    per_tree=per_tree,
    edge_style={"stroke-opacity": 0.25},
    tip_labels_style={"font-size": 15},
);
```


<div class="toyplot" id="te77887e14e1f4dcdbf665eb0d04e8d1f" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t53f7a0218a66452398483c1f29e5f96f"><g class="toyplot-coordinates-Cartesian" id="t5b9eba0d666e464883e7c72aaf909e56"><clipPath id="tb3e656f864014948976ce5ce2d1e914b"><rect x="50.0" y="57.085515704272865" width="200.0" height="175.0"></rect></clipPath><g clip-path="url(#tb3e656f864014948976ce5ce2d1e914b)"></g><g class="toyplot-coordinates-Axis" id="t2d1ad3d2e2f042939c36698c79e4a23f" transform="translate(50.0,232.08551570427286)"><line x1="0.986968105514573" y1="0" x2="176.96416441728948" y2="0" style=""></line><g><line x1="0.986968105514573" y1="0" x2="0.986968105514573" y2="-5.0" style=""></line><line x1="44.9812671834583" y1="0" x2="44.9812671834583" y2="-5.0" style=""></line><line x1="88.97556626140202" y1="0" x2="88.97556626140202" y2="-5.0" style=""></line><line x1="132.96986533934577" y1="0" x2="132.96986533934577" y2="-5.0" style=""></line><line x1="176.96416441728948" y1="0" x2="176.96416441728948" y2="-5.0" style=""></line></g><g><g transform="translate(0.986968105514573,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(44.9812671834583,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(88.97556626140202,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(132.96986533934577,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(176.96416441728948,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t22631bf2327f4ff4abff5d178878cbfd"><clipPath id="tc68a9ff38d1149139ea6141528bec2c8"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tc68a9ff38d1149139ea6141528bec2c8)"><g class="toytree-mark-Toytree" id="t4c07e3c433f4490d86b699bef6dc4270"><g class="toytree-Edges" style="stroke:rgb(100.0%,0.0%,0.0%);stroke-opacity:0.25;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.0 196.4 L 227.0 216.1" id="5,0" style=""></path><path d="M 183.0 196.4 L 227.0 176.8" id="5,1" style=""></path><path d="M 161.0 117.9 L 227.0 137.5" id="6,2" style=""></path><path d="M 161.0 117.9 L 227.0 98.2" id="6,3" style=""></path><path d="M 95.0 137.5 L 227.0 58.9" id="8,4" style=""></path><path d="M 139.0 157.1 L 183.0 196.4" id="7,5" style=""></path><path d="M 139.0 157.1 L 161.0 117.9" id="7,6" style=""></path><path d="M 95.0 137.5 L 139.0 157.1" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:15px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(226.964,216.086)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(226.964,176.793)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(226.964,137.5)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(226.964,98.2072)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(226.964,58.9145)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:15.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g><g class="toytree-mark-Toytree" id="tdfa055e756854af089f51964a62267f9"><g class="toytree-Edges" style="stroke:rgb(0.0%,50.2%,0.0%);stroke-opacity:0.25;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.0 176.8 L 227.0 216.1" id="5,0" style=""></path><path d="M 183.0 176.8 L 227.0 137.5" id="5,1" style=""></path><path d="M 183.0 137.5 L 227.0 176.8" id="6,2" style=""></path><path d="M 183.0 137.5 L 227.0 98.2" id="6,3" style=""></path><path d="M 95.0 137.5 L 227.0 58.9" id="8,4" style=""></path><path d="M 139.0 157.1 L 183.0 176.8" id="7,5" style=""></path><path d="M 139.0 157.1 L 183.0 137.5" id="7,6" style=""></path><path d="M 95.0 137.5 L 139.0 157.1" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tc7d1aa846ec24a53a577b343b8b91b30"><g class="toytree-Edges" style="stroke:rgb(100.0%,0.0%,0.0%);stroke-opacity:0.25;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 161.0 196.4 L 227.0 216.1" id="5,0" style=""></path><path d="M 161.0 196.4 L 227.0 176.8" id="5,1" style=""></path><path d="M 183.0 117.9 L 227.0 137.5" id="6,2" style=""></path><path d="M 183.0 117.9 L 227.0 98.2" id="6,3" style=""></path><path d="M 73.0 137.5 L 227.0 58.9" id="8,4" style=""></path><path d="M 117.0 157.1 L 161.0 196.4" id="7,5" style=""></path><path d="M 117.0 157.1 L 183.0 117.9" id="7,6" style=""></path><path d="M 73.0 137.5 L 117.0 157.1" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="td82c6a81cd4643c2a3bda49edb0405c2"><g class="toytree-Edges" style="stroke:rgb(100.0%,0.0%,0.0%);stroke-opacity:0.25;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 172.0 196.4 L 227.0 216.1" id="5,0" style=""></path><path d="M 172.0 196.4 L 227.0 176.8" id="5,1" style=""></path><path d="M 183.0 117.9 L 227.0 137.5" id="6,2" style=""></path><path d="M 183.0 117.9 L 227.0 98.2" id="6,3" style=""></path><path d="M 95.0 137.5 L 227.0 58.9" id="8,4" style=""></path><path d="M 139.0 157.1 L 172.0 196.4" id="7,5" style=""></path><path d="M 139.0 157.1 L 183.0 117.9" id="7,6" style=""></path><path d="M 95.0 137.5 L 139.0 157.1" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tbd89850cbdf64632817d915796c2edb0"><g class="toytree-Edges" style="stroke:rgb(100.0%,0.0%,0.0%);stroke-opacity:0.25;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.0 196.4 L 227.0 216.1" id="5,0" style=""></path><path d="M 183.0 196.4 L 227.0 176.8" id="5,1" style=""></path><path d="M 161.0 117.9 L 227.0 137.5" id="6,2" style=""></path><path d="M 161.0 117.9 L 227.0 98.2" id="6,3" style=""></path><path d="M 95.0 137.5 L 227.0 58.9" id="8,4" style=""></path><path d="M 139.0 157.1 L 183.0 196.4" id="7,5" style=""></path><path d="M 139.0 157.1 L 161.0 117.9" id="7,6" style=""></path><path d="M 95.0 137.5 L 139.0 157.1" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t6c55df6b84644138af2b477345ab9233"><g class="toytree-Edges" style="stroke:rgb(100.0%,0.0%,0.0%);stroke-opacity:0.25;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.0 196.4 L 227.0 176.8" id="5,0" style=""></path><path d="M 183.0 196.4 L 227.0 216.1" id="5,1" style=""></path><path d="M 161.0 117.9 L 227.0 137.5" id="6,2" style=""></path><path d="M 161.0 117.9 L 227.0 98.2" id="6,3" style=""></path><path d="M 51.0 137.5 L 227.0 58.9" id="8,4" style=""></path><path d="M 139.0 157.1 L 183.0 196.4" id="7,5" style=""></path><path d="M 139.0 157.1 L 161.0 117.9" id="7,6" style=""></path><path d="M 51.0 137.5 L 139.0 157.1" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="te2ae35988f3c4866abca217e148f3e83"><g class="toytree-Edges" style="stroke:rgb(100.0%,0.0%,0.0%);stroke-opacity:0.25;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 161.0 196.4 L 227.0 216.1" id="5,0" style=""></path><path d="M 161.0 196.4 L 227.0 176.8" id="5,1" style=""></path><path d="M 183.0 117.9 L 227.0 137.5" id="6,2" style=""></path><path d="M 183.0 117.9 L 227.0 98.2" id="6,3" style=""></path><path d="M 95.0 137.5 L 227.0 58.9" id="8,4" style=""></path><path d="M 139.0 157.1 L 161.0 196.4" id="7,5" style=""></path><path d="M 139.0 157.1 L 183.0 117.9" id="7,6" style=""></path><path d="M 95.0 137.5 L 139.0 157.1" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tbeb175de94dc4767ad304b427364672b"><g class="toytree-Edges" style="stroke:rgb(0.0%,50.2%,0.0%);stroke-opacity:0.25;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 161.0 157.1 L 227.0 176.8" id="5,0" style=""></path><path d="M 161.0 157.1 L 227.0 137.5" id="5,1" style=""></path><path d="M 183.0 157.1 L 227.0 216.1" id="6,2" style=""></path><path d="M 183.0 157.1 L 227.0 98.2" id="6,3" style=""></path><path d="M 95.0 137.5 L 227.0 58.9" id="8,4" style=""></path><path d="M 139.0 157.1 L 161.0 157.1" id="7,5" style=""></path><path d="M 139.0 157.1 L 183.0 157.1" id="7,6" style=""></path><path d="M 95.0 137.5 L 139.0 157.1" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t53f7a0218a66452398483c1f29e5f96f";
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
        })(modules["toyplot.coordinates.Axis"],"t2d1ad3d2e2f042939c36698c79e4a23f",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.5236095599999998, "min": -4.022434}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


### Interior node placement (`interior_algorithm`)

The `interior_algorithm` argument controls how internal nodes are placed along the tip-spread axis for linear cloud-tree layouts.

- `0` (recommended default): midpoint of immediate children.
- `1`: mean of descendant tip positions.
- `2`: robust weighted midpoint of immediate children using child branch lengths.
- `3`: median of descendant tip positions.
- `4`: trimmed mean of descendant tip positions.

In many datasets the differences are subtle with default tip spacing. If you need stronger geometric control, use explicit `fixed_position` values as a fallback.



```python
# baseline interior-node placement (recommended default)
mtree.draw_cloud_tree(
    interior_algorithm=0,
    scale_bar=True,
    edge_style={"stroke-opacity": 0.2, "stroke-width": 2.0},
    tip_labels_style={"font-size": 14},
);
```


<div class="toyplot" id="tfe54333e30994f609da7a61bc39fc9da" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t998446c70ccb41f1812064a7412142ac"><g class="toyplot-coordinates-Cartesian" id="t4f353dc818394e3c83d245636c028a63"><clipPath id="tdf96e8f0c90d4ca793a481b5a87a047c"><rect x="50.0" y="57.67004458856911" width="200.0" height="175.0"></rect></clipPath><g clip-path="url(#tdf96e8f0c90d4ca793a481b5a87a047c)"></g><g class="toyplot-coordinates-Axis" id="tdaa1682ab1094590b143c505d4315f13" transform="translate(50.0,232.6700445885691)"><line x1="0.9875188058381914" y1="0" x2="177.50037152778265" y2="0" style=""></line><g><line x1="0.9875188058381914" y1="0" x2="0.9875188058381914" y2="-5.0" style=""></line><line x1="45.115731986324306" y1="0" x2="45.115731986324306" y2="-5.0" style=""></line><line x1="89.24394516681042" y1="0" x2="89.24394516681042" y2="-5.0" style=""></line><line x1="133.37215834729653" y1="0" x2="133.37215834729653" y2="-5.0" style=""></line><line x1="177.50037152778265" y1="0" x2="177.50037152778265" y2="-5.0" style=""></line></g><g><g transform="translate(0.9875188058381914,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(45.115731986324306,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(89.24394516681042,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(133.37215834729653,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(177.50037152778265,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="ta1debc3765a4483aacb80c78050415b0"><clipPath id="teaf932d5e1ee4b568ecf5ba7b12df4aa"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#teaf932d5e1ee4b568ecf5ba7b12df4aa)"><g class="toytree-mark-Toytree" id="t4228605bc7a6419eb596cf42fdee00ce"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.4 196.9 L 227.5 216.7" id="5,0" style=""></path><path d="M 183.4 196.9 L 227.5 177.1" id="5,1" style=""></path><path d="M 161.3 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 161.3 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 107.8 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 157.3 L 183.4 196.9" id="7,5" style=""></path><path d="M 139.2 157.3 L 161.3 117.7" id="7,6" style=""></path><path d="M 95.1 107.8 L 139.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:14px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(227.5,216.67)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(227.5,177.085)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(227.5,137.5)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(227.5,97.915)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(227.5,58.33)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g><g class="toytree-mark-Toytree" id="td1e417e10c4d40b2bc7019165d6f4810"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.4 177.1 L 227.5 216.7" id="5,0" style=""></path><path d="M 183.4 177.1 L 227.5 137.5" id="5,1" style=""></path><path d="M 183.4 137.5 L 227.5 177.1" id="6,2" style=""></path><path d="M 183.4 137.5 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 107.8 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 157.3 L 183.4 177.1" id="7,5" style=""></path><path d="M 139.2 157.3 L 183.4 137.5" id="7,6" style=""></path><path d="M 95.1 107.8 L 139.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t0a332258b8564eec85d7607a89cf7a77"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 161.3 196.9 L 227.5 216.7" id="5,0" style=""></path><path d="M 161.3 196.9 L 227.5 177.1" id="5,1" style=""></path><path d="M 183.4 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 183.4 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 73.1 107.8 L 227.5 58.3" id="8,4" style=""></path><path d="M 117.2 157.3 L 161.3 196.9" id="7,5" style=""></path><path d="M 117.2 157.3 L 183.4 117.7" id="7,6" style=""></path><path d="M 73.1 107.8 L 117.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tb9ac03a933fd4c2bb932bd9ae75619e1"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 172.3 196.9 L 227.5 216.7" id="5,0" style=""></path><path d="M 172.3 196.9 L 227.5 177.1" id="5,1" style=""></path><path d="M 183.4 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 183.4 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 107.8 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 157.3 L 172.3 196.9" id="7,5" style=""></path><path d="M 139.2 157.3 L 183.4 117.7" id="7,6" style=""></path><path d="M 95.1 107.8 L 139.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tf6c077aa8243483c8b826c8433eef9bf"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.4 196.9 L 227.5 216.7" id="5,0" style=""></path><path d="M 183.4 196.9 L 227.5 177.1" id="5,1" style=""></path><path d="M 161.3 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 161.3 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 107.8 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 157.3 L 183.4 196.9" id="7,5" style=""></path><path d="M 139.2 157.3 L 161.3 117.7" id="7,6" style=""></path><path d="M 95.1 107.8 L 139.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="te4652eabf01548b39dc51765a53718c0"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.4 196.9 L 227.5 177.1" id="5,0" style=""></path><path d="M 183.4 196.9 L 227.5 216.7" id="5,1" style=""></path><path d="M 161.3 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 161.3 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 51.0 107.8 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 157.3 L 183.4 196.9" id="7,5" style=""></path><path d="M 139.2 157.3 L 161.3 117.7" id="7,6" style=""></path><path d="M 51.0 107.8 L 139.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t2b77f2f7a165486c949bbce5bb253763"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 161.3 196.9 L 227.5 216.7" id="5,0" style=""></path><path d="M 161.3 196.9 L 227.5 177.1" id="5,1" style=""></path><path d="M 183.4 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 183.4 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 107.8 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 157.3 L 161.3 196.9" id="7,5" style=""></path><path d="M 139.2 157.3 L 183.4 117.7" id="7,6" style=""></path><path d="M 95.1 107.8 L 139.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t4132b781dce14961b7a8ce1bea0590bc"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 161.3 157.3 L 227.5 177.1" id="5,0" style=""></path><path d="M 161.3 157.3 L 227.5 137.5" id="5,1" style=""></path><path d="M 183.4 157.3 L 227.5 216.7" id="6,2" style=""></path><path d="M 183.4 157.3 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 107.8 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 157.3 L 161.3 157.3" id="7,5" style=""></path><path d="M 139.2 157.3 L 183.4 157.3" id="7,6" style=""></path><path d="M 95.1 107.8 L 139.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t998446c70ccb41f1812064a7412142ac";
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
        })(modules["toyplot.coordinates.Axis"],"tdaa1682ab1094590b143c505d4315f13",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.5098694656, "min": -4.0223784}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>



```python
# robust alternative: descendant-tip median placement
mtree.draw_cloud_tree(
    interior_algorithm=3,
    scale_bar=True,
    edge_style={"stroke-opacity": 0.2, "stroke-width": 2.0},
    tip_labels_style={"font-size": 14},
);
```


<div class="toyplot" id="t9d6f9ac950a74a1da0113981fa971eed" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tc5b8c093df8748b08747ca11adb34cf6"><g class="toyplot-coordinates-Cartesian" id="t456a8a2239274205a8cac1dc42466657"><clipPath id="t8a2ef33f07444eed812086328b3dd0ab"><rect x="50.0" y="57.67004458856911" width="200.0" height="175.0"></rect></clipPath><g clip-path="url(#t8a2ef33f07444eed812086328b3dd0ab)"></g><g class="toyplot-coordinates-Axis" id="t5141a98b722a4e6cb53a40f6d0f771e7" transform="translate(50.0,232.6700445885691)"><line x1="0.9875188058381914" y1="0" x2="177.50037152778265" y2="0" style=""></line><g><line x1="0.9875188058381914" y1="0" x2="0.9875188058381914" y2="-5.0" style=""></line><line x1="45.115731986324306" y1="0" x2="45.115731986324306" y2="-5.0" style=""></line><line x1="89.24394516681042" y1="0" x2="89.24394516681042" y2="-5.0" style=""></line><line x1="133.37215834729653" y1="0" x2="133.37215834729653" y2="-5.0" style=""></line><line x1="177.50037152778265" y1="0" x2="177.50037152778265" y2="-5.0" style=""></line></g><g><g transform="translate(0.9875188058381914,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(45.115731986324306,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(89.24394516681042,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(133.37215834729653,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(177.50037152778265,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="td9fadebcc3664a5b9d49586f4e8a3437"><clipPath id="t2c58a30db2084d059a6ac42a0d4e8483"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t2c58a30db2084d059a6ac42a0d4e8483)"><g class="toytree-mark-Toytree" id="te8902999b92741d3bebd663e2dd18f84"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.4 196.9 L 227.5 216.7" id="5,0" style=""></path><path d="M 183.4 196.9 L 227.5 177.1" id="5,1" style=""></path><path d="M 161.3 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 161.3 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 137.5 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 157.3 L 183.4 196.9" id="7,5" style=""></path><path d="M 139.2 157.3 L 161.3 117.7" id="7,6" style=""></path><path d="M 95.1 137.5 L 139.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:14px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(227.5,216.67)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(227.5,177.085)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(227.5,137.5)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(227.5,97.915)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(227.5,58.33)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g><g class="toytree-mark-Toytree" id="t83d8b56748724e3489e384fdad0980ec"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.4 177.1 L 227.5 216.7" id="5,0" style=""></path><path d="M 183.4 177.1 L 227.5 137.5" id="5,1" style=""></path><path d="M 183.4 137.5 L 227.5 177.1" id="6,2" style=""></path><path d="M 183.4 137.5 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 137.5 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 157.3 L 183.4 177.1" id="7,5" style=""></path><path d="M 139.2 157.3 L 183.4 137.5" id="7,6" style=""></path><path d="M 95.1 137.5 L 139.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t66021ba050a1422a9b03ac501e3cf8f0"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 161.3 196.9 L 227.5 216.7" id="5,0" style=""></path><path d="M 161.3 196.9 L 227.5 177.1" id="5,1" style=""></path><path d="M 183.4 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 183.4 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 73.1 137.5 L 227.5 58.3" id="8,4" style=""></path><path d="M 117.2 157.3 L 161.3 196.9" id="7,5" style=""></path><path d="M 117.2 157.3 L 183.4 117.7" id="7,6" style=""></path><path d="M 73.1 137.5 L 117.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tb8df879ef2de469da2a380da7db8fcae"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 172.3 196.9 L 227.5 216.7" id="5,0" style=""></path><path d="M 172.3 196.9 L 227.5 177.1" id="5,1" style=""></path><path d="M 183.4 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 183.4 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 137.5 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 157.3 L 172.3 196.9" id="7,5" style=""></path><path d="M 139.2 157.3 L 183.4 117.7" id="7,6" style=""></path><path d="M 95.1 137.5 L 139.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t4459c64e5d174ba2ac47873d59144e6b"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.4 196.9 L 227.5 216.7" id="5,0" style=""></path><path d="M 183.4 196.9 L 227.5 177.1" id="5,1" style=""></path><path d="M 161.3 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 161.3 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 137.5 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 157.3 L 183.4 196.9" id="7,5" style=""></path><path d="M 139.2 157.3 L 161.3 117.7" id="7,6" style=""></path><path d="M 95.1 137.5 L 139.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t92b5b2a4bead4bbbb775ac02e591f06d"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.4 196.9 L 227.5 177.1" id="5,0" style=""></path><path d="M 183.4 196.9 L 227.5 216.7" id="5,1" style=""></path><path d="M 161.3 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 161.3 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 51.0 137.5 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 157.3 L 183.4 196.9" id="7,5" style=""></path><path d="M 139.2 157.3 L 161.3 117.7" id="7,6" style=""></path><path d="M 51.0 137.5 L 139.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t372435a1931742789ce91bee75b0e705"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 161.3 196.9 L 227.5 216.7" id="5,0" style=""></path><path d="M 161.3 196.9 L 227.5 177.1" id="5,1" style=""></path><path d="M 183.4 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 183.4 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 137.5 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 157.3 L 161.3 196.9" id="7,5" style=""></path><path d="M 139.2 157.3 L 183.4 117.7" id="7,6" style=""></path><path d="M 95.1 137.5 L 139.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tf75471d15efb432db77cb6c65b191506"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 161.3 157.3 L 227.5 177.1" id="5,0" style=""></path><path d="M 161.3 157.3 L 227.5 137.5" id="5,1" style=""></path><path d="M 183.4 157.3 L 227.5 216.7" id="6,2" style=""></path><path d="M 183.4 157.3 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 137.5 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 157.3 L 161.3 157.3" id="7,5" style=""></path><path d="M 139.2 157.3 L 183.4 157.3" id="7,6" style=""></path><path d="M 95.1 137.5 L 139.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "tc5b8c093df8748b08747ca11adb34cf6";
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
        })(modules["toyplot.coordinates.Axis"],"t5141a98b722a4e6cb53a40f6d0f771e7",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.5098694656, "min": -4.0223784}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>



```python
# branch-length-informed alternative: weighted child midpoint
mtree.draw_cloud_tree(
    interior_algorithm=2,
    scale_bar=True,
    edge_style={"stroke-opacity": 0.2, "stroke-width": 2.0},
    tip_labels_style={"font-size": 14},
);
```


<div class="toyplot" id="t347f017f47974888aae04b8f39724863" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tbb6e48b02c034c2f9aed8c25c9ef7aa6"><g class="toyplot-coordinates-Cartesian" id="t853ee2160d694cc98e31970d02b650e8"><clipPath id="t52e6c49f8c7846afb0ae182a4898ceac"><rect x="50.0" y="57.67004458856911" width="200.0" height="175.0"></rect></clipPath><g clip-path="url(#t52e6c49f8c7846afb0ae182a4898ceac)"></g><g class="toyplot-coordinates-Axis" id="tc26f828a07cd462385b5ecd839837010" transform="translate(50.0,232.6700445885691)"><line x1="0.9875188058381914" y1="0" x2="177.50037152778265" y2="0" style=""></line><g><line x1="0.9875188058381914" y1="0" x2="0.9875188058381914" y2="-5.0" style=""></line><line x1="45.115731986324306" y1="0" x2="45.115731986324306" y2="-5.0" style=""></line><line x1="89.24394516681042" y1="0" x2="89.24394516681042" y2="-5.0" style=""></line><line x1="133.37215834729653" y1="0" x2="133.37215834729653" y2="-5.0" style=""></line><line x1="177.50037152778265" y1="0" x2="177.50037152778265" y2="-5.0" style=""></line></g><g><g transform="translate(0.9875188058381914,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(45.115731986324306,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(89.24394516681042,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(133.37215834729653,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(177.50037152778265,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t8e847e8d949a44e8aeb52f00e2e4f02a"><clipPath id="t407692887edf41a1a2bc8c219fb757fe"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t407692887edf41a1a2bc8c219fb757fe)"><g class="toytree-mark-Toytree" id="t0e00e52296ef4ba184ccfb27e18329ae"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.4 196.9 L 227.5 216.7" id="5,0" style=""></path><path d="M 183.4 196.9 L 227.5 177.1" id="5,1" style=""></path><path d="M 161.3 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 161.3 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 122.7 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 144.1 L 183.4 196.9" id="7,5" style=""></path><path d="M 139.2 144.1 L 161.3 117.7" id="7,6" style=""></path><path d="M 95.1 122.7 L 139.2 144.1" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:14px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(227.5,216.67)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(227.5,177.085)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(227.5,137.5)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(227.5,97.915)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(227.5,58.33)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g><g class="toytree-mark-Toytree" id="t485bae2076c248f9a437f904982b1348"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.4 177.1 L 227.5 216.7" id="5,0" style=""></path><path d="M 183.4 177.1 L 227.5 137.5" id="5,1" style=""></path><path d="M 183.4 137.5 L 227.5 177.1" id="6,2" style=""></path><path d="M 183.4 137.5 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 132.6 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 157.3 L 183.4 177.1" id="7,5" style=""></path><path d="M 139.2 157.3 L 183.4 137.5" id="7,6" style=""></path><path d="M 95.1 132.6 L 139.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tc14e97c47f6d4ae7b4340abe1e15a01c"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 161.3 196.9 L 227.5 216.7" id="5,0" style=""></path><path d="M 161.3 196.9 L 227.5 177.1" id="5,1" style=""></path><path d="M 183.4 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 183.4 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 73.1 141.5 L 227.5 58.3" id="8,4" style=""></path><path d="M 117.2 165.2 L 161.3 196.9" id="7,5" style=""></path><path d="M 117.2 165.2 L 183.4 117.7" id="7,6" style=""></path><path d="M 73.1 141.5 L 117.2 165.2" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t12c1efd8592e4412848fd1857d1a942f"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 172.3 196.9 L 227.5 216.7" id="5,0" style=""></path><path d="M 172.3 196.9 L 227.5 177.1" id="5,1" style=""></path><path d="M 183.4 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 183.4 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 136.8 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 162.9 L 172.3 196.9" id="7,5" style=""></path><path d="M 139.2 162.9 L 183.4 117.7" id="7,6" style=""></path><path d="M 95.1 136.8 L 139.2 162.9" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t378e2b4458ca44328c8ecee89701fa0f"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.4 196.9 L 227.5 216.7" id="5,0" style=""></path><path d="M 183.4 196.9 L 227.5 177.1" id="5,1" style=""></path><path d="M 161.3 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 161.3 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 122.7 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 144.1 L 183.4 196.9" id="7,5" style=""></path><path d="M 139.2 144.1 L 161.3 117.7" id="7,6" style=""></path><path d="M 95.1 122.7 L 139.2 144.1" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="ta09f349419774b9799f281a30e888111"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.4 196.9 L 227.5 177.1" id="5,0" style=""></path><path d="M 183.4 196.9 L 227.5 216.7" id="5,1" style=""></path><path d="M 161.3 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 161.3 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 51.0 115.5 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 144.1 L 183.4 196.9" id="7,5" style=""></path><path d="M 139.2 144.1 L 161.3 117.7" id="7,6" style=""></path><path d="M 51.0 115.5 L 139.2 144.1" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t16604c26ecdb4b04b91a7266678971b5"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 161.3 196.9 L 227.5 216.7" id="5,0" style=""></path><path d="M 161.3 196.9 L 227.5 177.1" id="5,1" style=""></path><path d="M 183.4 117.7 L 227.5 137.5" id="6,2" style=""></path><path d="M 183.4 117.7 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 142.4 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 170.5 L 161.3 196.9" id="7,5" style=""></path><path d="M 139.2 170.5 L 183.4 117.7" id="7,6" style=""></path><path d="M 95.1 142.4 L 139.2 170.5" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t839997122a504186acec50a7bf7c5f1f"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.2;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 161.3 157.3 L 227.5 177.1" id="5,0" style=""></path><path d="M 161.3 157.3 L 227.5 137.5" id="5,1" style=""></path><path d="M 183.4 157.3 L 227.5 216.7" id="6,2" style=""></path><path d="M 183.4 157.3 L 227.5 97.9" id="6,3" style=""></path><path d="M 95.1 132.6 L 227.5 58.3" id="8,4" style=""></path><path d="M 139.2 157.3 L 161.3 157.3" id="7,5" style=""></path><path d="M 139.2 157.3 L 183.4 157.3" id="7,6" style=""></path><path d="M 95.1 132.6 L 139.2 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "tbb6e48b02c034c2f9aed8c25c9ef7aa6";
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
        })(modules["toyplot.coordinates.Axis"],"tc26f828a07cd462385b5ecd839837010",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.5098694656, "min": -4.0223784}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


#### Fallback: explicit tip positions

When interior algorithms alone are not enough, set `fixed_position` to deterministically control tip spacing, then choose any interior algorithm on top of that.



```python
# explicit tip-axis positions (fallback for stronger geometric control)
fixed_order = mtree.get_consensus_tree().get_tip_labels()
fixed_position = [0.0, 1.0, 2.5, 6.0, 9.0]

mtree.draw_cloud_tree(
    fixed_order=fixed_order,
    fixed_position=fixed_position,
    interior_algorithm=3,
    scale_bar=True,
    edge_style={"stroke-opacity": 0.25, "stroke-width": 2.0},
    tip_labels_style={"font-size": 14},
);
```


<div class="toyplot" id="t5a5e5496d0384f4f92fb93573156bf21" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="td9bb077960bf4d3ba4658e98193dba12"><g class="toyplot-coordinates-Cartesian" id="t4b01ac6c1b184d11bae2ba30745f8511"><clipPath id="t1caf320e67d5419cb9ef57e9e3cdaf85"><rect x="50.0" y="57.65498494581712" width="200.0" height="175.0"></rect></clipPath><g clip-path="url(#t1caf320e67d5419cb9ef57e9e3cdaf85)"></g><g class="toyplot-coordinates-Axis" id="tc8153f0543c446589a9ab9cfd2d585fc" transform="translate(50.0,232.65498494581712)"><line x1="0.9875188058381914" y1="0" x2="177.50037152778265" y2="0" style=""></line><g><line x1="0.9875188058381914" y1="0" x2="0.9875188058381914" y2="-5.0" style=""></line><line x1="45.115731986324306" y1="0" x2="45.115731986324306" y2="-5.0" style=""></line><line x1="89.24394516681042" y1="0" x2="89.24394516681042" y2="-5.0" style=""></line><line x1="133.37215834729653" y1="0" x2="133.37215834729653" y2="-5.0" style=""></line><line x1="177.50037152778265" y1="0" x2="177.50037152778265" y2="-5.0" style=""></line></g><g><g transform="translate(0.9875188058381914,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">4</text></g><g transform="translate(45.115731986324306,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(89.24394516681042,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(133.37215834729653,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(177.50037152778265,6.0)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t885a0f662d2e4388bed34061d7a14551"><clipPath id="t050a1faa0c7a444593053591e6e460e8"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t050a1faa0c7a444593053591e6e460e8)"><g class="toytree-mark-Toytree" id="t10b57cf7a1ca43ee9b65710fd3a8105d"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.25;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.4 208.3 L 227.5 216.7" id="5,0" style=""></path><path d="M 183.4 208.3 L 227.5 200.0" id="5,1" style=""></path><path d="M 161.3 145.8 L 227.5 175.0" id="6,2" style=""></path><path d="M 161.3 145.8 L 227.5 116.7" id="6,3" style=""></path><path d="M 95.1 175.0 L 227.5 66.7" id="8,4" style=""></path><path d="M 139.2 187.5 L 183.4 208.3" id="7,5" style=""></path><path d="M 139.2 187.5 L 161.3 145.8" id="7,6" style=""></path><path d="M 95.1 175.0 L 139.2 187.5" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:14px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(227.5,216.655)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">a</text></g><g class="toytree-TipLabel" transform="translate(227.5,199.989)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">b</text></g><g class="toytree-TipLabel" transform="translate(227.5,174.991)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">d</text></g><g class="toytree-TipLabel" transform="translate(227.5,116.662)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">e</text></g><g class="toytree-TipLabel" transform="translate(227.5,66.6655)"><text x="15.0" y="3.577" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:14.0px;font-weight:300;vertical-align:baseline;white-space:pre">c</text></g></g></g><g class="toytree-mark-Toytree" id="t78dd9b05128e4df2ab372b6a06e063cd"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.25;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.4 195.8 L 227.5 216.7" id="5,0" style=""></path><path d="M 183.4 195.8 L 227.5 175.0" id="5,1" style=""></path><path d="M 183.4 158.3 L 227.5 200.0" id="6,2" style=""></path><path d="M 183.4 158.3 L 227.5 116.7" id="6,3" style=""></path><path d="M 95.1 175.0 L 227.5 66.7" id="8,4" style=""></path><path d="M 139.2 187.5 L 183.4 195.8" id="7,5" style=""></path><path d="M 139.2 187.5 L 183.4 158.3" id="7,6" style=""></path><path d="M 95.1 175.0 L 139.2 187.5" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="ta88064869d614df78c309bdc01f4b850"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.25;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 161.3 208.3 L 227.5 216.7" id="5,0" style=""></path><path d="M 161.3 208.3 L 227.5 200.0" id="5,1" style=""></path><path d="M 183.4 145.8 L 227.5 175.0" id="6,2" style=""></path><path d="M 183.4 145.8 L 227.5 116.7" id="6,3" style=""></path><path d="M 73.1 175.0 L 227.5 66.7" id="8,4" style=""></path><path d="M 117.2 187.5 L 161.3 208.3" id="7,5" style=""></path><path d="M 117.2 187.5 L 183.4 145.8" id="7,6" style=""></path><path d="M 73.1 175.0 L 117.2 187.5" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tc4067dc799994a18ade5272bc5ffad80"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.25;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 172.3 208.3 L 227.5 216.7" id="5,0" style=""></path><path d="M 172.3 208.3 L 227.5 200.0" id="5,1" style=""></path><path d="M 183.4 145.8 L 227.5 175.0" id="6,2" style=""></path><path d="M 183.4 145.8 L 227.5 116.7" id="6,3" style=""></path><path d="M 95.1 175.0 L 227.5 66.7" id="8,4" style=""></path><path d="M 139.2 187.5 L 172.3 208.3" id="7,5" style=""></path><path d="M 139.2 187.5 L 183.4 145.8" id="7,6" style=""></path><path d="M 95.1 175.0 L 139.2 187.5" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tdfe312b559e94e198c1ddc0d77302494"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.25;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.4 208.3 L 227.5 216.7" id="5,0" style=""></path><path d="M 183.4 208.3 L 227.5 200.0" id="5,1" style=""></path><path d="M 161.3 145.8 L 227.5 175.0" id="6,2" style=""></path><path d="M 161.3 145.8 L 227.5 116.7" id="6,3" style=""></path><path d="M 95.1 175.0 L 227.5 66.7" id="8,4" style=""></path><path d="M 139.2 187.5 L 183.4 208.3" id="7,5" style=""></path><path d="M 139.2 187.5 L 161.3 145.8" id="7,6" style=""></path><path d="M 95.1 175.0 L 139.2 187.5" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="td10e73dd24434830ab9cb44ecc1983b4"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.25;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 183.4 208.3 L 227.5 200.0" id="5,0" style=""></path><path d="M 183.4 208.3 L 227.5 216.7" id="5,1" style=""></path><path d="M 161.3 145.8 L 227.5 175.0" id="6,2" style=""></path><path d="M 161.3 145.8 L 227.5 116.7" id="6,3" style=""></path><path d="M 51.0 175.0 L 227.5 66.7" id="8,4" style=""></path><path d="M 139.2 187.5 L 183.4 208.3" id="7,5" style=""></path><path d="M 139.2 187.5 L 161.3 145.8" id="7,6" style=""></path><path d="M 51.0 175.0 L 139.2 187.5" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t8de0cfdf683b43148733c443d5af001e"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.25;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 161.3 208.3 L 227.5 216.7" id="5,0" style=""></path><path d="M 161.3 208.3 L 227.5 200.0" id="5,1" style=""></path><path d="M 183.4 145.8 L 227.5 175.0" id="6,2" style=""></path><path d="M 183.4 145.8 L 227.5 116.7" id="6,3" style=""></path><path d="M 95.1 175.0 L 227.5 66.7" id="8,4" style=""></path><path d="M 139.2 187.5 L 161.3 208.3" id="7,5" style=""></path><path d="M 139.2 187.5 L 183.4 145.8" id="7,6" style=""></path><path d="M 95.1 175.0 L 139.2 187.5" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t7354376029d74233903ed3d28f8bf8f4"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.25;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 161.3 187.5 L 227.5 200.0" id="5,0" style=""></path><path d="M 161.3 187.5 L 227.5 175.0" id="5,1" style=""></path><path d="M 183.4 166.7 L 227.5 216.7" id="6,2" style=""></path><path d="M 183.4 166.7 L 227.5 116.7" id="6,3" style=""></path><path d="M 95.1 175.0 L 227.5 66.7" id="8,4" style=""></path><path d="M 139.2 187.5 L 161.3 187.5" id="7,5" style=""></path><path d="M 139.2 187.5 L 183.4 166.7" id="7,6" style=""></path><path d="M 95.1 175.0 L 139.2 187.5" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "td9bb077960bf4d3ba4658e98193dba12";
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
        })(modules["toyplot.coordinates.Axis"],"tc8153f0543c446589a9ab9cfd2d585fc",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.5098694656, "min": -4.0223784}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>

