# Penalized-pseudolikelihood validation

This directory records the statistical and numerical evidence behind ToyTree's ultrametric models. The machine-readable [release ledger](release-status.json) is authoritative.

## Final supported surface

- `clock`: validated strict clock.
- `discrete`: validated `ape::chronos`-compatible fractional-Poisson branchwise finite mixture with an explicit category count.
- `correlated`: validated complete-tree log-rate smoothing at a user-supplied positive lambda.
- `uncorrelated_lognormal`: validated centered log-rate dispersion at a user-supplied positive lambda; positive continuous branches are the primary validated scope and zero-rich fits require passing fit diagnostics.
- `relaxed`: compatibility-only implementation of the `ape::chronos` Gamma-CDF convention; UCLN is recommended for new uncorrelated-rate analyses.

The dispatcher is `edges_make_ultrametric`. Automatic lambda estimation, cross-family selection, automatic category-count selection, PHIIC, and discrete-Gamma fitting are not exposed. V18 showed that per-tree terminal-edge CV can retain broad lambda and chronogram uncertainty, so correlated and UCLN users must supply lambda and report sensitivity across scientifically plausible values.

All methods accept finite, nonnegative additive branch lengths; expected substitutions per site are common but not required. Calibration values establish the returned time unit. With no calibrations, root age is one and results are relative times and rates.

## Current evidence

- [V7](README-v7.md): strict-clock numerical and recovery validation.
- [V10](README-v10.md): discrete chronos-compatibility finalization; discrete-Gamma retirement.
- [V12](README-v12.md): fixed-lambda UCLN validation.
- [V16](README-v16.md): fixed-lambda correlated validation, including exact-zero branches.
- [V17](README-v17.md): paired ToyTree/`ape::chronos` reliability and accuracy benchmark.
- [V18](README-v18.md): matched per-tree lambda-identifiability study and decision not to expose automatic lambda estimation.
- [Final report](final-report/REPORT.md): deterministic synthesis of the release evidence.

## Historical workflows

Superseded runners and rejected algorithms are not maintained in the active source tree. The [archive manifest](archive/README.md) pins the exact pre-cleanup commit and gives worktree and single-file recovery commands. Results, configurations, environment records, and version-specific design notes remain here as evidence. This avoids silently changing historical studies while keeping unsupported algorithms out of the installed package.

## Reproduction conventions

Each retained result records its configuration, seed stream, environment, and source hash. Recreate historical studies from the archive commit, not by combining an old configuration with current production code. The final report generator reads committed compact summaries and result tables, never reruns expensive fits.
