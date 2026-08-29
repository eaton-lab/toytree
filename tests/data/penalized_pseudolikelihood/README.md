# Penalized-pseudolikelihood reference fixtures

`ape-5.8.1.json` pins fixed-objective and full-fit values produced by
`ape::chronos` 5.8-1. Normal Python test runs consume the JSON and do not
require R. Run `regenerate_ape_fixture.R` only when intentionally refreshing
the external reference, then review all numeric changes.

The fixture covers the strict clock, branchwise discrete mixture, and the
Gamma-CDF `relaxed` model. ToyTree's `uncorrelated_lognormal` and correlated
models use scale-invariant summed log-rate penalties and are validated by the
simulation study under `validation/penalized_pseudolikelihood`; they are not
asserted to reproduce ape's raw-rate penalties.
