# R2B-R2 owner-correct fixed-point history rerun — read first

This stage executes the first full owner-correct, photon-conserving, nonautonomous H/He/thermal history from the durable R2B-R1 input/operator lock.

The authoritative global group opacity/current remains the canonical B2C2A-R1 forcing. The current accepted material state determines conditional owner fractions and owner-internal node allocations. `EFFECTIVE_HI_SUBGRID` removes photons and accumulates unresolved absorbed energy only; its resolved H, He, and thermal sources are structurally exact zero.

The calculation must fail closed without clipping, owner reassignment, `kappa=J/Phi` constitutive inversion, cloud/geometry inversion, post-hoc lane selection, or a recombination surrogate. Accepted-step commit and rejected-step rollback are transactional and byte-audited.

The stage begins from the exact 46,080-node z=6 material state and the 85-row canonical BDF forcing locked by R2B-R1. Primary and two auditor subgrid lanes are all evaluated. Production node chemistry is authorized only if all primary scientific gates close; auditors quantify systematic sensitivity and are never selected after seeing outcomes.
