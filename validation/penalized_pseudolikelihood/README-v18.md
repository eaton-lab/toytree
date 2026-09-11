# V18: matched per-tree lambda identifiability

## Final decision

V18 did not support exposing automatic lambda estimation for either the fixed-lambda `correlated` or `uncorrelated_lognormal` model. ToyTree requires a user-supplied lambda and recommends reporting chronogram sensitivity across scientifically plausible values. No confirmation run was authorized.

The 64-dataset-per-model pilot scored every dataset and produced valid, stable selected fits, but point selection remained insufficiently identified:

| Metric | Correlated | UCLN |
|---|---:|---:|
| Grid-boundary selection | 0.234 | 0.281 |
| Selected/oracle age-RMSE ratio, median | 1.120 | 1.038 |
| Selected/oracle age-RMSE ratio, p90 | 2.387 | 1.245 |
| Supported chronogram spread, median | 0.140 | 0.046 |
| Supported chronogram spread, p90 | 0.459 | 0.103 |

Correlated failed the boundary, p90 recovery, and both chronogram-spread gates. UCLN passed its recovery and spread gates but failed the prespecified boundary-selection gate. Its stronger result does not overcome the core design question: a generally exposed point estimator should be dependable without knowing which simulated regime generated a user's tree.

## Frozen design

The pilot compared matched correlated and UCLN simulations at 24 and 48 tips, log-rate sigma 0.3 and 0.6, root-only or root-plus-three internal interval calibrations, expected or continuous-Gamma branch observations, and four replicates. The 17-candidate lambda grid spanned `1e-4` through `1e4`. Each terminal branch was omitted from initialization and the objective; fold columns were resampled as paired units 2,000 times. Selection uncertainty was evaluated together with oracle chronogram recovery and the spread among supported full-tree fits.

The compact machine-readable outcome is [summary-v18-pilot.json](v18/summary-v18-pilot.json). The 52 MB raw result was removed from the current checkout to keep Git artifacts manageable. Its source commit, blob ID, SHA-256, byte count, and exact `git show` recovery command are recorded in that summary and the [archive manifest](archive/manifest.json). The historical runner and test are likewise available at the pinned archive commit; they are intentionally not maintained against the final production API.
