<div class="nb-md-page-hook" aria-hidden="true"></div>

### Inference: Parsimony (CI / RI / RCI)

`toytree.infer.consistency_and_retention_indices` summarizes how well a
single discrete trait follows a tree topology.

The result is returned as a pandas DataFrame with one row for each
statistic (`fitch_parsimony_score`, `CI`, `RI`, and `RCI`). Columns
report the observed value, the permutation null mean, one-sided
p-values in both directions, and the tail that is usually interpreted as
phylogenetic signal for that statistic.

The **consistency index (CI)** compares the minimum possible number of
changes for the observed number of states to the observed Fitch
parsimony score. Lower CI means more extra changes, so it is commonly
used as a measure of homoplasy.

The **retention index (RI)** measures how well trait states are retained
as clade-structured patterns instead of being scattered repeatedly across
the tree. High RI means the observed states can be explained largely by
shared ancestry rather than repeated gains or losses.

The **rescaled consistency index (RCI)** is `CI * RI`. It combines the
homoplasy penalty from CI with the retention term from RI, which often
makes it more useful for comparing characters across trees or datasets
than CI alone.



```python
import numpy as np
import pandas as pd
import toytree
```

### How to read the result table

The returned DataFrame includes both one-sided permutation p-values for
each statistic:

- `p_value_greater`: tests whether the observed value is greater than the
  permutation null.
- `p_value_less`: tests whether the observed value is smaller than the
  permutation null.

The `signal_tail` column indicates which direction is usually interpreted
as stronger phylogenetic structure. For `CI`, `RI`, and `RCI`, larger
values indicate stronger tree-structured signal. For
`fitch_parsimony_score`, the direction is reversed: fewer implied
changes indicate stronger phylogenetic structure.


### Demonstration

First simulate a small tree and one discrete trait with three states.



```python
tree = toytree.rtree.unittree(20, seed=42)
trait = tree.pcm.simulate_discrete_trait(
    nstates=3,
    tips_only=True,
    state_names="ABC",
    seed=7,
)
trait.name = "state"
trait.head(10)
```




    0    C
    1    A
    2    A
    3    A
    4    A
    5    A
    6    C
    7    A
    8    A
    9    C
    Name: state, dtype: object




```python
trait.value_counts().sort_index()
```




    state
    A    9
    B    8
    C    3
    Name: count, dtype: int64



Now compute the parsimony summary table for the observed trait.



```python
signal_stats = toytree.infer.consistency_and_retention_indices(
    tree,
    trait,
    npermutations=500,
    rng=7,
)
signal_stats
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>observed</th>
      <th>null_mean</th>
      <th>p_value_greater</th>
      <th>p_value_less</th>
      <th>signal_tail</th>
    </tr>
    <tr>
      <th>statistic</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>fitch_parsimony_score</th>
      <td>6.000000</td>
      <td>8.790000</td>
      <td>1.00000</td>
      <td>0.01996</td>
      <td>less</td>
    </tr>
    <tr>
      <th>CI</th>
      <td>0.333333</td>
      <td>0.231359</td>
      <td>0.01996</td>
      <td>1.00000</td>
      <td>greater</td>
    </tr>
    <tr>
      <th>RI</th>
      <td>0.555556</td>
      <td>0.245556</td>
      <td>0.01996</td>
      <td>1.00000</td>
      <td>greater</td>
    </tr>
    <tr>
      <th>RCI</th>
      <td>0.185185</td>
      <td>0.060549</td>
      <td>0.01996</td>
      <td>1.00000</td>
      <td>greater</td>
    </tr>
  </tbody>
</table>
</div>



You can inspect whichever tail matters for your question directly
from the result table. The snippet below focuses on the three homoplasy
indices and shows both one-sided p-values alongside the recommended
`signal_tail` direction.



```python
signal_stats.loc[
    ["CI", "RI", "RCI"],
    ["observed", "null_mean", "p_value_greater", "p_value_less", "signal_tail"],
]

```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>observed</th>
      <th>null_mean</th>
      <th>p_value_greater</th>
      <th>p_value_less</th>
      <th>signal_tail</th>
    </tr>
    <tr>
      <th>statistic</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>CI</th>
      <td>0.333333</td>
      <td>0.231359</td>
      <td>0.01996</td>
      <td>1.0</td>
      <td>greater</td>
    </tr>
    <tr>
      <th>RI</th>
      <td>0.555556</td>
      <td>0.245556</td>
      <td>0.01996</td>
      <td>1.0</td>
      <td>greater</td>
    </tr>
    <tr>
      <th>RCI</th>
      <td>0.185185</td>
      <td>0.060549</td>
      <td>0.01996</td>
      <td>1.0</td>
      <td>greater</td>
    </tr>
  </tbody>
</table>
</div>



To make the interpretation concrete, compare that clustered trait to a
randomized version with the same state counts but shuffled tip labels.



```python
rng = np.random.default_rng(7)
randomized_trait = pd.Series(
    rng.permutation(trait.to_numpy()),
    index=trait.index,
    name="state",
    dtype=object,
)
randomized_trait.head(10)
```




    0    A
    1    A
    2    A
    3    B
    4    B
    5    B
    6    B
    7    B
    8    A
    9    C
    Name: state, dtype: object




```python
randomized_stats = toytree.infer.consistency_and_retention_indices(
    tree,
    randomized_trait,
    npermutations=500,
    rng=7,
)
comparison = pd.DataFrame(
    {
        "clustered_trait": signal_stats["observed"],
        "randomized_trait": randomized_stats["observed"],
    }
)
comparison

```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>clustered_trait</th>
      <th>randomized_trait</th>
    </tr>
    <tr>
      <th>statistic</th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>fitch_parsimony_score</th>
      <td>6.000000</td>
      <td>8.000000</td>
    </tr>
    <tr>
      <th>CI</th>
      <td>0.333333</td>
      <td>0.250000</td>
    </tr>
    <tr>
      <th>RI</th>
      <td>0.555556</td>
      <td>0.333333</td>
    </tr>
    <tr>
      <th>RCI</th>
      <td>0.185185</td>
      <td>0.083333</td>
    </tr>
  </tbody>
</table>
</div>



In this example the clustered trait has a lower Fitch parsimony score
and higher CI, RI, and RCI than the randomized trait. That is the
typical pattern when a character is more consistent with the tree than a
random tip-label permutation.

