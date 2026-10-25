# Independent final supplier and scientific review

Unit: `REI-GRID044-ENDPOINT-BINDING-01`  
Reviewer: `/root/supplier_intake`  
Implementation author: `/root/normalization_review`  
Date: 2026-10-25 UTC

## Decision

**PASS_SCOPED_ENDPOINT_BINDING. No unresolved scientific blocking finding for the frozen finite endpoint unit.** The observed code, raw values, original source identities, independent arithmetic, and directly viewed figure support the actual saved-state photo-source binding and the endpoint callback adapter. This decision admits that finite unit only. It does not admit a fully coupled six-provider trajectory, physical HE degradation, new BASS absorption transport, a continuous VigilODE physical domain, full-network completion, or L4.

The pre-execution findings were corrected before the scientific run: explicit `atomic_abundance_per_Href[:, -1]`, label-based Li7/Li6 reordering, actual donor `a`, zero-width neutron/tritium support, a canonical ownership key independent of arbitrary domain/state prose, and separate controls for omission of the source and derivative quotient terms. The final frozen contract records those clarifications.

## Evidence and independent method

Reviewed `consumer.py`, `test_consumer.py`, generated `rust/client.rs` and its generator, the unchanged WU/REC/CR/VigilODE source modules, all relevant output JSON, resource receipts, the implementation handoff and reproduction document. Directly opened `figures/GRID044_ACTUAL_ENDPOINT_SOURCES.png`.

The independent review script `rei_review/review_endpoint_arithmetic.py` reads only immutable original bytes and saved outputs. It imports no consumer or scientific provider function and executes no source suite, quadrature, opacity integral, or ODE. NumPy is used only to read the immutable donor NPZ. It independently constructs the 13 adjacent-charge transitions from the declared isotope/charge labels, accumulates the 26 source contributions with `math.fsum`, reconstructs all 25 source outputs and all 25x23 analytic coefficients, and compares the actual Rust raw values. It also checks the saved normalization directional algebra, wrong-J control and source identities.

Its full result and reviewed-file SHA256 snapshot are in `rei_review/FINAL_REVIEW_ARITHMETIC.json`. All **10** immutable inputs and reused modules byte-match their original source archive or pinned supplier intake, not merely a newly written manifest. The arithmetic loop took 0.008019 observed CPU seconds and 0.008032 wall seconds after Python/NumPy import; startup and review-reading/image overhead are unmeasured and are not represented as zero.

## Verified numerical conclusions

| Quantity or comparison | Observed value |
|---|---:|
| Selected physical reference density | 5.151254745827818 m^-3 |
| Saved donor scale factor | 0.33333333333333326 |
| Fixed comoving reference density at a_today=1 | 0.19078721280843758 m^-3 |
| Actual primary-electron source | 6.113207047135675e-19 ref^-1 s^-1 |
| Actual primary-electron source in physical volume | 3.1490686813785706e-18 m^-3 s^-1 |
| Stellar contribution to number source | 4.876273618673197e-19 ref^-1 s^-1 |
| External-IGM contribution to number source | 1.2369334284624778e-19 ref^-1 s^-1 |
| Independent 25-output reconstruction versus saved REC | 1.9849382606629986e-16 row-scaled |
| Independent 22-source reconstruction versus saved WU | 1.9849382606629986e-16 row-scaled |
| Independent 25x23 coefficients versus saved REC J | 1.8984984282475022e-16 row-scaled |
| Independent coefficients versus saved complex-step J | 1.8984984282475022e-16 row-scaled |
| Independent actual-source reconstruction versus Rust | 1.9849382606629986e-16 row-scaled |
| Independent 21x21 coefficients versus Rust | 0.0 |
| Largest independent component energy residual | 1.582703458723587e-16 row-scaled |

Scales use the sum of absolute individual source contributions, the largest coefficient in each Jacobian row, and the sum of absolute energy-sector powers. They have no unit-sized floor. A vanishing scale requires an exact-zero difference, preserving the meaning of the very small Li contributions. The saved neutron and both T populations remain exact zero. The 26 energy contributions retain the independently supplied `K`; no kinetic moment is manufactured by subtracting the other sectors.

The observed signed energy-source vector, radiation loss / binding gain / primary kinetic gain, is

`[-8.35115562362068e-36, 6.882360343067273e-36, 1.4687952805534072e-36] J m^-3 s^-1`.

This is a collision-level partition in the admitted stationary-target, no-recoil valence approximation. It is not a complete momentum/finite-mass ledger or a heating result. `thermal_heating_J_m3_s` remains null and UNQUALIFIED.

The author's recorded changed-contract suite has **32 Python checks and 9 Rust comparison checks**, all passing their scoped criteria. The independent review did not replay it. Its quoted direct WU/REC discrepancy 1.924856455018995e-16 and complex-step discrepancy 1.488667807882561e-16 differ slightly from the independent reconstruction above because the independent reconstruction uses a separate accumulation order; both are far below the frozen row-scaled tolerances.

## Reference density and derivative assessment

The donor abundances are already normalized to the fixed comoving bookkeeping reference. The consumer keeps REC's normalized output unchanged, and multiplies by `r` once for physical number-source units and by `r * 1.602176634e-19` once for SI power density. It uses the saved donor mean scale factor to set `n_ref0=r*a^3` and does not redefine the reference by actual hydrogen or baryon populations.

For physical continuity equations `dot n+3Hn=S` and `dot r+3Hr=R`, the implemented

`F=(S-xR)/r`,
`dF=(dS-R dx-x dR)/r-F dr/r`

is correct. The fixed-comoving reference has `R=0`, despite its changing physical density; abundance derivatives at the frozen endpoint have `dr=0`, while a scale-factor tangent includes `dr=-3r da/a`. The explicit manufactured changing-reference source exercises nonzero `R`, `dR`, and `dr`. Its recorded directional discrepancy is 2.147543150575634e-16; the fixed-comoving scale-factor discrepancy is 8.367371580054058e-17. The independent review reproduced the saved directional algebra from the saved source and tangent values.

The two negative controls are distinct. Removing `-xR/r` changes the manufactured source by 0.03812178499999999 in its stated units. Removing `-F dr/r` changes the tangent by 0.2024793964639783 on the row scale. These algebraic controls are explicitly distinguished from astrophysical source data.

## Single ownership and supplier validity

Each of the 13 chemical transitions has one physical extent owner. Stellar and external-IGM spectra are additive contributions under that owner. Actual isotope, charge, state and electron-pool identities determine the physical key; alternate provider-domain or state-resolution prose cannot create a second owner. Both duplicate mutations are observed to reject. WU incidence includes the fast electron once and gives exact isotope, baryon and material-plus-fast-electron charge residuals in decimal-representation rational arithmetic. That exact arithmetic does not make the physical rate estimates exact.

The source identity is the saved GRID044 continuum at z=2 with 5..150 eV birth support and unchanged source normalizations. The original `MODEL_CONFIG.json` is parameter provenance; its older midpoint-impulse wording does not supersede the opacity response's continuous free-streaming contract. The saved donor state is paired with these prescribed sources as an instantaneous counterfactual operator; it is not claimed to have evolved under them.

CR contributes its unchanged **generic photo-event energy ledger**. The selected continuum rates are supplied by REI/REC. CR's C23B spectral assembler, which has different published redshifts and energy support, is not called, substituted, or relabelled. The rejected substitution control records that distinction. Do not summarize this join as admission of the original CR spectral model at z=2.

HE receives primary-electron number and first kinetic-energy moments only. Spectrum and angular measure are null; no monoenergetic spectrum, recoil law, stopping law or thermal heating is inferred. Existing HE101/C8 and exhausted-reservation constraints remain intact. BASS reuses prescribed geometry and signed stress stocks in J/m^3; its new absorption angular measure and stress-rate/feedback join remain open. Scalar photo-rate and energy moments are insufficient to manufacture those angular transfers.

## VigilODE result and limits

The unchanged D5 `gateway.rs` is used for the new 21-state callback. Its RHS actually computes `A*x`, and the Jacobian full-writes `A`. Raw values match the independent physical frozen coefficients. The positive-supported point keeps zero-width n/T blocks at zero. The actual state and zero boundary are evaluated; negative state, upper-bound violation, outside-point time and a time-derivative stencil reject. The raw call counters are four RHS calls, four Jacobian calls and four pairs.

A finite wrong Jacobian is gate-admitted, as the original gateway contract permits, and the independent coefficient comparison detects row-scaled error **0.5**. This cleanly separates callback contract admission from mathematical derivative correctness. The time domain is a single endpoint, the box is only an envelope, and isotope-simplex/complete physical-domain, continuous-time trajectory/error control, and native floating-point certification remain OPEN. No old D1–D5 suite or norm implementation was replayed or replaced.

## Figure and delivery assessment

The saved PNG was actually viewed. The 13 event labels and two source colors are legible; the T event is explicitly marked exact zero; positive tiny values remain visible on the logarithmic axis. A separate panel shows signed radiation loss, binding gain and primary kinetic gain. The final panel labels mathematical controls and the normalization mutation, including its different absolute-unit meaning. The figure states the instantaneous, photo-only scope and absence of a new trajectory or stopping/feedback calculation. It supports the finite result without presenting a physical history or thermal-heating curve.

A documentation-only reproducibility clarification was requested: distributed `execution/suite01-*` directories already exist, so the shown historical commands must be identified as recorded commands, and any authorized future reproduction must choose fresh attempt names while retaining the cumulative ledger. No scientific rerun is needed for this clarification.

The implementation's resource receipt retains the initial linker failure, successful single-thread repair and all executed stages. Recorded scientific work totals 2.900492 CPU seconds and 2.940682361000654 wall seconds; infrastructure totals 14.682127000000001 CPU seconds and 14.797034617000463 wall seconds. Existing campaign allowances were not reset or transferred. Historical-budget and programme-gate review is additionally delegated to the independent baseline reviewer.

Expected-SHA publication, source ZIP, durable dual backups, final DAG update and root scientific admission remain root delivery obligations. This review makes no claim that those external delivery steps have already completed.
