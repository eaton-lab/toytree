# Documentation development workflow

This file describes how developers and automation should create the Toytree
documentation. It is an internal reference, not a page in the published site.
Keep it outside `docs/pages` and do not add it to the navigation in
`mkdocs.yml`.

## Source layout

- `docs/src/` contains source Jupyter notebooks.
- `docs/pages/` contains the Markdown and static assets consumed by Zensical.
- `docs/nb_to_md.py` executes and converts notebooks into published pages.
- `mkdocs.yml` configures the site and its navigation.

Notebook-derived pages use matching filename stems. For example,
`docs/src/drawing-basics.ipynb` produces `docs/pages/drawing-basics.md` and,
when needed, a `docs/pages/drawing-basics_files/` asset directory. The notebook
is the source of truth; edits made only to generated Markdown will be
overwritten the next time the notebook is converted.

Some pages are authored directly as Markdown in `docs/pages`. These do not
need a corresponding notebook.

## Set up the documentation environment

From the repository root, install Toytree in editable mode with its optional
documentation dependencies:

```bash
python -m pip install -e '.[docs]'
```

The `docs` extra installs Jupyter and nbconvert for notebook execution and
conversion, plus Zensical and the Markdown extensions used to build the site.

## Publish notebook-derived pages

After editing a notebook in `docs/src`, run the converter from the repository
root. Pass a notebook stem, with no directory or extension:

```bash
python docs/nb_to_md.py drawing-basics
```

More than one notebook can be processed in one command:

```bash
python docs/nb_to_md.py drawing-basics drawing-options
```

The converter performs the following work for each notebook:

1. Executes a temporary copy of the source notebook.
2. Converts the executed copy to Markdown with nbconvert.
3. Adds the hidden page marker used by the notebook-output stylesheet.
4. Writes `docs/pages/<stem>.md`.
5. Replaces `docs/pages/<stem>_files/` with newly generated assets, or removes
   the old asset directory when the new output has no external assets.

Execution does not rewrite the source notebook. A failed execution therefore
does not leave a partially modified notebook or published page.

To convert using outputs already saved in a notebook, without executing its
cells, use:

```bash
python docs/nb_to_md.py --no-execute drawing-basics
```

The converter also accepts `--all`, but this means every notebook in
`docs/src`, including drafts, scratch files, and backups. Prefer explicitly
named notebooks for routine development and automation.

After conversion, review and commit all related files:

- the source `.ipynb` file;
- the generated `.md` file;
- any generated `<stem>_files/` assets; and
- `mkdocs.yml`, if the published page should be added to or moved in the site
  navigation.

## Build and preview the site

Build the site from the repository root:

```bash
python -m zensical build -f mkdocs.yml
```

For a local preview with automatic rebuilds:

```bash
python -m zensical serve -f mkdocs.yml
```

Zensical reads `docs/pages` as its documentation directory and writes the
built site to `site/`. It does not read or execute notebooks from `docs/src`.

## Automation behavior

The GitHub Pages workflow currently runs for version tags. It builds and
deploys the Markdown and assets already committed under `docs/pages`; it does
not run `docs/nb_to_md.py`.

Bots modifying a notebook-derived page should run the converter for each
notebook they changed and include the resulting Markdown and assets in the
same change. They should not regenerate every notebook with `--all` unless the
task explicitly calls for a complete documentation rebuild.
