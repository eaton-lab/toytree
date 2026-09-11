<div class="nb-md-page-hook" aria-hidden="true"></div>

# Simulating trees and branch rates

The `toytree.rtree` subpackage separates four different simulation tasks: topology distributions, time-tree processes, coalescent genealogies, and rate processes applied to an existing time tree. Choose a method based on the random object you intend to simulate; a random topology is not automatically a diversification time tree.

| Task | Public API | Key result |
| --- | --- | --- |
| Random labeled topology | `random_topology` | Yule–Harding or uniform/PDA topology with arbitrary unit edges |
| Fixed example shape | `unittree`, `baltree`, `imbtree` | Ultrametric construction with a requested height |
| Reconstructed diversification tree | `birth_death_conditioned_tree` | Direct constant-rate birth–death draw conditioned on extant tip count and crown or origin age |
| Complete diversification history | `birth_death_process` | Forward event history with extinct lineages and stopping metadata |
| Population genealogy | `coalescent_tree` | Constant-size Kingman genealogy |
| Rates on a time tree | `simulate_branch_rates` | Strict, UCLN, or time-scaled ACLN phylogram with edge annotations |


## Random topology distributions

`random_topology` returns a rooted, labeled, bifurcating topology. `model="yule"` repeatedly splits a uniformly selected extant leaf and therefore samples the Yule–Harding distribution. `model="pda"` uses uniform edge insertion and samples the proportional-to-distinguishable-arrangements distribution, which is uniform over rooted labeled cladograms. PDA tends to produce more imbalanced trees than Yule.

Every real edge is assigned length 1. These lengths are placeholders: they do not represent elapsed time or expected substitutions. Labels are exchangeable by default (`randomize_labels=True`). Explicit labels must be unique after conversion to strings.



```python
import toytree

yule = toytree.rtree.random_topology(12, model="yule", seed=123)
pda = toytree.rtree.random_topology(12, model="pda", seed=123)

```

## Fixed example shapes

`unittree` starts from a Yule topology, gives all internal edges—including the two basal edges—the same construction length, extends terminal branches to the present, and rescales the result to `treeheight`. `baltree` and `imbtree` construct the maximally balanced and maximally imbalanced extremes. Balanced trees support both odd and even tip counts.

These functions are useful for examples and controlled tests. Their branch lengths are deterministic constructions, not samples from a biological process. Labels follow tip index order by default; set `randomize_labels=True` when exchangeable placement is desired.



```python
unit = toytree.rtree.unittree(9, treeheight=5.0, seed=123)
balanced = toytree.rtree.baltree(9, treeheight=5.0)
imbalanced = toytree.rtree.imbtree(9, treeheight=5.0)

```

## Conditioned reconstructed birth–death trees

Use `birth_death_conditioned_tree` for a standard constant-rate reconstructed tree with a fixed number of completely sampled extant taxa. Supply exactly one conditioning age:

- `crown_age` fixes the age of the sampled MRCA, so the returned root height equals that age and the root distance is zero.
- `origin_age` fixes the age at which one lineage began. The sampled crown is younger; the unobserved stem duration is stored in `tree.treenode.dist`, and the requested age is stored as `tree.treenode.origin_age`.

`birth_rate` and `death_rate` are per-lineage rates in reciprocal age units. For example, if age is measured in millions of years, the rates are events per lineage per million years. The implementation uses the analytic conditioned reconstructed process of Gernhard (2008), including the critical limit where birth and death rates are equal. It assumes complete extant sampling and integrates extinct lineages out.



```python
conditioned = toytree.rtree.birth_death_conditioned_tree(
    ntips=40,
    birth_rate=0.8,
    death_rate=0.2,
    crown_age=10.0,
    seed=123,
)

```

## Complete forward birth–death histories

Use `birth_death_process` when extinct lineages and individual events are part of the desired output. Supply exactly one of `stop_time` or `stop_ntips`. The result is a `BirthDeathProcessResult`, not just a tree. It contains `complete_tree`, `reconstructed_tree`, elapsed time, event counts, restart counts, extant/extinct tip counts, and the stopping convention.

`start="stem"` begins with one lineage below an explicit origin; `start="crown"` begins with two lineages at the initial split. With richness stopping, the simulation stops exactly at the birth event reaching the target, so the two newborn terminal branches legitimately have length zero. Finite `max_restarts` and `max_events` safeguards prevent impossible or high-extinction requests from running indefinitely.



```python
history = toytree.rtree.birth_death_process(
    birth_rate=0.8,
    death_rate=0.3,
    stop_time=10.0,
    start="crown",
    seed=123,
)
complete = history.complete_tree
extant_only = history.reconstructed_tree
print(history.births, history.deaths, history.extant_tips)

```

## Kingman coalescent genealogies

`coalescent_tree` samples a contemporaneous constant-size Kingman genealogy. `nsample` counts gene copies, `Ne` is effective population size, and `ploidy` converts individuals to gene copies. With `k` active lineages, the coalescence rate is

\[
\binom{k}{2}/(\mathrm{ploidy}\,N_e).
\]

Branch lengths are in generations when `Ne` is expressed in individuals. For a finite sample, the expected TMRCA is `2 * ploidy * Ne * (1 - 1 / nsample)`; it only approaches `4 * Ne` for a large diploid sample.



```python
genealogy = toytree.rtree.coalescent_tree(
    nsample=20,
    Ne=10_000,
    ploidy=2,
    seed=123,
)

```

## Simulating branch rates

`simulate_branch_rates` treats every input edge length as elapsed time and returns a new tree without modifying the input. If the root has a nonzero distance, as in an origin-conditioned tree, that value is treated as the explicit origin-to-crown stem duration and is also converted. The output edge distance is `time * rate`. All models annotate edges with `time`, `rate`, and `expected_substitutions`:

- `strict` assigns `mean_rate` to every edge and does not use `sigma`.
- `uncorrelated_lognormal` (UCLN) draws independent lognormal edge rates. `mean_rate` is the arithmetic mean and `sigma` is the dimensionless log-rate standard deviation.
- `autocorrelated_lognormal` (ACLN) evolves endpoint log rates by Brownian diffusion. Here `sigma` has units of log-rate per square-root time, so the amount of change scales correctly with branch duration. Edges additionally store `start_rate` and `end_rate`.

The time unit is determined by the input tree and the rate denominator. A tree in Myr combined with rates in expected substitutions/site/Myr produces output branch lengths in expected substitutions/site. Other consistent output units are equally valid.



```python
timetree = toytree.rtree.birth_death_conditioned_tree(
    30, birth_rate=0.6, death_rate=0.2, crown_age=8.0, seed=123
)
phylogram = toytree.rtree.simulate_branch_rates(
    timetree,
    model="uncorrelated_lognormal",
    mean_rate=0.01,
    sigma=0.5,
    seed=456,
)

```

## Reproducibility and labels

Every stochastic API accepts an integer, `numpy.random.SeedSequence`, `numpy.random.Generator`, or `None` as `seed`. Integer and SeedSequence inputs create a generator; a supplied Generator is consumed in place, which is convenient for a reproducible stream of replicates. All APIs use the same label validation and reject duplicate labels.

This release intentionally removes the ambiguous legacy names `rtree`, `bdtree`, and `coaltree`. Migrate them to `random_topology`, the appropriate `birth_death_*` method, and `coalescent_tree`, respectively. Replace the former `random_names` argument with `randomize_labels`.
