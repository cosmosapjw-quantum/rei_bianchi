# Same-author hostile audit, one finite pass

- **BLOCK_NOW resolved (scientific interpretation):** The original draft labeled `E_low+E_missing` as a terminal heating upper. This is false for all future heat: selected electrons with >=10.2 eV can cascade to heat later. Repaired by presenting THREE distinct budgets: selected first-generation subthreshold lower, first-generation plus unselected-energy upper, and a broader all-primary-energy ceiling. Added 19 tests including a negative check preventing promotion to total future heat.
- **Current source-ownership blocker (BLOCK_NOW for production):** PR299 REI/BASS mixed F/J and PR297/300 singlet photon events are conditional source owners. No common photon source replacement that prevents counting the same original photons twice has been established. This work does not add them to the native F/J.
- **Clock verification:** independent PR297/PR298 proper intervals match within 1.13e-14 relative; `Hmid Δt/Δx` differs by 3.89e-5 because it is a midpoint discretization, not a new physical clock defect. Distinguish source-time and quadrature diagnostics.
- **Electron loading limitation:** `-T/Ntherm dN_e/dt` shown only under prompt thermalization of first-generation H/He electrons. Electron cascade/secondary count and actual temperature evolution are not solved.
- **Baryon source and weak beta:** PR298's `J[HII,n]=1/878.4 s^-1` must not be deleted. This node does not mutate either source operator and preserves PR298/299 negative controls.
- **Source provenance:** four exact primary CSVs read from immutable source archives and SHA256-locked. No borrowed PDFs included. `native_REI17=NOT_RUN`, full Bianchi K/directional RT `UNBOUND`.
- **Independence:** same model self-adversarial review and independent algebraic/cgs computation, not a distinct-author blind referee or a second model. `R6/C9_DISTINCT_AUTHOR=NOT_RUN`.

Stop condition: do not promote canonical DAG, production or heating/optical depth/CMB without native source-owner coupling and complete energy-deposition data.
