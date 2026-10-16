# Native coupling: root-adopted boundary

This records the root frozen coupling contract, rather than authorizing a new solver or closure. Native Rust owns geometry, time, photons, coupled H/He chemistry and its common event/energy ledger. Python supplier code is an algorithm/source reference. The first clock unit retains cold Grackle 1–10^6 K and the existing coupled backward-Euler chemistry.

| Boundary | Input and convention | Single owner / next action |
|---|---|---|
| Clock → trial | Direct GL8 dt [proper seconds], signed db; log1p endpoint interval | One tentative dt is shared by source and chemistry; global point_at_scale/checkpoint geometry retained |
| REC → fresh IC | PR94 xe=.000210349192936, Tgas=9.306042400380866 K | Recipient nH/fHe, xHeII=xHeIII=0, ionizing stock=0. Thermal state is erg/H, not donor J/m³. Baseline IC remains distinct |
| Source → photons | photons/H/s × proper dt × spectral/angular fractions | Apply geometry/source Jacobian once. Positive subcells preserve actual N/U and ray/age/clock identity |
| Geometry → reactions | k_i=a_i E n_i, E=sqrt(sum((k_i/a_i)^2)) or equivalent birth-cohort data | Next native representation retains this energy through cross-section/heat evaluation; repeated fixed-grid projection is unresolved |
| Photons → coupled chemistry | Proper cm⁻³, gamma_s per absorber/s, heat power erg per absorber/s | Existing evaluate/chemical_stage owns photo destruction, binding/heat and CI/RR/DR/escape/CMB. Do not apply frozen reference absorption a second time |
| Expansion → thermal work | Existing driver adiabatic maps | Point RHS H=0 if expansion already applied outside; no duplicated work |
| New representation → checkpoint | Birth/characteristic state, source/grid/clock identity | Version the schema; reject incompatible old projected restart. Bound cohort memory before long runs |
| D/H standalone | Proper-SI densities, explicit rates, dt, Δχ and source | Frozen-rate CX map owns its thermal/chemical defect once; no implicit D abundance and no HHe activation |

The next representation tests are false-HeII threshold regression, photon/energy/clock ledgers, actual-source refinement and new-schema resume. Native source quadrature/child-moment receipts follow the representation seam. A short-clock PASS does not admit the full production trajectory.

HH requires an actual k_HH(T)/cross-section/event contract. CR-on requires a selected source, thermal versus active-electron closure and actual transferred energy/count. These missing inputs do not block CR-off H/He. BASS Sigma=sqrt(3)|s|/H is distinct from recipient signed s/H; Einstein/massive/Stokes remain optional model choices.
