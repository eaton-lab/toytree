<div class="nb-md-page-hook" aria-hidden="true"></div>

# Make trees ultrametric

ToyTree provides a fast edge-extension method and five branch-length pseudolikelihood chronogram models. Choose the model from its biological rate assumptions. Terminal-edge cross-validation is provided only to select **lam** within the correlated-rate model; it is not a cross-family model selector. PHIIC is intentionally not calculated.


## Models

- **clock** fits one rate shared by all branches. It has no rate penalty.
- **discrete** is a branchwise finite mixture. Every branch likelihood is independently integrated over an explicitly chosen number of ordered rate categories with simplex-constrained weights. Categories are not persistent assignments to branches, and this model has no rate penalty.
- **relaxed** reproduces the non-correlated `ape::chronos` model. It compares the empirical distribution of raw branch rates with a Gamma distribution whose shape is the mean raw rate and scale is one. This penalty depends on the chosen time unit.
- **uncorrelated_lognormal** estimates one rate per branch and penalizes summed squared deviations of log rates from their profiled mean. It is a penalized/MAP-like iid-lognormal model, not a marginalized Bayesian UCLN likelihood. Its penalty is invariant to a common scaling of time and rates.
- **correlated** penalizes summed squared differences between parent and child log-rates. Basal log-rates are penalized around a profiled common root log-rate, so the tree remains connected at the root. This penalty is invariant to a common scaling of all rates.

The lognormal and correlated penalties are sums rather than means, so a fixed **lam** has the same per-contrast interpretation as tree size changes. Under the lognormal interpretation, `lam = 1 / (2 * sigma_log**2)` for a fixed log-rate standard deviation and profiled mean. The chronos-relaxed penalty is a distribution-matching penalty, not a local smoothing penalty.


## Calibrations and scale

Calibrations map a selector that resolves to exactly one internal node to either a fixed age or a finite minimum-maximum interval. Ages must be non-negative. Tip calibrations are rejected because heterochronous tips are not implemented. Finite ancestor maxima are propagated through descendants during optimization rather than checked only after fitting.

When no calibration is supplied, the root age is fixed to 1.0 and the result is a relative-time chronogram. Penalized models require an explicit positive **lam**. The discrete model requires one positive integer **ncategories** value no greater than the number of branches.

Input phylogram branches must remain in expected substitutions per site. Years, millions of years (Myr), and generations are possible units for calibrations and estimated elapsed times; they are not alternative units for the input branches. If the same root calibration is written as `10` Myr or `10_000_000` years, an invariant model returns the same relative chronogram: absolute ages multiply by `1e6`, rates divide by `1e6`, and the penalty is unchanged. Its rate units change from substitutions/site/Myr to substitutions/site/year. A calibration expressed in generations similarly produces rates in substitutions/site/generation.

`uncorrelated_lognormal` and `correlated` have this invariance at the same numeric **lam**. The raw-rate Gamma-CDF penalty in `relaxed` does not: changing Myr to years changes both the mean-rate shape parameter and Gamma CDF values, so normalized node ages may change rather than merely rescaling. Use one consistent time unit for chronos-compatible analyses and reassess **lam** if that unit changes.


## Statistical model and validation scope

The observation model is a fractional-Poisson branch-length pseudolikelihood: each observed branch length is treated as a non-negative continuous Poisson-like observation with mean equal to elapsed time multiplied by rate. Input distances must therefore represent substitutions per site. They must not be support values, coalescent times, raw mutation counts, or unrelated edge weights. No alignment length or branch-length uncertainty is used.

The implementations are covered by numerical parity or objective-definition tests, calibration-domain and optimizer tests, and model-matched simulation recovery. The `relaxed` objective and fitted solution basin are pinned against `ape::chronos` 5.8-1; this establishes compatibility with that convention, not time-unit invariance.

`uncorrelated_lognormal` is retained because it has a distinct validated use case. In a separately seeded 200-dataset iid-lognormal confirmation with noisy count observations and sparse calibrations, 99% of fits converged, median root-normalized internal-age MAE was 0.056, absolute age bias was 0.009, and the paired-bootstrap upper 95% error ratio versus `relaxed` was 0.217. In 100 lower-noise simulations with internal ages fixed at truth, all fits converged and median log-rate Spearman correlation was 0.948. These tests support UCLN when independent lognormal rate variation or time-unit invariance is required.

The chronos-compatible `relaxed` objective should be chosen for parity with that established convention, not because it dominated UCLN in ToyTree's simulations. In the sparse-calibration iid-Gamma count confirmation it converged in 88.5% of fits and had median normalized age MAE 0.163; its raw-rate penalty is intrinsically unit-sensitive. Independent branch rates and free internal ages can still be weakly identifiable, so additional calibrations can materially improve rate and age recovery. Validation does not cover topology error, calibration-model misspecification, heterochronous tips, or branch-length uncertainty from a particular sequence-analysis pipeline.


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

Choose the clock family from its assumptions: strict clock for one shared rate, discrete for a user-chosen finite branchwise mixture, correlated for ancestor-descendant autocorrelation, `uncorrelated_lognormal` for independent lognormal rates or time-unit invariance, and `relaxed` when reproducing the `ape::chronos` Gamma-CDF convention. Merely having a calibration does not favor one independent-rate model over the other. Neither PHIIC nor terminal-edge prediction identifies the family or the discrete **ncategories** value. For the correlated model, `tree.mod.edges_make_ultrametric_correlated_lambda_cv(...)` performs deterministic leave-one-terminal-edge-out prediction over a supplied **lam** grid, selects the minimum mean Pearson score, refits the selected value, and warns when the minimum lies at a grid boundary. Exact score ties favor the larger **lam**.

PHIIC is omitted deliberately. The former ToyTree expression matched neither the optimized penalized objective nor the distinct criterion returned by `ape::chronos`. Paradis (2013) proposed PHIIC for penalized-likelihood model selection, so it is not invalid merely because it differs from the fitting objective, but it has not been validated for ToyTree's modified log-rate penalties or as a lambda selector here. Exact objective parity with `ape::chronos` does not by itself justify exposing PHIIC.

Inspect **converged**, **optimizer_message**, and the per-start metadata when requesting **full=True**. Full results declare `observation_model="fractional_poisson"` and `branch_length_units="substitutions_per_site"`, and report `pseudologlik` plus `penalized_pseudologlik`. Multiple starts perturb both rates and internal ages. Discrete fits default to four starts based on the optimizer diagnostic; other methods default to one unless `nstarts` is supplied.



```python
selected = tree.mod.edges_make_ultrametric_correlated_lambda_cv(
    lambdas=[0.01, 0.1, 1.0, 10.0],
    calibrations=calibrations,
    seed=123,
)
selected["selected_lam"], selected["mean_score"]

```
