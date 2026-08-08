# Claim–source audit

| Claim | Project source | Literature source | Status |
|---|---|---|---|
| Six full-OTS parent channels and child species topology | `full_ots_kernel`; `full_ots_population_rhs` | Friedrich et al. 2012 §3.1.2, Table 1 | supported |
| `p=0.96`, `ell=1.425`, `m=0.737` | both project kernels | Friedrich et al. Table 2 | supported |
| Relative-opacity definitions of `y,z,y2a,y2b` | both project kernels | Friedrich et al. §3.1.2 | supported |
| Current sigmoid is the cited `v(T)` | project code only | Hummer–Seaton function/table not imported | not supported |
| Current exponential is the cited `f(x_HI)` | project code only | source only gives/table-uses a bounded absorption fraction | contradicted over current state range |
| Net RHS uniquely determines events | no | source parent/branch topology is required | rejected |
| Source parent topology plus branch kernels determines expected event yields | exact event registry | Friedrich et al. | supported conditionally |
| Every OTS child excess energy is currently resolved as heat | no explicit source owner in current thermal RHS | multifrequency heating requires spectral/optical-depth moments | not supported |
| Total energy can close with an unresolved OTS energy account | exact algebra | conservation law | supported |
| FLRW `3H pV` is valid for arbitrary tilted Bianchi gas | current code is FLRW specialization | 1+3 conservation uses hydrogen-frame expansion scalar | rejected outside specialization |
