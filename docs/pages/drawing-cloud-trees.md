<div class="nb-md-page-hook" aria-hidden="true"></div>

# Drawing Cloud Trees

Cloud tree drawings provide a useful way to visualize discordance among sets of trees in a MultiTree object.


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

### Cloud tree drawings
The `.draw_cloud_tree` function takes similar styling arguments as the `ToyTree.draw` function but accepts a few additional arguments.


```python
# draw a cloud tree
mtree.draw_cloud_tree(
    scale_bar=True,
    edge_style={
        "stroke-opacity": 0.1,
        "stroke-width": 2.5,
    },
);
```


<div class="toyplot" id="t0aeb42b2c8984a99988097b15372dce2" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t017249048aa040669c9a77658766f80d"><g class="toyplot-coordinates-Cartesian" id="t016cf892d33342698ca374a3f305d434"><clipPath id="t7bb5972c45b248899b92b37daafc9e1a"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#t7bb5972c45b248899b92b37daafc9e1a)"><g class="toytree-mark-Toytree" id="t02b0d5fc4dbc454e8667e779a5812daa"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-width:2.5;fill:none"><path d="M 173.7 198.1 L 214.6 218.3" id="5,0" style=""></path><path d="M 173.7 198.1 L 214.6 177.9" id="5,1" style=""></path><path d="M 153.2 117.3 L 214.6 137.5" id="6,2" style=""></path><path d="M 153.2 117.3 L 214.6 97.1" id="6,3" style=""></path><path d="M 91.9 137.5 L 214.6 56.7" id="8,4" style=""></path><path d="M 132.8 157.7 L 173.7 198.1" id="7,5" style=""></path><path d="M 132.8 157.7 L 153.2 117.3" id="7,6" style=""></path><path d="M 91.9 137.5 L 132.8 157.7" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(214.558,218.347)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">a</text></g><g class="toytree-TipLabel" transform="translate(214.558,177.924)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">b</text></g><g class="toytree-TipLabel" transform="translate(214.558,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">d</text></g><g class="toytree-TipLabel" transform="translate(214.558,97.0763)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">e</text></g><g class="toytree-TipLabel" transform="translate(214.558,56.6526)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">c</text></g></g></g><g class="toytree-mark-Toytree" id="t0b31f5c175404085a1b0141d1782ea40"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-width:2.5;fill:none"><path d="M 173.7 177.9 L 214.6 218.3" id="5,0" style=""></path><path d="M 173.7 177.9 L 214.6 137.5" id="5,1" style=""></path><path d="M 173.7 137.5 L 214.6 177.9" id="6,2" style=""></path><path d="M 173.7 137.5 L 214.6 97.1" id="6,3" style=""></path><path d="M 91.9 137.5 L 214.6 56.7" id="8,4" style=""></path><path d="M 132.8 157.7 L 173.7 177.9" id="7,5" style=""></path><path d="M 132.8 157.7 L 173.7 137.5" id="7,6" style=""></path><path d="M 91.9 137.5 L 132.8 157.7" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t1e92244583f64ca5a7ce2679f1970dd9"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-width:2.5;fill:none"><path d="M 153.2 198.1 L 214.6 218.3" id="5,0" style=""></path><path d="M 153.2 198.1 L 214.6 177.9" id="5,1" style=""></path><path d="M 173.7 117.3 L 214.6 137.5" id="6,2" style=""></path><path d="M 173.7 117.3 L 214.6 97.1" id="6,3" style=""></path><path d="M 71.5 137.5 L 214.6 56.7" id="8,4" style=""></path><path d="M 112.3 157.7 L 153.2 198.1" id="7,5" style=""></path><path d="M 112.3 157.7 L 173.7 117.3" id="7,6" style=""></path><path d="M 71.5 137.5 L 112.3 157.7" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t58eda75a402743979d56250bf97a4e81"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-width:2.5;fill:none"><path d="M 163.5 198.1 L 214.6 218.3" id="5,0" style=""></path><path d="M 163.5 198.1 L 214.6 177.9" id="5,1" style=""></path><path d="M 173.7 117.3 L 214.6 137.5" id="6,2" style=""></path><path d="M 173.7 117.3 L 214.6 97.1" id="6,3" style=""></path><path d="M 91.9 137.5 L 214.6 56.7" id="8,4" style=""></path><path d="M 132.8 157.7 L 163.5 198.1" id="7,5" style=""></path><path d="M 132.8 157.7 L 173.7 117.3" id="7,6" style=""></path><path d="M 91.9 137.5 L 132.8 157.7" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="te3eb999b220a4f97aaeee50b519466f2"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-width:2.5;fill:none"><path d="M 173.7 198.1 L 214.6 218.3" id="5,0" style=""></path><path d="M 173.7 198.1 L 214.6 177.9" id="5,1" style=""></path><path d="M 153.2 117.3 L 214.6 137.5" id="6,2" style=""></path><path d="M 153.2 117.3 L 214.6 97.1" id="6,3" style=""></path><path d="M 91.9 137.5 L 214.6 56.7" id="8,4" style=""></path><path d="M 132.8 157.7 L 173.7 198.1" id="7,5" style=""></path><path d="M 132.8 157.7 L 153.2 117.3" id="7,6" style=""></path><path d="M 91.9 137.5 L 132.8 157.7" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t26f52953e35541fb9b82bd145048359e"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-width:2.5;fill:none"><path d="M 173.7 198.1 L 214.6 177.9" id="5,0" style=""></path><path d="M 173.7 198.1 L 214.6 218.3" id="5,1" style=""></path><path d="M 153.2 117.3 L 214.6 137.5" id="6,2" style=""></path><path d="M 153.2 117.3 L 214.6 97.1" id="6,3" style=""></path><path d="M 51.0 117.3 L 214.6 56.7" id="8,4" style=""></path><path d="M 132.8 137.5 L 173.7 198.1" id="7,5" style=""></path><path d="M 132.8 137.5 L 153.2 117.3" id="7,6" style=""></path><path d="M 51.0 117.3 L 132.8 137.5" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t39e6c3c0898f471292e28f8d6326d03f"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-width:2.5;fill:none"><path d="M 153.2 198.1 L 214.6 218.3" id="5,0" style=""></path><path d="M 153.2 198.1 L 214.6 177.9" id="5,1" style=""></path><path d="M 173.7 117.3 L 214.6 137.5" id="6,2" style=""></path><path d="M 173.7 117.3 L 214.6 97.1" id="6,3" style=""></path><path d="M 91.9 137.5 L 214.6 56.7" id="8,4" style=""></path><path d="M 132.8 157.7 L 153.2 198.1" id="7,5" style=""></path><path d="M 132.8 157.7 L 173.7 117.3" id="7,6" style=""></path><path d="M 91.9 137.5 L 132.8 157.7" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tbcf74841680f440ea2ae0ec6f3c1f501"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:0.1;stroke-linecap:round;stroke-width:2.5;fill:none"><path d="M 153.2 157.7 L 214.6 177.9" id="5,0" style=""></path><path d="M 153.2 157.7 L 214.6 137.5" id="5,1" style=""></path><path d="M 173.7 157.7 L 214.6 218.3" id="6,2" style=""></path><path d="M 173.7 157.7 L 214.6 97.1" id="6,3" style=""></path><path d="M 91.9 117.3 L 214.6 56.7" id="8,4" style=""></path><path d="M 132.8 137.5 L 153.2 157.7" id="7,5" style=""></path><path d="M 132.8 137.5 L 173.7 157.7" id="7,6" style=""></path><path d="M 91.9 117.3 L 132.8 137.5" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g></g><g class="toyplot-coordinates-Axis" id="tfa0c75dc241a4de1bdeacc5b1d377b9f" transform="translate(50.0,225.0)translate(0,15.0)"><line x1="1.022101932181507" y1="0" x2="164.5584110812203" y2="0" style=""></line><g><line x1="41.906179219441206" y1="0" x2="41.906179219441206" y2="-5" style=""></line><line x1="82.79025650670091" y1="0" x2="82.79025650670091" y2="-5" style=""></line><line x1="123.6743337939606" y1="0" x2="123.6743337939606" y2="-5" style=""></line><line x1="164.5584110812203" y1="0" x2="164.5584110812203" y2="-5" style=""></line></g><g><g transform="translate(41.906179219441206,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(82.79025650670091,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(123.6743337939606,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(164.5584110812203,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t017249048aa040669c9a77658766f80d";
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
        })(modules["toyplot.coordinates.Axis"],"tfa0c75dc241a4de1bdeacc5b1d377b9f",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.8668800000000001, "min": -4.025}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


### Styling individual trees
I find it useful to set different styles on different trees in a set to better examine their differences. Pass a `per_tree` list of draw-kwargs dictionaries to override shared draw settings for individual trees. In this example the edge color depends on whether the tree topology matches the most common topology in the set or not.


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
    interior_algorithm=0,
    per_tree=per_tree,
    edge_style={"stroke-opacity": 0.25},
    tip_labels_style={"font-size": 15},
);
```


<div class="toyplot" id="t0cd238b8462e4bd2ade0222e1e9de4c7" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t7868f4f044cc4dcabcd7526e84304ade"><g class="toyplot-coordinates-Cartesian" id="t7bf4669d739149b4997d9a4ba43c5878"><clipPath id="teb6e83ca5ec248c4a74b31d6ad580286"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#teb6e83ca5ec248c4a74b31d6ad580286)"><g class="toytree-mark-Toytree" id="t284667a8957b4f8caf33289591b9d94d"><g class="toytree-Edges" style="stroke:rgb(100.0%,0.0%,0.0%);stroke-opacity:0.25;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 171.9 197.0 L 212.3 216.8" id="5,0" style=""></path><path d="M 171.9 197.0 L 212.3 177.2" id="5,1" style=""></path><path d="M 151.7 117.7 L 212.3 137.5" id="6,2" style=""></path><path d="M 151.7 117.7 L 212.3 97.8" id="6,3" style=""></path><path d="M 91.2 107.7 L 212.3 58.2" id="8,4" style=""></path><path d="M 131.6 157.3 L 171.9 197.0" id="7,5" style=""></path><path d="M 131.6 157.3 L 151.7 117.7" id="7,6" style=""></path><path d="M 91.2 107.7 L 131.6 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:15px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(212.306,216.839)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">a</text></g><g class="toytree-TipLabel" transform="translate(212.306,177.17)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">b</text></g><g class="toytree-TipLabel" transform="translate(212.306,137.5)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">d</text></g><g class="toytree-TipLabel" transform="translate(212.306,97.8303)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">e</text></g><g class="toytree-TipLabel" transform="translate(212.306,58.1606)"><text x="15.0" y="3.8324999999999996" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">c</text></g></g></g><g class="toytree-mark-Toytree" id="t1fd2a881e5004b9f90e44c421186fa1b"><g class="toytree-Edges" style="stroke:rgb(0.0%,50.2%,0.0%);stroke-opacity:0.25;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 171.9 177.2 L 212.3 216.8" id="5,0" style=""></path><path d="M 171.9 177.2 L 212.3 137.5" id="5,1" style=""></path><path d="M 171.9 137.5 L 212.3 177.2" id="6,2" style=""></path><path d="M 171.9 137.5 L 212.3 97.8" id="6,3" style=""></path><path d="M 91.2 107.7 L 212.3 58.2" id="8,4" style=""></path><path d="M 131.6 157.3 L 171.9 177.2" id="7,5" style=""></path><path d="M 131.6 157.3 L 171.9 137.5" id="7,6" style=""></path><path d="M 91.2 107.7 L 131.6 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t31e18d6937d6421cbce53a17c105cef7"><g class="toytree-Edges" style="stroke:rgb(100.0%,0.0%,0.0%);stroke-opacity:0.25;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 151.7 197.0 L 212.3 216.8" id="5,0" style=""></path><path d="M 151.7 197.0 L 212.3 177.2" id="5,1" style=""></path><path d="M 171.9 117.7 L 212.3 137.5" id="6,2" style=""></path><path d="M 171.9 117.7 L 212.3 97.8" id="6,3" style=""></path><path d="M 71.0 107.7 L 212.3 58.2" id="8,4" style=""></path><path d="M 111.4 157.3 L 151.7 197.0" id="7,5" style=""></path><path d="M 111.4 157.3 L 171.9 117.7" id="7,6" style=""></path><path d="M 71.0 107.7 L 111.4 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tf509d79fe0a24e51b7f9a39b1b2ca8ea"><g class="toytree-Edges" style="stroke:rgb(100.0%,0.0%,0.0%);stroke-opacity:0.25;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 161.8 197.0 L 212.3 216.8" id="5,0" style=""></path><path d="M 161.8 197.0 L 212.3 177.2" id="5,1" style=""></path><path d="M 171.9 117.7 L 212.3 137.5" id="6,2" style=""></path><path d="M 171.9 117.7 L 212.3 97.8" id="6,3" style=""></path><path d="M 91.2 107.7 L 212.3 58.2" id="8,4" style=""></path><path d="M 131.6 157.3 L 161.8 197.0" id="7,5" style=""></path><path d="M 131.6 157.3 L 171.9 117.7" id="7,6" style=""></path><path d="M 91.2 107.7 L 131.6 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tdf925af6c2494365a9491f7896defb1a"><g class="toytree-Edges" style="stroke:rgb(100.0%,0.0%,0.0%);stroke-opacity:0.25;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 171.9 197.0 L 212.3 216.8" id="5,0" style=""></path><path d="M 171.9 197.0 L 212.3 177.2" id="5,1" style=""></path><path d="M 151.7 117.7 L 212.3 137.5" id="6,2" style=""></path><path d="M 151.7 117.7 L 212.3 97.8" id="6,3" style=""></path><path d="M 91.2 107.7 L 212.3 58.2" id="8,4" style=""></path><path d="M 131.6 157.3 L 171.9 197.0" id="7,5" style=""></path><path d="M 131.6 157.3 L 151.7 117.7" id="7,6" style=""></path><path d="M 91.2 107.7 L 131.6 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="tbc94218eff0d46b18852b5d9c845c1e4"><g class="toytree-Edges" style="stroke:rgb(100.0%,0.0%,0.0%);stroke-opacity:0.25;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 171.9 197.0 L 212.3 177.2" id="5,0" style=""></path><path d="M 171.9 197.0 L 212.3 216.8" id="5,1" style=""></path><path d="M 151.7 117.7 L 212.3 137.5" id="6,2" style=""></path><path d="M 151.7 117.7 L 212.3 97.8" id="6,3" style=""></path><path d="M 50.8 107.7 L 212.3 58.2" id="8,4" style=""></path><path d="M 131.6 157.3 L 171.9 197.0" id="7,5" style=""></path><path d="M 131.6 157.3 L 151.7 117.7" id="7,6" style=""></path><path d="M 50.8 107.7 L 131.6 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t9471c13f75834c96b5607bad75df54a5"><g class="toytree-Edges" style="stroke:rgb(100.0%,0.0%,0.0%);stroke-opacity:0.25;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 151.7 197.0 L 212.3 216.8" id="5,0" style=""></path><path d="M 151.7 197.0 L 212.3 177.2" id="5,1" style=""></path><path d="M 171.9 117.7 L 212.3 137.5" id="6,2" style=""></path><path d="M 171.9 117.7 L 212.3 97.8" id="6,3" style=""></path><path d="M 91.2 107.7 L 212.3 58.2" id="8,4" style=""></path><path d="M 131.6 157.3 L 151.7 197.0" id="7,5" style=""></path><path d="M 131.6 157.3 L 171.9 117.7" id="7,6" style=""></path><path d="M 91.2 107.7 L 131.6 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g><g class="toytree-mark-Toytree" id="t8326be86f37342c3a60992e079055ca8"><g class="toytree-Edges" style="stroke:rgb(0.0%,50.2%,0.0%);stroke-opacity:0.25;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 151.7 157.3 L 212.3 177.2" id="5,0" style=""></path><path d="M 151.7 157.3 L 212.3 137.5" id="5,1" style=""></path><path d="M 171.9 157.3 L 212.3 216.8" id="6,2" style=""></path><path d="M 171.9 157.3 L 212.3 97.8" id="6,3" style=""></path><path d="M 91.2 107.7 L 212.3 58.2" id="8,4" style=""></path><path d="M 131.6 157.3 L 151.7 157.3" id="7,5" style=""></path><path d="M 131.6 157.3 L 171.9 157.3" id="7,6" style=""></path><path d="M 91.2 107.7 L 131.6 157.3" id="8,7" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g></g></g><g class="toyplot-coordinates-Axis" id="t49ed12be47c34779b1d333bc9bca3855" transform="translate(50.0,225.0)translate(0,15.0)"><line x1="0.8074935400516623" y1="0" x2="162.30620155038758" y2="0" style=""></line><g><line x1="41.182170542635646" y1="0" x2="41.182170542635646" y2="-5" style=""></line><line x1="81.55684754521963" y1="0" x2="81.55684754521963" y2="-5" style=""></line><line x1="121.9315245478036" y1="0" x2="121.9315245478036" y2="-5" style=""></line><line x1="162.30620155038758" y1="0" x2="162.30620155038758" y2="-5" style=""></line></g><g><g transform="translate(41.182170542635646,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">3</text></g><g transform="translate(81.55684754521963,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">2</text></g><g transform="translate(121.9315245478036,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(162.30620155038758,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t7868f4f044cc4dcabcd7526e84304ade";
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
        })(modules["toyplot.coordinates.Axis"],"t49ed12be47c34779b1d333bc9bca3855",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.9336000000000002, "min": -4.02}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 200.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


### Interior node placement (`interior_algorithm`)

The `interior_algorithm` argument controls how internal nodes are placed along the tip-spread axis for linear cloud-tree layouts.

- `0` (recommended default): midpoint of immediate children.
- `1`: mean of descendant tip positions.
- `2`: robust weighted midpoint of immediate children (uses child branch lengths).
- `3`: median of descendant tip positions.
- `4`: trimmed mean of descendant tip positions.

In many datasets the differences are subtle using default tip spacing. If you need stronger control over the geometry, use explicit `fixed_position` values as a fallback.


```python
# baseline interior-node placement (recommended default)
mtree.draw_cloud_tree(
    interior_algorithm=0,
    scale_bar=True,
    edge_style={"stroke-opacity": 0.2, "stroke-width": 2.0},
    tip_labels_style={"font-size": 14},
);
```


```python
# robust alternative: descendant-tip median placement
mtree.draw_cloud_tree(
    interior_algorithm=3,
    scale_bar=True,
    edge_style={"stroke-opacity": 0.2, "stroke-width": 2.0},
    tip_labels_style={"font-size": 14},
);
```


```python
# branch-length-informed alternative: weighted child midpoint
mtree.draw_cloud_tree(
    interior_algorithm=2,
    scale_bar=True,
    edge_style={"stroke-opacity": 0.2, "stroke-width": 2.0},
    tip_labels_style={"font-size": 14},
);
```

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
