# BASS_HE R10Q: same-origin bright nonzero witness

## Result and admission boundary

Authoring verdict: `FINITE_R_COUPLING_ESTABLISHED__QUANTITATIVE_EFFECT_OPEN`.
Evidence: direct analytic derivation plus operator/algebra CAS checks.
Independent proof review: **PENDING / NOT_PERFORMED**.
Historical R10P `SYMMETRY_ALLOWED_ONLY__MATRIX_ELEMENT_UNESTABLISHED` is preserved, not rewritten.

The theorem concerns the same R10P unboosted, clamped-nuclei, one-electron point-Coulomb Hamiltonian, nuclear charge-center origin O, molecular z axis, collision plane xz and Ly(O)=-i*hbar*(z*dx-x*dz). For kappa2>kappa1>0 and every fixed finite R>0, the overlap of the lowest sigma and the lowest |m|=1 bright pi_x state is nonzero. Positive real meridional phase fixes a negative imaginary sign. This is not a physical collision-amplitude or cross-section certificate.

## Exact overlap witness

Set z1=-kappa2*R/(kappa1+kappa2), z2=kappa1*R/(kappa1+kappa2). Introduce midpoint integration coordinate zeta=z+delta, delta=(kappa2-kappa1)*R/[2(kappa1+kappa2)]. The operator remains Ly(O)=-i*hbar*[(zeta-delta)*dx-x*dzeta]; the origin lever term is NOT discarded.

Let d_plus^2=rho^2+(zeta-R/2)^2, d_minus^2=rho^2+(zeta+R/2)^2. On zeta>0:

    V(-zeta)-V(zeta)=(kappa2-kappa1)*(1/d_plus-1/d_minus)>0.

The normalized meridional functions G,A are the exact Friedrichs ground states of their m=0 and |m|=1 sectors, respectively, not trial functions. They can be chosen strictly positive. The half-space Dirichlet spectral bottom is strictly above the full-sector ground E_m: equality at E_m<0 would provide a half-space minimizer whose zero extension is a full ground state, contradicting strict positivity and simplicity.

For w=u_m(zeta)-u_m(-zeta),

    (h_m^+ - E_m)w=[V(-zeta)-V(zeta)]u_m(-zeta)>0,
    w(zeta=0)=0.

The negative-part test and strong maximum principle give G_plus>G_minus>0 and A_plus>A_minus>0. This analytic step is not certified merely by CAS output.

With C_R=kappa1*kappa2*R/(kappa1+kappa2),

    T_R=(1/sqrt(2))*integral_{rho>0,zeta>0}
        rho^2*(G_plus*A_plus-G_minus*A_minus)
        *(d_plus^-3-d_minus^-3) d rho d zeta > 0.

The original charge-center torque identity yields

    (E_g-E_pi)*L_gb^O=i*hbar*C_R*T_R,
    L_gb^O=-i*hbar*C_R*T_R/Delta_R != 0.

Here Delta_R=E_pi-E_g>0 follows independently by applying the m=0 Rayleigh principle to the m=1 meridional ground, removing its positive centrifugal form. Coulomb torque integrals are controlled by the Hardy bound integral |g*pi|/d_A^2 <=4||grad g||_2||grad pi||_2; use the commutator as a weak/form matrix identity. The full report details boundary/domain conditions.

Dark pi_y remains reflection-forbidden. Equal charges give a reflection-even pair and zero paired overlap; excited pi states with meridional nodes are outside the proof. No small-R leading power, uniform numerical lower bound, ETF completion, author omega orientation, support choice or discrepancy repair is asserted.

## Actual checks and preserved failures

Wolfram 15.0.1: 19 atomic/operator identities zero; 10 reflection identities zero and 3 inequalities True. Formal-placeholder warnings in the first return are preserved. SymPy1.14.0/Python3.13.5: final28 identities zero, 3 inequalities True, exit0. A first global radical simplify timeout and a later unexpanded-normal-form exit1 are preserved, diagnosed and resolved without changing physical assumptions. This is not a rerun of old R10M/R10P suites. CAS does not validate the maximum-principle/domain proof or replace independent review.

## Full immutable package

This GitHub file is a publication summary, not the full package.

BASS_HE_R10Q_BRIGHT_NONZERO_WITNESS_20260930_v1.zip
Bytes: 67717
SHA256: 996f2e4bd7469a18266b2a9c5be45ee748ff8d71ded5b9fb0bd467a306cffab3
CRC PASS; 27 members, 26 manifest payloads verified.

Includes RESEARCH_REPORT_KO.md, HANDOFF_KO.md, DECISION.json, equation/convention/source ledgers, actual CAS inputs and named-output transcriptions with warnings, independent symbolic implementation, preserved failed attempts, and the original R10P ZIP unchanged. No private source PDFs, 2024 CSV data or molecular numerical solver results.

Drive object: 1TRN4eROTtYsHhmqXn7EjnuWGgSCh-BKx
Parent: 1pkohlay5eIfFJsBwPZ_yn2jIZONZjesI
Upload success ACK, metadata size67717. Provider checksum not exposed by metadata wrapper. New output raw restore NOT_RUN.

Dropbox object: id:BSpOijBcT10AAAAAADw4Uw
Path: /BASS_DERIVATION_DOSSIERS_20260912/BASS_HE_R10Q_BRIGHT_NONZERO_WITNESS_20260930_v1.zip
Upload completed, returned size67717. New output raw restore NOT_RUN; no provider hash claim.

Input R10P ZIP was actually retrieved and checked: 31880 bytes, SHA256 f4569b157a4e9faf7488c531d8099034497c6ac9d91404f9a912a1e188afa530, 21 payloads. Its CAS/scientific runs were not repeated.

## Source identity and next bounded node

Basis publication HEAD2b3331a15e442364269de3b568a2c0ff8540ad9f, treebb01c57c13dd9ebcb94cd396f21d91162ff58b51.
Scientific source HEAD1a83a67e12de1ddc2aede0ff67168f7071450ab3, tree230904af1337df1b86976c54a303d41db8ab7d96.

Next: R10R_INDEPENDENT_NONZERO_PROOF_ADMISSION. Read packaged HANDOFF_KO.md. Independently check the nodeless branch binding, half-space strict gap, reflected PDE/negative-part proof, same-origin torque and weak Coulomb domain conditions. Return confirmed, conditionally confirmed, concrete proof gap, or rejected, with reasons. Do not substitute another general search or a molecular solve. On confirmation, frame/ETF-consistent coherent dynamics remains a distinct later research scope.

No new Delta/contour, B/C, molecular overlap solve, rotation ODE/transport, interpolation, Nmax/continuum, Eq55 or production mutation. No merge/force-push.

CODE_I02_CLOSED=true
full_certificate_fail_closed=true
scientific_PROMOTE=HOLD
Eq55_next_node_authorized=false
Eq55=NOT_RUN
production_default_change=NOT_AUTHORIZED
