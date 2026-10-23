# Resume boundary — reviewed C1 complete

Current node: `COUPLED_ISOTOPE_NATIVE_CONTRACT`.
Completed selected work: **C1**, source/charge/energy/EOS contract and finite
algebra checks. Independent decision:
`PASS_SCOPED_C1_CONTRACT_AND_FINITE_ALGEBRA`; no repair requested.
Actual diagnostic: **191 checks PASS**, exit 0, **0 new cosmological IVPs** and
0 historical sweep reruns. `evidence/EXECUTION.json` preserves the actual run;
`REVIEW.md` and `evidence/INDEPENDENT_REVIEW.json` preserve the one review pass.

Branch: `research/rei-coupled-isotope-contract-20261022`.
Base PR219: `5a1e5220b301a1c497f2863d6fd823e605faba80`.
Independent PR220 donor: `8be7533cc97b3302bf42608699d6e8313ed6af8a`.
These are historical source identities; a remote publication SHA is not yet
part of this local source checkpoint.

Read `CONTRACT.md`, `REPORT_KO.md`, actual evidence and `REVIEW.md`.
`DAG.json` marks C1 COMPLETE and **C2 READY**; C2 is not executed, and C3–C10
remain NOT_SELECTED/PENDING. Coupled physical production remains
**HOLD_DEPENDENCIES**.

## Next selected work

C2 maps actual source rows, code functions, units, applicability and physical
providers to the reviewed isotope-charge event interface. In particular map
nuclear `mass_table`, `_q_j`, `rate_table` and evaluated decay inputs; the donor
atomic decay block, rates and RHS; charge-resolved daughter injection; and
thermal/radiation energy moments. This is source/function/provider mapping,
not completion of a native solver, closed radiation solution or new IVP.

Remaining inputs: charge-conditioned daughter probabilities and excited or
continuum yields; applicable charge-resolved reaction and decay models; a
consistent physical mass/binding table; RR/DR energy moments; nonthermal
transport, stopping and stress; generated-photon transport/closure; and actual
removal of the duplicate atomic beta owner in the future coupled composition.
An unknown provider remains UNRESOLVED and must not become a zero source.

## Protected assumptions and identity

Retain non-tilted LRS Bianchi I with signature (-,+,+,+), proper-time event
units, conserved-baryon normalization, and all **21 isotope-charge states**,
including representable absent n/T. The massive nonbaryonic stress, radiation
stress and baryonic thermal/fast stress remain distinct. Nuclear heating must
not become a shear-stress exchange term.

Use one beta-event owner and one energy owner per exchange. Coupled beta
constants come from the evaluated nuclear input; historical atomic helpers
and results remain unchanged. Preserve the old 12.32-Julian-year and evaluated
12.312-year definitions separately. Fast stopping transfers energy from fast
to thermal without adding Q again. Separate total electrons from thermal
electrons, and use the changing thermal particle count in the common-T EOS.

Keep PR219's 5–60 eV external field and PR220's 5–200 eV field distinct.
Keep PR219's original 83 atomic records / 82 conditional nuclear backgrounds,
PR220's 127 main + 2 full62 oracle cohort, and REC119's 126-case cohort separate;
do not sum these counts or import their admissions into a coupled claim.
Preserve inherited tolerances and raw/failed records. The fixed PR220 lift is
not valid for a positive T source without replacement or a new proof.

This checkpoint contains finite algebra and manufactured limiting examples;
it supplies no physical branching distribution, rate or trajectory.
