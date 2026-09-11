# `rtree` simulation validation

This directory records fixed-seed validation for the public tree and branch-rate simulators. The confirmation workload checks quantities that are known independently of the implementation:

- exact four-tip Yule–Harding and uniform/PDA shape probabilities;
- the analytic conditioned reconstructed birth–death branching-time CDF;
- an independent pure-birth conditional branching-time mean;
- Kingman first-coalescence and finite-sample TMRCA expectations;
- forward birth–death event-type probabilities and stopping invariants;
- UCLN lognormal moments and independence;
- time-scaled ACLN standardized log-rate increments; and
- empirical doubling-time scaling for topology, coalescent, and pure-birth construction.

Run the small development check with:

```bash
python validation/rtree/run_validation.py --mode quick
```

Record release evidence with:

```bash
python validation/rtree/run_validation.py --mode confirmation
```

The confirmation command writes `results-confirmation.json`. It is deterministic except for elapsed-time measurements. Timing gates are intentionally loose: they detect a return of the former quadratic `Node` hash/update behavior, not small machine-to-machine performance differences. Unit tests contain the same statistical checks at smaller sample sizes so ordinary CI remains fast.

The distributions assume rooted bifurcating trees, contemporaneous tips where specified, complete extant sampling for the conditioned birth–death method, a constant-size neutral Kingman coalescent, and the rate parameterizations documented by the public functions. They do not validate incomplete sampling, fossilized birth–death models, population structure, recombination, or topology inference.
