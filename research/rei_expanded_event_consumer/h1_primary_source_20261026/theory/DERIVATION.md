# H1 primary-source pushforward from the admitted continuous photon history

## Result and whole-DAG position
At the actual saved z=2 GRID044 endpoint, construct the positive energy-only primary-electron measure for the single existing event H1_0 -> H1_1 + e_fast. This closes the spectral-source input subobligation of REI-H1-PRIMARY-DEGRADATION-BINDING-01 under REI-EXP-EVENT-CONSUMER. The current central DAG has 88 nodes at a5db4bac9dafadae29685bbea3cec7f43ab990b2. REI-GRID044-ENDPOINT-BINDING-01 already imported WU incidence, REC moments, CR energy ledger, HE receiver, BASS geometry and D5; those 32 Python + 9 Rust checks are reused. REI-L4 remains false; HE stopping and full coupled evolution remain open.

## Assumptions and unchanged inputs
Use the normal orthonormal tetrad, metric (-,+,+,+), proper seconds, stationary ground-state target and inherited zero recoil. Photon births are the original isotropic stellar and external_IGM continua on 5..150 eV; anisotropic redshift is retained. The energy marginal makes no new isotropic-electron angular assumption. Prescribed geometry, source shapes/normalizers, zero-opacity photon propagation, actual saved target and fixed-comoving reference are inherited. The instantaneous pairing is a counterfactual source response, not a trajectory produced by these sources.

Use the original SavedBackground loader: log H is PCHIP; b-b(0) is CubicHermiteSpline with derivative s/H. At observer eta_o=1.9459101490553132 and redshift2, r=5.151254745827818 m^-3, n_ref0=0.19078721280843758 m^-3. H1 abundance is the actual endpoint field selected by its label; no synthetic y or invented n/T.

## Forward measure, not inversion of moments
For birth eta, birth polar cosine mu in [0,1] (axisymmetric reflection), birth energy E_b, define
r_perp=exp(eta-eta_o+b_o-b), r_parallel=exp(eta-eta_o-2(b_o-b)),
g=sqrt(r_perp^2+(r_parallel^2-r_perp^2)mu^2), E_gamma=g E_b.
The source photon inventory per reference is the positive measure
dN_s=(q_s(eta)/H(eta)) d eta d mu [phi_s(E_b)/Z_s] dE_b.
The original source normalization and escape fraction are applied exactly once.

For H1, chi=13.6 eV, restrict E_gamma to [chi,150]. Define dA_s=sigma_HI(E_gamma)dN_s.
Use exactly the admitted production quadrature: birth8, angle12, energy16; donor knots and support crossings; moving angular support cuts; log birth-energy map with dE_b=E_b log(U/L)du. The new operation exposes the original integrand's positive atoms A_sj instead of discarding their energy after summation. It does not rerun the original six-channel suite or construct a spectrum from Gamma/P/K.
At each atom,
epsilon_j=E_gamma,j-chi,
w_sj=c r y_H1 alpha_s A_sj [per reference per proper second].
The energy-only source is mu_e=sum_(s,j) w_sj delta_(epsilon_j).
Physical number source measure is r mu_e [m^-3 s^-1]. A_sj has units m^2 per reference.

## Observable and ledger identities
For each source separately, M0=sum w=y alpha Gamma,
P=sum E_gamma w=y alpha P_saved,
K=sum epsilon w=y alpha K_saved,
P=chi M0+K.
Primary charge -M0 plus ion charge +M0 cancels; H1 nucleus count is unchanged. Reservoir increments are (-P,+chi M0,+K) for radiation, binding, fast-electron kinetic energy. Convert physical energy with r*1.602176634e-19. Thermal deposition is unspecified. The existing event remains the only extent owner; the HE packet is a receiver of that event.

Report atom support and positive cumulative number/energy fractions below 10.2,13.6,24.59,54.42,100 eV. These are direct finite-measure observables useful for future provider support selection. They have no new continuum-convergence certificate: inherited moment checks control only their original observables.

## Derivatives and fixed-reference meaning
Hold photon inventory, geometry, sigma and chi fixed in the local tangent. Let b_sj=c A_sj.
w_sj=r y alpha_s b_sj, hence
dw_sj=b_sj(r alpha_s dy+r y d alpha_s+y alpha_s dr).
The physical source R_sj=r w_sj has dR=r dw+w dr; at fixed y,alpha, dR/dr=2R/r. Implement y and alpha derivatives from b, not division by possibly zero y/alpha. The local source packet does not modify the 40-state collision operator, change reference, or integrate an IVP.
For a general normalized state x with physical source S and reference source Rref, F=(S-x Rref)/r and dF=(dS-Rref dx-x dRref)/r-F dr/r. Existing reference-normalization proof is reused; the atom tangent is the changed dependency.

## Independent check and discriminating controls
Wolfram checked seven exact symbolic residuals: finite moment partition, two atom directional derivatives, two physical r-derivatives, kinetic y-derivative, general quotient derivative. All are zero. Linearity extends the atom result to any finite set. This is a symbolic identity check, not a rate or stopping validation.

Numerical contract uses strict finite positivity/support and fixed meaning-based tolerances. Matching the same production moments tests extraction and normalization only. The previously computed fine/oracle comparisons and 1e-4 response criterion are reused without replay. Controls must detect omitted proper density r, using birth energy rather than redshifted observer energy, missing chi subtraction, duplicate extent owner, and improper use of an unadmitted stopping provider. Zero target and zero source amplitude must produce exactly zero atoms with finite derivative bases. No numerical heating value is emitted without qualified stopping input.

## Source intake and next real dependency
WU PR150 at87933da5654bb2e4d93f7de4341df5e0fa0f8716 supplies actual source registries, but all new rate/Q/consumer activations remain false and energy columns UNQUALIFIED. HE PR102 at ac6042a6b0610b09d0576538767ee0299389a5eb (science965da72aa7a5e885e12956fafadfb8dc2519b81f) supplies conditional finite-mass exchange/typed intake; physical_provider_admitted=false and activation=false. Its H-He thermal Q integrals do not provide electron-energy stopping. HE101 reserve0/C8 partial export remains unchanged. Therefore next input is a source-qualified electron stopping/secondary-outcome operator for this endpoint's actual species, charges, T, density and emitted epsilon support, with units/frame/reference, valid domain, energy ownership and uncertainty. Do not restart HE101 or infer heat from K. No strong no-go or novelty claim is made.

## R1-R10 chain
R1 actual next source subobligation identified; R2 exact source/endpoint/compiler results reused; R3 stationary/no-recoil and fixed-reference scope aligned; R4 choose positive forward atoms; R5 above construction and tangent derived; R6 actual Wolfram independent check; R7 bounded changed-source extraction and controls in coding unit; R8 decision conditional on that output/review; R9 frozen implementation contract; R10 source delivery plus explicit stopping input handoff. Every stage remains inside the same 88-node whole-DAG position until controller appends the scoped child.
