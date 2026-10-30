# F4 / BASS21 → retained17 static F,J, Li6 electron reservoir

2026-10-30, bounded source-owned node after immutable Draft PR278 (HEAD 197b09a4439fb16d462a7ccced9a0f1cfaad4203). Read-only sibling PR277, immutable source parent PR276 (HEAD 970175ffce1e1139b911a1f45bee9271a69153b9).

**Qualified claim:** Actual original BASS21 193 archived epochs and native atomic coefficient loader used for 21×21 F/J and 17×17/17×4 Li6 source blocks. **Not** a numerical common-source REI17↔BASS21 full F/J calculation: the REI17 all-channel native F/J and truly common ion/electron/thermal/photon/clock state are not bound. Source-matched cross-owner commutator = BLOCKED_INPUT. New IVPs 0.

## Original source and dimensions

- Original BASS owner commit cc602e209e7deeb511ab2a1f3b2268d55206c43c; network Python SHA256 baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80; saved 193-epoch BASS21 trajectory SHA256 37d1bab173e81449cf474b21a678077edd0150cf0b2cb386d014764580678086.
- Exact PR278 master full source archive, 4,716,410 bytes, SHA256 df871a18f297da15d05a5dadbad55e2aa29571217ad9136d9c4826921d1a11db.
- Original 129 rate coefficients are a prior **numeric source projection** from Git blob 2eba600a9d7a7359ca55f566f1b841a363a3e5c7. Whole original coefficient JSON byte identity is not asserted.
- Original Y=n_i/n_b, proper time t; ne=nb qᵀY, T/UV/nb/H held at actual saved epoch. Split U=original BASS indices 0–12 and 17–20 (17 states), V=13–16 (Li6 I–IV). The BASS actual n/T pilot has zero n and T, and Li6 isotope total conserved. This is not REI ON_refined 300 K.
- Native generator A=G0+D in s^-1 and B=Gne in m³/s. Native F21=(A+ne B)Y [baryon^-1 s^-1], J21=A+ne B+nb (BY)qᵀ [s^-1]. Both A and B have **exact zero** direct U↔V blocks at all 193 source epochs.

With u=Y_U, v=Y_V and e_v=q_vᵀv, define a **hypothetical BASS-only** 17-state restriction F_u0=(A_uu+nb(q_uᵀu)B_uu)u. It is not the REI17 F. Then exactly at fixed T,UV,nb:

\[
P F_{21}-F_{u0}=n_b e_v B_{uu}u,\qquad
J_{uu}-J_{u0}=n_b e_v B_{uu},\qquad
J_{uv}=n_b (B_{uu}u)q_v^\mathsf T.
\]

J_uv has rank ≤1, first Li6-neutral column zero. For identical u, Li6 nucleus stock N6, the two physically allowable Li6 charge allocations all-neutral and all-Li6³⁺ yield a different projected F:

\[
\Delta F_u=3n_b N_6 B_{uu}u.
\]

The source-native pilot evaluates this difference nonzero. Thus u alone is not an exact closed BASS chemical state in the presence of the shared electron pool. Retaining e_v is required for this RHS closure, **but** does not close the evolution of e_v itself since its Li6 charge generator depends on full v. This is a bounded constructive counterexample, not a generic chemistry no-go theorem.

## Actual 193-point maxima

| Quantity | value | z |
|:--|--:|--:|
| Li6 omitted electron/baryon | 2.258620986823887e-14 | 2.0000 |
| Max Li6 share of total electrons | 5.003009841582314e-11 | 16.4981 |
| RHS defect max [baryon^-1 s^-1] | 7.19681972382632e-30 | 9.12296 |
| J_UU defect max [s^-1] | 1.7329878339767385e-27 | 20.0 |
| J_UV cross max entry [s^-1] | 3.0596290097298003e-15 | 9.22608 |
| Two-lift same-u witness max [baryon^-1 s^-1] | 2.3098803794671163e-29 | 9.22608 |

All 193 epoch source rows and 21×21,17×17,17×4 data are in the source-contained master result ZIP. The cross-Jacobian differentiates with respect to **unit** Y_Li6; multiplying by actual Li6 abundance is required for interpreting its physical impact.

## Validation and failure record

- Local full analysis script and frozen-source output: Python new **10/10 PASS** including original SHA, model topology, 193 CSV rows, source events, conservation, exact Jacobian factorization, independent finite difference of native BASS.evaluate, and two charge-lift test. Wolfram abstract exact shared-electron J-block residuals zero. Native F21 generator max absolute residual 9.86e-32 and J21 3.16e-30 s^-1.
- Subtracting two ~1e-12 matrices to resolve a ~1e-27 J defect lost relative precision. An initial overly strict subtraction test failed; changed to explicit machine-roundoff *parent scale* guard. The reported ΔJ is computed directly from its exact algebraic factorization, cross Jacobian independently checked. This is not a full independent R6/C9 test. No physics input/rate was changed.
- First source-included result ZIP clean restoration failed on a manifest entry for transient .pyc cache; cache excluded, rebuild, ZIP CRC PASS, manifest 11/11 SHA PASS, clean restore Python 10/10 PASS.
- New minimal Git reproduction code: code/check_bass_static_fj.py, run with Python+NumPy and the immutable PR278 source ZIP as its sole positional argument. This code was executed against the exact Drive source, returning the five numerical maxima in RESULTS.json.
- Complete *new* source-contained result ZIP: 5,239,732 bytes, SHA256 a95bac78f7aa67660289c9a2faf1881a96995ae9f787c1b9134a2aa3e46fd6f0, includes immutable PR278 ZIP, full runnable code/tests, manifest, 193 data rows and 193 array snapshots. Google Drive: https://drive.google.com/file/d/1WBIf8JnEUK05ugDE4Ud-YwF0KnDNKdcN/view (raw provider re-read exact size and SHA); also saved to ChatGPT Library under /REI_F4_COMMON_STATIC_FJ_20261030.
- Distinct-author R6/C9 NOT_RUN; native subagent NOT_RUN. Existing PR278 inherited cargo fmt CI failure is not cured. Original compute budget not reset; unknown host/network overhead not assumed zero.

## Blocking actual full REI17↔BASS21 source matched projection

Current PR278 repo source inspection: rust/rei_microphysics/src/isotope_state.rs is a 13-state non-Li isotope **bookkeeper**, not a 17-state full kinetics owner. igm_rates.rs + igm_thermal.rs provide Grackle H/He only (external photo gamma and separately gas-deposited heat per absorber), and REI 17-state saved-source photo operator has only seven photo events. None is the authorized *full* REI17 Li6/T/nuclear/CR/fast/electron/thermal/radiation kinetics and Jacobian. Previous PR276 HHe source comparison or PR277 photon-energy ledger does not fill the missing owner.

For REI y=Y/rho where rho=nHref/nb, the common-clock transformed BASS vector is dy/dx = PF21/(rho H) - (d ln rho/dx) y. Common rho, H, K, physical isotope inventory, thermal/electron state, UV/radiation, original IC and geometric direction-dependent clock must be sourced before computing a genuine cross-owner F/J and opacity. PR277's Li I 1s Auger/fluorescence branching and heat deposition remains a **separate unresolved source-owner obligation**.

## Gate and stop

- Original REI working **33/88**, central **28/88**, physical-fast **4/7**, **physical Δ0**, F4=PARTIAL, L4_ready=false, NO_MORE_IVPs=true.
- Source-only subnode completed **1/1 qualified BASS internal diagnostic**, not canonical completed node.
- NO_MERGE=true; NO_FORCE_PUSH=true; AUTO_NEXT_NODE=false; NO_BUDGET_RESET=true.
- Next authorized action *outside this invocation*: identify source-authorized same-state complete REI17↔BASS21 native event/thermal/fast/clock source and only then test full static F,J. No new IVP.

Primary conceptual reference: Tóth, Li, Rabitz & Tomlin (1997) SIAM J. Appl. Math. DOI 10.1137/S0036139995293294. This paper is not the data owner for the numerical results above.
