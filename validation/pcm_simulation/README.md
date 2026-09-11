# PCM trait-simulation hardening and validation

This directory defines the implementation and release-validation contract for
trait simulation in `toytree.pcm`. It is developer-facing and intentionally is
not included in the documentation navigation.

## Goals

The simulation API should serve two related purposes:

1. provide useful, statistically well-defined trait simulators for users; and
2. generate known-truth data for validating comparative methods in
   `pcm.phylolinalg` and `pcm.traits`.

Every public simulator must therefore document its probability model, parameter
units, root condition, tree requirements, random-number behavior, returned data
shape, and directly compatible fitting methods. Tests of output shape and seeded
values are necessary but are not sufficient: each distribution must also be
checked against an independently calculated expectation.

## Public API and compatibility policy

The recognizable method names and single-realization return types are retained:

| Method | Default return | Primary downstream methods |
| --- | --- | --- |
| `simulate_continuous_trait` | node-indexed `Series` | `fit_continuous_ml`, PIC, Blomberg's K |
| `simulate_multivariate_continuous_trait` | node-indexed `DataFrame` | PGLS predictor/response workflows |
| `simulate_discrete_trait` | node-indexed `Series` | `fit_discrete_ctmc`, discrete ASR |
| `simulate_pgls_trait` | tip-name-indexed `Series` | `pgls`, `pgls_matrix` |
| `simulate_pglm_trait` | tip-name-indexed `Series` or latent `DataFrame` | `pglm` |
| `simulate_stochastic_map` | `PCMStochasticMapResult` | conditional CTMC history summaries |

The existing methods continue to simulate one realization per call. Replicate
studies use independent `SeedSequence` children rather than changing a method's
return type according to an `nreplicates` argument. Inputs accept an integer,
`numpy.random.Generator`, `numpy.random.SeedSequence`, or `None`; Booleans and
negative integer seeds are rejected.

Zero-length branches are valid and produce deterministic transitions. Negative
or nonfinite branch lengths are invalid. A zero diffusion or residual variance
is a valid deterministic boundary. Multivariate diffusion matrices may be
positive semidefinite, including singular matrices, but must not be indefinite.

When `tips_only=True`, continuous and discrete simulators return rows in ToyTree
tip-index order. With `inplace=True`, those tip values are stored and internal
nodes receive missing values. All-node output remains indexed by numeric node
index. These conventions preserve current callers and are accepted by the named
inference methods.

## Continuous models

### Brownian motion

For an edge of duration `t`,

```text
X_child | X_parent ~ Normal(X_parent, sigma2 * t).
```

For multiple traits, `sigma2` is replaced by a diffusion matrix `R`. Conditional
on a fixed root state, tip covariance is the root-to-MRCA shared-time matrix
Kronecker-multiplied by `R`.

### Ornstein-Uhlenbeck

For one trait with optimum `theta`,

```text
E[X_child | X_parent] = theta + exp(-alpha*t) * (X_parent - theta)
Var[X_child | X_parent] = sigma2 * (1 - exp(-2*alpha*t)) / (2*alpha).
```

The `alpha=0` limit is Brownian motion. The public `optimum=None` default means
`theta=root_state`, preserving the current conditional-root model and matching
`fit_continuous_ml`. An explicit optimum supports a more general conditioned OU
simulation. Regime-specific optima are child-edge keyed like other regime
parameters.

For multiple traits, the transition is `exp(-A*t)` and covariance is the finite
time integral of `exp(-A*s) R exp(-A.T*s)`. The selection matrix must have
eigenvalues with nonnegative real components; zero components retain BM limits.

### Early burst

The instantaneous diffusion rate is `sigma2 * exp(r*t)` from the root, giving
branch variance

```text
sigma2 * (exp(r*t_child) - exp(r*t_parent)) / r,
```

with the exact Brownian limit at `r=0`. Multivariate EB uses the corresponding
pairwise integrated covariance implied by `R` and the per-trait `r` vector.

### Continuous validation gates

- empirical branch means and variances agree with analytic BM, OU, and EB
  transitions within Monte Carlo confidence bounds;
- empirical tip covariance agrees with the tree covariance kernel;
- multivariate BM/OU/EB covariance agrees with independent matrix calculations;
- zero branch lengths and zero/singular diffusion terms are exact;
- invalid branches and indefinite covariance matrices are rejected;
- seeded calls and spawned streams are reproducible;
- BM/OU/EB parameters are recoverable by `fit_continuous_ml` over replicated
  datasets without material bias under identifiable designs;
- BM simulations yield standardized PIC behavior and Blomberg's K near its BM
  expectation over replicates.

Regime-specific models are validated as simulation models. They are not claimed
to be recoverable by the current single-regime `fit_continuous_ml` implementation.

## Discrete CTMC models

Off-diagonal Q entries are direct transition rates:

```text
q_ij = rate_scalar * relative_rates[i, j]
q_ii = -sum(j != i, q_ij)
P(t) = expm(Q*t).
```

ER shares one off-diagonal rate, SYM shares rates between each state pair, and
ARD permits each direction to differ. The stationary distribution is derived
from Q. `root_prior=None` uses that distribution when it is unique. For a
reducible ER or SYM model, the canonical uniform stationary prior is used; a
reducible ARD model requires an explicit prior because Q does not select a
unique default. A supplied root prior changes root sampling but does not change
Q.

State labels must be unique, nonmissing, hashable, and either all strings or all
non-Boolean integers. Their entered order defines Q row/column order and must be
carried into fitting so custom labels cannot silently reorder an ARD model.

### Discrete validation gates

- empirical single-edge transition frequencies agree with `expm(Q*t)`;
- empirical root frequencies agree with the resolved root prior;
- long-time frequencies approach the stationary distribution for irreducible Q;
- reducible ARD matrices require an explicit root prior, while zero-rate ER/SYM
  matrices use or override their canonical uniform prior correctly;
- ER, SYM, and ARD constraints and parameter counts are exact;
- custom state-label order survives simulation and fitting;
- fitted ER/SYM/ARD rates recover generating rates over replicated,
  sufficiently informative trees;
- no user validation depends on Python `assert` statements.

## PGLS response simulation

The generative model is

```text
Y = X beta + epsilon,
epsilon ~ MVN(0, sigma2 * V_lambda).
```

As in `pgls` and `pgls_matrix`, the working tree is scaled to root height 1
before applying Pagel's lambda. Consequently, `sigma2` is residual variance on
the normalized-tree covariance scale, not on the input tree's original time
scale. Predictor rows are built by Patsy and output is indexed by retained tip
names after missing-row removal.

Validation covers the analytic residual covariance, exact `sigma2=0` behavior,
Patsy column alignment, numeric and categorical predictors, row filtering, and
replicated recovery of beta, lambda, and sigma2.

## PGLM response simulation

The simulator uses a latent phylogenetic process,

```text
eta = X beta + epsilon,
epsilon ~ MVN(0, sigma2 * V_lambda),
mu = inverse_link(eta),
Y | mu ~ selected response family.
```

Supported paths are binomial-logit, Poisson-log, negative-binomial-log,
Gamma-log/inverse, and beta-logit. Family dispersion parameters use the same
definitions as `_glm_families.py`.

The simulator is an exact generator for this stated latent model. The current
`pglm` fitter is a pruning-based IRLS approximation rather than the exact
integrated likelihood of that latent phylogenetic GLMM. Validation must therefore
report empirical bias, convergence, and coverage instead of claiming algebraic
estimator parity. Large systematic recovery failures belong to the later
inference-hardening phase rather than being hidden by changes to the generator.

## Stochastic mapping

Stochastic mapping is conditional posterior simulation rather than a generative
trait simulator. It remains in `pcm.sim` but is documented separately. It must:

- consume observed scalar tip states and a fitted CTMC result;
- sample the root posterior and descendant states jointly from parent to child;
- simulate conditioned histories from parent endpoints to child endpoints;
- retain uniformization as the default engine and rejection as an alternative;
- use strict positive-integer validation for replicate and attempt counts; and
- produce reproducible segment, event, dwell, transition, and node-state tables.

## Implementation milestones

1. Shared validation/RNG/output/regime/formula infrastructure and dead-code
   removal.
2. Continuous scalar and multivariate correctness plus analytic tests.
3. Discrete CTMC correctness, explicit state ordering, and recovery tests.
4. PGLS/PGLM consolidation and recovery validation.
5. Stochastic-mapping input consistency.
6. Fixed-seed quick and confirmation validation scripts with recorded evidence.
7. Source-notebook repair, paired-page regeneration, focused and broad tests.

## Replicated recovery study

`run_validation.py` provides two deterministic, task-parallel study modes:

```bash
python validation/pcm_simulation/run_validation.py --mode quick --ncores 4
python validation/pcm_simulation/run_validation.py --mode confirmation --ncores 8
```

The quick mode uses 16 independent 64-tip trees. The confirmation mode uses
100 independent 128-tip trees. Each replicate simulates and refits BM, OU, EB,
ER, ARD, PGLS, and binomial PGLM data; it also checks standardized PICs and
Blomberg's K. Seeds are spawned deterministically from the recorded base seed,
and each replicate is an independent process task.

The checked-in `results-confirmation.json` passed every predeclared release
gate. Across 100 datasets, all BM/OU/EB and PGLS fits converged. Median ratios
of estimated to generating diffusion variance were 1.002 for BM, 1.173 for OU,
and 0.786 for EB; median OU-alpha and EB-r errors were 0.184 and 0.157. BM
standardized PIC variance was 1.009 times its expectation and median Blomberg's
K was 0.944. PGLS recovered its coefficients without material average bias,
with median variance ratio 0.998 and median lambda error -0.002. ER and ARD
preserved the entered state order and their median rate ratios were close to
one.

The complete distributions are important. A single discrete character can
provide very little information about a CTMC rate, so ER/ARD rate estimates
have a long upper tail despite good median recovery. OU alpha and diffusion
likewise show a correlated upper tail on individual datasets. These are
single-dataset inference-identifiability limitations, not failures of the
independently validated transition simulators. PGLM is reported separately as
diagnostic-only: its exact latent generator exposed modest attenuation in the
current approximate fitter (mean binomial intercept and slope errors 0.091 and
-0.092), which belongs to inference hardening rather than simulator repair.

The evidence files are intentionally compact: `results-quick.json` is the
development check and `results-confirmation.json` is the release record. They
store every per-replicate estimate, environment versions, configuration,
seeds, summaries, and gate outcomes without caches or large intermediate data.

Each milestone is committed and pushed only after its focused tests pass. Public
API breaks outside the compatibility rules above require explicit review. The
developer README itself must remain absent from `mkdocs.yml`.

## Completion criteria

This effort is complete when:

- all public simulator docstrings fully specify every parameter and model unit;
- analytic and fixed-seed distributional gates pass;
- named inference methods accept simulator outputs without manual relabeling;
- replicated recovery results and known limitations are recorded;
- focused PCM tests and relevant documentation checks pass;
- the full applicable suite has no new failures; and
- the branch contains coherent commits with no unexplained tracked changes.
