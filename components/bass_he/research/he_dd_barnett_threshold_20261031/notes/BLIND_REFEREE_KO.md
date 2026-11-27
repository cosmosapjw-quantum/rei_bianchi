# Same-author blind referee pass, physics-first (PR138)

**Finding A (critical, resolved by restricted domain).** EXFOR L0138002 has `(G,X)PI0`, not `(G,PI0)He4`. Incorrectly labeling all 216 rows as exclusively coherent would fail. The exact two-body threshold is 137.4207069 MeV, and the lightest nuclear-breakup plus π0 final state p+T+π0 has 158.0046815 MeV threshold. Only source readings 139.8–156.13 MeV are selected and used as exclusive-coherent by kinematic exclusion. Data below threshold are preserved only as measured background/noisy points. The source's 2% sys is shared across points.

**Finding B (strong constructive result).** The maximum pi0 decay daughter energy reaches the coherent production threshold only at 171.1649069 MeV incident, even allowing all pion CM angles. In the Barnett-selected below-breakup source range (<158.0047 MeV), the subsequent pion-feedback kernel has strictly zero support. Do **not** extrapolate this result to 206–241 MeV Rambo sources; the old PR137 feedback remains relevant there.

**Finding C (physical model uncertainty, OPEN).** p-wave sin² angular PDF follows a restricted spin-0/M1 hypothesis but is not directly extracted from the Barnett differential angular paper. The angular-agnostic isotropic alternative is calculated at two representative energies as a separate model sensitivity. The source 1σ statistical and shared 2% systematics **do not include** this angular or nuclear/cascade model uncertainty.

**Finding D (kinetic vs heat, resolved representation).** Two deuterons' laboratory kinetic sum for alpha+gamma->dd is E_gamma-Q_dd exactly, independent of daughter angle. In alpha+gamma->npD, no source-owned differential three-body D kinetic distribution exists in this unit; record 0≤K_D≤E_gamma-Q_npD for **that channel only**. Neither bracket is a net deposition or all-nuclei D kinetic estimate.

**Finding E (nuclear/network limitation).** 16 of 17 ACROPOLIS source channel stoichiometries are exact A,Z-conserving and are checked; original Li6(gamma,X) final-state products are unspecified and placed in an unassigned ledger. Signed D response is a perturbative fixed-BBN-abundance afterburner and not a full nonlinear abundance solution.

**Finding F (numerical).** Low NE=64 versus reference 96 points/decade and isotropic-vs-pwave angular choice were executed for two source epochs. Recorded source-grid mean energy discrepancy max=2.34e-5 for the nominal 96 grid. Fine-grid high-z (10^6) model-error budgets remain unresolved because first-hit probabilities are exponentially small. Do not call the result a precision BBN constraint.

**Finding G (provenance).** 216 EXFOR data lines are distinct tabulated observations, NOT 216 experiments, and repeated energy measurements have possible correlations. No weighted pooling into falsely overprecise 1σ data. Source original SHA-256 and published DOI are recorded. No unpublished data/author correspondence required to reproduce this scoped calculation.

**Outcome:** scoped numerical physics VALID for stated model and input source; canonical Central/HE DAG stays 28/88 and 14/18, delta=0; production HOLD. Same-context R6/C9 NOT an independent distinct-author referee.
