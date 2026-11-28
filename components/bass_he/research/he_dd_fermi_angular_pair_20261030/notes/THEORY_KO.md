# BASS_HE | measured-angle correlated deuteron response × Fermi MeV photons

2026-10-30 KST. Theory run R1–R10, physical-data-first; frozen predecessor BASS_HE PR118 HEAD `d92e94290977d4f0bb59ea16c8219d52a295bd99`. No old IVP/4501-node LP/production work. Metric signature (-,+,+,+); retain c and photon energy E_gamma measured in MeV. The local numbers here are **not measured event rates or thermal heat**.

## R1–R3. Precise sources, assumptions, new scope

* True experiment: Arends et al., Phys. Lett. B **62**, 411 (1976), IAEA EXFOR `IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871:exforall/M04/M0475.x4`, raw 3349 bytes SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`, original Git blob `c49433293921dbb012d7f1b0387745732a598efa`. Twelve *reported* DA data `[nb/sr_CM]` at lab photon 213/258/330 MeV × CM angle 46/61/73/87 deg; source `ERR-S` is pointwise statistical. Six **different** total-SIG records 201/225/253/285/320/359 MeV; **none** at 330 MeV. Source reports coincidence detection using scintillator TOF, but the original detector acceptance/event-normalization correction still lacks full independent qualification.
* Photon data: Fermi LAT Ackermann et al., ApJ 799, 86 (2015), Table 3, DOI `10.1088/0004-637X/799/1/86`. The 78-row public Git mirror `82492749123082/KM3-230213A_UHECR_TA@774174d9faaa5df40b67af5fa42b4191f09d38c6:data/fermi_igrb_1410.3696.csv`, 15975 bytes SHA256 `a78ced8234a7eb104a5f5b406a6bc609591ec2c323a26008625b239b5dccc0e5` and Git blob `794cb6fcbef243be950613475c4254d6ab3877a4`. Original CDS raw file byte not authenticated. Real Fermi energy-integrated photon bin limits `[200,282.8]`,`[282.8,400]` MeV. Three **correlated** FG models A/B/C (not independent experiments); IGRB, EGB (includes resolved sources), and `fsrc` (same underlying high-lat resolved measured values repeated across A/B/C).
* Fermi basic uncertainties include instrumental systematics and statistics; FG-model errors are separately reported. EXFOR DA ERR-S and Fermi BASIC/FG are not a joint covariance. The original Fermi table specifies bin-integrated intensity, **not point-specific photon spectral intensity at 213,258,330 MeV**.
* New goal: source-owned 12 measured DA and exact daughter pair kinematics, crossed with Fermi 3×(IGRB/EGB)×two model shapes + one shared `fsrc`×two shape assumptions, yielding 168 conditional *model-data* records and 12 source-exact measured-coordinate kinematic records. Independent physical Central/HE DAG cannot be promoted by this construction.

## R4. Counterexample and unavoidable intra-bin spectral assumption

Fix any observed energy bin B and measured integrated intensity I_B>0. Let smooth nonnegative `phi` integrate to 1 and have `phi(0)>0`. Then `I_B * phi((E-E0)/h)/h` has unchanged integral I_B over B when supported there, yet diverges at an interior chosen E0 as h→0. Hence **bin-integrated intensity alone does not bound point-specific differential source rates**. This elementary conditional counterexample is not claimed as a new strong no-go theorem. Any point-source coupling at the EXFOR DA coordinates requires a declared spectral shape or further spectral data.

Use exactly two choices: (i) flat `w_b(E)=1/ΔE_b`; (ii) Fermi *IGRB* best-fit model-dependent `g(E)=(E/100 MeV)^(-gamma_FG)*exp[-E/Ecut_FG]`, normalized within the measured bin by `w_b(E)=g(E)/∫_B g(E')dE'`, `gamma(A,B,C)=(2.32,2.28,2.26)`, `Ecut=(279,206,233) GeV`. Using IGRB spectral shape for EGB or resolved `fsrc` is **an EXTRA hypothesis**, not their measured differential spectrum. Fermi's published high-lat `fsrc` values are 4.092e−7 (200–282.8 MeV), 3.026e−7 (282.8–400 MeV) photons cm^-2 s^-1 sr_sky^-1. They are not triple-counted across FG models.

## R5. Derived two-deuteron and conditional observational response

With `M=M_alpha*c²=3727.3794118 MeV`, `m=m_d*c²=1875.61294500 MeV`, `Q=2m-M=23.84647820 MeV`, `s=M²+2MEγ`, `q*=sqrt(s/4−m²)` and `μ=cos θ_CM`, for a 4He target at rest and photon along +z:

`K_±=(M+Eγ)/2−m ± Eγ q* μ/sqrt(s)`;

`(p_±c)_z=Eγ/2 ± (M+Eγ)q*μ/sqrt(s)` and `(p_±c)_x=±q*sqrt(1−μ²)` (chosen transverse plane; azimuth rotation trivial), with both daughters on-shell. Then:

`K_++K_-=Eγ−Q`; `p_++p_-=p_γ`; and the *uniform one-of-two-daughters marginal* has mean `(Eγ−Q)/2`, variance `[(K_+−K_-)/2]^2` at a specified CM angle. The ± labels are kinematic, **not detector-arm IDs**.

Let `I_b` denote the measured Fermi energy-bin-integrated photon sky intensity. At the *measured* EXFOR `(E_j,θ_a)`, define the reported (not event-normalized) response:

`D_rep(E_j,θ_a |FG,component,model)= Ω_hyp * (1e−33 cm²/nb) * I_b * w_b(E_j) * (dσ_rep/dΩ_CM)(E_j,θ_a)`, units `s^-1 MeV^-1 sr_CM^-1 per He`.

For IGRB or EGB `Ω_hyp=4π` requires an unverified local isotropic 4He-rest photon sky. For `fsrc`, `Ω_hyp=4π(1−sin20°)` requires uniform source intensity within |b|>20° at target location and zero elsewhere. Neither is established for cosmological space-time; do not mix masked and all-sky sources as independent populations. Note the sky solid-angle `sr_sky` and CM deuteron solid-angle `sr_CM` are distinct.

Source-specific statistical DA ERR-S, Fermi BASIC and FG errors are **separately scaled**, not quadrature-combined into invented joint confidence intervals. Multiply D_rep by `(Eγ−Q)` to form a *born kinetic* response; it is not actual deposited thermal heat. Never insert a factor of 2 into an experimental DA that has unresolved event-vs-inclusive normalization; two actual daughters **per kinematically identified event** is only a pair-injection identity.

## R6–R8. Verification and scientific status

**Direct-source / established:** exact 12 measured DA values/ERR-S, exact Fermi original mirror 78 rows/6 relevant 2-bin×FG records, single resolved source data, original detector coincidence notes. **Derived:** two-body momenta, positive conditional 168-row reported-source response, spectral-shape bump counterexample. **Numerically checked:** Python 26/26 source/physics tests, compileall; high-precision 80-digit on-shell/conservation checks for all 12 measured coordinates; Wolfram independent checks at 330 MeV, 46° for `K+=(195.8904979880839) MeV`, `K-=(110.26302381191601) MeV`, IGRB A flat `D_rep=9.982330240587364e−42` and high-lat `fsrc` flat `D_rep=2.9887652843124764e−42`, consistent with independent Wolfram. Distinct-author native R6/C9 unavailable **NOT_RUN**, not replaced by same-context or CAS checks.

**Unresolved:** original Arends/other detector efficiency and exclusive counting, Fermi photon sky measured at actual He frame / epoch, photon attenuation and redshift history, fast-D redistribution/deposition, actual C_V, original Rice numeric 12 coordinates (Rice et al., PRC 61 064612, 2000), original CDS raw-byte source. No measured 330 MeV total SIG. No overclaim of a new measured 168-row experiment.

## R9–R10. Computational form and admission

Code `src/angular_injection_atlas.py` reads source bytes and fails closed on SHA-256/Git blob mismatch. It produces `results/MEASURED_ANGULAR_DPAIR_12.json` (12 actual measured coordinates with exact kinematics), `results/ANGULAR_DPAIR_FERMI_168.json` and `.csv` (168 conditional records), and exact source provenance. Reproduce using `python src/angular_injection_atlas.py --root .` then `python -m unittest discover -s tests -p 'test_*.py' -v`; no old 4501 LP/IVP replay. The genuinely new scoped auxiliary DAG is **source 1/3 → model-data 2/3**, with third source-owned physical event/transport/heat node **open**. Existing Central 28/88, HE physical 14/18, Fermi ABC 3/4 and PR118 high-lat source 2/3 do not change. `kappa=null;R_event=null;heat_rate=null;physical_activation=false;L4=false;production=HOLD`.
