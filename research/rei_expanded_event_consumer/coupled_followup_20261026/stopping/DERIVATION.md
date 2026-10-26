# Conservative moving-cutoff coupling and charge-tagged BED coordinates

This followup adds a finite-volume mesh-work coupling, solves its implicit thermal-cutoff feedback, and reconciles the native hydrogen binding ledger by an explicitly tagged energy coordinate. It does not repeat CR59's already derived continuum interface law. It advances components of `CR_N4_STOPPING_KERNEL`, `HE-EXP-STOPPING`, `HE-RESERVOIR` and `HE-CLOSURE`; none of those full nodes is closed by this result. The preceding integration has 29/88 admitted canonical nodes. Parent closure still requires the actual source evolution/domain, a calibrated reduction and the selected observable's error bound.

## Reused source and exact continuum ownership

Immutable CR59 code at `cosmosapjw-quantum/bass_cr`, commit `029b2122db4f76f5a639e8ae4d58cf552e71b91d`, already contains `moving_interface`, `bath_energy_rate` and the Maxwellian EE current. Its source SHA256 is `0fae93ddfd555e1d135606eab51cfe010911c7624f661d27317024cf3f54ba86`. The preceding unit bound its warm coefficients to the actual saved T=14994.847774798709 K, ne=5.996197830412253 m^-3 with a declared Maxwell bath and prescribed Coulomb logarithm20. Those existing checks are reused, not rerun.

For an energy-number density f, current j=Af-(Df)' is positive toward larger physical kinetic E. At a moving cutoff c(t), the signed tail-to-reservoir number rate is Phi=cdot*f(c)-j(c). With closed upper boundary and I=integral_c^U j dE, the existing continuum law reads

\[
\dot N_+=-\Phi,\quad \dot U_+=-c\Phi+I,\qquad
\dot N_r=\Phi,\quad\dot U_r=c\Phi-I.
\]

Both signs of Phi are retained. Negative Phi describes backflow or reclassification into the resolved tail. The reservoir energy includes both crossing-particle energy and the SAME collision-current moment. An additional stopping-heat integral would duplicate ownership. These balances do not identify a first crossing as irreversible assimilation. They also do not prove that the reservoir has become Maxwellian.

## New finite-volume mesh-work law

Let cell counts n_i have physical kinetic representatives e_i(t), with upper relative current zero. For each edge, use the same relative current F_i=j_i-w_i*f_i; the mesh motion has already been included once. The number equation is ndot_i=F_i-F_(i+1). Define the declared discrete energy U_h=sum e_i n_i. Its exact derivative is

\[
\dot U_h=\sum_i e_i\dot n_i+\sum_i\dot e_i n_i
=-e_0\Phi+\sum_{i=1}^{m-1}(e_i-e_{i-1})F_i+\sum_i\dot e_i n_i,
\quad\Phi=-F_0.
\]

Consequently the moment compatible with cutoff energy c is

\[
I_h=(c-e_0)\Phi+\sum_{i=1}^{m-1}(e_i-e_{i-1})F_i+\sum_i\dot e_i n_i.
\]

Set reservoir_Ndot=Phi and reservoir_Udot=c*Phi-I_h. Then total number and the declared discrete energy cancel exactly. This is an identity of the chosen finite approximation, not a claim that midpoint energies equal continuum moments. It handles moving representatives and the first-cell/cutoff energy mismatch explicitly. A nonzero upper current is rejected in this scope: extension requires a named escaped-number/energy owner.

The frozen three-cell diagnostic has centres(2,4,7), counts(5,6,7), centre velocities(.1,.2,.3), edge currents(-2,3,-1,0), and c=1. It gives ndot=(-5,4,-1), Phi=2, Udot_h=14/5, I_h=24/5, reservoir_Udot=-14/5. Omitting centre motion loses19/5 units of energy rate. Omitting I_h loses24/5. These are discriminating arithmetic controls, not a physical source or evolution.

## New implicit cutoff and mesh feedback

For a separately selected caloric reservoir U_r(N_r,theta), define C=partial U_r/partial theta and h=partial U_r/partial N_r. Then

\[
C\dot\theta=(c-h)\Phi-I_h.
\]

The frozen example is a conditional pure-electron Maxwell caloric relation U_r=3 N_r theta/2. It has C=3N_r/2 and h=3theta/2. This relation is not a validated reduction of the actual injected source; ion/neutral heat capacities and spatial expansion work are outside this local component.

Take c=kappa*theta. It is insufficient to treat I_h as fixed when the same unknown theta_dot moves the mesh. On a frozen reconstruction branch let I_h=I0+L*theta_dot. Solving the coupled equations gives

\[
\boxed{[C-\kappa(c-h)f(c)+L]\dot\theta=-(c-h)j(c)-I_0.}
\]

The added L is essential. If edge velocities are w_i=s_i*theta_dot, s_0=kappa, and representative velocities are edot_i=r_i*theta_dot, the finite-volume formula supplies it constructively:

\[
I_0=-(c-e_0)j_0+\sum_{i=1}^{m-1}\Delta e_i j_i,
\quad
L=(c-e_0)\kappa f_0-\sum_{i=1}^{m-1}\Delta e_i s_i f_i+\sum_i r_i n_i.
\]

All densities, laboratory currents, cell positions and chosen traces are frozen instantaneously while solving for the velocity. If a reconstruction changes its upwind trace with the motion sign, solve on a declared branch and require sign consistency; there is no single-affine claim across a branch switch. A nonlinear velocity dependence would require the corresponding implicit equation instead of this formula.

The implementation returns the effective capacity Ceff and C/Ceff conditioning ratio. It rejects Ceff<=0 on this selected positive-capacity branch; this guard is not a universal physical impossibility theorem. It never regularizes a singular denominator or adds compensating heat. In the frozen theta1,kappa2,Nr10,f(c)1,j(c)3,I0=4 example, L=0 gives Ceff14 and theta_dot=-11/28; L=2 gives Ceff16, theta_dot=-11/32, Phi=-59/16, I_h=53/16 and reservoir_Udot=-171/16. The same caloric derivative reproduces that reservoir energy exactly.

The actual primary source is a finite atomic measure, not an evolved interface density. It supplies neither f(c) nor its derivative. An interface reconstruction, actual trajectory/domain and reduction error are therefore still missing. No cutoff evolution or deposition has been computed.

## Exact binding-coordinate reconciliation and its scope

The native BED model has Bn=13.6057 eV; the existing old chemical ledger uses Bo=13.6 eV. Define delta=Bn-Bo=.0057 eV and transform EVERY species energy by

\[
\mathcal E'_s=\mathcal E_s-\delta q_s.
\]

Here q is charge in units of the positive elementary charge. An electron's tagged coordinate is xi=E+delta, while an ion's potential energy decreases by delta per positive charge. Total energy shifts by -delta*Qnet, which is constant for charge-conserving processes. This is a charge-dependent energy-zero convention, not a shift of physical kinetic energy. The preceding statement that a common kinetic-energy zero cannot remove the binding difference remains true; the all-charge ledger transformation is the additional structure that makes the reconciliation possible.

A native BED event has incoming E and outgoing W,E-Bn-W. In tagged coordinates its two outputs are W+delta,E-Bn-W+delta, and

\[
\xi_1+\xi_2+B_o=\xi_{\rm in}.
\]

The kernel transforms by k_tag(xi,omega)=k_native(xi-delta,omega-delta), with Jacobian1. Its support is xi>=Bn+delta and delta<=omega<=(xi+delta-Bn)/2. The tagged threshold is NOT13.6 eV. Velocities, stress, stopping, Maxwell weights and physical cutoff energies always use E=xi-delta. In particular a tagged Maxwell density is proportional to sqrt(xi-delta)*exp[-(xi-delta)/theta], starting at xi=delta.

The interface transforms consistently: c_tag=c+delta, h_tag=h+delta and e_i_tag=e_i+delta. I_h, L and Ceff are unchanged. The resolved energy rate shifts by -delta*Phi, while the reservoir rate shifts by +delta*Phi. Physical reservoir energy is recovered by subtracting delta*N_r. No artificial heat reservoir is present.

This exact representation does not silently replace the old source contract, which calls its atoms physical kinetic energies. The numerical old photoelectron value E_gamma-Bo would coincide with a tagged native value only after an explicit source/ledger semantic remap. Its old photon cross-section convention also remains distinct. Such a remap would lower the saved minimum physical electron energy from .011132743029032 to .005432743029032 eV, outside the preceding implementation's .011eV lower query bound. Therefore neither old source activation nor complete physical threshold reconciliation is claimed here. The tagged API accepts only explicitly identified native BED kinetic inputs and rejects legacy or already-tagged semantics.

## Nuclear cross-feed, excitation source and remaining dependencies

The parallel nuclear lane supplies a typed DDEP tritium mean beta kinetic energy5.68keV per disintegration after parent-state matching. That moment can enter a named nonthermal birth-energy reservoir; it does not determine a spectrum or heat. Its18.564keV endpoint exceeds the prior EE/BED implementation's150eV query ceiling. The neutron continuum/bound client is a separate source and must not inherit tritium values. Nuclear mass/Q, neutrino and recoil owners remain distinct from stopping energy transfer.

Original Stone–Kim–Desclaux2002 Table1 supplies a real H1s->2p excitation dataset, but its printed gap10.204eV differs from the database summary's10.1988eV and WU's finite-native10.20435eV. The source correction is retained separately. We have not combined the table with an unmatched gap, used its >3keV asymptotic fit near threshold, or created an excitation provider in this batch.

## Symmetry, invariants, observables and loop position

The all-charge energy shift is a representation gauge with a charge-conservation invariant. Moving the cutoff is a representation choice only when both number and energy transfers are retained; it is not a symmetry of an unvalidated thermal closure. Exact discrete number/energy cancellation, the caloric Schur identity and the native paired ledger are invariants. Physical observables remain kinetic spectra, residence/assimilation, secondary yields, bath temperature and deposition; none follows from conservation alone.

| Stage | New result and whole-DAG position |
|---|---|
| R1 | Reused29/88 integration and pinned unchanged HE/CR heads; selected stopping descendant |
| R2 | Reused CR59 interface and prior coefficient/BED admission; checked original excitation provenance |
| R3 | Fixed local frame, physical/tagged meanings, closed upper boundary and conditional caloric branch |
| R4 | Derived exact finite-volume mesh moment and its affine velocity derivative |
| R5 | Solved cutoff Schur feedback; derived all-charge gauge and boundary covariance |
| R6 | Ten independent Wolfram residuals zero, exact rational fixtures recorded |
| R7 | Independent review identified and resolved the previously missing I_h velocity dependence |
| R8 | Froze three minimal APIs and delta-only tests; implementation delegated |
| R9 | Root controls the one bounded test attempt; no old source or suite replay |
| R10 | Component handoff preserves partial parent gates and unchanged canonical count |

The theory worker used no local scientific runtime. Prior planning is9.802204949/10CPU plus UNKNOWN overhead, not a fresh allowance. Remote symbolic checks and source inspection have no fabricated zero-cost accounting; root's separate execution admission is required for the proposed tiny test child.
