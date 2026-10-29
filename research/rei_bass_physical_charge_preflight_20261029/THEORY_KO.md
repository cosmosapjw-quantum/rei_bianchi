# REI↔BASS: source-qualified isotope-inventory obstruction and photo-only exact lumping

2026-10-29 · Theory-first R1–R10, coding C1–C10. Original REI working DAG **33/88**, central last **28/88**, physical delta **0**. `F4=PARTIAL`, `L4_ready=false`, `NO_MORE_IVPs=true`. New result **DERIVED + source-byte-verified + symbolic/numerical checks, not physical τ**.

## 1. Exact source identity and units

Parent REI PR264 `7067a0e73743ce9fb3a07c81bc4207188129985a` derives `e_B M y+ρ y_T+ =ρ q17 y` for selected seven photo events, with `ρ=nHref/n_b` and `x=ln(a/a_ref)`. The present unit does not change this statement. Metric signature (-,+,+,+). Reference populations `y_i=n_i/nHref` in REI, `Y_i=n_i/n_b` in BASS, and BASS `K=GAMMA_PER_NE/10^6` with positive optical-depth equation `τ_x=K n_e/H`. Rate γ in `s⁻¹`, H in `s⁻¹` for log scale factor, and ρ dimensionless. Actual K, nHref, n_b and H numerical time histories are not bound.

In this invocation, the complete BASS PR234 SOURCE ZIP 222443 bytes, SHA256 `6a9c84ce076a3545a992f0b364d0fd67fe1063b7a33a290dbe77d44ecee98838` was retrieved via its previously acknowledged Google Drive object and its 46 members pass CRC. Original `atomic_model.json` SHA256 `9cc399e9e33ece544109f442f50b00c463cde96e406965e796240eaabd49c614`, `atomic_network.py` `baecce07aded483fa60006cc576feff67d068c0d70394f7095abacc6d47eaa80`, `coupled.py` `09a3325c584b895f8c1de44d3b64a458ec7e27f8eec843c7e15aa246a6088d47`, and `compact_system.py` `3ebf56b5a8f1f392681365ec0769364329f293f944a0de4a5add441c8cbc1c49` are verified by raw bytes.

REI PR262 complete SOURCE ZIP 162333 bytes SHA256 `f7c01af8e5d996d0f4e953626e494fb50877387061f4cf0fcbb9c168b203509e` was downloaded from its previously acknowledged Drive object; 73 members pass CRC. Its selected seven `ON_refined` source-row JSON SHA256 `7653f7f75fcbe92465de1b22faabf565efee36e90d1d967499f68ff123a6bc77`, Git blob `46d72047383da10db2d65deea309019d20e915b6`, preserves the 17 heavy-state values (numerical extraction from original 361-row CSV Git blob `189c2d903e25c18bee49e0ab6add3ba1d1805e93`). This selection is **not** the complete 361-row CSV in byte form.

## 2. Actual BASS physical source branch is not absent-T everywhere

BASS original `atomic_network.py` contains all **21** atomic species, including `TI,TII`, in its full62 geometry+chemistry+τ model. The source-pinned `atomic_model.json` fixes its *pilot initial* `T/H1=0` and He4/H1=0.08112582781456953. Its `compact_system.py` explicitly refuses any nonzero initial neutron/T inventory under `NEED_FULL62: nonzero initial neutron/tritium inventory`; compact33 preserves 9 selected atomic entries and reduced30 6 charged fractions, omitting T under this eligibility gate. It also requires equal isotope charge fractions for H1/D, He3/He4 and Li6/Li7. **Thus the omission is a source-selected invariant initial-data submanifold, not an assertion that BASS full62 cannot represent T.**

The original REI saved seven snapshots have *positive* `y_T0+y_T+=4.642253218319375×10⁻¹⁹` at z=2.404494 and `4.642967968776813×10⁻¹⁹` at z=4.701690 per Href, with the intermediate rows positive too. Consequently no `ρ>0` can make the same isotope T inventory equal to the BASS zero-T initial submanifold at those snapshots. This is **source-data incompatibility between two different pilots**, not a universal physical theorem and not an implementation defect of either solver.

## 3. Sharp two-isotope common-normalizer obstruction

For each REI snapshot, let `h=N_H1^REI>0`, `g=N_He4^REI>0` be the sums of charge states per Href. Let `h_B=N_H1^BASS>0`, `g_B=N_He4^BASS>0` be the stored BASS source-initial isotope inventories per n_b. Define `A=h/h_B` and `B=g/g_B`. If both pilots represented the *same isotopic state* with a common positive normalization `ρ=nHref/n_b`, they would require `ρA=ρB=1`. Define instead the best possible maximum *relative isotope inventory mismatch*

`E(ρ)=max{|ρA-1|,|ρB-1|},  ρ>0`.

**Proposition.** For any `A,B>0`, `min_{ρ>0} E(ρ)=|A−B|/(A+B)`, attained at `ρ*=2/(A+B)`. Proof: put `δ=E(ρ)`. Then both intervals `[(1−δ)/A,(1+δ)/A]` and `[(1−δ)/B,(1+δ)/B]` must share `ρ`. Assuming `A>=B`, overlap requires `(1−δ)/B <= (1+δ)/A`, equivalent to `δ >= (A−B)/(A+B)`. At `ρ*`, residuals are `+(A−B)/(A+B)` and `−(A−B)/(A+B)`, attaining the bound. The `B>A` case is symmetric. No assumptions about H or collision rates are used.

The archived BASS owner normalizes number inventories with its **binary64** `math.fsum` baryon-weighted denominator and computes each isotope scale by binary64 division. We compute that exact source behavior and only then convert individual binary64 scale values into exact `Fraction`. REI saved JSON decimal literals are read as `Decimal` and exact `Fraction`. This is represented-data arithmetic; it is not uncertain physical input calibration. The seven fixed REDSHIFT rows yield `δ* = 0.0049430259146521619, ..., 0.0051858663146863389`, i.e. unavoidable max-relative **0.4943026%–0.5185866%** for the named H1 and He4 inventories. T>0 versus T_B=0 is a separate exact incompatibility; it is *not* added as a finite relative-error percentage with zero denominator.

A rank/observable projection may still be algebraically defined: source-specific equality of **electron observable** does not imply the two preserved state spaces use equal isotope inventories, nor does it supply `K,H,ρ, full J_y` or any causal CMB response. Adjusting one scalar `ρ` cannot fix unequal isotope ratios.

## 4. Positive source-only exact closure with explicit invariant totals

For REI 17-state `y` and the seven Puchwein-model photo events only, let proper-time rates be `Γ_H`, `Γ_I`, `Γ_II` (s⁻¹), common to H1/D/T, He3/He4 singly/second ionization as declared in PR262. Define aggregate charge populations per Href

`h+=y_H1+ + y_D+`, `p=y_He3+ + y_He4+`, `d=y_He3++ + y_He4++`, `t=y_T+`.

Let frozen isotope-total *ports* be `N_H=N_H1+N_D`, `N_He=N_He3+N_He4`, `N_T=y_T0+y_T+`. Then the exact seven-event instantaneous system is

`ḣ=Γ_H (N_H−h), ṗ=Γ_I(N_He−p−d)−Γ_II p, ḋ=Γ_II p, ṫ=Γ_H(N_T−t)`.

Its fixed-total, fixed-rate Jacobian is

```
[ -Γ_H      0               0       0 ]
[   0   -(Γ_I+Γ_II)       -Γ_I      0 ]
[   0       Γ_II            0       0 ]
[   0         0             0     -Γ_H]
```

and characteristic polynomial `(λ+Γ_H)^2(λ+Γ_I)(λ+Γ_II)`. Its positive state simplex is forward invariant for nonnegative rates. This is an exact **photo-only** lumping with totals regarded as fixed state-parameters. The user-locked `NO_MORE_IVPs` is respected: no time evolution was executed. With non-autonomous rates and positive `H`, the same relation is an instantaneous x-RHS divided by H; if `ρ(x)` varies, `Z'_x=(ρ'/ρ) Z+(ρ/H) W^{-1}F_agg`, including `ρ'/ρ` exactly. In the T supplement `t_B=ρ t`, `t'_B=(ρ'/ρ)t_B+(ρ/H)Γ_H(N_T−t)`.

This closure **is not** a BASS full62/reduced30 solver equivalence. BASS `atomic_network.evaluate` uses `G0=uv*_Gphoto` from a separately prescribed external photon spectrum, recombination `Gne`, weak decay `D`, and electron feedback:

`F_B=(G0+D+n_e Gne)Y, n_e=n_b q_B^T Y`, 

`J_B=G0+D+n_e Gne+n_b (GneY)q_B^T`.

The full BASS Jacobian *formula* is source-available, but the 21-state **numerical** coefficient arrays are not present in the PR234 compact source ZIP. The REI original `model.py` also includes neutron/T beta, capture, injection, escape, nuclear/CR channels, and supplied but different UV source. Its `J_REI^full` and a common physically source-consistent trajectory are not provided here. Different hidden neutron/population configurations can have identical six charged fractions and different beta source derivatives. This shows why the additional full-source factors cannot be presumed to commute with `M`, without declaring any global no-go for other models.

## 5. Hidden Li6, T, and physical τ boundary

The BASS source assigns `Li6/H1=10⁻¹⁴>0` and Li7/H1 `5×10⁻¹⁰`. The selected REI **17 visible** state rows have Li7 ions but omit charge-resolved Li6, even though the original history reports a hidden Li6 baryon category. Without source-qualified Li6 charge-state distribution `h_i` (i=0,1,2,3), only `0 <= q_Li6^T h <= 3 N_Li6` can be asserted for `N_Li6=sum h_i`, conditional on nonnegative populations. The T complement from PR264 cannot by itself reconstruct the full21 BASS electron pool. Its source-only jet relative distortion near 10⁻¹⁶ cannot be substituted for the **0.5% inventory incompatibility** above: these are distinct quantities with distinct normalizers.

Physical τ remains `τ_x=K n_e/H` with the specified owner K and actual frame/time source; `n_e` is not the derivative of the seven frozen photo-event rate. Missing actual `nHref(x), n_b(x), H(x), K, full chemical J, source-consistent IC, directional Bianchi z(n)` prevent physical τ or CMB inference. Do not infer simulation/posterior/observable acceptance from the static proof.

## 6. Evidence, limits and next step

Source zip and five raw-file SHA fingerprints checked. 7/7 saved states produce strict positive mismatch witnesses and T-positive versus T-zero branch mismatch. Python `unittest` 32/32 PASS, independent standalone C++20 minimax comparator 7/7 PASS, Wolfram corrected exact minimax/He-closure identities `{0,0,0}`; exact rational random 200 cases and source-only rate structural tests. The first Python tamper negative test caught a code path using the filename as source hash key rather than its pinned source-role key; repaired without changing science input or acceptance. The first Wolfram command emitted module-variable warnings; a corrected call returned `{0,0,0}`. Saved-only figures read, no interpolation of the seven independent snapshots as a physical history.

Admitted claim: **specified REI snapshot and BASS pilot inventory cannot be mapped into the same source-identical isotope state by a single positive `ρ`**. A conditional seven-photo-event closed reduced block is derived separately. This does not establish universality, novel no-go, production solver validity, physical τ, posterior, or time-global error.

Next node: acquire a *single source-consistent physical model configuration* (explicitly either a shared initial isotope inventory or a qualified source-change contract), complete Li6 charge/T/fast reservoir ownership, bind actual `K,H,n_b,nHref` and full Jacobian, and obtain genuine different-author R6/C9. The original 33/88 (working), 28/88 (central), `F4 PARTIAL`, `L4 false`, budget holds and `NO_MORE_IVPs` are preserved.

**Literature provenance:** Puchwein et al. 2019 DOI 10.1093/mnras/stz222 (UVB table, not an isotope identity theorem); Tóth, Li, Rabitz & Tomlin 1997 DOI 10.1137/S0036139995293294 (lumping conditions); Eilertsen et al. arXiv:2606.28895 (generic/critical parameter qualification). Published results are background; the above source-locked fixture calculations are our direct derivations, not sourced claims from those papers.
