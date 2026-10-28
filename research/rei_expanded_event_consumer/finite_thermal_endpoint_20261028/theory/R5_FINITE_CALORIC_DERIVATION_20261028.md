# R5: finite caloric endpoint, residual transport and composition

Date: 2026-10-28 KST. New unit 5/20; original DAG working 33/88, central 28/88, delta 0. Evidence: DERIVED, with explicit same-context checks. Independent review, CAS evaluation and runtime verification are NOT_RUN. No novelty or full physical-state admission is asserted.

## 1. Definitions and finite balance

Use the R3 common-V0 convention. Let Na,Ta,c_v>0, A=Q+W, D=Na+deltaN>0 and E=c_v Na Ta+A>0. Here c_v has units J K^-1 per particle; for the specified monatomic bath c_v=3 k_B/2. U and A are energies per reference volume and N is particle count per reference volume. The coefficient is fixed within a transaction. Atomic binding, excitation, fast-electron energy and radiation are separate stores.

Under the ideal caloric law and the supplied integrated gas balance, the reconstructed endpoint is

T_hat = E/(c_v D).

Indeed the final energy equals the initial caloric energy plus the two already integrated gas contributions, E=c_v Na Ta+Q+W; solving E=c_v D T_hat gives the formula uniquely because c_v D>0. Subtracting Ta gives

T_hat-Ta = (Q+W-c_v Ta deltaN)/(c_v D).

Consequently the sign of the temperature change is the sign of the numerator, not of Q alone. Dividing by Ta and factoring Na gives the exact logarithmic increment

log(T_hat/Ta) = log(1+(Q+W)/(c_v Na Ta)) - log(1+deltaN/Na).

Both log arguments are strictly positive by E,D>0. The arguments are dimensionless. The algebraic map is exact conditional on its caloric law and supplied integrals; it is not an exact time integrator for unknown Q or W.

Differentiating U=c_v N T at fixed c_v yields d(log T)/dt = (dU/dt)/U - (dN/dt)/N. Thus the infinitesimal limit retains the particle-number term. It is consistent with the prior differential source's caloric structure without asserting that its distinct bath is the current recipient.

## 2. Saved endpoints and residual identity

Let Ua,Ub,Nb be independent saved quantities, with Ub,Nb>0. Define

r0 = Ua-c_v Na Ta,
r_bal = Ub-Ua-Q-W,
rN = Nb-D,
rE = r0+r_bal = Ub-E.

The first equality separates an initial caloric mismatch from a balance residual. R1's aggregate rE is unchanged. The saved temperature is T_b=Ub/(c_v Nb)=(E+rE)/(c_v(D+rN)). Direct common-denominator subtraction gives

T_b-T_hat = ((E+rE)D-E(D+rN))/(c_v D(D+rN))
           = (rE D-E rN)/(c_v D(D+rN)).

This proof needs no assumption that either residual vanishes. Using r_bal instead of rE would silently assume r0=0. Using rE+r0 would double-count the initial mismatch. The identity diagnoses a discrepancy; it does not alter any saved stock, energy or residual.

For an H-only contribution with fine changes (dg,ds,dp,dc), the existing coarse map gives dNeutral=dg+ds+dp, dIon=dc and dThermalElectron=dc. Hence

deltaN_H = dg+ds+dp+2dc = sum(deltaFine)+dc.

Only when the fine sum is exactly zero may this reduce to dc. Other bath species and their changes require their own supplied inventory. The separate fast-electron count is not added as another thermal electron.

## 3. Tangent map and normalization cancellation

For a differentiable parameter family remaining inside the positive domain, write variations as delta. Parameter variation of c_v is allowed although it is constant in time within each member transaction. The product rule gives

delta D = delta Na + delta(deltaN),
delta E = c_v Ta delta Na + c_v Na delta Ta + Na Ta delta c_v + delta Q + delta W.

Differentiate c_v D T_hat=E to obtain

delta T_hat = delta E/(c_v D) - E delta c_v/(c_v^2 D) - E delta D/(c_v D^2),
delta log T_hat = delta E/E - delta c_v/c_v - delta D/D.

An independent algebraic check within this derivation is the cross-multiplied identity

c_v D delta T_hat + D T_hat delta c_v + c_v T_hat delta D = delta E.

This is a different algebraic form, not an independent external review or an executed test. For the saved route replace E,D by Ub,Nb, retaining the variations of any residuals rather than treating them as constants without justification.

For R=Vb/V0>0, physical densities are u=E/R and n=D/R. Their variations are delta u=delta E/R-E delta R/R^2 and delta n=delta D/R-D delta R/R^2. Therefore delta log u-delta log n=delta E/E-delta D/D: both explicit volume terms cancel in the temperature, but not in u or n individually.

For a supplied positive right-endpoint baryon density b, let w=E/(Rb), chi=D/(Rb). Then T_hat=w/(c_v chi), and both delta R/R and delta b/b cancel from its logarithmic tangent. This cancellation requires the same endpoint and normalization for numerator and denominator. It does not permit deleting those terms from individual native coordinates, substituting a foreign b, or claiming a physical EOS match. An integrated event receives no extra 1/H; a conversion of an instantaneous derivative to another clock is a separate operation.

## 4. Conditional error transport and interval image

Assume nonnegative supplied bounds |rE|<=eE and |rN|<=eN<D. The denominator obeys D+rN>=D-eN>0. The triangle inequality applied to section 2 gives

|T_b-T_hat| <= (eE D+E eN)/(c_v D(D-eN)).

If separate bounds e0 and e_bal are available, eE=e0+e_bal is sufficient. A sharper joint bound may be used when justified; it must not omit r0 or count it twice. The displayed bound is a sufficient enclosure, not a universal optimal error constant.

If also E-eE>0, the exact image of the full rectangular energy/count box is

[(E-eE)/(c_v(D+eN)), (E+eE)/(c_v(D-eN))].

Proof: for U,N>0, partial T/partial U=1/(c_v N)>0 and partial T/partial N=-U/(c_v N^2)<0. Thus the lower and upper corners are respectively (E-eE,D+eN) and (E+eE,D-eN). For a correlated admissible subset of that box the same interval remains an enclosure, but its endpoints need not be attainable. No probabilistic independence assumption is needed for enclosure. If c_v is uncertain, its uncertainty must be supplied and included; the fixed-c_v interval must not be reused unchanged.

For the correlated affine-polytope alternative, write z=sum_i lambda_i v_i, with lambda_i>=0 and sum lambda_i=1. Affineness gives E(z)=sum lambda_i E(v_i), D(z)=sum lambda_i D(v_i). Multiplying each vertex temperature by w_i=lambda_i D(v_i)/D(z) gives E(z)/(c_v D(z)), so the temperature is a convex combination of vertex temperatures. Its extrema are attained at vertices. Physical sharpness additionally needs those vertices to be physically admissible; an outer polytope alone does not establish that.

A small arithmetic or saved conservation residual does not provide eE or eN for model, transport, rate or EOS error. Missing physical radii remain null. The amplification diverges as the positive denominator margin D-eN tends to zero; logarithmic sensitivity also becomes singular as E approaches zero. These are conditioning/domain limits, not global physical impossibility results.

## 5. Composition across reference volumes

Let the first segment use V0 and the second use its own reference V1=R01 V0. For any count increment dN12 expressed per V1, the extensive number is V1 dN12. Expressing it per V0 gives R01 dN12. The identical argument applies to energy and work. Therefore

deltaN02 = deltaN01 + R01 deltaN12,
Q02 = Q01 + R01 Q12,
W02 = W01 + R01 W12,
R02 = R01 R12.

The first endpoint, when used as the second initial state, must likewise be converted to the second reference: N1_local=N1_common/R01 and U1_local=U1_common/R01. Substitution in the two balances proves agreement with a single common-V0 balance when the interface state and residual treatment match. If saved residuals are retained, their second-segment energy/count contributions scale by R01 as well. Temperature increments are not quantities to add in place of these balances.

The derivative contains product terms, for example

delta(deltaN02)=delta(deltaN01)+delta R01 deltaN12+R01 delta(deltaN12),
delta R02=R12 delta R01+R01 delta R12.

The same product rule applies to Q and W. Associativity of repeated composition follows from multiplication of volume ratios and distributivity of scaled extensive increments. It does not establish closure when intermediate physical states or sources are inconsistent.

## 6. Work and zero-event limits

When deltaN=Q=W=0, T_hat=Ta. If the only change is a different representation volume and there is no assigned work, u and n both dilute by 1/R while their temperature ratio remains unchanged. This representation statement is not the physical adiabatic cooling law.

For an actual adiabatically expanding ideal monatomic parcel, N is constant, Q=0 and p=(gamma-1)U/R with gamma=5/3. The first law d(U V0)=-p dV gives dU/dR=-(gamma-1)U/R. Integration yields U_b=U_a R^(-2/3), W=U_a(R^(-2/3)-1), and the finite map gives T_b=T_a R^(-2/3). W is negative for expansion R>1. Multiplying this answer by the same factor again would double-count work. This limit assumes isotropic ideal-gas pressure and no other work/heat ports; a general Bianchi matter model requires its actual work source.

Every term in E,rE,r0,r_bal has energy-per-reference-volume units; D,rN have count-per-reference-volume units. Section 2 and section 4 have temperature units. No natural-units identification or energy conversion of the already SI source is used.

## 7. General caloric EOS on one branch

Let F(T,z) denote gas energy per the chosen common volume for fixed non-temperature state z. On a positive temperature bracket [Tlo,Thi], assume F is continuous, differentiable as required, and partial_T F>=m>0. If F(Tlo,z)<=U<=F(Thi,z), continuity gives a solution and strict monotonicity makes it unique.

For two solutions in that same bracket at fixed z, the mean-value theorem gives |delta T|<=|delta U|/m. For differentiable joint variations of U,z on the same branch, implicit differentiation gives

delta T = (delta U - partial_z F dot delta z)/(partial_T F).

This is not a supplied general-EOS implementation. Molecular, relativistic, degenerate or multi-temperature matter must supply the appropriate caloric model and bracket. An ionization-energy term included in F must not also be applied as a separate energy store. EOS uncertainty requires its own bound; the inverse theorem does not manufacture one.

## 8. Disposition and next executable work

The finite identities, residual split, conditional bounds, tangent and volume composition above are directly derived. R4's dimensioned examples distinguish heat-only from count-aware updates. No BASS source values were evaluated anew. There is no new empirical speedup, convergence, physical trajectory or native25 claim.

The next verification is one fresh non-author review of the explicit assumptions and formulas, then the exact-rational implementation and targeted tests described in C1-C4 when an authorized executor and a quantified resource ceiling are available. Current same-context checking is not R6 independent completion. Physical outputs remain null and the original DAG remains unchanged.
