# FS2010 × original BASS193: multispecies chemical source compatibility

**Scientific scope:** source-frozen, arrival-endpoint **chemistry diagnostics** on the original PR302 first-flight history. Not actual electron-collision-time chemistry, not an FS2010 deposition measurement, not a new cosmological IVP. Date 2026-10-31.

## Source authority and results

- Original PR302 Draft HEAD `3a213db3b1fed40e0348e724579e8d73653f3634`, parent PR300 `0e9024f92682bc3b7a0080cc86855cbddca8b0d9`; read-only siblings #296/#298/#299/#301.
- Original private 75,877,059-byte PR302 master `REI_F4_FS2010_FULL193_THRESHOLD_20261031_FULL.zip` SHA256 `603b7eaacec1e8f0e3afe17c5c37ea9c4aee23890e969b1f121bf2b6f4f77192` (not redistributed).
- Original nested PR300 source ZIP SHA256 `7efbf46e67faf78e5ebaac6e5a3676c2bc633d63e87e5c5b5c5c8f2ebd28b2b0`. Original BASS193 193-state H/He and 192 arrival source data are matched by **both saved redshift endpoints**, maximum absolute discrepancy 3.56e-15. Sample endpoints are not every instantaneous collision.
- New physical artifact `results/BASS193_FS2010_SPECIES_COMPAT_192.csv`: 192 rows, original source energy with frozen primary electron conditional energy + native H/He fractions at saved endpoints and electron-pool consistency formulas.

## Mathematical condition and source-specific findings

FS2010 (Furlanetto & Stoever 2010, MNRAS **404**, 1869, DOI `10.1111/j.1365-2966.2010.16401.x`) tabulates electron redistribution in an H/He target under *one* ionized fraction: `x_HII = x_HeII = x_i`, `x_HeIII = 0`. Its table's `x_i` support is [1e-4, 0.999], and electron input `E_e` is tabulated from 10 to 9937.21 eV. The sub-10.2-eV energy terminal convention remains separate.

Let `y_He=nHe4/nHref` from the original BASS state, `xH=x_HII`, `x2=x_HeII`, and `x3=x_HeIII`. Then the actual *H+He* electron number per reference H nucleus and a forced one-xi projection are

    q_e,orig = xH + y_He (x2+2*x3),
    q_e,FS(x_i=xH) = (1+y_He)*xH,
    delta q_e = y_He(x2 + 2*x3 - xH).

This is an **electron-count identity**, not a proof of cascade equivalence: a small `delta q_e` can mask large differences in `n_HI`, `n_HeI`, `n_HeII`, `n_HeIII` and hence ionization/excitation branching. The real source transition collision rates depend on each species separately. For example, `n_HeI/nHe = 1 - x2 - x3` is not generally `1-xH`.

Weight each arrival endpoint by its saved original first-flight electron kinetic energy `E_j` (conditional source, not true observed amount): `⟨X⟩_E = sum_j E_j X(z_{j+1}) / sum_j E_j`. Recalculated from the raw frozen 193-state files:

- Source total `E_primary = 6.749242464433259e-11 eV/baryon`; original sub-10.2 terminal assignment `8.581099847924098e-12`; remaining **unknown deposition partition** `5.891132479640848e-11`.
- Source-weighted saved endpoint `⟨xHII⟩_E = 0.7636333513555101`, `⟨xHeII⟩_E = 0.5977541157035376`, `⟨xHeIII⟩_E = 0.08833706160404509`.
- `⟨|xHeII-xHII|⟩_E = 0.16587923565197238`; `⟨|delta q_e|/q_e,orig⟩_E = 0.014319417828763002` (max across saved arrival endpoints 0.08112582757377493). In particular, merely matching electron pool rates cannot justify a single-xi species response.
- **94.9856746565% of the conditional first-generation kinetic energy** resides in arrival bins whose saved *endpoints* have `xHeIII>1e-3`. More conservatively, 93.3250019903% has `xHeIII>1e-3` at **both saved interval endpoints** (not a continuous-trajectory guarantee without a bound on the between-endpoint evolution).
- No positive-energy arrival interval has matching *both* saved-endpoint exact FS chemical assumptions. `0.7835755717%` of source energy arrives where saved `xHII>0.999`, outside the tabulated one-xi range. This is a model-applicability assessment, not a total deposition loss estimate.

Therefore a forced single-`x_i=x_HII` interpolation through the original FS2010 grid cannot be admitted as an *exact* source-owned BASS193 secondary electron response. It can be calculated as an explicitly off-manifold comparison proxy if clearly labeled, but is not a native replacement or physical heating source. A justified multi-ion Monte Carlo, a cross-section recalibration or bounded transfer error with the original BASS193 species is required for an authoritative channel-by-channel deposition result. No general impossibility/no-go is claimed.

## Publicly accessible alternative source, not original byte-identity

Official author `https://cosmicdawn.astro.ucla.edu/codes_and_tools.html` offers raw `elec_interp.tar` with 14 xi tables and C interpolator, but raw tar remains **NOT_ACQUIRED** (network transport blocked). Independently, a tagged source snapshot of `21cmfast/21cmFAST` at git commit `2a51aa316e216a1eb60650f9e7fbe35fe9e62040`, under `src/py21cmfast/_data/x_int_tables`, yields **14/14 Git-blobs matching their GitHub directory identities, 258 energy points/file (3,612 total); 10 to 9937.21 eV monotonic, 9 numeric columns, no negative values and maximum original `|f_ion+f_heat+f_exc-1|` ≈3.9e-5** in decimal tables. The C file credits Steven Furlanetto. This is **redistribution provenance only**, not UCLA TAR byte comparison or validation of BASS193 multi-species applicability. The first dataset line `E=10eV` is terminal, and 10.2-eV rounding near threshold can create small apparent deviations. No 3-keV Table 1 approximation has been used.

## Unchanged unresolved native physics

Langer (1991) state-resolved neutral Li `1S/3P` source composition, covariances and Ferrett (1987) `n=2+n=3` lab denominator versus isotope-complete BASS K operator have not been established. Their additional physically justified source replacement would need a valid common owner, common IC/clock and source non-double-counting. Nothing here adjusts those quantities or creates an evolved temperature, electron density or CMB observable.

## Verdict

- **New auxiliary physical data:** 192 state-crosswalk rows, 2 original-source figures, source-input checks and reproducible code/tests.
- **Canonical DAG** 28/88; **working DAG** 33/88; **F4-fast** 4/7; **canonical physical delta** 0. Retained F4 PARTIAL, L4 NOT_READY, PRODUCTION HOLD.
- R6/C9 **same-author bounded verification only**; distinct-author audit NOT_RUN; native subagent NOT_RUN. No merge/force push/parent changes.
