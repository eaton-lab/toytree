<div class="nb-md-page-hook" aria-hidden="true"></div>

# Make trees ultrametric

ToyTree provides a fast edge-extension method and six branch-length pseudolikelihood chronogram models. Choose the model from its biological rate assumptions. Terminal-edge cross-validation is provided only to select **lam** within the correlated-rate model; it is not a cross-family model selector. PHIIC is intentionally not calculated.


## Models

- **clock** fits one rate shared by all branches. It has no rate penalty. The shared rate has an exact conditional estimate for any feasible chronogram, so ToyTree profiles it analytically and numerically optimizes only free node ages.
- **discrete** is the `ape::chronos`-compatible branchwise finite mixture. Every branch likelihood is independently integrated over an explicitly chosen number of ordered rate categories with simplex-constrained weights. Categories are not persistent assignments to branches, and this model has no rate penalty. Its fractional-Poisson working likelihood is sensitive to the numeric scale of input branches; it is retained for compatibility.
- **discrete_gamma** is ToyTree's recommended finite-category model for new analyses. It uses a multiplicative Gamma observation model with a fixed within-category branch-length coefficient of variation, `branch_cv=0.1` by default. This makes its normalized chronogram, relative rates, and weights invariant to common rescaling of either input-branch or calibration-time units.
- **relaxed** is provided only for parity with the non-correlated `ape::chronos` model. It compares the empirical distribution of raw branch rates with a Gamma distribution whose shape is the mean raw rate and scale is one. This penalty depends on the chosen calibration time unit; for new uncorrelated-rate analyses, prefer `uncorrelated_lognormal`.
- **uncorrelated_lognormal** estimates one rate per branch and penalizes summed squared deviations of log rates from their profiled mean. It is ToyTree's recommended model for continuous uncorrelated rates. It is a penalized/MAP-like iid-lognormal model, not a marginalized Bayesian UCLN likelihood, and its penalty is invariant to a common rescaling of rates caused by changing calibration time units.
- **correlated** penalizes summed squared differences between parent and child log-rates. Basal log-rates are penalized around a profiled common root log-rate, so the tree remains connected at the root. Its penalty is invariant to a common rescaling of rates caused by changing calibration time units.

The lognormal and correlated penalties are sums rather than means, so a fixed **lam** has the same per-contrast interpretation as tree size changes. Under the lognormal interpretation, `lam = 1 / (2 * sigma_log**2)` for a fixed log-rate standard deviation and profiled mean. The chronos-relaxed penalty is a distribution-matching penalty, not a local smoothing penalty.


## Calibrations and scale

Calibrations map a selector that resolves to exactly one internal node to either a fixed age or a finite minimum-maximum interval. Ages must be non-negative. Tip calibrations are rejected because heterochronous tips are not implemented. Finite ancestor maxima are propagated through descendants during optimization rather than checked only after fitting.

When no calibration is supplied, the root age is fixed to 1.0 and the result is a relative-time chronogram. Penalized models require an explicit positive **lam**. Both discrete models require one positive integer **ncategories** value no greater than the number of branches.

Input phylogram branches may be expressed in any finite, non-negative additive units for which branch length can be modeled as elapsed time multiplied by a rate. Expected substitutions per site are common, but the implementation does not require those units. If branch lengths are substitutions per site and calibrations are in millions of years (Myr), fitted rates are substitutions/site/Myr. If branch lengths instead represent mutations, generations, or another additive quantity, rates retain those input units in the numerator.

Calibration ages define the output time unit. For example, calibrations in years, Myr, or generations return a chronogram in years, Myr, or generations and rates in input-branch units per year, Myr, or generation. Writing the same root calibration as `10` Myr or `10_000_000` years causes a calibration-time-unit-invariant model to multiply ages by `1e6`, divide rates by `1e6`, and preserve the normalized chronogram and penalty. Choosing biologically meaningful calibration units also makes downstream quantities easier to interpret: a Brownian trait rate can be reported in trait-units squared per Myr, and a discrete-trait transition rate in transitions per Myr.

Without calibrations, ToyTree fixes the root age to `1.0`. The returned branch lengths are then relative, dimensionless time with every root-to-tip path summing to one; absolute divergence times are not identified. Fitted rates have input-branch units per relative root-age unit. This normalized chronogram is useful for shape comparisons and scale-free analyses, but downstream rates acquire absolute interpretations only after the tree is calibrated.

The clock and both discrete models are calibration-time-unit invariant because they have no rate penalty. The centered log-rate penalty in `uncorrelated_lognormal` and the log-rate-difference penalty in `correlated` are also invariant to the corresponding common rate rescaling, so the same numeric **lam** can be retained. Only the raw-rate Gamma-CDF penalty in `relaxed` lacks this property: changing Myr to years changes both its mean-rate shape parameter and Gamma CDF values, so normalized node ages may change rather than merely rescaling. Use one consistent calibration time unit for chronos-parity analyses and reassess **lam** if that unit changes.


## Statistical model and validation scope

Most methods use a fractional-Poisson branch-length pseudolikelihood: each observed branch length is treated as a non-negative continuous Poisson-like observation with mean equal to elapsed time multiplied by rate. It accepts any consistent additive branch-length unit; values must not be support values or unrelated edge weights. The `discrete_gamma` model instead treats each strictly positive branch as Gamma distributed around the same mean. Its fixed `branch_cv` is within-category relative branch-length noise or estimation dispersion, not biological variation among category rates. No model uses alignment length or branch-length uncertainty automatically.

Changing the numeric unit of the input branch lengths is distinct from changing the calibration time unit. Multiplying every input branch length changes the numerical scale and effective information of the fractional-Poisson mixture, so `discrete` can change its normalized age, relative-rate, and weight estimates. The multiplicative Gamma density in `discrete_gamma` changes only by a data-only additive likelihood constant. ToyTree reports the equivalent scale-normalized score `log f(x) + log(x)`, so fitted rates rescale while its reported score, normalized chronogram, and weights remain unchanged. The strict clock also transforms exactly by rescaling its single fitted rate. Penalized fractional-Poisson models can require **lam** to be selected again after input-branch rescaling. Calibration-time-unit invariance instead holds observed branches fixed and rewrites the same calibration ages in another time unit.

The implementations are covered by numerical parity or objective-definition tests, calibration-domain and optimizer tests, and model-matched simulation recovery. The `relaxed` objective and fitted solution basin are pinned against `ape::chronos` 5.8-1; this establishes compatibility with that convention, not calibration-time-unit invariance.

The strict-clock estimator is validated and is no longer experimental within this documented scope. Its conditional rate and analytic age gradient are tested directly, and its fitted solution is pinned against `ape::chronos` 5.8-1. In an independently seeded confirmation of 360 datasets spanning 12, 48, and 96 tips, two calibration regimes, and noiseless, Gamma-noise, and lognormal-noise branches, all 720 primary fits converged and all release gates passed. Median root-normalized internal-age MAE was `1.84e-7` without noise and `0.00727` with noise; maximum one-start versus four-start age disagreement was `5.45e-6`. This validates optimization and recovery when the strict-clock assumption holds. It does not model topology error or uncertainty in branch lengths estimated from sequence data.

`uncorrelated_lognormal` is retained as ToyTree's recommended model for uncorrelated rates. In a separately seeded 200-dataset iid-lognormal confirmation with noisy count observations and sparse calibrations, 99% of fits converged, median root-normalized internal-age MAE was 0.056, absolute age bias was 0.009, and the paired-bootstrap upper 95% error ratio versus `relaxed` was 0.217. In 100 lower-noise simulations with internal ages fixed at truth, all fits converged and median log-rate Spearman correlation was 0.948. These tests support UCLN when independent lognormal rate variation is appropriate; unlike `relaxed`, its penalty is calibration-time-unit invariant.

The chronos-compatible `relaxed` objective is implemented only for parity with that established convention. It is not recommended over UCLN for new uncorrelated-rate analyses. In the sparse-calibration iid-Gamma count confirmation it converged in 88.5% of fits and had median normalized age MAE 0.163; its raw-rate penalty is intrinsically sensitive to the calibration time unit. Independent branch rates and free internal ages can still be weakly identifiable, so additional calibrations can materially improve rate and age recovery. Validation does not cover topology error, calibration-model misspecification, heterochronous tips, or branch-length uncertainty from a particular sequence-analysis pipeline.

The hardened discrete optimizers use ordered rates, simplex weights, analytic gradients, an authoritative final joint fit, retry handling, and cross-start chronogram diagnostics. `discrete` retains objective parity with `ape::chronos`; `discrete_gamma` is a new model whose release validation is prespecified separately. Until that confirmation passes, its recommendation describes its statistical formulation and unit behavior rather than a completed empirical validation claim.


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
discrete_gamma = tree.mod.edges_make_ultrametric(
    method="discrete_gamma",
    calibrations=calibrations,
    ncategories=2,
    branch_cv=0.1,
    full=True,
)
discrete_gamma["rates"], discrete_gamma["weights"]

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
uncorrelated_lognormal["penalty_model"], uncorrelated_lognormal["scale_invariant"]

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

Choose the clock family from its assumptions: strict clock for one shared rate, `discrete_gamma` for a user-chosen finite branchwise mixture, correlated for ancestor-descendant autocorrelation, and `uncorrelated_lognormal` for continuous independent lognormal rates. Retain `discrete` when `ape::chronos` fractional-Poisson mixture compatibility is required. Use `relaxed` only when reproducing the `ape::chronos` Gamma-CDF convention is specifically required. Neither PHIIC nor terminal-edge prediction identifies the family or the discrete **ncategories** value. For the correlated model, `tree.mod.edges_make_ultrametric_correlated_lambda_cv(...)` performs deterministic leave-one-terminal-edge-out prediction over a supplied **lam** grid, selects the minimum mean Pearson score, refits the selected value, and warns when the minimum lies at a grid boundary. Exact score ties favor the larger **lam**.

For `discrete_gamma`, `branch_cv` controls within-category relative observation dispersion. Estimate it from replicate or bootstrap branch-length estimates when those are available. Otherwise, report a sensitivity analysis across values such as `0.05`, `0.1`, `0.2`, and `0.3`; smaller values assert more precise branches. Do not interpret `branch_cv` as the variation among the fitted biological rate categories. Choose **ncategories** a priori from the scientific model or compare sensitivity across explicitly reported values; ToyTree does not automatically select it.

PHIIC is omitted deliberately. The former ToyTree expression matched neither the optimized penalized objective nor the distinct criterion returned by `ape::chronos`. Paradis (2013) proposed PHIIC for penalized-likelihood model selection, so it is not invalid merely because it differs from the fitting objective, but it has not been validated for ToyTree's modified log-rate penalties or as a lambda selector here. Exact objective parity with `ape::chronos` does not by itself justify exposing PHIIC.

Inspect **converged**, **optimizer_message**, **gradient_max_abs**, **solution_stable**, and the per-start metadata when requesting **full=True**. Full results declare their observation model and report `pseudologlik` plus `penalized_pseudologlik`. Multiple starts perturb rates, internal ages, and mixture weights. Both discrete fits default to four starts based on prior optimizer diagnostics; other methods default to one unless `nstarts` is supplied.



```python
selected = tree.mod.edges_make_ultrametric_correlated_lambda_cv(
    lambdas=[0.01, 0.1, 1.0, 10.0],
    calibrations=calibrations,
    seed=123,
)
selected["selected_lam"], selected["mean_score"]

```
