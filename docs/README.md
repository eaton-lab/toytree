# Docs workflow

Install the local docs toolchain from the repository root:

```bash
python -m pip install -e '.[docs]'
```

Docs source layout:

- `docs/src/`: canonical notebook sources
- `docs/pages/`: published Markdown pages and published static assets
- `docs/pages/css/`: site styling
- `docs/pages/javascripts/`: site JavaScript
- `docs/pages/assets/`: static assets

Build and serve the docs locally:

```bash
python -m zensical build -f mkdocs.yml
python -m zensical serve -f mkdocs.yml
```

Execute notebooks and publish Markdown pages:

```bash
python docs/nb_to_md.py quick_guide parse_trees
python docs/nb_to_md.py --all
python docs/nb_to_md.py --no-execute quick_guide
```

Each notebook in `docs/src/<name>.ipynb` is paired with the generated page
`docs/pages/<name>.md`. The pairing is automated by `docs/nb_to_md.py`; use a
list of notebook stems for selected pages or `--all` for every source notebook.
Both the notebook and generated Markdown page are committed.

The GitHub Pages action builds Zensical from committed Markdown. It does not
execute notebooks or regenerate paired pages: notebook execution can be slow,
may require optional scientific dependencies, and should be reviewed as a
normal source diff before publication.
