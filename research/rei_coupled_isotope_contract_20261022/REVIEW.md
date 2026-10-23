# Independent scientific review: selected C1

Decision: **PASS_SCOPED_C1_CONTRACT_AND_FINITE_ALGEBRA**.
Coupled physical production remains **HOLD_DEPENDENCIES**. No current C1 blocker
was found, no repair is requested, and this single review pass is complete.

## Scope and independence

The parent dispatched a fresh reviewer for the next READY
`COUPLED_ISOTOPE_NATIVE_CONTRACT` node at PR219 base
`5a1e5220b301a1c497f2863d6fd823e605faba80`. This reviewer did not author or
modify CONTRACT.md, check_contract.py, fixtures, or producer evidence. Review
was read-only except for this file and `evidence/INDEPENDENT_REVIEW.json`.
No subordinate reviewer, cosmological IVP, historical sweep, or diagnostic
rerun was launched. A small read-only JSON inspection checked the observed
evidence and source projections without replacing the producer output.

Requested role: independent Astra-tier scientific review. The session's
instructional model description is GPT-6 Astra Pro; an actual runtime model
identifier is not exposed by the tool output and is not inferred from that
description. Actual skill context read: physmath-research-loop 1.3.0 SKILL.md,
POLICY_INTEGRATION.md, CODING_LOOP.md including C1/C9, repository AGENTS.md,
CONTRACT.md and RESUME.md. The review follows the selected-stage boundary and
finite one-pass stopping rule; it does not mark C2-C10 complete.

## Evidence inspected

The authoritative local checkout HEAD was observed as the stated PR219 base.
Actual nuclear `nuclear_network.py`, `NUCLEAR_NETWORK_CONTRACT.json` and
`EVALUATED_DECAY_INPUTS.json` were read, including mass_table, _q_j, rate_table
and proper-time/event conventions. The PR220 donor's actual atomic code,
atomic_model.json, compact_system.py and FROZEN_CONTRACT.md were inspected.
The final diagnostic source, fixture provenance, ALGEBRA_CHECKS.json,
EXECUTION.json, SOURCES.md and symbolic result were read.

The finite run reports exit 0 and 191 of 191 checks PASS, including 34 directed
integer stoichiometry checks, 16 source-alias checks, four beta endpoints,
102 manufactured mass-reference checks, seven energy controls, four EOS
checks and four quotient checks. All accepted floating residuals in the
record are zero against `64*binary64_epsilon = 1.4210854715202004e-14`.
The intentionally double-booked Q ledger has normalized residual 1/3 and
`accepted=false`; its enclosing negative control correctly passes. Missing
daughter probabilities, missing energy partition, duplicate beta ownership
and fractions at zero inventory are rejected.

A read-only consistency inspection confirmed that all 18 fixture families
are exact projections of their inherited source fields, the isotope order/A/Z
arrays agree, all six available source readbacks are BYTE_MATCH, and current
diagnostic/contract bytes match the recorded execution identities. These are
input/provenance checks, not substitutes for physics validation. The measured
run used 0.021744148 CPU seconds and 11904 KiB peak RSS, with no subprocesses
or cosmological IVPs, within the stated cap.

## Scientific assessment

1. **State and charge.** The ordered 21 states represent every charge of the
   eight inherited nuclear species, including initially absent n and T.
   Absolute abundances avoid dividing by absent tritium. For a neutral closed
   cell with no positrons/negative ions, `delta_e=q dot nu` and
   `delta_e+delta_N_bound=Z dot nu` are correct. The neutral-T shakeoff
   endpoint has two new free electrons and one fewer bound electron, hence
   only one additional total electron, as required for beta-minus decay.
   The inherited strong/EM and beta stoichiometry retain exact baryon balance.

2. **Rates and time.** Proper-time event rates have units events per baryon
   per second; the binary `n_B k` and multiplicity-factor convention and
   `d/dx=H^-1 d/dt` for H>0 are consistent. The coupled single-beta-owner
   requirement is necessary because the donor atomic RHS already includes
   its decay matrix. The actual two tritium definitions differ by about
   0.06711455 percent in lambda. This creates a future composition hazard;
   it does not invalidate the old zero-T pilot.

3. **Mass and energy.** The actual nuclear code uses bare masses and subtracts
   electron rest mass for beta-minus. Its legacy Li approximation is correctly
   retained. The derived neutral-reference identities have the correct signs:
   `Q0=Qbare+sum(B0 nu)` and `Qavailable=Q0-Delta I=Qbare+sum(B nu)`.
   The manufactured tests confirm algebra only. The event ledger includes
   ionization, excitation, fast, radiation and neutrino ownership without
   counting Q twice. Fast stopping is a signed reservoir transfer. RR/DR
   number coefficients alone do not supply a thermal energy moment.

4. **Thermal EOS.** For the declared classical nonrelativistic common-T
   thermal pool, differentiation of `(3/2) k_B T C_th` yields the stated
   temperature equation. A capture can reduce the nucleus count while
   preserving the free-electron count; the `H1II+n -> DII` fixture explicitly
   detects the erroneous electron-only particle derivative. The adiabatic
   slope -2 and manufactured threshold-photoionization T/2 limit are sound
   within that EOS. Total electrons and thermal electrons remain distinct
   when nonthermal products exist; their transport/stress closure is not
   silently supplied.

5. **Quotient.** The product-rule source term
   `(S_Aq-f_Aq S_A)/Y_A` is correct for positive isotope inventory. Shared
   electronic generators do not ensure shared fractions with unequal source
   terms. Aligned injection is a valid surviving special case. The actual
   donor lift fixes n/T rows to zero, so a positive T source leaves its image.
   This is a counterexample to that fixed map, not a strong no-go result for
   all smaller representations.

6. **Source and claim boundaries.** The primary Frolov arXiv abstract was
   independently opened and confirms secondary-electron continuum final
   states. The Williams/Koonin DOI resolver was inaccessible to this reviewer;
   the parent's explicitly limited abstract intake is recorded in SOURCES.md.
   No branch probability or new physical correction is adopted. The symbolic
   warning is preserved alongside its three zero residuals. Neither symbolic
   output nor manufactured dyadic fixtures is misrepresented as a physical
   mass/rate/trajectory validation. PR219, PR220 and REC119 cohorts remain
   separate and their old admissions are not enlarged.

## Current finding and next action

Concrete current-task defects: **none found**. No optional additional gate or
historical rerun is justified. PASS permits the next selected **C2** work to
map actual charge-resolved providers and energy moments to a conditional
native event interface.

Future provider obligations remain: charge-conditioned daughter probabilities
and excitation/continuum yields; applicable charge-resolved reaction/decay
models; a consistent physical mass/binding table; RR/DR energy moments;
nonthermal transport, stopping and stress; and generated-photon closure.
These are material conditions for coupled production, but not missing C1
deliverables. The future implementation must remove the legacy atomic decay
owner in the coupled path while preserving historical helpers/results.

The final `REPORT_KO.md` received a compact scope read within this same pass.
Its equations, measured decay discrepancy, diagnostic counts, manufactured
limits, separate cohorts, and unresolved provider statements agree with the
reviewed contract and observed evidence. It does not claim that the coupled
production RHS was implemented or that a new cosmological trajectory ran.
