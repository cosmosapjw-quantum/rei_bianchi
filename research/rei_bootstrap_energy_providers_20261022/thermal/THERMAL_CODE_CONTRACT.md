# Frozen bounded scalar implementation contract v1

Authority: `/root/thermal_contract`, 2026-10-22. Paired equations: THERMAL_DERIVATION.md. Final execution baseline observed: `3e56bbd3d939ab235df2d47f9d012c95674d00fc` in `/workspace/scratch/d5baa30c266d/rei_isotope`, per controller's settled existing-checkout choice. Earlier inspection of rei_bianchi at8be7533 is intake context only. New files only: `research/rei_bootstrap_energy_providers_20261022/thermal/`. Existing production files, recovered evidence and old83 are read-only. No staging/commit/publication or branch switching by this worker. Sibling changes must be preserved.

## Implementable scope

Use standard-library Python, no new dependencies, no IVP, quadrature campaign, source download, provider fit, closure choice or production coupling. Implement `thermal_ledger.py`, `test_thermal_ledger.py`, `run_checks.py`, and generated `THERMAL_SCALAR_RESULT.json` / `THERMAL_SCALAR_RUN.log` in the owned directory. Functions may use dataclasses or plain dicts but must expose these operations:

1. `particle_sources(stoichiometric_sources, cumulative_thresholds, charges)` returns S_heavy=sum S_i, S_e=sum q_i S_i, Q_B=sum I_i S_i for **fully thermalized atomic populations only**. The gas function separately accepts S_heavy and S_e so a nuclear/nonthermal caller never silently uses the atomic shortcut.
2. `gas_rhs(n_part,T,H,S_heavy,S_e,Q_kin,k_B)` returns U, P, dot n, dot U, dot T from the paired equations. Require finite inputs, n_part>0, T>=0, k_B>0. Sources and H can be signed. Isotropic gas only; do not add matter/radiation stress to its heating.
3. `photo_event(R,A,chi,thermal_fraction=1)` returns a single allocation record with gas=f(A-chi R), binding=chi R, radiation=-A, nonthermal=(1-f)(A-chi R); other owner entries zero. R,A,chi>=0, 0<=f<=1, A>=chi R. Threshold checks use exact arithmetic for exact fixtures and otherwise a documented roundoff allowance 64 machine epsilon times max(abs(A),abs(chi R)), permitting only roundoff-sized negativity to be treated as zero. Reject materially subthreshold energy; no broad clipping.
4. `rr_event(R,C,chi)` returns gas=-C, binding=-chi R, radiation=C+chi R; R,C,chi>=0. Photon component means bolometric complete prompt cascade. No fake spectrum or one-photon-per-capture claim.
5. `band_rhs(N,U,p_radiation,H,s,C_N,C_E,F_N,F_E)` returns dot N=C_N-3HN-F_N, dot U=C_E-4HU-6sp_radiation-F_E. p_radiation is signed. This is a supplied-moment evaluator, not a closed angular/spectral operator. Keep any p_matter in a separate component-work helper `3H(epsilon+P)+6sp`; never merge named input fields.
6. `exchange_residual(allocation)` sums unique owner sources. A small generic allocation constructor may accept the named owners gas,binding,excitation,radiation,nonthermal,neutrino,nuclear_rest,emitter plus external_power; closure is sum(owner sources)-external_power. Reject duplicate owner entries if a list representation is used. Do not invent nuclear event data: tests use explicitly synthetic numbers.

Zero event rate R=0 requires A=0 in PI and C=0 in RR; reject inconsistent positive moments. Finite inputs are required throughout. This is consistency of supplied moments, not a new microscopic provider.

## Changed-only checks and independent expected values

Reuse the published29 receipt and review by reference; do not relabel or rerun them. New tests must cover these eight nonzero targets:

T1: k_B=1,n=2,T=3,H=1/10,S_heavy=3/10,S_e=1/10,Q=5. Expected S_part=2/5, dot n=-1/5, U=9,P=6,dot U=1/2,dot T=7/15. Reverse chain rule gives dot U=1/2. Distinct heavy/electron fields must each influence the result.

T2: ion stages q=[0,1,2], I=[0,3,8], S=[-2,1,1] give S_heavy=0,S_e=3,Q_B=11. This is synthetic atomic stoichiometry.

T3: PI R=2,A=22,chi=3,f=1/4 gives gas=4,binding=6,radiation=-22,nonthermal=12,sum=0. Subsequent separate deposition gas=12,nonthermal=-12 conserves total without resending absorbed radiation.

T4: RR R=5,C=10,chi=3 gives gas=-10,binding=-15,radiation=25,sum=0. Capture-level fixture chi_l=1 would allocate free-bound=15 and cascade=10; they sum to25 but must not be represented as a predictive spectrum.

T5: anisotropic fixture from paired derivation: N=4,U=26/3,p=26/45,H=1/2,s=1/4,C_N=C_E=0,F_N=-24/5,F_E=-78/5 gives dot N=-6/5,dot U=-13/5. Compute its expected angular integrals analytically in test comments or with exact Fraction polynomial moments; do not copy the production RHS to obtain its expectation.

T6: shared interface J=-7/3 (energy) and K=-2/3 (number); first band's upper contribution F=(K,J), neighbor's lower contribution F=(-K,-J), hence boundary-only dot terms cancel. Reverse J,K signs and preserve cancellation. Both bands retain their own 4HU+6sp work; specify e.g. U=(2,3),p=(1/5,-1/10),H=1/2,s=1/4 so combined work=203/20. A cumulative counter is not used.

T7: synthetic nuclear allocation nuclear_rest=-10, gas=2, nonthermal=3, radiation=4, neutrino=1 has sum0, binding=0. Separately supplied gas S_heavy=-1/5,S_e=2/5 at n=2,T=3,H=0,Q=0,k_B=1 gives dot T=-3/10. These are ownership arithmetic examples, not a physical nuclear reaction.

T8: independent massive and radiation amplitudes s=2,p_matter=-3,p_radiation=5 yield shear works -36 and60, total24. External radiation +9 with external_power9 closes an open-system residual; adding emitter=-9 and external_power0 closes its extended system.

Use Fraction for rational expected values when useful. For floating dimensional comparisons, tolerance is 64*sys.float_info.epsilon times the sum of absolute terms in the tested identity. If the sum is zero require exact zero. Do not use a dimensionless default1 floor on SI energy residuals. Report maximum normalized residual and actual check counts. Validate representative invalid n, fraction, negative rate and materially subthreshold inputs.

Mutation/discrimination controls: independently omit S_heavy in T1, omit nonthermal in T3, omit shear in T5, omit boundary in T5, and omit neutrinos in T7; each must exceed the same residual threshold. These controls change a test candidate only, never production files. Check SI rescaling of T3 by an energy factor 1e-23 to ensure the criterion still detects a missing channel. No optional test expansion after these risks are resolved.

## Execution and stopping rule

From the owned directory run `python3 -m unittest -v test_thermal_ledger` and `python3 run_checks.py`. Each invocation wall limit60s, memory expectation below128MiB, no integration attempts. Controller may cap total lightweight execution at120s; preserve actual wall time and exit codes, including failures. One targeted implementation repair is permitted for a mechanical defect under unchanged equations; ambiguous physics/tolerance/input identity returns to authority. If a stated bound is inadequate stop with actual evidence rather than enlarge the run.

Receipt: actual interpreter/version, requested versus observed executor identity (unknown stays unknown), baseline HEAD and dirty-path summary, exact commands/exit/wall, changed files, tested fixture IDs, residuals, discrimination results, counts, reused29 reference, physical_IVPs=0, old83_reruns=0, NCP_runs=0. Classification is EXECUTED_SCALAR_CHECKS_PENDING_INDEPENDENT_REVIEW until fresh Astra authority reviews raw source/diff/results. PASS leads to integration of this scalar research module; predictive provider, spectral, coupled and production claims remain at their inherited state.
