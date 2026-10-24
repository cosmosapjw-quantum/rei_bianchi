# REI C3: zero-onset and tiny-stock local source representation

Status: FROZEN_FOR_LOWER_TIER_IMPLEMENTATION after root acceptance. This unit selects the numerical-design part of C3, with R4–R5 construction and C1–C3 framing. The finite code probe is the evidence for that design, not completion of the whole coupled C3–C10 program.

## Source and task boundary

- Repository: cosmosapjw-quantum/rei_bianchi.
- Branch: research/rei-coupled-isotope-contract-20261022.
- Current checked HEAD: c1714f82ea7de15fee230a1a995365970ee6dc02.
- Root tree: dd1ce4d9870c86e30823e15ecf6a05436a811367.
- Input: c3_probe/input/BINDINGS.json, copied from research/rei_coupled_isotope_mapping_20261022/BINDINGS.json at that HEAD. Git blob a2a49cacaac248e5d65408824c9f4f4bc373a693 was verified locally.
- Read its 21 slots as the source of index/name/A/Z/q; do not copy a guessed order.
- Root's current StandaloneDossier(4) sections1.2–1.3 define17 states: n,H0,H+,D0,D+,T0,T+,He3(0,+,2+),He4(0,+,2+),Li7(0,+,2+,3+). Map these explicitly to the21-state indices [0,1,2,3,4,5,6,7,8,9,10,11,12,17,18,19,20]. The additional21-state slots13–16 are Li6. A projection to17 states omits their inventory; do not renormalize it away or replace baryon-weighted A.Y=1 by an unweighted Markov normalization. Be ancestry remains separate.
- Pre-node current PR221/219/199 refs and the newly found C2 Dropbox archive are recorded in PRE_C3_REFRESH.json. No branch movement was observed.
- Allowed new implementation/evidence paths: orchestration_20261022/lanes/rei_bianchi/c3_probe/ only. Input and this frozen contract must remain unchanged.
- No production source edits, atomic donor edits, old evidence rewrites, old diagnostic reruns, new ODE/IVP, rate-builder call, or NCP action. Root handles publication.

AGENTS.md at the pinned HEAD says: “A lower-tier coding agent owns only implementation, targeted tests, bounded builds/runs, raw-result preservation, mechanical evidence assembly” and “The controller must give the coding agent the frozen base identity, allowed paths, limits, commands, controls, and stopping rule. It must then send the observed diff and raw outcomes to a fresh Astra-tier reviewer before any scoped scientific admission or publication decision.” It also says to reuse the existing checkout and not create another clone/worktree. The full observed policy is intake/AGENTS.md.

Implement with Python standard library only; no package installation or compiled library is needed. The requested execution role is lower-tier; report actual model identity only if exposed.

## Physical problem and simplification

C2 already proved the number/energy source bindings and beta-owner boundary. The new issue is representational: n and T begin at exact zero, whereas saved conditional inventories can be near 1e-104. A fixed isotope-fraction quotient with n=T=0 cannot carry their injection. Absolute abundances Y_i=n_i/n_B avoid division by the isotope inventory.

A finite physical rate can underflow if multiplied before a scale division. That is a numerical representation defect, not an absent physical channel. Use logarithms for positive event products, and an explicit exact-zero branch for zero reactants. Retain the event log even if a requested binary64 projection becomes zero. This costs O(number of event reactants + nonzero stoichiometric entries); no 21-by-21 dense reaction network solve is required.

This probe has supplied, explicitly MANUFACTURED event coefficients and charge endpoints. It does not infer physical daughter probabilities. All reactants/products lie in the 21-slot set. The local independent variable is proper time in seconds. No H or cosmological scale factor enters this module.

## Mathematical definition

For an event, integer reactant multiplicities m_j and product multiplicities p_j give nu_j=p_j-m_j. Require A.nu=0 exactly. The event is unary (sum m=1) or binary (sum m=2). Coefficient k has units s^-1 for unary and m^3/s for binary. With positive n_B:

R = k n_B^(order-1) product_j(Y_j^m_j) / product_j(m_j!).

R is events per baryon per second. This includes the 1/2 factor for identical DD reactants; coefficient convention is frozen to this definition.

Use supplied finite log(k), with independent applicability status:
ACTIVE, SUPPORT_ZERO, ABSENT, or UNRESOLVED.
SUPPORT_ZERO and ABSENT produce different explicit statuses although both have zero contribution.
UNRESOLVED must return/raise an explicit unresolved-input result, never a zero source.
For ACTIVE, any zero reactant produces ZERO_REACTANT and exact R=0; otherwise

ell_R = log(k)+(order-1)log(n_B)+sum m_j log(Y_j)-sum log(m_j!).

An ACTIVE positive event with ell_R below binary64 projection range remains mathematically positive; mark its raw projection UNDERFLOW, retain ell_R, and continue scaled evaluation. Do not classify it SUPPORT_ZERO. No rate extrapolation or interpolation is performed in this finite C3 subnode.

Choose fixed positive slot scales s_i, independently supplied by the fixture, and u_i=Y_i/s_i. Then

F_i/s_i = sum_e nu_ie exp(ell_Re-log(s_i)).

The physical bookkeeping per event is exact integer data:
delta_e=q.nu;
delta_bound=(Z-q).nu;
delta_N=ones.nu;
delta_C=(1+q).nu in the all-thermal limit.
Require delta_e+delta_bound=Z.nu and A.nu=0. A thermal/fast partition, energy moment, or temperature derivative is not inferred by this probe.

Use math.fsum over signed contributions for accumulation. For conservation testing reconstruct each event in Decimal and use exact integer stoichiometry; do not “pass” a balance by allowing every tiny raw number to underflow to zero.

The scaled Jacobian is J^u_ij = (s_j/s_i) partial F_i / partial Y_j, with fixed scales. For positive reactants, compute from the event log and exponent m_j, but do not divide by Y_j at exact zero. The boundary formula is the polynomial derivative:

partial R/partial Y_j =
k n_B^(order-1) m_j Y_j^(m_j-1) product_(l!=j) Y_l^m_l / product_l(m_l!).

Evaluate this by the same reduced-exponent log-product rule. A remaining zero factor yields exact zero. A multiplicity-one derivative at Y_j=0 can be nonzero; the DD derivative at D=0 is zero. These endpoint facts are the principal independent analytic oracle.

## Required finite fixtures

Use explicit integer reactant/product maps and label every fixture MANUFACTURED. No claim is made that the chosen coefficients are astrophysical.

1. Ordinary DD: 2 DII -> TII + H1II, Y_DII=0.02, n_B=3, k=2e-20, TII initially exactly zero. Require positive T source and exact event baryon/charge balance. Verify the identical-reactant 1/2 factor against Decimal.
2. Tiny DD: same reaction with Y_DII=1e-104, n_B=1, k=1 and target scales s_TII=s_H1II=s_DII=1e-104. The event is positive and representable in raw/scaled projections; compare both to Decimal.
3. Underflowing unary beta endpoint: TI -> He3II with Y_TI=1e-104, k=1e-230, s_TI=s_He3II=1e-104. Raw event R near1e-334 underflows, but scaled sources near +/-1e-230 are nonzero and accurate. Store logR and UNDERFLOW. This is a manufactured coefficient and a supplied endpoint; it does not replace physical beta constants.
4. Zero-stock unary endpoint: same event with Y_TI=0. Source must be zero, and the scaled Jacobian must equal the nonzero analytic decay derivative.
5. One-zero binary onset: DII + H1II -> He3III with Y_DII=0, Y_H1II=0.5, n_B=1, k=1e-100, s_DII=s_He3III=1e-104. Source is zero but d(F_He3III/s_He3III)/du_DII is positive, about5e-101. delta_N=-1, delta_e=0, delta_C=-1.
6. DD zero boundary: Y_DII=0. Both event and its first derivative are zero.
7. The same event declarations with SUPPORT_ZERO, ABSENT and UNRESOLVED verify distinct status behavior. An intentionally nonconserving stoichiometry must be rejected.
8. A moderate two-event sum checks scaled Jacobian against central differences in u only where all perturbed inputs stay positive. No finite difference is used to certify a zero boundary or the underflow fixture.
9. Negative control: naive raw multiplication before scale division returns zero in fixture3 and is rejected by the positive scaled oracle. Negative control: applying the quotient derivative R/Y at the exact-zero fixture does not supply the correct nonzero boundary derivative. These controls should demonstrate the observed failure mechanism without altering the accepted implementation.

For full 21-slot vectors, unspecified slots are zero. Tiny manufactured fixtures need not satisfy cosmological A.Y=1 because this is a homogeneous local operator and no background density inference is performed. For the ordinary DD fixture, set H1I to complete A.Y=1 without changing its reactants. Add one projection control with Li6I=1e-8, compensate H1I by6e-8 to retain full A.Y=1, and verify that the17-state projection has baryon deficit6e-8, exactly the omitted Li6 inventory contribution within the roundoff criterion. Never renormalize that projection.

## Acceptance and evidence

- Independent oracle: decimal.Decimal at precision100; construct Decimal values from the declared decimal strings, not from already rounded products. Decimal.exp/ln may evaluate finite log coefficients; for fixture oracle use the direct decimal k strings to make it independent from the log implementation.
- All exact stoichiometric identities must equal the integer reference exactly.
- Positive representable scaled rates/sources/Jacobian elements must agree with Decimal within relative2e-12. No absolute floor may hide their tiny size.
- Moderate summed sources: absolute error <=2e-12 times sum of absolute reference event contributions, with exact zero where that denominator is zero.
- Moderate central-difference Jacobian controls: relative2e-7 with step1e-5 times a scale-aware moderate u coordinate. Explain the finite-difference truncation/roundoff scope. This does not certify off-grid rates or trajectories.
- Required positive/zero/unresolved/underflow statuses must match exactly.
- Store individual fixture inputs, Decimal references, outputs, errors, tolerances and statuses, plus both negative controls; do not report only a total test count.
- Record command, Python version, exit code, wall and CPU time, max RSS if available, source/input SHA256, and one invocation. No benchmark/speedup claim.
- Total scientific execution cap: wall30s and CPU30s, one process, no numerical thread pool, 256MiB address-space cap if straightforward. The parent may enforce timeout. The expected run is substantially below1s.
- On substantive failure, preserve raw evidence and stop for interpretation; no automatic tolerance widening, model change or rerun. Root may authorize one targeted repair within the same cumulative cap.

Deliver local_source.py (or similarly small module), run_probe.py, RESULT.json, EXECUTION.json, stdout/stderr and short IMPLEMENTATION.md. Tests may be in the runner rather than a separate suite. Run once under the prescribed cap; do not import or rerun old C1/C2 code.

## Positive transition and remaining work

A scoped PASS supports this local representation and the manufactured zero/tiny-stock controls only. It enables the next small event-assembly implementation using supplied charge branches and provider-matched coefficients. C3 still needs an off-grid coefficient policy and full thermal/fast Jacobian dependencies before its complete numerical design can be claimed. Physical daughter branches, mass/binding consistency, DR moments, photon/fast transport and coupled production remain open inputs. D10 zero-initial matter stress is a separate ready theory/saved-data node and is not run here.
