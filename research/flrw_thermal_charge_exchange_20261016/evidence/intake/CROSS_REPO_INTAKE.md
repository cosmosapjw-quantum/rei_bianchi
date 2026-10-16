# Cross-repository intake — 2026-10-16 UTC

Read-only intake at primary REI `eb2abcac4f44b7bc4ff532286953fcb4e353c7bb`. Exact source/result file references and all pins are in the sibling JSON. No science run, publication or archive restoration was performed.

| Lane | Exact latest inspected head | Reusable observed result / boundary |
|---|---|---|
| REI166 | 553ce556d9f8662290c000ec675c7e6007c9d895 | Native positive MD14 cohorts exist; actual DOP853 reference fails internal positivity at call291. Source-age differences increase. Supplier/reference work is owned separately. |
| REI167 | 24dc6893182167dd9fd25fb18d70707d52b9229b | Native birth/Newton causal study exists; common-endpoint reference reported running. |
| REI168 | c02fb3492b99b79c8b2e3bae1a6183510ff1df9b | Actual source-free RR/DR midpoint vs Radau second-order results at moderate density; dense/roundoff limits retained. |
| BASS_HE73 | 98b31fbd779ed1ade8848580c2836f32259e3ef3 | HE26 exact moving-cut source donor:108 source controls,24 manufactured angular cases. HE27 native attachment is the published next handoff. |
| bass_cr76 | 172ca4c814b0b5bb05a03b509086e85f9cdd6138 | Exact irreversible photon/absorber pair and positive source-age photo-only reactor; manufactured second-order test. |
| WU088_HH100 | e9a80d7a7280a4b944a7a9d0a2ce3bb4ca971a2f | Exact finite screened multipole intervals and nonzero P/Q transfer; HH_R10 OFF. No physical H-H rate donor yet. |
| bass166 | 02149a6830dfe7ed214b77f5309e38350d2659fb | Source geometry and one native fixed-event H/He component; evolving implementation continued in REI159/162/167. |
| rec_bianchi99 | a5e92bd17f1c0a1fd331ee203405d3971c444efb | Actual U7 independent HyRec through z20:xe=0.00021034919293635483,Tm=9.306042400382015K. Candidate off;U5 spectrum gate HOLD;no temporal refinement. |

## Selected independent opportunity

The original proposed frozen-rate H/D charge-exchange map is already implemented. Primary `rust/rei_microphysics/src/deuterium_charge_exchange.rs`, blob `dd0a8c9b96ef3e53b8eef0fd08961045779f20b7`, supplies exact scaled Riccati/tanh kinetics, stoichiometric invariants, zero electron delta and sole signed thermal/binding energy ownership. Existing seven tests include semigroup, stiff/degenerate/reverse behavior and D=0.

A thermally self-consistent isolated CX scalar extent is distinct in the inspected source: use constant proper volume and thermal particle count, `u(xi)=u0-DeltaChi*xi`, `T=2u/(3 kB nthermal)`, evaluate actual Savin rates at evolving T, stop at stoichiometric and provider-domain events. Existing `deuterium_atomic.rs` blob `8477162430af02585a32d18092454e1f7bb52f60` has the point RHS and a wrapper to the frozen map, not this internally evolving scalar map.

Savin fit domain is inclusive 2.7–200000 K. The explicit selected defect is 0.0037 eV, not either fit exponent37.1 or33K. Existing D atomic provider domain1–1e6K does not widen the CX domain. Tiny manufactured-oracle and actual-Savin cases can advance this component without touching running native source references or activating production. No equilibrium-uniqueness or rigorous quadrature claim follows merely from the scalar reduction.

Other possible later components: source-bound competing H/D photon absorption with one event/energy owner; prescribed-expansion composition of the frozen map. Both need narrow explicit contracts and remain separate from full isotope-network admission.

## Evidence and coverage

Actual machine results were read for HE26,CR76,WU100,BASS166,REC99,REI166 and REI168, not titles alone. Latest related open PRs and complete REI/bass_cr trees were inspected; charge/deuter branch/PR searches found no current thermal-CX lane. An old BASS_HE charge-goal branch points to a 2026-10-13 opacity-backup commit and is unrelated.

This is bounded absence-of-duplication evidence, not proof that no unpublished owner work exists. All visible GitHub authors are the same owner; branch names identify research lanes, not live processes. Cloud backup success is reported by upstream PR metadata and receipts; this intake did not independently restore those archives. No cloud identifiers, credentials or private raw payload are copied into these notes.

