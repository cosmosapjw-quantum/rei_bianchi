# BASS_HE → REI IGM source-conditional high-z Puchwein D1 source moment bridge

## Actual physics
* Primary author source: Puchwein et al., MNRAS **485**, 47-68 (2019), DOI 10.1093/mnras/stz222, original **Table D1**, not equivalent-equilibrium D2. <https://academic.oup.com/mnras/article/485/1/47/5298898>
* Newly extracted 13 rows z5.49..10.50, six public source moments per row [Γ_HI, ℋ_HI, Γ_HeI, ℋ_HeI, Γ_HeII, ℋ_HeII]. 39 **source-conditioned model** pointwise species rows and 3 integrated responses on z=9.99→6.14, **0 new measured observations**.
* Flat matter+Λ fiducial H(z) with Puchwein H0=67.9 km/s/Mpc, Ωm=.305, ΩΛ=.695, explicitly neglect Ωr. Proper-time Jacobian dt/dz=−1/[(1+z)H(z)]. D_s =∫ Γ_s dt, Q_s=∫ ℋ_s dt, excess energy per event=Q_s/D_s. Absorbed-energy bookkeeping P_abs=I_s Γ_s+ℋ_s (do not double count binding energy).
* Independent mpmath70 and Gauss-Legendre integration support SCIPY piecewise integral; interpolation rate-linear vs log-linear **4.5–10.9%** physics-model difference dominates quadrature (<1e-14).
* Source exposures [HI,HeI,HeII]=[5.651564732153396,6.950243081345549,0.01997477771165762]. Integrated excess heat [34.225543971923,59.031737342809,0.8374521113457] eV per frozen target. NOT physical global deposited heat or evolved neutral fractions.
* **Critical caution:** During EoR, Puchwein D1 effective homogeneous neutral-weighted rates are NOT in-bubble local rates. Do not insert as physical opacity along a photon characteristic or infer a CMB τ from D_s. No new IVP, no causal RT, no full reionization history.

## Reproduction / backup
* `python source_integral_stdlib.py` is a self-contained standard-library runnable script with the 13-row public projection. Source and code are Git blob pinned against a locally run executable.
* Exact **full local source+tests+plots** ZIP from the conversation: SHA256 `cc62c1d046be912e50e712bf2ac94d46890a472896673c2407133bca9b0e3543`, 172883 bytes, 43 nested hashes+clean extracted 17 tests pass. Remote Google Drive file ID `15KgpQHYbod4gkkWJm1GbIwNTpncQJhd_` upload ACK and size readback; **whole remote ZIP SHA readback NOT_RUN**.
* GitHub contains exact tested public-source projection and standard-library implementation. The full SciPy/70dps/plots/17-test implementations are preserved in the ZIP; they are **not** silently claimed as GitHub source-file replicas.
* R1–R10 and C1–C10 each have a separate checkpoint entry committed together for recovery; no claim of independent 20 experiments or one commit per stage.

## Relevance to original REI DAG
This is a candidate RUX02 high-z **six-moment** input and RUX03 source/thermal sign aid; source-owned photon emissivity, bubble-weighting, spectral RT, chemical states/clock, and source-operator identity at the actual REI consumer are NOT admitted. RUX04/05/07/09/10 and central D0 remain HOLD; **central 28/88, HE 14/18, canonical +0**, `L4=false`, `PRODUCTION=HOLD`, `NO_MERGE=true`, `NO_FORCE_PUSH=true`, `AUTO_NEXT_NODE=false`, no new IVP. Next actionable science is the narrow actual source/consumer binding using REI owner saved states, not another optional HE-DD nuclear physics expansion.

## Blind referee
Same author checked potential source/D1-D2 swap, local-vs-neutral-weighted physical error, optical depth false claim, sign/units, interpolation vs quadrature error and double-counted ionization energy; see full ZIP `BLIND_REFEREE_KO.md`. Truly independent authors, original file byte identity and GitHub CI are **NOT_RUN/NOT_VERIFIED**.
