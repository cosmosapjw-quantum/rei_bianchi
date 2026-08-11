# Literature evidence ledger

| Topic | Source role | Stage use |
|---|---|---|
| Modified Patankar Runge-Kutta order/structure | Kopecz & Meister, Applied Numerical Mathematics 123 (2018), 159-179 | supports positivity/conservation and second-order method class; does not replace project-specific map validation |
| MPRK nonlinear stability | Izgin, Kopecz & Meister, PAMM 2021/2023 | motivates validating the actual nonlinear discrete map rather than a Dahlquist surrogate |
| Interval Newton/Krawczyk | Moore and standard interval-analysis literature | sufficient local existence/uniqueness enclosure for implicit population/thermal blocks |
| Taylor/affine set propagation | validated ODE/set-valued integration literature | motivates preserving parameter dependence and controlling wrapping over future interval composition |

No source is used to infer a missing branch correlation, Bianchi driver, or
production history.
