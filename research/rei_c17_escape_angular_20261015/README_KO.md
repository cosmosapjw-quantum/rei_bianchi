# REI C17: spectral-independent positive Case-A angular transfer and sharp Pi bounds

**Execution:** 2026-10-15 KST. **Research status:** analytic positive theorem + numerical verification + source-locked conditional short-interval C15 recombination-energy implementation. **NOT** a verified physical Case-A line/continuum photon emissivity, globally backreacting nonlinear Einstein-Boltzmann closure, original cold zbar20→4 ionization history, or observational CMB prediction. Original code/checkpoints/worktrees of rei_bianchi, BASS, BASS_HE, bass_cr, rec_bianchi and WU088_HH are not overwritten.

Parent rei_bianchi [C16 PR #144](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/144) SHA f85394d50078fc384ce6aff55e669da866dfca35 (which inherits C15 physical Einstein Sigma/Pi and C11/C13 native MD14 source chemistry). The original C11 Case-A RR/DR thermal owner exports an **escaped bolometric energy only**, not a recombination photon number, continuum spectrum or angular distribution. This study defines a photon moment propagation contract that explicitly retains these missing inputs.

## 1. New constructive physical-mathematical lemma: exact angular bounds

Comoving normal orthonormal frame, signature (-,+,+,+), LRS Bianchi I:
 ds²=-c²dt²+a²e^-2b(dx²+dy²)+a²e^4b dz²,
 s=dot b, Sigma=sqrt(3)|s|/H, orientation=sgn(s).

For a photon initially emitted at a_e, b_e with source direction mu and bolometric energy measure dU_e(mu)>=0, the exact collisionless Killing-momentum map is

 R(mu,d)=sqrt[(1-mu²)exp(2d)+mu²exp(-4d)],
 E_o/E_e=(a_e/a_o) R,
 mu_o=mu exp(-2d)/R, d=b_o-b_e.

The observer's **physical** Pi=P_parallel-P_perpendicular (not the PR137 intermediate Pi/3) for one emitting shell is
 Pi_o=(a_e/a_o) ∫ dU_e(mu) k(mu²,d),
 k(y,d)=[(A+2B)y-A]/[2 sqrt(A+(B-A)y)],
 A=exp(2d), B=exp(-4d), y=mu².

Directly differentiated, k'(y) is strictly positive on [0,1] for A,B>0: it has the sign of a positive affine function with endpoint values proportional to A(A+5B)>0 and B(2A+B)>0. Consequently, **FOR ANY POSITIVE EMISSION ANGULAR LAW of total bolometric energy U_e**, with no source spectral assumptions,

 -[U_e a_e/(2 a_o)] exp(d) <= Pi_o <=
     [U_e a_e/a_o] exp(-2d).

Both endpoints are attainable with finite, nonnegative, zero-longitudinal-flux distributions: a transverse ring mu=0 for lower, and equal +/- axial beams mu=+/-1 for upper. This is a SHARP interval under *free massless collisionless transport* on the explicitly given Bianchi geometry. The corresponding energy bounds are
 U_e (a_e/a_o) min(exp(d),exp(-2d))
 <= U_o <=
 U_e (a_e/a_o) max(exp(d),exp(-2d)).

For a sequence of nonnegative emitter time shells the source bounds add. Since the same transverse/axial extremizing ray orientations maximize/minimize for every observation time even under time-varying b(a), the integrated fixed-background, **linearized shear-source response** after solving
 d(a³ delta s)/d ln a=(8pi G/3c²) a³ Pi_rec/H
 has sharp signed lower and upper integrals over each individual positive source shell, with H>0 and a>0. This is not a rigorous bound for fully perturbed background geometry including the backreaction of radiation energy on H.

An isotropically emitting **additional physical model** means dU_e/dmu=U_e/2 at emission, giving
 U_o=(U_e a_e/a_o)∫R dmu/2,
 Pi_o=(U_e a_e/a_o)∫R P2(mu_o) dmu/2,
 cP_zo=0 exactly.
The small-d analytic angular integral gives
 Pi_o/(U_e a_e/a_o)=-8 d/5+O(d²).
The sign is opposite to the sign of the accumulated shear displacement. This is a conditional alternative law, NEVER inferred from Case-A scalar owner.

**Wolfram exact checks:** endpoint k(0)=-sqrt(A)/2, k(1)=sqrt(B); derivative positive at y=0 and y=1; isotropic response derivative at d=0 is -8/5. The theorem is a source-angle positivity/transport identity, NOT asserted as novel relative to kinetic theory or a no-go statement about physics with known atomic angular emission.

## 2. Actual original C15 H/He energy source and signed Sigma history

Original C15 EinsteinBoltzmann(PARAMS) with actual MD14/BB50K UV photon emission (13.6–100 eV), proper BASS clock, C11 original H/He case-A chemistry and PR137 gamma/nu plus PR140 massive Vlasov Pi is re-executed for a=.1999→.2. Original warm gas initial xHII=.4,xHeII=.5,xHeIII=.3,Tgas=12000K is deliberately prescribed, NOT the cold physical zbar20 source initial state. C17 reads actual increments of C11's escaped energy Uesc from every C15 step, placing an optional isotropic emission event at the actual midpoint (a,b) and transporting its **bolometric energy angular distribution** to each later original proper time using exact Killing maps. Neither a manufactured photon E nor a photon count is inserted into original RT; the source age stores only (a_e,b_e,Uesc per H) and computes energy and Pi from these sufficient moment data under the explicit opt-in collisionless/isotropic law.

The original C15 scalar energy ledger
 U_UV+U_thermal+U_bind+Uesc+W_geom-U_MD14=constant
becomes after source-local transparent transfer
 U_UV+U_thermal+U_bind+Urec+Wrec_geom+W_geom-U_MD14=constant
where Urec+Wrec_geom=Uesc exactly by event accounting. The C17 code checks the original photon/electron/nuclei and energy ledgers against the original C15 at every accepted source step. **This is a mathematically consistent energy bookkeeping substitution on fixed original Einstein geometry, not a new gravitating evolved atomic radiation field.**

For nsteps32 and Gaussian32 angles, actual C15 original source:
- Sigma_init 0 with radiation+massive Pi seed: Uesc≈.002134217081027237 eV/H, Urec≈.0021336849687204965 eV/H; Pi_rec,iso≈-5.53905e-14 eV/H; linearized |delta Sigma|≈1.48143e-27.
- Sigma_init=.002, +orientation: Urec≈.002133683535280102, Pi_rec,iso≈-9.8247984e-10 eV/H; linearized |delta Sigma|≈3.50224e-23.
- Sigma_init=.002, -orientation: Pi_rec,iso≈+9.8236960e-10 eV/H; linearized |delta Sigma|≈3.50195e-23.

The sharp positive-any-angular-emitter upper for |delta Sigma| at nsteps32 is ≈1.13855e-16 under **fixed source geometry and transparent free streaming**, compared with C16's coarser conditional envelope ≈2.31e-16. This sharp bound is actually attainable by transverse/axial symmetric positive beams in this restricted model. It is not the nonlinear, fully sourced Einstein solution nor a full global numerical error enclosure. The coupled external stellar source energy+matter four-force, gas recoil/Compton transfer, and escaped source photon spectrum/opacity remain missing and explicitly separate.

## 3. Numerical method and algorithmic efficiency

The integrator does not infer daughter spectrum from Case-A bolometric data. It uses only guaranteed radiation-energy moments for the stated angular assumption, with positive angular Gauss-Legendre rules and independent high-accuracy SciPy quadrature/actual C13 Killing packet propagation. For small |d| naive summation of R P2 subtracts O(1) positive and negative terms to produce an O(d) result, losing relative precision. The implementation uses exact cancellation-free expressions

 a=expm1(2d), b=expm1(-4d), r=a+(b-a)mu², R=sqrt(1+r),
 R-1=r/(R+1),
 R P2(mu_o)-P2(mu)
 = [((a+2b)mu²-a)-(3mu²-1)r/(R+1)]/(2R).

Since <P2>=0 for isotropic emission, integrate only this O(d) difference. This preserves the -8/5 coefficient even at |d|=1e-12, and Gaussian8/16/32/64 source-angle pressure results agree at roundoff; the original direct method showed avoidable ~1e-18 eV/H noise in this particular tiny shear regime.

Original owner C15 source b(t), Uesc(t) is held fixed; midpoint-birth vs endpoint-birth and grids nstep8/16/32/64/128 measure source-age quadrature uncertainty. Source-angle rules nmu8/16/24/32/64 and independent scalar integral verify angular response. Native source photons remain 13.6–100 eV and origin hashes unchanged. Baryon/ionizing photon positivity and original rate-domain behavior unchanged. Actual source-cohort memory representation is three 64-bit scalars per emitted age (24 bytes) versus 3×nmu positive hypothetical resolved angular packet arrays; this is a **conditional bolometric model storage advantage**, not a drop-in replacement for frequency-dependent H/He/Thomson RT.

Microkernel benchmark compares TRUE original C15 emission ages/geometry repeated only for size scaling, scalar source-born 64-angle packets vs NumPy vectorized bolometric angular sum; five warmed repeats, expected speedup is scoped to that computation, not native AX08. Three signed Sigma/orientation source cases may use multiprocessing; report actual timings and repeated identity, do not claim speedup from one noisy run.

## 4. Literature context and next genuine physics

- Pawlik & Schaye 2011, multigroup photon-conserving H/He RT, https://arxiv.org/abs/1008.1071 : our bolometric construction cannot replace frequency-dependent opacity and heating.
- Raičević et al. 2014, recombination radiation propagation vs Case A/B approximations, https://arxiv.org/abs/1311.0182 : escaped recombination radiation needs physical transport, not silently isotropic photon injection.
- Lee, Nungesser & Tod 2020, Bianchi I Einstein–Vlasov anisotropy, https://arxiv.org/abs/1911.04937 : exact collisionless shear/radiation stress identities are consistent with this restricted angular mapping.

Sibling rei_bianchi PR142 already implements an independent C13/C14 Einstein-gamma-nu stress source with prescribed warm initial H/He; C15 PR141 additionally brings real BASS PR140 positive massive Vlasov. C16 PR144 derived sharp unpropagated angular moment cone and true photo-ionization momentum recoil demands. This C17 specifically advances C16 to exact, source-age dependent **propagated angular bounds** and a separate opt-in isotropic transparent closure, without overwriting sibling PRs. The rec_bianchi HyRec z20 initial gas donor remains opt-in, BASS_HE warm source tau source-specific, bass_cr PR71 child-bin precision HOLD, WU088_HH physical HH rate OFF: no unauthorized physical source remapping.

Next: obtain state-/transition-resolved original physical atomic recombination photon emissivity and opacity (number spectrum + angular emission/escape) or fully justified isotropic transparent approximation; then implement it as actual radiation stress-energy alongside emitting stellar material, baryonic recoil, Thomson/Compton and full species total Q^a in Einstein H/shear and low-temperature native z20 H/He. This remains required before original z20→4 EoR and polarized CMB observable claims.

## 5. Reproduction and archive

C17 isolated branch root, no Codex, NumPy/SciPy/matplotlib:
  export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
  python3 -m unittest discover -s research/rei_c17_escape_angular_20261015 -p 'test_*.py' -v
  python3 research/rei_c17_escape_angular_20261015/study.py

Machine-readable scientific receipts: C17_STUDY_RESULTS.json, ESCAPING_CASEA_STRESS_HISTORY.csv, and plot ESCAPING_CASEA_STRESS_HISTORY.png; source test test_recomb_angular.py. Original C9–C16/Rust regression and two-cloud byte-verified backup receipts are added only after actual execution/readback, never merely asserted.
