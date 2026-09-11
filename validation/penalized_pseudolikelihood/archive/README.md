# Historical validation archive

The active package contains only supported fitting methods and current validation/reporting code. Superseded and rejected development workflows remain reproducible from commit `cb0dfc3c4fae61a75c3d8bdd367ad1c57bd2953d`.

Create a detached worktree without changing your current checkout:

```bash
git worktree add /tmp/toytree-pl-archive cb0dfc3c4fae61a75c3d8bdd367ad1c57bd2953d
```

Run historical commands from that worktree and its recorded environment. To recover one file without a worktree, use `git show cb0dfc3c4fae61a75c3d8bdd367ad1c57bd2953d:PATH`. The machine-readable [manifest](manifest.json) maps rejected workflows to their study versions.

The 52 MB V18 raw result is intentionally absent from the current tree. Its compact conclusion is in `../v18/summary-v18-pilot.json`; the manifest records the source commit, blob, SHA-256, and byte size for exact recovery. No Git history rewrite or Git LFS dependency is required.
