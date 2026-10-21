# REI H/He/Li sandbox pilot: frozen physical and execution contract v1

Authority: root Astra theory/contract, 2026-10-22 KST. User-selected physmath-research-loop 1.0.0. This is a new scoped model and new authorized pilot, not an extension of D9's zero-new-IVP accounting. Implementation/runs belong to the lower-tier implementation agent; a fresh independent Astra review must precede scientific acceptance.

## R1–R2. Question, evidence, and exact reuse

Compute a visible, physically realizable finite parameter sweep and z=20 to 2 histories of non-tilted LRS Bianchi I with separate signed massive-matter, photon and massless-neutrino stresses, and an actually evolved primordial isotope/charge census. The scientific question is how shear and independently initialized matter/radiation quadrupoles coexist with a prescribed reionizing atomic gas and its electron-dependent photon scattering.

Reuse HE32 `CompactTransport` exactly from BASS_HE e8bb035d31f59e34734947b9082bdbd60128b799, SHA256 0fa826025836a0126fac580de98e3b45c9dcc750e1e243afe933c249ae8e4b6c, and its five immutable vendor files. Existing finite-subspace parity and two original/compact trajectories are accepted within their recorded scope; do not rerun them. The operator supports even L=2..32. Production L=16 gives 39 transport states; L=8 gives 23. This is the same exact reflection-even reduction at the chosen finite cutoff, not a new angular closure. Use L=16 for this wider initial quadrupole domain; three L=24 comparisons assess the new angular range.

PR198 and its half-contraction results, the recovered B pilot and D9, and PR199 AGE/Grackle HOLD are independent preserved lanes. No old raw trajectory is a new chemistry trajectory. No production admission is issued by this contract.

## R3. Geometry, matter and conventions

Metric (-,+,+,+), a_perp=a exp(-b), a_parallel=a exp(2b), x=ln(a/a_ref), a_ref=1/21. H=dot(a)/a, s=dot(b). In the comoving orthonormal normal frame sigma=diag(-s,-s,2s), pi_X=diag(-p_X,-p_X,2p_X).

Use SI energy density and K=8*pi*G/c^2. H^2=K*epsilon/3+Lambda*c^2/3+s^2 and dot(s)=-3*H*s+K*(p_m+p_gamma+p_nu). Preserve the pinned cosmology and canonical FV source. Massive fraction is 0.1 of Omega_m, mass/T_ref=30, radial24/angular12/Gauss3. This massive component is nonbaryonic, not a collection of H/He/Li atoms. The remaining inherited dust includes the baryon rest-mass budget exactly once.

All reported axes use full spatial Frobenius convention:

S_F=sqrt(6)*s/H; Sigma_F=abs(S_F); P_X=sqrt(6)*K*p_X/H^2;
Pi_m=abs(P_m); Pi_r=abs(P_gamma+P_nu); Pi_total=abs(P_m+P_gamma+P_nu).

Half-contraction axes equal these values/sqrt(2). Sum signed tensors before taking norms. The atomic baryons are non-tilted and isotropic, hence pi_baryon=0 in this selected fluid closure. Gamma and neutrino towers start with the same brightness quadrupole but evolve independently: Thomson scattering acts only on photons. The two species do not share a common energy vector during this pilot.

## R4. Complete selected census and explicit abundance parameters

State order: n; H1_0,H1_1; D_0,D_1; T_0,T_1; He3_0,He3_1,He3_2; He4_0,He4_1,He4_2; Li6_0,Li6_1,Li6_2,Li6_3; Li7_0,Li7_1,Li7_2,Li7_3. Total21 heavy-particle states, electrons obtained from charge neutrality. Li IV is included.

Initial nuclear number ratios relative to H1 are parameters, not a new BBN calculation or observational fit: H1=1, D=2.5e-5, T=0, He3=1e-5, He4=0.245/(4*(1-0.245)), Li6=1e-14, Li7=5e-10, n=0. Divide all nuclear numbers by their A-weighted sum to obtain Y_A=n_A/n_B and sum A*Y_A=1. Publish the actual resulting abundances. Fixed isotope numbers are preserved by the selected atomic reactions.

H1 and D start with ionized fraction2e-4; He3/He4 neutral; Li6/Li7 start entirely singly ionized; all T and neutron populations are exactly0. For numerical scale separation, evolve normalized charge fractions separately for each populated isotope and multiply by its nuclear abundance for the21-state output. Unpopulated T/n have zero state and zero source, not invented conditional fractions. Zero-abundance conditional plots must say absent. No clipping or renormalization.

The selected finite primordial census includes the stable light isotopes and n/T inventory from the supplied diagram. Unstable short-lived H/He/Li isotopes beyond this census, negative ions and molecules are outside this model. Nuclear synthesis, photodisintegration and beta-decay evolution are not implemented here. The n/T zero IC makes their omission explicit for this atomic slice; no positive n/T experiment is authorized. Keep the diagram's19-reaction target matrix as a separate unresolved obligation ledger.

## R5. Source-backed selected atomic rates

All six elemental photo channels H I, He I, He II, Li I, Li II, Li III use the exact Verner1996 table rows. sigma is in megabarns in the table, converted to cm^2 by1e-18 (or SI by1e-22). Preserve thresholds13.60,24.59,54.42,5.392,75.64,122.5eV. Use no fitted photo formula outside its published E_max.

Total radiative recombination uses the exact Verner–Ferland1996 table1 formula
alpha(T)=a/[sqrt(T/T0)*(1+sqrt(T/T0))^(1-b)*(1+sqrt(T/T1))^(1+b)] in cm^3/s.
Select the **HeI a** row explicitly (3K<T<1e6K, table-description rms2.5%); this differs from prior R9's broad-range HeI b choice and is an intentional new closure identity. All other six-channel rows are unambiguous. Labels identify the recombined product: LiI means LiII+e→LiI. Do not add ground RR to total RR. Exact source rows and provider labels belong in each case identity.

The same elemental electronic coefficient is assigned to each isotope of that element, explicitly `ElementalElectronicEquality`. This is not isotope-resolved spectroscopy. Electron-impact ionization, DR, charge exchange, molecules, negative ions, multilevel trapping and stimulated recombination are omitted process terms, not experimentally certified zeros or error bounds. In particular do not call the existing full Li CI/RR/DR bundle below its common~58022K minimum.

## R6. Prescribed UV, temperature and charge closure

Define f(z)=0.5*(1+tanh((7.5-z)/1.25)), T(z)=100+9900*f(z)K, and Gamma_HI(z)=5e-14*f(z)/s. These are declared pilot inputs, not a fitted reionization history.

The external isotropic UV photon number density per energy is n_E(E,z)=A(z)*(E/13.6eV)^(-2), with exact compact support 5<=E<=60eV. Determine A(z) by c*integral(sigma_HI*n_E dE)=Gamma_HI(z). Integrate each rate above its own threshold with Gauss–Legendre64 once per worker; compare128 once, not per RHS. Retain spectral photon and energy integrals for the energy ledger. This support lies below LiI's64.39eV inner-edge limit. LiII and LiIII photoionization are exactly0 for this specified source, while their RR channels remain implemented. Their initial higher-charge fractions are0 and remain0 in the nominal pilot; display this explicitly. The high-charge RR operator must still be checked at a frozen positive-population point without inventing a cosmological trajectory.

Let n_B=Omega_b*rho_crit_energy/(m_u*c^2*a^3), n_e=n_B*sum(q*Y_A*f_Aq). For each isotope, the nearest-neighbour charge generator has rates beta_q and r_q=n_e*alpha_(q+1→q), and df/dx=G*f/H. Its off-diagonal rates are nonnegative and column sums0. Charge neutrality determines n_e from the full census once. The normalized isotope states prevent trace Li6 from being hidden below an absolute tolerance on total density. CMB photoionization is not added; the specified UV reservoir is the sole atomic photo source.

Pass actual proper n_e in cm^-3 to CompactTransport.rhs; reuse its returned geometry and H for the chemical RHS (one massive-moment evaluation per joint RHS). Add tau'=sigma_T*c*n_e/H with unit conversion made explicit. The temperature/UV histories do not themselves provide a kinetic radiation field or a closed energy equation.

## R7. Energy, conservation and useful derived observables

The external UV, atomic thermal energy and binding energies are test-fluid contributions omitted from the inherited Einstein source. Baryon rest mass is already in inherited dust and is not added again. Record max((U_thermal+U_binding+U_UV)/epsilon_background) as an approximation diagnostic, not a bound on trajectory error. The baryon-density convention assigns nuclear mass A*m_u, neglecting nuclear mass defects; do not identify this census convention with isotope-exact rest masses.

Define epsilon_binding(q)=sum_(j<q) chi_j, with neutral ground-state reference0 and positive cumulative ionization energy. Thus U_binding=B>=0 for positive populations; it is stored ionization energy, not the negative bound-state energy sometimes called binding energy. Use the same fitted thresholds in the energy ledger and photo integrals.

For n_part=sum(heavy densities)+n_e, S_e=dot(n_e)+3H*n_e, and B=sum(n_i*epsilon_binding_i), publish
Q_thermal_required=(3/2)*kB*n_part*dot(T)+(3/2)*kB*T*S_e+3H*kB*T*n_part,
Q_binding=sum(chi_q*(R_PI,q-R_RR,q)),
Q_gas_required=Q_thermal_required+Q_binding,
P_photo=sum integral(E dR_PI), and Q_gas_required-P_photo.
The last expression is the combined bath-minus-escaped-recombination requirement, not actual recombination cooling or independently known thermostat heating. No invented3kBT/2 emitted energy per RR event.

Store separate baryon, isotope, ionic-charge/electron, photon/neutrino number, massive-number and initial-axis diagnostics. Algebraic Friedmann residual is labelled algebraic, not an independent evolution proof. An optional integrated shear-work budget reuses the established D9 identity Q=M*S_F, M=exp(3x)*H/H_i, Q'=M*(P_m+P_r), and uses saved sampled histories only.

## R8. Finite sweep and selective numerical controls

Nominal grid75 cases: Sigma_F0 in[0,0.01,0.05,0.2,0.6], A_m in[-0.8,0,1.6], A_r in[-0.8,-0.4,0,0.4,1.6]. Initial distributions W=1+A*P2 are positive on this grid; axes P_m0/P_r0 must be computed from the actual pinned source, not assumed equal to A. All initial shear orientations positive, except Sigma0=0 whose orientation is immaterial. Publish actual signed axes and norms in CSV and plots.

Add2 actual cancellation cases at Sigma_F0=0 with A_m=+1.6 and-0.8, choosing A_r so realized P_r0=-P_m0 and verifying -1<=A_r<=2. Add2 negative-shear orientation cases at Sigma_F0=0.6 (A_m,A_r)=(0,0),(1.6,-0.8) to expose signed behavior. Total79 nominal cases. No clone of old IVPs is counted here because this chemistry/electron model is new.

Production SciPy Radau, rtol2e-8, atol2e-11 for normalized states, finite max_step0.04 in x, L16, output257uniform-x samples including both endpoints. Three selected cases (isotropic zero-stress; strongest shear with A_m1.6/A_r-0.8; cancellation with A_m1.6) rerun with L24 and rtol2e-9,atol2e-12. These are finite combined sensitivity controls, not a general convergence theorem. Require max absolute changes in S_F,P_m,P_r and populated charge fractions <=2e-5 for scoped plots. If a control fails, report the concrete discrepancy before deciding a bounded repair; do not silently mask it.

Actual trajectory acceptance: solver success/exact endpoints, all finite; normalized charge minimum>=-2e-9; per-populated-isotope sum residual<=2e-9; initial-axis abs error<=2e-10; massive/photon/neutrino number relative drift<=2e-9; canonical cells nonnegative; angular brightness evaluated at257angles minimum>=-2e-8 (sampled positivity only); no silently clipped diagnostics. Check direct and independent scalar RR, spectral64/128 relative difference<=2e-8, generator conservation and high-charge RR direction. Report algebraic conservation precision separately from angular/refinement evidence.

## R9–R10. Execution, review, delivery and next question

Sandbox Python/C++ actual probes already PASS; effective8CPU/8GiB. Maximum4 independent worker processes, one BLAS thread each, reduce against observed available CPU/RAM. Every case is immutable config+source hash, atomic raw write, receipt and resumable hash check. Cap900seconds wall and2400aggregate childCPU for new production+controls; at most90newIVPattempts, stop only this task's new admissions on budget exhaustion. Other sessions are not blockers and their processes/checkouts must not be modified. No optimization timing campaign, backend rewrite or installation required.

Implement a single self-contained command that verifies vendor/data hashes, computes missing authorized cases, saves receipts, emits all figures and summaries, and can rerun offline from the delivered directory. A separate --audit-existing path must work without IVPs. Store worker CPU and real wall time as execution receipts, not speedup claims. All helpers use package-relative paths.

Figures: signed final shear over realized initial matter/radiation axes at fixed Sigma; Sigma/Pi_m/Pi_r/Pi_total histories z20→2; photon/neutrino stress comparison; both actual cancellation histories; H/D/He3/He4/Li6/Li7 charge fractions and abundances with explicit absent/zero states; energy and positivity/refinement controls. No interpolated continuous certificate, hidden clipping, extrapolated scatter map or log-of-zero repair. Use scientific plots and CSV/NPZ source data.

Independent PHYS-MATH review → actual implementation/light checks → PHYS-MATH-CODE/figure hostile review. New acceptance at most PASS_SCOPED_PRELIMINARY_ATOMIC_TEST_FLUID; full19-reaction target and native production remain NOT_ESTABLISHED/NOT_ISSUED. Publish additively on a new REI research branch from the observed PR199 metadata base, expected-head fast-forward only, draft PR. Create-only stage archive to Drive+Dropbox with actual upload ACK and full-byte GET/hash readback; later publication ACK is separate from archive packing state.

The next scientific question after a passing pilot is a source-backed harder-UV and closed thermal/radiation extension, including required LiI inner-shell/Auger and energy moments. This is a dependency, not a claim that such a model is impossible. The nuclear19-target remains an explicit separate lane.
