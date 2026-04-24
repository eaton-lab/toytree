#!/usr/bin/env python
"""Execute docs notebooks and publish them as Markdown pages.

This helper runs notebooks from ``docs/src`` in a temporary working
directory, converts the executed notebooks to Markdown with ``nbconvert``, and
writes the published pages plus any ``<page>_files`` assets into ``docs/pages``.
It reports notebook failures at the end and separately lists Markdown pages
that changed relative to a previous on-disk version.
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

NB_MD_PAGE_HOOK = '<div class="nb-md-page-hook" aria-hidden="true"></div>\n'
DOCS_DIR = Path(__file__).resolve().parent
SRC_DIR = DOCS_DIR / "src"
PAGES_DIR = DOCS_DIR / "pages"


def build_parser() -> argparse.ArgumentParser:
    """Return the CLI parser for notebook execution and Markdown publishing."""
    parser = argparse.ArgumentParser(
        description=(
            "Execute notebooks from docs/src and publish Markdown pages to "
            "docs/pages."
        ),
    )
    parser.add_argument(
        "notebooks",
        nargs="*",
        help=(
            "Notebook stems or paths to execute, for example 'quick_guide' or "
            "'docs/src/quick_guide.ipynb'."
        ),
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Execute and publish every .ipynb notebook in docs/src.",
    )
    parser.add_argument(
        "--no-execute",
        action="store_true",
        help="Convert notebooks using their saved outputs instead of executing them.",
    )
    return parser


def _insert_page_hook(md_text: str) -> str:
    """Insert a hidden page hook so markdown-only CSS can target outputs."""
    if NB_MD_PAGE_HOOK.strip() in md_text:
        return md_text

    # Preserve YAML front matter at the very top so the docs builder still
    # parses metadata correctly, but insert the hook immediately after it.
    if md_text.startswith("---\n"):
        end = md_text.find("\n---\n", 4)
        if end != -1:
            end += len("\n---\n")
            return md_text[:end] + "\n" + NB_MD_PAGE_HOOK + md_text[end:]
    return NB_MD_PAGE_HOOK + "\n" + md_text


def _resolve_notebook(token: str) -> Path:
    """Resolve a notebook stem or path to an existing ``.ipynb`` src file."""
    raw = Path(token).expanduser()
    candidates = []
    if raw.suffix == ".ipynb":
        candidates.extend(
            [
                raw,
                Path.cwd() / raw,
                SRC_DIR / raw.name,
            ]
        )
    else:
        candidates.extend(
            [
                SRC_DIR / f"{raw.name}.ipynb",
                raw.with_suffix(".ipynb"),
                Path.cwd() / raw.with_suffix(".ipynb"),
            ]
        )

    seen: set[Path] = set()
    for candidate in candidates:
        path = candidate.resolve()
        if path in seen:
            continue
        seen.add(path)
        if path.exists() and path.suffix == ".ipynb":
            return path
    raise FileNotFoundError(token)


def _run_nbconvert(cmd: list[str]) -> None:
    """Execute an nbconvert command and raise on failure."""
    subprocess.run(cmd, check=True, capture_output=True, text=True)


def _publish_notebook(notebook: Path, *, execute: bool = True) -> tuple[bool, bool]:
    """Execute one notebook and publish its Markdown page.

    Returns
    -------
    tuple[bool, bool]
        A pair ``(created, changed)`` describing whether the Markdown page was
        newly created and whether it differed from a previous on-disk version.
    """
    stem = notebook.stem
    target_md = PAGES_DIR / f"{stem}.md"
    target_assets = PAGES_DIR / f"{stem}_files"

    with tempfile.TemporaryDirectory(prefix=f"toytree-docs-{stem}-") as tmpdir:
        tmpdir_path = Path(tmpdir)
        executed_path = tmpdir_path / "executed.ipynb"

        if execute:
            # Execute a temporary copy so failed runs never partially modify the
            # checked-in source notebooks under docs/src.
            _run_nbconvert(
                [
                    sys.executable,
                    "-m",
                    "nbconvert",
                    "--to",
                    "notebook",
                    "--execute",
                    "--ExecutePreprocessor.timeout=-1",
                    str(notebook),
                    "--output",
                    executed_path.name,
                    "--output-dir",
                    str(tmpdir_path),
                ]
            )
        else:
            shutil.copy2(notebook, executed_path)

        # Convert the executed notebook to markdown in a temp output directory
        # and only sync files into docs/pages once conversion has succeeded.
        _run_nbconvert(
            [
                sys.executable,
                "-m",
                "nbconvert",
                "--to",
                "markdown",
                str(executed_path),
                "--output",
                stem,
                "--output-dir",
                str(tmpdir_path),
            ]
        )

        tmp_md = tmpdir_path / f"{stem}.md"
        md_text = _insert_page_hook(tmp_md.read_text())
        created = not target_md.exists()
        changed = target_md.exists() and target_md.read_text() != md_text

        target_md.write_text(md_text)

        tmp_assets = tmpdir_path / f"{stem}_files"
        if target_assets.exists():
            shutil.rmtree(target_assets)
        if tmp_assets.exists():
            shutil.copytree(tmp_assets, target_assets)

    return created, changed


def _iter_selected_notebooks(args: argparse.Namespace) -> list[Path]:
    """Return the src notebooks selected by CLI arguments."""
    if args.all:
        notebooks = sorted(SRC_DIR.glob("*.ipynb"))
        if not notebooks:
            raise FileNotFoundError("no notebooks found in docs/src")
        return notebooks

    if not args.notebooks:
        raise FileNotFoundError("select one or more notebooks or use --all")

    resolved = []
    seen: set[Path] = set()
    for token in args.notebooks:
        path = _resolve_notebook(token)
        if path not in seen:
            seen.add(path)
            resolved.append(path)
    return resolved


def main(argv: list[str] | None = None) -> int:
    """Execute selected notebooks and publish their Markdown pages."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        notebooks = _iter_selected_notebooks(args)
    except FileNotFoundError as exc:
        parser.error(str(exc))

    SRC_DIR.mkdir(parents=True, exist_ok=True)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)

    created: list[str] = []
    changed: list[str] = []
    failed: list[tuple[str, str]] = []

    for notebook in notebooks:
        try:
            was_created, was_changed = _publish_notebook(
                notebook,
                execute=not args.no_execute,
            )
        except subprocess.CalledProcessError as exc:
            stderr = exc.stderr.strip() or exc.stdout.strip() or str(exc)
            failed.append((notebook.name, stderr))
            continue

        if was_created:
            created.append(notebook.stem)
        elif was_changed:
            changed.append(notebook.stem)

    print(f"processed notebooks: {len(notebooks)}")
    print("created markdown pages: " + (", ".join(created) if created else "none"))
    print("changed markdown pages: " + (", ".join(changed) if changed else "none"))

    if failed:
        print("failed notebooks:", file=sys.stderr)
        for name, stderr in failed:
            print(f"- {name}", file=sys.stderr)
            print(stderr, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
