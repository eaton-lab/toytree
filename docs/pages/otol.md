<div class="nb-md-page-hook" aria-hidden="true"></div>

# otol - Open Tree of Life API

Citation: Smith, S.A., & Brown, J.W. (2018). Constructing a broadly inclusive seed plant phylogeny. American Journal of Botany, 105(3), 302-314.
"

Citation: Zuntini, A.R., Carruthers, T., Maurin, O. et al. (2024). Phylogenomics and the rise of the angiosperms. Nature 629, 843–850.
"ot_2304"
It covers nearly 8,000 genera (roughly 60% of all accepted angiosperm genera, representing >85% of species diversity) and is fossil dated.



```python
import toytree
import numpy as np
```


```python
SUBTREE_SPP_LIST = [
    "Amborella trichopoda",
    "Carex littledai",
    "Panicum virgatum",
    "Sorghum bicolor",
    "Zea mays",
    "Oryza sativa",
    "Brachypodium distachyon",
    "Hordeum vulgare",
    "Thinopyrum intermedium",
    "Aquilegia coerulea",
    "Amaranthus hypochondriacus",
    "Silene latifolia",
    "Arabidopsis thaliana",
    "Ligum trigynum",
    "Malus domestica",
    "Prunus persica",
    "Glycine max",
    "Medicago truncatula",
    "Trifolium repens",
    "Trofolium pratense",
    "Vaccinium darrowi",
    "Rhododendron vialli",
    "Cornus florida",
    "Hydrangea quercifolia",
    "Daucus carota",
    "Hydocotyle leucocephala",
    "Helianthus annuus",
    "Lactuca sativa",
    "Cuscuta campestris",
    "Solanum lycopersicum",
    "Catharanthus roseus",
    "Coffea arabica",
    "Abeliophyllum distichum",
    "Handroanthus impetiginosus",
    "Sesamum indicum",
    "Salvia mitiorrhiza",
    "Mimulus guttatus",
    "Rehmannia glutinosa",
    "Lindenbergia phillipensis",
    "Lindenbergia luchunensis",
    "Phelipanche aegyptiaca",
    "Orobanche cernua",
    "Orobanche cumana",
    "Orobanche gracilis",
    "Orobanche hederae",
    "Orobanche minor",
    "Striga hermonthica",
    "Striga asiatica",
    "Castilleja foliolosa",
    "Phtheirospermum japonicum",
    "Pedicularis groenlandica",
    "Pedicularis cranolopha",
]

```


```python
SUBTREE_SPP_LIST = [
    "Castilleja caudata",
    "Castilleja campestris",
    "Orobanche cumana",
    "Pedicularis anas",
    "Pedicularis groenlandica",
    "Pedicularis canadensis",
    "Pedicularis latituba",
    "Mimulus guttatus",
    "Aquilegia coerulea",
    "Delphinium exaltatum",
    "Amaranthus greggii",
    "Amaranthus tuberculatus",
    "Amaranthus tricolor",
    "Beta vulgaris",
    "Quercus minima",
    "Quercus macrocarpa",
    "Quercus mexicana",
    "Quercus virginiana",
    "Quercus alba",
    "Quercus rubra",
    "Quercus californica",
    "Boswellia sacra",
]

SUBTREE_GEN_LIST = [
    "Castilleja",
    "Orobanche",
    "Phelipanche",
    "Lindenbergia",
    "Rehmannia",
    "Pedicularis",
    "Mimulus",
    "Erythranthe",
    "Aquilegia",
    "Quercus",
    "Fagus",
    "Boswellia",
    "Delphinium",
]
```

### Get resolved names


```python
names = toytree.otol.resolve_taxonomic_names(
    SUBTREE_SPP_LIST,
    approximate=True,
    context="Angiosperms",
    include_synonyms=True,
    on_ambiguous='first', 
    on_unresolved="warn",
)
names
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>query</th>
      <th>status</th>
      <th>matched_name</th>
      <th>rank</th>
      <th>taxon_name</th>
      <th>ott_id</th>
      <th>ncbi_id</th>
      <th>is_synonym</th>
      <th>reason</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Castilleja caudata</td>
      <td>matched</td>
      <td>Castilleja caudata</td>
      <td>species</td>
      <td>Castilleja caudata</td>
      <td>338833</td>
      <td>395288</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Castilleja campestris</td>
      <td>matched</td>
      <td>Castilleja campestris</td>
      <td>species</td>
      <td>Castilleja campestris</td>
      <td>83184</td>
      <td>428863</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Orobanche cumana</td>
      <td>matched</td>
      <td>Orobanche cumana</td>
      <td>varietas</td>
      <td>Orobanche cernua var. cumana</td>
      <td>1010133</td>
      <td>78542</td>
      <td>True</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Pedicularis anas</td>
      <td>matched</td>
      <td>Pedicularis anas</td>
      <td>species</td>
      <td>Pedicularis anas</td>
      <td>1032908</td>
      <td>216507</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Pedicularis groenlandica</td>
      <td>matched</td>
      <td>Pedicularis groenlandica</td>
      <td>species</td>
      <td>Pedicularis groenlandica</td>
      <td>261492</td>
      <td>262426</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Pedicularis canadensis</td>
      <td>matched</td>
      <td>Pedicularis canadensis</td>
      <td>species</td>
      <td>Pedicularis canadensis</td>
      <td>3882309</td>
      <td>1325716</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Pedicularis latituba</td>
      <td>matched</td>
      <td>Pedicularis latituba</td>
      <td>species</td>
      <td>Pedicularis latituba</td>
      <td>869589</td>
      <td>1043536</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>7</th>
      <td>Mimulus guttatus</td>
      <td>matched</td>
      <td>Mimulus guttatus</td>
      <td>species</td>
      <td>Erythranthe guttata</td>
      <td>504496</td>
      <td>4155</td>
      <td>True</td>
      <td>resolved_first_of_2</td>
    </tr>
    <tr>
      <th>8</th>
      <td>Aquilegia coerulea</td>
      <td>matched</td>
      <td>Aquilegia coerulea</td>
      <td>species</td>
      <td>Aquilegia coerulea</td>
      <td>192307</td>
      <td>218851</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>9</th>
      <td>Delphinium exaltatum</td>
      <td>matched</td>
      <td>Delphinium exaltatum</td>
      <td>species</td>
      <td>Delphinium exaltatum</td>
      <td>693550</td>
      <td>46987</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>10</th>
      <td>Amaranthus greggii</td>
      <td>matched</td>
      <td>Amaranthus greggii</td>
      <td>species</td>
      <td>Amaranthus greggii</td>
      <td>151502</td>
      <td>240022</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>11</th>
      <td>Amaranthus tuberculatus</td>
      <td>matched</td>
      <td>Amaranthus tuberculatus</td>
      <td>species</td>
      <td>Amaranthus tuberculatus</td>
      <td>828461</td>
      <td>277990</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>12</th>
      <td>Amaranthus tricolor</td>
      <td>matched</td>
      <td>Amaranthus tricolor</td>
      <td>species</td>
      <td>Amaranthus tricolor</td>
      <td>653438</td>
      <td>29722</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>13</th>
      <td>Beta vulgaris</td>
      <td>matched</td>
      <td>Beta vulgaris</td>
      <td>species</td>
      <td>Beta vulgaris</td>
      <td>273185</td>
      <td>161934</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>14</th>
      <td>Quercus minima</td>
      <td>matched</td>
      <td>Quercus minima</td>
      <td>species</td>
      <td>Quercus minima</td>
      <td>117134</td>
      <td>262625</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>15</th>
      <td>Quercus macrocarpa</td>
      <td>matched</td>
      <td>Quercus macrocarpa</td>
      <td>species</td>
      <td>Quercus macrocarpa</td>
      <td>37377</td>
      <td>519047</td>
      <td>False</td>
      <td>resolved_first_of_2</td>
    </tr>
    <tr>
      <th>16</th>
      <td>Quercus mexicana</td>
      <td>matched</td>
      <td>Quercus mexicana</td>
      <td>species</td>
      <td>Quercus mexicana</td>
      <td>3930585</td>
      <td>1266341</td>
      <td>False</td>
      <td>resolved_first_of_2</td>
    </tr>
    <tr>
      <th>17</th>
      <td>Quercus virginiana</td>
      <td>matched</td>
      <td>Quercus virginiana</td>
      <td>species</td>
      <td>Quercus virginiana</td>
      <td>272703</td>
      <td>58333</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>18</th>
      <td>Quercus alba</td>
      <td>matched</td>
      <td>Quercus alba</td>
      <td>species</td>
      <td>Quercus alba</td>
      <td>791112</td>
      <td>3513</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>19</th>
      <td>Quercus rubra</td>
      <td>matched</td>
      <td>Quercus rubra</td>
      <td>species</td>
      <td>Quercus rubra</td>
      <td>791115</td>
      <td>3512</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>20</th>
      <td>Quercus californica</td>
      <td>matched</td>
      <td>Quercus californica</td>
      <td>species</td>
      <td>Quercus kelloggii</td>
      <td>403375</td>
      <td>97698</td>
      <td>True</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>21</th>
      <td>Boswellia sacra</td>
      <td>matched</td>
      <td>Boswellia sacra</td>
      <td>species</td>
      <td>Boswellia sacra</td>
      <td>815270</td>
      <td>173701</td>
      <td>False</td>
      <td>ok</td>
    </tr>
  </tbody>
</table>
</div>




```python
# toytree.otol.fetch_json_taxon_info(1041561)
```


```python
# toytree.otol.fetch_json_match_names("Striga asiatica")[0]['matches'][0]['taxon']
```

### Get induced tree


```python
ttree = toytree.otol.fetch_newick_subtree_from_taxonomy(names)
```


```python
ttree.draw('s', node_hover=True);
```


<div class="toyplot" id="t7a7b1eda83864e57880c0b0cd0e96535" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="522.956px" height="580.7px" viewBox="0 0 522.956 580.7" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t014ee742b04f42e0af18b94b96426f87"><g class="toyplot-coordinates-Cartesian" id="t828b1307c1b34e43b6c9157a818be29e"><clipPath id="tef16784e2b074e7ea0ac564fe1130ed5"><rect x="35.0" y="35.0" width="452.956" height="510.70000000000005"></rect></clipPath><g clip-path="url(#tef16784e2b074e7ea0ac564fe1130ed5)"><g class="toytree-mark-Toytree" id="tf3c6c99548e74f76a20bf8b5012198d6"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 166.4 510.2 L 166.4 521.2 L 184.2 521.2" id="22,0" style=""></path><path d="M 166.4 510.2 L 166.4 499.2 L 184.2 499.2" id="22,1" style=""></path><path d="M 148.5 433.3 L 148.5 477.2 L 184.2 477.2" id="24,2" style=""></path><path d="M 166.4 389.3 L 166.4 455.2 L 184.2 455.2" id="23,3" style=""></path><path d="M 166.4 389.3 L 166.4 433.3 L 184.2 433.3" id="23,4" style=""></path><path d="M 166.4 389.3 L 166.4 411.3 L 184.2 411.3" id="23,5" style=""></path><path d="M 166.4 389.3 L 166.4 389.3 L 184.2 389.3" id="23,6" style=""></path><path d="M 166.4 389.3 L 166.4 367.3 L 184.2 367.3" id="23,7" style=""></path><path d="M 166.4 389.3 L 166.4 345.3 L 184.2 345.3" id="23,8" style=""></path><path d="M 166.4 389.3 L 166.4 323.3 L 184.2 323.3" id="23,9" style=""></path><path d="M 112.7 273.9 L 112.7 301.3 L 184.2 301.3" id="29,10" style=""></path><path d="M 130.6 246.4 L 130.6 279.4 L 184.2 279.4" id="28,11" style=""></path><path d="M 166.4 246.4 L 166.4 257.4 L 184.2 257.4" id="25,12" style=""></path><path d="M 166.4 246.4 L 166.4 235.4 L 184.2 235.4" id="25,13" style=""></path><path d="M 166.4 180.4 L 166.4 213.4 L 184.2 213.4" id="26,14" style=""></path><path d="M 166.4 180.4 L 166.4 191.4 L 184.2 191.4" id="26,15" style=""></path><path d="M 166.4 180.4 L 166.4 169.4 L 184.2 169.4" id="26,16" style=""></path><path d="M 166.4 180.4 L 166.4 147.4 L 184.2 147.4" id="26,17" style=""></path><path d="M 148.5 103.5 L 148.5 125.5 L 184.2 125.5" id="31,18" style=""></path><path d="M 166.4 81.5 L 166.4 103.5 L 184.2 103.5" id="30,19" style=""></path><path d="M 166.4 81.5 L 166.4 81.5 L 184.2 81.5" id="30,20" style=""></path><path d="M 166.4 81.5 L 166.4 59.5 L 184.2 59.5" id="30,21" style=""></path><path d="M 59.0 410.6 L 59.0 510.2 L 166.4 510.2" id="34,22" style=""></path><path d="M 148.5 433.3 L 148.5 389.3 L 166.4 389.3" id="24,23" style=""></path><path d="M 76.9 311.0 L 76.9 433.3 L 148.5 433.3" id="33,24" style=""></path><path d="M 148.5 213.4 L 148.5 246.4 L 166.4 246.4" id="27,25" style=""></path><path d="M 148.5 213.4 L 148.5 180.4 L 166.4 180.4" id="27,26" style=""></path><path d="M 130.6 246.4 L 130.6 213.4 L 148.5 213.4" id="28,27" style=""></path><path d="M 112.7 273.9 L 112.7 246.4 L 130.6 246.4" id="29,28" style=""></path><path d="M 94.8 188.7 L 94.8 273.9 L 112.7 273.9" id="32,29" style=""></path><path d="M 148.5 103.5 L 148.5 81.5 L 166.4 81.5" id="31,30" style=""></path><path d="M 94.8 188.7 L 94.8 103.5 L 148.5 103.5" id="32,31" style=""></path><path d="M 76.9 311.0 L 76.9 188.7 L 94.8 188.7" id="33,32" style=""></path><path d="M 59.0 410.6 L 59.0 311.0 L 76.9 311.0" id="34,33" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(184.242,521.2)"><circle r="8.0"></circle></g><g id="Node-1" transform="translate(184.242,499.214)"><circle r="8.0"></circle></g><g id="Node-2" transform="translate(184.242,477.229)"><circle r="8.0"></circle></g><g id="Node-3" transform="translate(184.242,455.243)"><circle r="8.0"></circle></g><g id="Node-4" transform="translate(184.242,433.257)"><circle r="8.0"></circle></g><g id="Node-5" transform="translate(184.242,411.271)"><circle r="8.0"></circle></g><g id="Node-6" transform="translate(184.242,389.286)"><circle r="8.0"></circle></g><g id="Node-7" transform="translate(184.242,367.3)"><circle r="8.0"></circle></g><g id="Node-8" transform="translate(184.242,345.314)"><circle r="8.0"></circle></g><g id="Node-9" transform="translate(184.242,323.329)"><circle r="8.0"></circle></g><g id="Node-10" transform="translate(184.242,301.343)"><circle r="8.0"></circle></g><g id="Node-11" transform="translate(184.242,279.357)"><circle r="8.0"></circle></g><g id="Node-12" transform="translate(184.242,257.371)"><circle r="8.0"></circle></g><g id="Node-13" transform="translate(184.242,235.386)"><circle r="8.0"></circle></g><g id="Node-14" transform="translate(184.242,213.4)"><circle r="8.0"></circle></g><g id="Node-15" transform="translate(184.242,191.414)"><circle r="8.0"></circle></g><g id="Node-16" transform="translate(184.242,169.429)"><circle r="8.0"></circle></g><g id="Node-17" transform="translate(184.242,147.443)"><circle r="8.0"></circle></g><g id="Node-18" transform="translate(184.242,125.457)"><circle r="8.0"></circle></g><g id="Node-19" transform="translate(184.242,103.471)"><circle r="8.0"></circle></g><g id="Node-20" transform="translate(184.242,81.4857)"><circle r="8.0"></circle></g><g id="Node-21" transform="translate(184.242,59.5)"><circle r="8.0"></circle></g><g id="Node-22" transform="translate(166.355,510.207)"><circle r="8.0"></circle></g><g id="Node-23" transform="translate(166.355,389.286)"><circle r="8.0"></circle></g><g id="Node-24" transform="translate(148.469,433.257)"><circle r="8.0"></circle></g><g id="Node-25" transform="translate(166.355,246.379)"><circle r="8.0"></circle></g><g id="Node-26" transform="translate(166.355,180.421)"><circle r="8.0"></circle></g><g id="Node-27" transform="translate(148.469,213.4)"><circle r="8.0"></circle></g><g id="Node-28" transform="translate(130.583,246.379)"><circle r="8.0"></circle></g><g id="Node-29" transform="translate(112.697,273.861)"><circle r="8.0"></circle></g><g id="Node-30" transform="translate(166.355,81.4857)"><circle r="8.0"></circle></g><g id="Node-31" transform="translate(148.469,103.471)"><circle r="8.0"></circle></g><g id="Node-32" transform="translate(94.8108,188.666)"><circle r="8.0"></circle></g><g id="Node-33" transform="translate(76.9247,310.962)"><circle r="8.0"></circle></g><g id="Node-34" transform="translate(59.0385,410.584)"><circle r="8.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(184.242,521.2)"><title>idx: 0
dist: 27.4285714286
support: nan
height: 0
ott_id: 192307
ncbi_id: 218851
name: Aquilegia_coerulea</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(184.242,499.214)"><title>idx: 1
dist: 27.4285714286
support: nan
height: 0
ott_id: 693550
ncbi_id: 46987
name: Delphinium_exaltatum</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(184.242,477.229)"><title>idx: 2
dist: 26.4285714286
support: nan
height: 0
ott_id: 815270
ncbi_id: 173701
name: Boswellia_sacra</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(184.242,455.243)"><title>idx: 3
dist: 25.4285714286
support: nan
height: 0
ott_id: 403375
ncbi_id: 97698
name: Quercus_californica</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(184.242,433.257)"><title>idx: 4
dist: 25.4285714286
support: nan
height: 0
ott_id: 117134
ncbi_id: 262625
name: Quercus_minima</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(184.242,411.271)"><title>idx: 5
dist: 25.4285714286
support: nan
height: 0
ott_id: 37377
ncbi_id: 519047
name: Quercus_macrocarpa</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(184.242,389.286)"><title>idx: 6
dist: 25.4285714286
support: nan
height: 0
ott_id: 3930585
ncbi_id: 1266341
name: Quercus_mexicana</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(184.242,367.3)"><title>idx: 7
dist: 25.4285714286
support: nan
height: 0
ott_id: 272703
ncbi_id: 58333
name: Quercus_virginiana</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(184.242,345.314)"><title>idx: 8
dist: 25.4285714286
support: nan
height: 0
ott_id: 791112
ncbi_id: 3513
name: Quercus_alba</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(184.242,323.329)"><title>idx: 9
dist: 25.4285714286
support: nan
height: 0
ott_id: 791115
ncbi_id: 3512
name: Quercus_rubra</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(184.242,301.343)"><title>idx: 10
dist: 25.4285714286
support: nan
height: 0
ott_id: 504496
ncbi_id: 4155
name: Mimulus_guttatus</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(184.242,279.357)"><title>idx: 11
dist: 24.4285714286
support: nan
height: 0
ott_id: 1010133
ncbi_id: 78542
name: Orobanche_cumana</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(184.242,257.371)"><title>idx: 12
dist: 22.4285714286
support: nan
height: 0
ott_id: 338833
ncbi_id: 395288
name: Castilleja_caudata</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(184.242,235.386)"><title>idx: 13
dist: 22.4285714286
support: nan
height: 0
ott_id: 83184
ncbi_id: 428863
name: Castilleja_campestris</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(184.242,213.4)"><title>idx: 14
dist: 22.4285714286
support: nan
height: 0
ott_id: 1032908
ncbi_id: 216507
name: Pedicularis_anas</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g><g class="toytree-NodeLabel" transform="translate(184.242,191.414)"><title>idx: 15
dist: 22.4285714286
support: nan
height: 0
ott_id: 261492
ncbi_id: 262426
name: Pedicularis_groenlandica</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">15</text></g><g class="toytree-NodeLabel" transform="translate(184.242,169.429)"><title>idx: 16
dist: 22.4285714286
support: nan
height: 0
ott_id: 3882309
ncbi_id: 1325716
name: Pedicularis_canadensis</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">16</text></g><g class="toytree-NodeLabel" transform="translate(184.242,147.443)"><title>idx: 17
dist: 22.4285714286
support: nan
height: 0
ott_id: 869589
ncbi_id: 1043536
name: Pedicularis_latituba</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">17</text></g><g class="toytree-NodeLabel" transform="translate(184.242,125.457)"><title>idx: 18
dist: 25.4285714286
support: nan
height: 0
ott_id: 273185
ncbi_id: 161934
name: Beta_vulgaris</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">18</text></g><g class="toytree-NodeLabel" transform="translate(184.242,103.471)"><title>idx: 19
dist: 24.4285714286
support: nan
height: 0
ott_id: 653438
ncbi_id: 29722
name: Amaranthus_tricolor</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">19</text></g><g class="toytree-NodeLabel" transform="translate(184.242,81.4857)"><title>idx: 20
dist: 24.4285714286
support: nan
height: 0
ott_id: 151502
ncbi_id: 240022
name: Amaranthus_greggii</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">20</text></g><g class="toytree-NodeLabel" transform="translate(184.242,59.5)"><title>idx: 21
dist: 24.4285714286
support: nan
height: 0
ott_id: 828461
ncbi_id: 277990
name: Amaranthus_tuberculatus</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">21</text></g><g class="toytree-NodeLabel" transform="translate(166.355,510.207)"><title>idx: 22
dist: 1
support: nan
height: 27.4285714286
ott_id: 387826
ncbi_id: 3440
name: Ranunculaceae</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">22</text></g><g class="toytree-NodeLabel" transform="translate(166.355,389.286)"><title>idx: 23
dist: 1
support: nan
height: 25.4285714286
ott_id: 791121
ncbi_id: 3511
name: Quercus</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">23</text></g><g class="toytree-NodeLabel" transform="translate(148.469,433.257)"><title>idx: 24
dist: 1
support: nan
height: 26.4285714286
ott_id: 1008296
ncbi_id: 71275
name: rosids</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">24</text></g><g class="toytree-NodeLabel" transform="translate(166.355,246.379)"><title>idx: 25
dist: 1
support: nan
height: 22.4285714286
ott_id: 317400
ncbi_id: 46036
name: Castilleja</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">25</text></g><g class="toytree-NodeLabel" transform="translate(166.355,180.421)"><title>idx: 26
dist: 1
support: nan
height: 22.4285714286
ott_id: 989660
ncbi_id: 43174
name: Pedicularis</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">26</text></g><g class="toytree-NodeLabel" transform="translate(148.469,213.4)"><title>idx: 27
dist: 1
support: nan
height: 23.4285714286
ott_id: 5144557
ncbi_id: 1325730
name: Pedicularideae</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">27</text></g><g class="toytree-NodeLabel" transform="translate(130.583,246.379)"><title>idx: 28
dist: 1
support: nan
height: 24.4285714286
ott_id: 23373
ncbi_id: 91896
name: Orobanchaceae</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">28</text></g><g class="toytree-NodeLabel" transform="translate(112.697,273.861)"><title>idx: 29
dist: 1
support: nan
height: 25.4285714286
ott_id: 5264061
ncbi_id: nan
name: higher_core_Lamiales</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">29</text></g><g class="toytree-NodeLabel" transform="translate(166.355,81.4857)"><title>idx: 30
dist: 1
support: nan
height: 24.4285714286
ott_id: 317808
ncbi_id: 3564
name: Amaranthus</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">30</text></g><g class="toytree-NodeLabel" transform="translate(148.469,103.471)"><title>idx: 31
dist: 1
support: nan
height: 25.4285714286
ott_id: 216628
ncbi_id: 3524
name: Caryophyllales</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">31</text></g><g class="toytree-NodeLabel" transform="translate(94.8108,188.666)"><title>idx: 32
dist: 1
support: nan
height: 26.4285714286
ott_id: 5316182
ncbi_id: 1437201
name: ott5316182</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">32</text></g><g class="toytree-NodeLabel" transform="translate(76.9247,310.962)"><title>idx: 33
dist: 1
support: nan
height: 27.4285714286
ott_id: 5316182
ncbi_id: 1437201
name: Pentapetalae</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">33</text></g><g class="toytree-NodeLabel" transform="translate(59.0385,410.584)"><title>idx: 34
dist: 1
support: nan
height: 28.4285714286
ott_id: 5298374
ncbi_id: 1437183
name: Mesangiospermae</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">34</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(184.242,521.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Aquilegia_coerulea</text></g><g class="toytree-TipLabel" transform="translate(184.242,499.214)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Delphinium_exaltatum</text></g><g class="toytree-TipLabel" transform="translate(184.242,477.229)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Boswellia_sacra</text></g><g class="toytree-TipLabel" transform="translate(184.242,455.243)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_californica</text></g><g class="toytree-TipLabel" transform="translate(184.242,433.257)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_minima</text></g><g class="toytree-TipLabel" transform="translate(184.242,411.271)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_macrocarpa</text></g><g class="toytree-TipLabel" transform="translate(184.242,389.286)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_mexicana</text></g><g class="toytree-TipLabel" transform="translate(184.242,367.3)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_virginiana</text></g><g class="toytree-TipLabel" transform="translate(184.242,345.314)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_alba</text></g><g class="toytree-TipLabel" transform="translate(184.242,323.329)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_rubra</text></g><g class="toytree-TipLabel" transform="translate(184.242,301.343)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Mimulus_guttatus</text></g><g class="toytree-TipLabel" transform="translate(184.242,279.357)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Orobanche_cumana</text></g><g class="toytree-TipLabel" transform="translate(184.242,257.371)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Castilleja_caudata</text></g><g class="toytree-TipLabel" transform="translate(184.242,235.386)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Castilleja_campestris</text></g><g class="toytree-TipLabel" transform="translate(184.242,213.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_anas</text></g><g class="toytree-TipLabel" transform="translate(184.242,191.414)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_groenlandica</text></g><g class="toytree-TipLabel" transform="translate(184.242,169.429)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_canadensis</text></g><g class="toytree-TipLabel" transform="translate(184.242,147.443)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_latituba</text></g><g class="toytree-TipLabel" transform="translate(184.242,125.457)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Beta_vulgaris</text></g><g class="toytree-TipLabel" transform="translate(184.242,103.471)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Amaranthus_tricolor</text></g><g class="toytree-TipLabel" transform="translate(184.242,81.4857)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Amaranthus_greggii</text></g><g class="toytree-TipLabel" transform="translate(184.242,59.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Amaranthus_tuberculatus</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t8f7d4c3b30724222ab7eb0d9485fa219"><clipPath id="t461caff19c7e4540b814e23f852c9ea8"><rect x="35.0" y="35.0" width="452.95599999999996" height="510.70000000000005"></rect></clipPath><g clip-path="url(#t461caff19c7e4540b814e23f852c9ea8)"></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
itree = toytree.otol.fetch_newick_induced_tree_otol(names, constrain_by_taxonomy=True)
```


```python
itree.draw('s', node_hover=True);
```


<div class="toyplot" id="td9521ff6b0464ae4b1009fd2f7b4816b" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="522.956px" height="580.7px" viewBox="0 0 522.956 580.7" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t0b338a4a9bc2416d85ab9b9cc1c780ed"><g class="toyplot-coordinates-Cartesian" id="ta8432c711deb4ce69ecf9e681ec0fc38"><clipPath id="t55c98b4387c74972ae112e11eee4c1ba"><rect x="35.0" y="35.0" width="452.956" height="510.70000000000005"></rect></clipPath><g clip-path="url(#t55c98b4387c74972ae112e11eee4c1ba)"><g class="toytree-mark-Toytree" id="t464c97bba2484694b1d8385aeda88f94"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 166.4 510.2 L 166.4 521.2 L 184.2 521.2" id="22,0" style=""></path><path d="M 166.4 510.2 L 166.4 499.2 L 184.2 499.2" id="22,1" style=""></path><path d="M 112.7 437.4 L 112.7 477.2 L 184.2 477.2" id="29,2" style=""></path><path d="M 148.5 438.8 L 148.5 455.2 L 184.2 455.2" id="24,3" style=""></path><path d="M 166.4 422.3 L 166.4 433.3 L 184.2 433.3" id="23,4" style=""></path><path d="M 166.4 422.3 L 166.4 411.3 L 184.2 411.3" id="23,5" style=""></path><path d="M 166.4 378.3 L 166.4 389.3 L 184.2 389.3" id="25,6" style=""></path><path d="M 166.4 378.3 L 166.4 367.3 L 184.2 367.3" id="25,7" style=""></path><path d="M 166.4 334.3 L 166.4 345.3 L 184.2 345.3" id="26,8" style=""></path><path d="M 166.4 334.3 L 166.4 323.3 L 184.2 323.3" id="26,9" style=""></path><path d="M 130.6 282.1 L 130.6 301.3 L 184.2 301.3" id="32,10" style=""></path><path d="M 148.5 262.9 L 148.5 279.4 L 184.2 279.4" id="31,11" style=""></path><path d="M 166.4 246.4 L 166.4 257.4 L 184.2 257.4" id="30,12" style=""></path><path d="M 166.4 246.4 L 166.4 235.4 L 184.2 235.4" id="30,13" style=""></path><path d="M 112.7 185.9 L 112.7 213.4 L 184.2 213.4" id="37,14" style=""></path><path d="M 130.6 158.4 L 130.6 191.4 L 184.2 191.4" id="36,15" style=""></path><path d="M 166.4 158.4 L 166.4 169.4 L 184.2 169.4" id="33,16" style=""></path><path d="M 166.4 158.4 L 166.4 147.4 L 184.2 147.4" id="33,17" style=""></path><path d="M 166.4 92.5 L 166.4 125.5 L 184.2 125.5" id="34,18" style=""></path><path d="M 166.4 92.5 L 166.4 103.5 L 184.2 103.5" id="34,19" style=""></path><path d="M 166.4 92.5 L 166.4 81.5 L 184.2 81.5" id="34,20" style=""></path><path d="M 166.4 92.5 L 166.4 59.5 L 184.2 59.5" id="34,21" style=""></path><path d="M 59.0 423.0 L 59.0 510.2 L 166.4 510.2" id="40,22" style=""></path><path d="M 148.5 438.8 L 148.5 422.3 L 166.4 422.3" id="24,23" style=""></path><path d="M 130.6 397.5 L 130.6 438.8 L 148.5 438.8" id="28,24" style=""></path><path d="M 148.5 356.3 L 148.5 378.3 L 166.4 378.3" id="27,25" style=""></path><path d="M 148.5 356.3 L 148.5 334.3 L 166.4 334.3" id="27,26" style=""></path><path d="M 130.6 397.5 L 130.6 356.3 L 148.5 356.3" id="28,27" style=""></path><path d="M 112.7 437.4 L 112.7 397.5 L 130.6 397.5" id="29,28" style=""></path><path d="M 76.9 335.7 L 76.9 437.4 L 112.7 437.4" id="39,29" style=""></path><path d="M 148.5 262.9 L 148.5 246.4 L 166.4 246.4" id="31,30" style=""></path><path d="M 130.6 282.1 L 130.6 262.9 L 148.5 262.9" id="32,31" style=""></path><path d="M 94.8 234.0 L 94.8 282.1 L 130.6 282.1" id="38,32" style=""></path><path d="M 148.5 125.5 L 148.5 158.4 L 166.4 158.4" id="35,33" style=""></path><path d="M 148.5 125.5 L 148.5 92.5 L 166.4 92.5" id="35,34" style=""></path><path d="M 130.6 158.4 L 130.6 125.5 L 148.5 125.5" id="36,35" style=""></path><path d="M 112.7 185.9 L 112.7 158.4 L 130.6 158.4" id="37,36" style=""></path><path d="M 94.8 234.0 L 94.8 185.9 L 112.7 185.9" id="38,37" style=""></path><path d="M 76.9 335.7 L 76.9 234.0 L 94.8 234.0" id="39,38" style=""></path><path d="M 59.0 423.0 L 59.0 335.7 L 76.9 335.7" id="40,39" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(184.242,521.2)"><circle r="8.0"></circle></g><g id="Node-1" transform="translate(184.242,499.214)"><circle r="8.0"></circle></g><g id="Node-2" transform="translate(184.242,477.229)"><circle r="8.0"></circle></g><g id="Node-3" transform="translate(184.242,455.243)"><circle r="8.0"></circle></g><g id="Node-4" transform="translate(184.242,433.257)"><circle r="8.0"></circle></g><g id="Node-5" transform="translate(184.242,411.271)"><circle r="8.0"></circle></g><g id="Node-6" transform="translate(184.242,389.286)"><circle r="8.0"></circle></g><g id="Node-7" transform="translate(184.242,367.3)"><circle r="8.0"></circle></g><g id="Node-8" transform="translate(184.242,345.314)"><circle r="8.0"></circle></g><g id="Node-9" transform="translate(184.242,323.329)"><circle r="8.0"></circle></g><g id="Node-10" transform="translate(184.242,301.343)"><circle r="8.0"></circle></g><g id="Node-11" transform="translate(184.242,279.357)"><circle r="8.0"></circle></g><g id="Node-12" transform="translate(184.242,257.371)"><circle r="8.0"></circle></g><g id="Node-13" transform="translate(184.242,235.386)"><circle r="8.0"></circle></g><g id="Node-14" transform="translate(184.242,213.4)"><circle r="8.0"></circle></g><g id="Node-15" transform="translate(184.242,191.414)"><circle r="8.0"></circle></g><g id="Node-16" transform="translate(184.242,169.429)"><circle r="8.0"></circle></g><g id="Node-17" transform="translate(184.242,147.443)"><circle r="8.0"></circle></g><g id="Node-18" transform="translate(184.242,125.457)"><circle r="8.0"></circle></g><g id="Node-19" transform="translate(184.242,103.471)"><circle r="8.0"></circle></g><g id="Node-20" transform="translate(184.242,81.4857)"><circle r="8.0"></circle></g><g id="Node-21" transform="translate(184.242,59.5)"><circle r="8.0"></circle></g><g id="Node-22" transform="translate(166.355,510.207)"><circle r="8.0"></circle></g><g id="Node-23" transform="translate(166.355,422.264)"><circle r="8.0"></circle></g><g id="Node-24" transform="translate(148.469,438.754)"><circle r="8.0"></circle></g><g id="Node-25" transform="translate(166.355,378.293)"><circle r="8.0"></circle></g><g id="Node-26" transform="translate(166.355,334.321)"><circle r="8.0"></circle></g><g id="Node-27" transform="translate(148.469,356.307)"><circle r="8.0"></circle></g><g id="Node-28" transform="translate(130.583,397.53)"><circle r="8.0"></circle></g><g id="Node-29" transform="translate(112.697,437.379)"><circle r="8.0"></circle></g><g id="Node-30" transform="translate(166.355,246.379)"><circle r="8.0"></circle></g><g id="Node-31" transform="translate(148.469,262.868)"><circle r="8.0"></circle></g><g id="Node-32" transform="translate(130.583,282.105)"><circle r="8.0"></circle></g><g id="Node-33" transform="translate(166.355,158.436)"><circle r="8.0"></circle></g><g id="Node-34" transform="translate(166.355,92.4786)"><circle r="8.0"></circle></g><g id="Node-35" transform="translate(148.469,125.457)"><circle r="8.0"></circle></g><g id="Node-36" transform="translate(130.583,158.436)"><circle r="8.0"></circle></g><g id="Node-37" transform="translate(112.697,185.918)"><circle r="8.0"></circle></g><g id="Node-38" transform="translate(94.8108,234.012)"><circle r="8.0"></circle></g><g id="Node-39" transform="translate(76.9247,335.696)"><circle r="8.0"></circle></g><g id="Node-40" transform="translate(59.0385,422.951)"><circle r="8.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(184.242,521.2)"><title>idx: 0
dist: 29.4285714286
support: nan
height: 0
ott_id: 192307
ncbi_id: 218851
name: Aquilegia_coerulea</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(184.242,499.214)"><title>idx: 1
dist: 29.4285714286
support: nan
height: 0
ott_id: 693550
ncbi_id: 46987
name: Delphinium_exaltatum</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(184.242,477.229)"><title>idx: 2
dist: 28.4285714286
support: nan
height: 0
ott_id: 815270
ncbi_id: 173701
name: Boswellia_sacra</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(184.242,455.243)"><title>idx: 3
dist: 26.4285714286
support: nan
height: 0
ott_id: 403375
ncbi_id: 97698
name: Quercus_californica</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(184.242,433.257)"><title>idx: 4
dist: 25.4285714286
support: nan
height: 0
ott_id: 3930585
ncbi_id: 1266341
name: Quercus_mexicana</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(184.242,411.271)"><title>idx: 5
dist: 25.4285714286
support: nan
height: 0
ott_id: 791115
ncbi_id: 3512
name: Quercus_rubra</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(184.242,389.286)"><title>idx: 6
dist: 25.4285714286
support: nan
height: 0
ott_id: 37377
ncbi_id: 519047
name: Quercus_macrocarpa</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(184.242,367.3)"><title>idx: 7
dist: 25.4285714286
support: nan
height: 0
ott_id: 791112
ncbi_id: 3513
name: Quercus_alba</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(184.242,345.314)"><title>idx: 8
dist: 25.4285714286
support: nan
height: 0
ott_id: 117134
ncbi_id: 262625
name: Quercus_minima</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(184.242,323.329)"><title>idx: 9
dist: 25.4285714286
support: nan
height: 0
ott_id: 272703
ncbi_id: 58333
name: Quercus_virginiana</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(184.242,301.343)"><title>idx: 10
dist: 27.4285714286
support: nan
height: 0
ott_id: 273185
ncbi_id: 161934
name: Beta_vulgaris</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(184.242,279.357)"><title>idx: 11
dist: 26.4285714286
support: nan
height: 0
ott_id: 828461
ncbi_id: 277990
name: Amaranthus_tuberculatus</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(184.242,257.371)"><title>idx: 12
dist: 25.4285714286
support: nan
height: 0
ott_id: 653438
ncbi_id: 29722
name: Amaranthus_tricolor</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(184.242,235.386)"><title>idx: 13
dist: 25.4285714286
support: nan
height: 0
ott_id: 151502
ncbi_id: 240022
name: Amaranthus_greggii</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(184.242,213.4)"><title>idx: 14
dist: 27.4285714286
support: nan
height: 0
ott_id: 504496
ncbi_id: 4155
name: Mimulus_guttatus</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g><g class="toytree-NodeLabel" transform="translate(184.242,191.414)"><title>idx: 15
dist: 26.4285714286
support: nan
height: 0
ott_id: 1010133
ncbi_id: 78542
name: Orobanche_cumana</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">15</text></g><g class="toytree-NodeLabel" transform="translate(184.242,169.429)"><title>idx: 16
dist: 24.4285714286
support: nan
height: 0
ott_id: 338833
ncbi_id: 395288
name: Castilleja_caudata</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">16</text></g><g class="toytree-NodeLabel" transform="translate(184.242,147.443)"><title>idx: 17
dist: 24.4285714286
support: nan
height: 0
ott_id: 83184
ncbi_id: 428863
name: Castilleja_campestris</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">17</text></g><g class="toytree-NodeLabel" transform="translate(184.242,125.457)"><title>idx: 18
dist: 24.4285714286
support: nan
height: 0
ott_id: 1032908
ncbi_id: 216507
name: Pedicularis_anas</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">18</text></g><g class="toytree-NodeLabel" transform="translate(184.242,103.471)"><title>idx: 19
dist: 24.4285714286
support: nan
height: 0
ott_id: 261492
ncbi_id: 262426
name: Pedicularis_groenlandica</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">19</text></g><g class="toytree-NodeLabel" transform="translate(184.242,81.4857)"><title>idx: 20
dist: 24.4285714286
support: nan
height: 0
ott_id: 3882309
ncbi_id: 1325716
name: Pedicularis_canadensis</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">20</text></g><g class="toytree-NodeLabel" transform="translate(184.242,59.5)"><title>idx: 21
dist: 24.4285714286
support: nan
height: 0
ott_id: 869589
ncbi_id: 1043536
name: Pedicularis_latituba</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">21</text></g><g class="toytree-NodeLabel" transform="translate(166.355,510.207)"><title>idx: 22
dist: 1
support: nan
height: 29.4285714286
ott_id: 387826
ncbi_id: 3440
name: Ranunculaceae</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">22</text></g><g class="toytree-NodeLabel" transform="translate(166.355,422.264)"><title>idx: 23
dist: 1
support: nan
height: 25.4285714286
ott_id: nan
ncbi_id: nan
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">23</text></g><g class="toytree-NodeLabel" transform="translate(148.469,438.754)"><title>idx: 24
dist: 1
support: nan
height: 26.4285714286
ott_id: nan
ncbi_id: nan
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">24</text></g><g class="toytree-NodeLabel" transform="translate(166.355,378.293)"><title>idx: 25
dist: 1
support: nan
height: 25.4285714286
ott_id: nan
ncbi_id: nan
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">25</text></g><g class="toytree-NodeLabel" transform="translate(166.355,334.321)"><title>idx: 26
dist: 1
support: nan
height: 25.4285714286
ott_id: nan
ncbi_id: nan
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">26</text></g><g class="toytree-NodeLabel" transform="translate(148.469,356.307)"><title>idx: 27
dist: 1
support: nan
height: 26.4285714286
ott_id: nan
ncbi_id: nan
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">27</text></g><g class="toytree-NodeLabel" transform="translate(130.583,397.53)"><title>idx: 28
dist: 1
support: nan
height: 27.4285714286
ott_id: 791121
ncbi_id: 3511
name: Quercus</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">28</text></g><g class="toytree-NodeLabel" transform="translate(112.697,437.379)"><title>idx: 29
dist: 1
support: nan
height: 28.4285714286
ott_id: 1008296
ncbi_id: 71275
name: rosids</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">29</text></g><g class="toytree-NodeLabel" transform="translate(166.355,246.379)"><title>idx: 30
dist: 1
support: nan
height: 25.4285714286
ott_id: nan
ncbi_id: nan
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">30</text></g><g class="toytree-NodeLabel" transform="translate(148.469,262.868)"><title>idx: 31
dist: 1
support: nan
height: 26.4285714286
ott_id: 317808
ncbi_id: 3564
name: Amaranthus</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">31</text></g><g class="toytree-NodeLabel" transform="translate(130.583,282.105)"><title>idx: 32
dist: 1
support: nan
height: 27.4285714286
ott_id: 216628
ncbi_id: 3524
name: Caryophyllales</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">32</text></g><g class="toytree-NodeLabel" transform="translate(166.355,158.436)"><title>idx: 33
dist: 1
support: nan
height: 24.4285714286
ott_id: 317400
ncbi_id: 46036
name: Castilleja</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">33</text></g><g class="toytree-NodeLabel" transform="translate(166.355,92.4786)"><title>idx: 34
dist: 1
support: nan
height: 24.4285714286
ott_id: 989660
ncbi_id: 43174
name: Pedicularis</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">34</text></g><g class="toytree-NodeLabel" transform="translate(148.469,125.457)"><title>idx: 35
dist: 1
support: nan
height: 25.4285714286
ott_id: 5144557
ncbi_id: 1325730
name: Pedicularideae</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">35</text></g><g class="toytree-NodeLabel" transform="translate(130.583,158.436)"><title>idx: 36
dist: 1
support: nan
height: 26.4285714286
ott_id: 23373
ncbi_id: 91896
name: Orobanchaceae</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">36</text></g><g class="toytree-NodeLabel" transform="translate(112.697,185.918)"><title>idx: 37
dist: 1
support: nan
height: 27.4285714286
ott_id: 5264061
ncbi_id: nan
name: higher_core_Lamiales</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">37</text></g><g class="toytree-NodeLabel" transform="translate(94.8108,234.012)"><title>idx: 38
dist: 1
support: nan
height: 28.4285714286
ott_id: 5316182
ncbi_id: 1437201
name: ott5316182</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">38</text></g><g class="toytree-NodeLabel" transform="translate(76.9247,335.696)"><title>idx: 39
dist: 1
support: nan
height: 29.4285714286
ott_id: 5316182
ncbi_id: 1437201
name: Pentapetalae</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">39</text></g><g class="toytree-NodeLabel" transform="translate(59.0385,422.951)"><title>idx: 40
dist: 1
support: nan
height: 30.4285714286
ott_id: 5298374
ncbi_id: 1437183
name: Mesangiospermae</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">40</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(184.242,521.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Aquilegia_coerulea</text></g><g class="toytree-TipLabel" transform="translate(184.242,499.214)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Delphinium_exaltatum</text></g><g class="toytree-TipLabel" transform="translate(184.242,477.229)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Boswellia_sacra</text></g><g class="toytree-TipLabel" transform="translate(184.242,455.243)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_californica</text></g><g class="toytree-TipLabel" transform="translate(184.242,433.257)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_mexicana</text></g><g class="toytree-TipLabel" transform="translate(184.242,411.271)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_rubra</text></g><g class="toytree-TipLabel" transform="translate(184.242,389.286)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_macrocarpa</text></g><g class="toytree-TipLabel" transform="translate(184.242,367.3)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_alba</text></g><g class="toytree-TipLabel" transform="translate(184.242,345.314)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_minima</text></g><g class="toytree-TipLabel" transform="translate(184.242,323.329)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_virginiana</text></g><g class="toytree-TipLabel" transform="translate(184.242,301.343)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Beta_vulgaris</text></g><g class="toytree-TipLabel" transform="translate(184.242,279.357)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Amaranthus_tuberculatus</text></g><g class="toytree-TipLabel" transform="translate(184.242,257.371)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Amaranthus_tricolor</text></g><g class="toytree-TipLabel" transform="translate(184.242,235.386)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Amaranthus_greggii</text></g><g class="toytree-TipLabel" transform="translate(184.242,213.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Mimulus_guttatus</text></g><g class="toytree-TipLabel" transform="translate(184.242,191.414)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Orobanche_cumana</text></g><g class="toytree-TipLabel" transform="translate(184.242,169.429)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Castilleja_caudata</text></g><g class="toytree-TipLabel" transform="translate(184.242,147.443)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Castilleja_campestris</text></g><g class="toytree-TipLabel" transform="translate(184.242,125.457)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_anas</text></g><g class="toytree-TipLabel" transform="translate(184.242,103.471)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_groenlandica</text></g><g class="toytree-TipLabel" transform="translate(184.242,81.4857)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_canadensis</text></g><g class="toytree-TipLabel" transform="translate(184.242,59.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_latituba</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="ted63e59a1b1f480eb7257feee30dcd64"><clipPath id="t75605c10bf1f4f6489b0c2da0348743c"><rect x="35.0" y="35.0" width="452.95599999999996" height="510.70000000000005"></rect></clipPath><g clip-path="url(#t75605c10bf1f4f6489b0c2da0348743c)"></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
times = toytree.otol.get_timetree_node_ages(itree, max_pairs=3)
```

    TimeTree node-age retrieval completed with non-ok nodes: 7 total (7 unresolved, 0 errors).



```python
itree.set_node_data("height", dict(times.age)).ladderize().draw(scale_bar=True);
```


<div class="toyplot" id="te8362e085df14e1086ba80b62bf9f03d" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="715.1439999999999px" height="961.1199999999991px" viewBox="0 0 715.1439999999999 961.1199999999991" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="td482071916b44f8d807b524941435072"><g class="toyplot-coordinates-Cartesian" id="t65b309f1c1ff4fbf91dfe65e66721a13"><clipPath id="td832938063a04228a4616f19c7c21ffc"><rect x="35.0" y="35.0" width="645.1439999999999" height="891.1199999999991"></rect></clipPath><g clip-path="url(#td832938063a04228a4616f19c7c21ffc)"><g class="toytree-mark-Toytree" id="t97e9293476fc44938a128bd6e4e62788"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 51.0 840.4 L 51.0 903.9 L 316.7 903.9" id="96,0" style=""></path><path d="M 189.4 859.8 L 189.4 887.3 L 316.7 887.3" id="58,1" style=""></path><path d="M 285.7 858.3 L 285.7 870.7 L 316.7 870.7" id="53,2" style=""></path><path d="M 301.5 845.8 L 301.5 854.1 L 316.7 854.1" id="52,3" style=""></path><path d="M 301.5 845.8 L 301.5 837.5 L 316.7 837.5" id="52,4" style=""></path><path d="M 252.9 806.4 L 252.9 820.9 L 316.7 820.9" id="56,5" style=""></path><path d="M 271.9 791.9 L 271.9 804.3 L 316.7 804.3" id="55,6" style=""></path><path d="M 294.3 779.4 L 294.3 787.7 L 316.7 787.7" id="54,7" style=""></path><path d="M 294.3 779.4 L 294.3 771.1 L 316.7 771.1" id="54,8" style=""></path><path d="M 141.1 694.0 L 141.1 754.5 L 316.7 754.5" id="94,9" style=""></path><path d="M 170.1 718.4 L 170.1 737.9 L 316.7 737.9" id="65,10" style=""></path><path d="M 170.3 699.0 L 170.3 721.3 L 316.7 721.3" id="64,11" style=""></path><path d="M 258.0 696.4 L 258.0 704.7 L 316.7 704.7" id="59,12" style=""></path><path d="M 258.0 696.4 L 258.0 688.1 L 316.7 688.1" id="59,13" style=""></path><path d="M 242.5 657.0 L 242.5 671.5 L 316.7 671.5" id="62,14" style=""></path><path d="M 283.1 642.4 L 283.1 654.9 L 316.7 654.9" id="61,15" style=""></path><path d="M 299.1 630.0 L 299.1 638.3 L 316.7 638.3" id="60,16" style=""></path><path d="M 299.1 630.0 L 299.1 621.7 L 316.7 621.7" id="60,17" style=""></path><path d="M 236.8 596.8 L 236.8 605.1 L 316.7 605.1" id="66,18" style=""></path><path d="M 236.8 596.8 L 236.8 588.5 L 316.7 588.5" id="66,19" style=""></path><path d="M 185.9 563.6 L 185.9 571.9 L 316.7 571.9" id="67,20" style=""></path><path d="M 185.9 563.6 L 185.9 555.3 L 316.7 555.3" id="67,21" style=""></path><path d="M 271.2 530.4 L 271.2 538.7 L 316.7 538.7" id="68,22" style=""></path><path d="M 271.2 530.4 L 271.2 522.1 L 316.7 522.1" id="68,23" style=""></path><path d="M 234.8 497.2 L 234.8 505.5 L 316.7 505.5" id="69,24" style=""></path><path d="M 234.8 497.2 L 234.8 488.9 L 316.7 488.9" id="69,25" style=""></path><path d="M 245.0 464.0 L 245.0 472.3 L 316.7 472.3" id="71,26" style=""></path><path d="M 245.0 464.0 L 245.0 455.7 L 316.7 455.7" id="71,27" style=""></path><path d="M 219.2 430.8 L 219.2 439.1 L 316.7 439.1" id="72,28" style=""></path><path d="M 219.2 430.8 L 219.2 422.5 L 316.7 422.5" id="72,29" style=""></path><path d="M 214.8 397.5 L 214.8 405.8 L 316.7 405.8" id="73,30" style=""></path><path d="M 214.8 397.5 L 214.8 389.2 L 316.7 389.2" id="73,31" style=""></path><path d="M 231.6 351.1 L 231.6 372.6 L 316.7 372.6" id="88,32" style=""></path><path d="M 254.6 329.5 L 254.6 356.0 L 316.7 356.0" id="87,33" style=""></path><path d="M 254.6 329.5 L 254.6 339.4 L 316.7 339.4" id="87,34" style=""></path><path d="M 254.6 293.0 L 254.6 322.8 L 316.7 322.8" id="86,35" style=""></path><path d="M 254.6 263.3 L 254.6 306.2 L 316.7 306.2" id="85,36" style=""></path><path d="M 254.6 220.3 L 254.6 289.6 L 316.7 289.6" id="84,37" style=""></path><path d="M 254.6 220.3 L 254.6 273.0 L 316.7 273.0" id="84,38" style=""></path><path d="M 285.6 248.1 L 285.6 256.4 L 316.7 256.4" id="75,39" style=""></path><path d="M 285.6 248.1 L 285.6 239.8 L 316.7 239.8" id="75,40" style=""></path><path d="M 285.6 214.9 L 285.6 223.2 L 316.7 223.2" id="76,41" style=""></path><path d="M 285.6 214.9 L 285.6 206.6 L 316.7 206.6" id="76,42" style=""></path><path d="M 279.1 177.6 L 279.1 190.0 L 316.7 190.0" id="78,43" style=""></path><path d="M 297.9 165.1 L 297.9 173.4 L 316.7 173.4" id="77,44" style=""></path><path d="M 297.9 165.1 L 297.9 156.8 L 316.7 156.8" id="77,45" style=""></path><path d="M 270.7 118.4 L 270.7 140.2 L 316.7 140.2" id="83,46" style=""></path><path d="M 304.1 115.3 L 304.1 123.6 L 316.7 123.6" id="79,47" style=""></path><path d="M 304.1 115.3 L 304.1 107.0 L 316.7 107.0" id="79,48" style=""></path><path d="M 306.1 78.0 L 306.1 90.4 L 316.7 90.4" id="81,49" style=""></path><path d="M 306.1 65.5 L 306.1 73.8 L 316.7 73.8" id="80,50" style=""></path><path d="M 306.1 65.5 L 306.1 57.2 L 316.7 57.2" id="80,51" style=""></path><path d="M 285.7 858.3 L 285.7 845.8 L 301.5 845.8" id="53,52" style=""></path><path d="M 250.0 832.3 L 250.0 858.3 L 285.7 858.3" id="57,53" style=""></path><path d="M 271.9 791.9 L 271.9 779.4 L 294.3 779.4" id="55,54" style=""></path><path d="M 252.9 806.4 L 252.9 791.9 L 271.9 791.9" id="56,55" style=""></path><path d="M 250.0 832.3 L 250.0 806.4 L 252.9 806.4" id="57,56" style=""></path><path d="M 189.4 859.8 L 189.4 832.3 L 250.0 832.3" id="58,57" style=""></path><path d="M 100.1 776.9 L 100.1 859.8 L 189.4 859.8" id="95,58" style=""></path><path d="M 186.0 676.7 L 186.0 696.4 L 258.0 696.4" id="63,59" style=""></path><path d="M 283.1 642.4 L 283.1 630.0 L 299.1 630.0" id="61,60" style=""></path><path d="M 242.5 657.0 L 242.5 642.4 L 283.1 642.4" id="62,61" style=""></path><path d="M 186.0 676.7 L 186.0 657.0 L 242.5 657.0" id="63,62" style=""></path><path d="M 170.3 699.0 L 170.3 676.7 L 186.0 676.7" id="64,63" style=""></path><path d="M 170.1 718.4 L 170.1 699.0 L 170.3 699.0" id="65,64" style=""></path><path d="M 150.5 633.5 L 150.5 718.4 L 170.1 718.4" id="93,65" style=""></path><path d="M 159.8 548.5 L 159.8 596.8 L 236.8 596.8" id="92,66" style=""></path><path d="M 163.9 500.2 L 163.9 563.6 L 185.9 563.6" id="91,67" style=""></path><path d="M 200.7 513.8 L 200.7 530.4 L 271.2 530.4" id="70,68" style=""></path><path d="M 200.7 513.8 L 200.7 497.2 L 234.8 497.2" id="70,69" style=""></path><path d="M 163.9 500.2 L 163.9 513.8 L 200.7 513.8" id="91,70" style=""></path><path d="M 169.8 423.3 L 169.8 464.0 L 245.0 464.0" id="90,71" style=""></path><path d="M 208.5 414.2 L 208.5 430.8 L 219.2 430.8" id="74,72" style=""></path><path d="M 208.5 414.2 L 208.5 397.5 L 214.8 397.5" id="74,73" style=""></path><path d="M 208.5 382.6 L 208.5 414.2 L 208.5 414.2" id="89,74" style=""></path><path d="M 254.6 220.3 L 254.6 248.1 L 285.6 248.1" id="84,75" style=""></path><path d="M 254.6 220.3 L 254.6 214.9 L 285.6 214.9" id="84,76" style=""></path><path d="M 279.1 177.6 L 279.1 165.1 L 297.9 165.1" id="78,77" style=""></path><path d="M 254.6 220.3 L 254.6 177.6 L 279.1 177.6" id="84,78" style=""></path><path d="M 291.5 96.6 L 291.5 115.3 L 304.1 115.3" id="82,79" style=""></path><path d="M 306.1 78.0 L 306.1 65.5 L 306.1 65.5" id="81,80" style=""></path><path d="M 291.5 96.6 L 291.5 78.0 L 306.1 78.0" id="82,81" style=""></path><path d="M 270.7 118.4 L 270.7 96.6 L 291.5 96.6" id="83,82" style=""></path><path d="M 254.6 220.3 L 254.6 118.4 L 270.7 118.4" id="84,83" style=""></path><path d="M 254.6 263.3 L 254.6 220.3 L 254.6 220.3" id="85,84" style=""></path><path d="M 254.6 293.0 L 254.6 263.3 L 254.6 263.3" id="86,85" style=""></path><path d="M 254.6 329.5 L 254.6 293.0 L 254.6 293.0" id="87,86" style=""></path><path d="M 231.6 351.1 L 231.6 329.5 L 254.6 329.5" id="88,87" style=""></path><path d="M 208.5 382.6 L 208.5 351.1 L 231.6 351.1" id="89,88" style=""></path><path d="M 169.8 423.3 L 169.8 382.6 L 208.5 382.6" id="90,89" style=""></path><path d="M 163.9 500.2 L 163.9 423.3 L 169.8 423.3" id="91,90" style=""></path><path d="M 159.8 548.5 L 159.8 500.2 L 163.9 500.2" id="92,91" style=""></path><path d="M 150.5 633.5 L 150.5 548.5 L 159.8 548.5" id="93,92" style=""></path><path d="M 141.1 694.0 L 141.1 633.5 L 150.5 633.5" id="94,93" style=""></path><path d="M 100.1 776.9 L 100.1 694.0 L 141.1 694.0" id="95,94" style=""></path><path d="M 51.0 840.4 L 51.0 776.9 L 100.1 776.9" id="96,95" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(316.664,903.92)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Amborella_trichopoda</text></g><g class="toytree-TipLabel" transform="translate(316.664,887.318)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Carex_littledalei</text></g><g class="toytree-TipLabel" transform="translate(316.664,870.715)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Panicum_virgatum</text></g><g class="toytree-TipLabel" transform="translate(316.664,854.113)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Sorghum_bicolor</text></g><g class="toytree-TipLabel" transform="translate(316.664,837.511)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Zea_mays</text></g><g class="toytree-TipLabel" transform="translate(316.664,820.908)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Oryza_sativa</text></g><g class="toytree-TipLabel" transform="translate(316.664,804.306)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Brachypodium_distachyon</text></g><g class="toytree-TipLabel" transform="translate(316.664,787.704)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Hordeum_vulgare</text></g><g class="toytree-TipLabel" transform="translate(316.664,771.101)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Thinopyrum_intermedium</text></g><g class="toytree-TipLabel" transform="translate(316.664,754.499)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Aquilegia_coerulea</text></g><g class="toytree-TipLabel" transform="translate(316.664,737.896)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Arabidopsis_thaliana</text></g><g class="toytree-TipLabel" transform="translate(316.664,721.294)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Linum_trigynum</text></g><g class="toytree-TipLabel" transform="translate(316.664,704.692)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Malus_domestica</text></g><g class="toytree-TipLabel" transform="translate(316.664,688.089)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Prunus_persica</text></g><g class="toytree-TipLabel" transform="translate(316.664,671.487)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Glycine_max</text></g><g class="toytree-TipLabel" transform="translate(316.664,654.885)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Medicago_truncatula</text></g><g class="toytree-TipLabel" transform="translate(316.664,638.282)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Trifolium_repens</text></g><g class="toytree-TipLabel" transform="translate(316.664,621.68)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Trifolium_pratense</text></g><g class="toytree-TipLabel" transform="translate(316.664,605.078)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Amaranthus_hypochondriacus</text></g><g class="toytree-TipLabel" transform="translate(316.664,588.475)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Silene_latifolia</text></g><g class="toytree-TipLabel" transform="translate(316.664,571.873)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Cornus_florida</text></g><g class="toytree-TipLabel" transform="translate(316.664,555.271)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Hydrangea_quercifolia</text></g><g class="toytree-TipLabel" transform="translate(316.664,538.668)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Helianthus_annuus</text></g><g class="toytree-TipLabel" transform="translate(316.664,522.066)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Lactuca_sativa</text></g><g class="toytree-TipLabel" transform="translate(316.664,505.464)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Daucus_carota</text></g><g class="toytree-TipLabel" transform="translate(316.664,488.861)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Hydrocotyle_leucocephala</text></g><g class="toytree-TipLabel" transform="translate(316.664,472.259)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Vaccinium_darrowii</text></g><g class="toytree-TipLabel" transform="translate(316.664,455.656)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Rhododendron_vialii</text></g><g class="toytree-TipLabel" transform="translate(316.664,439.054)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Catharanthus_roseus</text></g><g class="toytree-TipLabel" transform="translate(316.664,422.452)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Coffea_arabica</text></g><g class="toytree-TipLabel" transform="translate(316.664,405.849)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Cuscuta_campestris</text></g><g class="toytree-TipLabel" transform="translate(316.664,389.247)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Solanum_lycopersicum</text></g><g class="toytree-TipLabel" transform="translate(316.664,372.645)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Mimulus_guttatus</text></g><g class="toytree-TipLabel" transform="translate(316.664,356.042)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Salvia_miltiorrhiza</text></g><g class="toytree-TipLabel" transform="translate(316.664,339.44)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Sesamum_indicum</text></g><g class="toytree-TipLabel" transform="translate(316.664,322.838)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Abeliophyllum_distichum</text></g><g class="toytree-TipLabel" transform="translate(316.664,306.235)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Handroanthus_impetiginosus</text></g><g class="toytree-TipLabel" transform="translate(316.664,289.633)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Rehmannia_glutinosa</text></g><g class="toytree-TipLabel" transform="translate(316.664,273.031)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Phtheirospermum_japonicum</text></g><g class="toytree-TipLabel" transform="translate(316.664,256.428)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Lindenbergia_philippensis</text></g><g class="toytree-TipLabel" transform="translate(316.664,239.826)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Lindenbergia_luchunensis</text></g><g class="toytree-TipLabel" transform="translate(316.664,223.224)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Striga_hermonthica</text></g><g class="toytree-TipLabel" transform="translate(316.664,206.621)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Striga_asiatica</text></g><g class="toytree-TipLabel" transform="translate(316.664,190.019)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Castilleja_foliolosa</text></g><g class="toytree-TipLabel" transform="translate(316.664,173.416)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_groenlandica</text></g><g class="toytree-TipLabel" transform="translate(316.664,156.814)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_cranolopha</text></g><g class="toytree-TipLabel" transform="translate(316.664,140.212)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Phelipanche_aegyptiaca</text></g><g class="toytree-TipLabel" transform="translate(316.664,123.609)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Orobanche_cernua</text></g><g class="toytree-TipLabel" transform="translate(316.664,107.007)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Orobanche_cumana</text></g><g class="toytree-TipLabel" transform="translate(316.664,90.4047)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Orobanche_gracilis</text></g><g class="toytree-TipLabel" transform="translate(316.664,73.8024)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Orobanche_hederae</text></g><g class="toytree-TipLabel" transform="translate(316.664,57.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Orobanche_minor</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="teab06bd91ac44a2bb785064e8decf777"><clipPath id="t9d0b349dce5b4a8388de687c23cfec6c"><rect x="35.0" y="35.0" width="645.1439999999999" height="891.1199999999991"></rect></clipPath><g clip-path="url(#t9d0b349dce5b4a8388de687c23cfec6c)"></g><g class="toyplot-coordinates-Axis" id="t0da6d39f924f4d398c5cdda360edc3e4" transform="translate(50.0,911.1199999999991)translate(0,15.0)"><line x1="0.9840063236809893" y1="0" x2="266.6640645063096" y2="0" style=""></line><g><line x1="22.383574388121243" y1="0" x2="22.383574388121243" y2="-5" style=""></line><line x1="63.096989407819315" y1="0" x2="63.096989407819315" y2="-5" style=""></line><line x1="103.81040442751738" y1="0" x2="103.81040442751738" y2="-5" style=""></line><line x1="144.52381944721543" y1="0" x2="144.52381944721543" y2="-5" style=""></line><line x1="185.2372344669135" y1="0" x2="185.2372344669135" y2="-5" style=""></line><line x1="225.95064948661158" y1="0" x2="225.95064948661158" y2="-5" style=""></line><line x1="266.6640645063096" y1="0" x2="266.6640645063096" y2="-5" style=""></line></g><g><g transform="translate(22.383574388121243,6)"><text x="-8.34" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">180</text></g><g transform="translate(63.096989407819315,6)"><text x="-8.34" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">150</text></g><g transform="translate(103.81040442751738,6)"><text x="-8.34" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">120</text></g><g transform="translate(144.52381944721543,6)"><text x="-5.56" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">90</text></g><g transform="translate(185.2372344669135,6)"><text x="-5.56" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">60</text></g><g transform="translate(225.95064948661158,6)"><text x="-5.56" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">30</text></g><g transform="translate(266.6640645063096,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "td482071916b44f8d807b524941435072";
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
        })(modules["toyplot.coordinates.Axis"],"t0da6d39f924f4d398c5cdda360edc3e4",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 256.780180678841, "min": -196.49351279716396}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 615.1439999999999, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>


## Fetching a study by Author or DOI


```python
toytree.otol.fetch_json_studies_by_author(["Zuntini, A.R."])

```


```python
toytree.otol.fetch_json_studies_by_doi('https://doi.org/10.1038/s41586-024-07324-0')

```




    [{'ot:studyId': 'ot_2304',
      'ot:studyPublicationReference': 'Zuntini, A.R., Carruthers, T., Maurin, O. et al. Phylogenomics and the rise of the angiosperms. Nature (2024). https://doi.org/10.1038/s41586-024-07324-0',
      'ot:curatorName': ['Emily Jane McTavish', 'Brian O&#x27;Meara'],
      'ot:studyYear': 2024,
      'ot:focalClade': 5268475,
      'ot:focalCladeOTTTaxonName': 'Archaeplastida',
      'ot:dataDeposit': 'https://www.gbif.org/dataset/4195e042-b632-47ba-9545-32a5e3033ff7',
      'ot:studyPublication': 'https://doi.org/10.1038/s41586-024-07324-0',
      'ot:tag': []}]




```python
# toytree.otol.fetch_json_induced_subtree(SUBTREE_SPP_LIST)

```


```python


```


```python
resolved = toytree.otol.resolve_taxonomic_names(
    SUBTREE_SPP_LIST,
    on_ambiguous="first",
    on_unresolved="raise",
)
nwk1 = toytree.otol.fetch_newick_induced_tree_otol(
    resolved, constrain_by_taxonomy=False
)

```


```python
toytree.tree(nwk1).draw('s');
toytree.tree(nwk1).mod.remove_unary_nodes().draw('s', node_hover=True);

```


<div class="toyplot" id="t1d50b8fbb7204466b1bf81d0a137b2bd" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="730.444px" height="362.2px" viewBox="0 0 730.444 362.2" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t1821790cc50f45bf8f91ba805074c1dc"><g class="toyplot-coordinates-Cartesian" id="te983c1dad6634dd4a91a8adcf04fa074"><clipPath id="t1c386cd3ec974332bae5555dea0cd42a"><rect x="35.0" y="35.0" width="660.444" height="292.2"></rect></clipPath><g clip-path="url(#t1c386cd3ec974332bae5555dea0cd42a)"><g class="toytree-mark-Toytree" id="t987b6ccff99c478dbf62bb1e8fec8ded"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 198.1 302.7 L 198.1 302.7 L 201.3 302.7" id="12,0" style=""></path><path d="M 198.1 280.6 L 198.1 280.6 L 201.3 280.6" id="32,1" style=""></path><path d="M 198.1 258.5 L 198.1 258.5 L 201.3 258.5" id="53,2" style=""></path><path d="M 198.1 236.4 L 198.1 236.4 L 201.3 236.4" id="72,3" style=""></path><path d="M 198.1 214.3 L 198.1 214.3 L 201.3 214.3" id="74,4" style=""></path><path d="M 198.1 192.2 L 198.1 192.2 L 201.3 192.2" id="83,5" style=""></path><path d="M 198.1 170.0 L 198.1 170.0 L 201.3 170.0" id="92,6" style=""></path><path d="M 139.7 154.4 L 139.7 147.9 L 201.3 147.9" id="99,7" style=""></path><path d="M 139.7 154.4 L 139.7 125.8 L 201.3 125.8" id="99,8" style=""></path><path d="M 110.6 129.1 L 110.6 103.7 L 201.3 103.7" id="108,9" style=""></path><path d="M 198.1 81.6 L 198.1 81.6 L 201.3 81.6" id="124,10" style=""></path><path d="M 198.1 59.5 L 198.1 59.5 L 201.3 59.5" id="142,11" style=""></path><path d="M 194.8 302.7 L 194.8 302.7 L 198.1 302.7" id="13,12" style=""></path><path d="M 191.6 302.7 L 191.6 302.7 L 194.8 302.7" id="14,13" style=""></path><path d="M 188.3 302.7 L 188.3 302.7 L 191.6 302.7" id="15,14" style=""></path><path d="M 185.1 302.7 L 185.1 302.7 L 188.3 302.7" id="16,15" style=""></path><path d="M 181.9 302.7 L 181.9 302.7 L 185.1 302.7" id="17,16" style=""></path><path d="M 178.6 302.7 L 178.6 302.7 L 181.9 302.7" id="18,17" style=""></path><path d="M 175.4 302.7 L 175.4 302.7 L 178.6 302.7" id="19,18" style=""></path><path d="M 172.1 302.7 L 172.1 302.7 L 175.4 302.7" id="20,19" style=""></path><path d="M 168.9 302.7 L 168.9 302.7 L 172.1 302.7" id="21,20" style=""></path><path d="M 165.7 302.7 L 165.7 302.7 L 168.9 302.7" id="22,21" style=""></path><path d="M 162.4 302.7 L 162.4 302.7 L 165.7 302.7" id="23,22" style=""></path><path d="M 159.2 302.7 L 159.2 302.7 L 162.4 302.7" id="24,23" style=""></path><path d="M 155.9 302.7 L 155.9 302.7 L 159.2 302.7" id="25,24" style=""></path><path d="M 152.7 302.7 L 152.7 302.7 L 155.9 302.7" id="26,25" style=""></path><path d="M 149.5 302.7 L 149.5 302.7 L 152.7 302.7" id="27,26" style=""></path><path d="M 146.2 302.7 L 146.2 302.7 L 149.5 302.7" id="28,27" style=""></path><path d="M 143.0 302.7 L 143.0 302.7 L 146.2 302.7" id="29,28" style=""></path><path d="M 139.7 302.7 L 139.7 302.7 L 143.0 302.7" id="30,29" style=""></path><path d="M 136.5 302.7 L 136.5 302.7 L 139.7 302.7" id="31,30" style=""></path><path d="M 133.3 291.6 L 133.3 302.7 L 136.5 302.7" id="47,31" style=""></path><path d="M 194.8 280.6 L 194.8 280.6 L 198.1 280.6" id="33,32" style=""></path><path d="M 191.6 280.6 L 191.6 280.6 L 194.8 280.6" id="34,33" style=""></path><path d="M 188.3 280.6 L 188.3 280.6 L 191.6 280.6" id="35,34" style=""></path><path d="M 185.1 280.6 L 185.1 280.6 L 188.3 280.6" id="36,35" style=""></path><path d="M 181.9 280.6 L 181.9 280.6 L 185.1 280.6" id="37,36" style=""></path><path d="M 178.6 280.6 L 178.6 280.6 L 181.9 280.6" id="38,37" style=""></path><path d="M 175.4 280.6 L 175.4 280.6 L 178.6 280.6" id="39,38" style=""></path><path d="M 172.1 280.6 L 172.1 280.6 L 175.4 280.6" id="40,39" style=""></path><path d="M 168.9 280.6 L 168.9 280.6 L 172.1 280.6" id="41,40" style=""></path><path d="M 165.7 280.6 L 165.7 280.6 L 168.9 280.6" id="42,41" style=""></path><path d="M 162.4 280.6 L 162.4 280.6 L 165.7 280.6" id="43,42" style=""></path><path d="M 159.2 280.6 L 159.2 280.6 L 162.4 280.6" id="44,43" style=""></path><path d="M 155.9 280.6 L 155.9 280.6 L 159.2 280.6" id="45,44" style=""></path><path d="M 152.7 280.6 L 152.7 280.6 L 155.9 280.6" id="46,45" style=""></path><path d="M 133.3 291.6 L 133.3 280.6 L 152.7 280.6" id="47,46" style=""></path><path d="M 130.0 291.6 L 130.0 291.6 L 133.3 291.6" id="48,47" style=""></path><path d="M 126.8 291.6 L 126.8 291.6 L 130.0 291.6" id="49,48" style=""></path><path d="M 123.5 291.6 L 123.5 291.6 L 126.8 291.6" id="50,49" style=""></path><path d="M 120.3 291.6 L 120.3 291.6 L 123.5 291.6" id="51,50" style=""></path><path d="M 117.1 291.6 L 117.1 291.6 L 120.3 291.6" id="52,51" style=""></path><path d="M 113.8 275.1 L 113.8 291.6 L 117.1 291.6" id="71,52" style=""></path><path d="M 194.8 258.5 L 194.8 258.5 L 198.1 258.5" id="54,53" style=""></path><path d="M 191.6 258.5 L 191.6 258.5 L 194.8 258.5" id="55,54" style=""></path><path d="M 188.3 258.5 L 188.3 258.5 L 191.6 258.5" id="56,55" style=""></path><path d="M 185.1 258.5 L 185.1 258.5 L 188.3 258.5" id="57,56" style=""></path><path d="M 181.9 258.5 L 181.9 258.5 L 185.1 258.5" id="58,57" style=""></path><path d="M 178.6 258.5 L 178.6 258.5 L 181.9 258.5" id="59,58" style=""></path><path d="M 175.4 258.5 L 175.4 258.5 L 178.6 258.5" id="60,59" style=""></path><path d="M 172.1 258.5 L 172.1 258.5 L 175.4 258.5" id="61,60" style=""></path><path d="M 168.9 258.5 L 168.9 258.5 L 172.1 258.5" id="62,61" style=""></path><path d="M 165.7 258.5 L 165.7 258.5 L 168.9 258.5" id="63,62" style=""></path><path d="M 162.4 258.5 L 162.4 258.5 L 165.7 258.5" id="64,63" style=""></path><path d="M 159.2 258.5 L 159.2 258.5 L 162.4 258.5" id="65,64" style=""></path><path d="M 155.9 258.5 L 155.9 258.5 L 159.2 258.5" id="66,65" style=""></path><path d="M 152.7 258.5 L 152.7 258.5 L 155.9 258.5" id="67,66" style=""></path><path d="M 149.5 258.5 L 149.5 258.5 L 152.7 258.5" id="68,67" style=""></path><path d="M 146.2 258.5 L 146.2 258.5 L 149.5 258.5" id="69,68" style=""></path><path d="M 143.0 258.5 L 143.0 258.5 L 146.2 258.5" id="70,69" style=""></path><path d="M 113.8 275.1 L 113.8 258.5 L 143.0 258.5" id="71,70" style=""></path><path d="M 71.7 202.1 L 71.7 275.1 L 113.8 275.1" id="120,71" style=""></path><path d="M 194.8 236.4 L 194.8 236.4 L 198.1 236.4" id="73,72" style=""></path><path d="M 178.6 225.3 L 178.6 236.4 L 194.8 236.4" id="80,73" style=""></path><path d="M 194.8 214.3 L 194.8 214.3 L 198.1 214.3" id="75,74" style=""></path><path d="M 191.6 214.3 L 191.6 214.3 L 194.8 214.3" id="76,75" style=""></path><path d="M 188.3 214.3 L 188.3 214.3 L 191.6 214.3" id="77,76" style=""></path><path d="M 185.1 214.3 L 185.1 214.3 L 188.3 214.3" id="78,77" style=""></path><path d="M 181.9 214.3 L 181.9 214.3 L 185.1 214.3" id="79,78" style=""></path><path d="M 178.6 225.3 L 178.6 214.3 L 181.9 214.3" id="80,79" style=""></path><path d="M 175.4 225.3 L 175.4 225.3 L 178.6 225.3" id="81,80" style=""></path><path d="M 172.1 225.3 L 172.1 225.3 L 175.4 225.3" id="82,81" style=""></path><path d="M 168.9 208.7 L 168.9 225.3 L 172.1 225.3" id="85,82" style=""></path><path d="M 194.8 192.2 L 194.8 192.2 L 198.1 192.2" id="84,83" style=""></path><path d="M 168.9 208.7 L 168.9 192.2 L 194.8 192.2" id="85,84" style=""></path><path d="M 165.7 208.7 L 165.7 208.7 L 168.9 208.7" id="86,85" style=""></path><path d="M 162.4 208.7 L 162.4 208.7 L 165.7 208.7" id="87,86" style=""></path><path d="M 159.2 208.7 L 159.2 208.7 L 162.4 208.7" id="88,87" style=""></path><path d="M 155.9 208.7 L 155.9 208.7 L 159.2 208.7" id="89,88" style=""></path><path d="M 152.7 208.7 L 152.7 208.7 L 155.9 208.7" id="90,89" style=""></path><path d="M 149.5 208.7 L 149.5 208.7 L 152.7 208.7" id="91,90" style=""></path><path d="M 146.2 189.4 L 146.2 208.7 L 149.5 208.7" id="97,91" style=""></path><path d="M 194.8 170.0 L 194.8 170.0 L 198.1 170.0" id="93,92" style=""></path><path d="M 191.6 170.0 L 191.6 170.0 L 194.8 170.0" id="94,93" style=""></path><path d="M 188.3 170.0 L 188.3 170.0 L 191.6 170.0" id="95,94" style=""></path><path d="M 185.1 170.0 L 185.1 170.0 L 188.3 170.0" id="96,95" style=""></path><path d="M 146.2 189.4 L 146.2 170.0 L 185.1 170.0" id="97,96" style=""></path><path d="M 143.0 189.4 L 143.0 189.4 L 146.2 189.4" id="98,97" style=""></path><path d="M 139.7 154.4 L 139.7 189.4 L 143.0 189.4" id="99,98" style=""></path><path d="M 136.5 154.4 L 136.5 154.4 L 139.7 154.4" id="100,99" style=""></path><path d="M 133.3 154.4 L 133.3 154.4 L 136.5 154.4" id="101,100" style=""></path><path d="M 130.0 154.4 L 130.0 154.4 L 133.3 154.4" id="102,101" style=""></path><path d="M 126.8 154.4 L 126.8 154.4 L 130.0 154.4" id="103,102" style=""></path><path d="M 123.5 154.4 L 123.5 154.4 L 126.8 154.4" id="104,103" style=""></path><path d="M 120.3 154.4 L 120.3 154.4 L 123.5 154.4" id="105,104" style=""></path><path d="M 117.1 154.4 L 117.1 154.4 L 120.3 154.4" id="106,105" style=""></path><path d="M 113.8 154.4 L 113.8 154.4 L 117.1 154.4" id="107,106" style=""></path><path d="M 110.6 129.1 L 110.6 154.4 L 113.8 154.4" id="108,107" style=""></path><path d="M 107.3 129.1 L 107.3 129.1 L 110.6 129.1" id="109,108" style=""></path><path d="M 104.1 129.1 L 104.1 129.1 L 107.3 129.1" id="110,109" style=""></path><path d="M 100.9 129.1 L 100.9 129.1 L 104.1 129.1" id="111,110" style=""></path><path d="M 97.6 129.1 L 97.6 129.1 L 100.9 129.1" id="112,111" style=""></path><path d="M 94.4 129.1 L 94.4 129.1 L 97.6 129.1" id="113,112" style=""></path><path d="M 91.1 129.1 L 91.1 129.1 L 94.4 129.1" id="114,113" style=""></path><path d="M 87.9 129.1 L 87.9 129.1 L 91.1 129.1" id="115,114" style=""></path><path d="M 84.7 129.1 L 84.7 129.1 L 87.9 129.1" id="116,115" style=""></path><path d="M 81.4 129.1 L 81.4 129.1 L 84.7 129.1" id="117,116" style=""></path><path d="M 78.2 129.1 L 78.2 129.1 L 81.4 129.1" id="118,117" style=""></path><path d="M 74.9 129.1 L 74.9 129.1 L 78.2 129.1" id="119,118" style=""></path><path d="M 71.7 202.1 L 71.7 129.1 L 74.9 129.1" id="120,119" style=""></path><path d="M 68.5 202.1 L 68.5 202.1 L 71.7 202.1" id="121,120" style=""></path><path d="M 65.2 202.1 L 65.2 202.1 L 68.5 202.1" id="122,121" style=""></path><path d="M 62.0 202.1 L 62.0 202.1 L 65.2 202.1" id="123,122" style=""></path><path d="M 58.7 136.3 L 58.7 202.1 L 62.0 202.1" id="165,123" style=""></path><path d="M 194.8 81.6 L 194.8 81.6 L 198.1 81.6" id="125,124" style=""></path><path d="M 191.6 81.6 L 191.6 81.6 L 194.8 81.6" id="126,125" style=""></path><path d="M 188.3 81.6 L 188.3 81.6 L 191.6 81.6" id="127,126" style=""></path><path d="M 185.1 81.6 L 185.1 81.6 L 188.3 81.6" id="128,127" style=""></path><path d="M 181.9 81.6 L 181.9 81.6 L 185.1 81.6" id="129,128" style=""></path><path d="M 178.6 81.6 L 178.6 81.6 L 181.9 81.6" id="130,129" style=""></path><path d="M 175.4 81.6 L 175.4 81.6 L 178.6 81.6" id="131,130" style=""></path><path d="M 172.1 81.6 L 172.1 81.6 L 175.4 81.6" id="132,131" style=""></path><path d="M 168.9 81.6 L 168.9 81.6 L 172.1 81.6" id="133,132" style=""></path><path d="M 165.7 81.6 L 165.7 81.6 L 168.9 81.6" id="134,133" style=""></path><path d="M 162.4 81.6 L 162.4 81.6 L 165.7 81.6" id="135,134" style=""></path><path d="M 159.2 81.6 L 159.2 81.6 L 162.4 81.6" id="136,135" style=""></path><path d="M 155.9 81.6 L 155.9 81.6 L 159.2 81.6" id="137,136" style=""></path><path d="M 152.7 81.6 L 152.7 81.6 L 155.9 81.6" id="138,137" style=""></path><path d="M 149.5 81.6 L 149.5 81.6 L 152.7 81.6" id="139,138" style=""></path><path d="M 146.2 81.6 L 146.2 81.6 L 149.5 81.6" id="140,139" style=""></path><path d="M 143.0 81.6 L 143.0 81.6 L 146.2 81.6" id="141,140" style=""></path><path d="M 139.7 70.6 L 139.7 81.6 L 143.0 81.6" id="156,141" style=""></path><path d="M 194.8 59.5 L 194.8 59.5 L 198.1 59.5" id="143,142" style=""></path><path d="M 191.6 59.5 L 191.6 59.5 L 194.8 59.5" id="144,143" style=""></path><path d="M 188.3 59.5 L 188.3 59.5 L 191.6 59.5" id="145,144" style=""></path><path d="M 185.1 59.5 L 185.1 59.5 L 188.3 59.5" id="146,145" style=""></path><path d="M 181.9 59.5 L 181.9 59.5 L 185.1 59.5" id="147,146" style=""></path><path d="M 178.6 59.5 L 178.6 59.5 L 181.9 59.5" id="148,147" style=""></path><path d="M 175.4 59.5 L 175.4 59.5 L 178.6 59.5" id="149,148" style=""></path><path d="M 172.1 59.5 L 172.1 59.5 L 175.4 59.5" id="150,149" style=""></path><path d="M 168.9 59.5 L 168.9 59.5 L 172.1 59.5" id="151,150" style=""></path><path d="M 165.7 59.5 L 165.7 59.5 L 168.9 59.5" id="152,151" style=""></path><path d="M 162.4 59.5 L 162.4 59.5 L 165.7 59.5" id="153,152" style=""></path><path d="M 159.2 59.5 L 159.2 59.5 L 162.4 59.5" id="154,153" style=""></path><path d="M 155.9 59.5 L 155.9 59.5 L 159.2 59.5" id="155,154" style=""></path><path d="M 139.7 70.6 L 139.7 59.5 L 155.9 59.5" id="156,155" style=""></path><path d="M 136.5 70.6 L 136.5 70.6 L 139.7 70.6" id="157,156" style=""></path><path d="M 133.3 70.6 L 133.3 70.6 L 136.5 70.6" id="158,157" style=""></path><path d="M 130.0 70.6 L 130.0 70.6 L 133.3 70.6" id="159,158" style=""></path><path d="M 126.8 70.6 L 126.8 70.6 L 130.0 70.6" id="160,159" style=""></path><path d="M 123.5 70.6 L 123.5 70.6 L 126.8 70.6" id="161,160" style=""></path><path d="M 120.3 70.6 L 120.3 70.6 L 123.5 70.6" id="162,161" style=""></path><path d="M 117.1 70.6 L 117.1 70.6 L 120.3 70.6" id="163,162" style=""></path><path d="M 113.8 70.6 L 113.8 70.6 L 117.1 70.6" id="164,163" style=""></path><path d="M 58.7 136.3 L 58.7 70.6 L 113.8 70.6" id="165,164" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(201.291,302.7)"><circle r="8.0"></circle></g><g id="Node-1" transform="translate(201.291,280.591)"><circle r="8.0"></circle></g><g id="Node-2" transform="translate(201.291,258.482)"><circle r="8.0"></circle></g><g id="Node-3" transform="translate(201.291,236.373)"><circle r="8.0"></circle></g><g id="Node-4" transform="translate(201.291,214.264)"><circle r="8.0"></circle></g><g id="Node-5" transform="translate(201.291,192.155)"><circle r="8.0"></circle></g><g id="Node-6" transform="translate(201.291,170.045)"><circle r="8.0"></circle></g><g id="Node-7" transform="translate(201.291,147.936)"><circle r="8.0"></circle></g><g id="Node-8" transform="translate(201.291,125.827)"><circle r="8.0"></circle></g><g id="Node-9" transform="translate(201.291,103.718)"><circle r="8.0"></circle></g><g id="Node-10" transform="translate(201.291,81.6091)"><circle r="8.0"></circle></g><g id="Node-11" transform="translate(201.291,59.5)"><circle r="8.0"></circle></g><g id="Node-12" transform="translate(198.051,302.7)"><circle r="8.0"></circle></g><g id="Node-13" transform="translate(194.811,302.7)"><circle r="8.0"></circle></g><g id="Node-14" transform="translate(191.571,302.7)"><circle r="8.0"></circle></g><g id="Node-15" transform="translate(188.331,302.7)"><circle r="8.0"></circle></g><g id="Node-16" transform="translate(185.091,302.7)"><circle r="8.0"></circle></g><g id="Node-17" transform="translate(181.852,302.7)"><circle r="8.0"></circle></g><g id="Node-18" transform="translate(178.612,302.7)"><circle r="8.0"></circle></g><g id="Node-19" transform="translate(175.372,302.7)"><circle r="8.0"></circle></g><g id="Node-20" transform="translate(172.132,302.7)"><circle r="8.0"></circle></g><g id="Node-21" transform="translate(168.892,302.7)"><circle r="8.0"></circle></g><g id="Node-22" transform="translate(165.652,302.7)"><circle r="8.0"></circle></g><g id="Node-23" transform="translate(162.413,302.7)"><circle r="8.0"></circle></g><g id="Node-24" transform="translate(159.173,302.7)"><circle r="8.0"></circle></g><g id="Node-25" transform="translate(155.933,302.7)"><circle r="8.0"></circle></g><g id="Node-26" transform="translate(152.693,302.7)"><circle r="8.0"></circle></g><g id="Node-27" transform="translate(149.453,302.7)"><circle r="8.0"></circle></g><g id="Node-28" transform="translate(146.213,302.7)"><circle r="8.0"></circle></g><g id="Node-29" transform="translate(142.974,302.7)"><circle r="8.0"></circle></g><g id="Node-30" transform="translate(139.734,302.7)"><circle r="8.0"></circle></g><g id="Node-31" transform="translate(136.494,302.7)"><circle r="8.0"></circle></g><g id="Node-32" transform="translate(198.051,280.591)"><circle r="8.0"></circle></g><g id="Node-33" transform="translate(194.811,280.591)"><circle r="8.0"></circle></g><g id="Node-34" transform="translate(191.571,280.591)"><circle r="8.0"></circle></g><g id="Node-35" transform="translate(188.331,280.591)"><circle r="8.0"></circle></g><g id="Node-36" transform="translate(185.091,280.591)"><circle r="8.0"></circle></g><g id="Node-37" transform="translate(181.852,280.591)"><circle r="8.0"></circle></g><g id="Node-38" transform="translate(178.612,280.591)"><circle r="8.0"></circle></g><g id="Node-39" transform="translate(175.372,280.591)"><circle r="8.0"></circle></g><g id="Node-40" transform="translate(172.132,280.591)"><circle r="8.0"></circle></g><g id="Node-41" transform="translate(168.892,280.591)"><circle r="8.0"></circle></g><g id="Node-42" transform="translate(165.652,280.591)"><circle r="8.0"></circle></g><g id="Node-43" transform="translate(162.413,280.591)"><circle r="8.0"></circle></g><g id="Node-44" transform="translate(159.173,280.591)"><circle r="8.0"></circle></g><g id="Node-45" transform="translate(155.933,280.591)"><circle r="8.0"></circle></g><g id="Node-46" transform="translate(152.693,280.591)"><circle r="8.0"></circle></g><g id="Node-47" transform="translate(133.254,291.645)"><circle r="8.0"></circle></g><g id="Node-48" transform="translate(130.014,291.645)"><circle r="8.0"></circle></g><g id="Node-49" transform="translate(126.774,291.645)"><circle r="8.0"></circle></g><g id="Node-50" transform="translate(123.535,291.645)"><circle r="8.0"></circle></g><g id="Node-51" transform="translate(120.295,291.645)"><circle r="8.0"></circle></g><g id="Node-52" transform="translate(117.055,291.645)"><circle r="8.0"></circle></g><g id="Node-53" transform="translate(198.051,258.482)"><circle r="8.0"></circle></g><g id="Node-54" transform="translate(194.811,258.482)"><circle r="8.0"></circle></g><g id="Node-55" transform="translate(191.571,258.482)"><circle r="8.0"></circle></g><g id="Node-56" transform="translate(188.331,258.482)"><circle r="8.0"></circle></g><g id="Node-57" transform="translate(185.091,258.482)"><circle r="8.0"></circle></g><g id="Node-58" transform="translate(181.852,258.482)"><circle r="8.0"></circle></g><g id="Node-59" transform="translate(178.612,258.482)"><circle r="8.0"></circle></g><g id="Node-60" transform="translate(175.372,258.482)"><circle r="8.0"></circle></g><g id="Node-61" transform="translate(172.132,258.482)"><circle r="8.0"></circle></g><g id="Node-62" transform="translate(168.892,258.482)"><circle r="8.0"></circle></g><g id="Node-63" transform="translate(165.652,258.482)"><circle r="8.0"></circle></g><g id="Node-64" transform="translate(162.413,258.482)"><circle r="8.0"></circle></g><g id="Node-65" transform="translate(159.173,258.482)"><circle r="8.0"></circle></g><g id="Node-66" transform="translate(155.933,258.482)"><circle r="8.0"></circle></g><g id="Node-67" transform="translate(152.693,258.482)"><circle r="8.0"></circle></g><g id="Node-68" transform="translate(149.453,258.482)"><circle r="8.0"></circle></g><g id="Node-69" transform="translate(146.213,258.482)"><circle r="8.0"></circle></g><g id="Node-70" transform="translate(142.974,258.482)"><circle r="8.0"></circle></g><g id="Node-71" transform="translate(113.815,275.064)"><circle r="8.0"></circle></g><g id="Node-72" transform="translate(198.051,236.373)"><circle r="8.0"></circle></g><g id="Node-73" transform="translate(194.811,236.373)"><circle r="8.0"></circle></g><g id="Node-74" transform="translate(198.051,214.264)"><circle r="8.0"></circle></g><g id="Node-75" transform="translate(194.811,214.264)"><circle r="8.0"></circle></g><g id="Node-76" transform="translate(191.571,214.264)"><circle r="8.0"></circle></g><g id="Node-77" transform="translate(188.331,214.264)"><circle r="8.0"></circle></g><g id="Node-78" transform="translate(185.091,214.264)"><circle r="8.0"></circle></g><g id="Node-79" transform="translate(181.852,214.264)"><circle r="8.0"></circle></g><g id="Node-80" transform="translate(178.612,225.318)"><circle r="8.0"></circle></g><g id="Node-81" transform="translate(175.372,225.318)"><circle r="8.0"></circle></g><g id="Node-82" transform="translate(172.132,225.318)"><circle r="8.0"></circle></g><g id="Node-83" transform="translate(198.051,192.155)"><circle r="8.0"></circle></g><g id="Node-84" transform="translate(194.811,192.155)"><circle r="8.0"></circle></g><g id="Node-85" transform="translate(168.892,208.736)"><circle r="8.0"></circle></g><g id="Node-86" transform="translate(165.652,208.736)"><circle r="8.0"></circle></g><g id="Node-87" transform="translate(162.413,208.736)"><circle r="8.0"></circle></g><g id="Node-88" transform="translate(159.173,208.736)"><circle r="8.0"></circle></g><g id="Node-89" transform="translate(155.933,208.736)"><circle r="8.0"></circle></g><g id="Node-90" transform="translate(152.693,208.736)"><circle r="8.0"></circle></g><g id="Node-91" transform="translate(149.453,208.736)"><circle r="8.0"></circle></g><g id="Node-92" transform="translate(198.051,170.045)"><circle r="8.0"></circle></g><g id="Node-93" transform="translate(194.811,170.045)"><circle r="8.0"></circle></g><g id="Node-94" transform="translate(191.571,170.045)"><circle r="8.0"></circle></g><g id="Node-95" transform="translate(188.331,170.045)"><circle r="8.0"></circle></g><g id="Node-96" transform="translate(185.091,170.045)"><circle r="8.0"></circle></g><g id="Node-97" transform="translate(146.213,189.391)"><circle r="8.0"></circle></g><g id="Node-98" transform="translate(142.974,189.391)"><circle r="8.0"></circle></g><g id="Node-99" transform="translate(139.734,154.385)"><circle r="8.0"></circle></g><g id="Node-100" transform="translate(136.494,154.385)"><circle r="8.0"></circle></g><g id="Node-101" transform="translate(133.254,154.385)"><circle r="8.0"></circle></g><g id="Node-102" transform="translate(130.014,154.385)"><circle r="8.0"></circle></g><g id="Node-103" transform="translate(126.774,154.385)"><circle r="8.0"></circle></g><g id="Node-104" transform="translate(123.535,154.385)"><circle r="8.0"></circle></g><g id="Node-105" transform="translate(120.295,154.385)"><circle r="8.0"></circle></g><g id="Node-106" transform="translate(117.055,154.385)"><circle r="8.0"></circle></g><g id="Node-107" transform="translate(113.815,154.385)"><circle r="8.0"></circle></g><g id="Node-108" transform="translate(110.575,129.052)"><circle r="8.0"></circle></g><g id="Node-109" transform="translate(107.335,129.052)"><circle r="8.0"></circle></g><g id="Node-110" transform="translate(104.096,129.052)"><circle r="8.0"></circle></g><g id="Node-111" transform="translate(100.856,129.052)"><circle r="8.0"></circle></g><g id="Node-112" transform="translate(97.6159,129.052)"><circle r="8.0"></circle></g><g id="Node-113" transform="translate(94.3761,129.052)"><circle r="8.0"></circle></g><g id="Node-114" transform="translate(91.1362,129.052)"><circle r="8.0"></circle></g><g id="Node-115" transform="translate(87.8964,129.052)"><circle r="8.0"></circle></g><g id="Node-116" transform="translate(84.6566,129.052)"><circle r="8.0"></circle></g><g id="Node-117" transform="translate(81.4167,129.052)"><circle r="8.0"></circle></g><g id="Node-118" transform="translate(78.1769,129.052)"><circle r="8.0"></circle></g><g id="Node-119" transform="translate(74.9371,129.052)"><circle r="8.0"></circle></g><g id="Node-120" transform="translate(71.6972,202.058)"><circle r="8.0"></circle></g><g id="Node-121" transform="translate(68.4574,202.058)"><circle r="8.0"></circle></g><g id="Node-122" transform="translate(65.2176,202.058)"><circle r="8.0"></circle></g><g id="Node-123" transform="translate(61.9777,202.058)"><circle r="8.0"></circle></g><g id="Node-124" transform="translate(198.051,81.6091)"><circle r="8.0"></circle></g><g id="Node-125" transform="translate(194.811,81.6091)"><circle r="8.0"></circle></g><g id="Node-126" transform="translate(191.571,81.6091)"><circle r="8.0"></circle></g><g id="Node-127" transform="translate(188.331,81.6091)"><circle r="8.0"></circle></g><g id="Node-128" transform="translate(185.091,81.6091)"><circle r="8.0"></circle></g><g id="Node-129" transform="translate(181.852,81.6091)"><circle r="8.0"></circle></g><g id="Node-130" transform="translate(178.612,81.6091)"><circle r="8.0"></circle></g><g id="Node-131" transform="translate(175.372,81.6091)"><circle r="8.0"></circle></g><g id="Node-132" transform="translate(172.132,81.6091)"><circle r="8.0"></circle></g><g id="Node-133" transform="translate(168.892,81.6091)"><circle r="8.0"></circle></g><g id="Node-134" transform="translate(165.652,81.6091)"><circle r="8.0"></circle></g><g id="Node-135" transform="translate(162.413,81.6091)"><circle r="8.0"></circle></g><g id="Node-136" transform="translate(159.173,81.6091)"><circle r="8.0"></circle></g><g id="Node-137" transform="translate(155.933,81.6091)"><circle r="8.0"></circle></g><g id="Node-138" transform="translate(152.693,81.6091)"><circle r="8.0"></circle></g><g id="Node-139" transform="translate(149.453,81.6091)"><circle r="8.0"></circle></g><g id="Node-140" transform="translate(146.213,81.6091)"><circle r="8.0"></circle></g><g id="Node-141" transform="translate(142.974,81.6091)"><circle r="8.0"></circle></g><g id="Node-142" transform="translate(198.051,59.5)"><circle r="8.0"></circle></g><g id="Node-143" transform="translate(194.811,59.5)"><circle r="8.0"></circle></g><g id="Node-144" transform="translate(191.571,59.5)"><circle r="8.0"></circle></g><g id="Node-145" transform="translate(188.331,59.5)"><circle r="8.0"></circle></g><g id="Node-146" transform="translate(185.091,59.5)"><circle r="8.0"></circle></g><g id="Node-147" transform="translate(181.852,59.5)"><circle r="8.0"></circle></g><g id="Node-148" transform="translate(178.612,59.5)"><circle r="8.0"></circle></g><g id="Node-149" transform="translate(175.372,59.5)"><circle r="8.0"></circle></g><g id="Node-150" transform="translate(172.132,59.5)"><circle r="8.0"></circle></g><g id="Node-151" transform="translate(168.892,59.5)"><circle r="8.0"></circle></g><g id="Node-152" transform="translate(165.652,59.5)"><circle r="8.0"></circle></g><g id="Node-153" transform="translate(162.413,59.5)"><circle r="8.0"></circle></g><g id="Node-154" transform="translate(159.173,59.5)"><circle r="8.0"></circle></g><g id="Node-155" transform="translate(155.933,59.5)"><circle r="8.0"></circle></g><g id="Node-156" transform="translate(139.734,70.5545)"><circle r="8.0"></circle></g><g id="Node-157" transform="translate(136.494,70.5545)"><circle r="8.0"></circle></g><g id="Node-158" transform="translate(133.254,70.5545)"><circle r="8.0"></circle></g><g id="Node-159" transform="translate(130.014,70.5545)"><circle r="8.0"></circle></g><g id="Node-160" transform="translate(126.774,70.5545)"><circle r="8.0"></circle></g><g id="Node-161" transform="translate(123.535,70.5545)"><circle r="8.0"></circle></g><g id="Node-162" transform="translate(120.295,70.5545)"><circle r="8.0"></circle></g><g id="Node-163" transform="translate(117.055,70.5545)"><circle r="8.0"></circle></g><g id="Node-164" transform="translate(113.815,70.5545)"><circle r="8.0"></circle></g><g id="Node-165" transform="translate(58.7379,136.306)"><circle r="8.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(201.291,302.7)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(201.291,280.591)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(201.291,258.482)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(201.291,236.373)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(201.291,214.264)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(201.291,192.155)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(201.291,170.045)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(201.291,147.936)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(201.291,125.827)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(201.291,103.718)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(201.291,81.6091)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(201.291,59.5)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(198.051,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(194.811,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(191.571,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g><g class="toytree-NodeLabel" transform="translate(188.331,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">15</text></g><g class="toytree-NodeLabel" transform="translate(185.091,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">16</text></g><g class="toytree-NodeLabel" transform="translate(181.852,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">17</text></g><g class="toytree-NodeLabel" transform="translate(178.612,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">18</text></g><g class="toytree-NodeLabel" transform="translate(175.372,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">19</text></g><g class="toytree-NodeLabel" transform="translate(172.132,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">20</text></g><g class="toytree-NodeLabel" transform="translate(168.892,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">21</text></g><g class="toytree-NodeLabel" transform="translate(165.652,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">22</text></g><g class="toytree-NodeLabel" transform="translate(162.413,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">23</text></g><g class="toytree-NodeLabel" transform="translate(159.173,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">24</text></g><g class="toytree-NodeLabel" transform="translate(155.933,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">25</text></g><g class="toytree-NodeLabel" transform="translate(152.693,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">26</text></g><g class="toytree-NodeLabel" transform="translate(149.453,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">27</text></g><g class="toytree-NodeLabel" transform="translate(146.213,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">28</text></g><g class="toytree-NodeLabel" transform="translate(142.974,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">29</text></g><g class="toytree-NodeLabel" transform="translate(139.734,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">30</text></g><g class="toytree-NodeLabel" transform="translate(136.494,302.7)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">31</text></g><g class="toytree-NodeLabel" transform="translate(198.051,280.591)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">32</text></g><g class="toytree-NodeLabel" transform="translate(194.811,280.591)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">33</text></g><g class="toytree-NodeLabel" transform="translate(191.571,280.591)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">34</text></g><g class="toytree-NodeLabel" transform="translate(188.331,280.591)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">35</text></g><g class="toytree-NodeLabel" transform="translate(185.091,280.591)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">36</text></g><g class="toytree-NodeLabel" transform="translate(181.852,280.591)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">37</text></g><g class="toytree-NodeLabel" transform="translate(178.612,280.591)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">38</text></g><g class="toytree-NodeLabel" transform="translate(175.372,280.591)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">39</text></g><g class="toytree-NodeLabel" transform="translate(172.132,280.591)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">40</text></g><g class="toytree-NodeLabel" transform="translate(168.892,280.591)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">41</text></g><g class="toytree-NodeLabel" transform="translate(165.652,280.591)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">42</text></g><g class="toytree-NodeLabel" transform="translate(162.413,280.591)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">43</text></g><g class="toytree-NodeLabel" transform="translate(159.173,280.591)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">44</text></g><g class="toytree-NodeLabel" transform="translate(155.933,280.591)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">45</text></g><g class="toytree-NodeLabel" transform="translate(152.693,280.591)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">46</text></g><g class="toytree-NodeLabel" transform="translate(133.254,291.645)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">47</text></g><g class="toytree-NodeLabel" transform="translate(130.014,291.645)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">48</text></g><g class="toytree-NodeLabel" transform="translate(126.774,291.645)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">49</text></g><g class="toytree-NodeLabel" transform="translate(123.535,291.645)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">50</text></g><g class="toytree-NodeLabel" transform="translate(120.295,291.645)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">51</text></g><g class="toytree-NodeLabel" transform="translate(117.055,291.645)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">52</text></g><g class="toytree-NodeLabel" transform="translate(198.051,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">53</text></g><g class="toytree-NodeLabel" transform="translate(194.811,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">54</text></g><g class="toytree-NodeLabel" transform="translate(191.571,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">55</text></g><g class="toytree-NodeLabel" transform="translate(188.331,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">56</text></g><g class="toytree-NodeLabel" transform="translate(185.091,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">57</text></g><g class="toytree-NodeLabel" transform="translate(181.852,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">58</text></g><g class="toytree-NodeLabel" transform="translate(178.612,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">59</text></g><g class="toytree-NodeLabel" transform="translate(175.372,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">60</text></g><g class="toytree-NodeLabel" transform="translate(172.132,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">61</text></g><g class="toytree-NodeLabel" transform="translate(168.892,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">62</text></g><g class="toytree-NodeLabel" transform="translate(165.652,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">63</text></g><g class="toytree-NodeLabel" transform="translate(162.413,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">64</text></g><g class="toytree-NodeLabel" transform="translate(159.173,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">65</text></g><g class="toytree-NodeLabel" transform="translate(155.933,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">66</text></g><g class="toytree-NodeLabel" transform="translate(152.693,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">67</text></g><g class="toytree-NodeLabel" transform="translate(149.453,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">68</text></g><g class="toytree-NodeLabel" transform="translate(146.213,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">69</text></g><g class="toytree-NodeLabel" transform="translate(142.974,258.482)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">70</text></g><g class="toytree-NodeLabel" transform="translate(113.815,275.064)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">71</text></g><g class="toytree-NodeLabel" transform="translate(198.051,236.373)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">72</text></g><g class="toytree-NodeLabel" transform="translate(194.811,236.373)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">73</text></g><g class="toytree-NodeLabel" transform="translate(198.051,214.264)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">74</text></g><g class="toytree-NodeLabel" transform="translate(194.811,214.264)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">75</text></g><g class="toytree-NodeLabel" transform="translate(191.571,214.264)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">76</text></g><g class="toytree-NodeLabel" transform="translate(188.331,214.264)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">77</text></g><g class="toytree-NodeLabel" transform="translate(185.091,214.264)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">78</text></g><g class="toytree-NodeLabel" transform="translate(181.852,214.264)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">79</text></g><g class="toytree-NodeLabel" transform="translate(178.612,225.318)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">80</text></g><g class="toytree-NodeLabel" transform="translate(175.372,225.318)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">81</text></g><g class="toytree-NodeLabel" transform="translate(172.132,225.318)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">82</text></g><g class="toytree-NodeLabel" transform="translate(198.051,192.155)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">83</text></g><g class="toytree-NodeLabel" transform="translate(194.811,192.155)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">84</text></g><g class="toytree-NodeLabel" transform="translate(168.892,208.736)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">85</text></g><g class="toytree-NodeLabel" transform="translate(165.652,208.736)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">86</text></g><g class="toytree-NodeLabel" transform="translate(162.413,208.736)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">87</text></g><g class="toytree-NodeLabel" transform="translate(159.173,208.736)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">88</text></g><g class="toytree-NodeLabel" transform="translate(155.933,208.736)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">89</text></g><g class="toytree-NodeLabel" transform="translate(152.693,208.736)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">90</text></g><g class="toytree-NodeLabel" transform="translate(149.453,208.736)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">91</text></g><g class="toytree-NodeLabel" transform="translate(198.051,170.045)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">92</text></g><g class="toytree-NodeLabel" transform="translate(194.811,170.045)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">93</text></g><g class="toytree-NodeLabel" transform="translate(191.571,170.045)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">94</text></g><g class="toytree-NodeLabel" transform="translate(188.331,170.045)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">95</text></g><g class="toytree-NodeLabel" transform="translate(185.091,170.045)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">96</text></g><g class="toytree-NodeLabel" transform="translate(146.213,189.391)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">97</text></g><g class="toytree-NodeLabel" transform="translate(142.974,189.391)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">98</text></g><g class="toytree-NodeLabel" transform="translate(139.734,154.385)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">99</text></g><g class="toytree-NodeLabel" transform="translate(136.494,154.385)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">100</text></g><g class="toytree-NodeLabel" transform="translate(133.254,154.385)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">101</text></g><g class="toytree-NodeLabel" transform="translate(130.014,154.385)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">102</text></g><g class="toytree-NodeLabel" transform="translate(126.774,154.385)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">103</text></g><g class="toytree-NodeLabel" transform="translate(123.535,154.385)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">104</text></g><g class="toytree-NodeLabel" transform="translate(120.295,154.385)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">105</text></g><g class="toytree-NodeLabel" transform="translate(117.055,154.385)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">106</text></g><g class="toytree-NodeLabel" transform="translate(113.815,154.385)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">107</text></g><g class="toytree-NodeLabel" transform="translate(110.575,129.052)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">108</text></g><g class="toytree-NodeLabel" transform="translate(107.335,129.052)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">109</text></g><g class="toytree-NodeLabel" transform="translate(104.096,129.052)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">110</text></g><g class="toytree-NodeLabel" transform="translate(100.856,129.052)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">111</text></g><g class="toytree-NodeLabel" transform="translate(97.6159,129.052)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">112</text></g><g class="toytree-NodeLabel" transform="translate(94.3761,129.052)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">113</text></g><g class="toytree-NodeLabel" transform="translate(91.1362,129.052)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">114</text></g><g class="toytree-NodeLabel" transform="translate(87.8964,129.052)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">115</text></g><g class="toytree-NodeLabel" transform="translate(84.6566,129.052)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">116</text></g><g class="toytree-NodeLabel" transform="translate(81.4167,129.052)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">117</text></g><g class="toytree-NodeLabel" transform="translate(78.1769,129.052)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">118</text></g><g class="toytree-NodeLabel" transform="translate(74.9371,129.052)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">119</text></g><g class="toytree-NodeLabel" transform="translate(71.6972,202.058)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">120</text></g><g class="toytree-NodeLabel" transform="translate(68.4574,202.058)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">121</text></g><g class="toytree-NodeLabel" transform="translate(65.2176,202.058)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">122</text></g><g class="toytree-NodeLabel" transform="translate(61.9777,202.058)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">123</text></g><g class="toytree-NodeLabel" transform="translate(198.051,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">124</text></g><g class="toytree-NodeLabel" transform="translate(194.811,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">125</text></g><g class="toytree-NodeLabel" transform="translate(191.571,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">126</text></g><g class="toytree-NodeLabel" transform="translate(188.331,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">127</text></g><g class="toytree-NodeLabel" transform="translate(185.091,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">128</text></g><g class="toytree-NodeLabel" transform="translate(181.852,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">129</text></g><g class="toytree-NodeLabel" transform="translate(178.612,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">130</text></g><g class="toytree-NodeLabel" transform="translate(175.372,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">131</text></g><g class="toytree-NodeLabel" transform="translate(172.132,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">132</text></g><g class="toytree-NodeLabel" transform="translate(168.892,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">133</text></g><g class="toytree-NodeLabel" transform="translate(165.652,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">134</text></g><g class="toytree-NodeLabel" transform="translate(162.413,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">135</text></g><g class="toytree-NodeLabel" transform="translate(159.173,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">136</text></g><g class="toytree-NodeLabel" transform="translate(155.933,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">137</text></g><g class="toytree-NodeLabel" transform="translate(152.693,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">138</text></g><g class="toytree-NodeLabel" transform="translate(149.453,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">139</text></g><g class="toytree-NodeLabel" transform="translate(146.213,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">140</text></g><g class="toytree-NodeLabel" transform="translate(142.974,81.6091)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">141</text></g><g class="toytree-NodeLabel" transform="translate(198.051,59.5)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">142</text></g><g class="toytree-NodeLabel" transform="translate(194.811,59.5)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">143</text></g><g class="toytree-NodeLabel" transform="translate(191.571,59.5)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">144</text></g><g class="toytree-NodeLabel" transform="translate(188.331,59.5)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">145</text></g><g class="toytree-NodeLabel" transform="translate(185.091,59.5)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">146</text></g><g class="toytree-NodeLabel" transform="translate(181.852,59.5)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">147</text></g><g class="toytree-NodeLabel" transform="translate(178.612,59.5)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">148</text></g><g class="toytree-NodeLabel" transform="translate(175.372,59.5)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">149</text></g><g class="toytree-NodeLabel" transform="translate(172.132,59.5)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">150</text></g><g class="toytree-NodeLabel" transform="translate(168.892,59.5)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">151</text></g><g class="toytree-NodeLabel" transform="translate(165.652,59.5)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">152</text></g><g class="toytree-NodeLabel" transform="translate(162.413,59.5)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">153</text></g><g class="toytree-NodeLabel" transform="translate(159.173,59.5)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">154</text></g><g class="toytree-NodeLabel" transform="translate(155.933,59.5)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">155</text></g><g class="toytree-NodeLabel" transform="translate(139.734,70.5545)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">156</text></g><g class="toytree-NodeLabel" transform="translate(136.494,70.5545)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">157</text></g><g class="toytree-NodeLabel" transform="translate(133.254,70.5545)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">158</text></g><g class="toytree-NodeLabel" transform="translate(130.014,70.5545)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">159</text></g><g class="toytree-NodeLabel" transform="translate(126.774,70.5545)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">160</text></g><g class="toytree-NodeLabel" transform="translate(123.535,70.5545)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">161</text></g><g class="toytree-NodeLabel" transform="translate(120.295,70.5545)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">162</text></g><g class="toytree-NodeLabel" transform="translate(117.055,70.5545)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">163</text></g><g class="toytree-NodeLabel" transform="translate(113.815,70.5545)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">164</text></g><g class="toytree-NodeLabel" transform="translate(58.7379,136.306)"><text x="-7.506" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">165</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(201.291,302.7)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Boswellia_sacra_ott815270</text></g><g class="toytree-TipLabel" transform="translate(201.291,280.591)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_minima_ott117134</text></g><g class="toytree-TipLabel" transform="translate(201.291,258.482)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Amaranthus_greggii_ott151502</text></g><g class="toytree-TipLabel" transform="translate(201.291,236.373)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_groenlandica_ott261492</text></g><g class="toytree-TipLabel" transform="translate(201.291,214.264)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Castilleja_campestris_ott83184</text></g><g class="toytree-TipLabel" transform="translate(201.291,192.155)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Orobanche_cernua_var._cumana_ott1010133</text></g><g class="toytree-TipLabel" transform="translate(201.291,170.045)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Erythranthe_guttata_ott504496</text></g><g class="toytree-TipLabel" transform="translate(201.291,147.936)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_latituba_ott869589</text></g><g class="toytree-TipLabel" transform="translate(201.291,125.827)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_anas_ott1032908</text></g><g class="toytree-TipLabel" transform="translate(201.291,103.718)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Castilleja_caudata_ott338833</text></g><g class="toytree-TipLabel" transform="translate(201.291,81.6091)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Delphinium_exaltatum_ott693550</text></g><g class="toytree-TipLabel" transform="translate(201.291,59.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Aquilegia_coerulea_ott192307</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t39e7bfe7c3dd482db685dbfea080ce1f"><clipPath id="t2a777b18df3a4b22982d9926aab21d86"><rect x="35.0" y="35.0" width="660.444" height="292.2"></rect></clipPath><g clip-path="url(#t2a777b18df3a4b22982d9926aab21d86)"></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



<div class="toyplot" id="ta77ba66d63b64aadab4f4a991e59c3b7" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="730.444px" height="362.2px" viewBox="0 0 730.444 362.2" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t64576962fc654b6d8259e08506ffe778"><g class="toyplot-coordinates-Cartesian" id="t00630a2e71e84aada07d846104eb1a7c"><clipPath id="te7280a96de7d4e8a9a4884dc78e9f309"><rect x="35.0" y="35.0" width="660.444" height="292.2"></rect></clipPath><g clip-path="url(#te7280a96de7d4e8a9a4884dc78e9f309)"><g class="toytree-mark-Toytree" id="tc6cab79fda76433784c67a98b1182b4d"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 180.9 291.6 L 180.9 302.7 L 201.3 302.7" id="12,0" style=""></path><path d="M 180.9 291.6 L 180.9 280.6 L 201.3 280.6" id="12,1" style=""></path><path d="M 160.6 275.1 L 160.6 258.5 L 201.3 258.5" id="13,2" style=""></path><path d="M 99.5 206.4 L 99.5 236.4 L 201.3 236.4" id="18,3" style=""></path><path d="M 119.8 176.5 L 119.8 214.3 L 201.3 214.3" id="17,4" style=""></path><path d="M 119.8 176.5 L 119.8 192.2 L 201.3 192.2" id="17,5" style=""></path><path d="M 180.9 159.0 L 180.9 170.0 L 201.3 170.0" id="14,6" style=""></path><path d="M 180.9 159.0 L 180.9 147.9 L 201.3 147.9" id="14,7" style=""></path><path d="M 160.6 142.4 L 160.6 125.8 L 201.3 125.8" id="15,8" style=""></path><path d="M 140.2 123.1 L 140.2 103.7 L 201.3 103.7" id="16,9" style=""></path><path d="M 180.9 70.6 L 180.9 81.6 L 201.3 81.6" id="20,10" style=""></path><path d="M 180.9 70.6 L 180.9 59.5 L 201.3 59.5" id="20,11" style=""></path><path d="M 160.6 275.1 L 160.6 291.6 L 180.9 291.6" id="13,12" style=""></path><path d="M 79.1 240.7 L 79.1 275.1 L 160.6 275.1" id="19,13" style=""></path><path d="M 160.6 142.4 L 160.6 159.0 L 180.9 159.0" id="15,14" style=""></path><path d="M 140.2 123.1 L 140.2 142.4 L 160.6 142.4" id="16,15" style=""></path><path d="M 119.8 176.5 L 119.8 123.1 L 140.2 123.1" id="17,16" style=""></path><path d="M 99.5 206.4 L 99.5 176.5 L 119.8 176.5" id="18,17" style=""></path><path d="M 79.1 240.7 L 79.1 206.4 L 99.5 206.4" id="19,18" style=""></path><path d="M 58.7 155.7 L 58.7 240.7 L 79.1 240.7" id="21,19" style=""></path><path d="M 58.7 155.7 L 58.7 70.6 L 180.9 70.6" id="21,20" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(201.291,302.7)"><circle r="8.0"></circle></g><g id="Node-1" transform="translate(201.291,280.591)"><circle r="8.0"></circle></g><g id="Node-2" transform="translate(201.291,258.482)"><circle r="8.0"></circle></g><g id="Node-3" transform="translate(201.291,236.373)"><circle r="8.0"></circle></g><g id="Node-4" transform="translate(201.291,214.264)"><circle r="8.0"></circle></g><g id="Node-5" transform="translate(201.291,192.155)"><circle r="8.0"></circle></g><g id="Node-6" transform="translate(201.291,170.045)"><circle r="8.0"></circle></g><g id="Node-7" transform="translate(201.291,147.936)"><circle r="8.0"></circle></g><g id="Node-8" transform="translate(201.291,125.827)"><circle r="8.0"></circle></g><g id="Node-9" transform="translate(201.291,103.718)"><circle r="8.0"></circle></g><g id="Node-10" transform="translate(201.291,81.6091)"><circle r="8.0"></circle></g><g id="Node-11" transform="translate(201.291,59.5)"><circle r="8.0"></circle></g><g id="Node-12" transform="translate(180.926,291.645)"><circle r="8.0"></circle></g><g id="Node-13" transform="translate(160.561,275.064)"><circle r="8.0"></circle></g><g id="Node-14" transform="translate(180.926,158.991)"><circle r="8.0"></circle></g><g id="Node-15" transform="translate(160.561,142.409)"><circle r="8.0"></circle></g><g id="Node-16" transform="translate(140.197,123.064)"><circle r="8.0"></circle></g><g id="Node-17" transform="translate(119.832,176.494)"><circle r="8.0"></circle></g><g id="Node-18" transform="translate(99.4672,206.433)"><circle r="8.0"></circle></g><g id="Node-19" transform="translate(79.1026,240.748)"><circle r="8.0"></circle></g><g id="Node-20" transform="translate(180.926,70.5545)"><circle r="8.0"></circle></g><g id="Node-21" transform="translate(58.7379,155.652)"><circle r="8.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(201.291,302.7)"><title>idx: 0
dist: 21
support: nan
height: 12
name: Boswellia_sacra_ott815270</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(201.291,280.591)"><title>idx: 1
dist: 16
support: nan
height: 17
name: Quercus_minima_ott117134</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(201.291,258.482)"><title>idx: 2
dist: 19
support: nan
height: 20
name: Amaranthus_greggii_ott151502</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(201.291,236.373)"><title>idx: 3
dist: 1
support: nan
height: 27
name: Castilleja_caudata_ott338833</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(201.291,214.264)"><title>idx: 4
dist: 1
support: nan
height: 18
name: Pedicularis_latituba_ott869589</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(201.291,192.155)"><title>idx: 5
dist: 1
support: nan
height: 18
name: Pedicularis_anas_ott1032908</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(201.291,170.045)"><title>idx: 6
dist: 3
support: nan
height: 4
name: Pedicularis_groenlandica_ott261492</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(201.291,147.936)"><title>idx: 7
dist: 7
support: nan
height: 0
name: Castilleja_campestris_ott83184</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(201.291,125.827)"><title>idx: 8
dist: 3
support: nan
height: 7
name: Orobanche_cernua_var._cumana_ott1010133</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(201.291,103.718)"><title>idx: 9
dist: 6
support: nan
height: 11
name: Erythranthe_guttata_ott504496</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(201.291,81.6091)"><title>idx: 10
dist: 19
support: nan
height: 16
name: Delphinium_exaltatum_ott693550</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(201.291,59.5)"><title>idx: 11
dist: 15
support: nan
height: 20
name: Aquilegia_coerulea_ott192307</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(180.926,291.645)"><title>idx: 12
dist: 6
support: nan
height: 33
name: mrcaott2ott371</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(160.561,275.064)"><title>idx: 13
dist: 1
support: nan
height: 39
name: mrcaott2ott557</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(180.926,158.991)"><title>idx: 14
dist: 3
support: nan
height: 7
name: mrcaott36252ott75219</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g><g class="toytree-NodeLabel" transform="translate(160.561,142.409)"><title>idx: 15
dist: 7
support: nan
height: 10
name: mrcaott1452ott23465</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">15</text></g><g class="toytree-NodeLabel" transform="translate(140.197,123.064)"><title>idx: 16
dist: 2
support: nan
height: 17
name: mrcaott1452ott39175</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">16</text></g><g class="toytree-NodeLabel" transform="translate(119.832,176.494)"><title>idx: 17
dist: 9
support: nan
height: 19
name: mrcaott1452ott33561</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">17</text></g><g class="toytree-NodeLabel" transform="translate(99.4672,206.433)"><title>idx: 18
dist: 12
support: nan
height: 28
name: 'Core_Lamialesott5263556'</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">18</text></g><g class="toytree-NodeLabel" transform="translate(79.1026,240.748)"><title>idx: 19
dist: 4
support: nan
height: 40
name: mrcaott2ott248</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">19</text></g><g class="toytree-NodeLabel" transform="translate(180.926,70.5545)"><title>idx: 20
dist: 9
support: nan
height: 35
name: mrcaott2441ott22673</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">20</text></g><g class="toytree-NodeLabel" transform="translate(58.7379,155.652)"><title>idx: 21
dist: 0
support: nan
height: 44
name: mrcaott2ott2441</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">21</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(201.291,302.7)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Boswellia_sacra_ott815270</text></g><g class="toytree-TipLabel" transform="translate(201.291,280.591)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_minima_ott117134</text></g><g class="toytree-TipLabel" transform="translate(201.291,258.482)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Amaranthus_greggii_ott151502</text></g><g class="toytree-TipLabel" transform="translate(201.291,236.373)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Castilleja_caudata_ott338833</text></g><g class="toytree-TipLabel" transform="translate(201.291,214.264)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_latituba_ott869589</text></g><g class="toytree-TipLabel" transform="translate(201.291,192.155)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_anas_ott1032908</text></g><g class="toytree-TipLabel" transform="translate(201.291,170.045)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_groenlandica_ott261492</text></g><g class="toytree-TipLabel" transform="translate(201.291,147.936)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Castilleja_campestris_ott83184</text></g><g class="toytree-TipLabel" transform="translate(201.291,125.827)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Orobanche_cernua_var._cumana_ott1010133</text></g><g class="toytree-TipLabel" transform="translate(201.291,103.718)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Erythranthe_guttata_ott504496</text></g><g class="toytree-TipLabel" transform="translate(201.291,81.6091)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Delphinium_exaltatum_ott693550</text></g><g class="toytree-TipLabel" transform="translate(201.291,59.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Aquilegia_coerulea_ott192307</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="t6a674971e5f845cebf8ec2eca51dc997"><clipPath id="t66b9ae71d45442a2bdc0d0437858adff"><rect x="35.0" y="35.0" width="660.444" height="292.2"></rect></clipPath><g clip-path="url(#t66b9ae71d45442a2bdc0d0437858adff)"></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
nwk2 = toytree.otol.fetch_newick_subtree_from_taxonomy(resolved)

```


```python
toytree.tree(nwk2).mod.remove_unary_nodes().draw('s', node_hover=True);

```


<div class="toyplot" id="t8041b71f184445deab53c2430cc910c5" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="730.444px" height="405.8999999999999px" viewBox="0 0 730.444 405.8999999999999" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t82f673a70fee453182a107c8eba03b45"><g class="toyplot-coordinates-Cartesian" id="tc7c98c97a44d45d69f557c4f77a1a887"><clipPath id="t373288a7a2dc471f9ba74efb14ce995c"><rect x="35.0" y="35.0" width="660.444" height="335.8999999999999"></rect></clipPath><g clip-path="url(#t373288a7a2dc471f9ba74efb14ce995c)"><g class="toytree-mark-Toytree" id="tc1226a92391c4158993ffd359ca92e61"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 153.8 317.0 L 153.8 346.4 L 201.3 346.4" id="15,0" style=""></path><path d="M 153.8 317.0 L 153.8 324.3 L 201.3 324.3" id="15,1" style=""></path><path d="M 177.5 280.2 L 177.5 302.3 L 201.3 302.3" id="14,2" style=""></path><path d="M 177.5 280.2 L 177.5 280.2 L 201.3 280.2" id="14,3" style=""></path><path d="M 177.5 280.2 L 177.5 258.1 L 201.3 258.1" id="14,4" style=""></path><path d="M 177.5 225.0 L 177.5 236.1 L 201.3 236.1" id="16,5" style=""></path><path d="M 177.5 225.0 L 177.5 214.0 L 201.3 214.0" id="16,6" style=""></path><path d="M 106.3 165.7 L 106.3 191.9 L 201.3 191.9" id="21,7" style=""></path><path d="M 130.0 139.5 L 130.0 169.8 L 201.3 169.8" id="20,8" style=""></path><path d="M 177.5 136.7 L 177.5 147.8 L 201.3 147.8" id="17,9" style=""></path><path d="M 177.5 136.7 L 177.5 125.7 L 201.3 125.7" id="17,10" style=""></path><path d="M 177.5 81.6 L 177.5 103.6 L 201.3 103.6" id="18,11" style=""></path><path d="M 177.5 81.6 L 177.5 81.6 L 201.3 81.6" id="18,12" style=""></path><path d="M 177.5 81.6 L 177.5 59.5 L 201.3 59.5" id="18,13" style=""></path><path d="M 153.8 317.0 L 153.8 280.2 L 177.5 280.2" id="15,14" style=""></path><path d="M 58.7 256.2 L 58.7 317.0 L 153.8 317.0" id="23,15" style=""></path><path d="M 82.5 195.4 L 82.5 225.0 L 177.5 225.0" id="22,16" style=""></path><path d="M 153.8 109.2 L 153.8 136.7 L 177.5 136.7" id="19,17" style=""></path><path d="M 153.8 109.2 L 153.8 81.6 L 177.5 81.6" id="19,18" style=""></path><path d="M 130.0 139.5 L 130.0 109.2 L 153.8 109.2" id="20,19" style=""></path><path d="M 106.3 165.7 L 106.3 139.5 L 130.0 139.5" id="21,20" style=""></path><path d="M 82.5 195.4 L 82.5 165.7 L 106.3 165.7" id="22,21" style=""></path><path d="M 58.7 256.2 L 58.7 195.4 L 82.5 195.4" id="23,22" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(201.291,346.4)"><circle r="8.0"></circle></g><g id="Node-1" transform="translate(201.291,324.331)"><circle r="8.0"></circle></g><g id="Node-2" transform="translate(201.291,302.262)"><circle r="8.0"></circle></g><g id="Node-3" transform="translate(201.291,280.192)"><circle r="8.0"></circle></g><g id="Node-4" transform="translate(201.291,258.123)"><circle r="8.0"></circle></g><g id="Node-5" transform="translate(201.291,236.054)"><circle r="8.0"></circle></g><g id="Node-6" transform="translate(201.291,213.985)"><circle r="8.0"></circle></g><g id="Node-7" transform="translate(201.291,191.915)"><circle r="8.0"></circle></g><g id="Node-8" transform="translate(201.291,169.846)"><circle r="8.0"></circle></g><g id="Node-9" transform="translate(201.291,147.777)"><circle r="8.0"></circle></g><g id="Node-10" transform="translate(201.291,125.708)"><circle r="8.0"></circle></g><g id="Node-11" transform="translate(201.291,103.638)"><circle r="8.0"></circle></g><g id="Node-12" transform="translate(201.291,81.5692)"><circle r="8.0"></circle></g><g id="Node-13" transform="translate(201.291,59.5)"><circle r="8.0"></circle></g><g id="Node-14" transform="translate(177.532,280.192)"><circle r="8.0"></circle></g><g id="Node-15" transform="translate(153.773,316.974)"><circle r="8.0"></circle></g><g id="Node-16" transform="translate(177.532,225.019)"><circle r="8.0"></circle></g><g id="Node-17" transform="translate(177.532,136.742)"><circle r="8.0"></circle></g><g id="Node-18" transform="translate(177.532,81.5692)"><circle r="8.0"></circle></g><g id="Node-19" transform="translate(153.773,109.156)"><circle r="8.0"></circle></g><g id="Node-20" transform="translate(130.014,139.501)"><circle r="8.0"></circle></g><g id="Node-21" transform="translate(106.255,165.708)"><circle r="8.0"></circle></g><g id="Node-22" transform="translate(82.4967,195.364)"><circle r="8.0"></circle></g><g id="Node-23" transform="translate(58.7379,256.169)"><circle r="8.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(201.291,346.4)"><title>idx: 0
dist: 1
support: nan
height: 4
name: Boswellia_sacra_ott815270</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(201.291,324.331)"><title>idx: 1
dist: 1
support: nan
height: 4
name: Amaranthus_greggii_ott151502</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(201.291,302.262)"><title>idx: 2
dist: 1
support: nan
height: 3
name: Quercus_alba_ott791112</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(201.291,280.192)"><title>idx: 3
dist: 1
support: nan
height: 3
name: Quercus_minima_ott117134</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(201.291,258.123)"><title>idx: 4
dist: 1
support: nan
height: 3
name: Quercus_virginiana_ott272703</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(201.291,236.054)"><title>idx: 5
dist: 1
support: nan
height: 3
name: Aquilegia_coerulea_ott192307</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(201.291,213.985)"><title>idx: 6
dist: 1
support: nan
height: 3
name: Delphinium_exaltatum_ott693550</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(201.291,191.915)"><title>idx: 7
dist: 1
support: nan
height: 3
name: Erythranthe_guttata_ott504496</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(201.291,169.846)"><title>idx: 8
dist: 1
support: nan
height: 2
name: Orobanche_cernua_var._cumana_ott1010133</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(201.291,147.777)"><title>idx: 9
dist: 1
support: nan
height: 0
name: Castilleja_caudata_ott338833</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(201.291,125.708)"><title>idx: 10
dist: 1
support: nan
height: 0
name: Castilleja_campestris_ott83184</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(201.291,103.638)"><title>idx: 11
dist: 1
support: nan
height: 0
name: Pedicularis_latituba_ott869589</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(201.291,81.5692)"><title>idx: 12
dist: 1
support: nan
height: 0
name: Pedicularis_anas_ott1032908</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(201.291,59.5)"><title>idx: 13
dist: 1
support: nan
height: 0
name: Pedicularis_groenlandica_ott261492</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(177.532,280.192)"><title>idx: 14
dist: 1
support: nan
height: 4
name: Quercus_ott791121</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g><g class="toytree-NodeLabel" transform="translate(153.773,316.974)"><title>idx: 15
dist: 1
support: nan
height: 5
name: Magnoliopsida_ott99252</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">15</text></g><g class="toytree-NodeLabel" transform="translate(177.532,225.019)"><title>idx: 16
dist: 1
support: nan
height: 4
name: Ranunculaceae_ott387826</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">16</text></g><g class="toytree-NodeLabel" transform="translate(177.532,136.742)"><title>idx: 17
dist: 1
support: nan
height: 1
name: Castilleja_ott317400</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">17</text></g><g class="toytree-NodeLabel" transform="translate(177.532,81.5692)"><title>idx: 18
dist: 1
support: nan
height: 1
name: Pedicularis_ott989660</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">18</text></g><g class="toytree-NodeLabel" transform="translate(153.773,109.156)"><title>idx: 19
dist: 1
support: nan
height: 2
name: Pedicularideae_ott5144557</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">19</text></g><g class="toytree-NodeLabel" transform="translate(130.014,139.501)"><title>idx: 20
dist: 1
support: nan
height: 3
name: Orobanchaceae_ott23373</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">20</text></g><g class="toytree-NodeLabel" transform="translate(106.255,165.708)"><title>idx: 21
dist: 1
support: nan
height: 4
name: Lamiales_ott23736</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">21</text></g><g class="toytree-NodeLabel" transform="translate(82.4967,195.364)"><title>idx: 22
dist: 1
support: nan
height: 5
name: Magnoliopsida_ott99252</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">22</text></g><g class="toytree-NodeLabel" transform="translate(58.7379,256.169)"><title>idx: 23
dist: 0
support: nan
height: 6
name: Magnoliopsida_ott99252</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">23</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(201.291,346.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Boswellia_sacra_ott815270</text></g><g class="toytree-TipLabel" transform="translate(201.291,324.331)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Amaranthus_greggii_ott151502</text></g><g class="toytree-TipLabel" transform="translate(201.291,302.262)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_alba_ott791112</text></g><g class="toytree-TipLabel" transform="translate(201.291,280.192)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_minima_ott117134</text></g><g class="toytree-TipLabel" transform="translate(201.291,258.123)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_virginiana_ott272703</text></g><g class="toytree-TipLabel" transform="translate(201.291,236.054)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Aquilegia_coerulea_ott192307</text></g><g class="toytree-TipLabel" transform="translate(201.291,213.985)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Delphinium_exaltatum_ott693550</text></g><g class="toytree-TipLabel" transform="translate(201.291,191.915)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Erythranthe_guttata_ott504496</text></g><g class="toytree-TipLabel" transform="translate(201.291,169.846)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Orobanche_cernua_var._cumana_ott1010133</text></g><g class="toytree-TipLabel" transform="translate(201.291,147.777)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Castilleja_caudata_ott338833</text></g><g class="toytree-TipLabel" transform="translate(201.291,125.708)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Castilleja_campestris_ott83184</text></g><g class="toytree-TipLabel" transform="translate(201.291,103.638)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_latituba_ott869589</text></g><g class="toytree-TipLabel" transform="translate(201.291,81.5692)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_anas_ott1032908</text></g><g class="toytree-TipLabel" transform="translate(201.291,59.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_groenlandica_ott261492</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="tf9f3a4953d0e4fd2a16fb22380c0b4be"><clipPath id="t6d59b86654d64712ab5a9fe702ce3422"><rect x="35.0" y="35.0" width="660.444" height="335.8999999999999"></rect></clipPath><g clip-path="url(#t6d59b86654d64712ab5a9fe702ce3422)"></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
nwk3 = toytree.otol.fetch_newick_induced_tree_otol(
    resolved, constrain_by_taxonomy=True
)

```


```python
t = toytree.tree(nwk3)
t.mod.remove_unary_nodes().draw('s', node_hover=True);

```


<div class="toyplot" id="t3a352d16f91947bbbeeb3f009e6768e8" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="730.444px" height="405.8999999999999px" viewBox="0 0 730.444 405.8999999999999" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tddfd32b355414e03b97e7943bef438d7"><g class="toyplot-coordinates-Cartesian" id="tb2ce15efc0af467fb0b57e588c91a531"><clipPath id="t23c37c861c6a48e6bbe7ebbe5004f477"><rect x="35.0" y="35.0" width="660.444" height="335.8999999999999"></rect></clipPath><g clip-path="url(#t23c37c861c6a48e6bbe7ebbe5004f477)"><g class="toytree-mark-Toytree" id="tb51630ee117b4398b4b96cf3c555993b"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 140.2 327.1 L 140.2 346.4 L 201.3 346.4" id="16,0" style=""></path><path d="M 160.6 307.8 L 160.6 324.3 L 201.3 324.3" id="15,1" style=""></path><path d="M 180.9 291.2 L 180.9 302.3 L 201.3 302.3" id="14,2" style=""></path><path d="M 180.9 291.2 L 180.9 280.2 L 201.3 280.2" id="14,3" style=""></path><path d="M 119.8 292.6 L 119.8 258.1 L 201.3 258.1" id="17,4" style=""></path><path d="M 180.9 214.0 L 180.9 236.1 L 201.3 236.1" id="18,5" style=""></path><path d="M 180.9 214.0 L 180.9 214.0 L 201.3 214.0" id="18,6" style=""></path><path d="M 180.9 214.0 L 180.9 191.9 L 201.3 191.9" id="18,7" style=""></path><path d="M 180.9 158.8 L 180.9 169.8 L 201.3 169.8" id="19,8" style=""></path><path d="M 180.9 158.8 L 180.9 147.8 L 201.3 147.8" id="19,9" style=""></path><path d="M 140.2 156.1 L 140.2 125.7 L 201.3 125.7" id="21,10" style=""></path><path d="M 119.8 129.8 L 119.8 103.6 L 201.3 103.6" id="22,11" style=""></path><path d="M 180.9 70.5 L 180.9 81.6 L 201.3 81.6" id="24,12" style=""></path><path d="M 180.9 70.5 L 180.9 59.5 L 201.3 59.5" id="24,13" style=""></path><path d="M 160.6 307.8 L 160.6 291.2 L 180.9 291.2" id="15,14" style=""></path><path d="M 140.2 327.1 L 140.2 307.8 L 160.6 307.8" id="16,15" style=""></path><path d="M 119.8 292.6 L 119.8 327.1 L 140.2 327.1" id="17,16" style=""></path><path d="M 99.5 211.2 L 99.5 292.6 L 119.8 292.6" id="23,17" style=""></path><path d="M 160.6 186.4 L 160.6 214.0 L 180.9 214.0" id="20,18" style=""></path><path d="M 160.6 186.4 L 160.6 158.8 L 180.9 158.8" id="20,19" style=""></path><path d="M 140.2 156.1 L 140.2 186.4 L 160.6 186.4" id="21,20" style=""></path><path d="M 119.8 129.8 L 119.8 156.1 L 140.2 156.1" id="22,21" style=""></path><path d="M 99.5 211.2 L 99.5 129.8 L 119.8 129.8" id="23,22" style=""></path><path d="M 79.1 140.9 L 79.1 211.2 L 99.5 211.2" id="25,23" style=""></path><path d="M 79.1 140.9 L 79.1 70.5 L 180.9 70.5" id="25,24" style=""></path><path d="M 58.7 140.9 L 58.7 140.9 L 79.1 140.9" id="26,25" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(201.291,346.4)"><circle r="8.0"></circle></g><g id="Node-1" transform="translate(201.291,324.331)"><circle r="8.0"></circle></g><g id="Node-2" transform="translate(201.291,302.262)"><circle r="8.0"></circle></g><g id="Node-3" transform="translate(201.291,280.192)"><circle r="8.0"></circle></g><g id="Node-4" transform="translate(201.291,258.123)"><circle r="8.0"></circle></g><g id="Node-5" transform="translate(201.291,236.054)"><circle r="8.0"></circle></g><g id="Node-6" transform="translate(201.291,213.985)"><circle r="8.0"></circle></g><g id="Node-7" transform="translate(201.291,191.915)"><circle r="8.0"></circle></g><g id="Node-8" transform="translate(201.291,169.846)"><circle r="8.0"></circle></g><g id="Node-9" transform="translate(201.291,147.777)"><circle r="8.0"></circle></g><g id="Node-10" transform="translate(201.291,125.708)"><circle r="8.0"></circle></g><g id="Node-11" transform="translate(201.291,103.638)"><circle r="8.0"></circle></g><g id="Node-12" transform="translate(201.291,81.5692)"><circle r="8.0"></circle></g><g id="Node-13" transform="translate(201.291,59.5)"><circle r="8.0"></circle></g><g id="Node-14" transform="translate(180.926,291.227)"><circle r="8.0"></circle></g><g id="Node-15" transform="translate(160.561,307.779)"><circle r="8.0"></circle></g><g id="Node-16" transform="translate(140.197,327.089)"><circle r="8.0"></circle></g><g id="Node-17" transform="translate(119.832,292.606)"><circle r="8.0"></circle></g><g id="Node-18" transform="translate(180.926,213.985)"><circle r="8.0"></circle></g><g id="Node-19" transform="translate(180.926,158.812)"><circle r="8.0"></circle></g><g id="Node-20" transform="translate(160.561,186.398)"><circle r="8.0"></circle></g><g id="Node-21" transform="translate(140.197,156.053)"><circle r="8.0"></circle></g><g id="Node-22" transform="translate(119.832,129.846)"><circle r="8.0"></circle></g><g id="Node-23" transform="translate(99.4672,211.226)"><circle r="8.0"></circle></g><g id="Node-24" transform="translate(180.926,70.5346)"><circle r="8.0"></circle></g><g id="Node-25" transform="translate(79.1026,140.88)"><circle r="8.0"></circle></g><g id="Node-26" transform="translate(58.7379,140.88)"><circle r="8.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(201.291,346.4)"><title>idx: 0
dist: 1
support: nan
height: 2
name: Boswellia_sacra_ott815270</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(201.291,324.331)"><title>idx: 1
dist: 1
support: nan
height: 1
name: Quercus_alba_ott791112</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(201.291,302.262)"><title>idx: 2
dist: 1
support: nan
height: 0
name: Quercus_minima_ott117134</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(201.291,280.192)"><title>idx: 3
dist: 1
support: nan
height: 0
name: Quercus_virginiana_ott272703</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(201.291,258.123)"><title>idx: 4
dist: 1
support: nan
height: 3
name: Amaranthus_greggii_ott151502</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(201.291,236.054)"><title>idx: 5
dist: 1
support: nan
height: 0
name: Pedicularis_latituba_ott869589</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(201.291,213.985)"><title>idx: 6
dist: 1
support: nan
height: 0
name: Pedicularis_anas_ott1032908</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(201.291,191.915)"><title>idx: 7
dist: 1
support: nan
height: 0
name: Pedicularis_groenlandica_ott261492</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(201.291,169.846)"><title>idx: 8
dist: 1
support: nan
height: 0
name: Castilleja_campestris_ott83184</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(201.291,147.777)"><title>idx: 9
dist: 1
support: nan
height: 0
name: Castilleja_caudata_ott338833</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(201.291,125.708)"><title>idx: 10
dist: 1
support: nan
height: 2
name: Orobanche_cernua_var._cumana_ott1010133</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(201.291,103.638)"><title>idx: 11
dist: 1
support: nan
height: 3
name: Erythranthe_guttata_ott504496</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(201.291,81.5692)"><title>idx: 12
dist: 1
support: nan
height: 4
name: Delphinium_exaltatum_ott693550</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(201.291,59.5)"><title>idx: 13
dist: 1
support: nan
height: 4
name: Aquilegia_coerulea_ott192307</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(180.926,291.227)"><title>idx: 14
dist: 1
support: nan
height: 1
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g><g class="toytree-NodeLabel" transform="translate(160.561,307.779)"><title>idx: 15
dist: 1
support: nan
height: 2
name: Quercus_ott791121</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">15</text></g><g class="toytree-NodeLabel" transform="translate(140.197,327.089)"><title>idx: 16
dist: 1
support: nan
height: 3
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">16</text></g><g class="toytree-NodeLabel" transform="translate(119.832,292.606)"><title>idx: 17
dist: 1
support: nan
height: 4
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">17</text></g><g class="toytree-NodeLabel" transform="translate(180.926,213.985)"><title>idx: 18
dist: 1
support: nan
height: 1
name: Pedicularis_ott989660</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">18</text></g><g class="toytree-NodeLabel" transform="translate(180.926,158.812)"><title>idx: 19
dist: 1
support: nan
height: 1
name: Castilleja_ott317400</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">19</text></g><g class="toytree-NodeLabel" transform="translate(160.561,186.398)"><title>idx: 20
dist: 1
support: nan
height: 2
name: Pedicularideae_ott5144557</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">20</text></g><g class="toytree-NodeLabel" transform="translate(140.197,156.053)"><title>idx: 21
dist: 1
support: nan
height: 3
name: Orobanchaceae_ott23373</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">21</text></g><g class="toytree-NodeLabel" transform="translate(119.832,129.846)"><title>idx: 22
dist: 1
support: nan
height: 4
name: Lamiales_ott23736</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">22</text></g><g class="toytree-NodeLabel" transform="translate(99.4672,211.226)"><title>idx: 23
dist: 1
support: nan
height: 5
name: </title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">23</text></g><g class="toytree-NodeLabel" transform="translate(180.926,70.5346)"><title>idx: 24
dist: 1
support: nan
height: 5
name: Ranunculaceae_ott387826</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">24</text></g><g class="toytree-NodeLabel" transform="translate(79.1026,140.88)"><title>idx: 25
dist: 1
support: nan
height: 6
name: Magnoliopsida_ott99252</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">25</text></g><g class="toytree-NodeLabel" transform="translate(58.7379,140.88)"><title>idx: 26
dist: 0
support: nan
height: 7
name: taxonomy_root</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">26</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(201.291,346.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Boswellia_sacra_ott815270</text></g><g class="toytree-TipLabel" transform="translate(201.291,324.331)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_alba_ott791112</text></g><g class="toytree-TipLabel" transform="translate(201.291,302.262)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_minima_ott117134</text></g><g class="toytree-TipLabel" transform="translate(201.291,280.192)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_virginiana_ott272703</text></g><g class="toytree-TipLabel" transform="translate(201.291,258.123)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Amaranthus_greggii_ott151502</text></g><g class="toytree-TipLabel" transform="translate(201.291,236.054)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_latituba_ott869589</text></g><g class="toytree-TipLabel" transform="translate(201.291,213.985)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_anas_ott1032908</text></g><g class="toytree-TipLabel" transform="translate(201.291,191.915)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_groenlandica_ott261492</text></g><g class="toytree-TipLabel" transform="translate(201.291,169.846)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Castilleja_campestris_ott83184</text></g><g class="toytree-TipLabel" transform="translate(201.291,147.777)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Castilleja_caudata_ott338833</text></g><g class="toytree-TipLabel" transform="translate(201.291,125.708)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Orobanche_cernua_var._cumana_ott1010133</text></g><g class="toytree-TipLabel" transform="translate(201.291,103.638)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Erythranthe_guttata_ott504496</text></g><g class="toytree-TipLabel" transform="translate(201.291,81.5692)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Delphinium_exaltatum_ott693550</text></g><g class="toytree-TipLabel" transform="translate(201.291,59.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Aquilegia_coerulea_ott192307</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="tbc80465abf47432b9a15de2d4295a2ee"><clipPath id="tf5abfca3c3dd4585b6c091a724a69379"><rect x="35.0" y="35.0" width="660.444" height="335.8999999999999"></rect></clipPath><g clip-path="url(#tf5abfca3c3dd4585b6c091a724a69379)"></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
t2 = toytree.ToyTree(t.treenode.children[0]._detach())

```


```python
t2.draw('s');

```


<div class="toyplot" id="ta294853422b14b518b8248bfcbccaddc" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="730.444px" height="362.2px" viewBox="0 0 730.444 362.2" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t6594ef92486b4a698d5a34b437a8053e"><g class="toyplot-coordinates-Cartesian" id="tec5bea65583345f3982a6f59be55e24a"><clipPath id="tf62da44a137b4ba6a059b81ebeee164a"><rect x="35.0" y="35.0" width="660.444" height="292.2"></rect></clipPath><g clip-path="url(#tf62da44a137b4ba6a059b81ebeee164a)"><g class="toytree-mark-Toytree" id="t89d751a2309e4ba2ad80c4f8c24ba50f"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 177.5 291.6 L 177.5 302.7 L 201.3 302.7" id="12,0" style=""></path><path d="M 177.5 291.6 L 177.5 280.6 L 201.3 280.6" id="12,1" style=""></path><path d="M 153.8 275.1 L 153.8 258.5 L 201.3 258.5" id="13,2" style=""></path><path d="M 177.5 214.3 L 177.5 236.4 L 201.3 236.4" id="14,3" style=""></path><path d="M 177.5 214.3 L 177.5 214.3 L 201.3 214.3" id="14,4" style=""></path><path d="M 177.5 214.3 L 177.5 192.2 L 201.3 192.2" id="14,5" style=""></path><path d="M 177.5 159.0 L 177.5 170.0 L 201.3 170.0" id="15,6" style=""></path><path d="M 177.5 159.0 L 177.5 147.9 L 201.3 147.9" id="15,7" style=""></path><path d="M 130.0 156.2 L 130.0 125.8 L 201.3 125.8" id="17,8" style=""></path><path d="M 106.3 130.0 L 106.3 103.7 L 201.3 103.7" id="18,9" style=""></path><path d="M 177.5 70.6 L 177.5 81.6 L 201.3 81.6" id="20,10" style=""></path><path d="M 177.5 70.6 L 177.5 59.5 L 201.3 59.5" id="20,11" style=""></path><path d="M 153.8 275.1 L 153.8 291.6 L 177.5 291.6" id="13,12" style=""></path><path d="M 82.5 202.5 L 82.5 275.1 L 153.8 275.1" id="19,13" style=""></path><path d="M 153.8 186.6 L 153.8 214.3 L 177.5 214.3" id="16,14" style=""></path><path d="M 153.8 186.6 L 153.8 159.0 L 177.5 159.0" id="16,15" style=""></path><path d="M 130.0 156.2 L 130.0 186.6 L 153.8 186.6" id="17,16" style=""></path><path d="M 106.3 130.0 L 106.3 156.2 L 130.0 156.2" id="18,17" style=""></path><path d="M 82.5 202.5 L 82.5 130.0 L 106.3 130.0" id="19,18" style=""></path><path d="M 58.7 136.5 L 58.7 202.5 L 82.5 202.5" id="21,19" style=""></path><path d="M 58.7 136.5 L 58.7 70.6 L 177.5 70.6" id="21,20" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(201.291,302.7)"><circle r="8.0"></circle></g><g id="Node-1" transform="translate(201.291,280.591)"><circle r="8.0"></circle></g><g id="Node-2" transform="translate(201.291,258.482)"><circle r="8.0"></circle></g><g id="Node-3" transform="translate(201.291,236.373)"><circle r="8.0"></circle></g><g id="Node-4" transform="translate(201.291,214.264)"><circle r="8.0"></circle></g><g id="Node-5" transform="translate(201.291,192.155)"><circle r="8.0"></circle></g><g id="Node-6" transform="translate(201.291,170.045)"><circle r="8.0"></circle></g><g id="Node-7" transform="translate(201.291,147.936)"><circle r="8.0"></circle></g><g id="Node-8" transform="translate(201.291,125.827)"><circle r="8.0"></circle></g><g id="Node-9" transform="translate(201.291,103.718)"><circle r="8.0"></circle></g><g id="Node-10" transform="translate(201.291,81.6091)"><circle r="8.0"></circle></g><g id="Node-11" transform="translate(201.291,59.5)"><circle r="8.0"></circle></g><g id="Node-12" transform="translate(177.532,291.645)"><circle r="8.0"></circle></g><g id="Node-13" transform="translate(153.773,275.064)"><circle r="8.0"></circle></g><g id="Node-14" transform="translate(177.532,214.264)"><circle r="8.0"></circle></g><g id="Node-15" transform="translate(177.532,158.991)"><circle r="8.0"></circle></g><g id="Node-16" transform="translate(153.773,186.627)"><circle r="8.0"></circle></g><g id="Node-17" transform="translate(130.014,156.227)"><circle r="8.0"></circle></g><g id="Node-18" transform="translate(106.255,129.973)"><circle r="8.0"></circle></g><g id="Node-19" transform="translate(82.4967,202.518)"><circle r="8.0"></circle></g><g id="Node-20" transform="translate(177.532,70.5545)"><circle r="8.0"></circle></g><g id="Node-21" transform="translate(58.7379,136.536)"><circle r="8.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(201.291,302.7)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(201.291,280.591)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(201.291,258.482)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(201.291,236.373)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(201.291,214.264)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(201.291,192.155)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(201.291,170.045)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(201.291,147.936)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(201.291,125.827)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(201.291,103.718)"><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(201.291,81.6091)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(201.291,59.5)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(177.532,291.645)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(153.773,275.064)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(177.532,214.264)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g><g class="toytree-NodeLabel" transform="translate(177.532,158.991)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">15</text></g><g class="toytree-NodeLabel" transform="translate(153.773,186.627)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">16</text></g><g class="toytree-NodeLabel" transform="translate(130.014,156.227)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">17</text></g><g class="toytree-NodeLabel" transform="translate(106.255,129.973)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">18</text></g><g class="toytree-NodeLabel" transform="translate(82.4967,202.518)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">19</text></g><g class="toytree-NodeLabel" transform="translate(177.532,70.5545)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">20</text></g><g class="toytree-NodeLabel" transform="translate(58.7379,136.536)"><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">21</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(201.291,302.7)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Boswellia_sacra_ott815270</text></g><g class="toytree-TipLabel" transform="translate(201.291,280.591)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_minima_ott117134</text></g><g class="toytree-TipLabel" transform="translate(201.291,258.482)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Amaranthus_greggii_ott151502</text></g><g class="toytree-TipLabel" transform="translate(201.291,236.373)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_latituba_ott869589</text></g><g class="toytree-TipLabel" transform="translate(201.291,214.264)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_anas_ott1032908</text></g><g class="toytree-TipLabel" transform="translate(201.291,192.155)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_groenlandica_ott261492</text></g><g class="toytree-TipLabel" transform="translate(201.291,170.045)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Castilleja_campestris_ott83184</text></g><g class="toytree-TipLabel" transform="translate(201.291,147.936)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Castilleja_caudata_ott338833</text></g><g class="toytree-TipLabel" transform="translate(201.291,125.827)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Orobanche_cernua_var._cumana_ott1010133</text></g><g class="toytree-TipLabel" transform="translate(201.291,103.718)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Erythranthe_guttata_ott504496</text></g><g class="toytree-TipLabel" transform="translate(201.291,81.6091)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Delphinium_exaltatum_ott693550</text></g><g class="toytree-TipLabel" transform="translate(201.291,59.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Aquilegia_coerulea_ott192307</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="tca03783231db478782f0f3e350c4dc8b"><clipPath id="tb53cf3b595ee4cd3ac046ee97e076290"><rect x="35.0" y="35.0" width="660.444" height="292.2"></rect></clipPath><g clip-path="url(#tb53cf3b595ee4cd3ac046ee97e076290)"></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


### Fetching a tree from a published study


```python
res = toytree.otol.fetch_json_induced_subtree(SUBTREE_GEN_LIST)
b = res['broken']
n = res['newick']
t = toytree.tree(n)

```


```python
res

```




    {'broken': {'ott1028998': 'mrcaott288140ott863220',
      'ott317400': 'ott5263556',
      'ott733734': 'mrcaott96ott39620',
      'ott791121': 'mrcaott37377ott106844',
      'ott918756': 'ott5263556',
      'ott989660': 'mrcaott1452ott33561'},
     'newick': "(((((((((((((((((((((((((mrcaott96ott39620)Burseraceae_ott350867)mrcaott96ott21231)mrcaott96ott982264)mrcaott96ott655994)mrcaott96ott1860)mrcaott96ott9337)mrcaott96ott24291)mrcaott96ott84975)mrcaott96ott378)mrcaott2ott96)mrcaott2ott29446)mrcaott2ott345)mrcaott2ott50744,(((((mrcaott37377ott106844,mrcaott288140ott863220)mrcaott37377ott288140)mrcaott32687ott37377)Fagales_ott267709)mrcaott579ott32687)mrcaott371ott579)mrcaott2ott371)mrcaott2ott1276)mrcaott2ott607)mrcaott2ott2464)mrcaott2ott8384)mrcaott2ott20991)mrcaott2ott557,(((((((((((((((((((((((((((Erythranthe_ott5334418)mrcaott75211ott422994)mrcaott39175ott75211,((Mimulus_ott596470)mrcaott423002ott548451)mrcaott423002ott1024159)mrcaott39175ott423002)mrcaott39175ott108490)mrcaott1452ott39175)mrcaott1452ott432231)mrcaott1452ott33561)mrcaott1016ott1452)mrcaott1016ott5046)mrcaott1016ott10430)mrcaott1016ott295840)mrcaott1016ott55260)mrcaott1016ott22352)mrcaott1016ott108502)mrcaott248ott1016)'Core_Lamiales ott5263556')mrcaott248ott55259)mrcaott248ott11341)Lamiales_ott23736)mrcaott248ott1191)mrcaott248ott101831)mrcaott248ott68444)mrcaott248ott5942)mrcaott248ott320)mrcaott248ott650)mrcaott248ott308117)mrcaott248ott67236)mrcaott2ott248)mrcaott2ott10053)mrcaott2ott8379)mrcaott2ott969,(((((((((((((Aquilegia_ott964055)mrcaott38573ott7049099)mrcaott38573ott949642)mrcaott34125ott38573)Thalictroideae_ott5479017)mrcaott2441ott22673)mrcaott2441ott203150)mrcaott2441ott1072050)Ranunculaceae_ott387826)mrcaott2441ott21786)mrcaott2441ott3773)mrcaott2441ott92057)mrcaott2441ott3851)Ranunculales_ott872975)mrcaott2ott2441;",
     'supporting_studies': ['ot_311@tree1',
      'ot_1624@Tr85668',
      'ot_2291@tree7',
      'ot_2304@tree2',
      'ot_1489@tree1',
      'ot_502@tree1',
      'ot_535@tree1',
      'pg_2712@tree6296',
      'pg_2820@tree6566',
      'pg_2539@tree6294',
      'ot_2304@tree4',
      'pg_1944@tree3959',
      'ot_1176@tree1',
      'ot_1417@Tr94055',
      'ot_2116@tree1',
      'ot_859@tree1',
      'ot_1489@tree2',
      'pg_2644@tree6164',
      'ot_1960@tree2',
      'pg_713@tree1287',
      'pg_225@tree5991',
      'ot_1489@tree4']}




```python


```


```python
# store the rooting info in taxatree
toytree.tree(nwk).draw('s', tip_labels_align=True, node_hover=True);

```


<div class="toyplot" id="tf85b54a7ecbb4633a99fcbe65ef666f0" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="690.4119999999999px" height="340.35px" viewBox="0 0 690.4119999999999 340.35" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t386a568901f9416e81d95eb3123871ae"><g class="toyplot-coordinates-Cartesian" id="t3058059d15a440cd8fd23b37a9d682d3"><clipPath id="t56ee251c557c49ca99203e189c5297f2"><rect x="35.0" y="35.0" width="620.4119999999999" height="270.35"></rect></clipPath><g clip-path="url(#t56ee251c557c49ca99203e189c5297f2)"><g class="toytree-mark-Toytree" id="t046b632dd5b0415c9194ab0b77e434ae"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 168.8 269.8 L 168.8 280.9 L 196.3 280.9" id="11,0" style=""></path><path d="M 168.8 269.8 L 168.8 258.7 L 196.3 258.7" id="11,1" style=""></path><path d="M 86.3 211.7 L 86.3 236.6 L 196.3 236.6" id="16,2" style=""></path><path d="M 113.8 186.8 L 113.8 214.4 L 196.3 214.4" id="15,3" style=""></path><path d="M 168.8 181.2 L 168.8 192.3 L 196.3 192.3" id="12,4" style=""></path><path d="M 168.8 181.2 L 168.8 170.2 L 196.3 170.2" id="12,5" style=""></path><path d="M 168.8 137.0 L 168.8 148.0 L 196.3 148.0" id="13,6" style=""></path><path d="M 168.8 137.0 L 168.8 125.9 L 196.3 125.9" id="13,7" style=""></path><path d="M 141.3 87.2 L 141.3 103.8 L 196.3 103.8" id="18,8" style=""></path><path d="M 168.8 70.6 L 168.8 81.6 L 196.3 81.6" id="17,9" style=""></path><path d="M 168.8 70.6 L 168.8 59.5 L 196.3 59.5" id="17,10" style=""></path><path d="M 58.8 189.5 L 58.8 269.8 L 168.8 269.8" id="19,11" style=""></path><path d="M 141.3 159.1 L 141.3 181.2 L 168.8 181.2" id="14,12" style=""></path><path d="M 141.3 159.1 L 141.3 137.0 L 168.8 137.0" id="14,13" style=""></path><path d="M 113.8 186.8 L 113.8 159.1 L 141.3 159.1" id="15,14" style=""></path><path d="M 86.3 211.7 L 86.3 186.8 L 113.8 186.8" id="16,15" style=""></path><path d="M 58.8 189.5 L 58.8 211.7 L 86.3 211.7" id="19,16" style=""></path><path d="M 141.3 87.2 L 141.3 70.6 L 168.8 70.6" id="18,17" style=""></path><path d="M 58.8 189.5 L 58.8 87.2 L 141.3 87.2" id="19,18" style=""></path></g><g class="toytree-AlignEdges" style="stroke:rgb(66.0%,66.0%,66.0%);stroke-opacity:0.75;stroke-dasharray:2,4;stroke-linecap:round;stroke-width:2"><path d="M 196.3 280.9 L 196.3 280.9"></path><path d="M 196.3 258.7 L 196.3 258.7"></path><path d="M 196.3 236.6 L 196.3 236.6"></path><path d="M 196.3 214.4 L 196.3 214.4"></path><path d="M 196.3 192.3 L 196.3 192.3"></path><path d="M 196.3 170.2 L 196.3 170.2"></path><path d="M 196.3 148.0 L 196.3 148.0"></path><path d="M 196.3 125.9 L 196.3 125.9"></path><path d="M 196.3 103.8 L 196.3 103.8"></path><path d="M 196.3 81.6 L 196.3 81.6"></path><path d="M 196.3 59.5 L 196.3 59.5"></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(82.7%,82.7%,82.7%);fill-opacity:1.0;stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-width:1.5"><g id="Node-0" transform="translate(196.287,280.85)"><circle r="8.0"></circle></g><g id="Node-1" transform="translate(196.287,258.715)"><circle r="8.0"></circle></g><g id="Node-2" transform="translate(196.287,236.58)"><circle r="8.0"></circle></g><g id="Node-3" transform="translate(196.287,214.445)"><circle r="8.0"></circle></g><g id="Node-4" transform="translate(196.287,192.31)"><circle r="8.0"></circle></g><g id="Node-5" transform="translate(196.287,170.175)"><circle r="8.0"></circle></g><g id="Node-6" transform="translate(196.287,148.04)"><circle r="8.0"></circle></g><g id="Node-7" transform="translate(196.287,125.905)"><circle r="8.0"></circle></g><g id="Node-8" transform="translate(196.287,103.77)"><circle r="8.0"></circle></g><g id="Node-9" transform="translate(196.287,81.635)"><circle r="8.0"></circle></g><g id="Node-10" transform="translate(196.287,59.5)"><circle r="8.0"></circle></g><g id="Node-11" transform="translate(168.784,269.783)"><circle r="8.0"></circle></g><g id="Node-12" transform="translate(168.784,181.243)"><circle r="8.0"></circle></g><g id="Node-13" transform="translate(168.784,136.972)"><circle r="8.0"></circle></g><g id="Node-14" transform="translate(141.281,159.107)"><circle r="8.0"></circle></g><g id="Node-15" transform="translate(113.779,186.776)"><circle r="8.0"></circle></g><g id="Node-16" transform="translate(86.276,211.678)"><circle r="8.0"></circle></g><g id="Node-17" transform="translate(168.784,70.5675)"><circle r="8.0"></circle></g><g id="Node-18" transform="translate(141.281,87.1687)"><circle r="8.0"></circle></g><g id="Node-19" transform="translate(58.7733,189.543)"><circle r="8.0"></circle></g></g><g class="toytree-NodeLabels" style="font-family:Helvetica;font-size:9px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-NodeLabel" transform="translate(196.287,280.85)"><title>idx: 0
dist: 1
support: nan
height: 3
name: Amaranthusgreggii_ott151502</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">0</text></g><g class="toytree-NodeLabel" transform="translate(196.287,258.715)"><title>idx: 1
dist: 1
support: nan
height: 3
name: Quercusminima_ott117134</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">1</text></g><g class="toytree-NodeLabel" transform="translate(196.287,236.58)"><title>idx: 2
dist: 1
support: nan
height: 3
name: Erythrantheguttata_ott504496</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">2</text></g><g class="toytree-NodeLabel" transform="translate(196.287,214.445)"><title>idx: 3
dist: 1
support: nan
height: 2
name: Orobanchecernuavar.cumana_ott1010133</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">3</text></g><g class="toytree-NodeLabel" transform="translate(196.287,192.31)"><title>idx: 4
dist: 1
support: nan
height: 0
name: Castillejacaudata_ott338833</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">4</text></g><g class="toytree-NodeLabel" transform="translate(196.287,170.175)"><title>idx: 5
dist: 1
support: nan
height: 0
name: Castillejacampestris_ott83184</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">5</text></g><g class="toytree-NodeLabel" transform="translate(196.287,148.04)"><title>idx: 6
dist: 1
support: nan
height: 0
name: Pedicularisanas_ott1032908</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">6</text></g><g class="toytree-NodeLabel" transform="translate(196.287,125.905)"><title>idx: 7
dist: 1
support: nan
height: 0
name: Pedicularisgroenlandica_ott261492</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">7</text></g><g class="toytree-NodeLabel" transform="translate(196.287,103.77)"><title>idx: 8
dist: 1
support: nan
height: 3
name: Boswelliasacra_ott815270</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">8</text></g><g class="toytree-NodeLabel" transform="translate(196.287,81.635)"><title>idx: 9
dist: 1
support: nan
height: 2
name: Aquilegiacoerulea_ott192307</title><text x="-2.5020000000000002" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">9</text></g><g class="toytree-NodeLabel" transform="translate(196.287,59.5)"><title>idx: 10
dist: 1
support: nan
height: 2
name: Delphiniumexaltatum_ott693550</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">10</text></g><g class="toytree-NodeLabel" transform="translate(168.784,269.783)"><title>idx: 11
dist: 1
support: nan
height: 4
name: Magnoliopsida_ott99252</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">11</text></g><g class="toytree-NodeLabel" transform="translate(168.784,181.243)"><title>idx: 12
dist: 1
support: nan
height: 1
name: Castilleja_ott317400</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">12</text></g><g class="toytree-NodeLabel" transform="translate(168.784,136.972)"><title>idx: 13
dist: 1
support: nan
height: 1
name: Pedicularis_ott989660</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">13</text></g><g class="toytree-NodeLabel" transform="translate(141.281,159.107)"><title>idx: 14
dist: 1
support: nan
height: 2
name: Pedicularideae_ott5144557</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">14</text></g><g class="toytree-NodeLabel" transform="translate(113.779,186.776)"><title>idx: 15
dist: 1
support: nan
height: 3
name: Orobanchaceae_ott23373</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">15</text></g><g class="toytree-NodeLabel" transform="translate(86.276,211.678)"><title>idx: 16
dist: 1
support: nan
height: 4
name: Lamiales_ott23736</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">16</text></g><g class="toytree-NodeLabel" transform="translate(168.784,70.5675)"><title>idx: 17
dist: 1
support: nan
height: 3
name: Ranunculaceae_ott387826</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">17</text></g><g class="toytree-NodeLabel" transform="translate(141.281,87.1687)"><title>idx: 18
dist: 1
support: nan
height: 4
name: Magnoliopsida_ott99252</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">18</text></g><g class="toytree-NodeLabel" transform="translate(58.7733,189.543)"><title>idx: 19
dist: 0
support: nan
height: 5
name: Magnoliopsida_ott99252</title><text x="-5.0040000000000004" y="2.2995" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:9.0px;font-weight:300;vertical-align:baseline;white-space:pre">19</text></g></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(196.287,280.85)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Amaranthusgreggii_ott151502</text></g><g class="toytree-TipLabel" transform="translate(196.287,258.715)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercusminima_ott117134</text></g><g class="toytree-TipLabel" transform="translate(196.287,236.58)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Erythrantheguttata_ott504496</text></g><g class="toytree-TipLabel" transform="translate(196.287,214.445)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Orobanchecernuavar.cumana_ott1010133</text></g><g class="toytree-TipLabel" transform="translate(196.287,192.31)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Castillejacaudata_ott338833</text></g><g class="toytree-TipLabel" transform="translate(196.287,170.175)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Castillejacampestris_ott83184</text></g><g class="toytree-TipLabel" transform="translate(196.287,148.04)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularisanas_ott1032908</text></g><g class="toytree-TipLabel" transform="translate(196.287,125.905)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularisgroenlandica_ott261492</text></g><g class="toytree-TipLabel" transform="translate(196.287,103.77)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Boswelliasacra_ott815270</text></g><g class="toytree-TipLabel" transform="translate(196.287,81.635)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Aquilegiacoerulea_ott192307</text></g><g class="toytree-TipLabel" transform="translate(196.287,59.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Delphiniumexaltatum_ott693550</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="td9b8d5dae04d4381802ac0ee276fac01"><clipPath id="t60548d05a20a474f8eb8c00dfe2229a6"><rect x="35.0" y="35.0" width="620.4119999999999" height="270.35"></rect></clipPath><g clip-path="url(#t60548d05a20a474f8eb8c00dfe2229a6)"></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
toytree.otol.fetch_json_mrca(["Quercus", "Boswellia"])

```




    {'mrca': {'conflicts_with': {'ot_1360@Tr93591': ['Tn13791757',
        'Tn13791760',
        'Tn13791786',
        'Tn13791793',
        'Tn13791825',
        'Tn13791850'],
       'ot_1417@Tr94055': ['Tn13857155', 'Tn13857203', 'Tn13857325', 'Tn13857439'],
       'ot_1489@tree1': ['node112', 'node113', 'node122', 'node85'],
       'ot_1489@tree2': ['node282',
        'node298',
        'node299',
        'node301',
        'node305',
        'node307'],
       'ot_1489@tree4': ['node407', 'node408'],
       'ot_1624@Tr85668': ['Tn12610217'],
       'ot_2089@Tr65393': ['Tn10412906',
        'Tn10412909',
        'Tn10412938',
        'Tn10412976',
        'Tn10412996',
        'Tn10413034',
        'Tn10413106',
        'Tn10413111',
        'Tn10413114',
        'Tn10413123',
        'Tn10413131',
        'Tn10413152',
        'Tn10413259',
        'Tn10413272',
        'Tn10413319',
        'Tn10413322',
        'Tn10413330',
        'Tn10413361',
        'Tn10413476',
        'Tn10413514',
        'Tn10413560',
        'Tn10413564',
        'Tn10413587',
        'Tn10413637',
        'Tn10413676',
        'Tn10413688',
        'Tn10413716'],
       'ot_2116@tree1': ['node155'],
       'ot_2291@tree7': ['node145446',
        'node148192',
        'node148193',
        'node148197',
        'node148469',
        'node148523',
        'node148524',
        'node148525',
        'node148527',
        'node148529',
        'node148530',
        'node148533',
        'node148534',
        'node148566',
        'node148567',
        'node148573',
        'node148574',
        'node148576',
        'node148578',
        'node148801',
        'node148802',
        'node158125',
        'node158267',
        'node166951',
        'node184719',
        'node184720',
        'node184738',
        'node185136',
        'node185146',
        'node185172',
        'node185188',
        'node185216',
        'node185218',
        'node185246',
        'node185256',
        'node185257',
        'node185258',
        'node185259',
        'node185261',
        'node185262',
        'node185264',
        'node185266',
        'node185280',
        'node185281',
        'node185282',
        'node185308',
        'node185469',
        'node185471',
        'node185479',
        'node185509',
        'node185531',
        'node185533',
        'node185545',
        'node185549',
        'node185561',
        'node185563',
        'node185565',
        'node185592',
        'node185608',
        'node185609',
        'node185613',
        'node185615',
        'node185617',
        'node185621',
        'node185622',
        'node185623',
        'node185625',
        'node185626',
        'node185647',
        'node185649',
        'node185651',
        'node185653',
        'node185654',
        'node185664',
        'node185665',
        'node185666',
        'node185668',
        'node185670',
        'node185672',
        'node185696',
        'node185697',
        'node185703',
        'node185705',
        'node185712',
        'node185746',
        'node185747',
        'node185748',
        'node185762',
        'node185763',
        'node185767',
        'node185769',
        'node185771',
        'node185779',
        'node185833',
        'node190093',
        'node190094',
        'node190095',
        'node190853',
        'node190854',
        'node191172',
        'node191173',
        'node191387',
        'node191388'],
       'ot_311@tree1': ['node21593',
        'node21723',
        'node21724',
        'node21738',
        'node21740',
        'node21742',
        'node21744',
        'node21745',
        'node21746',
        'node21748',
        'node21985',
        'node22025',
        'node22033',
        'node28470'],
       'ot_502@tree1': ['node108', 'node539', 'node549', 'node550'],
       'ot_535@tree1': ['node35', 'node62', 'node63', 'node72'],
       'ot_859@tree1': ['node74', 'node75'],
       'pg_2539@tree6294': ['node1095082', 'node1095106', 'node1095165'],
       'pg_2712@tree6296': ['node1095851',
        'node1095852',
        'node1095853',
        'node1095854',
        'node1095879',
        'node1095934'],
       'pg_2820@tree6566': ['node1140396',
        'node1140397',
        'node1140442',
        'node1140443',
        'node1140465']},
      'node_id': 'mrcaott2ott371',
      'num_tips': 88231,
      'partial_path_of': {'ot_1176@tree1': 'node9', 'ot_1960@tree2': 'node93'},
      'supported_by': {'ot_2304@tree2': 'node13855', 'ot_2304@tree4': 'node21026'},
      'terminal': {'ot_2037@tree13': 'node741',
       'ot_766@Tr85440': 'Tn12578681',
       'pg_1242@tree2507': 'ott339346',
       'pg_2822@tree6569': 'node1141898'}},
     'nearest_taxon': {'name': 'Mesangiospermae',
      'ott_id': 5298374,
      'rank': 'no rank',
      'tax_sources': ['ncbi:1437183'],
      'unique_name': 'Mesangiospermae'},
     'source_id_map': {'ot_1176@tree1': {'git_sha': '',
       'study_id': 'ot_1176',
       'tree_id': 'tree1'},
      'ot_1360@Tr93591': {'git_sha': '',
       'study_id': 'ot_1360',
       'tree_id': 'Tr93591'},
      'ot_1417@Tr94055': {'git_sha': '',
       'study_id': 'ot_1417',
       'tree_id': 'Tr94055'},
      'ot_1489@tree1': {'git_sha': '', 'study_id': 'ot_1489', 'tree_id': 'tree1'},
      'ot_1489@tree2': {'git_sha': '', 'study_id': 'ot_1489', 'tree_id': 'tree2'},
      'ot_1489@tree4': {'git_sha': '', 'study_id': 'ot_1489', 'tree_id': 'tree4'},
      'ot_1624@Tr85668': {'git_sha': '',
       'study_id': 'ot_1624',
       'tree_id': 'Tr85668'},
      'ot_1960@tree2': {'git_sha': '', 'study_id': 'ot_1960', 'tree_id': 'tree2'},
      'ot_2037@tree13': {'git_sha': '',
       'study_id': 'ot_2037',
       'tree_id': 'tree13'},
      'ot_2089@Tr65393': {'git_sha': '',
       'study_id': 'ot_2089',
       'tree_id': 'Tr65393'},
      'ot_2116@tree1': {'git_sha': '', 'study_id': 'ot_2116', 'tree_id': 'tree1'},
      'ot_2291@tree7': {'git_sha': '', 'study_id': 'ot_2291', 'tree_id': 'tree7'},
      'ot_2304@tree2': {'git_sha': '', 'study_id': 'ot_2304', 'tree_id': 'tree2'},
      'ot_2304@tree4': {'git_sha': '', 'study_id': 'ot_2304', 'tree_id': 'tree4'},
      'ot_311@tree1': {'git_sha': '', 'study_id': 'ot_311', 'tree_id': 'tree1'},
      'ot_502@tree1': {'git_sha': '', 'study_id': 'ot_502', 'tree_id': 'tree1'},
      'ot_535@tree1': {'git_sha': '', 'study_id': 'ot_535', 'tree_id': 'tree1'},
      'ot_766@Tr85440': {'git_sha': '',
       'study_id': 'ot_766',
       'tree_id': 'Tr85440'},
      'ot_859@tree1': {'git_sha': '', 'study_id': 'ot_859', 'tree_id': 'tree1'},
      'pg_1242@tree2507': {'git_sha': '',
       'study_id': 'pg_1242',
       'tree_id': 'tree2507'},
      'pg_2539@tree6294': {'git_sha': '',
       'study_id': 'pg_2539',
       'tree_id': 'tree6294'},
      'pg_2712@tree6296': {'git_sha': '',
       'study_id': 'pg_2712',
       'tree_id': 'tree6296'},
      'pg_2820@tree6566': {'git_sha': '',
       'study_id': 'pg_2820',
       'tree_id': 'tree6566'},
      'pg_2822@tree6569': {'git_sha': '',
       'study_id': 'pg_2822',
       'tree_id': 'tree6569'}},
     'synth_id': 'opentree16.1'}




```python
if b:

    # get lineages for all passed tips
    lineages = toytree.otol.fetch_json_taxon_info(SUBTREE_GEN_LIST, include_lineage=True)

    # iterate over broken nodes to insert
    # TODO: sort so mrca targets go first
    for key, val in b.items():
        
        if val.startswith("o"):
            continue
    
        # build name of broken node
        name = toytree.otol.fetch_json_taxon_info(key)[0].get("name", key)
        name = f"{name}_{key}"

        # find lowest shared rank with existing taxa
        
        
        # try to insert at genus if mrca with any existing
        for node in t:
    
        # try to insert at family
    
        # ...
        
        t.mod.add_child_node(f"~{val}", name=name, dist=1, inplace=True)

```


```python


```


    ---------------------------------------------------------------------------

    NameError                                 Traceback (most recent call last)

    Cell In[131], line 1
    ----> 1 lineages


    NameError: name 'lineages' is not defined



```python
name = toytree.otol.fetch_json_taxon_info("ott918756")[0].get("name")
name

```




    'Orobanche'




```python
t.draw();

```


<div class="toyplot" id="t37e55f30c76c4dcf9f5ba3a270a2849a" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="488.49600000000004px" height="275.0px" viewBox="0 0 488.49600000000004 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="te08cfd57746e48c0a98ef76151b2508a"><g class="toyplot-coordinates-Cartesian" id="td12de2aa3a854a5ca054e70a13b14c56"><clipPath id="t0d49505050354a16be8be731bb66c860"><rect x="35.0" y="35.0" width="418.49600000000004" height="205.0"></rect></clipPath><g clip-path="url(#t0d49505050354a16be8be731bb66c860)"><g class="toytree-mark-Toytree" id="t469a419cbe544e0aa85b6d6dcc5ee55b"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 140.2 217.8 L 140.2 217.8 L 143.8 217.8" id="6,0" style=""></path><path d="M 111.6 185.7 L 111.6 185.7 L 115.2 185.7" id="20,1" style=""></path><path d="M 161.6 153.6 L 161.6 153.6 L 165.2 153.6" id="33,2" style=""></path><path d="M 161.6 121.4 L 161.6 121.4 L 165.2 121.4" id="35,3" style=""></path><path d="M 140.2 113.4 L 140.2 89.3 L 143.8 89.3" id="41,4" style=""></path><path d="M 97.4 57.2 L 97.4 57.2 L 100.9 57.2" id="66,5" style=""></path><path d="M 136.6 217.8 L 136.6 217.8 L 140.2 217.8" id="7,6" style=""></path><path d="M 133.0 217.8 L 133.0 217.8 L 136.6 217.8" id="8,7" style=""></path><path d="M 129.5 217.8 L 129.5 217.8 L 133.0 217.8" id="9,8" style=""></path><path d="M 125.9 217.8 L 125.9 217.8 L 129.5 217.8" id="10,9" style=""></path><path d="M 122.3 217.8 L 122.3 217.8 L 125.9 217.8" id="11,10" style=""></path><path d="M 118.8 217.8 L 118.8 217.8 L 122.3 217.8" id="12,11" style=""></path><path d="M 115.2 217.8 L 115.2 217.8 L 118.8 217.8" id="13,12" style=""></path><path d="M 111.6 217.8 L 111.6 217.8 L 115.2 217.8" id="14,13" style=""></path><path d="M 108.1 217.8 L 108.1 217.8 L 111.6 217.8" id="15,14" style=""></path><path d="M 104.5 217.8 L 104.5 217.8 L 108.1 217.8" id="16,15" style=""></path><path d="M 100.9 217.8 L 100.9 217.8 L 104.5 217.8" id="17,16" style=""></path><path d="M 97.4 217.8 L 97.4 217.8 L 100.9 217.8" id="18,17" style=""></path><path d="M 93.8 217.8 L 93.8 217.8 L 97.4 217.8" id="19,18" style=""></path><path d="M 90.2 201.7 L 90.2 217.8 L 93.8 217.8" id="26,19" style=""></path><path d="M 108.1 185.7 L 108.1 185.7 L 111.6 185.7" id="21,20" style=""></path><path d="M 104.5 185.7 L 104.5 185.7 L 108.1 185.7" id="22,21" style=""></path><path d="M 100.9 185.7 L 100.9 185.7 L 104.5 185.7" id="23,22" style=""></path><path d="M 97.4 185.7 L 97.4 185.7 L 100.9 185.7" id="24,23" style=""></path><path d="M 93.8 185.7 L 93.8 185.7 L 97.4 185.7" id="25,24" style=""></path><path d="M 90.2 201.7 L 90.2 185.7 L 93.8 185.7" id="26,25" style=""></path><path d="M 86.6 201.7 L 86.6 201.7 L 90.2 201.7" id="27,26" style=""></path><path d="M 83.1 201.7 L 83.1 201.7 L 86.6 201.7" id="28,27" style=""></path><path d="M 79.5 201.7 L 79.5 201.7 L 83.1 201.7" id="29,28" style=""></path><path d="M 75.9 201.7 L 75.9 201.7 L 79.5 201.7" id="30,29" style=""></path><path d="M 72.4 201.7 L 72.4 201.7 L 75.9 201.7" id="31,30" style=""></path><path d="M 68.8 201.7 L 68.8 201.7 L 72.4 201.7" id="32,31" style=""></path><path d="M 65.2 157.6 L 65.2 201.7 L 68.8 201.7" id="62,32" style=""></path><path d="M 158.0 153.6 L 158.0 153.6 L 161.6 153.6" id="34,33" style=""></path><path d="M 154.5 137.5 L 154.5 153.6 L 158.0 153.6" id="37,34" style=""></path><path d="M 158.0 121.4 L 158.0 121.4 L 161.6 121.4" id="36,35" style=""></path><path d="M 154.5 137.5 L 154.5 121.4 L 158.0 121.4" id="37,36" style=""></path><path d="M 150.9 137.5 L 150.9 137.5 L 154.5 137.5" id="38,37" style=""></path><path d="M 147.3 137.5 L 147.3 137.5 L 150.9 137.5" id="39,38" style=""></path><path d="M 143.8 137.5 L 143.8 137.5 L 147.3 137.5" id="40,39" style=""></path><path d="M 140.2 113.4 L 140.2 137.5 L 143.8 137.5" id="41,40" style=""></path><path d="M 136.6 113.4 L 136.6 113.4 L 140.2 113.4" id="42,41" style=""></path><path d="M 133.0 113.4 L 133.0 113.4 L 136.6 113.4" id="43,42" style=""></path><path d="M 129.5 113.4 L 129.5 113.4 L 133.0 113.4" id="44,43" style=""></path><path d="M 125.9 113.4 L 125.9 113.4 L 129.5 113.4" id="45,44" style=""></path><path d="M 122.3 113.4 L 122.3 113.4 L 125.9 113.4" id="46,45" style=""></path><path d="M 118.8 113.4 L 118.8 113.4 L 122.3 113.4" id="47,46" style=""></path><path d="M 115.2 113.4 L 115.2 113.4 L 118.8 113.4" id="48,47" style=""></path><path d="M 111.6 113.4 L 111.6 113.4 L 115.2 113.4" id="49,48" style=""></path><path d="M 108.1 113.4 L 108.1 113.4 L 111.6 113.4" id="50,49" style=""></path><path d="M 104.5 113.4 L 104.5 113.4 L 108.1 113.4" id="51,50" style=""></path><path d="M 100.9 113.4 L 100.9 113.4 L 104.5 113.4" id="52,51" style=""></path><path d="M 97.4 113.4 L 97.4 113.4 L 100.9 113.4" id="53,52" style=""></path><path d="M 93.8 113.4 L 93.8 113.4 L 97.4 113.4" id="54,53" style=""></path><path d="M 90.2 113.4 L 90.2 113.4 L 93.8 113.4" id="55,54" style=""></path><path d="M 86.6 113.4 L 86.6 113.4 L 90.2 113.4" id="56,55" style=""></path><path d="M 83.1 113.4 L 83.1 113.4 L 86.6 113.4" id="57,56" style=""></path><path d="M 79.5 113.4 L 79.5 113.4 L 83.1 113.4" id="58,57" style=""></path><path d="M 75.9 113.4 L 75.9 113.4 L 79.5 113.4" id="59,58" style=""></path><path d="M 72.4 113.4 L 72.4 113.4 L 75.9 113.4" id="60,59" style=""></path><path d="M 68.8 113.4 L 68.8 113.4 L 72.4 113.4" id="61,60" style=""></path><path d="M 65.2 157.6 L 65.2 113.4 L 68.8 113.4" id="62,61" style=""></path><path d="M 61.7 157.6 L 61.7 157.6 L 65.2 157.6" id="63,62" style=""></path><path d="M 58.1 157.6 L 58.1 157.6 L 61.7 157.6" id="64,63" style=""></path><path d="M 54.5 157.6 L 54.5 157.6 L 58.1 157.6" id="65,64" style=""></path><path d="M 51.0 107.4 L 51.0 157.6 L 54.5 157.6" id="79,65" style=""></path><path d="M 93.8 57.2 L 93.8 57.2 L 97.4 57.2" id="67,66" style=""></path><path d="M 90.2 57.2 L 90.2 57.2 L 93.8 57.2" id="68,67" style=""></path><path d="M 86.6 57.2 L 86.6 57.2 L 90.2 57.2" id="69,68" style=""></path><path d="M 83.1 57.2 L 83.1 57.2 L 86.6 57.2" id="70,69" style=""></path><path d="M 79.5 57.2 L 79.5 57.2 L 83.1 57.2" id="71,70" style=""></path><path d="M 75.9 57.2 L 75.9 57.2 L 79.5 57.2" id="72,71" style=""></path><path d="M 72.4 57.2 L 72.4 57.2 L 75.9 57.2" id="73,72" style=""></path><path d="M 68.8 57.2 L 68.8 57.2 L 72.4 57.2" id="74,73" style=""></path><path d="M 65.2 57.2 L 65.2 57.2 L 68.8 57.2" id="75,74" style=""></path><path d="M 61.7 57.2 L 61.7 57.2 L 65.2 57.2" id="76,75" style=""></path><path d="M 58.1 57.2 L 58.1 57.2 L 61.7 57.2" id="77,76" style=""></path><path d="M 54.5 57.2 L 54.5 57.2 L 58.1 57.2" id="78,77" style=""></path><path d="M 51.0 107.4 L 51.0 57.2 L 54.5 57.2" id="79,78" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(143.758,217.8)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Boswellia_ott733734</text></g><g class="toytree-TipLabel" transform="translate(115.202,185.68)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quercus_ott791121</text></g><g class="toytree-TipLabel" transform="translate(165.175,153.56)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Erythranthe_ott5334418</text></g><g class="toytree-TipLabel" transform="translate(165.175,121.44)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Mimulus_ott596470</text></g><g class="toytree-TipLabel" transform="translate(143.758,89.32)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_ott989660</text></g><g class="toytree-TipLabel" transform="translate(100.924,57.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Aquilegia_ott964055</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="tfcecf23ff21544c58ec0778589475df1"><clipPath id="t793414bd0ae34332a49a77b667199e33"><rect x="35.0" y="35.0" width="418.49600000000004" height="205.0"></rect></clipPath><g clip-path="url(#t793414bd0ae34332a49a77b667199e33)"></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
t.get_nodes("~Orob")

```




    [<Node(idx=6, name='Orobanche')>]




```python


```




    [{'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'Pedicularideae',
      'ott_id': 5144557,
      'rank': 'tribe',
      'source': 'ott3.7draft3',
      'synonyms': [],
      'tax_sources': ['ncbi:1325730'],
      'unique_name': 'Pedicularideae'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'Orobanchaceae',
      'ott_id': 23373,
      'rank': 'family',
      'source': 'ott3.7draft3',
      'synonyms': ['Aeginetiaceae',
       'Cyclocheilaceae',
       'Cyclocheileae',
       'Melampyraceae',
       'Nesogenaceae',
       'Pedicularidaceae',
       'Phelypaeaceae',
       'Rehmanniaceae',
       'Rhinanthaceae'],
      'tax_sources': ['study713:78',
       'ncbi:91896',
       'worms:382476',
       'gbif:6651',
       'irmng:119096'],
      'unique_name': 'Orobanchaceae'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'higher_core_Lamiales',
      'ott_id': 5264061,
      'rank': 'no rank',
      'source': 'ott3.7draft3',
      'synonyms': [],
      'tax_sources': ['study713:49'],
      'unique_name': 'higher_core_Lamiales'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'Core_Lamiales',
      'ott_id': 5263556,
      'rank': 'no rank',
      'source': 'ott3.7draft3',
      'synonyms': [],
      'tax_sources': ['study713:13'],
      'unique_name': 'Core_Lamiales'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'Lamiales',
      'ott_id': 23736,
      'rank': 'order',
      'source': 'ott3.7draft3',
      'synonyms': ['Scrophulariales'],
      'tax_sources': ['study713:1',
       'ncbi:4143',
       'worms:234498',
       'gbif:408',
       'irmng:12140',
       'irmng:11489'],
      'unique_name': 'Lamiales'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'lamiids',
      'ott_id': 596112,
      'rank': 'no rank',
      'source': 'ott3.7draft3',
      'synonyms': ['Gentiananae', 'euasterids I'],
      'tax_sources': ['ncbi:91888'],
      'unique_name': 'lamiids'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'asterids',
      'ott_id': 1008294,
      'rank': 'no rank',
      'source': 'ott3.7draft3',
      'synonyms': ['Asteridae'],
      'tax_sources': ['ncbi:71274'],
      'unique_name': 'asterids'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'Pentapetalae',
      'ott_id': 5316182,
      'rank': 'no rank',
      'source': 'ott3.7draft3',
      'synonyms': [],
      'tax_sources': ['ncbi:1437201'],
      'unique_name': 'Pentapetalae'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'Gunneridae',
      'ott_id': 853757,
      'rank': 'no rank',
      'source': 'ott3.7draft3',
      'synonyms': ['core eudicots', 'core eudicotyledons'],
      'tax_sources': ['ncbi:91827'],
      'unique_name': 'Gunneridae'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'eudicotyledons',
      'ott_id': 431495,
      'rank': 'no rank',
      'source': 'ott3.7draft3',
      'synonyms': [],
      'tax_sources': ['ncbi:71240'],
      'unique_name': 'eudicotyledons'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'Mesangiospermae',
      'ott_id': 5298374,
      'rank': 'no rank',
      'source': 'ott3.7draft3',
      'synonyms': [],
      'tax_sources': ['ncbi:1437183'],
      'unique_name': 'Mesangiospermae'},
     {'flags': ['sibling_higher'],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'Magnoliopsida',
      'ott_id': 99252,
      'rank': 'class',
      'source': 'ott3.7draft3',
      'synonyms': ['Angiospermae', 'Magnoliophyta'],
      'tax_sources': ['ncbi:3398', 'worms:182757', 'gbif:220', 'irmng:1102'],
      'unique_name': 'Magnoliopsida'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'Spermatophyta',
      'ott_id': 10218,
      'rank': 'no rank',
      'source': 'ott3.7draft3',
      'synonyms': [],
      'tax_sources': ['ncbi:58024'],
      'unique_name': 'Spermatophyta'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'Euphyllophyta',
      'ott_id': 1007992,
      'rank': 'no rank',
      'source': 'ott3.7draft3',
      'synonyms': ['euphyllophytes'],
      'tax_sources': ['ncbi:78536'],
      'unique_name': 'Euphyllophyta'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'Tracheophyta',
      'ott_id': 10210,
      'rank': 'phylum',
      'source': 'ott3.7draft3',
      'synonyms': ['Arthrophyta',
       'Coniferophyta',
       'Cycadophyta',
       'Equisetophyta',
       'Ginkgophyta',
       'Gnetophyta',
       'Lycopodiophyta',
       'Magnoliophyta',
       'Microphyllophyta',
       'Polypodiophyta',
       'Psilophyta',
       'Psilotophyta',
       'Pteridophyta',
       'Pterophyta'],
      'tax_sources': ['ncbi:58023', 'worms:596326', 'gbif:7707728', 'irmng:227'],
      'unique_name': 'Tracheophyta'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'Embryophyta',
      'ott_id': 56610,
      'rank': 'no rank',
      'source': 'ott3.7draft3',
      'synonyms': [],
      'tax_sources': ['ncbi:3193'],
      'unique_name': 'Embryophyta'},
     {'flags': ['sibling_higher'],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'Streptophyta',
      'ott_id': 916750,
      'rank': 'phylum',
      'source': 'ott3.7draft3',
      'synonyms': ['Charophyta/Embryophyta group',
       'Streptophytina',
       'charophyte/embryophyte group'],
      'tax_sources': ['ncbi:35493', 'worms:536191'],
      'unique_name': 'Streptophyta'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'Chloroplastida',
      'ott_id': 361838,
      'rank': 'kingdom',
      'source': 'ott3.7draft3',
      'synonyms': ['Chlorobionta',
       'Chlorophyta/Embryophyta group',
       'Viridiplantae',
       'chlorophyte/embryophyte group'],
      'tax_sources': ['silva:D13324/#3', 'study713:361838', 'ncbi:33090'],
      'unique_name': 'Chloroplastida'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'Archaeplastida',
      'ott_id': 5268475,
      'rank': 'kingdom',
      'source': 'ott3.7draft3',
      'synonyms': ['Plantae'],
      'tax_sources': ['silva:D13324/#2', 'worms:3', 'gbif:6', 'irmng:15'],
      'unique_name': 'Archaeplastida'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'Eukaryota',
      'ott_id': 304358,
      'rank': 'domain',
      'source': 'ott3.7draft3',
      'synonyms': ['D4P07G08',
       'DH147-EKD10',
       'DH147-EKD23',
       'Eucaryotae',
       'Eukarya',
       'Eukaryotae',
       'LG25-05',
       'NAMAKO-1',
       'RT5iin25',
       'SA1-3C06'],
      'tax_sources': ['silva:D11377/#1', 'ncbi:2759'],
      'unique_name': 'Eukaryota'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'cellular organisms',
      'ott_id': 93302,
      'rank': 'no rank',
      'source': 'ott3.7draft3',
      'synonyms': ['biota'],
      'tax_sources': ['ncbi:131567'],
      'unique_name': 'cellular organisms'},
     {'flags': [],
      'is_suppressed': False,
      'is_suppressed_from_synth': False,
      'name': 'life',
      'ott_id': 805080,
      'rank': 'no rank',
      'source': 'ott3.7draft3',
      'synonyms': ['all'],
      'tax_sources': ['silva:0', 'ncbi:1', 'gbif:0', 'irmng:0'],
      'unique_name': 'life'}]




```python
toytree.otol.fetch_json_mrca(["Orobanche", "Lindenbergia"])

```




    {'mrca': {'conflicts_with': {'ot_2304@tree2': ['node8859',
        'node8941',
        'node9051',
        'node9075',
        'node9393',
        'node9403',
        'node9404',
        'node9405']},
      'node_id': 'ott5263556',
      'num_tips': 28827,
      'partial_path_of': {'ot_1417@Tr94055': 'Tn13857041',
       'ot_1624@Tr85668': 'Tn12609901',
       'ot_535@tree1': 'node112',
       'ot_859@tree1': 'node177',
       'pg_2820@tree6566': 'node1140546'},
      'supported_by': {'ot_2304@tree4': 'node20399',
       'ot_311@tree1': 'node60025',
       'ot_502@tree1': 'node986',
       'ott3.7draft3': 'ott5263556',
       'pg_2539@tree6294': 'node1094751',
       'pg_713@tree1287': 'node435792'},
      'taxon': {'name': 'Core_Lamiales',
       'ott_id': 5263556,
       'rank': 'no rank',
       'tax_sources': ['study713:13'],
       'unique_name': 'Core_Lamiales'},
      'terminal': {'ot_2089@Tr65393': 'Tn10413075', 'ot_2116@tree1': 'node173'}},
     'source_id_map': {'ot_1417@Tr94055': {'git_sha': '',
       'study_id': 'ot_1417',
       'tree_id': 'Tr94055'},
      'ot_1624@Tr85668': {'git_sha': '',
       'study_id': 'ot_1624',
       'tree_id': 'Tr85668'},
      'ot_2089@Tr65393': {'git_sha': '',
       'study_id': 'ot_2089',
       'tree_id': 'Tr65393'},
      'ot_2116@tree1': {'git_sha': '', 'study_id': 'ot_2116', 'tree_id': 'tree1'},
      'ot_2304@tree2': {'git_sha': '', 'study_id': 'ot_2304', 'tree_id': 'tree2'},
      'ot_2304@tree4': {'git_sha': '', 'study_id': 'ot_2304', 'tree_id': 'tree4'},
      'ot_311@tree1': {'git_sha': '', 'study_id': 'ot_311', 'tree_id': 'tree1'},
      'ot_502@tree1': {'git_sha': '', 'study_id': 'ot_502', 'tree_id': 'tree1'},
      'ot_535@tree1': {'git_sha': '', 'study_id': 'ot_535', 'tree_id': 'tree1'},
      'ot_859@tree1': {'git_sha': '', 'study_id': 'ot_859', 'tree_id': 'tree1'},
      'ott3.7draft3': {'taxonomy': 'ott3.7draft3'},
      'pg_2539@tree6294': {'git_sha': '',
       'study_id': 'pg_2539',
       'tree_id': 'tree6294'},
      'pg_2820@tree6566': {'git_sha': '',
       'study_id': 'pg_2820',
       'tree_id': 'tree6566'},
      'pg_713@tree1287': {'git_sha': '',
       'study_id': 'pg_713',
       'tree_id': 'tree1287'}},
     'synth_id': 'opentree16.1'}




```python
toytree.otol.fetch_json_node_info("ott918756")

```




    [{'broken': True,
      'conflicts_with': {'ot_2304@tree2': ['node8859',
        'node8941',
        'node9051',
        'node9075',
        'node9393',
        'node9403',
        'node9404',
        'node9405']},
      'node_id': 'ott5263556',
      'num_tips': 28827,
      'partial_path_of': {'ot_1417@Tr94055': 'Tn13857041',
       'ot_1624@Tr85668': 'Tn12609901',
       'ot_535@tree1': 'node112',
       'ot_859@tree1': 'node177',
       'pg_2820@tree6566': 'node1140546'},
      'query': 'ott918756',
      'source_id_map': {'ot_1417@Tr94055': {'git_sha': '',
        'study_id': 'ot_1417',
        'tree_id': 'Tr94055'},
       'ot_1624@Tr85668': {'git_sha': '',
        'study_id': 'ot_1624',
        'tree_id': 'Tr85668'},
       'ot_2089@Tr65393': {'git_sha': '',
        'study_id': 'ot_2089',
        'tree_id': 'Tr65393'},
       'ot_2116@tree1': {'git_sha': '', 'study_id': 'ot_2116', 'tree_id': 'tree1'},
       'ot_2304@tree2': {'git_sha': '', 'study_id': 'ot_2304', 'tree_id': 'tree2'},
       'ot_2304@tree4': {'git_sha': '', 'study_id': 'ot_2304', 'tree_id': 'tree4'},
       'ot_311@tree1': {'git_sha': '', 'study_id': 'ot_311', 'tree_id': 'tree1'},
       'ot_502@tree1': {'git_sha': '', 'study_id': 'ot_502', 'tree_id': 'tree1'},
       'ot_535@tree1': {'git_sha': '', 'study_id': 'ot_535', 'tree_id': 'tree1'},
       'ot_859@tree1': {'git_sha': '', 'study_id': 'ot_859', 'tree_id': 'tree1'},
       'ott3.7draft3': {'taxonomy': 'ott3.7draft3'},
       'pg_2539@tree6294': {'git_sha': '',
        'study_id': 'pg_2539',
        'tree_id': 'tree6294'},
       'pg_2820@tree6566': {'git_sha': '',
        'study_id': 'pg_2820',
        'tree_id': 'tree6566'},
       'pg_713@tree1287': {'git_sha': '',
        'study_id': 'pg_713',
        'tree_id': 'tree1287'}},
      'supported_by': {'ot_2304@tree4': 'node20399',
       'ot_311@tree1': 'node60025',
       'ot_502@tree1': 'node986',
       'ott3.7draft3': 'ott5263556',
       'pg_2539@tree6294': 'node1094751',
       'pg_713@tree1287': 'node435792'},
      'synth_id': 'opentree16.1',
      'taxon': {'name': 'Core_Lamiales',
       'ott_id': 5263556,
       'rank': 'no rank',
       'tax_sources': ['study713:13'],
       'unique_name': 'Core_Lamiales'},
      'terminal': {'ot_2089@Tr65393': 'Tn10413075', 'ot_2116@tree1': 'node173'}}]




```python


```


```python
toytree.otol.match_names(SUBTREE_GEN_LIST, output="raw")

```




    {'context': 'Flowering plants',
     'governing_code': 'ICN',
     'includes_approximate_matches': False,
     'includes_deprecated_taxa': False,
     'includes_suppressed_names': False,
     'matched_names': ['Castilleja',
      'Orobanche',
      'Pedicularis',
      'Mimulus',
      'Erythranthe',
      'Aquilegia',
      'Quercus',
      'Boswellia'],
     'results': [{'matches': [{'is_approximate_match': False,
         'is_synonym': False,
         'matched_name': 'Castilleja',
         'nomenclature_code': 'ICN',
         'score': 1.0,
         'search_string': 'castilleja',
         'taxon': {'flags': [],
          'is_suppressed': False,
          'is_suppressed_from_synth': False,
          'name': 'Castilleja',
          'ott_id': 317400,
          'rank': 'genus',
          'source': 'ott3.7draft3',
          'synonyms': ['Euchroma', 'Gentrya', 'Ophiocephalus'],
          'tax_sources': ['study713:88',
           'ncbi:46036',
           'gbif:3170565',
           'irmng:1010255'],
          'unique_name': 'Castilleja'}}],
       'name': 'Castilleja'},
      {'matches': [{'is_approximate_match': False,
         'is_synonym': False,
         'matched_name': 'Orobanche',
         'nomenclature_code': 'ICN',
         'score': 1.0,
         'search_string': 'orobanche',
         'taxon': {'flags': [],
          'is_suppressed': False,
          'is_suppressed_from_synth': False,
          'name': 'Orobanche',
          'ott_id': 918756,
          'rank': 'genus',
          'source': 'ott3.7draft3',
          'synonyms': ['Aphyllon', 'Boulardia', 'Myzorrhiza', 'Phelipanche'],
          'tax_sources': ['study713:81',
           'ncbi:36747',
           'worms:425727',
           'gbif:3173259',
           'irmng:1019858'],
          'unique_name': 'Orobanche'}}],
       'name': 'Orobanche'},
      {'matches': [{'is_approximate_match': False,
         'is_synonym': False,
         'matched_name': 'Pedicularis',
         'nomenclature_code': 'ICN',
         'score': 1.0,
         'search_string': 'pedicularis',
         'taxon': {'flags': ['sibling_higher'],
          'is_suppressed': False,
          'is_suppressed_from_synth': False,
          'name': 'Pedicularis',
          'ott_id': 989660,
          'rank': 'genus',
          'source': 'ott3.7draft3',
          'synonyms': ['Pediculariopsis'],
          'tax_sources': ['study713:86',
           'ncbi:43174',
           'gbif:3171670',
           'irmng:1038450'],
          'unique_name': 'Pedicularis'}}],
       'name': 'Pedicularis'},
      {'matches': [{'is_approximate_match': False,
         'is_synonym': False,
         'matched_name': 'Mimulus',
         'nomenclature_code': 'ICN',
         'score': 1.0,
         'search_string': 'mimulus',
         'taxon': {'flags': [],
          'is_suppressed': False,
          'is_suppressed_from_synth': False,
          'name': 'Mimulus',
          'ott_id': 596470,
          'rank': 'genus',
          'source': 'ott3.7draft3',
          'synonyms': ['Diplacus', 'Eunanus', 'Mimetanthe'],
          'tax_sources': ['study713:74',
           'ncbi:4154',
           'gbif:6008574',
           'irmng:1301444',
           'irmng:1301412'],
          'unique_name': 'Mimulus'}}],
       'name': 'Mimulus'},
      {'matches': [{'is_approximate_match': False,
         'is_synonym': False,
         'matched_name': 'Erythranthe',
         'nomenclature_code': 'ICN',
         'score': 1.0,
         'search_string': 'erythranthe',
         'taxon': {'flags': [],
          'is_suppressed': False,
          'is_suppressed_from_synth': False,
          'name': 'Erythranthe',
          'ott_id': 5334418,
          'rank': 'genus',
          'source': 'ott3.7draft3',
          'synonyms': [],
          'tax_sources': ['ncbi:1502711', 'gbif:3171742', 'irmng:1042751'],
          'unique_name': 'Erythranthe'}}],
       'name': 'Erythranthe'},
      {'matches': [{'is_approximate_match': False,
         'is_synonym': False,
         'matched_name': 'Aquilegia',
         'nomenclature_code': 'ICN',
         'score': 1.0,
         'search_string': 'aquilegia',
         'taxon': {'flags': [],
          'is_suppressed': False,
          'is_suppressed_from_synth': False,
          'name': 'Aquilegia',
          'ott_id': 964055,
          'rank': 'genus',
          'source': 'ott3.7draft3',
          'synonyms': [],
          'tax_sources': ['ncbi:3450', 'gbif:3033167', 'irmng:1025084'],
          'unique_name': 'Aquilegia'}}],
       'name': 'Aquilegia'},
      {'matches': [{'is_approximate_match': False,
         'is_synonym': False,
         'matched_name': 'Quercus',
         'nomenclature_code': 'ICN',
         'score': 1.0,
         'search_string': 'quercus',
         'taxon': {'flags': [],
          'is_suppressed': False,
          'is_suppressed_from_synth': False,
          'name': 'Quercus',
          'ott_id': 791121,
          'rank': 'genus',
          'source': 'ott3.7draft3',
          'synonyms': ['Cyclobalanopsis', 'Dryopsila', 'Ilex', 'Perytis'],
          'tax_sources': ['ncbi:3511',
           'gbif:2877951',
           'irmng:1353947',
           'irmng:1088291',
           'irmng:1022836'],
          'unique_name': 'Quercus'}}],
       'name': 'Quercus'},
      {'matches': [{'is_approximate_match': False,
         'is_synonym': False,
         'matched_name': 'Boswellia',
         'nomenclature_code': 'ICN',
         'score': 1.0,
         'search_string': 'boswellia',
         'taxon': {'flags': [],
          'is_suppressed': False,
          'is_suppressed_from_synth': False,
          'name': 'Boswellia',
          'ott_id': 733734,
          'rank': 'genus',
          'source': 'ott3.7draft3',
          'synonyms': [],
          'tax_sources': ['ncbi:80276', 'gbif:3190439', 'irmng:1307840'],
          'unique_name': 'Boswellia'}}],
       'name': 'Boswellia'}],
     'taxonomy': {'author': 'open tree of life project',
      'name': 'ott',
      'source': 'ott3.7draft3',
      'version': '3.7',
      'weburl': 'https://tree.opentreeoflife.org/about/taxonomy-version/ott3.7'},
     'unambiguous_names': ['Castilleja',
      'Orobanche',
      'Pedicularis',
      'Mimulus',
      'Erythranthe',
      'Aquilegia',
      'Quercus',
      'Boswellia'],
     'unmatched_names': []}




```python
nwk = toytree.otol.induced_subtree(SUBTREE_SPP_LIST, insert_broken_nodes=True)
toytree.tree(nwk).draw();

```


    ---------------------------------------------------------------------------

    ToytreeError                              Traceback (most recent call last)

    Cell In[58], line 1
    ----> 1 nwk = toytree.otol.induced_subtree(SUBTREE_SPP_LIST, insert_broken_nodes=True)
          2 toytree.tree(nwk).draw();


    File ~/Documents/tools/toytree/toytree/otol/src/otol.py:1020, in induced_subtree(query, full_json, label_format, insert_broken_nodes)
       1013 def induced_subtree(
       1014     query: Sequence[int | str],
       1015     full_json: bool = False,
       1016     label_format: str = "name_and_id",
       1017     insert_broken_nodes: bool = False,
       1018 ) -> str | dict[str, Any]:
       1019     """Return induced subtree for mixed query values."""
    -> 1020     return _get_default_client().get_synthetic_induced_subtree(
       1021         query=query,
       1022         full_json=full_json,
       1023         label_format=label_format,
       1024         insert_broken_nodes=insert_broken_nodes,
       1025     )


    File ~/Documents/tools/toytree/toytree/otol/src/otol.py:709, in _OTOLClient.get_synthetic_induced_subtree(self, query, full_json, label_format, insert_broken_nodes)
        701 def get_synthetic_induced_subtree(
        702     self,
        703     query: Sequence[int | str],
       (...)
        706     insert_broken_nodes: bool = False,
        707 ) -> str | dict[str, Any]:
        708     """Return induced subtree for a mixed query list."""
    --> 709     node_ids = self._query_to_node_ids(query)
        710     ott_ids: list[int] = []
        711     for node_id in node_ids:


    File ~/Documents/tools/toytree/toytree/otol/src/otol.py:413, in _OTOLClient._query_to_node_ids(self, query)
        410     names.append(text)
        412 if names:
    --> 413     table = self.resolve_names(names, on_unresolved="raise")
        414     for idx, ott_id in zip(name_positions, table["ott_id"].tolist()):
        415         out[idx] = f"ott{int(ott_id)}"


    File ~/Documents/tools/toytree/toytree/otol/src/otol.py:388, in _OTOLClient.resolve_names(self, query, do_approximate_matching, context, include_synonyms, on_unresolved, on_ambiguous)
        386     message = f"TNRS resolution has unresolved rows: {amb} ambiguous, {unm} unmatched."
        387     if on_unresolved == "raise":
    --> 388         raise ToytreeError(message)
        389     warnings.warn(message, stacklevel=2)
        390 return table


    ToytreeError: TNRS resolution has unresolved rows: 1 ambiguous, 1 unmatched.



```python
toytree.otol.node_info('mrcaott1452ott33561')

```




    [{'conflicts_with': {'ot_1417@Tr94055': ['Tn13857001'],
       'ot_1624@Tr85668': ['Tn12610356'],
       'ot_311@tree1': ['node60030',
        'node60060',
        'node60062',
        'node60090',
        'node60394',
        'node60440',
        'node60441',
        'node60755',
        'node60801',
        'node60802',
        'node60806',
        'node60814',
        'node60908',
        'node60909',
        'node60919',
        'node60925',
        'node60927',
        'node60960',
        'node60970',
        'node61052',
        'node61124',
        'node61125',
        'node61127',
        'node61128',
        'node61135',
        'node61137',
        'node61143',
        'node61147',
        'node61149',
        'node61151',
        'node61159',
        'node61170',
        'node61172',
        'node61180',
        'node61182',
        'node61184',
        'node61202',
        'node61221',
        'node61371',
        'node61372',
        'node61373',
        'node61374',
        'node61398',
        'node61399',
        'node62425',
        'node62427',
        'node62429',
        'node62430',
        'node62432',
        'node62446',
        'node62584',
        'node62586',
        'node62612',
        'node62624',
        'node62646',
        'node62658',
        'node62659',
        'node62661',
        'node62673',
        'node62674',
        'node62680',
        'node62684',
        'node62711',
        'node62713',
        'node62715',
        'node62719',
        'node62758',
        'node62780',
        'node62782',
        'node62792',
        'node62814',
        'node62830',
        'node62838',
        'node62840',
        'node62861',
        'node62891',
        'node62945',
        'node62949',
        'node62973',
        'node63069',
        'node63157',
        'node63158',
        'node63170',
        'node63206',
        'node63232',
        'node63234',
        'node63235',
        'node63258',
        'node63266',
        'node63267',
        'node63274',
        'node63276',
        'node63282'],
       'pg_1118@tree2226': ['node540308',
        'node540352',
        'node540376',
        'node540377',
        'node540389',
        'node540395',
        'node540396',
        'node540397',
        'node540398',
        'node540399',
        'node540403',
        'node540421'],
       'pg_2044@tree4212': ['node781294',
        'node781302',
        'node781336',
        'node781338',
        'node781390',
        'node781391',
        'node781401',
        'node781402',
        'node781404']},
      'node_id': 'mrcaott1452ott33561',
      'num_tips': 9853,
      'partial_path_of': {'ot_2304@tree2': 'node9551',
       'ot_2304@tree4': 'node20521',
       'ot_859@tree1': 'node179',
       'pg_713@tree1287': 'node435879'},
      'query': 'mrcaott1452ott33561',
      'source_id_map': {'ot_1417@Tr94055': {'git_sha': '',
        'study_id': 'ot_1417',
        'tree_id': 'Tr94055'},
       'ot_1624@Tr85668': {'git_sha': '',
        'study_id': 'ot_1624',
        'tree_id': 'Tr85668'},
       'ot_2089@Tr65393': {'git_sha': '',
        'study_id': 'ot_2089',
        'tree_id': 'Tr65393'},
       'ot_2116@tree1': {'git_sha': '', 'study_id': 'ot_2116', 'tree_id': 'tree1'},
       'ot_2304@tree2': {'git_sha': '', 'study_id': 'ot_2304', 'tree_id': 'tree2'},
       'ot_2304@tree4': {'git_sha': '', 'study_id': 'ot_2304', 'tree_id': 'tree4'},
       'ot_311@tree1': {'git_sha': '', 'study_id': 'ot_311', 'tree_id': 'tree1'},
       'ot_502@tree1': {'git_sha': '', 'study_id': 'ot_502', 'tree_id': 'tree1'},
       'ot_535@tree1': {'git_sha': '', 'study_id': 'ot_535', 'tree_id': 'tree1'},
       'ot_859@tree1': {'git_sha': '', 'study_id': 'ot_859', 'tree_id': 'tree1'},
       'pg_1118@tree2226': {'git_sha': '',
        'study_id': 'pg_1118',
        'tree_id': 'tree2226'},
       'pg_2044@tree4212': {'git_sha': '',
        'study_id': 'pg_2044',
        'tree_id': 'tree4212'},
       'pg_2539@tree6294': {'git_sha': '',
        'study_id': 'pg_2539',
        'tree_id': 'tree6294'},
       'pg_2820@tree6566': {'git_sha': '',
        'study_id': 'pg_2820',
        'tree_id': 'tree6566'},
       'pg_713@tree1287': {'git_sha': '',
        'study_id': 'pg_713',
        'tree_id': 'tree1287'}},
      'supported_by': {'ot_502@tree1': 'node1004',
       'pg_2539@tree6294': 'node1094779'},
      'synth_id': 'opentree16.1',
      'terminal': {'ot_2089@Tr65393': 'Tn10413075',
       'ot_2116@tree1': 'node173',
       'ot_535@tree1': 'ott648839',
       'pg_2820@tree6566': 'node1140548'}}]




```python
nwk = toytree.otol.study_tree(study_id='pg_1944', tree_id='tree3959',)

```


```python
toytree.tree(nwk).draw();

```


<div class="toyplot" id="tfa4fbe37d23649b888db68c9441b0032" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="641.768px" height="1000.0px" viewBox="0 0 641.768 1000.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tc40f65db07344202af36f2d8c0818bf2"><g class="toyplot-coordinates-Cartesian" id="t7fc05a9528b44e1b9dd1fa63c25a718f"><clipPath id="tf20d22eeb1ec4ee48a5a656d3ef0ff08"><rect x="35.0" y="35.0" width="571.768" height="930.0"></rect></clipPath><g clip-path="url(#tf20d22eeb1ec4ee48a5a656d3ef0ff08)"><g class="toytree-mark-Toytree" id="t3b61a76821e842d0a179f2831c95877c"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 369.7 939.3 L 369.7 942.8 L 395.6 942.8" id="127,0" style=""></path><path d="M 369.7 939.3 L 369.7 935.8 L 412.5 935.8" id="127,1" style=""></path><path d="M 377.2 925.2 L 377.2 928.7 L 425.4 928.7" id="128,2" style=""></path><path d="M 377.2 925.2 L 377.2 921.7 L 415.2 921.7" id="128,3" style=""></path><path d="M 309.3 923.5 L 309.3 914.7 L 326.4 914.7" id="130,4" style=""></path><path d="M 296.2 915.6 L 296.2 907.7 L 323.6 907.7" id="131,5" style=""></path><path d="M 326.0 897.1 L 326.0 900.6 L 339.1 900.6" id="132,6" style=""></path><path d="M 326.0 897.1 L 326.0 893.6 L 344.5 893.6" id="132,7" style=""></path><path d="M 318.1 891.8 L 318.1 886.6 L 352.5 886.6" id="133,8" style=""></path><path d="M 291.0 885.7 L 291.0 879.5 L 310.0 879.5" id="134,9" style=""></path><path d="M 294.7 869.0 L 294.7 872.5 L 317.1 872.5" id="136,10" style=""></path><path d="M 294.7 869.0 L 294.7 865.5 L 308.9 865.5" id="136,11" style=""></path><path d="M 291.3 863.7 L 291.3 858.5 L 314.5 858.5" id="137,12" style=""></path><path d="M 280.7 857.6 L 280.7 851.4 L 293.8 851.4" id="138,13" style=""></path><path d="M 291.8 840.9 L 291.8 844.4 L 300.8 844.4" id="140,14" style=""></path><path d="M 291.8 840.9 L 291.8 837.4 L 297.5 837.4" id="140,15" style=""></path><path d="M 290.3 835.6 L 290.3 830.3 L 300.2 830.3" id="141,16" style=""></path><path d="M 288.6 829.5 L 288.6 823.3 L 296.6 823.3" id="142,17" style=""></path><path d="M 284.8 812.8 L 284.8 816.3 L 303.8 816.3" id="144,18" style=""></path><path d="M 284.8 812.8 L 284.8 809.3 L 295.7 809.3" id="144,19" style=""></path><path d="M 283.2 807.5 L 283.2 802.2 L 299.9 802.2" id="145,20" style=""></path><path d="M 281.6 801.4 L 281.6 795.2 L 303.5 795.2" id="146,21" style=""></path><path d="M 260.9 794.8 L 260.9 788.2 L 297.0 788.2" id="147,22" style=""></path><path d="M 265.5 777.6 L 265.5 781.1 L 271.5 781.1" id="149,23" style=""></path><path d="M 265.5 777.6 L 265.5 774.1 L 278.7 774.1" id="149,24" style=""></path><path d="M 271.0 763.6 L 271.0 767.1 L 284.5 767.1" id="151,25" style=""></path><path d="M 271.0 763.6 L 271.0 760.1 L 278.4 760.1" id="151,26" style=""></path><path d="M 268.7 758.3 L 268.7 753.0 L 277.5 753.0" id="152,27" style=""></path><path d="M 240.8 752.2 L 240.8 746.0 L 248.2 746.0" id="153,28" style=""></path><path d="M 218.8 745.6 L 218.8 739.0 L 242.6 739.0" id="154,29" style=""></path><path d="M 210.9 728.4 L 210.9 731.9 L 227.2 731.9" id="156,30" style=""></path><path d="M 210.9 728.4 L 210.9 724.9 L 235.4 724.9" id="156,31" style=""></path><path d="M 205.6 723.2 L 205.6 717.9 L 236.6 717.9" id="157,32" style=""></path><path d="M 324.8 707.3 L 324.8 710.9 L 339.0 710.9" id="159,33" style=""></path><path d="M 324.8 707.3 L 324.8 703.8 L 332.8 703.8" id="159,34" style=""></path><path d="M 319.4 702.1 L 319.4 696.8 L 342.4 696.8" id="160,35" style=""></path><path d="M 309.1 695.9 L 309.1 689.8 L 345.6 689.8" id="161,36" style=""></path><path d="M 278.0 689.3 L 278.0 682.7 L 297.2 682.7" id="162,37" style=""></path><path d="M 271.6 672.2 L 271.6 675.7 L 289.2 675.7" id="163,38" style=""></path><path d="M 271.6 672.2 L 271.6 668.7 L 304.4 668.7" id="163,39" style=""></path><path d="M 254.6 671.2 L 254.6 661.7 L 321.3 661.7" id="165,40" style=""></path><path d="M 241.6 651.1 L 241.6 654.6 L 288.9 654.6" id="166,41" style=""></path><path d="M 241.6 651.1 L 241.6 647.6 L 318.9 647.6" id="166,42" style=""></path><path d="M 272.7 637.1 L 272.7 640.6 L 288.5 640.6" id="168,43" style=""></path><path d="M 272.7 637.1 L 272.7 633.5 L 290.1 633.5" id="168,44" style=""></path><path d="M 261.5 623.0 L 261.5 626.5 L 267.8 626.5" id="170,45" style=""></path><path d="M 261.5 623.0 L 261.5 619.5 L 281.7 619.5" id="170,46" style=""></path><path d="M 259.2 617.7 L 259.2 612.5 L 265.6 612.5" id="171,47" style=""></path><path d="M 261.8 601.9 L 261.8 605.4 L 275.1 605.4" id="172,48" style=""></path><path d="M 261.8 601.9 L 261.8 598.4 L 266.3 598.4" id="172,49" style=""></path><path d="M 258.8 596.6 L 258.8 591.4 L 263.0 591.4" id="173,50" style=""></path><path d="M 258.2 599.6 L 258.2 584.3 L 343.6 584.3" id="174,51" style=""></path><path d="M 262.9 573.8 L 262.9 577.3 L 272.7 577.3" id="175,52" style=""></path><path d="M 262.9 573.8 L 262.9 570.3 L 275.0 570.3" id="175,53" style=""></path><path d="M 255.1 575.0 L 255.1 563.3 L 276.6 563.3" id="177,54" style=""></path><path d="M 281.8 552.7 L 281.8 556.2 L 295.0 556.2" id="179,55" style=""></path><path d="M 281.8 552.7 L 281.8 549.2 L 293.7 549.2" id="179,56" style=""></path><path d="M 224.3 562.3 L 224.3 542.2 L 243.1 542.2" id="181,57" style=""></path><path d="M 239.4 531.6 L 239.4 535.1 L 249.3 535.1" id="182,58" style=""></path><path d="M 239.4 531.6 L 239.4 528.1 L 256.3 528.1" id="182,59" style=""></path><path d="M 236.6 526.4 L 236.6 521.1 L 251.8 521.1" id="183,60" style=""></path><path d="M 206.4 529.2 L 206.4 514.1 L 240.8 514.1" id="185,61" style=""></path><path d="M 238.5 503.5 L 238.5 507.0 L 297.0 507.0" id="187,62" style=""></path><path d="M 238.5 503.5 L 238.5 500.0 L 278.4 500.0" id="187,63" style=""></path><path d="M 264.6 489.5 L 264.6 493.0 L 270.4 493.0" id="188,64" style=""></path><path d="M 264.6 489.5 L 264.6 485.9 L 271.4 485.9" id="188,65" style=""></path><path d="M 279.9 475.4 L 279.9 478.9 L 287.9 478.9" id="191,66" style=""></path><path d="M 279.9 475.4 L 279.9 471.9 L 285.2 471.9" id="191,67" style=""></path><path d="M 273.6 470.1 L 273.6 464.9 L 282.1 464.9" id="192,68" style=""></path><path d="M 211.9 464.0 L 211.9 457.8 L 384.4 457.8" id="193,69" style=""></path><path d="M 206.7 457.4 L 206.7 450.8 L 261.6 450.8" id="194,70" style=""></path><path d="M 204.3 450.6 L 204.3 443.8 L 282.7 443.8" id="195,71" style=""></path><path d="M 202.5 443.7 L 202.5 436.7 L 257.7 436.7" id="196,72" style=""></path><path d="M 320.3 426.2 L 320.3 429.7 L 348.0 429.7" id="198,73" style=""></path><path d="M 320.3 426.2 L 320.3 422.7 L 343.9 422.7" id="198,74" style=""></path><path d="M 315.9 420.9 L 315.9 415.7 L 342.0 415.7" id="199,75" style=""></path><path d="M 329.8 405.1 L 329.8 408.6 L 343.9 408.6" id="200,76" style=""></path><path d="M 329.8 405.1 L 329.8 401.6 L 353.0 401.6" id="200,77" style=""></path><path d="M 327.4 399.8 L 327.4 394.6 L 353.4 394.6" id="201,78" style=""></path><path d="M 303.2 384.0 L 303.2 387.5 L 319.7 387.5" id="203,79" style=""></path><path d="M 303.2 384.0 L 303.2 380.5 L 326.6 380.5" id="203,80" style=""></path><path d="M 285.8 385.3 L 285.8 373.5 L 320.1 373.5" id="205,81" style=""></path><path d="M 306.0 362.9 L 306.0 366.5 L 316.0 366.5" id="206,82" style=""></path><path d="M 306.0 362.9 L 306.0 359.4 L 317.7 359.4" id="206,83" style=""></path><path d="M 302.4 357.7 L 302.4 352.4 L 322.6 352.4" id="207,84" style=""></path><path d="M 382.1 341.9 L 382.1 345.4 L 458.1 345.4" id="209,85" style=""></path><path d="M 382.1 341.9 L 382.1 338.3 L 424.1 338.3" id="209,86" style=""></path><path d="M 295.9 336.6 L 295.9 331.3 L 408.3 331.3" id="210,87" style=""></path><path d="M 263.2 320.8 L 263.2 324.3 L 271.6 324.3" id="212,88" style=""></path><path d="M 263.2 320.8 L 263.2 317.3 L 267.5 317.3" id="212,89" style=""></path><path d="M 298.3 306.7 L 298.3 310.2 L 321.3 310.2" id="213,90" style=""></path><path d="M 298.3 306.7 L 298.3 303.2 L 337.9 303.2" id="213,91" style=""></path><path d="M 299.3 292.7 L 299.3 296.2 L 409.5 296.2" id="216,92" style=""></path><path d="M 299.3 292.7 L 299.3 289.1 L 356.3 289.1" id="216,93" style=""></path><path d="M 239.5 287.4 L 239.5 282.1 L 273.2 282.1" id="217,94" style=""></path><path d="M 282.6 271.6 L 282.6 275.1 L 287.8 275.1" id="219,95" style=""></path><path d="M 282.6 271.6 L 282.6 268.1 L 294.2 268.1" id="219,96" style=""></path><path d="M 275.7 266.3 L 275.7 261.0 L 301.0 261.0" id="220,97" style=""></path><path d="M 272.9 260.1 L 272.9 254.0 L 300.9 254.0" id="221,98" style=""></path><path d="M 276.9 243.5 L 276.9 247.0 L 297.1 247.0" id="222,99" style=""></path><path d="M 276.9 243.5 L 276.9 239.9 L 286.4 239.9" id="222,100" style=""></path><path d="M 235.6 238.2 L 235.6 232.9 L 266.5 232.9" id="223,101" style=""></path><path d="M 227.1 252.9 L 227.1 225.9 L 329.6 225.9" id="226,102" style=""></path><path d="M 368.4 215.3 L 368.4 218.9 L 398.6 218.9" id="227,103" style=""></path><path d="M 368.4 215.3 L 368.4 211.8 L 426.4 211.8" id="227,104" style=""></path><path d="M 287.6 210.1 L 287.6 204.8 L 329.5 204.8" id="228,105" style=""></path><path d="M 378.3 194.3 L 378.3 197.8 L 425.8 197.8" id="229,106" style=""></path><path d="M 378.3 194.3 L 378.3 190.7 L 391.9 190.7" id="229,107" style=""></path><path d="M 290.6 189.0 L 290.6 183.7 L 331.9 183.7" id="230,108" style=""></path><path d="M 275.2 173.2 L 275.2 176.7 L 283.1 176.7" id="232,109" style=""></path><path d="M 275.2 173.2 L 275.2 169.7 L 281.5 169.7" id="232,110" style=""></path><path d="M 253.6 167.9 L 253.6 162.6 L 279.3 162.6" id="233,111" style=""></path><path d="M 234.5 161.7 L 234.5 155.6 L 309.6 155.6" id="234,112" style=""></path><path d="M 217.7 145.1 L 217.7 148.6 L 303.3 148.6" id="238,113" style=""></path><path d="M 217.7 145.1 L 217.7 141.5 L 260.8 141.5" id="238,114" style=""></path><path d="M 211.9 139.8 L 211.9 134.5 L 245.7 134.5" id="239,115" style=""></path><path d="M 301.9 124.0 L 301.9 127.5 L 307.9 127.5" id="240,116" style=""></path><path d="M 301.9 124.0 L 301.9 120.5 L 311.3 120.5" id="240,117" style=""></path><path d="M 300.7 118.7 L 300.7 113.4 L 313.1 113.4" id="241,118" style=""></path><path d="M 231.1 102.9 L 231.1 106.4 L 274.9 106.4" id="243,119" style=""></path><path d="M 231.1 102.9 L 231.1 99.4 L 308.7 99.4" id="243,120" style=""></path><path d="M 223.5 97.6 L 223.5 92.3 L 257.3 92.3" id="244,121" style=""></path><path d="M 285.3 81.8 L 285.3 85.3 L 300.3 85.3" id="247,122" style=""></path><path d="M 285.3 81.8 L 285.3 78.3 L 298.1 78.3" id="247,123" style=""></path><path d="M 208.0 72.4 L 208.0 71.3 L 331.7 71.3" id="248,124" style=""></path><path d="M 208.0 72.4 L 208.0 64.2 L 337.4 64.2" id="248,125" style=""></path><path d="M 51.0 106.0 L 51.0 57.2 L 175.8 57.2" id="250,126" style=""></path><path d="M 350.7 932.3 L 350.7 939.3 L 369.7 939.3" id="129,127" style=""></path><path d="M 350.7 932.3 L 350.7 925.2 L 377.2 925.2" id="129,128" style=""></path><path d="M 309.3 923.5 L 309.3 932.3 L 350.7 932.3" id="130,129" style=""></path><path d="M 296.2 915.6 L 296.2 923.5 L 309.3 923.5" id="131,130" style=""></path><path d="M 285.3 900.6 L 285.3 915.6 L 296.2 915.6" id="135,131" style=""></path><path d="M 318.1 891.8 L 318.1 897.1 L 326.0 897.1" id="133,132" style=""></path><path d="M 291.0 885.7 L 291.0 891.8 L 318.1 891.8" id="134,133" style=""></path><path d="M 285.3 900.6 L 285.3 885.7 L 291.0 885.7" id="135,134" style=""></path><path d="M 278.5 879.1 L 278.5 900.6 L 285.3 900.6" id="139,135" style=""></path><path d="M 291.3 863.7 L 291.3 869.0 L 294.7 869.0" id="137,136" style=""></path><path d="M 280.7 857.6 L 280.7 863.7 L 291.3 863.7" id="138,137" style=""></path><path d="M 278.5 879.1 L 278.5 857.6 L 280.7 857.6" id="139,138" style=""></path><path d="M 277.3 854.3 L 277.3 879.1 L 278.5 879.1" id="143,139" style=""></path><path d="M 290.3 835.6 L 290.3 840.9 L 291.8 840.9" id="141,140" style=""></path><path d="M 288.6 829.5 L 288.6 835.6 L 290.3 835.6" id="142,141" style=""></path><path d="M 277.3 854.3 L 277.3 829.5 L 288.6 829.5" id="143,142" style=""></path><path d="M 257.4 824.5 L 257.4 854.3 L 277.3 854.3" id="148,143" style=""></path><path d="M 283.2 807.5 L 283.2 812.8 L 284.8 812.8" id="145,144" style=""></path><path d="M 281.6 801.4 L 281.6 807.5 L 283.2 807.5" id="146,145" style=""></path><path d="M 260.9 794.8 L 260.9 801.4 L 281.6 801.4" id="147,146" style=""></path><path d="M 257.4 824.5 L 257.4 794.8 L 260.9 794.8" id="148,147" style=""></path><path d="M 254.0 801.1 L 254.0 824.5 L 257.4 824.5" id="150,148" style=""></path><path d="M 254.0 801.1 L 254.0 777.6 L 265.5 777.6" id="150,149" style=""></path><path d="M 207.5 773.3 L 207.5 801.1 L 254.0 801.1" id="155,150" style=""></path><path d="M 268.7 758.3 L 268.7 763.6 L 271.0 763.6" id="152,151" style=""></path><path d="M 240.8 752.2 L 240.8 758.3 L 268.7 758.3" id="153,152" style=""></path><path d="M 218.8 745.6 L 218.8 752.2 L 240.8 752.2" id="154,153" style=""></path><path d="M 207.5 773.3 L 207.5 745.6 L 218.8 745.6" id="155,154" style=""></path><path d="M 202.8 748.2 L 202.8 773.3 L 207.5 773.3" id="158,155" style=""></path><path d="M 205.6 723.2 L 205.6 728.4 L 210.9 728.4" id="157,156" style=""></path><path d="M 202.8 748.2 L 202.8 723.2 L 205.6 723.2" id="158,157" style=""></path><path d="M 199.8 638.7 L 199.8 748.2 L 202.8 748.2" id="186,158" style=""></path><path d="M 319.4 702.1 L 319.4 707.3 L 324.8 707.3" id="160,159" style=""></path><path d="M 309.1 695.9 L 309.1 702.1 L 319.4 702.1" id="161,160" style=""></path><path d="M 278.0 689.3 L 278.0 695.9 L 309.1 695.9" id="162,161" style=""></path><path d="M 262.7 680.8 L 262.7 689.3 L 278.0 689.3" id="164,162" style=""></path><path d="M 262.7 680.8 L 262.7 672.2 L 271.6 672.2" id="164,163" style=""></path><path d="M 254.6 671.2 L 254.6 680.8 L 262.7 680.8" id="165,164" style=""></path><path d="M 240.4 661.2 L 240.4 671.2 L 254.6 671.2" id="167,165" style=""></path><path d="M 240.4 661.2 L 240.4 651.1 L 241.6 651.1" id="167,166" style=""></path><path d="M 237.4 649.1 L 237.4 661.2 L 240.4 661.2" id="169,167" style=""></path><path d="M 237.4 649.1 L 237.4 637.1 L 272.7 637.1" id="169,168" style=""></path><path d="M 235.4 612.0 L 235.4 649.1 L 237.4 649.1" id="178,169" style=""></path><path d="M 259.2 617.7 L 259.2 623.0 L 261.5 623.0" id="171,170" style=""></path><path d="M 258.2 599.6 L 258.2 617.7 L 259.2 617.7" id="174,171" style=""></path><path d="M 258.8 596.6 L 258.8 601.9 L 261.8 601.9" id="173,172" style=""></path><path d="M 258.2 599.6 L 258.2 596.6 L 258.8 596.6" id="174,173" style=""></path><path d="M 257.8 586.7 L 257.8 599.6 L 258.2 599.6" id="176,174" style=""></path><path d="M 257.8 586.7 L 257.8 573.8 L 262.9 573.8" id="176,175" style=""></path><path d="M 255.1 575.0 L 255.1 586.7 L 257.8 586.7" id="177,176" style=""></path><path d="M 235.4 612.0 L 235.4 575.0 L 255.1 575.0" id="178,177" style=""></path><path d="M 232.9 582.4 L 232.9 612.0 L 235.4 612.0" id="180,178" style=""></path><path d="M 232.9 582.4 L 232.9 552.7 L 281.8 552.7" id="180,179" style=""></path><path d="M 224.3 562.3 L 224.3 582.4 L 232.9 582.4" id="181,180" style=""></path><path d="M 222.3 544.3 L 222.3 562.3 L 224.3 562.3" id="184,181" style=""></path><path d="M 236.6 526.4 L 236.6 531.6 L 239.4 531.6" id="183,182" style=""></path><path d="M 222.3 544.3 L 222.3 526.4 L 236.6 526.4" id="184,183" style=""></path><path d="M 206.4 529.2 L 206.4 544.3 L 222.3 544.3" id="185,184" style=""></path><path d="M 199.8 638.7 L 199.8 529.2 L 206.4 529.2" id="186,185" style=""></path><path d="M 198.3 567.6 L 198.3 638.7 L 199.8 638.7" id="190,186" style=""></path><path d="M 203.6 496.5 L 203.6 503.5 L 238.5 503.5" id="189,187" style=""></path><path d="M 203.6 496.5 L 203.6 489.5 L 264.6 489.5" id="189,188" style=""></path><path d="M 198.3 567.6 L 198.3 496.5 L 203.6 496.5" id="190,189" style=""></path><path d="M 196.3 505.6 L 196.3 567.6 L 198.3 567.6" id="197,190" style=""></path><path d="M 273.6 470.1 L 273.6 475.4 L 279.9 475.4" id="192,191" style=""></path><path d="M 211.9 464.0 L 211.9 470.1 L 273.6 470.1" id="193,192" style=""></path><path d="M 206.7 457.4 L 206.7 464.0 L 211.9 464.0" id="194,193" style=""></path><path d="M 204.3 450.6 L 204.3 457.4 L 206.7 457.4" id="195,194" style=""></path><path d="M 202.5 443.7 L 202.5 450.6 L 204.3 450.6" id="196,195" style=""></path><path d="M 196.3 505.6 L 196.3 443.7 L 202.5 443.7" id="197,196" style=""></path><path d="M 195.3 361.2 L 195.3 505.6 L 196.3 505.6" id="237,197" style=""></path><path d="M 315.9 420.9 L 315.9 426.2 L 320.3 426.2" id="199,198" style=""></path><path d="M 307.4 410.4 L 307.4 420.9 L 315.9 420.9" id="202,199" style=""></path><path d="M 327.4 399.8 L 327.4 405.1 L 329.8 405.1" id="201,200" style=""></path><path d="M 307.4 410.4 L 307.4 399.8 L 327.4 399.8" id="202,201" style=""></path><path d="M 299.1 397.2 L 299.1 410.4 L 307.4 410.4" id="204,202" style=""></path><path d="M 299.1 397.2 L 299.1 384.0 L 303.2 384.0" id="204,203" style=""></path><path d="M 285.8 385.3 L 285.8 397.2 L 299.1 397.2" id="205,204" style=""></path><path d="M 282.7 371.5 L 282.7 385.3 L 285.8 385.3" id="208,205" style=""></path><path d="M 302.4 357.7 L 302.4 362.9 L 306.0 362.9" id="207,206" style=""></path><path d="M 282.7 371.5 L 282.7 357.7 L 302.4 357.7" id="208,207" style=""></path><path d="M 275.2 354.0 L 275.2 371.5 L 282.7 371.5" id="211,208" style=""></path><path d="M 295.9 336.6 L 295.9 341.9 L 382.1 341.9" id="210,209" style=""></path><path d="M 275.2 354.0 L 275.2 336.6 L 295.9 336.6" id="211,210" style=""></path><path d="M 241.2 333.9 L 241.2 354.0 L 275.2 354.0" id="215,211" style=""></path><path d="M 254.7 313.7 L 254.7 320.8 L 263.2 320.8" id="214,212" style=""></path><path d="M 254.7 313.7 L 254.7 306.7 L 298.3 306.7" id="214,213" style=""></path><path d="M 241.2 333.9 L 241.2 313.7 L 254.7 313.7" id="215,214" style=""></path><path d="M 232.7 310.6 L 232.7 333.9 L 241.2 333.9" id="218,215" style=""></path><path d="M 239.5 287.4 L 239.5 292.7 L 299.3 292.7" id="217,216" style=""></path><path d="M 232.7 310.6 L 232.7 287.4 L 239.5 287.4" id="218,217" style=""></path><path d="M 231.4 279.9 L 231.4 310.6 L 232.7 310.6" id="225,218" style=""></path><path d="M 275.7 266.3 L 275.7 271.6 L 282.6 271.6" id="220,219" style=""></path><path d="M 272.9 260.1 L 272.9 266.3 L 275.7 266.3" id="221,220" style=""></path><path d="M 233.8 249.2 L 233.8 260.1 L 272.9 260.1" id="224,221" style=""></path><path d="M 235.6 238.2 L 235.6 243.5 L 276.9 243.5" id="223,222" style=""></path><path d="M 233.8 249.2 L 233.8 238.2 L 235.6 238.2" id="224,223" style=""></path><path d="M 231.4 279.9 L 231.4 249.2 L 233.8 249.2" id="225,224" style=""></path><path d="M 227.1 252.9 L 227.1 279.9 L 231.4 279.9" id="226,225" style=""></path><path d="M 223.2 216.8 L 223.2 252.9 L 227.1 252.9" id="236,226" style=""></path><path d="M 287.6 210.1 L 287.6 215.3 L 368.4 215.3" id="228,227" style=""></path><path d="M 285.3 199.5 L 285.3 210.1 L 287.6 210.1" id="231,228" style=""></path><path d="M 290.6 189.0 L 290.6 194.3 L 378.3 194.3" id="230,229" style=""></path><path d="M 285.3 199.5 L 285.3 189.0 L 290.6 189.0" id="231,230" style=""></path><path d="M 226.7 180.6 L 226.7 199.5 L 285.3 199.5" id="235,231" style=""></path><path d="M 253.6 167.9 L 253.6 173.2 L 275.2 173.2" id="233,232" style=""></path><path d="M 234.5 161.7 L 234.5 167.9 L 253.6 167.9" id="234,233" style=""></path><path d="M 226.7 180.6 L 226.7 161.7 L 234.5 161.7" id="235,234" style=""></path><path d="M 223.2 216.8 L 223.2 180.6 L 226.7 180.6" id="236,235" style=""></path><path d="M 195.3 361.2 L 195.3 216.8 L 223.2 216.8" id="237,236" style=""></path><path d="M 185.3 237.3 L 185.3 361.2 L 195.3 361.2" id="246,237" style=""></path><path d="M 211.9 139.8 L 211.9 145.1 L 217.7 145.1" id="239,238" style=""></path><path d="M 205.0 129.2 L 205.0 139.8 L 211.9 139.8" id="242,239" style=""></path><path d="M 300.7 118.7 L 300.7 124.0 L 301.9 124.0" id="241,240" style=""></path><path d="M 205.0 129.2 L 205.0 118.7 L 300.7 118.7" id="242,241" style=""></path><path d="M 196.0 113.4 L 196.0 129.2 L 205.0 129.2" id="245,242" style=""></path><path d="M 223.5 97.6 L 223.5 102.9 L 231.1 102.9" id="244,243" style=""></path><path d="M 196.0 113.4 L 196.0 97.6 L 223.5 97.6" id="245,244" style=""></path><path d="M 185.3 237.3 L 185.3 113.4 L 196.0 113.4" id="246,245" style=""></path><path d="M 175.8 154.9 L 175.8 237.3 L 185.3 237.3" id="249,246" style=""></path><path d="M 208.0 72.4 L 208.0 81.8 L 285.3 81.8" id="248,247" style=""></path><path d="M 175.8 154.9 L 175.8 72.4 L 208.0 72.4" id="249,248" style=""></path><path d="M 51.0 106.0 L 51.0 154.9 L 175.8 154.9" id="250,249" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(395.597,942.8)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Centranthus</text></g><g class="toytree-TipLabel" transform="translate(412.517,935.771)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Valeriana</text></g><g class="toytree-TipLabel" transform="translate(425.376,928.743)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Valerianella</text></g><g class="toytree-TipLabel" transform="translate(415.22,921.714)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Fedia</text></g><g class="toytree-TipLabel" transform="translate(326.401,914.686)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Nardostachys</text></g><g class="toytree-TipLabel" transform="translate(323.595,907.657)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Patrinia</text></g><g class="toytree-TipLabel" transform="translate(339.072,900.629)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Dipsacus</text></g><g class="toytree-TipLabel" transform="translate(344.528,893.6)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pterocephalodes</text></g><g class="toytree-TipLabel" transform="translate(352.466,886.571)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Scabiosa</text></g><g class="toytree-TipLabel" transform="translate(309.978,879.543)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Triplostegia</text></g><g class="toytree-TipLabel" transform="translate(317.099,872.514)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Morina</text></g><g class="toytree-TipLabel" transform="translate(308.934,865.486)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Acanthocalyx</text></g><g class="toytree-TipLabel" transform="translate(314.544,858.457)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Cryptothladia</text></g><g class="toytree-TipLabel" transform="translate(293.772,851.429)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Zabelia</text></g><g class="toytree-TipLabel" transform="translate(300.839,844.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Kolkwitzia</text></g><g class="toytree-TipLabel" transform="translate(297.5,837.371)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Dipelta</text></g><g class="toytree-TipLabel" transform="translate(300.159,830.343)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Abelia</text></g><g class="toytree-TipLabel" transform="translate(296.63,823.314)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Linnaea</text></g><g class="toytree-TipLabel" transform="translate(303.752,816.286)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Triosteum</text></g><g class="toytree-TipLabel" transform="translate(295.746,809.257)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Symphoricarpos</text></g><g class="toytree-TipLabel" transform="translate(299.913,802.229)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Leycesteria</text></g><g class="toytree-TipLabel" transform="translate(303.458,795.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Lonicera</text></g><g class="toytree-TipLabel" transform="translate(296.995,788.171)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Heptacodium</text></g><g class="toytree-TipLabel" transform="translate(271.462,781.143)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Diervilla</text></g><g class="toytree-TipLabel" transform="translate(278.693,774.114)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Weigela</text></g><g class="toytree-TipLabel" transform="translate(284.519,767.086)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Tetradoxa</text></g><g class="toytree-TipLabel" transform="translate(278.425,760.057)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Adoxa</text></g><g class="toytree-TipLabel" transform="translate(277.543,753.029)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Sinadoxa</text></g><g class="toytree-TipLabel" transform="translate(248.234,746)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Sambucus</text></g><g class="toytree-TipLabel" transform="translate(242.639,738.971)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Viburnum</text></g><g class="toytree-TipLabel" transform="translate(227.218,731.943)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Sphenostemon</text></g><g class="toytree-TipLabel" transform="translate(235.369,724.914)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Paracryphia</text></g><g class="toytree-TipLabel" transform="translate(236.576,717.886)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Quintinia</text></g><g class="toytree-TipLabel" transform="translate(339.013,710.857)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Coriandrum</text></g><g class="toytree-TipLabel" transform="translate(332.756,703.829)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Angelica</text></g><g class="toytree-TipLabel" transform="translate(342.426,696.8)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Apium</text></g><g class="toytree-TipLabel" transform="translate(345.602,689.771)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Daucus</text></g><g class="toytree-TipLabel" transform="translate(297.187,682.743)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Heteromorpha</text></g><g class="toytree-TipLabel" transform="translate(289.221,675.714)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Arctopus</text></g><g class="toytree-TipLabel" transform="translate(304.395,668.686)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Sanicula</text></g><g class="toytree-TipLabel" transform="translate(321.325,661.657)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Azorella</text></g><g class="toytree-TipLabel" transform="translate(288.911,654.629)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Mackinlaya</text></g><g class="toytree-TipLabel" transform="translate(318.907,647.6)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Platysace</text></g><g class="toytree-TipLabel" transform="translate(288.496,640.571)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Myodocarpus</text></g><g class="toytree-TipLabel" transform="translate(290.053,633.543)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Delarbrea</text></g><g class="toytree-TipLabel" transform="translate(267.824,626.514)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Schefflera</text></g><g class="toytree-TipLabel" transform="translate(281.71,619.486)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Tetrapanax</text></g><g class="toytree-TipLabel" transform="translate(265.619,612.457)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Polyscias</text></g><g class="toytree-TipLabel" transform="translate(275.114,605.429)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Tetraplasandra</text></g><g class="toytree-TipLabel" transform="translate(266.257,598.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pseudopanax</text></g><g class="toytree-TipLabel" transform="translate(262.962,591.371)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Cussonia</text></g><g class="toytree-TipLabel" transform="translate(343.589,584.343)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Hydrocotyle</text></g><g class="toytree-TipLabel" transform="translate(272.727,577.314)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Panax</text></g><g class="toytree-TipLabel" transform="translate(274.977,570.286)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Aralia</text></g><g class="toytree-TipLabel" transform="translate(276.643,563.257)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Hedera</text></g><g class="toytree-TipLabel" transform="translate(295.004,556.229)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pittosporum</text></g><g class="toytree-TipLabel" transform="translate(293.713,549.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Sollya</text></g><g class="toytree-TipLabel" transform="translate(243.119,542.171)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Griselinia</text></g><g class="toytree-TipLabel" transform="translate(249.341,535.143)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Melanophylla</text></g><g class="toytree-TipLabel" transform="translate(256.338,528.114)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Torricellia</text></g><g class="toytree-TipLabel" transform="translate(251.823,521.086)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Aralidium</text></g><g class="toytree-TipLabel" transform="translate(240.84,514.057)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pennantia</text></g><g class="toytree-TipLabel" transform="translate(297.016,507.029)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Columellia</text></g><g class="toytree-TipLabel" transform="translate(278.361,500)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Desfontainia</text></g><g class="toytree-TipLabel" transform="translate(270.355,492.971)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Brunia</text></g><g class="toytree-TipLabel" transform="translate(271.421,485.943)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Berzelia</text></g><g class="toytree-TipLabel" transform="translate(287.901,478.914)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Forgesia</text></g><g class="toytree-TipLabel" transform="translate(285.156,471.886)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Valdivia</text></g><g class="toytree-TipLabel" transform="translate(282.149,464.857)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Escallonia</text></g><g class="toytree-TipLabel" transform="translate(384.386,457.829)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Eremosyne</text></g><g class="toytree-TipLabel" transform="translate(261.599,450.8)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Anopterus</text></g><g class="toytree-TipLabel" transform="translate(282.725,443.771)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Tribeles</text></g><g class="toytree-TipLabel" transform="translate(257.741,436.743)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Polyosma</text></g><g class="toytree-TipLabel" transform="translate(347.995,429.714)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Cichorium</text></g><g class="toytree-TipLabel" transform="translate(343.871,422.686)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Lactuca</text></g><g class="toytree-TipLabel" transform="translate(341.98,415.657)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Tragopogon</text></g><g class="toytree-TipLabel" transform="translate(343.888,408.629)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Guizotia</text></g><g class="toytree-TipLabel" transform="translate(353.02,401.6)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Helianthus</text></g><g class="toytree-TipLabel" transform="translate(353.385,394.571)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Tagetes</text></g><g class="toytree-TipLabel" transform="translate(319.668,387.543)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Echinops</text></g><g class="toytree-TipLabel" transform="translate(326.586,380.514)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Gerbera</text></g><g class="toytree-TipLabel" transform="translate(320.071,373.486)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Barnadesia</text></g><g class="toytree-TipLabel" transform="translate(316.008,366.457)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Moschopsis</text></g><g class="toytree-TipLabel" transform="translate(317.734,359.429)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Acicarpha</text></g><g class="toytree-TipLabel" transform="translate(322.597,352.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Boopis</text></g><g class="toytree-TipLabel" transform="translate(458.093,345.371)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Goodenia</text></g><g class="toytree-TipLabel" transform="translate(424.07,338.343)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Scaevola</text></g><g class="toytree-TipLabel" transform="translate(408.273,331.314)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Dampiera</text></g><g class="toytree-TipLabel" transform="translate(271.646,324.286)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Menyanthes</text></g><g class="toytree-TipLabel" transform="translate(267.535,317.257)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Fauria</text></g><g class="toytree-TipLabel" transform="translate(321.306,310.229)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Villarsia</text></g><g class="toytree-TipLabel" transform="translate(337.939,303.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Nymphoides</text></g><g class="toytree-TipLabel" transform="translate(409.536,296.171)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Stylidium</text></g><g class="toytree-TipLabel" transform="translate(356.334,289.143)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Forstera</text></g><g class="toytree-TipLabel" transform="translate(273.152,282.114)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Donatia</text></g><g class="toytree-TipLabel" transform="translate(287.802,275.086)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Alseuosmia</text></g><g class="toytree-TipLabel" transform="translate(294.194,268.057)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Wittsteinia</text></g><g class="toytree-TipLabel" transform="translate(300.993,261.029)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Crispiloba</text></g><g class="toytree-TipLabel" transform="translate(300.896,254)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Platyspermation</text></g><g class="toytree-TipLabel" transform="translate(297.09,246.971)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Corokia</text></g><g class="toytree-TipLabel" transform="translate(286.445,239.943)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Argophyllum</text></g><g class="toytree-TipLabel" transform="translate(266.451,232.914)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Phelline</text></g><g class="toytree-TipLabel" transform="translate(329.568,225.886)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pentaphragma</text></g><g class="toytree-TipLabel" transform="translate(398.621,218.857)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Trachelium</text></g><g class="toytree-TipLabel" transform="translate(426.414,211.829)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Campanula</text></g><g class="toytree-TipLabel" transform="translate(329.452,204.8)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Cyphia</text></g><g class="toytree-TipLabel" transform="translate(425.757,197.771)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Lobelia</text></g><g class="toytree-TipLabel" transform="translate(391.907,190.743)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Dialypetalum</text></g><g class="toytree-TipLabel" transform="translate(331.921,183.714)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pseudonemacladus</text></g><g class="toytree-TipLabel" transform="translate(283.141,176.686)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Abrophyllum</text></g><g class="toytree-TipLabel" transform="translate(281.53,169.657)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Cuttsia</text></g><g class="toytree-TipLabel" transform="translate(279.264,162.629)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Carpodetus</text></g><g class="toytree-TipLabel" transform="translate(309.569,155.6)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Roussea</text></g><g class="toytree-TipLabel" transform="translate(303.252,148.571)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Cardiopteris</text></g><g class="toytree-TipLabel" transform="translate(260.782,141.543)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Gonocaryum</text></g><g class="toytree-TipLabel" transform="translate(245.667,134.514)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Citronella</text></g><g class="toytree-TipLabel" transform="translate(307.897,127.486)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Irvingbaileya</text></g><g class="toytree-TipLabel" transform="translate(311.301,120.457)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Gomphandra</text></g><g class="toytree-TipLabel" transform="translate(313.133,113.429)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Grisollea</text></g><g class="toytree-TipLabel" transform="translate(274.939,106.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Helwingia</text></g><g class="toytree-TipLabel" transform="translate(308.741,99.3714)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Phyllonoma</text></g><g class="toytree-TipLabel" transform="translate(257.309,92.3429)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Ilex</text></g><g class="toytree-TipLabel" transform="translate(300.337,85.3143)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Atropa</text></g><g class="toytree-TipLabel" transform="translate(298.095,78.2857)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Nicotiana</text></g><g class="toytree-TipLabel" transform="translate(331.68,71.2571)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Coffea</text></g><g class="toytree-TipLabel" transform="translate(337.394,64.2286)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Jasminum</text></g><g class="toytree-TipLabel" transform="translate(175.799,57.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Spinacia</text></g></g></g></g></g><g class="toyplot-coordinates-Cartesian" id="tb4d25e80adc84adc8c7b9fc091ecc91e"><clipPath id="tbebc37aae76f4897b61b647e3752cf03"><rect x="35.0" y="35.0" width="571.768" height="930.0"></rect></clipPath><g clip-path="url(#tbebc37aae76f4897b61b647e3752cf03)"></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python


```


```python
# toytree.otol.node_info(SUBTREE_GEN_LIST)

```


```python
toytree.otol.supporting_studies()

```


    ---------------------------------------------------------------------------

    ToytreeError                              Traceback (most recent call last)

    Cell In[24], line 1
    ----> 1 toytree.otol.supporting_studies(SUBTREE_SPP_LIST)


    File ~/Documents/tools/toytree/toytree/otol/src/otol.py:1038, in supporting_studies(query)
       1036 def supporting_studies(query: FLEX_QUERY) -> list[str]:
       1037     """Return study IDs that support subtree relationships."""
    -> 1038     return _get_default_client().get_supporting_studies(query=query)


    File ~/Documents/tools/toytree/toytree/otol/src/otol.py:796, in _OTOLClient.get_supporting_studies(self, query)
        794     data = self.get_synthetic_subtree(query, full_json=True)
        795 else:
    --> 796     data = self.get_synthetic_induced_subtree(query, full_json=True)
        797 return list(data.get("supporting_studies", []))


    File ~/Documents/tools/toytree/toytree/otol/src/otol.py:709, in _OTOLClient.get_synthetic_induced_subtree(self, query, full_json, label_format, insert_broken_nodes)
        701 def get_synthetic_induced_subtree(
        702     self,
        703     query: Sequence[int | str],
       (...)
        706     insert_broken_nodes: bool = False,
        707 ) -> str | dict[str, Any]:
        708     """Return induced subtree for a mixed query list."""
    --> 709     node_ids = self._query_to_node_ids(query)
        710     ott_ids: list[int] = []
        711     for node_id in node_ids:


    File ~/Documents/tools/toytree/toytree/otol/src/otol.py:413, in _OTOLClient._query_to_node_ids(self, query)
        410     names.append(text)
        412 if names:
    --> 413     table = self.resolve_names(names, on_unresolved="raise")
        414     for idx, ott_id in zip(name_positions, table["ott_id"].tolist()):
        415         out[idx] = f"ott{int(ott_id)}"


    File ~/Documents/tools/toytree/toytree/otol/src/otol.py:388, in _OTOLClient.resolve_names(self, query, do_approximate_matching, context, include_synonyms, on_unresolved, on_ambiguous)
        386     message = f"TNRS resolution has unresolved rows: {amb} ambiguous, {unm} unmatched."
        387     if on_unresolved == "raise":
    --> 388         raise ToytreeError(message)
        389     warnings.warn(message, stacklevel=2)
        390 return table


    ToytreeError: TNRS resolution has unresolved rows: 1 ambiguous, 1 unmatched.



```python
toytree.otol.study_id_from_doi("10.1002/ajb2.1019")

```


```python
toytree.otol.study_tree("10.1002/ajb2.1019")

```


    ---------------------------------------------------------------------------

    HTTPError                                 Traceback (most recent call last)

    File ~/Documents/tools/toytree/toytree/otol/src/otol.py:211, in _OTOLClient._request_text(self, url, use_cache, cache_namespace)
        210 response = self.session.get(url=url, timeout=self.timeout)
    --> 211 response.raise_for_status()
        212 text = response.text


    File ~/miniconda3/envs/toytree-dev/lib/python3.12/site-packages/requests/models.py:1024, in Response.raise_for_status(self)
       1023 if http_error_msg:
    -> 1024     raise HTTPError(http_error_msg, response=self)


    HTTPError: 404 Client Error: Not Found for url: https://api.opentreeoflife.org/v3/study/10.1002/ajb2.1019.tre/?tip_label=ot:originallabel

    
    The above exception was the direct cause of the following exception:


    ToytreeError                              Traceback (most recent call last)

    Cell In[22], line 1
    ----> 1 toytree.otol.study_tree("10.1002/ajb2.1019")


    File ~/Documents/tools/toytree/toytree/otol/src/otol.py:1047, in study_tree(study_id, tree_id, label_format)
       1041 def study_tree(
       1042     study_id: str | int,
       1043     tree_id: str | int | None = None,
       1044     label_format: str | None = None,
       1045 ) -> str:
       1046     """Return Newick/Nexus text for an OTOL study or one tree in that study."""
    -> 1047     return _get_default_client().get_study_or_tree(
       1048         study_id=study_id,
       1049         tree_id=tree_id,
       1050         label_format=label_format,
       1051     )


    File ~/Documents/tools/toytree/toytree/otol/src/otol.py:822, in _OTOLClient.get_study_or_tree(self, study_id, tree_id, label_format)
        819 else:
        820     url = urljoin(self.base_url, f"study/{study_id}{suffix}/{label}")
    --> 822 text = self._request_text(url)
        823 if text.startswith("'") and text.endswith("'"):
        824     return text[1:-1]


    File ~/Documents/tools/toytree/toytree/otol/src/otol.py:217, in _OTOLClient._request_text(self, url, use_cache, cache_namespace)
        215     return text
        216 except Exception as exc:
    --> 217     raise self._error_from_response(url, exc, response) from exc


    ToytreeError: OTOL request failed at endpoint 'https://api.opentreeoflife.org/v3/study/10.1002/ajb2.1019.tre/?tip_label=ot:originallabel'. status=404. error=404 Client Error: Not Found for url: https://api.opentreeoflife.org/v3/study/10.1002/ajb2.1019.tre/?tip_label=ot:originallabel. response_snippet='{"message": "Nothing found at this URL"}'



```python
toytree.otol.synthetic_subtree(TAXON_LIST, full_json=True)

```


    ---------------------------------------------------------------------------

    ToytreeError                              Traceback (most recent call last)

    Cell In[21], line 1
    ----> 1 toytree.otol.synthetic_subtree(TAXON_LIST, full_json=True)


    File ~/Documents/tools/toytree/toytree/otol/src/otol.py:1006, in synthetic_subtree(query, full_json, extra_params)
       1000 def synthetic_subtree(
       1001     query: int | str,
       1002     full_json: bool = False,
       1003     extra_params: dict[str, Any] | None = None,
       1004 ) -> str | dict[str, Any]:
       1005     """Return synthetic subtree below one OTOL node/taxon query."""
    -> 1006     return _get_default_client().get_synthetic_subtree(
       1007         query=query,
       1008         full_json=full_json,
       1009         **({} if extra_params is None else extra_params),
       1010     )


    File ~/Documents/tools/toytree/toytree/otol/src/otol.py:647, in _OTOLClient.get_synthetic_subtree(self, query, full_json, **kwargs)
        640 def get_synthetic_subtree(
        641     self,
        642     query: int | str,
        643     full_json: bool = False,
        644     **kwargs: Any,
        645 ) -> str | dict[str, Any]:
        646     """Return Newick subtree below one OTOL node."""
    --> 647     node_id = self._query_to_node_ids(query)[0]
        648     info = self.get_node_info(node_id)[0]
        649     if int(info.get("num_tips", 0)) >= 25_000:


    File ~/Documents/tools/toytree/toytree/otol/src/otol.py:413, in _OTOLClient._query_to_node_ids(self, query)
        410     names.append(text)
        412 if names:
    --> 413     table = self.resolve_names(names, on_unresolved="raise")
        414     for idx, ott_id in zip(name_positions, table["ott_id"].tolist()):
        415         out[idx] = f"ott{int(ott_id)}"


    File ~/Documents/tools/toytree/toytree/otol/src/otol.py:388, in _OTOLClient.resolve_names(self, query, do_approximate_matching, context, include_synonyms, on_unresolved, on_ambiguous)
        386     message = f"TNRS resolution has unresolved rows: {amb} ambiguous, {unm} unmatched."
        387     if on_unresolved == "raise":
    --> 388         raise ToytreeError(message)
        389     warnings.warn(message, stacklevel=2)
        390 return table


    ToytreeError: TNRS resolution has unresolved rows: 1 ambiguous, 0 unmatched.



```python
toytree.otol.mrca_taxon_id(TAXON_LIST[:2])

```




    5263556




```python
toytree.otol.taxon_info(5263556)

```




    {'flags': [],
     'is_suppressed': False,
     'is_suppressed_from_synth': False,
     'name': 'Core_Lamiales',
     'ott_id': 5263556,
     'rank': 'no rank',
     'source': 'ott3.7draft3',
     'synonyms': [],
     'tax_sources': ['study713:13'],
     'unique_name': 'Core_Lamiales'}




```python
toytree.otol.resolve_names(TAXON_LIST, context="Angiosperms", on_ambiguous="first")

```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>query</th>
      <th>status</th>
      <th>matched_name</th>
      <th>ott_id</th>
      <th>is_synonym</th>
      <th>reason</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Castilleja</td>
      <td>matched</td>
      <td>Castilleja</td>
      <td>317400</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Castilleja campestris</td>
      <td>matched</td>
      <td>Castilleja campestris</td>
      <td>83184</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Orobanche cumana</td>
      <td>matched</td>
      <td>Orobanche cumana</td>
      <td>1010133</td>
      <td>True</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Pedicularis anas</td>
      <td>matched</td>
      <td>Pedicularis anas</td>
      <td>1032908</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Pedicularis groenlandica</td>
      <td>matched</td>
      <td>Pedicularis groenlandica</td>
      <td>261492</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Mimulus guttatus</td>
      <td>matched</td>
      <td>Mimulus guttatus</td>
      <td>504496</td>
      <td>True</td>
      <td>resolved_first_of_2</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Aquilegia coerulea</td>
      <td>matched</td>
      <td>Aquilegia coerulea</td>
      <td>192307</td>
      <td>False</td>
      <td>ok</td>
    </tr>
  </tbody>
</table>
</div>




```python
toytree.otol.get_taxon_id_table(TAXON_LIST)

```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>query</th>
      <th>status</th>
      <th>matched_name</th>
      <th>ott_id</th>
      <th>is_synonym</th>
      <th>reason</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Castilleja</td>
      <td>matched</td>
      <td>Castilleja</td>
      <td>317400</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Castilleja campestris</td>
      <td>matched</td>
      <td>Castilleja campestris</td>
      <td>83184</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Orobanche cumana</td>
      <td>unmatched</td>
      <td>None</td>
      <td>&lt;NA&gt;</td>
      <td>None</td>
      <td>no_match</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Pedicularis anas</td>
      <td>matched</td>
      <td>Pedicularis anas</td>
      <td>1032908</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Pedicularis groenlandica</td>
      <td>matched</td>
      <td>Pedicularis groenlandica</td>
      <td>261492</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Mimulus guttatus</td>
      <td>unmatched</td>
      <td>None</td>
      <td>&lt;NA&gt;</td>
      <td>None</td>
      <td>no_match</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Aquilegia coerulea</td>
      <td>matched</td>
      <td>Aquilegia coerulea</td>
      <td>192307</td>
      <td>False</td>
      <td>ok</td>
    </tr>
  </tbody>
</table>
</div>




```python
toytree.otol.resolve_names(TAXON_LIST, include_synonyms=True)

```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>query</th>
      <th>status</th>
      <th>matched_name</th>
      <th>ott_id</th>
      <th>is_synonym</th>
      <th>reason</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Castilleja</td>
      <td>matched</td>
      <td>Castilleja</td>
      <td>317400.0</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Castilleja campestris</td>
      <td>matched</td>
      <td>Castilleja campestris</td>
      <td>83184.0</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Orobanche cumana</td>
      <td>matched</td>
      <td>Orobanche cumana</td>
      <td>1010133.0</td>
      <td>True</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Pedicularis anas</td>
      <td>matched</td>
      <td>Pedicularis anas</td>
      <td>1032908.0</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Pedicularis groenlandica</td>
      <td>matched</td>
      <td>Pedicularis groenlandica</td>
      <td>261492.0</td>
      <td>False</td>
      <td>ok</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Mimulus guttatus</td>
      <td>ambiguous</td>
      <td>None</td>
      <td>NaN</td>
      <td>None</td>
      <td>2_matches</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Aquilegia coerulea</td>
      <td>matched</td>
      <td>Aquilegia coerulea</td>
      <td>192307.0</td>
      <td>False</td>
      <td>ok</td>
    </tr>
  </tbody>
</table>
</div>




```python
matched = toytree.otol.get_matched_names("Mimulus guttatus")
results = matched['results']
print(matched.keys())

```

    dict_keys(['context', 'governing_code', 'includes_approximate_matches', 'includes_deprecated_taxa', 'includes_suppressed_names', 'matched_names', 'results', 'taxonomy', 'unambiguous_names', 'unmatched_names'])



```python
print(results[0].keys())

```

    dict_keys(['matches', 'name'])

matched['results'][0]['matches']

```python
for i in results:
    print(i['name'], i['matches'])

```

    Mimulus guttatus [{'is_approximate_match': False, 'is_synonym': True, 'matched_name': 'Mimulus guttatus', 'nomenclature_code': 'ICN', 'score': 1.0, 'search_string': 'mimulus guttatus', 'taxon': {'flags': [], 'is_suppressed': False, 'is_suppressed_from_synth': False, 'name': 'Erythranthe guttata', 'ott_id': 504496, 'rank': 'species', 'source': 'ott3.7draft3', 'synonyms': ['Mimulus clementinus', 'Mimulus equinus', 'Mimulus glabratus adscendens', 'Mimulus glabratus ascendens', 'Mimulus grandiflorus', 'Mimulus guttatus', 'Mimulus guttatus guttatus', 'Mimulus guttatus haidensis', 'Mimulus guttatus laxus', 'Mimulus guttatus lyratus', 'Mimulus guttatus puberulus', 'Mimulus guttatus subsp. guttatus', 'Mimulus hirsutus', 'Mimulus langsdorffii', 'Mimulus langsdorffii argutus', 'Mimulus langsdorffii guttatus', 'Mimulus langsdorffii minima', 'Mimulus langsdorffii platyphyllus', 'Mimulus laxus', 'Mimulus lyratus', 'Mimulus microphyllis', 'Mimulus paniculatus', 'Mimulus petiolaris', 'Mimulus prionophyllus', 'Mimulus puberulus', 'Mimulus rivularis'], 'tax_sources': ['ncbi:4155', 'gbif:7346102', 'irmng:10208223'], 'unique_name': 'Erythranthe guttata'}}, {'is_approximate_match': False, 'is_synonym': True, 'matched_name': 'Mimulus guttatus', 'nomenclature_code': 'ICN', 'score': 1.0, 'search_string': 'mimulus guttatus', 'taxon': {'flags': [], 'is_suppressed': False, 'is_suppressed_from_synth': False, 'name': 'Erythranthe lutea', 'ott_id': 662909, 'rank': 'species', 'source': 'ott3.7draft3', 'synonyms': ['Erythranthe lutea rivularis', 'Mimulus cupreus', 'Mimulus glabratus micranthus', 'Mimulus guttatus', 'Mimulus luteus', 'Mimulus luteus alpinus', 'Mimulus luteus cupreus', 'Mimulus luteus rivularis', 'Mimulus luteus youngeanus', 'Mimulus ocellatus', 'Mimulus perluteus', 'Mimulus punctatus'], 'tax_sources': ['ncbi:270988', 'gbif:7730307'], 'unique_name': 'Erythranthe lutea'}}]



```python
i.keys()

```




    dict_keys(['matches', 'name'])




```python
toytree.otol.resolve_names(["Mimulus guttatus"])

```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>query</th>
      <th>status</th>
      <th>matched_name</th>
      <th>ott_id</th>
      <th>is_synonym</th>
      <th>reason</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Mimulus guttatus</td>
      <td>ambiguous</td>
      <td>None</td>
      <td>None</td>
      <td>None</td>
      <td>2_matches</td>
    </tr>
  </tbody>
</table>
</div>




```python
DOI_Smith = "10.1002/ajb2.1019"
DOI_Zuntini = "..."

```


```python
res = toytree.infer.phylomaker_subtree(TAXON_LIST, strict="warn")

```

    WARNING: ambiguous/unmatched taxa present; using matched rows only.



```python
res.report

```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>query</th>
      <th>status</th>
      <th>matched_name</th>
      <th>ott_id</th>
      <th>is_synonym</th>
      <th>reason</th>
      <th>query_normalized</th>
      <th>source_context</th>
      <th>used_in_tree</th>
      <th>final_tip_label</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Aquilegia coerulea</td>
      <td>matched</td>
      <td>Aquilegia coerulea</td>
      <td>192307.0</td>
      <td>False</td>
      <td>ok</td>
      <td>Aquilegia coerulea</td>
      <td>None</td>
      <td>True</td>
      <td>Aquilegia_coerulea_ott192307</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Castilleja</td>
      <td>matched</td>
      <td>Castilleja</td>
      <td>317400.0</td>
      <td>False</td>
      <td>ok</td>
      <td>Castilleja</td>
      <td>None</td>
      <td>False</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Castilleja campestris</td>
      <td>matched</td>
      <td>Castilleja campestris</td>
      <td>83184.0</td>
      <td>False</td>
      <td>ok</td>
      <td>Castilleja campestris</td>
      <td>None</td>
      <td>True</td>
      <td>Castilleja_campestris_ott83184</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Mimulus guttatus</td>
      <td>ambiguous</td>
      <td>None</td>
      <td>NaN</td>
      <td>None</td>
      <td>2_matches</td>
      <td>Mimulus guttatus</td>
      <td>None</td>
      <td>False</td>
      <td>None</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Orobanche</td>
      <td>matched</td>
      <td>Orobanche</td>
      <td>918756.0</td>
      <td>False</td>
      <td>ok</td>
      <td>Orobanche</td>
      <td>None</td>
      <td>False</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>5</th>
      <td>Pedicularis anas</td>
      <td>matched</td>
      <td>Pedicularis anas</td>
      <td>1032908.0</td>
      <td>False</td>
      <td>ok</td>
      <td>Pedicularis anas</td>
      <td>None</td>
      <td>True</td>
      <td>Pedicularis_anas_ott1032908</td>
    </tr>
    <tr>
      <th>6</th>
      <td>Pedicularis groenlandica</td>
      <td>matched</td>
      <td>Pedicularis groenlandica</td>
      <td>261492.0</td>
      <td>False</td>
      <td>ok</td>
      <td>Pedicularis groenlandica</td>
      <td>None</td>
      <td>True</td>
      <td>Pedicularis_groenlandica_ott261492</td>
    </tr>
  </tbody>
</table>
</div>




```python
res.tree.draw();

```


<div class="toyplot" id="tfebae9da0f1044768a5429699cedd5fd" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="619.2px" height="275.0px" viewBox="0 0 619.2 275.0" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="td76fcee2d6964d83bcb9567064bfd9bd"><g class="toyplot-coordinates-Cartesian" id="t0982de7c488946a0aa944b42ceec8648"><clipPath id="t6c47db388d5642b58b97db33d527bf3a"><rect x="35.0" y="35.0" width="549.2" height="205.0"></rect></clipPath><g clip-path="url(#t6c47db388d5642b58b97db33d527bf3a)"><g class="toytree-mark-Toytree" id="t6a55e9e3e16b4ce19b7052977b2f8953"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 176.5 217.8 L 176.5 217.8 L 179.7 217.8" id="3,0" style=""></path><path d="M 131.4 177.7 L 131.4 137.5 L 134.7 137.5" id="17,1" style=""></path><path d="M 125.0 57.2 L 125.0 57.2 L 128.2 57.2" id="42,2" style=""></path><path d="M 173.3 217.8 L 173.3 217.8 L 176.5 217.8" id="4,3" style=""></path><path d="M 170.1 217.8 L 170.1 217.8 L 173.3 217.8" id="5,4" style=""></path><path d="M 166.9 217.8 L 166.9 217.8 L 170.1 217.8" id="6,5" style=""></path><path d="M 163.6 217.8 L 163.6 217.8 L 166.9 217.8" id="7,6" style=""></path><path d="M 160.4 217.8 L 160.4 217.8 L 163.6 217.8" id="8,7" style=""></path><path d="M 157.2 217.8 L 157.2 217.8 L 160.4 217.8" id="9,8" style=""></path><path d="M 154.0 217.8 L 154.0 217.8 L 157.2 217.8" id="10,9" style=""></path><path d="M 150.8 217.8 L 150.8 217.8 L 154.0 217.8" id="11,10" style=""></path><path d="M 147.5 217.8 L 147.5 217.8 L 150.8 217.8" id="12,11" style=""></path><path d="M 144.3 217.8 L 144.3 217.8 L 147.5 217.8" id="13,12" style=""></path><path d="M 141.1 217.8 L 141.1 217.8 L 144.3 217.8" id="14,13" style=""></path><path d="M 137.9 217.8 L 137.9 217.8 L 141.1 217.8" id="15,14" style=""></path><path d="M 134.7 217.8 L 134.7 217.8 L 137.9 217.8" id="16,15" style=""></path><path d="M 131.4 177.7 L 131.4 217.8 L 134.7 217.8" id="17,16" style=""></path><path d="M 128.2 177.7 L 128.2 177.7 L 131.4 177.7" id="18,17" style=""></path><path d="M 125.0 177.7 L 125.0 177.7 L 128.2 177.7" id="19,18" style=""></path><path d="M 121.8 177.7 L 121.8 177.7 L 125.0 177.7" id="20,19" style=""></path><path d="M 118.6 177.7 L 118.6 177.7 L 121.8 177.7" id="21,20" style=""></path><path d="M 115.3 177.7 L 115.3 177.7 L 118.6 177.7" id="22,21" style=""></path><path d="M 112.1 177.7 L 112.1 177.7 L 115.3 177.7" id="23,22" style=""></path><path d="M 108.9 177.7 L 108.9 177.7 L 112.1 177.7" id="24,23" style=""></path><path d="M 105.7 177.7 L 105.7 177.7 L 108.9 177.7" id="25,24" style=""></path><path d="M 102.5 177.7 L 102.5 177.7 L 105.7 177.7" id="26,25" style=""></path><path d="M 99.2 177.7 L 99.2 177.7 L 102.5 177.7" id="27,26" style=""></path><path d="M 96.0 177.7 L 96.0 177.7 L 99.2 177.7" id="28,27" style=""></path><path d="M 92.8 177.7 L 92.8 177.7 L 96.0 177.7" id="29,28" style=""></path><path d="M 89.6 177.7 L 89.6 177.7 L 92.8 177.7" id="30,29" style=""></path><path d="M 86.4 177.7 L 86.4 177.7 L 89.6 177.7" id="31,30" style=""></path><path d="M 83.1 177.7 L 83.1 177.7 L 86.4 177.7" id="32,31" style=""></path><path d="M 79.9 177.7 L 79.9 177.7 L 83.1 177.7" id="33,32" style=""></path><path d="M 76.7 177.7 L 76.7 177.7 L 79.9 177.7" id="34,33" style=""></path><path d="M 73.5 177.7 L 73.5 177.7 L 76.7 177.7" id="35,34" style=""></path><path d="M 70.3 177.7 L 70.3 177.7 L 73.5 177.7" id="36,35" style=""></path><path d="M 67.0 177.7 L 67.0 177.7 L 70.3 177.7" id="37,36" style=""></path><path d="M 63.8 177.7 L 63.8 177.7 L 67.0 177.7" id="38,37" style=""></path><path d="M 60.6 177.7 L 60.6 177.7 L 63.8 177.7" id="39,38" style=""></path><path d="M 57.4 177.7 L 57.4 177.7 L 60.6 177.7" id="40,39" style=""></path><path d="M 54.2 177.7 L 54.2 177.7 L 57.4 177.7" id="41,40" style=""></path><path d="M 50.9 117.4 L 50.9 177.7 L 54.2 177.7" id="65,41" style=""></path><path d="M 121.8 57.2 L 121.8 57.2 L 125.0 57.2" id="43,42" style=""></path><path d="M 118.6 57.2 L 118.6 57.2 L 121.8 57.2" id="44,43" style=""></path><path d="M 115.3 57.2 L 115.3 57.2 L 118.6 57.2" id="45,44" style=""></path><path d="M 112.1 57.2 L 112.1 57.2 L 115.3 57.2" id="46,45" style=""></path><path d="M 108.9 57.2 L 108.9 57.2 L 112.1 57.2" id="47,46" style=""></path><path d="M 105.7 57.2 L 105.7 57.2 L 108.9 57.2" id="48,47" style=""></path><path d="M 102.5 57.2 L 102.5 57.2 L 105.7 57.2" id="49,48" style=""></path><path d="M 99.2 57.2 L 99.2 57.2 L 102.5 57.2" id="50,49" style=""></path><path d="M 96.0 57.2 L 96.0 57.2 L 99.2 57.2" id="51,50" style=""></path><path d="M 92.8 57.2 L 92.8 57.2 L 96.0 57.2" id="52,51" style=""></path><path d="M 89.6 57.2 L 89.6 57.2 L 92.8 57.2" id="53,52" style=""></path><path d="M 86.4 57.2 L 86.4 57.2 L 89.6 57.2" id="54,53" style=""></path><path d="M 83.1 57.2 L 83.1 57.2 L 86.4 57.2" id="55,54" style=""></path><path d="M 79.9 57.2 L 79.9 57.2 L 83.1 57.2" id="56,55" style=""></path><path d="M 76.7 57.2 L 76.7 57.2 L 79.9 57.2" id="57,56" style=""></path><path d="M 73.5 57.2 L 73.5 57.2 L 76.7 57.2" id="58,57" style=""></path><path d="M 70.3 57.2 L 70.3 57.2 L 73.5 57.2" id="59,58" style=""></path><path d="M 67.0 57.2 L 67.0 57.2 L 70.3 57.2" id="60,59" style=""></path><path d="M 63.8 57.2 L 63.8 57.2 L 67.0 57.2" id="61,60" style=""></path><path d="M 60.6 57.2 L 60.6 57.2 L 63.8 57.2" id="62,61" style=""></path><path d="M 57.4 57.2 L 57.4 57.2 L 60.6 57.2" id="63,62" style=""></path><path d="M 54.2 57.2 L 54.2 57.2 L 57.4 57.2" id="64,63" style=""></path><path d="M 50.9 117.4 L 50.9 57.2 L 54.2 57.2" id="65,64" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(179.742,217.8)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_groenlandica_ott261492</text></g><g class="toytree-TipLabel" transform="translate(134.658,137.5)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Pedicularis_anas_ott1032908</text></g><g class="toytree-TipLabel" transform="translate(128.218,57.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">Aquilegia_coerulea_ott192307</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>


## Find studies 
One of the core utilities of the Open Tree of Life is to store trees from published studies. These trees are the primary data from which the synthetic tree is constructed, and often contain additional data, such as branch lengths, that are not available in the synthetic tree. You can search for trees associated with a study by its DOI, or you can find the set of studies that are informative about a set of taxa by searching taxon names or IDs. 

### Find studies by DOI


```python
# ...
columns = ["ot:studyId", "o

```

{"matched_studies": [{"ot:studyId": "ot_1974", "ot:studyPublicationReference": "Smith, S. A., & Brown, J. W. (2018). Constructing a broadly inclusive seed plant phylogeny. American Journal of Botany, 105(3), 302\u2013314. doi:10.1002/ajb2.1019\n", "ot:curatorName": ["Brian O&#x27;Meara"], "ot:studyYear": 2018, "ot:focalCladeOTTTaxonName": "", "ot:dataDeposit": "", "ot:studyPublication": "http://dx.doi.org/10.1002/ajb2.1019", "ot:tag": []}]}

### Find studies informative about a set of taxa


```python
tree = toytree.rtree.unittree(20)
tree[0].name = "XXXXXXXXXXXXXXXXXXXXXX"

```


```python
tree.draw(layout='d');

```


<div class="toyplot" id="tfc080901807a4229abe099565eacf734" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="431.2px" height="583.1759999999999px" viewBox="0 0 431.2 583.1759999999999" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tab0ed55158e3449088878bde3dab0e28"><g class="toyplot-coordinates-Cartesian" id="tfc2db9170a354bc19bfaec4433a8e9b1"><clipPath id="t66a00a6f489a422ca059a0bd347de5dd"><rect x="35.0" y="35.0" width="361.2" height="513.1759999999999"></rect></clipPath><g clip-path="url(#t66a00a6f489a422ca059a0bd347de5dd)"><g class="toytree-mark-Toytree" id="tcccc4754f6d24dafab84176b9d6dbd26"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 65.5 75.9 L 57.2 75.9 L 57.2 175.5" id="20,0" style=""></path><path d="M 65.5 75.9 L 73.9 75.9 L 73.9 175.5" id="20,1" style=""></path><path d="M 78.0 59.2 L 90.5 59.2 L 90.5 175.5" id="21,2" style=""></path><path d="M 119.7 75.9 L 107.2 75.9 L 107.2 175.5" id="23,3" style=""></path><path d="M 132.2 92.5 L 123.9 92.5 L 123.9 175.5" id="22,4" style=""></path><path d="M 132.2 92.5 L 140.6 92.5 L 140.6 175.5" id="22,5" style=""></path><path d="M 165.6 109.1 L 157.2 109.1 L 157.2 175.5" id="24,6" style=""></path><path d="M 165.6 109.1 L 173.9 109.1 L 173.9 175.5" id="24,7" style=""></path><path d="M 198.9 109.1 L 190.6 109.1 L 190.6 175.5" id="25,8" style=""></path><path d="M 198.9 109.1 L 207.3 109.1 L 207.3 175.5" id="25,9" style=""></path><path d="M 232.3 158.9 L 223.9 158.9 L 223.9 175.5" id="27,10" style=""></path><path d="M 232.3 158.9 L 240.6 158.9 L 240.6 175.5" id="27,11" style=""></path><path d="M 244.8 142.3 L 257.3 142.3 L 257.3 175.5" id="28,12" style=""></path><path d="M 286.5 142.3 L 274.0 142.3 L 274.0 175.5" id="30,13" style=""></path><path d="M 299.0 158.9 L 290.6 158.9 L 290.6 175.5" id="29,14" style=""></path><path d="M 299.0 158.9 L 307.3 158.9 L 307.3 175.5" id="29,15" style=""></path><path d="M 332.3 125.7 L 324.0 125.7 L 324.0 175.5" id="32,16" style=""></path><path d="M 332.3 125.7 L 340.7 125.7 L 340.7 175.5" id="32,17" style=""></path><path d="M 365.7 109.1 L 357.3 109.1 L 357.3 175.5" id="34,18" style=""></path><path d="M 365.7 109.1 L 374.0 109.1 L 374.0 175.5" id="34,19" style=""></path><path d="M 78.0 59.2 L 65.5 59.2 L 65.5 75.9" id="21,20" style=""></path><path d="M 133.3 50.9 L 78.0 50.9 L 78.0 59.2" id="38,21" style=""></path><path d="M 119.7 75.9 L 132.2 75.9 L 132.2 92.5" id="23,22" style=""></path><path d="M 188.5 59.2 L 119.7 59.2 L 119.7 75.9" id="37,23" style=""></path><path d="M 182.3 92.5 L 165.6 92.5 L 165.6 109.1" id="26,24" style=""></path><path d="M 182.3 92.5 L 198.9 92.5 L 198.9 109.1" id="26,25" style=""></path><path d="M 257.3 75.9 L 182.3 75.9 L 182.3 92.5" id="36,26" style=""></path><path d="M 244.8 142.3 L 232.3 142.3 L 232.3 158.9" id="28,27" style=""></path><path d="M 265.6 125.7 L 244.8 125.7 L 244.8 142.3" id="31,28" style=""></path><path d="M 286.5 142.3 L 299.0 142.3 L 299.0 158.9" id="30,29" style=""></path><path d="M 265.6 125.7 L 286.5 125.7 L 286.5 142.3" id="31,30" style=""></path><path d="M 299.0 109.1 L 265.6 109.1 L 265.6 125.7" id="33,31" style=""></path><path d="M 299.0 109.1 L 332.3 109.1 L 332.3 125.7" id="33,32" style=""></path><path d="M 332.3 92.5 L 299.0 92.5 L 299.0 109.1" id="35,33" style=""></path><path d="M 332.3 92.5 L 365.7 92.5 L 365.7 109.1" id="35,34" style=""></path><path d="M 257.3 75.9 L 332.3 75.9 L 332.3 92.5" id="36,35" style=""></path><path d="M 188.5 59.2 L 257.3 59.2 L 257.3 75.9" id="37,36" style=""></path><path d="M 133.3 50.9 L 188.5 50.9 L 188.5 59.2" id="38,37" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(57.2,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">XXXXXXXXXXXXXXXXXXXXXX</text></g><g class="toytree-TipLabel" transform="translate(73.8737,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(90.5474,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(107.221,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(123.895,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(140.568,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(157.242,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(173.916,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(190.589,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(207.263,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g><g class="toytree-TipLabel" transform="translate(223.937,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r10</text></g><g class="toytree-TipLabel" transform="translate(240.611,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r11</text></g><g class="toytree-TipLabel" transform="translate(257.284,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r12</text></g><g class="toytree-TipLabel" transform="translate(273.958,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r13</text></g><g class="toytree-TipLabel" transform="translate(290.632,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r14</text></g><g class="toytree-TipLabel" transform="translate(307.305,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r15</text></g><g class="toytree-TipLabel" transform="translate(323.979,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r16</text></g><g class="toytree-TipLabel" transform="translate(340.653,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r17</text></g><g class="toytree-TipLabel" transform="translate(357.326,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r18</text></g><g class="toytree-TipLabel" transform="translate(374,175.51)rotate(90)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r19</text></g></g></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
})();</script></div></div>



```python
import toyplot

c = toyplot.Canvas()
a = c.cartesian()
_, _, m = tree.draw(axes=a, )

```


<div class="toyplot" id="t9a35b03f7c034892b4e7556dcc211b0f" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="600px" height="600px" viewBox="0 0 600 600" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="tc562328ff6de45f990a7a3c26662dcf0"><g class="toyplot-coordinates-Cartesian" id="ta6c02f9361f5447fad11ab6936a1a8d1"><clipPath id="td675fc72903a4a0da985aa394cc627d5"><rect x="40.0" y="40.0" width="520.0" height="520.0"></rect></clipPath><g clip-path="url(#td675fc72903a4a0da985aa394cc627d5)"><g class="toytree-mark-Toytree" id="tf4f639509bd045a299360672ebfc171b"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 75.8 530.5 L 75.8 542.8 L 175.7 542.8" id="20,0" style=""></path><path d="M 75.8 530.5 L 75.8 518.2 L 175.7 518.2" id="20,1" style=""></path><path d="M 59.2 512.0 L 59.2 493.5 L 175.7 493.5" id="21,2" style=""></path><path d="M 75.8 450.4 L 75.8 468.9 L 175.7 468.9" id="23,3" style=""></path><path d="M 92.5 431.9 L 92.5 444.2 L 175.7 444.2" id="22,4" style=""></path><path d="M 92.5 431.9 L 92.5 419.6 L 175.7 419.6" id="22,5" style=""></path><path d="M 109.1 382.6 L 109.1 395.0 L 175.7 395.0" id="24,6" style=""></path><path d="M 109.1 382.6 L 109.1 370.3 L 175.7 370.3" id="24,7" style=""></path><path d="M 109.1 333.4 L 109.1 345.7 L 175.7 345.7" id="25,8" style=""></path><path d="M 109.1 333.4 L 109.1 321.0 L 175.7 321.0" id="25,9" style=""></path><path d="M 159.0 284.1 L 159.0 296.4 L 175.7 296.4" id="27,10" style=""></path><path d="M 159.0 284.1 L 159.0 271.8 L 175.7 271.8" id="27,11" style=""></path><path d="M 142.4 265.6 L 142.4 247.1 L 175.7 247.1" id="28,12" style=""></path><path d="M 142.4 204.0 L 142.4 222.5 L 175.7 222.5" id="30,13" style=""></path><path d="M 159.0 185.5 L 159.0 197.8 L 175.7 197.8" id="29,14" style=""></path><path d="M 159.0 185.5 L 159.0 173.2 L 175.7 173.2" id="29,15" style=""></path><path d="M 125.7 136.2 L 125.7 148.6 L 175.7 148.6" id="32,16" style=""></path><path d="M 125.7 136.2 L 125.7 123.9 L 175.7 123.9" id="32,17" style=""></path><path d="M 109.1 87.0 L 109.1 99.3 L 175.7 99.3" id="34,18" style=""></path><path d="M 109.1 87.0 L 109.1 74.6 L 175.7 74.6" id="34,19" style=""></path><path d="M 59.2 512.0 L 59.2 530.5 L 75.8 530.5" id="21,20" style=""></path><path d="M 50.9 430.4 L 50.9 512.0 L 59.2 512.0" id="38,21" style=""></path><path d="M 75.8 450.4 L 75.8 431.9 L 92.5 431.9" id="23,22" style=""></path><path d="M 59.2 348.8 L 59.2 450.4 L 75.8 450.4" id="37,23" style=""></path><path d="M 92.5 358.0 L 92.5 382.6 L 109.1 382.6" id="26,24" style=""></path><path d="M 92.5 358.0 L 92.5 333.4 L 109.1 333.4" id="26,25" style=""></path><path d="M 75.8 247.1 L 75.8 358.0 L 92.5 358.0" id="36,26" style=""></path><path d="M 142.4 265.6 L 142.4 284.1 L 159.0 284.1" id="28,27" style=""></path><path d="M 125.7 234.8 L 125.7 265.6 L 142.4 265.6" id="31,28" style=""></path><path d="M 142.4 204.0 L 142.4 185.5 L 159.0 185.5" id="30,29" style=""></path><path d="M 125.7 234.8 L 125.7 204.0 L 142.4 204.0" id="31,30" style=""></path><path d="M 109.1 185.5 L 109.1 234.8 L 125.7 234.8" id="33,31" style=""></path><path d="M 109.1 185.5 L 109.1 136.2 L 125.7 136.2" id="33,32" style=""></path><path d="M 92.5 136.2 L 92.5 185.5 L 109.1 185.5" id="35,33" style=""></path><path d="M 92.5 136.2 L 92.5 87.0 L 109.1 87.0" id="35,34" style=""></path><path d="M 75.8 247.1 L 75.8 136.2 L 92.5 136.2" id="36,35" style=""></path><path d="M 59.2 348.8 L 59.2 247.1 L 75.8 247.1" id="37,36" style=""></path><path d="M 50.9 430.4 L 50.9 348.8 L 59.2 348.8" id="38,37" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(175.661,542.8)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">XXXXXXXXXXXXXXXXXXXXXX</text></g><g class="toytree-TipLabel" transform="translate(175.661,518.16)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(175.661,493.52)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(175.661,468.88)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(175.661,444.24)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(175.661,419.6)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(175.661,394.96)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(175.661,370.32)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(175.661,345.68)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(175.661,321.04)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g><g class="toytree-TipLabel" transform="translate(175.661,296.4)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r10</text></g><g class="toytree-TipLabel" transform="translate(175.661,271.76)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r11</text></g><g class="toytree-TipLabel" transform="translate(175.661,247.12)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r12</text></g><g class="toytree-TipLabel" transform="translate(175.661,222.48)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r13</text></g><g class="toytree-TipLabel" transform="translate(175.661,197.84)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r14</text></g><g class="toytree-TipLabel" transform="translate(175.661,173.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r15</text></g><g class="toytree-TipLabel" transform="translate(175.661,148.56)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r16</text></g><g class="toytree-TipLabel" transform="translate(175.661,123.92)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r17</text></g><g class="toytree-TipLabel" transform="translate(175.661,99.28)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r18</text></g><g class="toytree-TipLabel" transform="translate(175.661,74.64)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r19</text></g></g></g></g><g class="toyplot-coordinates-Axis" id="t5abec567b4f747b690354994e73913a7" transform="translate(50.0,550.0)translate(0,10.0)"><line x1="0.5661385726061402" y1="0" x2="283.635424875676" y2="0" style=""></line><g><g transform="translate(0.5661385726061402,6)"><text x="-8.615" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-1.0</text></g><g transform="translate(142.10078172414106,6)"><text x="-8.615" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-0.5</text></g><g transform="translate(283.635424875676,6)"><text x="-6.95" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.0</text></g><g transform="translate(425.1700680272109,6)"><text x="-6.95" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.5</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g><g class="toyplot-coordinates-Axis" id="t2d357e8c76e64af0a323444282051dbe" transform="translate(50.0,550.0)rotate(-90.0)translate(0,-10.0)"><line x1="6.7476915791966325" y1="0" x2="475.33738457895987" y2="0" style=""></line><g><g transform="translate(6.7476915791966325,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g><g transform="translate(130.0607686843975,-6)"><text x="-2.78" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">5</text></g><g transform="translate(253.3738457895983,-6)"><text x="-5.56" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">10</text></g><g transform="translate(376.6869228947992,-6)"><text x="-5.56" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">15</text></g><g transform="translate(500.0,-6)"><text x="-5.56" y="-4.440892098500626e-16" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">20</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="3.0" y2="-4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="6" style="alignment-baseline:hanging;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "tc562328ff6de45f990a7a3c26662dcf0";
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
        })(modules["toyplot.coordinates.Axis"],"t5abec567b4f747b690354994e73913a7",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.7643519999999999, "min": -1.002}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 500.0, "min": 0.0}, "scale": "linear"}]);
(function(axis, axis_id, projection)
        {
            axis.show_coordinates(axis_id, projection);
        })(modules["toyplot.coordinates.Axis"],"t2d357e8c76e64af0a323444282051dbe",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 20.0, "min": -0.27360000000000173}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 500.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>



```python
c = toyplot.Canvas()
a0 = c.cartesian()
tree.draw(axes=a0)
a0.y.show = False
tree.annotate.add_tip_text(a0)

```




    <toytree.drawing.src.mark_annotation.AnnotationTipLabelMark at 0x7f1fca1d5730>




<div class="toyplot" id="t6fba19b363a244cb98bd78c2410bd9fc" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="600px" height="600px" viewBox="0 0 600 600" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="ta18cd1de15f74b56b9df2ea0d57187ba"><g class="toyplot-coordinates-Cartesian" id="t4fce64b2d8cc498cb27ab3415d475681"><clipPath id="t21b82f36cdef457e9f36f4376ac3db77"><rect x="40.0" y="40.0" width="520.0" height="520.0"></rect></clipPath><g clip-path="url(#t21b82f36cdef457e9f36f4376ac3db77)"><g class="toytree-mark-Toytree" id="t38ac62375074481186b1215d9b997d9d"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 75.8 530.0 L 75.8 542.8 L 175.7 542.8" id="20,0" style=""></path><path d="M 75.8 530.0 L 75.8 517.2 L 175.7 517.2" id="20,1" style=""></path><path d="M 59.2 510.9 L 59.2 491.7 L 175.7 491.7" id="21,2" style=""></path><path d="M 75.8 447.0 L 75.8 466.1 L 175.7 466.1" id="23,3" style=""></path><path d="M 92.5 427.8 L 92.5 440.6 L 175.7 440.6" id="22,4" style=""></path><path d="M 92.5 427.8 L 92.5 415.0 L 175.7 415.0" id="22,5" style=""></path><path d="M 109.1 376.7 L 109.1 389.5 L 175.7 389.5" id="24,6" style=""></path><path d="M 109.1 376.7 L 109.1 363.9 L 175.7 363.9" id="24,7" style=""></path><path d="M 109.1 325.6 L 109.1 338.3 L 175.7 338.3" id="25,8" style=""></path><path d="M 109.1 325.6 L 109.1 312.8 L 175.7 312.8" id="25,9" style=""></path><path d="M 159.0 274.4 L 159.0 287.2 L 175.7 287.2" id="27,10" style=""></path><path d="M 159.0 274.4 L 159.0 261.7 L 175.7 261.7" id="27,11" style=""></path><path d="M 142.4 255.3 L 142.4 236.1 L 175.7 236.1" id="28,12" style=""></path><path d="M 142.4 191.4 L 142.4 210.5 L 175.7 210.5" id="30,13" style=""></path><path d="M 159.0 172.2 L 159.0 185.0 L 175.7 185.0" id="29,14" style=""></path><path d="M 159.0 172.2 L 159.0 159.4 L 175.7 159.4" id="29,15" style=""></path><path d="M 125.7 121.1 L 125.7 133.9 L 175.7 133.9" id="32,16" style=""></path><path d="M 125.7 121.1 L 125.7 108.3 L 175.7 108.3" id="32,17" style=""></path><path d="M 109.1 70.0 L 109.1 82.8 L 175.7 82.8" id="34,18" style=""></path><path d="M 109.1 70.0 L 109.1 57.2 L 175.7 57.2" id="34,19" style=""></path><path d="M 59.2 510.9 L 59.2 530.0 L 75.8 530.0" id="21,20" style=""></path><path d="M 50.9 426.2 L 50.9 510.9 L 59.2 510.9" id="38,21" style=""></path><path d="M 75.8 447.0 L 75.8 427.8 L 92.5 427.8" id="23,22" style=""></path><path d="M 59.2 341.5 L 59.2 447.0 L 75.8 447.0" id="37,23" style=""></path><path d="M 92.5 351.1 L 92.5 376.7 L 109.1 376.7" id="26,24" style=""></path><path d="M 92.5 351.1 L 92.5 325.6 L 109.1 325.6" id="26,25" style=""></path><path d="M 75.8 236.1 L 75.8 351.1 L 92.5 351.1" id="36,26" style=""></path><path d="M 142.4 255.3 L 142.4 274.4 L 159.0 274.4" id="28,27" style=""></path><path d="M 125.7 223.3 L 125.7 255.3 L 142.4 255.3" id="31,28" style=""></path><path d="M 142.4 191.4 L 142.4 172.2 L 159.0 172.2" id="30,29" style=""></path><path d="M 125.7 223.3 L 125.7 191.4 L 142.4 191.4" id="31,30" style=""></path><path d="M 109.1 172.2 L 109.1 223.3 L 125.7 223.3" id="33,31" style=""></path><path d="M 109.1 172.2 L 109.1 121.1 L 125.7 121.1" id="33,32" style=""></path><path d="M 92.5 121.1 L 92.5 172.2 L 109.1 172.2" id="35,33" style=""></path><path d="M 92.5 121.1 L 92.5 70.0 L 109.1 70.0" id="35,34" style=""></path><path d="M 75.8 236.1 L 75.8 121.1 L 92.5 121.1" id="36,35" style=""></path><path d="M 59.2 341.5 L 59.2 236.1 L 75.8 236.1" id="37,36" style=""></path><path d="M 50.9 426.2 L 50.9 341.5 L 59.2 341.5" id="38,37" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(175.661,542.8)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">XXXXXXXXXXXXXXXXXXXXXX</text></g><g class="toytree-TipLabel" transform="translate(175.661,517.242)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(175.661,491.684)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(175.661,466.126)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(175.661,440.568)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(175.661,415.011)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(175.661,389.453)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(175.661,363.895)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(175.661,338.337)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(175.661,312.779)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g><g class="toytree-TipLabel" transform="translate(175.661,287.221)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r10</text></g><g class="toytree-TipLabel" transform="translate(175.661,261.663)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r11</text></g><g class="toytree-TipLabel" transform="translate(175.661,236.105)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r12</text></g><g class="toytree-TipLabel" transform="translate(175.661,210.547)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r13</text></g><g class="toytree-TipLabel" transform="translate(175.661,184.989)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r14</text></g><g class="toytree-TipLabel" transform="translate(175.661,159.432)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r15</text></g><g class="toytree-TipLabel" transform="translate(175.661,133.874)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r16</text></g><g class="toytree-TipLabel" transform="translate(175.661,108.316)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r17</text></g><g class="toytree-TipLabel" transform="translate(175.661,82.7579)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r18</text></g><g class="toytree-TipLabel" transform="translate(175.661,57.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r19</text></g></g></g><g class="toytree-Annotation-TipLabels" id="t70baf23d53274c9d98f2f6c983040801"><g class="toytree-Annotation-TipLabel" transform="translate(175.661,542.8)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">XXXXXXXXXXXXXXXXXXXXXX</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,517.242)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,491.684)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,466.126)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,440.568)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,415.011)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,389.453)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,363.895)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,338.337)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,312.779)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r9</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,287.221)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r10</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,261.663)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r11</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,236.105)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r12</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,210.547)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r13</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,184.989)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r14</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,159.432)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r15</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,133.874)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r16</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,108.316)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r17</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,82.7579)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r18</text></g><g class="toytree-Annotation-TipLabel" transform="translate(175.661,57.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;opacity:1.0;vertical-align:baseline;white-space:pre">r19</text></g></g></g><g class="toyplot-coordinates-Axis" id="t7a90b6f656b448a5a2546db48c15c0d9" transform="translate(50.0,550.0)translate(0,10.0)"><line x1="0.5661385726061402" y1="0" x2="283.635424875676" y2="0" style=""></line><g><g transform="translate(0.5661385726061402,6)"><text x="-8.615" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-1.0</text></g><g transform="translate(142.10078172414106,6)"><text x="-8.615" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">-0.5</text></g><g transform="translate(283.635424875676,6)"><text x="-6.95" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.0</text></g><g transform="translate(425.1700680272109,6)"><text x="-6.95" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.5</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "ta18cd1de15f74b56b9df2ea0d57187ba";
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
        })(modules["toyplot.coordinates.Axis"],"t7a90b6f656b448a5a2546db48c15c0d9",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.7643519999999999, "min": -1.002}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 500.0, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>



```python
c, a, m = tree.draw(scale_bar=True);

```


<div class="toyplot" id="t2895e95c9a3f4fdba67aa0eedd0c5825" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="583.1759999999999px" height="431.2px" viewBox="0 0 583.1759999999999 431.2" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="t51bad068d2904ce58c0a733569b7e86a"><g class="toyplot-coordinates-Cartesian" id="t4a8e333eb00b4117b6346a8f05b80524"><clipPath id="t0a9d8de3ed9f43c2bea6e38eb0824a74"><rect x="35.0" y="35.0" width="513.1759999999999" height="361.2"></rect></clipPath><g clip-path="url(#t0a9d8de3ed9f43c2bea6e38eb0824a74)"><g class="toytree-mark-Toytree" id="tcb63f0aa46964292b401087ae4d77584"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 75.9 365.7 L 75.9 374.0 L 175.5 374.0" id="20,0" style=""></path><path d="M 75.9 365.7 L 75.9 357.3 L 175.5 357.3" id="20,1" style=""></path><path d="M 59.2 353.2 L 59.2 340.7 L 175.5 340.7" id="21,2" style=""></path><path d="M 75.9 311.5 L 75.9 324.0 L 175.5 324.0" id="23,3" style=""></path><path d="M 92.5 299.0 L 92.5 307.3 L 175.5 307.3" id="22,4" style=""></path><path d="M 92.5 299.0 L 92.5 290.6 L 175.5 290.6" id="22,5" style=""></path><path d="M 109.1 265.6 L 109.1 274.0 L 175.5 274.0" id="24,6" style=""></path><path d="M 109.1 265.6 L 109.1 257.3 L 175.5 257.3" id="24,7" style=""></path><path d="M 109.1 232.3 L 109.1 240.6 L 175.5 240.6" id="25,8" style=""></path><path d="M 109.1 232.3 L 109.1 223.9 L 175.5 223.9" id="25,9" style=""></path><path d="M 158.9 198.9 L 158.9 207.3 L 175.5 207.3" id="27,10" style=""></path><path d="M 158.9 198.9 L 158.9 190.6 L 175.5 190.6" id="27,11" style=""></path><path d="M 142.3 186.4 L 142.3 173.9 L 175.5 173.9" id="28,12" style=""></path><path d="M 142.3 144.7 L 142.3 157.2 L 175.5 157.2" id="30,13" style=""></path><path d="M 158.9 132.2 L 158.9 140.6 L 175.5 140.6" id="29,14" style=""></path><path d="M 158.9 132.2 L 158.9 123.9 L 175.5 123.9" id="29,15" style=""></path><path d="M 125.7 98.9 L 125.7 107.2 L 175.5 107.2" id="32,16" style=""></path><path d="M 125.7 98.9 L 125.7 90.5 L 175.5 90.5" id="32,17" style=""></path><path d="M 109.1 65.5 L 109.1 73.9 L 175.5 73.9" id="34,18" style=""></path><path d="M 109.1 65.5 L 109.1 57.2 L 175.5 57.2" id="34,19" style=""></path><path d="M 59.2 353.2 L 59.2 365.7 L 75.9 365.7" id="21,20" style=""></path><path d="M 50.9 297.9 L 50.9 353.2 L 59.2 353.2" id="38,21" style=""></path><path d="M 75.9 311.5 L 75.9 299.0 L 92.5 299.0" id="23,22" style=""></path><path d="M 59.2 242.7 L 59.2 311.5 L 75.9 311.5" id="37,23" style=""></path><path d="M 92.5 248.9 L 92.5 265.6 L 109.1 265.6" id="26,24" style=""></path><path d="M 92.5 248.9 L 92.5 232.3 L 109.1 232.3" id="26,25" style=""></path><path d="M 75.9 173.9 L 75.9 248.9 L 92.5 248.9" id="36,26" style=""></path><path d="M 142.3 186.4 L 142.3 198.9 L 158.9 198.9" id="28,27" style=""></path><path d="M 125.7 165.6 L 125.7 186.4 L 142.3 186.4" id="31,28" style=""></path><path d="M 142.3 144.7 L 142.3 132.2 L 158.9 132.2" id="30,29" style=""></path><path d="M 125.7 165.6 L 125.7 144.7 L 142.3 144.7" id="31,30" style=""></path><path d="M 109.1 132.2 L 109.1 165.6 L 125.7 165.6" id="33,31" style=""></path><path d="M 109.1 132.2 L 109.1 98.9 L 125.7 98.9" id="33,32" style=""></path><path d="M 92.5 98.9 L 92.5 132.2 L 109.1 132.2" id="35,33" style=""></path><path d="M 92.5 98.9 L 92.5 65.5 L 109.1 65.5" id="35,34" style=""></path><path d="M 75.9 173.9 L 75.9 98.9 L 92.5 98.9" id="36,35" style=""></path><path d="M 59.2 242.7 L 59.2 173.9 L 75.9 173.9" id="37,36" style=""></path><path d="M 50.9 297.9 L 50.9 242.7 L 59.2 242.7" id="38,37" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(175.51,374)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">XXXXXXXXXXXXXXXXXXXXXX</text></g><g class="toytree-TipLabel" transform="translate(175.51,357.326)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(175.51,340.653)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(175.51,323.979)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(175.51,307.305)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(175.51,290.632)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(175.51,273.958)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(175.51,257.284)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(175.51,240.611)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(175.51,223.937)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g><g class="toytree-TipLabel" transform="translate(175.51,207.263)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r10</text></g><g class="toytree-TipLabel" transform="translate(175.51,190.589)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r11</text></g><g class="toytree-TipLabel" transform="translate(175.51,173.916)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r12</text></g><g class="toytree-TipLabel" transform="translate(175.51,157.242)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r13</text></g><g class="toytree-TipLabel" transform="translate(175.51,140.568)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r14</text></g><g class="toytree-TipLabel" transform="translate(175.51,123.895)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r15</text></g><g class="toytree-TipLabel" transform="translate(175.51,107.221)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r16</text></g><g class="toytree-TipLabel" transform="translate(175.51,90.5474)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r17</text></g><g class="toytree-TipLabel" transform="translate(175.51,73.8737)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r18</text></g><g class="toytree-TipLabel" transform="translate(175.51,57.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r19</text></g></g></g></g><g class="toyplot-coordinates-Axis" id="t79cbc1345dfa41f2a01733b655421484" transform="translate(50.0,381.2)translate(0,15.0)"><line x1="0.5577132620459113" y1="0" x2="270.0313763643415" y2="0" style=""></line><g><line x1="0.5577132620459113" y1="0" x2="0.5577132620459113" y2="-5" style=""></line><line x1="67.9261290376198" y1="0" x2="67.9261290376198" y2="-5" style=""></line><line x1="135.29454481319368" y1="0" x2="135.29454481319368" y2="-5" style=""></line><line x1="202.66296058876756" y1="0" x2="202.66296058876756" y2="-5" style=""></line><line x1="270.0313763643415" y1="0" x2="270.0313763643415" y2="-5" style=""></line></g><g><g transform="translate(0.5577132620459113,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(67.9261290376198,6)"><text x="-9.729999999999999" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.75</text></g><g transform="translate(135.29454481319368,6)"><text x="-6.95" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.5</text></g><g transform="translate(202.66296058876756,6)"><text x="-9.729999999999999" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.25</text></g><g transform="translate(270.0313763643415,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "t51bad068d2904ce58c0a733569b7e86a";
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
        })(modules["toyplot.coordinates.Axis"],"t79cbc1345dfa41f2a01733b655421484",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.7909664387304005, "min": -1.002069639220491}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 483.17599999999993, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>



```python
c, a, m = tree.draw();
tree.annotate.add_axes_scale_bar(a);

```


<div class="toyplot" id="tc26b0ce23f1549c5a6dfdcc291f6ea46" style="text-align:center"><svg class="toyplot-canvas-Canvas" xmlns:toyplot="http://www.sandia.gov/toyplot" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns="http://www.w3.org/2000/svg" width="583.1759999999999px" height="431.2px" viewBox="0 0 583.1759999999999 431.2" preserveAspectRatio="xMidYMid meet" style="background-color:transparent;border-color:#292724;border-style:none;border-width:1.0;fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;opacity:1.0;stroke:rgb(16.1%,15.3%,14.1%);stroke-opacity:1.0;stroke-width:1.0" id="td5b2b947275845608cd244fd5c1c74a9"><g class="toyplot-coordinates-Cartesian" id="t25b87729f0194e9c9fdc8c3bfa72d559"><clipPath id="tbf737b1eb6b848249ffedba4eb45c1f3"><rect x="35.0" y="35.0" width="513.1759999999999" height="361.2"></rect></clipPath><g clip-path="url(#tbf737b1eb6b848249ffedba4eb45c1f3)"><g class="toytree-mark-Toytree" id="tf2fe4b4db54b412182ca52ee8262b0b9"><g class="toytree-Edges" style="stroke:rgb(14.5%,14.5%,14.5%);stroke-opacity:1.0;stroke-linecap:round;stroke-width:2.0;fill:none"><path d="M 75.9 365.7 L 75.9 374.0 L 175.5 374.0" id="20,0" style=""></path><path d="M 75.9 365.7 L 75.9 357.3 L 175.5 357.3" id="20,1" style=""></path><path d="M 59.2 353.2 L 59.2 340.7 L 175.5 340.7" id="21,2" style=""></path><path d="M 75.9 311.5 L 75.9 324.0 L 175.5 324.0" id="23,3" style=""></path><path d="M 92.5 299.0 L 92.5 307.3 L 175.5 307.3" id="22,4" style=""></path><path d="M 92.5 299.0 L 92.5 290.6 L 175.5 290.6" id="22,5" style=""></path><path d="M 109.1 265.6 L 109.1 274.0 L 175.5 274.0" id="24,6" style=""></path><path d="M 109.1 265.6 L 109.1 257.3 L 175.5 257.3" id="24,7" style=""></path><path d="M 109.1 232.3 L 109.1 240.6 L 175.5 240.6" id="25,8" style=""></path><path d="M 109.1 232.3 L 109.1 223.9 L 175.5 223.9" id="25,9" style=""></path><path d="M 158.9 198.9 L 158.9 207.3 L 175.5 207.3" id="27,10" style=""></path><path d="M 158.9 198.9 L 158.9 190.6 L 175.5 190.6" id="27,11" style=""></path><path d="M 142.3 186.4 L 142.3 173.9 L 175.5 173.9" id="28,12" style=""></path><path d="M 142.3 144.7 L 142.3 157.2 L 175.5 157.2" id="30,13" style=""></path><path d="M 158.9 132.2 L 158.9 140.6 L 175.5 140.6" id="29,14" style=""></path><path d="M 158.9 132.2 L 158.9 123.9 L 175.5 123.9" id="29,15" style=""></path><path d="M 125.7 98.9 L 125.7 107.2 L 175.5 107.2" id="32,16" style=""></path><path d="M 125.7 98.9 L 125.7 90.5 L 175.5 90.5" id="32,17" style=""></path><path d="M 109.1 65.5 L 109.1 73.9 L 175.5 73.9" id="34,18" style=""></path><path d="M 109.1 65.5 L 109.1 57.2 L 175.5 57.2" id="34,19" style=""></path><path d="M 59.2 353.2 L 59.2 365.7 L 75.9 365.7" id="21,20" style=""></path><path d="M 50.9 297.9 L 50.9 353.2 L 59.2 353.2" id="38,21" style=""></path><path d="M 75.9 311.5 L 75.9 299.0 L 92.5 299.0" id="23,22" style=""></path><path d="M 59.2 242.7 L 59.2 311.5 L 75.9 311.5" id="37,23" style=""></path><path d="M 92.5 248.9 L 92.5 265.6 L 109.1 265.6" id="26,24" style=""></path><path d="M 92.5 248.9 L 92.5 232.3 L 109.1 232.3" id="26,25" style=""></path><path d="M 75.9 173.9 L 75.9 248.9 L 92.5 248.9" id="36,26" style=""></path><path d="M 142.3 186.4 L 142.3 198.9 L 158.9 198.9" id="28,27" style=""></path><path d="M 125.7 165.6 L 125.7 186.4 L 142.3 186.4" id="31,28" style=""></path><path d="M 142.3 144.7 L 142.3 132.2 L 158.9 132.2" id="30,29" style=""></path><path d="M 125.7 165.6 L 125.7 144.7 L 142.3 144.7" id="31,30" style=""></path><path d="M 109.1 132.2 L 109.1 165.6 L 125.7 165.6" id="33,31" style=""></path><path d="M 109.1 132.2 L 109.1 98.9 L 125.7 98.9" id="33,32" style=""></path><path d="M 92.5 98.9 L 92.5 132.2 L 109.1 132.2" id="35,33" style=""></path><path d="M 92.5 98.9 L 92.5 65.5 L 109.1 65.5" id="35,34" style=""></path><path d="M 75.9 173.9 L 75.9 98.9 L 92.5 98.9" id="36,35" style=""></path><path d="M 59.2 242.7 L 59.2 173.9 L 75.9 173.9" id="37,36" style=""></path><path d="M 50.9 297.9 L 50.9 242.7 L 59.2 242.7" id="38,37" style=""></path></g><g class="toytree-AdmixEdges" style="fill:rgb(0.0%,0.0%,0.0%);fill-opacity:0.0;stroke:rgb(90.6%,54.1%,76.5%);stroke-opacity:0.6;font-size:14px;stroke-linecap:round;stroke-width:5"></g><g class="toytree-Nodes" style="fill:rgb(40.0%,76.1%,64.7%);fill-opacity:1.0;stroke:rgb(14.9%,14.9%,14.9%);stroke-opacity:1.0;stroke-width:1.5"></g><g class="toytree-TipLabels" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;font-family:Helvetica;font-size:12px;font-weight:300;vertical-align:baseline;white-space:pre;stroke:none"><g class="toytree-TipLabel" transform="translate(175.51,374)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">XXXXXXXXXXXXXXXXXXXXXX</text></g><g class="toytree-TipLabel" transform="translate(175.51,357.326)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r1</text></g><g class="toytree-TipLabel" transform="translate(175.51,340.653)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r2</text></g><g class="toytree-TipLabel" transform="translate(175.51,323.979)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r3</text></g><g class="toytree-TipLabel" transform="translate(175.51,307.305)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r4</text></g><g class="toytree-TipLabel" transform="translate(175.51,290.632)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r5</text></g><g class="toytree-TipLabel" transform="translate(175.51,273.958)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r6</text></g><g class="toytree-TipLabel" transform="translate(175.51,257.284)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r7</text></g><g class="toytree-TipLabel" transform="translate(175.51,240.611)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r8</text></g><g class="toytree-TipLabel" transform="translate(175.51,223.937)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r9</text></g><g class="toytree-TipLabel" transform="translate(175.51,207.263)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r10</text></g><g class="toytree-TipLabel" transform="translate(175.51,190.589)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r11</text></g><g class="toytree-TipLabel" transform="translate(175.51,173.916)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r12</text></g><g class="toytree-TipLabel" transform="translate(175.51,157.242)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r13</text></g><g class="toytree-TipLabel" transform="translate(175.51,140.568)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r14</text></g><g class="toytree-TipLabel" transform="translate(175.51,123.895)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r15</text></g><g class="toytree-TipLabel" transform="translate(175.51,107.221)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r16</text></g><g class="toytree-TipLabel" transform="translate(175.51,90.5474)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r17</text></g><g class="toytree-TipLabel" transform="translate(175.51,73.8737)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r18</text></g><g class="toytree-TipLabel" transform="translate(175.51,57.2)"><text x="15.0" y="3.066" style="fill:rgb(14.5%,14.5%,14.5%);fill-opacity:1.0;stroke:rgb(0.0%,0.0%,0.0%);stroke-opacity:0.0;font-family:Helvetica;font-size:12.0px;font-weight:300;vertical-align:baseline;white-space:pre">r19</text></g></g></g></g><g class="toyplot-coordinates-Axis" id="t55119e7ebf69498e886d10407bfd95a6" transform="translate(50.0,381.2)translate(0,15.0)"><line x1="0.5577132620459113" y1="0" x2="270.0313763643415" y2="0" style=""></line><g><line x1="0.5577132620459113" y1="0" x2="0.5577132620459113" y2="-5" style=""></line><line x1="67.9261290376198" y1="0" x2="67.9261290376198" y2="-5" style=""></line><line x1="135.29454481319368" y1="0" x2="135.29454481319368" y2="-5" style=""></line><line x1="202.66296058876756" y1="0" x2="202.66296058876756" y2="-5" style=""></line><line x1="270.0313763643415" y1="0" x2="270.0313763643415" y2="-5" style=""></line></g><g><g transform="translate(0.5577132620459113,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">1</text></g><g transform="translate(67.9261290376198,6)"><text x="-9.729999999999999" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.75</text></g><g transform="translate(135.29454481319368,6)"><text x="-6.95" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.5</text></g><g transform="translate(202.66296058876756,6)"><text x="-9.729999999999999" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0.25</text></g><g transform="translate(270.0313763643415,6)"><text x="-2.78" y="8.555" style="fill:rgb(16.1%,15.3%,14.1%);fill-opacity:1.0;font-family:helvetica;font-size:10.0px;font-weight:normal;stroke:none;vertical-align:baseline;white-space:pre">0</text></g></g><g class="toyplot-coordinates-Axis-coordinates" style="visibility:hidden" transform=""><line x1="0" x2="0" y1="-3.0" y2="4.5" style="stroke:rgb(43.9%,50.2%,56.5%);stroke-opacity:1.0;stroke-width:1.0"></line><text x="0" y="-6" style="alignment-baseline:alphabetic;fill:rgb(43.9%,50.2%,56.5%);fill-opacity:1.0;font-size:10px;font-weight:normal;stroke:none;text-anchor:middle"></text></g></g></g></svg><div class="toyplot-behavior"><script>(function()
{
var modules={};
modules["toyplot/canvas/id"] = "td5b2b947275845608cd244fd5c1c74a9";
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
        })(modules["toyplot.coordinates.Axis"],"t55119e7ebf69498e886d10407bfd95a6",[{"domain": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 0.7909664387304005, "min": -1.002069639220491}, "range": {"bounds": {"max": Infinity, "min": -Infinity}, "max": 483.17599999999993, "min": 0.0}, "scale": "linear"}]);
})();</script></div></div>



```python


```
