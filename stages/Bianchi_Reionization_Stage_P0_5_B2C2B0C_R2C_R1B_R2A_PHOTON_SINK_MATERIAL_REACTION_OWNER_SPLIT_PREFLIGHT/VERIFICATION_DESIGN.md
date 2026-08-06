# Verification design

| Gate | Requirement |
|---|---|
| Owner closure | opacity/current sums close at `1e-11` |
| Exact zeros | unsupported and subgrid resolved sources exact zero |
| Capacity | resolved absorption within initial reservoir plus locked recombination/inflow |
| Refinement | budgets stable over `1,2,4,8` subdivisions |
| Positivity | nonnegative owner fractions and allocations |
| Lane symmetry | no post-result lane selection |
| Regression | unsplit low-group update reproduces overcount diagnosis |
