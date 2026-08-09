# rec_bianchi v0.68 semantic compatibility review

## Scope

This is a deliberate read-only review triggered by the remote SHA change to
`5e5ea3a15a8611587b43e89bbb932b02d2e13c0d`. It is not an adapter review and
imports no numerical recombination state.

## Compatible semantics

- `rec_bianchi` owns primordial recombination, canonical two-photon/Raman
  source adapters, and their accepted-history transaction semantics.
- `rei_bianchi` owns astrophysical reionization UV absorption, the full-OTS
  H/He event registry, resolved/unresolved sink ledgers, and late-time thermal
  evolution.
- Both projects require one-owner/XOR bookkeeping, exact structural zeroes,
  immutable accepted history, and byte-exact rollback.

## Required future firewall

A future splice must carry typed reaction identifiers, redshift and validity
windows, electron fraction and matter-temperature provenance, interpolation
error, and explicit photon/chemical/thermal/radiation energy owners. Primordial
Raman or two-photon packets must not be relabelled as the astrophysical
full-OTS packet spectrum, and the unresolved OTS energy ledger must not be
silently deposited into resolved gas heat.

## Verdict

`PASS_DOMAIN_AND_OWNERSHIP_FIREWALL_ONLY_NO_NUMERICAL_IMPORT`.

No adapter, accepted history, rates, radiation state, or surrogate is imported.
