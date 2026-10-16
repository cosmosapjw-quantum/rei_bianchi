# HE21: source-age aware positive H/He photon absorption, photo-only reference

**2026-10-16 KST.** This is a bounded independent Python implementation and local numerical experiment in the ChatGPT execution container. It is **not an NCP run, not native Rust, and not full Grackle Case-A chemistry**. The Desktop Commander connector returned a monthly usage blocker, so the authorized user's 64-vCPU NCP was not accessible in this run.

## Source provenance and physics

1. `BASS_HE` HE20 PR #66 commit `ccd9125e6776f3f8d3388d70c6675873464c5f30` supplied the native cold MD14 BB50K `E^2/expm1(E/k_B T)` spectral shape, original log-bin Simpson32 photon number/first energy moment and reference total emission (`3.4595570351021263e-6` photons/H) for the q=0, zbar20→19.998, 128-source-substep control. **Only this source total/spectral form** is inherited; the new model prescribes a constant normalized source distribution in `ln(a)`, rather than claiming to reproduce original MD14 time-dependent emissivity/solid-angle Jacobian.
2. `rei_bianchi` PR #152 v2 commit `bbbd18b5c16eff70bc32ba4296360dceb9060ec4` supplied the original Verner et al. 1996 Eq. (1) analytic cross section and the three H/He donor rows `(Z,N)=(1,1),(2,2),(2,1)` from `photo.dat`. The full raw donor's SHA is reported in that PR as `a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389`, **not rehashed in this run**. We preserve *distinct* cross-section support thresholds `13.60,24.59,54.42 eV` and native physical binding energies `13.598434599702,24.587389011,54.41776 eV` from `bass_cr` C19.
3. `bass_cr` PR #72 `e91ffe368c4e6db64c4b6c5962566302a33402b6` motivates a positive competing-opacity photon event map and endpoint gas coupling. The actual Grackle `igm_point_rhs` is **not** imported here; CI/RR/DR/CMB/Case-A escape are OFF. No `rei_bianchi` or `bass_cr` checkout is modified.

Metric signature `(-,+,+,+)`. The isotropic birth-angle distribution is imposed at each local normal-observer emission midpoint. Signed `q=s/H` obeys `-.5<q<1` and controls the prescribed LRS Killing-energy ratio for elapsed logarithmic expansion `dX=ln(a/a_birth)`:

`g=E/E_birth=exp(-dX)*sqrt((1-mu_birth^2)*exp(-2q*dX)+mu_birth^2*exp(4q*dX))`.

This is a controlled constant signed shear/H model, **not** the actual native AXBI `q_ref` background integration. Proper `dt=dX/H(X)` with a prescribed flat radiation/matter/Lambda Hubble background. Gas proper nH scales as `a^-3`; original cold nominal z20 `nH=0.0017575700008892194 cm^-3` is frozen at the initial scale. Helium number fraction `Y=.2454/(4*(1-.2454))`.

## Constructive equations

Known source spectrum permits splitting positive spectral support at the preimages of HI/HeI/HeII photo fit cutoffs at **every future chemical midpoint**. A positive Gauss rule with a small mass-preserving linear tilt matches each HE20 parent Simpson32 N and first energy moment; any non-positive child is rejected. No parent-only N/U is used to invent unknown source spectral information. The photon cohort carries birth time, initial direction, spectral support and emitted energy; all photons, including subthreshold photons, remain in radiation energy and redshift-work ledgers.

For a frozen end-point gas in one *photo-only* chemical midpoint, competing rates are `lambda_i=c nH alpha_i sigma_i(E)`, `alpha=(1-xHII,Y(1-xHeII-xHeIII),Y xHeII)`. Native-style exact exponential absorption from existing cohort count `N` uses `A_i=N[-expm1(-sum(lambda)dt)]lambda_i/sum(lambda)`. The gas fractions are updated with the three stoichiometric increments at a positive Picard endpoint fixed point; extra thermal energy `sum A_i(E-I_i)` is deposited to the gas. Temperature is reconstructed using `u=(3/2)(k_B T/eV)(1+Y+n_e/n_H)` and gas adiabatic work is handled by two half-steps. This is a *new conditional photo-only closure*, not an original native Grackle solver.

The following independent physical ledgers must close per initial H nucleus:

`N_birth = N_gamma,end + sum_i A_i`,  `Delta(n_e/n_H)=sum_i A_i`,

`U_birth+u_gas,initial = U_gamma,end + u_gas,end + Delta B_gas + W_gamma + W_gas`,

`B_gas=I_H xHII + Y[I_HeI(xHeII+xHeIII)+I_HeII xHeIII]`.

Wolfram independently reduced the exact stoichiometric electron and absorption-energy identities to zero (in this conversation), and the Python tests validate the discrete ledger. The photoelectric thresholds are the Verner fit support values; binding energies enter the thermal/binding split. The HE20 Born-source energy is not a complete physical stellar emitter stress tensor.

## Actual verification (local CPU, not NCP)

- Executed **10/10** focused pytest tests, including original Verner thresholds, no-photon gas work, fully ionized no-absorber limit, signed q, parent spectral moment checks, positivity, neutral/electron conservation, He I/He II distinct binding, rejection of invalid configurations, and a deliberately unsplit threshold-crossing negative control.
- Executed **27 source-age photo-only cases**, using q `-0.005,0,+0.005`, source bins per segment `4,8,16`, source/chemical time steps `4,8,16` and 3 CPU processes. Original normal-frame gas begins at `8.098143045064857 K`.
- Maximum relative photon-number defect `1.2241927776590274e-15`, maximum relative energy ledger defect `3.6079074550737803e-16`, maximum absolute electron count defect `2.964615315390051e-21`, and **zero threshold-straddling support** across the 27 threshold-split runs. These are *algebraic conservation* checks, **not** an established global truncation-error budget.
- q=0,m16,steps16: photo-only `A_HI=3.201997447152771e-06`, `A_HeI=2.5320912875012755e-07`, `A_HeII=1.4056182632971931e-14` per initial H, `Q_heat=2.0221673074953515e-05 eV/H`, final `Tgas=8.241238335323104 K`. This is under a **prescribed normalized source** and cannot be attributed to original Grackle/MD14 full EoR.
- **Corrected time-index readback, q=0,m4**: the actually archived 27-case CSV contains step counts **4→8→16**, with H I event counts `3.204608580758689e-06` → `3.2040821355557896e-06` → `3.201997446536296e-06` per H. The adjacent changes do not decrease monotonically, so no asymptotic time-convergence order or global accuracy is certified. Previous draft text mislabeled the step indices as 16→32→64 and included two values not supported by this archived 27-case dataset; that textual claim is **withdrawn** without changing the executed source, results, or acceptance tolerances. The NCP-heavy campaign remains blocked by connector quota.

## Replay

From this bundle root using Python 3.13, numpy and pytest:

```sh
python -m pytest -q tests/test_he21.py
PYTHONPATH=src python src/run_study.py
```

Inspect `results/HE21_PHOTO_ONLY_27.csv`, `results/RESULT_STATUS.json`, `results/pytest.log`, and `results/run_stdout.txt`. No timers/background worker or stale artifacts are required.

## Next scientifically necessary comparison

HE21 must feed these **birth-age-, direction-, spectrum- and fit-cut-preserving children** to the original source-pinned Rust `igm_point_rhs` (latest shared owner selected explicitly), with genuine photoevent/heat, CI/RR/DR, Compton, gas adiabatic work, emitted/escaped Case-A photon four-momentum, and consistency with `rei_bianchi` PR150's covariant q transport. Establish a matched-time q=0 / ±q energy×time×angular convergence campaign on 64-vCPU NCP before source-calibrated EoR or CMB claims. The full-photo-only surrogate implemented here does not replace that work.

Primary sources: Friedrich et al. (2012), DOI 10.1111/j.1365-2966.2012.20449.x; Verner et al. (1996), ApJ 465, 487, original table and analytical fit; Mellema et al. (2006), DOI 10.1016/j.newast.2005.09.004. Native subagent invocation: NOT_RUN (no native delegation action exposed).

## Byte/semantic reproducibility correction

CSV writer now pins `lineterminator="\n"`; GitHub plain-text storage and the packaged CSV therefore have identical content bytes (rather than comparing only numeric row semantics). The original first archive is retained as a superseded transport representation; the v2 archive is preserved, while the HE21 v3 archive supersedes it with corrected time-step readback. No physics equations, event values or acceptance tolerances were changed for the correction.
