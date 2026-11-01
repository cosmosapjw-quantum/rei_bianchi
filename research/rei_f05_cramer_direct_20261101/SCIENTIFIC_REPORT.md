# REI F05: independent direct-determinant interval enclosure of original [160,161] 26-event H/He physical map
Date: 2026-11-01 (Asia/Seoul). Status: DERIVED + NUMERICALLY_CHECKED + IMPLEMENTATION_VERIFIED_SCOPED, CANONICAL_HOLD.

## Exact source boundary and scientific objective
- Original repository: cosmosapjw-quantum/rei_bianchi, base PREDECESSOR PR348 HEAD fcc90939b6b7cc842fae65d5a0ffbb69a3ec3120 (Draft, no merge).
- Original fixed source: 26-event original H/He MPRK22(1) + Alexander SDIRK2; 46,080 genuine physical spatial cells, 160/131072 accepted ticks.
- Original TAR SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b; original accepted source state array SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01; original native kernel SHA256 579df3cc99987dcce9205166752570bdaf4c7cb3640c525be6da260d94b8e644.
- Original locked local map full-vs-twohalf defect gate: strict 2e-4 for xHII, xHeII, xHeIII and lnT; public output width <2e-3. Historical independent endpoint box lnT max 2.1245050576368385e-4 > gate, FAIL preserved.
- One new scientific object only: independent exact-rational structural derivation + interval Cramer replacement for original PR348 Krawczyk increment linear subsolver; no new plasma model, physics parameters, source tables, environmental ionizing background, original IVP history, solver or observer.

## Derived identity and independent numerical enclosure
Native MPRK final corrector A p_out = p_in with A=I+B gives A delta_p = -(A-I) p_in exactly. For each original H (2x2) and He (3x3) block, det(A) positive over complete original source uncertainty allows Cramer's delta_p_j = det(A_j)/det(A). Numerator, denominator and resulting ratio are outward interval-evaluated with the original source-owner directed IEEE754-nextafter interval type, not BLAS linear solve. Numerical source checks require positive lower determinant on all 46,080 cells in each full, half1 and half2 native map. H and He nuclear population sums enclose 0.
Original thermal-root exactly implies delta_U=h[(1-gamma) R_gamma + gamma R_final], gamma=1-1/sqrt(2); with Npart=NH+NHe+ne and U=3/2 k_B Npart T:
  delta ln(T) = log1p(delta_U/U_in) - log1p(delta_ne/Npart_in).
Both log arguments are positive for all source enclosures. The same original parent cancels algebraically before 3 native increments are composed as D_h=delta_full-delta_half1-delta_half2.

## Reproduced original-source numerical result (three shape lanes)
The three original source-shape lanes all ran to EXIT0 on the connected authorized Linux device with the identical physical source. These are THREE verification pathways over ONE source dataset, not independent observations or 138240 distinct spatial cells.
- 46,080 source cells x 30 physical CSV columns, per lane. All three generated CSV .gz bytes identical SHA256 3cd9d158a74e781da39cf2e2a6424ce5b1bd147be226a0c0070ebbb5e846d635.
- max |D_h lnT| upper 3.8632410543996545e-6; max |D_h xHII| upper 3.5398334803019514e-6; max |D_h xHeII| upper 2.3168783273159162e-6; max |D_h xHeIII| upper 2.5228253145328077e-8, all < frozen 2e-4 over 46080/46080 source cells.
- original output max width 2.257243260856967e-4 < 2e-3; original shared-root native full/half maps PASS, no table event, 14/14 original energy/photon/OTS/nuclei ledger PASS.
- PR348 inherited Krawczyk alternative max lnT bound 3.814222131823313e-6, a different, slightly tighter numerical envelope. Neither result retroactively changes historical failed independent endpoint bound 2.1245050576368385e-4.
- Four exact-rational positive/singular negative tests PASS locally normal 4/4 and python -O 4/4. Formal complete BLAS/IEEE rounding theorem NOT_RUN. Original upstream native source validation remains unchanged.

## Hostile scientific review: bounded pass
1. Cramer's rule is an EXACT rational map for point A with nonvanishing determinant. The outward interval determinant/quotient is conservative over independent A and b boxes; source correlations may be lost, but no point realization is excluded. The determinant was certified positive on every original cell and native stage. Inherited interval arithmetic (float64+nextafter) is NOT a separately verified MPFI/MPFR proof; the original native map may still internally use BLAS; only NEW linear increment enclosure bypasses BLAS inversion.
2. Full-vs-twohalf defect measures the original DISCRETE numerical-map comparison, not by itself a validated enclosure of the exact continuum ODE local truncation error. Literature on validated RK distinguishes enclosure of actual IVP flow from a discrete step-error estimate (Alexandre dit Sandretto and Chapoutot, Reliable Computing 22, 2016, pp.78-103, https://interval.louisiana.edu/reliable-computing-journal/volume-22/reliable-computing-22-pp-078-103.pdf). No new theorem of the full 131072-tick trajectory or physical global error is claimed.
3. The source model's original physical 26-event flux/thermal roots are unchanged; three shape lanes share original state, so one numeric source dataset. No instrumental observation or Einstein-self-consistent Bianchi geometry has been inferred.
4. Local native run emits NumPy-1-extension-in-NumPy-2.4.2 optional-import warnings for numexpr/bottleneck, but exits zero, produces the output and passes the native ledger. Record runtime_environment: WARNING, not source physics error or a successful fresh environment repair.
5. Native original acceptance worker still tests independent endpoint intervals and would reject original [160,161]. Adopting the new error estimator requires explicit source-owner gate review and a scientifically equivalent safe code path, not this research audit silently changing original authority. Production HOLD, tick161 NOT_ACCEPTED, original 14 conservation/event/width gates preserved.
6. The independent audit is same-author algorithmic cross-check and Wolfram identities, NOT distinct-author blind referee or formal verified arithmetic. No native subagent dispatch available.

## Direct scientific consequence and drift watchdog
This is a bounded F05 central-blocker investigation, not another source-dependent auxiliary atlas. It does not add any approved central node. CENTRAL 28/88_REPORTED, WORKING 33/88_REPORTED, PHYSICAL_FAST 4/7_REPORTED, canonical delta 0. Next meaningful action: original owner decides whether source-safe Cramer/Krawczyk interval increment direct enclosures meet the original estimator acceptance contract; then exactly one unchanged-source, unchanged-gate [160,161] acceptance retry in isolation. If blocked, stop PR proliferation and switch only to an already-authorized original REI H/He physical DAG milestone.

## Reproducibility and preservation
Code: research/rei_f05_cramer_direct_20261101/direct_cramer_audit.py
Tests: research/rei_f05_cramer_direct_20261101/tests/test_cramer.py
CI: .github/workflows/rei-f05-independent-cramer.yml
Original-local physical source CSV+RESULT per 3 lane: /home/cosmosapjw/archives/rei_f05_direct_interval_audit_20261101/{primary,recomb,shield}/
Original 26-event native solver, source TAR/accepted state and production histories never edited.
DAG: R1-10/C1-10 are stage receipts for ONE science unit, not canonical science node counts. No merge, no force push, no tolerance relaxation, no budget reset, no automatic acceptance.
