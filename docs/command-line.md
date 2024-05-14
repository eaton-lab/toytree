---
section: Command line
---

# Command line


## `toytree` cli
Sometimes you might not be in the mood to open a jupyter notebook just to take a quick peek at a tree, in which case, the toytree command line interface (cli) provides a convenient alternative. This tool can be called from a terminal shell to execute one or more simple commands to accomplish tasks such as creating tree drawings, rooting trees, and comparing trees. 

## Subcommands
Currently three subcommands are supported in the cli: draw, root, and distance. (Please reach out and let us know if you would like to see additional toytree methods implemented in the cli.) Call the help command (-h) to see the available subcommands.

```bash
$ toytree -h
```

This will bring up a help statement like below. Each subcommand also has its own help page that describes its usage and options, as demonstrated below.

```bash
usage: toytree [-h] [-v] {draw,root,distance} ...

toytree command line tool. Select a subcommand.

positional arguments:
  {draw,root,distance}  sub-commands
    draw                create tree drawing
    root                (re)root tree and return to STDOUT
    distance            compute distance between trees

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit

EXAMPLE: $ toytree draw TREE -ts o -d 400 400 -v
```

## toytree draw

```bash
$ toytree draw -h
```

```bash
usage: toytree draw [-h] [-ts treestyle] [-d dim dim] [-o basename] [-v [app]]
                    [-f {html,svg,pdf}]
                    TREE

positional arguments:
  TREE               tree newick file or string

options:
  -h, --help         show this help message and exit
  -ts treestyle      tree style (default: n)
  -d dim dim         width height (px) (default: (None, None))
  -o basename        output basename[.format suffix] (default: /tmp/test)
  -v [app]           open file with default browser or app. (default: None)
  -f {html,svg,pdf}  output file format (default: html)
```

## toytree root

```bash
$ toytree root -h
```

```bash
usage: toytree root [-h] [-o O [O ...]] [-r] TREE

positional arguments:
  TREE          tree newick file or string

options:
  -h, --help    show this help message and exit
  -o O [O ...]  outgroup
  -r            use regex matching on outgroup string.
```

## toytree distance

```bash
$ toytree distance -h
```

```bash
usage: toytree distance [-h] [-m {rf,rfi,rfj,qrt}] [-n] TREE1 TREE2

positional arguments:
  TREE1                tree1 newick file or string
  TREE2                tree2 newick file or string

options:
  -h, --help           show this help message and exit
  -m {rf,rfi,rfj,qrt}  distance metric method
  -n, --normalize      normalize value between [0-1]
```

## chaining
To indicate to the draw function that the NEWICk input is the STDOUT from the previous command, use the `-` character like below.

```bash
toytree root NEWICK | toytree draw - ...
```
