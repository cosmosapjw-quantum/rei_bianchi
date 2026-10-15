# R9 bounded bridge contract — frozen physical model v1

Restored from the contract author's conversation history on 2026-10-15 after the scratch executor became inaccessible. This is a semantic restoration, not a claim of byte-identical recovery. All frozen equations, inputs, model choices, units, acceptance tolerances and claim boundaries are retained. The authorized numerical refinement to photo4096 is consolidated below. Implementation: bridge_code/bridge_driver.py; original author: r9_remaining_contract.

## Scope and evidence

Four new bounded calculations support nuclear_precision, atomic_charge_cascade, bbn17 and full_transport. They do not close those complete programmes. Actual run status, hashes and results belong to ncp_results/runs/bridge_v1/BRIDGE_EXECUTION.json and the independent review. Existing R8 physics inputs are reused; no current nuclear posterior or coupled cosmological history is inferred.

## 1. Seventeen-state inventory and conditional ionic map

Input: recovered R8 local_codex/vendor_r6/evidence/nuclear/inputs/R5_DONOR_BBN.json, result.Y_final, number abundances per donor baryon. Do not combine its summary Li7/H with Y_final: the explicit endpoint retains Be7 and the summary uses a distinct late-time convention.

Ordering: n,H1_0,H1_1,D_0,D_1,T_0,T_1,He3_0,He3_1,He3_2,He4_0,He4_1,He4_2,Li7_0,Li7_1,Li7_2,Li7_3. The first13 match PR150; the last4 are this adapter's Li7 extension, not a native Rust implementation.
A=(1,1,1,2,2,3,3,3,3,3,4,4,4,7,7,7,7). Nuclear Z is0 for n,1 for H/D/T,2 for He,3 for Li. Ionic q is distinct.
Y_aq=Y_a f_aq; sum_q f_aq=1. B17=sum AY; Z17=sum ZY; e_free=sum qY; e_bound=sum(Z-q)Y; N_heavy=sum Y. Thus e_free+e_bound=Z17.
For proper nb in m^-3, n_aq=nbY_aq and n_thermal=nb(N_heavy+e_free), assuming a common ideal-gas temperature, no positrons and all free electrons thermal.

Selected conditional fractions: x_HII=0.000210349192936 from PR150 REC donor; x_DII=x_TII=x_HII by explicit H-equality assignment; He3/He4 neutral; Li7 singly ionized; neutron unchanged. This is an input sensitivity, not an evolved recombination result. Preserve the donor endpoint z≈4.26e6. A conditional z20 density may use the donor nb0*21^3, with cm^-3→m^-3 factor1e6; this does not evolve decays or ionic populations.

Retain every donor nuclide outside n,p,H2,H3,He3,He4,Li7 in an excluded-nuclide reservoir. Record Y,AY,ZY separately, especially Be7. No Be7→Li, T→He3, neutron decay, ionic assignment to the reservoir or normalization repair is implicit. The map identities are B_full=B17+B_excluded and Z_full=Z17+Z_excluded; report full sum AY minus1 separately. Free+bound electron closure is only for tracked species.
Report donor He4/p and He3/p independently of PR150 REC fHe_source=0.08188416223421702 and REI fHe=0.08130135170951498. Do not rescale away their discrepancy.
Legacy HHe projection is outside this map's domain when D/T/He3/Li are nonzero; a policy diagnostic is not evidence of running the Rust method.

Acceptance: all populations nonnegative/finite; isotope sum relative error<=1e-12, zero inputs exact zero; A,Z and electron-identity residuals<=5e-14 absolute per donor baryon. Donor normalization defect and helium differences are reported rather than repaired.

## 2. Actual E1 line spectrum for declared bound-shell injection

Inputs: R8 hydrogenic/transitions.csv, line_yields.csv, cascade.csv. Keep their nonrelativistic Coulomb E1 graph, masses and physical energies.
For every available species and n=3,5,10,12 choose f_nl=(2l+1)/n², l=0,...,n-1. This normalized statistical shell is declared bound excitation, not an inferred Case-A recombination injection.
If y_uk is the stored expected count on edge k from initial state u, N_k=sum_l f_nl y_(nl),k. The spectrum is dN/dE=sum_k N_k delta(E-epsilon_k). Exact line rows are authoritative; any bins must conserve both N and N epsilon. No arbitrary30eV carrier becomes a physical spectrum.
The independent downward recurrence is y_uk=sum_(u→d)b_ud[delta(k,ud)+y_dk].
Terminal states are1s and2s. P2s=sum_l f_nl P2s_nl; P1s=1-P2s. N_E1=sum_k N_k and U_E1=sum_k N_k epsilon_k.
Infer chi consistently from an existing species line. Then U_E1+(3/4)chi P2s=chi(1-1/n²).
The residual is metastable2s excitation. Its future complete2s→1s decay would have2P2s photons and(3/4)chi P2s energy in aggregate; differential spectrum and lifetime remain missing. Do not add fictitious two-photon lines to actual E1 emissions.
Export line yields, counts/energies, Lyalpha/Halpha yields and terminal probabilities. Preserve finite n, missing fine structure/continuum/recombination injection in metadata.

Acceptance: terminal probabilities in[0,1] within roundoff and sum residual<=1e-12; mixture count and energy+reservoir residual<=1e-11 relative with absolute floor1e-14 photons/eV per atom.

## 3. Nuclear sensitivity and refined quadrature

Input: unchanged R8 nuclear/np_kernel.c compiled with NP_NO_MAIN. Keep equal-mass Chen–Savage amplitude, constants, E<=1MeV, finite Maxwell window x<=80 and existing ensemble definitions.
Calibration s0=334.2mb at2200m/s and sensitivity scenarios s±=s0(1±0.01); L(s)=np_fit_L(s). The1% is chosen sensitivity, not a measured uncertainty or posterior.
T=[1e-3,1e-2,1,2.7255,6.109701377331961,100,1e4,1e6,1e7,1e8]K; evaluate all anchors with32,64,128,256 quadrature nodes.
The smooth Maxwell kernel is K(T;s)=(4/sqrt(pi)) integral_0^sqrt(80) y²exp(-y²) np_sv(kBT y²,L(s))dy, with kBT converted to MeV and output m³/s.
The adopted amplitude and L fit are affine: K(s)=K(s0)+(s-s0)dK/ds; dK/ds=[K(s+)-K(s-)]/(0.02s0). An independent slope from the L=0,1 kernels times dL/ds is useful. Report elasticity(s0/K0)dK/ds and numerical convergence separately.
Optional inverse propagation must preserve logprefactor/activation and distinguish rest-target from thermal ensembles; underflow is not exact physical zero.
No new nuclear posterior, EFT truncation band, experimental covariance or Li7 fit is claimed. BRUNE1994/MUNCH2020 tables remain possible future fit inputs.

Acceptance:64vs256 capture relative difference<=1e-10;32 diagnostic only; affine midpoint/prediction relative residual<=1e-12. Physical uncertainty remains separate from numerical convergence.

## 4. Li sub-Lyman source and conditional spectral response

Reuse PR150 BB50K shape g(E)=E²/expm1(E/(kBTstar)), E,kBT in eV, Tstar=50000K.
Iref=integral_13.6^100 g(E)dE; p(E)=g(E)/Iref. This denominator remains fixed. New source ID must distinguish the extension. Compute photon/energy moments on[5.392,13.6] and covered-total[5.392,64.39]eV. Existing source remains defined through100eV; LiI absorption above64.39 is missing.
For MD14 emissivity, use the existing source formula with selected fesc=.2:
psi(z)=.015(1+z)^2.7/[1+((1+z)/2.9)^5.6];
log10 yield=1/(.00038*.002^.227+.01858)-log10(2.55);
source births=fesc*10^(log10 yield)*psi*integral_band p dE.
Units: photons/s/cMpc³; proper photons/s/m³ multiply(1+z)^3/Mpc_m³. No year factor: yield is per Msun/year. Same sub-Lyman escape fraction is a declared extension, not fitted wavelength dependence.
Emissivity is not local incident photon flux; a transfer solution is required to relate them.

Use actual Verner photo.dat SHA256 a53e73b0af4cc6b801aef67b84bd964e3ed8c9c4992f214e4a69dc7e4443f389, row Z=3,N=3. Column order after Z,N: Eth,Emax,E0,sigma0,ya,P,yw,y0,y1.
Actual row: Eth5.392,Emax64.39,E0=3.107eV,sigma0=62.45Mb,ya15.01,P4.895,yw=y0=y1=0.
x=E/E0-y0; y=sqrt(x²+y1²);
sigma=sigma0[(x-1)²+yw²] y^(P/2-5.5)(1+sqrt(y/ya))^(-P).
1Mb=1e-22m². Zero belowEth, reject aboveEmax. Heating uses the same tabulatedEth5.392eV convention, not independently precise isotope binding.

For prescribed Fref=1 photon m^-2 s^-1 integrated over13.6–100, F_E=Fref*p(E).
Gamma=integral_band F_E sigma dE [s^-1 per LiI];
H=eV_J integral_band F_E sigma(E)(E-Eth)dE [J/s per LiI];
A=eV_J integral_band F_E sigma(E)E dE.
Identity A=Eth eV_J Gamma+H. Report sub-Lyman and covered-total results and ratios. These are normalized responses, not a cosmic ionization prediction. If actual photo bytes absent, source moments are allowed but photo-rate status is BLOCKED_INPUT.

Acceptance: adjacent quadrature relative difference<=1e-10; positivity/finite moments; absorption identity relative residual<=1e-12.
Authorized numerical repair: composite Simpson source ladder64,128,256,512,1024,2048; photo ladder additionally4096; retain16384 reference already computed. Source authoritative2048; photo authoritative4096. Preserve unsuccessful coarse comparisons. Root authorized4096 after covered photo1024vs2048 residuals6.29e-10/8.11e-10 failed. Final2048vs4096 must meet the unchanged1e-10 criterion. This is algorithm-only refinement, no altered physics or relaxed tolerance.

## Handoff and scientific ceiling

Do not modify the active PR150 pilot, duplicate the D provider, claim native17-state integration or infer full coupled transport. Four bounded calculations are computationally cheap even when executed on a64CPU host. Preserve source/input hashes, actual command/host/timing, errors and scoped checks.
The original R1–R5/R9 contract supplies definitions, sources and invariant derivations. R6 review and R7 execution have separate receipts; R8 admission and R10 packaging remain controller-owned. No new strong no-go is claimed.
