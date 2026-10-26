# Minimal neutron-beta caller in moving density normalization

Unit REI-COUPLED-FOLLOWUP-20261026. This is a concrete six-state physical suboperator and a constructive domain/linkage result, not the existing full33/reduced30 client. Baseline integrated count29/88 remains unchanged by this derivation. Prior beta-transfer results and original full-client gates are immutable. No local scientific execution was performed.

## 1. Exact caller definition and continuity equations

Use z=(x_n,x_p,x_H0,x_e_fast,x_antinue,ell), x_i=n_i/r, ell=ln(r/rstar), r=nref>0. H0 contains a bound electron; e_fast is distinct from a thermal electron reservoir. Proper time is tau; numerical coordinate eta has chi=dtau/deta>0. Let theta=dlnV/dtau and alpha=dlnr/dtau. A physical free-neutron injection density S has units volume^-1 time^-1. Two nonnegative declared branch rates are lambda_c and lambda_b, in inverse proper seconds.

For physical number-density vector n,

dn/dtau+theta*n=e_n*S+nu_c*lambda_c*n_n+nu_b*lambda_b*n_n,
nu_c=(-1,1,0,1,1), nu_b=(-1,0,1,0,1).

Dividing by r and differentiating its denominator gives the actual normalized caller:

g=e_n*S/r+nu_c*lambda_c*x_n+nu_b*lambda_b*x_n-(theta+alpha)*x,
f_x=dx/deta=chi*g, f_ell=dell/deta=chi*alpha.

The reference term is mandatory even if r is external; it cancels expansion only for a conserved comoving reference with alpha=-theta. A moving physical reference is therefore not an extra beta destruction channel. Source normalization is S/r, matching the existing n_i/n_ref interpretation; a source already normalized perHref must first be identified as such, not divided by r a second time. Current endpoint MODEL_CONFIG uses normal-tetrad, frozen donor H,b,nHref and illustrative photon sources; those photon amplitudes are not free-neutron S. This operator consequently requires its own explicit neutron source input; the actual zero-n/T pilot remains a supported-zero case.

The two branch columns conserve A=(1,1,1,0,0), electric charge q=(0,1,0,-1,0), and electron lepton number l=(0,0,1,1,-1). Counting the bound electron in H0 is essential. The normalized ledgers satisfy

A*f_x=chi*(S/r-d*A*x), q*f_x=-chi*d*q*x, l*f_x=-chi*d*l*x, d=theta+alpha.

Multiplication by r and inclusion of expansion recovers the physical density balances. Neutrino escape, proton/H0 interactions and electron stopping can be separate operators with their own destinations; this beta suboperator does not silently delete their number/energy.

## 2. Entire six-state analytic Jacobian and source-rate feedback

Each scalar provider S,lambda_c,lambda_b,theta,alpha,chi supplies its value and six analytic derivatives at z, immutable for this call. Define s=S/r, P=x_n and d=theta+alpha. For j=0,...,5,

s_j=S_j/r-s*delta(j,5), d_j=theta_j+alpha_j.

For i<5,

J_ij=chi_j*g_i+chi*[delta(i,0)*s_j
+nu_c[i]*(P*lambda_c_j+lambda_c*delta(j,0))
+nu_b[i]*(P*lambda_b_j+lambda_b*delta(j,0))
-x_i*d_j-d*delta(i,j)].

For the last row J_5j=chi_j*alpha+chi*alpha_j. Here delta(i,5)=0 for i<5. This is the full Jacobian of the declared six-state caller, including clock, source and rate dependence. The derivative of a finite map with rates held fixed is a different object and is not substituted for this RHS Jacobian.

Differentiating the ledger expressions above gives independent exact Jacobian tests, including the derivative of the normalization/clock factors. At fixed physical S, S_ell=0 but s_ell=-s. At fixed normalized s, physical S=r*s and S_ell=S, so s_ell=0. These are two different source conventions; the provided jets must express the chosen one.

## 3. Exact frozen-branch trajectory in the actual normalization

Define qref(tau)=V(tau)*r(tau), a(tau)=qref(tau)/qref(0), and u=a*x. Then

du/dtau=e_n*shat(tau)+nu_c*lambda_c*u_n+nu_b*lambda_b*u_n,
shat(tau)=V(tau)*S(tau)/(V0*r0).

Thus the previous exact beta transfer is the exact solution of a physical comoving-injection beta caller when shat and both lambdas are constant. This restriction specifies a complete source time law: S(tau)=V0*r0*shat/V(tau). It does not claim constant physical S or constant normalized s.

For h proper seconds, Theta=integral theta dtau and Aref=integral alpha dtau, let gref=exp[-Theta-Aref]. Use previous transfer(P0=x_n0,s=shat,lambda=lambda_c,kappa=lambda_b,h). It returns P1,B_c,B_b. The normalized state is

x(h)=gref*(P1,x_p0+B_c,x_H0_0+B_b,x_e0+B_c,x_nu0+B_c+B_b),
ell(h)=ell0+Aref.

This explicitly completes all daughter destinations. Prior competing-removal R now has the named bound-beta daughter, so no unspecified loss sink remains in this selected suboperator. Continuum and bound event counts enter the electron/atom pools once each. Existing populations undergo the same reference factor as newly produced populations. Missing that scaling for daughters is a concrete caller bug even when the parent formula is correct.

For the lifted state u=x/gref:
A*u=A*x0+shat*h, q*u=q*x0, l*u=l*x0.

For a reference change r→c*r with the same physical densities, x→x/c, ell→ell+lnc, shat→shat/c and physical S unchanged. Theta and Aref are unchanged for constant c. The formula gives x_new→x_new/c, hence r_new*x_new is invariant. Its tangent is delta x=-x*delta ln c, delta ell=delta ln c; source/provider jets must transform consistently. This is an exact normalization test, not a license to identify REC n_i/n_b and REI n_i/n_ref without their density ratio.

## 4. Constructive six-state invariant tube

The physical domain has x>=0 and finite ell. The vector field is quasipositive: on every x_i=0 lower face, loss/dilution terms vanish and remaining source/production terms are nonnegative. theta+alpha can have either sign. Positivity therefore holds for state-dependent smooth nonnegative S/lambdas and positive chi; no numerical clipping is justified.

Use the strictly positive weight vector w=(3,1,2,1,1). Both beta columns satisfy w*nu=0. Let W=w*x. Then exactly

dW/dtau=3*s-d*W.

For a chosen box assume actual provider bounds S<=Smax, chi<=Xchi, |alpha|<=Amax and d>=-Dminus, with Dminus>=0. If ell>=ellmin, r>=rmin=rstar*exp(ellmin)>0 and s<=smax=Smax/rmin. Over coordinate interval0<=eta-eta0<=Delta, proper duration is at most H=Xchi*Delta. Hence

ell0-Xchi*Amax*Delta <= ell <= ell0+Xchi*Amax*Delta,
W(tau)<=exp(Dminus*H)*(W0+3*smax*H)=Wmax,
0<=x_i<=Wmax/w_i.

The source bound can be sharpened using a phi1 integral, but the displayed expression is a valid simple finite bound including Dminus=0. No upper rate bound is needed for this population tube because branch stoichiometry cancels in W.

This supplies a finite-dimensional closure test: choose a proposed provider box with ell bounds and nonnegative species upper bounds; obtain whole-box provider bounds; choose Delta such that the displayed ell interval lies strictly inside those bounds and Wmax/w_i lies within each species bound. A first-exit argument then proves the trajectory remains in that box for the selected interval. Strict margins give an explicit tube radius for a nearby approximate trajectory if its defect/error envelope fits inside them. If any inequality fails, reduce the interval or enlarge the physically supported provider domain; do not infer a certificate from sampled points. The conditional certificate is operational once those actual box constants are supplied.

## 5. Whole-box RHS/Jacobian/curvature constants

For explicit unweighted infinity norms in these dimensionless abundance/ell coordinates, let Xi=max_i(Wmax/w_i), Pmax=Wmax/3, |d|<=Dmax, lambda_c+lambda_b<=Kmax. Let L_psi bound the l1 norm of each provider gradient across the same box. All rates are proper-time rates; chi carries the coordinate-time conversion. Then

Gmax=smax+Kmax*Pmax+Dmax*Xi,
M_f=max(Xchi*Gmax,Xchi*Amax),

L_x=L_chi*Gmax+Xchi*[L_S/rmin+smax
+Pmax*(L_lambdac+L_lambdab)+Kmax
+Xi*(L_theta+L_alpha)+Dmax],
L_ell=L_chi*Amax+Xchi*L_alpha,
L=max(L_x,L_ell).

Every row sum of the actual6x6Jacobian is bounded by L; hence the RHS is Lipschitz on the convex box. The reference logarithm has made the coordinate-derivative structure explicit, but rmin is still needed to bound the source quotient. Different physical scales use a fixed diagonal similarity/scaling transform D_out^-1 J D_state; do not compare this bound to the native33-variable WRMS norm without that fixed map and its original denominator.

If providers are autonomous functions of z, z''=Jf and ||z''||_infinity<=L*M_f. With explicit eta dependence, providers must additionally supply whole-box/time-slab partial-eta bounds. At fixed z,

partial_eta f_x=chi_eta*g+chi*[e_n*S_eta/r
+nu_c*lambda_c_eta*P+nu_b*lambda_b_eta*P
-(theta_eta+alpha_eta)*x],
partial_eta f_ell=chi_eta*alpha+chi*alpha_eta.

A bound B_eta on these expressions yields M2=B_eta+L*M_f. Thus the missing curvature object is specifically provider time-variation plus the displayed analytic chain, not a generic request for a second derivative.

For the restricted exact lifted trajectory in Section3, its analytic continuous reconstruction has zero mathematical RHS defect relative to that restricted caller. A floating representation has separate evaluation/roundoff error; zero analytic defect is not a measured zero numerical defect. No stored REC history is replaced by this exact oracle.

## 6. Canonical gate linkage and exact remaining differences

Read directly from prior intake/BLOCKER_MAP.json and current followup intake/FULL_GATE_REFERENCE: V6 requires actual full33/reduced30 RHS/Jacobian and energy/species-ledger agreement, original physical tolerance, before-callback domain refusal, immutable providers. V8 requires the selected whole-curve certificate and unchanged accepted prefix on failure. H5's original z~1100,313query history requires same-source F/G, reconstruction/retarded-state closure, fixed norm/initial error, whole-domain defect/stability/tube lower bound, endpoint/reference representation and cell curvature; current physical coverage is0/313.

This work supplies the actual full RHS/Jacobian of a named minimal beta caller, all its branch destinations, a restricted exact trajectory, and explicit six-state domain/stability/curvature bounds. The implementation contract directs domain refusal before provider callbacks and no mutation of an accepted state on rejection. Tests can validate this selected physical structure without replaying the old25tests.

Still required for canonical closure: embedding into the real33/30species/energy client and its native callback/scales; actual derivative-qualified provider functions and their whole-box constants; a selected numerical curve/defect enclosure with tube margins; the actual original REC history source/geometry/clock/retarded closure if claiming H5 coverage; energy-spectrum/stopping/recoil/neutrino owners for the corresponding energy equations. A beta-only normalization certificate is not a certificate of that original history or of a coupled Einstein/gas solve.

## 7. Cross-feed to energy/stress owner

The count source contributes continuum electron birth events at lambda_c*n_n per physical volume per proper second. Its spectral energy/momentum input must be a physical kinetic-energy law per continuum event in a declared frame; rest-mass defect stays in its own ledger. Bound beta has no free-electron source. Normal-frame volume and clock conversion are supplied by nref and chi, not by the energy spectrum. A transformed BED coordinate xi=E_native+offset must first map back to physical E_native for velocities and stopping; the offset is not a heat deposit. theory26 owns the resolved kinetic-to-thermal transfer. No nuclear Q is inserted as heat in this caller.
