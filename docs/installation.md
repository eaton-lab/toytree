---
section: Getting Started
---

# Installation
`toytree` can be installed using pip or conda (or mamba), any of which will
pull in all required dependencies. We also provide instructions below for
installing from source (GitHub).


Conda install (recommended)
---------------------------
```bash
$ conda install toytree -c conda-forge
```

Pip install
-----------
```bash
$ pip install toytree
```

Dependencies
------------
Our goal is to maintain `toytree` as a minimalist library that does not require
substantial dependencies outside of the standard Python scientific stack (i.e.,
numpy, scipy, and pandas). 

    - python>=3.7
    - numpy
    - scipy
    - pandas
    - loguru
    - requests
    - toyplot
    - ghostscript  # to save PNGs


Installing Development Versions
-------------------------------

```bash
$ git clone https://github.com/eaton-lab/toytree.git
$ cd toytree
$ conda install toytree -c conda-forge --only-deps
$ pip install -e . --no-deps
```


Building the documentation
---------------------------
```bash
$ conda install mkdocs-material mkdocstrings-python mkdocs-jupyter -c conda-forge
```
