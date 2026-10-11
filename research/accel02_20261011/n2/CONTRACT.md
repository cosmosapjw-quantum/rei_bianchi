# N2 characteristic source chronology — acceptance fixed before implementation

The inspected old `paired_runtime::endpoint` transports/redeposits to energy hats,
adds the entire source at the endpoint, and absorbs the entire old+new population
for a full step. This is not the continuous source solution. The current
source-bound warm interval already uses conserved momentum nodes, but its explicit
integrator and short temperature/time domain do not admit a long cold history.

This additive component keeps each photon's spatial covector fixed. At any stage
E=q R and dOmega/dOmega0=(a_rel^3 R^3)^-1. The source in reference-volume counts is
S=epsilon_photon_log(E,z) w/R^3. HM12 emission is explicitly restricted to the
current physical band 10..50000 eV. q covers the late 50 keV boundary; nodes above
the current band carry zero source, and nodes that redshift below 10 eV are retained.
No source spectrum is inferred from R15 integrated emissivity. No repeated energy
hat reconstruction occurs, so actual stage energies determine threshold activity.

For frozen opacity k=sum_j k_j and source S over dt,
N1=exp(-k dt) N0+S dt phi1(k dt), where phi1(x)=(1-exp(-x))/x.
The residence integral is I=N0 dt phi1(x)+S dt^2 phi2(x),
phi2(x)=(x-1+exp(-x))/x^2. Absorption by species j is k_j I.
This is exact only for frozen coefficients; the long-history midpoint scheme is
second order on smooth coefficients, with physical threshold/jump events reported
separately. It is not HE E13C3's affine-path proof or a chemistry solver.

Targeted acceptance: analytic constant source+absorption at optical depths
0,1e-12,1e-5,1,100,1e6 agrees to 3e-13 relative; positivity and species allocation;
photon ledger <=1e-12 scaled; covector transport semigroup <=1e-13; threshold
activity agrees with direct characteristic energy (no N/E-only shortcut).
Whole15.9→4 frozen-bath radiation runs use the physical HM12 source with r=0,.05.
Predeclared temporal target 2e-6 and spectral/angular target 1e-3 relative for
source, radiation energy, H/He photoionization and heat; event-induced failure is
preserved and is not permission to weaken these budgets. Normalization uses the
maximum magnitude over 65 common epochs, with exact zero channels treated as
absolute zeros. Number-ledger target is1e-10. The fixed bath is diagnostic and
cannot satisfy full N2 completion: coupled xHII/xHeII/xHeIII/T/tau wholeinterval
refinement belongs to the root integration layer. N1/N2 unchanged old proofs and
RUN001/RUN002 are not rerun.

Source identity: REI base f66929c23ea3fa6e39dd4808e5b27d136c568a03;
HM12/background bytes are inherited from the pinned physical-provider package.
Metric (-,+,+,+); proper seconds, energies eV, densities cm^-3; c remains explicit.
Native FT03 receiver and old paired runtime are preserved for provenance; no old
time/temperature guards are widened. CR/RCT/HH remain OFF in this bounded test.
