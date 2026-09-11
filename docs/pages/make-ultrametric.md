<div class="nb-md-page-hook" aria-hidden="true"></div>

# Make trees ultrametric

ToyTree provides a fast edge-extension method and five branch-length pseudolikelihood chronogram models. Choose the model from its biological rate assumptions. Correlated and UCLN fits require a user-supplied **lam**; automatic lambda estimation is intentionally not exposed because development studies found broad supported ranges for individual trees. PHIIC is intentionally not calculated.


## Models

- **clock** fits one rate shared by all branches. It has no rate penalty. The shared rate has an exact conditional estimate for any feasible chronogram, so ToyTree profiles it analytically and numerically optimizes only free node ages.
- **discrete** is the `ape::chronos`-compatible branchwise finite mixture. Every branch likelihood is independently integrated over an explicitly chosen number of ordered rate categories with simplex-constrained weights. Categories are not persistent assignments to branches, and this model has no rate penalty. Its fractional-Poisson working likelihood is sensitive to the numeric scale of input branches; it is retained for compatibility. Zero-rich data can place branch times or mixture components on a boundary, which is reported explicitly.
- **relaxed** is provided only for objective parity with the non-correlated `ape::chronos` model. It compares the empirical distribution of raw branch rates with a Gamma distribution whose shape is the mean raw rate and scale is one. ToyTree begins from a profiled strict-clock chronogram to avoid poor topology-only basins. This penalty depends on the chosen calibration time unit, and different chronograms can have nearly equal objective values; for new uncorrelated-rate analyses, prefer `uncorrelated_lognormal`.
- **uncorrelated_lognormal** estimates one rate per branch and penalizes summed squared deviations of log rates from their profiled mean. It is ToyTree's recommended model for continuous uncorrelated rates. It is a penalized/MAP-like iid-lognormal model, not a marginalized Bayesian UCLN likelihood, and its penalty is invariant to a common rescaling of rates caused by changing calibration time units. For each candidate chronogram, conditional log rates are solved before node ages are optimized directly under linear ancestry and calibration constraints. Four independent starts are used by default.
- **correlated** penalizes summed squared differences between parent and child log-rates. Basal log-rates are penalized around a profiled common root log-rate, so the tree remains connected at the root. Its penalty is invariant to a common rescaling of rates caused by changing calibration time units.

The lognormal and correlated penalties are sums rather than means, so a fixed **lam** has the same per-contrast interpretation as tree size changes. Under the lognormal interpretation, `lam = 1 / (2 * sigma_log**2)` for a fixed log-rate standard deviation and profiled mean. Passing **lam** therefore fixes the assumed log-rate dispersion; it does not estimate **sigma_log** or select **lam** from the tree. With `full=True`, `implied_sigma_log = sqrt(1 / (2 * lam))` reports that deterministic interpretation. The chronos-relaxed penalty is a distribution-matching penalty, not a local smoothing penalty.

### Release status

| Workflow | Status | Supported scope |
| --- | --- | --- |
| `clock` | Validated | One shared rate |
| `discrete` | Validated compatibility | `ape::chronos` branchwise finite mixture with an explicit **ncategories** |
| `uncorrelated_lognormal` | Validated, with a zero-rich-data condition | Supplied **lam** and positive continuous additive branches; zero-rich fits must pass reported diagnostics |
| `correlated` | Validated | Supplied **lam** |
| `relaxed` | Compatibility only | Reproducing the `ape::chronos` Gamma-CDF objective; prefer UCLN for new analyses |

There is no public automatic lambda selector, cross-family model selector, automatic discrete-category selector, PHIIC, or discrete-Gamma workflow. The branch-length pseudolikelihood is a stated statistical model rather than a blanket experimental designation; workflow-specific assumptions and exclusions still apply.


## Fit usability and failure behavior

Every model returns a standardized **fit_usable** Boolean and
**failure_reasons** list when **full=True**. A fit is unusable if the optimizer
did not converge or if multistart diagnostics explicitly mark the solution as
unstable. Stability that was not assessed is not a failure. A converged
`discrete` boundary optimum is also not a failure by itself: it indicates that
the fitted data support fewer effective categories than requested.

The default tree-only call is fail-closed. It raises `ToytreeError` instead of
returning an unusable candidate and directs the caller to rerun with
**full=True** for diagnostics. Full mode returns the candidate tree even on
failure, but **fit_usable** remains false. With **inplace=True**, the source tree
is modified only after a fit passes this usability check; a failed fit leaves it
unchanged.


## Calibrations and scale

Calibrations map a selector that resolves to exactly one internal node to either a fixed age or a finite minimum-maximum interval. Ages must be non-negative. Tip calibrations are rejected because heterochronous tips are not implemented. Finite ancestor maxima are propagated through descendants during optimization rather than checked only after fitting.

When no calibration is supplied, the root age is fixed to 1.0 and the result is a relative-time chronogram. Penalized models require an explicit positive **lam**. `discrete` requires one positive integer **ncategories** value no greater than the number of branches.

Input phylogram branches may be expressed in any finite, non-negative additive units for which branch length can be modeled as elapsed time multiplied by a rate. Expected substitutions per site are common, but the implementation does not require those units. If branch lengths are substitutions per site and calibrations are in millions of years (Myr), fitted rates are substitutions/site/Myr. If branch lengths instead represent mutations, generations, or another additive quantity, rates retain those input units in the numerator.

Calibration ages define the output time unit. For example, calibrations in years, Myr, or generations return a chronogram in years, Myr, or generations and rates in input-branch units per year, Myr, or generation. Writing the same root calibration as `10` Myr or `10_000_000` years causes a calibration-time-unit-invariant model to multiply ages by `1e6`, divide rates by `1e6`, and preserve the normalized chronogram and penalty. Choosing biologically meaningful calibration units also makes downstream quantities easier to interpret: a Brownian trait rate can be reported in trait-units squared per Myr, and a discrete-trait transition rate in transitions per Myr.

Without calibrations, ToyTree fixes the root age to `1.0`. The returned branch lengths are then relative, dimensionless time with every root-to-tip path summing to one; absolute divergence times are not identified. Fitted rates have input-branch units per relative root-age unit. This normalized chronogram is useful for shape comparisons and scale-free analyses, but downstream rates acquire absolute interpretations only after the tree is calibrated.

The clock and discrete models are calibration-time-unit invariant because they have no rate penalty. The centered log-rate penalty in `uncorrelated_lognormal` and the log-rate-difference penalty in `correlated` are also invariant to the corresponding common rate rescaling, so the same numeric **lam** can be retained. Only the raw-rate Gamma-CDF penalty in `relaxed` lacks this property: changing Myr to years changes both its mean-rate shape parameter and Gamma CDF values, so normalized node ages may change rather than merely rescaling. Use one consistent calibration time unit for chronos-parity analyses and reassess **lam** if that unit changes.


## Statistical model and validation scope

All supported models use a fractional-Poisson branch-length pseudolikelihood: each observed branch length is treated as a non-negative continuous Poisson-like observation with mean equal to elapsed time multiplied by rate. It accepts any consistent additive branch-length unit; values must not be support values or unrelated edge weights. No model uses alignment length or branch-length uncertainty automatically.

Changing the numeric unit of the input branch lengths is distinct from changing the calibration time unit. The strict clock transforms exactly by rescaling its single fitted rate. For `discrete`, multiplying every input branch length changes the numerical scale and effective information of its fractional-Poisson mixture, so normalized ages, relative rates, and weights can change. Penalized fractional-Poisson models can require **lam** to be selected again after input-branch rescaling. Calibration-time-unit invariance instead holds observed branches fixed and rewrites the same calibration ages in another time unit.

The implementations are covered by numerical parity or objective-definition tests, calibration-domain and optimizer tests, and model-matched simulation recovery. The `relaxed` objective is pinned exactly against `ape::chronos` 5.8-1, but its fitted solution basin is not. The analytic relaxed-penalty gradient supplied by `chronos` omits the dependence of the Gamma shape on the mean rate, so an ape fit need not be stationary under the objective it reports. ToyTree instead optimizes that shared objective from a data-informed strict-clock start. Compatibility here means objective parity, not identical fitted chronograms or calibration-time-unit invariance.

The strict-clock estimator is validated and is no longer experimental within this documented scope. Its conditional rate and analytic age gradient are tested directly, and its fitted solution is pinned against `ape::chronos` 5.8-1. In an independently seeded confirmation of 360 datasets spanning 12, 48, and 96 tips, two calibration regimes, and noiseless, Gamma-noise, and lognormal-noise branches, all 720 primary fits converged and all release gates passed. Median root-normalized internal-age MAE was `1.84e-7` without noise and `0.00727` with noise; maximum one-start versus four-start age disagreement was `5.45e-6`. This validates optimization and recovery when the strict-clock assumption holds. It does not model topology error or uncertainty in branch lengths estimated from sequence data.

The correlated estimator at a prespecified **lam** is also validated and is no longer experimental within this documented scope. V16 tested 540 independently seeded datasets spanning 24, 48, and 96 tips, two calibration regimes, three correlated-rate innovation scales, three branch-observation processes, and exact-zero branches. All 2,160 primary fits converged, and every frozen recovery, bias, calibration, optimizer-stability, objective-parity, gradient, and time-unit gate passed across 2,214 total fit tasks. Median root-normalized internal-age MAE was `0.0374`, its 90th percentile was `0.0705`, maximum absolute age bias was `0.0101`, and median fixed-age rate Spearman correlation was `0.942`. This validates fitting and recovery under model-matched correlated rates when **lam** is supplied; it does not validate automatic selection of **lam**, topology error, calibration misspecification, or branch-length uncertainty.

`uncorrelated_lognormal` at a prespecified **lam** is validated and is no longer experimental for positive continuous additive branch lengths within the tested scope. It is ToyTree's recommended model for continuous uncorrelated rates. V12 validates its objective, optimization, calibration-time-unit invariance, and model-matched recovery. The 40-dataset V11 failure replay and 72-dataset pilot passed every prespecified gate. All frozen gates passed when the confirmation was rescored over its 360 positive expected-branch and continuous-Gamma datasets: all fits converged, median root-normalized internal-age MAE was `0.0212`, maximum four-versus-eight-start relative objective gap was `1.59e-14`, and maximum normalized chronogram difference was `9.54e-8`. Across the full independently seeded 540-dataset confirmation, median fixed-age rate Spearman correlation was `0.833` overall and `0.913` in identifiable controls. Three of 180 high-variance fractional-Poisson datasets with many exact zeros failed at least one uniqueness/parity gate: the maximum four-versus-eight-start relative objective gap was `2.68e-4` and the maximum normalized chronogram difference was `0.153`. Thus zero-rich UCLN fits are supported conditionally, not automatically: use them for inference only when `converged`, `best_basin_replicated`, and `solution_stable` are all true.

Zero-length input branches are valid observations and are retained exactly; ToyTree does not silently replace them by a positive floor. Full UCLN results report the total zero count and fraction, terminal and internal zero counts, the minimum positive length, and its ratio to the positive median. Four starts are requested by default; if they find the winning basin only once, one additional feasible perturbed start tests basin replication. Full results report `evaluated_starts` and `basin_confirmation_run`. Many zeros can weaken age-rate identifiability. Consider collapsing an internal zero edge only when it represents an unresolved relationship; retaining or collapsing it is a modeling choice.

The chronos-compatible `relaxed` objective is implemented only for parity with that established convention. It is not recommended over UCLN for new uncorrelated-rate analyses. In a 36-dataset V17 development pilot under matched iid-Gamma rates, the strict-clock initialization converged with valid calibrations in every fit and reduced median normalized age MAE from `0.396` with the former topology-only start to `0.052`; ape's median was `0.109` among its 31 eligible fits. Every ToyTree fit reached an objective at least as high as ape, and the paired mean age-MAE improvement over ape was `0.0666` with a 95% bootstrap interval of `0.0542` to `0.0795`. This supports the initialization change but does not upgrade the model beyond compatibility-only status. Its raw-rate penalty is intrinsically sensitive to the calibration time unit, and independent branch rates plus free internal ages can remain weakly identifiable. Additional calibrations can materially improve rate and age recovery. Validation does not cover topology error, calibration-model misspecification, heterochronous tips, or branch-length uncertainty from a particular sequence-analysis pipeline.

The hardened `discrete` optimizer uses ordered rates, simplex weights, fixed-age EM initialization, analytic gradients, an authoritative final joint fit, bounded fallback optimization, and cross-start chronogram diagnostics. Numerical convergence is reported separately from whether all requested mixture categories are supported. Exact objective and fitted-solution parity with `ape::chronos`, together with calibration, boundary, and optimizer regression tests, validate `discrete` within its documented compatibility scope.


## Examples



```python
import toytree

toytree.set_log_level("WARNING")
tree = toytree.tree("((a:0.2,b:0.3):0.4,(c:0.5,d:0.6):0.2);")
calibrations = {-1: 1.0}

```


```python
clock = tree.mod.edges_make_ultrametric(
    method="clock", calibrations=calibrations, full=True
)
clock["tree"].is_ultrametric(), clock["pseudologlik"]

```


```python
discrete = tree.mod.edges_make_ultrametric(
    method="discrete",
    calibrations=calibrations,
    ncategories=2,
    full=True,
)
discrete["rates"], discrete["weights"]

```


```python
relaxed = tree.mod.edges_make_ultrametric(
    method="relaxed",
    calibrations=calibrations,
    lam=0.5,
    full=True,
)
relaxed["penalty_model"], relaxed["scale_invariant"]

```


```python
uncorrelated_lognormal = tree.mod.edges_make_ultrametric(
    method="uncorrelated_lognormal",
    calibrations=calibrations,
    lam=0.5,
    full=True,
)
uncorrelated_lognormal["penalty_model"], uncorrelated_lognormal["implied_sigma_log"]

```


```python
correlated = tree.mod.edges_make_ultrametric(
    method="correlated",
    calibrations=calibrations,
    lam=0.5,
    full=True,
)
correlated["penalty_model"], correlated["profiled_root_rate"]

```

## Choosing settings

Choose the clock family from its assumptions: strict clock for one shared rate, correlated for ancestor-descendant autocorrelation, and `uncorrelated_lognormal` for continuous independent lognormal rates. Retain `discrete` when `ape::chronos` fractional-Poisson mixture compatibility is required. Use `relaxed` only when reproducing the `ape::chronos` Gamma-CDF convention is specifically required. Neither PHIIC nor terminal-edge prediction identifies the family or the discrete **ncategories** value.

!!! note "Lambda is specified, not estimated"
    ToyTree does not expose an automatic lambda estimator for either `correlated` or `uncorrelated_lognormal`. Per-tree terminal-edge cross-validation was investigated but frequently supported broad lambda ranges and materially different chronograms. Supply **lam** from external knowledge and report sensitivity across scientifically plausible values. For `uncorrelated_lognormal`, **lam** fixes dispersion through `lam = 1 / (2 * sigma_log**2)`.

Choose the `discrete` **ncategories** value a priori from the scientific model or compare sensitivity across explicitly reported values; ToyTree does not automatically select it.

PHIIC is omitted deliberately. The former ToyTree expression matched neither the optimized penalized objective nor the distinct criterion returned by `ape::chronos`. Paradis (2013) proposed PHIIC for penalized-likelihood model selection, so it is not invalid merely because it differs from the fitting objective, but it has not been validated for ToyTree's modified log-rate penalties or as a lambda selector here. Exact objective parity with `ape::chronos` does not by itself justify exposing PHIIC.

Inspect **converged**, **optimizer_message**, **projected_gradient_max_abs**, **solution_stable**, and the per-start metadata when requesting **full=True**. UCLN results additionally report **profile_rate_converged**, **rate_gradient_max_abs**, **best_basin_replicated**, and zero-length branch diagnostics. A single best-basin replicate is not evidence of a stable optimum. Discrete results additionally report **mixture_identified**, **effective_ncategories**, **boundary_solution**, **boundary_reasons**, and **optimum_replicated**. A converged boundary fit can be numerically valid while showing that the requested K-category mixture is not fully identified. Full results declare their observation model and report `pseudologlik` plus `penalized_pseudologlik`. Multiple starts perturb rates, internal ages, and mixture weights. `discrete` defaults to eight starts and `uncorrelated_lognormal` defaults to four; other methods default to one unless `nstarts` is supplied.
