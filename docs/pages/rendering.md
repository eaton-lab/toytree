<div class="nb-md-page-hook" aria-hidden="true"></div>

# Save/Export Canvas
Toytree drawings can be saved to disk using the `render` functions of toyplot. You can save toyplot figures in a variety of formats, including HTML, SVG, PDF, and PNG. 


```python
import toyplot

import toytree
```

To save a tree drawing you must store the `Canvas` object to a named variable.


```python
# Draw an example tree and save the Canvas, axes, and mark
rtre = toytree.rtree.unittree(ntips=8)
canvas, axes, mark = rtre.draw()
```


<div class="toyplot" id="t64421a859b5f4c4983b8cef1a13d28b6" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="300.0px" height="275.0px" viewBox="0 0 300.0 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="te2727f5f2eb1489aacf30dd7b122e341"><g class="toyplot-coordinates-Cartesian" id="t6d027809521541a49896056aba37596e"><clipPath id="tab1ec0537efe4682a9fd7fca9df3de5c"><rect x="35.0" y="35.0" width="230.0" height="205.0"></rect></clipPath><g clip-path="url(#tab1ec0537efe4682a9fd7fca9df3de5c)"><g class="toytree-mark-Toytree" id="t0b02d97db2354af6934877c8c7ed2ec7"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 82.5 206.8 L 82.5 218.3 L 209.3 218.3" id="8,0" style=""></path><path d="M 82.5 206.8 L 82.5 195.2 L 209.3 195.2" id="8,1" style=""></path><path d="M 145.9 154.8 L 145.9 172.1 L 209.3 172.1" id="10,2" style=""></path><path d="M 177.6 137.5 L 177.6 149.0 L 209.3 149.0" id="9,3" style=""></path><path d="M 177.6 137.5 L 177.6 126.0 L 209.3 126.0" id="9,4" style=""></path><path d="M 145.9 91.3 L 145.9 102.9 L 209.3 102.9" id="11,5" style=""></path><path d="M 145.9 91.3 L 145.9 79.8 L 209.3 79.8" id="11,6" style=""></path><path d="M 82.5 89.9 L 82.5 56.7 L 209.3 56.7" id="13,7" style=""></path><path d="M 50.8 148.3 L 50.8 206.8 L 82.5 206.8" id="14,8" style=""></path><path d="M 145.9 154.8 L 145.9 137.5 L 177.6 137.5" id="10,9" style=""></path><path d="M 114.2 123.1 L 114.2 154.8 L 145.9 154.8" id="12,10" style=""></path><path d="M 114.2 123.1 L 114.2 91.3 L 145.9 91.3" id="12,11" style=""></path><path d="M 82.5 89.9 L 82.5 123.1 L 114.2 123.1" id="13,12" style=""></path><path d="M 50.8 148.3 L 50.8 89.9 L 82.5 89.9" id="14,13" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(209.311,218.347)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r0</text></g><g class="toytree-TipLabel" transform="translate(209.311,195.248)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r1</text></g><g class="toytree-TipLabel" transform="translate(209.311,172.149)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r2</text></g><g class="toytree-TipLabel" transform="translate(209.311,149.05)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r3</text></g><g class="toytree-TipLabel" transform="translate(209.311,125.95)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r4</text></g><g class="toytree-TipLabel" transform="translate(209.311,102.851)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r5</text></g><g class="toytree-TipLabel" transform="translate(209.311,79.7518)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r6</text></g><g class="toytree-TipLabel" transform="translate(209.311,56.6526)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0">r7</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


### toytree.save
`toytree.save()` is the main entry point for writing a canvas to disk. The output format is inferred from the filename suffix. HTML and SVG are written directly through Toyplot. PDF and PNG are generated from the canonical SVG output, using CairoSVG when it is available and falling back to the older ReportLab backend otherwise.

In most cases you can simply save by suffix. If you need more control over PDF or PNG export, `toytree.save()` also accepts options such as `backend`, `dpi`, `scale`, `background_color`, `output_width`, and `output_height`.



```python
toytree.save(canvas, "/tmp/drawing.html")
toytree.save(canvas, "/tmp/drawing.svg")
toytree.save(canvas, "/tmp/drawing.pdf")
toytree.save(canvas, "/tmp/drawing.png")

toytree.save(canvas, "/tmp/drawing-print.pdf", backend="cairosvg", background_color="white")
toytree.save(canvas, "/tmp/drawing-large.png", output_width=1600, dpi=300)

```

### toyplot.render
Toyplot still exposes the lower-level renderers directly. That can be useful when you are already working at the Toyplot layer. For most tree figures, `toytree.save()` is the simpler public API because it keeps the format dispatch in one place and adds the CairoSVG PDF/PNG conversion path.



```python
# the default option
toyplot.html.render(canvas, "tmp/tree-plot.html")

# to save to SVG
import toyplot.svg

toyplot.svg.render(canvas, "tmp/tree-plot.svg")

# to save to PDF
import toyplot.pdf

toyplot.pdf.render(canvas, "tmp/tree-plot.pdf")

# to save to PNG
import toyplot.png

toyplot.png.render(canvas, "tmp/tree-plot.png")
```

### Formats

#### HTML
HTML rendering is the default format. This will save the figure as a vector graphic (SVG) wrapped in HTML with additional optional javascript wrapping for interactive features. This is the only format that will retain the interactive hover features. It can be opened in a browser, and can be convenient for viewing very large trees. 

#### SVG
SVG is a vector format that is best for saving and creating publication quality figures. You can further edit the figure in Illustrator or InkScape (recommended). 

#### PDF
The SVG figure can be embedded in a PDF for easier sharing with people who do not know how to view an SVG file.

#### PNG 
PNG is a raster format. Instead of saving the instructions for the drawing it reduces it to pixels. This can be convenient for reducing the size of a drawing, especially if it contains tons of data (millions of points). 
