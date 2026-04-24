---
section: Getting Started
---


# Contributing

**Collaborator's are very welcome!**

If you haven’t already, you’ll want to first get familiar with the `toytree`
repository at [http://github.com/eaton-lab/toytree](http://github.com/eaton-lab/toytree). 
There you will find the source code and issue tracker where you can inquire
about ongoing development, discuss planned contributions, and volunteer to take
on known issues or future planned developments.

## Organization
As of `toytree` v.3.0 the code base has been reorganized explicitly to better
facilitate collaborative development. This involves the organization of code
into a nested hierarchy of subpackages that share common themes. Many of these
have a clear template structure which can be easily modified or extended to
create new useful methods. For example, a new method could be created for
annotating drawings within the `annotation` subpackage, or a new method for
modifying a tree could be created in the `mod` subpackage. 

## Getting started
To contribute as a developer you'll need to install `toytree` from source
on GitHub and install additional dependencies used for testing the code.
My workflow for this is to clone the repository (in your case, a fork of the
repo) and install in development mode using pip.

```bash
# install dependencies from conda
$ conda install toytree -c eaton-lab --only-deps

# clone the repo and cd into it
$ git clone https://github.com/eaton-lab/toytree.git
$ cd toytree/

# call pip install in 'development mode' (note the '-e .')
$ pip install -e .
```


## Coding Style
The Toyplot source code follows the PEP-8 Style Guide for Python Code.

## Documentation workflow
The docs site is built with `zensical` using `mkdocs.yml` as the top-level
config. Notebook sources live in `docs/source` and published pages plus static
site assets live in `docs/pages`.

Build and serve locally:

```bash
python -m zensical build -f mkdocs.yml
python -m zensical serve -f mkdocs.yml
```

## Notebook to Markdown docs pages
Visualization-heavy docs pages are authored as notebooks in `docs/source` and
published as Markdown pages in `docs/pages`. The recommended workflow is:

1. Edit the source notebook in `docs/source`.
2. Execute and convert it with `docs/nb_to_md.py`.
3. Commit the generated `.md` page and any generated `<page>_files/` assets.
4. Point `mkdocs.yml` nav at the published `.md` page.

Use the helper script from the repository root:

```bash
python docs/nb_to_md.py quick_guide parse_trees
python docs/nb_to_md.py --all
```

If notebook execution is unavailable in the current environment, you can still
publish pages from saved outputs:

```bash
python docs/nb_to_md.py --no-execute quick_guide
```

Important behavior:

- `docs/nb_to_md.py` executes notebooks in a temporary working directory, so
  failed runs do not partially rewrite the source notebooks in `docs/source`.
- `nbconvert --to markdown` preserves executed outputs, including inline
  HTML / SVG / JS figures such as Toyplot drawings.
- Notebook-derived markdown pages get a hidden `.nb-md-page-hook` marker so
  plain-text executed outputs can be styled on markdown pages.
- Manual markdown pages can use explicit output-styled blocks with
  ` ```output ` fences. These blocks are styled the same way as
  notebook-derived plain-text outputs.

Example:

````md
```output
expected stdout or serialized tree text
```
````
