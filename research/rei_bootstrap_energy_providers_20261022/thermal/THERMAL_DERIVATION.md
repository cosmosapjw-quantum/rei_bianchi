# Closed gas and photon energy ledger: bounded continuation

2026-10-22; theory authority `/root/thermal_contract`. This continuation uses physmath-research-loop 1.0.0 / approval 0.2. Locally observed repository HEAD is `8be7533cc97b3302bf42608699d6e8313ed6af8a`; no dirty entries were returned at intake. The published `a7bff87` theory and independently reviewed 29 arithmetic comparisons are reused without rerunning. Recovered local theory is an unadmitted candidate: its derivations are assessed here, but its claimed 72+30 checks and source reads are not new execution evidence in this lane.

## Result and assumptions

For homogeneous geodesic, non-tilted LRS Bianchi I, the equations below give a closed **exchange ledger conditional on supplied event and spectral moments**. Gas is nonrelativistic, monatomic and one-temperature; ions and thermal electrons are ideal and share T. Ionization thresholds are fixed. Atomic PI/RR uses negligible recoil and prompt complete cascades unless energy is explicitly assigned to another reservoir. This unit supplies scalar instantaneous calculations, not spectral transport or an integrated solution.

Use physical time seconds, SI densities and energies, signature (-,+,+,+), explicit k_B and c. Write isotropic pressure P and signed anisotropic amplitude p separately:

`sigma=diag(-s,-s,2s)`, `pi_X=diag(-p_X,-p_X,2p_X)`, `sigma:pi_X=6s p_X`.

Each separately owned component satisfies

`dot epsilon_X+3H(epsilon_X+P_X)+6s p_X=Q_X`.

Gas is isotropic in the physical implementation here, p_g=0. Nonbaryonic massive matter p_matter and photon p_radiation are distinct inputs and owners; they must never be equated or substituted for each other. Internal exchange sources sum to zero; expansion and shear work remain explicit. Conserved total proper energy density is not claimed in an expanding geometry.

## Particle number, internal energy and temperature

For every thermal species `dot n_i+3H n_i=S_i`, with `n_part=n_heavy+n_e` and `S_part=S_heavy+S_e`. Fixed-nucleus atomic channels have S_heavy=0. A thermal electron population must exclude separately evolved fast electrons until their declared deposition/injection. Quasineutrality counts all relevant charge populations, not only the thermal electron pool.

Let `U=3 k_B n_part T/2`, `P_g=k_B n_part T`. Expanding its first law gives

`dot U+5HU=Q_kin`,

`(3/2)k_B n_part dot T+3H k_B n_part T+(3/2)k_B T(S_heavy+S_e)=Q_kin`,

`dot T=-2HT-T(S_heavy+S_e)/n_part+2Q_kin/(3k_B n_part)`.

The gas heat capacity changes with both sources. For fixed composition and Q_kin=0 this returns T proportional to a^-2. Recovering dot U from the derivative of U verifies the equation independently.

Define stored ionization energy `B=sum_i I_i n_i`, with I_i positive cumulative thresholds from the chosen neutral ground reference. Then

`dot B+3HB=Q_B=sum_i I_i S_i`.

The reference neutral rest inventory is counted once in the inherited baryonic rest component. B is an internal positive reservoir and cannot also be included in that reference rest mass. Nuclear conversion needs a consistent separate rest-defect ledger; this scalar unit supplies no nuclear masses, reaction network or daughter charge closure.

## Single-event ownership and closure

PI with rate R, absorbed photon energy-rate A, threshold chi and immediate thermal deposition has `(Q_kin,Q_B,Q_gamma)=(A-chi R,chi R,-A)`. For nonthermal deposition replace the first entry by a declared thermal fraction and assign the remaining excess once to Q_nonthermal; do not additionally heat the gas by that amount.

RR with total capture rate R and removed electron kinetic energy-rate C has `(Q_kin,Q_B,Q_gamma)=(-C,-chi R,chi R+C)`. A capture to excited level l emits free-bound energy `chi_l R_l+C_l`; its complete prompt cascade emits `(chi-chi_l)R_l`. Assigning chi+C/R to every free-bound photon falsely puts line energy in the continuum. Total rate and kinetic moment do not specify the emitted spectrum or its photon count.

For a temperature-independent cross section and fixed target-state weighting, differentiation of `alpha=A0 T^(-3/2) integral epsilon sigma(epsilon) exp[-epsilon/(k_B T)] d epsilon` yields `lambda=k_B T alpha[3/2+d ln alpha/d ln T]`. Finite convergent moments and differentiation under the integral are required. A fitted alpha's accuracy does not bound its logarithmic derivative. RR moment-provider accuracy belongs to the separate provider lane. Case A diffuse emission and Case B local elimination require different consistent event sets; they cannot be added together.

The generic reservoir set is gas, stored ionization, resolved excitation, photons, nonthermal particles, neutrinos, and nuclear/reference rest-defect energy. Every transfer has one positive recipient and its actual donor. External primary radiation has an explicit external-power term or an evolved emitter reservoir with the equal negative source. A prescribed UV bath is therefore an open subsystem.

## Fixed photon bands, anisotropic work and partners

Let n(E,mu) be photon number per proper volume, energy and steradian. Axisymmetry uses dOmega=2pi dmu. Conserved spatial momenta give

`D=H+s(3mu^2-1)`, `dot E=-E D`, `dot mu=-3s mu(1-mu^2)`.

The number transport equation is `partial_t n+3Hn+partial_E(dot E n)+partial_mu(dot mu n)=C`. Its expanded dilution coefficient is `3H-D+partial_mu(dot mu)=2D`, consistent with occupation number proportional to n/E^2. Regular angular endpoints carry zero flux.

For fixed proper-energy boundaries, define `N=integral n`, `U_gamma=integral E n`, `p_gamma=(1/6)integral E(3mu^2-1)n`, and boundary fluxes `F_N=[integral dot E n dOmega]_lo^hi`, `F_E=[integral E dot E n dOmega]_lo^hi`. Integration by parts gives

`dot N+3HN=C_N-F_N`,

`dot U_gamma+4HU_gamma+6s p_gamma=C_E-F_E`.

At a shared interface the same flux must enter the adjacent band with opposite sign. The outside-band photon state owns its expansion and anisotropic work as well as transferred photons; a cumulative loss counter does not supply this state. Directional blueshift can reverse flux and must not be clipped. Photons emitted outside the grid enter the outside state directly.

Adding gas, B and a complete disjoint photon partition yields

`dot(U+B+sum_b U_b)+3H(U+B+P_g)+4H sum_b U_b+6s sum_b p_b=L_external`

when PI/RR transfers and internal interfaces cancel. Additional physical reservoirs add their own first-law equations. Adding an emitter with source -L_external closes the corresponding exchange system. This is a derived conditional identity; it does not provide the missing spectra, band closures, collision moments or Einstein backreaction.

## New discriminating analytic fixture

In dimensionless manufactured units choose `n(E,mu)=E[1+P2(mu)]/(4pi)`, `P2=(3mu^2-1)/2`, band [1,3], H=1/2, s=1/4, C=0. The distribution is nonnegative. Since `<P2^2>=1/5`, direct angular integrals give N=4, U=26/3, p_gamma=26/45, and energy-weighted mean D=3/5. Hence `F_N=-24/5`, `F_E=-78/5`, `dot N=-6/5`, `dot U=-13/5`. Substitution gives `dot U+4HU+6sp=78/5=-F_E`. Omitting shear work leaves -13/15 residual. These are analytic expected values for new lower-tier checks, not an execution receipt.

## R1–R10 state and transition

R1 scope/identity fixed above; R2 unchanged published derivations, provider classifications and 29-check review reused; R3 assumptions/ownership explicitly fixed; R4 conservative U/B and separate photon bands retained; R5 derivations above complete; R6 reverse gas chain rule, occupation-number identity and angular moment derivation completed; R7 old 29 checks reused and new anisotropic/source fixtures specified, new execution pending; R8 conditional equations adopted for implementation, production claim unchanged; R9 frozen scalar code contract accompanies this document; R10 next action is lower-tier execution followed by fresh independent authority review. No new no-go result is proposed (NG1–NG7 therefore not applicable).

The historical source citations remain in published THERMAL_THEORY.md. This continuation derives its new moments algebraically and does not represent inherited source-reading claims as new browsing. No old83, physical IVP or NCP trial is performed or authorized by this unit. Spectral source/cascade providers, directional transport, nuclear injection and full backreaction remain separate execution dependencies.
