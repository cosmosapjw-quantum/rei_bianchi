# Frozen minimal normalized neutron-beta caller contract

Unit REI-COUPLED-FOLLOWUP-20261026; theory author nuclear_blocker26; 2026-10-26. Implement only in new unit implementation/. No local scientific execution/import/py_compile without root authorization. Prior beta module/tests immutable; reuse its source or import only when an authorized execution occurs. Current budget planning9.802204949/10CPU+UNKNOWN; no new allowance or IVP. Full33/reduced30 REI admission is outside this six-state component. Preserve all existing tolerances/defaults.

## Selected state and physical channels

z=(x_n,x_p,x_H0,x_e_fast,x_antinue,ell), x_i=n_i/nref, ell=ln(nref/rstar), fixed rstar>0 in inverse volume. All first five entries nonnegative; ell finite inside explicit supplied bounds. H0 denotes neutral hydrogen with one bound electron; e_fast is a separate emitted-electron pool. Antineutrino is a counted carrier for this suboperator, not assumed trapped/thermal.

Continuum branch n→p+e_fast+antinue has nu_c=(-1,+1,0,+1,+1).
Bound branch n→H0+antinue has nu_b=(-1,0,+1,0,+1).
A=(1,1,1,0,0), q=(0,1,0,-1,0), l=(0,0,1,1,-1) give exact A nu=q nu=l nu=0. Bound electron lepton number belongs to H0. No energy equation or heat source is supplied by these count channels.

Inputs: rstar; six supplied immutable scalar jets for (S,lambda_c,lambda_b,theta,alpha,chi), each containing a finite value and exactly six finite analytic state-gradient entries at the declared state. S is free-neutron injection per physical volume per proper second; lambdas inverse proper seconds; theta=dln physical volume/dtau; alpha=dlnnref/dtau; chi=dtau/deta>0. S,lambda_c,lambda_b>=0. theta,alpha can have either sign. Source may be physically zero but missing source is an error. No empirical defaults. No hidden finite differences or callback evaluation inside Jacobian. Supplied gradients are derivative claims; tests exercise nonconstant providers, but this module does not certify arbitrary provider truth.

Before evaluation require explicit domain box for all six state coordinates plus finite input jets, rstar>0, chi>0; reject state outside box before any callback. Avoid callback API in this small module: caller obtains immutable jets after its own domain check; expose domain check separately so native caller can place it before provider invocation. Reject overflow/nonfinite r=rstar*exp(ell), r<=0, and any nonfinite returned value. Do not clip.

## RHS and exact analytic Jacobian

r=rstar*exp(ell), s=S/r, d=theta+alpha, P=x_n.
For i=0..4:
g_i=delta_i0*s+nu_c[i]*lambda_c*P+nu_b[i]*lambda_b*P-d*x_i.
f_i=chi*g_i; f_5=chi*alpha.

For j=0..5 define ds_j=S_j/r-s*delta_j5, dd_j=theta_j+alpha_j.
J_ij=chi_j*g_i+chi*(delta_i0*ds_j+nu_c[i]*(P*lambda_c_j+lambda_c*delta_j0)+nu_b[i]*(P*lambda_b_j+lambda_b*delta_j0)-x_i*dd_j-d*delta_ij) for i<5, where delta_ij=0 if j=5.
J_5j=chi_j*alpha+chi*alpha_j.
Return six RHS entries and6x6Jacobian; JVP is J times a supplied six-vector. Do not equate derivative policy ProvidedOnly with an estimated numerical derivative.

## Exact physical-count oracle under explicitly restricted inputs

For finite h>=0 proper seconds, prescribe integrated expansion Theta=integral theta dtau and integrated reference growth Aref=integral alpha dtau; g=exp[-(Theta+Aref)]. Keep lambdas and lifted source shat constant. shat=V(t)*S(t)/(V0*nref0) is number per initial reference per proper second. This implies S(t)=V0*nref0*shat/V(t); it is NOT generally constant S or constant s. No source time history is inferred from a single endpoint.

Use prior exact beta transfer with P0=x_n0,s=shat,lambda=lambda_c,kappa=lambda_b,h=h. Its outputs P1,B,R are lifted parent, continuum events, bound events. Then
x_new=g*(P1,x_p0+B,x_H0_0+R,x_e_fast0+B,x_antinue0+B+R),
ell_new=ell0+Aref.

All g>0 outputs preserve nonnegativity. For the lifted state u=x_new/g, A.u=A.x0+shat*h; q.u=q.x0; l.u=l.x0. The physical-density output is nref_new*x_new. Changing nref normalization changes x and ell but not these physical densities when source and initial state are transformed consistently.

Analytic oracle Jacobian can use chain rule from previous COMPONENT_DOMAIN_DERIVATIVE.md; no new derivative code required unless root explicitly assigns it. This oracle validates only its restricted lifted-source trajectory, not a general state-dependent provider history.

## Static test design; execution remains NOT_RUN until root GO

1. Exact integer A/q/l incidence nulls; neutral-H bound electron lepton ownership included.
2. At x_n=0, positive source gives f_n=chi*S/r; other branch production zero. At every species lower face f_i>=0 for valid input jets irrespective of sign d.
3. Constant provider jets with theta+alpha=0 reproduce proper-time beta equations times chi; ell equation retained.
4. Source quotient derivative: constant physical S with ell variable gives ds/dell=-s. Wrong zero derivative is a negative control.
5. Deliberately nonconstant analytic jets: S=S0*r*(1+a*x_p), lambda_c=L0*(1+b*x_H0), lambda_b=B0, theta=theta0+c*x_n, alpha=alpha0+d0*x_e_fast, chi=chi0*(1+e*x_n), with declared nonnegative constants and domain. Supply derivatives including S_ell=S and verify direct symbolic/product-rule expected entries. Exact symbolic relationships, no finite-difference arbitrary tolerance. Tests are manufactured provider verification, not physical source calibration.
6. Count ledgers at RHS/Jacobian: A f_x=chi*(s-d A x), q f_x=-chi*d q x, l f_x=-chi*d l x and derivative identities. One null-source neutral state remains neutral.
7. Restricted lifted oracle with nonzero Theta,Aref tests zero/positive branch cases, g scaling, physical normalization change, and nonnegative outputs. Test scalars are explicitly synthetic arithmetic controls, not cosmic rates.
8. Missing jets/derivative dimension, negative S/rates, chi<=0, nref overflow/underflow, out-of-box state and pool label substitution reject. Out-of-domain input is rejected before invoking any provider in a wrapper test; accepted state/prefix not mutated by failure.

Acceptance of implementation identities: exact integer/zero cases exact; floating arithmetic residual <=128*machine_epsilon*max(1,sum absolute compared terms) for RHS/Jacobian/oracle ledger identities, with unchanged prior beta kernel5e-13 oracle tolerance where prior algorithm rounding enters. This is implementation arithmetic verification, not the original full-client physical tolerance and cannot close V6/V8 alone. Avoid new local numerical tests until root budget/action explicit. Return source and authored test inventory to independent reviewer.
