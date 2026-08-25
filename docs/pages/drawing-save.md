<div class="nb-md-page-hook" aria-hidden="true"></div>

# Save and Export Drawings

`toytree.save()` is the public entry point for writing tree drawings to disk. It accepts the `Canvas` returned by `.draw()` and writes HTML, SVG, PDF, or PNG based on the filename suffix. Use this when you want to share a figure, keep an editable vector copy, or rasterize a drawing for slides and manuscripts.

In most workflows the only required step is to keep the returned `canvas` object and pass it to `toytree.save()`. SVG is usually the best archival format because it stays editable in vector-graphics tools. HTML preserves interactive hover behavior. PDF and PNG are convenient final-output formats for sharing or embedding in other documents.


```python
from pathlib import Path

import toytree

outdir = Path('/tmp/toytree-save-docs')
outdir.mkdir(exist_ok=True)
```

## Draw a figure

Save/export starts from a `Canvas`, so the first step is the same as any other drawing workflow: draw a tree and capture the returned objects.


```python
tree = toytree.rtree.unittree(ntips=8, seed=123)
canvas, axes, mark = tree.draw(
    width=350,
    height=250,
    node_sizes=8,
    tip_labels_align=True,
)
canvas
```




<div class="toyplot" id="tc5fa197e03d1421ea8daf8ae33ed49ab" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="350.0px" height="250.0px" viewBox="0 0 350.0 250.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tabe96d71c1844a58a0ed2dde3689d46e"><g class="toyplot-coordinates-Cartesian" id="t09c4546ff86e4206a3067a3666afe9f0"><clipPath id="td5af1bd7286d4afeb1fd0b14e1e54cc7"><rect x="35.0" y="35.0" width="280.0" height="180.0"></rect></clipPath><g clip-path="url(#td5af1bd7286d4afeb1fd0b14e1e54cc7)"><g class="toytree-mark-Toytree" id="t2ea9585676e240b48e911f13fd8cf2e5"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-linejoin:round;stroke-width:2.0;fill:none"><path d="M 86.7 178.3 L 86.7 192.9 L 274.7 192.9" id="9,0" style=""></path><path d="M 149.4 163.8 L 149.4 173.5 L 274.7 173.5" id="8,1" style=""></path><path d="M 149.4 163.8 L 149.4 154.1 L 274.7 154.1" id="8,2" style=""></path><path d="M 149.4 125.0 L 149.4 134.7 L 274.7 134.7" id="10,3" style=""></path><path d="M 149.4 125.0 L 149.4 115.3 L 274.7 115.3" id="10,4" style=""></path><path d="M 149.4 81.4 L 149.4 95.9 L 274.7 95.9" id="12,5" style=""></path><path d="M 212.0 66.8 L 212.0 76.5 L 274.7 76.5" id="11,6" style=""></path><path d="M 212.0 66.8 L 212.0 57.1 L 274.7 57.1" id="11,7" style=""></path><path d="M 86.7 178.3 L 86.7 163.8 L 149.4 163.8" id="9,8" style=""></path><path d="M 55.4 140.8 L 55.4 178.3 L 86.7 178.3" id="14,9" style=""></path><path d="M 86.7 103.2 L 86.7 125.0 L 149.4 125.0" id="13,10" style=""></path><path d="M 149.4 81.4 L 149.4 66.8 L 212.0 66.8" id="12,11" style=""></path><path d="M 86.7 103.2 L 86.7 81.4 L 149.4 81.4" id="13,12" style=""></path><path d="M 55.4 140.8 L 55.4 103.2 L 86.7 103.2" id="14,13" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-linejoin:round;stroke-width:2"><path d="M 274.7 192.9 L 274.7 192.9"></path><path d="M 274.7 173.5 L 274.7 173.5"></path><path d="M 274.7 154.1 L 274.7 154.1"></path><path d="M 274.7 134.7 L 274.7 134.7"></path><path d="M 274.7 115.3 L 274.7 115.3"></path><path d="M 274.7 95.9 L 274.7 95.9"></path><path d="M 274.7 76.5 L 274.7 76.5"></path><path d="M 274.7 57.1 L 274.7 57.1"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-8" transform="translate(149.392,163.777)"><circle r="4.0"></circle></g><g id="Node-9" transform="translate(86.7474,178.319)"><circle r="4.0"></circle></g><g id="Node-10" transform="translate(149.392,125)"><circle r="4.0"></circle></g><g id="Node-11" transform="translate(212.037,66.8343)"><circle r="4.0"></circle></g><g id="Node-12" transform="translate(149.392,81.3757)"><circle r="4.0"></circle></g><g id="Node-13" transform="translate(86.7474,103.188)"><circle r="4.0"></circle></g><g id="Node-14" transform="translate(55.425,140.753)"><circle r="4.0"></circle></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(274.682,192.86)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r0</text></g><g class="toytree-TipLabel" transform="translate(274.682,173.471)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(274.682,154.083)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(274.682,134.694)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(274.682,115.306)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(274.682,95.9171)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(274.682,76.5285)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(274.682,57.14)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



## Save by filename suffix

The simplest pattern is to choose an output suffix. If no suffix is given, `toytree.save()` defaults to HTML. That makes it easy to keep one interactive version and one publication-oriented vector or raster version of the same drawing.


```python
toytree.save(canvas, outdir / 'tree')
toytree.save(canvas, outdir / 'tree.svg')
toytree.save(canvas, outdir / 'tree.pdf')
toytree.save(canvas, outdir / 'tree.png')

sorted(path.name for path in outdir.iterdir())
```




    ['tree.html', 'tree.pdf', 'tree.png', 'tree.svg']



## Choosing an output format

- `HTML`: best when you want the interactive notebook or browser behavior, including hover content.
- `SVG`: best editable vector format for figures you may revise later in Inkscape or Illustrator.
- `PDF`: convenient vector output for sharing, printing, or embedding in manuscripts.
- `PNG`: raster output for slides, web use, and software that expects pixels instead of vector graphics.

## Control PDF and PNG export

For PDF and PNG, `toytree.save()` can also control the export backend and rasterization settings. The current implementation treats SVG as the canonical vector representation, and PDF/PNG export prefers CairoSVG when it is available. If CairoSVG is not installed, the function falls back to the older ReportLab path.

The most useful options are:

- `background_color`: temporarily override the canvas background during export.
- `dpi`: control rasterization density for PDF/PNG conversion.
- `scale`: uniformly scale PDF/PNG output.
- `output_width` and `output_height`: request a specific raster output size.
- `backend`: choose `"auto"`, `"cairosvg"`, or `"reportlab"` explicitly for PDF/PNG.


```python
toytree.save(canvas, outdir / 'tree-white-bg.pdf', background_color='white')
toytree.save(canvas, outdir / 'tree-large.png', dpi=300, output_width=1600)

sorted(path.name for path in outdir.iterdir())
```




    ['tree-large.png',
     'tree-white-bg.pdf',
     'tree.html',
     'tree.pdf',
     'tree.png',
     'tree.svg']



When you want to force a backend explicitly, use the same public function:

```python
toytree.save(canvas, 'figure.pdf', backend='cairosvg')
toytree.save(canvas, 'figure.png', backend='reportlab')
```

Use `reportlab` only when you need the legacy path or are working in an environment without CairoSVG.

## Related APIs

If you are already working directly with Toyplot, you can still call its lower-level renderers such as `toyplot.svg.render()` or `toyplot.html.render()`. For most `toytree` users, `toytree.save()` is the simpler API because it centralizes suffix handling and the PDF/PNG backend selection in one place.
