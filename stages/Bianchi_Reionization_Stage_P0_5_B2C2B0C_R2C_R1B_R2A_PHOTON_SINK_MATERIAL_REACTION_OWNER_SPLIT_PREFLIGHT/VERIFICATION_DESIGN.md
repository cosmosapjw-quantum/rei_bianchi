# Verification design

| Gate | Requirement | Result |
|---|---|---|
| Owner closure | opacity/current sums `<1e-11` | PASS |
| Exact zeros | unsupported and subgrid resolved sources exact zero | PASS |
| Capacity | resolved absorption within initial reservoir plus locked supply | 225/225 PASS |
| Refinement | budgets stable over `1,2,4,8` subdivisions | PASS |
| Positivity | nonnegative owner fractions and allocations | PASS |
| Lane symmetry | no post-result lane selection | PASS |
| Regression | unsplit low-group update reproduces overcount diagnosis | 20/20 expected failure |
| Independent replay | separate parser/arithmetic | PASS |
| Symbolic/high precision | Wolfram and Decimal-90 | PASS |
| Full repository/package | run after compact packaging | recorded in final receipts |
