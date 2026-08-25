# Docs workflow

Install the local docs toolchain:

```bash
python -m pip install -e '.[docs]'
```

Docs source layout:

- `docs/src/`: notebook sources
- `docs/pages/`: published Markdown pages and published static assets
- `docs/pages/css/`: site styling
- `docs/pages/javascripts/`: site JavaScript
- `docs/pages/assets/`: static assets

See [`DEVELOPMENT.md`](DEVELOPMENT.md) for the complete authoring, conversion,
and publication workflow.

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
