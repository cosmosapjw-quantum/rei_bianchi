# Frozen scientific contract — REI-LUMINA-20261027
Version: 1.0; source accessed 2026-10-26 UTC. Requested runtime label Astra; observed runtime model label unavailable. Workflow physmath-research-loop 1.0.0. Scope: external reference adapter and moment operator; parent retains canonical DAG authority.

## Authorities and acquired evidence
Primary: Zier et al., *Introducing the Lumina project: large-volume radiation-hydrodynamic simulations of the epochs of hydrogen and helium reionization*, DOI 10.1093/mnras/stag1469, publisher page https://academic.oup.com/mnras/article/552/4/stag1469/8971942 (publisher metadata 2026-10-26); full text obtained through Exa, with https://arxiv.org/html/2605.15310v2 as independent primary access. SciSpace returned exact paper ID kt7ibga5f9bg and companions. Relevant locations: §§3.1–3.4, Table1, §4, §§8.1–8.4, data availability.
Official numeric files: https://lumina-simulation.com/data/HI_reion_lumina.txt ; https://lumina-simulation.com/data/HeIII_reion_lumina.txt ; https://lumina-simulation.com/data/sfrd_lumina.txt ; https://lumina-simulation.com/data/tau_cmb_vs_z_lumina.txt . Metadata: https://lumina-simulation.com/data-access/ .
Raw-byte identity belongs to source manifest authored by data agent. Only those four public histories are currently adopted. Bulk fields require access; paper announces general release in 2028. No full paper copy is redistributed.

## R1–R4: selected construction and types
Existing pilot physics and canonical gates remain authoritative. New adapter yields ReferenceSeries, not IncidentRadiation, not a new background solution.
ReferenceSeries requires source URL+hash, quantity, units, redshift domain, sampling, weighting, statistic, population, regime, validation flags, raw column names, and original row order.
HI and HeIII: dimensionless volume-weighted ion fractions summarized across 125 subboxes of side100cMpc; first data column after z is subbox median. Neither is the full-volume mean. HI domain ends z=4.774995, HeIII ends z=2.992408. Their unequal grids are preserved; comparison/interpolation is inside intersection only.
Quantiles describe spatial variation, not independent observational likelihood errors. HI complement to HII obeys q_p(HII)=1−q_(1−p)(HI), including reversed endpoints. HeIII raw labels violate ordering in actual rows: retain all raw bytes; flag invalid_quantile_order; use median-only plot and no uncertainty inference. Paper Fig22 plots HeI+HeII, suggesting a complement-label origin, which remains an inference.
SFRD is a source-population diagnostic with declared file units, not ionizing emissivity. Stellar age/metallicity distributions and escape-weighted photon yields are additional inputs.
Tau is cumulative observer-to-z optical depth, dimensionless, z0..49; terminal published-table value0.0543742529. Its source calculation uses mass-averaged ion fractions and belowz3 fully ionized H+He. Treat as an independently supplied reference curve, not a reconstruction from the public median histories.
No T0(z), gamma(z), Gamma(z), bin-intensity(z), or mass-weighted ion fractions appear among these four public tables.

## R5: conserved chemistry and electron projection
The user's n denotes neutron and T denotes tritium in the prior six-state beta client; temperature below is explicitly T_gas (the algebra uses T only within the thermal equation). Lowercase n_species denotes number density. HII is a charge state of an existing hydrogen nucleus. Photoionization does not create a new baryon proton through neutron beta decay. Lumina's H/He histories provide no isotope-resolved neutron/tritium nuclear source, cosmic-ray source, or inverse-beta source. The previous six-state beta source remains unchanged; its neutron/tritium and external-production dependencies remain separately open. This adapter supplies only a benchmark and an explicitly selected photon-rate interface.
Species order N=(HI,HII,HeI,HeII,HeIII,e). Define three signed reaction fluxes J=(J_H,J_HeI,J_HeII), ionization minus recombination per proper volume per proper second. With expansion theta and comoving matter flow:
D_t N + theta N = S J,
S=[[-1,0,0],[1,0,0],[0,-1,0],[0,1,-1],[0,0,1],[1,1,1]].
Left vectors l_H=(1,1,0,0,0,0), l_He=(0,0,1,1,1,0), l_Q=(0,1,0,1,2,-1) satisfy l S=0. Thus nuclei and electric charge dilute conservatively. Ionization changes electron number; electron number is not a conserved charge.
For nH>0, nHe>0 define xHII=nHII/nH and helium simplex xHeI+xHeII+xHeIII=1. Let y=nHe/nH=Yp/[4(1−Yp)] under primordial uniform composition and approximate nucleus masses mHe=4mH. Charge neutrality gives
xe=ne/nH=xHII+y(xHeII+2xHeIII).
For Yp=.24: y=3/38, fully ionized xe=22/19.
Inputs must include independent helium fractions; the guess xHeII=xHII−xHeIII already fails positivity at early published rows (xHII≈1e−6, xHeIII≈1.2667e−5). Missing HeII is a dependency, not zero.
For spatially uniform composition and volume averaging:
<x>_mass=<rho x>_V/<rho>_V=<x>_V+Cov_V(rho,x)/<rho>_V.
Actual mean ne is <nH xHII+nHe(xHeII+2xHeIII)>_V. Species-weighted variants replace rho when composition varies. Subbox medians do not supply these products or covariances. No manufactured mass-weighted electron history is returned.

## R5: seven radiation-moment rows and the executable operator
Early regime z>4.75 uses six rows. Late z<=4.75 uses one HeII row, with HI and HeI rates supplied separately by the selected UVB contract. The strict equality choice follows §4's z<=4.75 transition convention. Photon energy boundaries and moments are eV; cross sections cm². Data are encoded in radiation_moments.json.
IncidentPhotonExposure must supply:
- phi[i] >=0, unit photon cm^-2 s^-1, proper frame, source and temporal trace identity;
- regime, z, spectral-template identity, speed convention, validity domain;
- if derived from energy density u[i], explicit unit conversion and phi=c_rate*u/eMean.
For isotropic radiation this exposure is c*n_gamma; it is not the magnitude of net flux, which vanishes for isotropic intensity. A comoving energy density must first be divided by a^3. Lumina defines its transported energy moment using reduced speed0.2c; own physical stress-energy must retain true-c normalization unless an explicit equivalence map is supplied.
The linear operators are
Gamma_j=sum_i phi_i sigma_ij [s^-1],
h_j=sum_i phi_i sigma_ij excess_ij * epsilon_eV [erg s^-1 target^-1],
Q_photo=sum_j n_j h_j [erg cm^-3 s^-1],
epsilon_eV=1.602176634e−12 erg/eV.
For late HI/HeI null heating entries mean inactive operator routes, not zero physical heating. Their UVB provider owns those terms. No fallback duplicates both UVB and transported HI/HeI heating.
Moment definitions: sigma_bar=∫sigma I(E)/E dE /∫I(E)/E dE; excess_bar=∫sigma I(E)(E−threshold)/E dE /∫sigma I(E)/E dE; eMean=∫I(E)dE/∫I(E)/E dE. Therefore eMean−threshold generally differs from excess_bar. Rates are exact for the adopted within-bin spectral template; spectral hardening or mixtures require new moments.
This operator is executable for explicitly supplied phi. The public global tables do not determine phi, so an arbitrary demonstration phi must remain a labelled fixture.
The conservative energy partner uses absorption weighting: absorbed_energy_ij=phi_i sigmaN_ij(threshold_j+excess_ij). This equals threshold_j times the primary ionization rate plus the primary excess-energy rate. It generally differs from phi_i sigmaN_ij eMean_i. For an energy-density sink, derive sigmaE_ij=sigmaN_ij(threshold_j+excess_ij)/eMean_i; then c_rate u_i sigmaE_ij is the same absorbed-energy rate. Use consistent energy units throughout. This relation follows directly by multiplying the defining moment integrals; it avoids treating photon-number and energy opacities as identical. Secondary-ionization/excitation channels, when selected by native physics, partition primary excess through that existing energy partner rather than adding it again as heat.

## Source and thermal conventions
Early sources: stars (BPASS2.2.1, escape fraction.18), AGN, HMXB and shock-heated ISM. Late transported source branch: AGN only. Source SEDs/escape rules affect rates; source labels alone do not determine intensity.
Lumina uses M1 transport, reduced speed.2c, omits cosmological photon redshifting, and deposits primary excess energy as heat without secondary ionizations. Import these as benchmark conventions, not replacements of existing kinetics.
For monoatomic nonrelativistic ideal gas with u=3nt kB T/2, p=nt kB T, D_t nt+theta nt=Snt, and D_t u+(u+p)theta=Q:
D_t T=−(2/3)theta T−T Snt/nt+2Q/(3kB nt).
Snt accounts for changing particle count (e.g. liberated electrons). If nt=nH(1+y+xe), the middle term is −T D_t xe/(1+y+xe). In isotropic homogeneous expansion theta=3H and constant ionization, Q=0 gives D_t T=−2HT.
This equation requires separately identified heating, cooling, compression and ionization energy bookkeeping. Adding primary heat to a kinetic electron injection that already thermalizes would double count.
nH>=.106cm^-3 cells in Lumina follow a transparent effective-ISM treatment; the effective EOS temperature cannot be used as a microscopic Maxwellian bath temperature. Thermal-history T0 fits use overdensity .3<Delta<10. A local bath (n,T) test must state this mask and density definition.
The aggregate Gamma/primary-energy moment operator has no electron-grid restriction. A separate kinetic coupling into a grid supported only through150eV requires actual within-bin spectral support or a conservative bound E_hi−E_threshold<=150eV. Mean excess is insufficient to certify support. For the100–200eV bin, maximum primary electron energies are186.4eV(HI),175.41eV(HeI),145.58eV(HeII); the late54.42–2000eV HeII bin extends to1945.58eV despite mean excess13.5eV. Mean excess>150eV establishes an out-of-grid component, while mean excess<=150eV alone grants no admission. Default kinetic action is DomainError with named row/species and upper-support value; an explicitly selected extended grid or rigorous tail closure requires convergence and energy-partner checks. Do not clip, renormalize, or replace an entire spectrum by a delta at its mean. Lumina table threshold convention is13.6/24.59/54.42eV; prior native BED13.6057eV remains separately named and unchanged.

## R5: Bianchi invariants and actual observables
Primary geometric cross-reference: Pontzen & Challinor(2007), https://arxiv.org/html/0706.2075v2 , §§2–4, separates homogeneous symmetry, group-invariant tetrads, photon propagation and Boltzmann scattering. The projection identities below are the present adapter derivation; they require an explicit observer and ray rather than an algebraic relabeling of global history tables.
Adopt signature(−,+,+,+). Geometry, observer four-velocity, spatial tetrad and chemical-frame conventions must be explicit. With normalized timelike U.U=−1, projector h=g+U U, expansion theta=∇.U, shear sigma_ab projected symmetric tracefree ∇U, scalar sigma²=sigma_ab sigma^ab/2. Tetrad rotations change components, while scalar contractions and the observer-defined photon energy are invariant under those rotations. Changing physical observer changes measured photon energy and is not merely gauge.
For null ray dx^a=k^a dλ, positive path length in U frame is dℓ=−U_a dx^a; optical depth dτ=σT ne dℓ is scalar for the specified matter rest-frame density. Observed1+z=(−U.k)_emit/(−U.k)_obs; both require actual null transport and observer endpoints.
For geodesic, irrotational homogeneous matter flow, directional redshift depends on expansion and shear contraction sigma_ab e^a e^b. A mean-scale-factor z is a background label; it is not automatically every observed line-of-sight redshift.
In FLRW, dℓ=c|dt| and |dt/dz|=[(1+z)H]^-1, recovering τ(z)=cσT∫ne(z')/[(1+z')H(z')]dz'. Lumina tau is an isotropic-reference diagnostic. No angular CMB spectrum, kSZ, 21cm map, Lyα spectrum, or Bianchi likelihood follows from four global tables alone. Positive next construction is electron history plus actual ray/visibility transfer under the existing scenario+L4 gate.

## R6–R10: verified scope, node gates, next execution
Remote Wolfram Language evaluation in wolfram_identity_check.wl/results.json returned LS=0, covariance residual0, y=3/38, xe=22/19, the derived thermal equation and adiabatic limit−2HT. Context search returned irrelevant/no results and supplies no scientific support; only explicit evaluator results are adopted. Remote CPU telemetry UNKNOWN, not zero.
Independent reviewer confirmed HeIII label anomaly, early helium-closure positivity issue and reduced-c normalization boundary. These are corrected in this contract. No new strong no-go claim is made; NG1–NG7 admission is not invoked.
REC-EXP-EXTERNAL: source contract and moment operator are ready; actual selected incident trace remains missing. Integrated heating or reionization histories do not become spectra. Preserve its OPEN state and canonical29/88 until native gate evidence exists.
REC-EXP-SPECTRAL: apply selected trace through typed units, detailed balance, energy partner, bin interfaces, native Lyα ownership and domain checks. Six+one moments alone close none of those full requirements.
REI-EXP-OBSERVABLE: retains scenario+L4 dependencies; tau reference and electron projection prepare its inputs.
Positive execution transition now: ingest four exact tables; validate semantics and anomalies; render source-labelled benchmark panels, HI complement on its native domain and HeIII median only; implement seven-row Gamma/heating operator with explicit incident input and regime dispatch; run permitted deterministic conservation/domain tests. Then use the selected incident trace to couple H6/REC-FIELD. This is a measurable reference/operator extension while canonical physics closure remains separately tracked.

