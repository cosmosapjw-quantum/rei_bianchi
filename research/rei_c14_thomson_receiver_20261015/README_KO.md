# REI C14: C13 time-dependent H/He electrons into original BASS/REI PR137 Thomson hierarchy

**Executed 2026-10-15 KST**, isolated branch from C13 HEAD
`d7d0e3ad2d6d7cccdfd70df3a0f310df93ec553d`.
**Scientific state: derived, numerical tests passed and local code verified for the exact bounded short interval.**
No original AX08 production source, running simulation, historic checkpoint or sibling repository is changed.

## 1. Actual source owners, not recreated toy inputs

* C13: real original Rust `rei_microphysics::axbi_sources::AxbiSource` source
  `MD14_Z002_FESC_BB50K_13P6_100_V1`, original C11 source-backed
  Grackle Case-A H/He atoms, BASS source-locked proper `dt` and Killing
  photon characteristics. The `a=0.1999→0.2` **prescribed** gas initial state
  at zbar≈4 has `xHII=0.4,xHeII=.5,xHeIII=.3,Tgas=12000 K` and NO claim to
  have evolved the full zbar=20 initial gas or complete source history.
  The source gas `n_e(a)` is dynamically derived from the actual photoionizing
  emissivity and rate reactions; not the unrelated static C11 receiver electron
  history used by earlier PR137.
* Original immutable `rei_bianchi` <https://github.com/cosmosapjw-quantum/rei_bianchi/pull/137>
  source commit `5d41df647c4fd624d8a1b574f67fdd0b82ff5102`,
  `research/rei_bass_hierarchy_backreaction_20261015/lrs_boltzmann.py`
  Git blob SHA1 **`e15e1875fba7fcc4a42e257e291c54d9b540a3f0`** and SHA256
  **`06ef834e4cd7adacf01f0ad6e3becc5aea9a493b5b99fd398be82610543984cc`**.
  Copied original source file has identical bytes; C14 wraps it but does not
  modify its definitions. `legendre_matrix(L,power=4/3)` and
  `thomson_coeffs(L)` are really imported and evaluated.
* `bass` source geometry and `rec_bianchi`, `bass_cr`, `WU088_HH`,
  `BASS_HE` source-qualified adapters are inherited from C12/C13 with
  their existing 16 Git-blob snapshots, guarded physics lanes and initial
  condition semantics. No external HH cross-section/rate was promoted.
  The warm BASS_HE P01 `tau` remains a separate source. The HyRec primordial
  donor remains opt-in disabled. The PR135/136 `Sigma/Pi` and
  collisionless massive-matter source remain a separate geometry supplier:
  C14 does not claim joint Einstein UV/chemistry feedback.

## 2. Applied equations and normalization repair

Signature (-,+,+,+), non-tilted comoving homogeneous LRS:
```
ds²=-c²dt²+a²e^(-2b)(dx²+dy²)+a²e^(4b)dz², s=db/dt.
x=ln a.  H(a)=da/(a dt) supplied by BASS, no accumulated time subtraction.
sigma^i_j=diag(-s,-s,2s), Sigma=sqrt(3)|s|/H.
```
Use real C13 electronic `n_e(a)=x_e(a)n_{H0}/a³` from native
MD14/BB50K photon emission and C11 H/He/Case A. One **source-matched**
PCHIP interpolation is evaluated exclusively within the donor interval.
Thomson `Gamma_T=c sigma_T n_e` [s^-1], `tau_T=int Gamma_T/H d(ln a)`.
Number and energy angular moments are normalized as in the original PR137:
```
F = sum_l (2l+1)J_l P_l(mu),    J_l=(1/2)int_-1^1 F P_l dmu.
dJ_E/dx=(s/H) A^(4) J_E - (Gamma_T/H)D J_E;
dJ_N/dx=(s/H) A^(3) J_N - (Gamma_T/H)D J_N.
```
Photon gamma uses `D_0=0,D_2=9/10,D_l>=3=1` plus the odd dipole
values from original source; massless neutrinos have **no collision**. Unpolarized
only; omitted E2 mixing and baryon recoil mean it is not full polarized Thomson
transport or a detailed CMB transfer calculation. Separate gas source already
handles its thermal and ionization ledgers.

**Material correction found and independently checked:** scalar physical
stress `Pi=P_parallel-P_perp=epsilon*J_2`, because
```
P_parallel/epsilon=<mu² W>, P_perp/epsilon=<(1-mu²)W/2>.
For positive W=1+kappa P2:
J2=kappa/5,  Pi/epsilon=kappa/5.
```
Wolfram exact integration returned `{kappa/5, 1/3+2kappa/15,
1/3-kappa/15,kappa/5,0,2kappa/15}`, explicitly ruling out the literal
`Pi=epsilon J2/3`. PR137 instead contains a *normalized Einstein RHS
intermediate*, `source=Pi/3`, multiplied by 3 times the shear
coefficient. C14 outputs **BOTH** `Pi_gamma_physical_Pa` and
`PR137_normalized_shear_source_gamma_Pa=Pi/3`, with
```
dot(s)+3 H s = [8pi G/(3c²)] (Pi_gamma_phys+Pi_nu_phys+...),
3*[8pi G/(3c²)]*PR137_source = [8pi G/(3c²)]*Pi_phys.
```
The source contribution is computed as a **read-only diagnostic**, not used
to evolve BASS/REI `s`. The physical source split
`Omega_gamma = a_rad T0^4/rho_crit, Omega_nu=Omega_r-Omega_gamma` is
separate; only gamma collides. The rounded owner Omega_r and effective
massless-nu term are not interpreted as a neutrino mass measurement.

## 3. Executed numerical results

For C13 native 8×8 source, prescribed a=.1999→.2,
128 C13 chemistry/source/expansion steps, actual Thomson integration
with `L=8`, `kappa_gamma=kappa_nu=.2` illustrative independent
positive initial quadrupole:
```
tau_C13 original trapezoid  = 8.450822111816708e-6       (q=0)
tau_BASS PR137 DOP853       = 8.450821310227940e-6
tau_independent Gauss       = 8.450821358017907e-6
relative C13 vs Gauss       = 8.919828841761002e-8.
```
In exact zero-shear q=0, `J_gamma2(t)=.04 exp(-.9 tau_T(t))`;
`J_nu2(t)=.04` independent of Thomson. The generated real C13
signed-source q=-.01,-.005,0,+.005,+.01 covers five independent
cases. Thomson gamma J2 collision-minus-free is approximately
`-3.04228e-7` at q0, while nu J2 collision-minus-free is within
binary64 roundoff. All original number monopoles and exact energy
shear identities pass separate tests.

**Measured optimizations:**
- Original positive linear LRS angular matrices for a given `L`
  cached as immutable shared NumPy arrays, verified elementwise **identical**
  to original BASS/PR137 source outputs. Seven repeated L8 **operator
  setup only** trials show an approximately 10,409× hot-cache pointer versus
  repeated polynomial quadrature build; **not a claim about solver speed**.
- Five q cases with native C13 inputs, 3 Python process workers vs serial
  whole-batch wall time 0.9581 vs 2.2566 s, **2.36×**, bitwise-identical
  scientific arrays (host and BLAS single-thread). This is not the full AX08
  runtime or whole machine resource utilization.
- Source C13 electron donor nsteps 32/64/128/256, L4/8/12/16 hierarchy and
  separate gamma/nu controls quantified in `C14_STUDY_RESULTS.json`.
  The resulting `C14_HHE_THOMSON_HISTORY.csv/png` contains a small
  **near-z4** history, not an observer zbar20→4 optical depth.

## 4. Commands, tests and limitations

Run from the C14 repo root on Python 3, NumPy/SciPy, matplotlib:
```bash
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
python3 -m unittest discover -s research/rei_c14_thomson_receiver_20261015 -p 'test_*.py' -v
python3 research/rei_c14_thomson_receiver_20261015/study_c14.py
python3 research/rei_c14_thomson_receiver_20261015/dynamic_thomson.py
```
Tests independently exercise the exact source blob, real C13 H/He electron
source/clock, FLRW exact exponential Thomson P2 limit, photon and nu number
monopoles, PR135-vs-PR137 pressure normalization, signed q and strict
neutrino collision exclusion, L hierarchy convergence, invalid data, caching.

**Accept:** derivation+implementation tested on source-locked near-z4 gas,
real owner PR137 source and positive gamma/nu split, unpolarized Thomson
only. **Do not claim:** full polarized E/B closure, photon mean-free-path
astrophysical source, self-consistent Einstein `Pi_gamma+Pi_nu+Pi_ion`
evolution, full true z20→4 ionization from primordial initial
state, AX11 spectral/multipole global error certificate, observer sky
`tau` or `GOAL_DONE`.

Next actual physics obligation is one independently matched proper
source/clock short interval with full Einstein pressure feedback
including live ionizing stress and reaction/Compton energy exchange,
and full GR/CMB angular/polarized source, then source-validated native
solver with the **actual** cold z20 gas using the original full
native `igm_rates/igm_thermal` domain rather than extrapolating C11's
10,000–24,000 K reduced table.

## 5. Backup/provenance

Original owner checkout `0fcb2ddd...` and C13/C12 parents never overwritten.
The GitHub branch/PR and independently checked ZIP (both Dropbox/Google
Drive) have an exact `BACKUP_RECEIPT.json` only **after** successful
external upload and byte-identity readback. No implicit backup claim.
