# REI C16B: H/He photo + RR/CI + thermal/escape bookkeeping research bridge

2026-10-16 (KST) | Independent source-bound C16.0B research lane, **not production**.

This portable archive replays the exact source-aware photon–gas photoionization module from `rei_bianchi` PR #154, then adds a deliberately *manufactured-rate* positive reaction operator for RR and CI, proper-H-normalized thermal/binding/escape ledgers, and a read-only `IgmPhotoInput` mapping for the real PR #150 native chemistry owner. It does not modify a production Rust source, launch an active NCP run, or silently promote fake rate coefficients to physical data.

## Source authority

- PR154 source commit `daf653e87a5b208ed6f51113e83d56fec4abf4f8`, parent PR149 `d5246c500522ffe4efe904f3206a60f9541c7dbd`.
- Byte-exact immutable `source_aware.py` Git blob `db822a53da3ccdca7cf96628e9ef3bbcec83db5a`, SHA256 `f4c5ff49f9e09a2123f3830160e857beb9c224deafc9ff379d6199829013bbf4`.
- PR150 native source HEAD observed `fe789b0b13b1883c5a74cbc907f72f6f963a5d66`, **snapshot only**, not an assumed present HEAD at handoff execution.
- Native `igm_rates.rs` blob `dc3cc028a41ac852d94835372ce13545389d1c3a`, `igm_thermal.rs` blob `0648618d9822e169e9672ac3c556f86595c3b0b6`, `igm_state.rs` blob `437365fbe329a10afe292f9dd7eebf549fef804c`.
- Original Verner 1996 photo-fit three rows and separate NIST physical binding energies are preserved in the byte-identical PR154 donor mirror. RR/CI manufactured numeric rates in tests are **not** Grackle source values.

## Mathematical model, conventions, claims

Signature `(-,+,+,+)`, LRS Bianchi I `ds²=-c²dt²+a²[e^{-2b}(dx²+dy²)+e^{4b}dz²]`. Here source-free Killing photon `E_j=q_j R_j/a`, `R_j²=(1-μ_{j0}²)e^{2b}+μ_{j0}²e^{-4b}`. Photon populations and the five gas species are number **per hydrogen nucleus**; proper `n_H` is in `cm⁻³`; time is proper seconds. Energy is `eV/H`.

At each ionization edge i=0 HI, i=1 HeI, i=2 HeII, neutral target X=(HI,HeI,HeII), incident ion I=(HII,HeII,HeIII), free electron count `e=HII+HeII+2HeIII`. The strictly owner-separated rates in each channel are

- photon: `P_ij = c n_H sigma_i(E_j) N_j X_i`;
- collision: `C_i=n_H beta_i(T) e X_i`;
- recombination: `R_i=n_H alpha_i(T) e I_i`.

Photo nodes use the unchanged PR154 positive Verner operator. For frozen `n_H`, nonnegative fixed coefficients, RR exact subflow solves `dI/dt=de/dt=-k I e`, reusing `source_aware.exact_pair`. CI exact subflow solves `dX/dt=-k X e, de/dt=+k X e`, with

`X(t) = X0 (X0+e0) exp(-k (X0+e0)t)/(e0+X0 exp(-k (X0+e0)t))`, interpreted as constant when e0=0 and by the continuous limit for zero exposure.

Both preserve reaction positivity, original H/He nucleus totals and the stated electron/ion stoichiometry, and are composed with Strang half-steps. The splitting has formal second order only for the **frozen coefficient, fixed-background** ODE model; changing T-dependent coefficients requires a separate source-native midpoint/implicit analysis.

The energy functions are

`B = chi_H HII + chi_HeI (HeII+HeIII) + chi_HeII HeIII`,
`Uγ = Σ_j N_j E_j`, `Utotal=Uγ+Uth+B+Uesc`.

For each photo event: `ΔUγ=-E`, `ΔUth=E-χ`, `ΔB=+χ`. For each CI: `ΔUth=-χ`, `ΔB=+χ`. For each RR: `ΔB=-χ`, `ΔUth=-ξ_RR`, `ΔUesc=χ+ξ_RR`. The per-event `ξ_RR≥0` is an externally supplied kinetic-energy debit; it is **not a physical Grackle cooling proxy until bound to the actual native `rr_cooling / rr` owner**. The escape radiation is bolometric-only with unknown photon spectrum, not injected into the UV inventory. The photon number ledger counts only photo-consumed photons. The baryon recoil Euler partner is unimplemented. Geometry work is booked exactly once with the PR154 Killing map.

This synthetic transaction checks

`Utotal(before) - Utotal(after) - W_geometry ≈ 0`,
`Nγ(before) - Nγ(after) - Σ photo_events ≈ 0`,
`e_after - e_before - Σ(photo+CI-RR) ≈ 0`

alongside nonnegative states and invariant H/He totals. Insufficient kinetic/CI energy is **rejected**, never repaired by clipping a nonphysical state.

## Real tests & numerical status

The package includes two actually run test sets: **29/29 new** Python physics/adapter tests and **22/22 unchanged PR154 tests**, with exit code 0, source-only provenance. New tests include independent DOP853 state ODE, exactly soluble CI logistic semigroup, absence of free-electron CI, RR Esc radiation routing, HeI→HeII→HeIII, photo-only parity to immutable PR154, positivity/charge/nuclei/energy, rejected insufficient thermal energy, units and native `IgmPhotoInput` conversion. The actual numerical refinement and wall time measurements are in `evidence/study_results.json`. The measured last-five slope is 1.9993293411871906; at 256 substeps the maximum absolute mixed-state error is 5.899466941628e-7 and the energy closure residual 2.56e-13 eV/H. A local 32-case serial versus 2-process sweep produced byte-identical deterministic science JSON; this does not establish NCP scaling. Wolfram exact CI ODE/IC/asymptotic/ledger identities: `{0,0,0,0}`; see `contracts/verification.wl`.

**No user Ubuntu or NCP scientific job ran in this invocation.** Remote Desktop Commander returned a monthly usage-cap error, with instruction not to retry/reconnect. Native subagent tools are unavailable (NOT_RUN), so all executable research was performed in the sandbox. The original NCP full FLRW campaign in PR150 was not altered or polled through untrusted historical state.

## Reproduce independently

```bash
cd REI_C16B_THERMAL_REACTION_HANDOFF_20261016
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
./verify.sh
```

`verify.sh` revalidates the Git blob identity of PR154 `source_aware.py`, runs 29 new + 22 original tests, runs the independent DOP853 study and regenerates its plot; no network required after dependencies are installed. Codes require Python >=3.11, NumPy/SciPy for independent reference, matplotlib for the plot. `codex_handoff_prompt.md` and `NCP_EXECUTION_KO.md` contain the exact native binding/physical admission instructions and the concrete read-first DAG.

## Publication-grade claim boundary

`derived`/`symbolically checked`: closed-form CI and eventwise conservation conditional on rates. `numerically checked`/`implementation-verified`: only this frozen-rate reference and exposed native input mapping. `unresolved`: physical T-dependent Grackle parity, CE/DR/freefree/CMB, actual Case-A recombination photon spectrum or thermal cooling, source-time histories and active+passive photon placement, baryon recoil, two-way Einstein work and full z20→4 reionization history. Scientific production admission **NOT_ISSUED**.

Literature: Grackle Smith et al. (2017) MNRAS 466, 2217, DOI 10.1093/mnras/stw3291; Mellema et al. (2006) New Astronomy 11, 374 DOI 10.1016/j.newast.2005.09.004; Friedrich et al. (2012) MNRAS 421, 2232 DOI 10.1111/j.1365-2966.2012.20449.x; Verner et al. (1996) ApJ 465, 487, DOI 10.1086/177435. Source claims are not inferred from these abstracts alone and are bound to actual referenced code interfaces.