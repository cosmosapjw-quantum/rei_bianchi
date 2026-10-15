# REI C16.0B: native Case-A 탈출광의 양의 angular moment 전파 및 정확한 전단 응답 범위

2026-10-15 KST. 직접 local Ubuntu에서 계산·코딩·Wolfram15 검증. 원래 non-tilted LRS Bianchi-I source (MD14 BB50kK, C11 Case-A H/He, C13 actual Killing photons, C14 gamma/nu Einstein–Boltzmann, C15 self-coupled metric and C16.0A energy Q0 work) 보존. Primary shear \(\Sigma=\sqrt{\sigma_{ab}\sigma^{ab}/2}/H=\sqrt3|s|/H\), orientation \(\varepsilon_\sigma=\mathrm{sgn}(s)\) 별도. 역사적 q_ref는 source-locked signed initial-condition adapter에만 있다.

Source roots:
- <https://github.com/cosmosapjw-quantum/rei_bianchi/pull/143> parent exact commit af67c5314669492b07cb574170c09f70994974e4, native C15 time-dependent escaped eV/H and C16.0A accepted source midpoint + local Einstein b/H.
- <https://github.com/cosmosapjw-quantum/rei_bianchi/pull/144> exact qmu commit f85394d50078fc384ce6aff55e669da866dfca35. Original qmu.py SHA256 723f8ab1fd30f35deb60acb560fcae003dc912c1053e3ff19ab72b7c85d52e8e. The actual 55-line Moment / positive_three_atom definitions from the original Git blob (SHA256 of original excerpt 504ada593d3ad3c7e17bc790da9640d3cd45526d315a74160ede3b05665c2079) are reused with only the C13 Python PhotonCloud import bound to the PR143 source. Real native C13 PhotonCloud.drift independently verifies the vectorized reconstruction.
- <https://github.com/cosmosapjw-quantum/rei_bianchi/pull/145> newer positive massive canonical-Vlasov source is an independent kinetic matter lane, not silently included in Case-A radiation emissivity.

## One constructive theorem beyond the instantaneous PR144 cone

For a source-free null photon emitted at \((a_e,b_e)\) with energy \(E_e\), directional cosine \(\mu_e\), and \(d=b-b_e\), its signed direction and energy along the exact Bianchi Killing characteristic are

\[
R^2=(1-\mu_e^2)e^{2d}+\mu_e^2 e^{-4d},\quad
E=E_e(a_e/a)R,\quad
\mu=\mu_e e^{-2d}/R.
\]
Its longitudinal pressure-difference contribution per emitted positive energy is \((a_e/a)\,f(z)\), \(z=\mu_e^2\), \(A=e^{2d}>0,B=e^{-4d}>0\):
\[
f(z)=\tfrac12\left[\frac{3Bz}{\sqrt{A+(B-A)z}}-\sqrt{A+(B-A)z}\right].
\]
Its derivative is exactly
\[
f'(z)=\frac{A(A+5B)+(B-A)(A+2B)z}{4[A+(B-A)z]^{3/2}}>0
\]
for all real \(d\) and \(z\in[0,1]\). The numerator is affine in \(z\), and at the two endpoints it is \(A(A+5B)>0\) and \(2B(2A+B)>0\). Therefore the source-emitted energy \(U_e\) alone gives the **sharp** pressure-difference interval, for positive angular distributions including zero net dipole,
\[
\boxed{-\frac12 U_e\frac{a_e}{a}e^{d}
\ \le \ \mathcal P_{2,\rm esc}(a) \ \le\
U_e\frac{a_e}{a}e^{-2d}.}
\]
The two extremes are physically nonnegative even distributions: all photon energy at \(\mu_e=0\), or half at each pole \(\mu_e=\pm1\). The exact PR144 positive_three_atom function constructs these realizers. An initially isotropic positive GL64 source and an alternative PR144 three-atom zero-\(P_2\) source are also separately calculated; neither should be identified as a measured Case-A recombination spectral/angular emission law.

Given the *actual* positive C15 Case-A energy increments at the **actual C13 Strang chemistry midpoints**, the same bounds sum independently over emitted cohorts. With \(\mathcal P_2\) per physical H nucleus, convert to SI spatial pressure difference \(\Delta P=n_H(a)\mathcal P_2\, (1.602176634\times10^{-13})\,\mathrm{J\,m^{-3}}\). On the **fixed actually solved** C16 Einstein background \(H(a),b(a)\), the additional signed shear forcing obeys the linear source-response equation
\[
\delta s'+3\delta s = \frac{8\pi G}{3c^2}\frac{\Delta P_{\rm esc}}{H},
\quad
\delta s(x_e)=0,\qquad '=\partial_{\ln a}.
\]
Its Green function \(e^{-3(x-x')}>0\), so the sharp positive-pressure boundaries integrate to an attainable sharp interval of **signed** \(\delta s\) on that frozen metric. This is a rigorous angular-source theorem for the linearized/fixed background operator, not a nonlinear self-consistent new Einstein stress-energy or stellar EOS theorem.

The user-defined \(\Sigma\) norm is non-differentiable at \(s=0\). The code computes the tight fixed-H total norm interval as \(\sqrt3 \min_{\delta s\in[\delta s_-,\delta s_+]}|s+\delta s|/H\) through its max. A signed \(\sqrt3\,\delta s/H\) interval is **not called** \(\delta\Sigma\) when the interval crosses \(s=0\); the differential magnitude is set to null, and the total nonnegative \(\Sigma\) range is returned.

## Real scientific execution and exact claim ceiling

Source-locked native C15 and C16.0A were run, not fabricated. Five actual near-\(\bar z=4\) cases at 32 positive accepted source steps: initial \(\Sigma=0,\kappa_\gamma=\kappa_\nu=.2\); initial exactly/shear-free \(\Sigma=0,\kappa=0\); \(\Sigma_{\rm ref}=.0086601457867,\varepsilon_\sigma=\pm1,\kappa=.2\); and \(\Sigma_{\rm ref}=.0173196421152,\varepsilon_\sigma=+1,\kappa=.2\). Independent positive bounds in `results/CASEA_ESCAPE_SHARP_STUDY.json`. Additional 16/32/64/128-step source-age refinements. User source conventional \(a=.1999\to.2\) with the original **manufactured warm C13 gas initial condition**, not zbar20 physical primordial EoR.

At \(\Sigma_{\rm ref}=.0086601457867,\varepsilon_\sigma=+1,\kappa=.2\), n=32:
- Actual native Case-A escaped emitted energy 0.00213421635127003 eV/H, full observational-shell escape positive.
- Transverse pressure response \(\delta\Sigma_{\rm signed,min}=-5.69272838\times10^{-17}\), balanced polar response \(\delta\Sigma_{\rm signed,max}=+1.1385453477\times10^{-16}\).
- The source PR144 three-atom \(P_2=0\) and positive isotropic GL64 sources give signed responses near \(10^{-23}\) in \(\Sigma\). These near-cancelling responses are separately reported with their numerical conditioning, not used as error-denominator.
- True original PhotonCloud.drift versus independent batched Killing quadrature has max discrepancy \(2.56573\times10^{-17}\) **of the physically attainable shear-source response span**, not a misleading 0-relative error on a tiny residual.
- Gauss16 vs Gauss32 total signed shear response difference \(1.71\times10^{-49}\,s^{-1}\) (at roundoff).
- Five repeated genuine n=32 source responses: batched sky angular kernel ~1.96x original per-node C13 PhotonCloud.drift reference (measured, not full H/He solver acceleration).

**Additional independent counterexample to low-\(\ell\) closure:** Two positive zero-flux emission skys with identical initial \(U=1\), \(F_z=0\), initial \(\mathcal P_2=0\), but different fourth and higher angular multipoles, give after a *manufactured* \(d=0.2\): \(\mathcal P_{2,\rm future}=-0.18360239025615616\) vs \(-0.2781744811626673\) eV/H, difference \(-0.09457209090651114\) eV/H. This is a mathematical kinematic example, **not** the actual tiny near-z4 C16 anisotropy. It proves that even knowing the source angular quadrupole does not determine exact finite-shear later pressure without higher kinetic multipoles or a closure, explaining why the BASS hierarchy remains scientifically necessary.

Actual source photons and gas chemistry, original C16A photon/thermal/binding/emission/escape ledger are unchanged. The **remaining C16.0B physical unknowns** are stellar mass-energy EOS/source current (not a fictitious cancelling reservoir), physically emitted Case-A recombination photon spectra and angles, baryon recoil under nonzero dipole/tilt, actual Einstein Hamiltonian derivative/Raychaudhuri under these sources, and nonlinear feedback of their radiation onto future chemical rates. Massless photon *energy-integrated* redshift does not require an assumed photon energy distribution; assigning `E_QUADRATURE_EV=30` is solely an arbitrary carrier for a given positive energy moment, **never a claimed Case-A photon frequency or photon-number source**.

Source tests `test_escape_transport.py` include actual SHA preservation, original PR144 positive three-atom construction, exact native C13 Killing drift, positive instantaneous/evolved angular cone, true original source event time/energy, both shear orientations, exact zero-shear \(\Sigma\) cusp, and negative nonrealizable moments. Local Wolfram15 `verify_sharp_escape.wl`: angular derivative theorem, both real extremizers, positive linear shear Green kernel **PASS**. No physical stellar spectrum/EOS inference or full \(z=20\to4\) EoR claim. This is a scoped constructive C16.0B progress step, **SCIENTIFIC_ADMISSION_NOT_ISSUED**.

## Reproduction, safety and publication

From the research branch root:
```bash
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1
D=research/rei_c16_escape_20261015
python3 "$D/test_escape_transport.py"
python3 "$D/study_escape.py"
wolframscript -file "$D/verify_sharp_escape.wl"
```
The new source is in an isolated worktree based on PR143 exact parent af67c5314669492b07cb574170c09f70994974e4; original user live repository, old science checkpoint, C11/C13/C14/C15 historical source, and parent PR143 are not mutated. No local Codex. Native host subagents NOT_RUN. Source snapshot and exact numerical evidence recorded in SOURCE_MANIFEST.json and RESULT_STATUS.json. GitHub source branch is periodically committed; subsequent reproducible archive and two-cloud full download/source-restore evidence are separately recorded after their successful actions.
