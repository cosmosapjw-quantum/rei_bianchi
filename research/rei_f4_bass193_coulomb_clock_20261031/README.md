# REI F4: original BASS193 electron stopping clocks (2026-10-31)

## Source and scientific claim

Original saved 193×21 BASS21 chemistry, ne=nb(q·Y), H(z), proper elapsed clock, Bianchi b(ln a), and PR306 immutable first-flight absorption:
- parent PR308 HEAD a8725f5cdd739af0682c53f9237d410f03bd9be0 (read only)
- original source owner PR306 ZIP REI_F4_CAUSAL_MEMORY_20261031_FULL.zip, 7,125,786 bytes, SHA256 d46b61d49b025c6a81b003304223cb9c9aec5863432c80c53e883cf11055ad88.
- independent sibling PR307 moment-bounded deposition and PR308 CCC channel-capacity analysis are not repeated.
- source is a conditional Li II 2E1 singlet upper, NOT observed positive Li II singlet abundance lower bound.

**Original adopted primary source:** Furlanetto and Stoever (2010), MNRAS 404 1869–1878, DOI 10.1111/j.1365-2966.2010.16401.x, Eq.(5) and Eq.(12), Gaussian cgs, E>13.7eV. Use original BASS electron bath and no new cosmological IVP. Under lnLambda>1,

t_ee = sqrt(2m_e) E^(3/2) / (4pi(alpha hbar c)^2 ne lnLambda),
lnLambda=ln[4E_eV/(7.40e-11(ne/cm^-3) eV)].

The characteristic stopping time for 61eV primary electrons has maximum across original 192 intervals of t_ee/Δt=0.07305598881236372 (original saved interval endpoints' minimum ne); integrated loss from 61 to 13.7eV has maximum τ/Δt=0.04400523622550507, and max H t_ee=0.0007348130555582834. Stronger statement about the 10.2–13.7eV residual and the full collision/secondary cascade is NOT made. Cross-check original source-weighted t_ee/Δt=5.123714642808894e-05. Source kinetic energy above 13.7eV is provably between 0.43315036703749826 and 0.7912973138436458 of original 6.749242464433258e-11 eV/b based only on five-band moments.

Bianchi a_perp=a exp(-b), a_parallel=a exp(2b) gives min dln(a_perp)/dln(a)=1.0000034842502283, min dln(a_parallel)/dln(a)=0.9996267666361096: no photon blueshift on the saved piecewise-linear b(x) background. A LiII 2E1 photon E<=60.922559447552eV cannot open the **direct Ferrett LiI 1s2s 3S** threshold at 64.41eV or LiII continuum ionization at 75.64eV; LiI outer-shell and subthreshold core resonances/Auger are NOT excluded.

Verner et al (1996), ApJ 465 487, DOI 10.1086/177435, author source https://www.pa.uky.edu/~verner/photo.html is ALREADY used by BASS native AtomicNetwork and not replaced here. Grackle https://grackle.readthedocs.io/en/latest/Network.html supplies authoritative public H/He chemistry comparison but is not a rate source for this specific Coulomb run. Original Curtin CCC https://atom.curtin.edu.au/CCC-WWW/index.html is appropriate for subsequent nonthermal electron ionization cross sections, not yet sampled in this unit.

## Data and validation
Original source files and exact 193×21 trajectory remain private in previous immutable source ZIP; this public branch includes actual source-derived witness rows and executable independently tested replay script. The FULL local study and plots: 193 plasma source rows, 12,352 E×epoch evaluations, 192 arrival bins, 5 PNG + 5 SVG, 26/26 tests, 14/14 deterministic output replay, 48/48 manifest and clean ZIP restore pass. Master local ZIP 8,039,981 bytes SHA256 f4afbef4475dc8e0320a4c5d22792b5da6ad6a8d4be19f427af949a4dfd59233 (do not claim external cloud backup without ACK). A minimal published replay was separately executed and matched five published extrema to <1e-14.

This is one source-scoped auxiliary science result. No full REI17 F/J, no actual gas ΔT or CMB. No new IVP, no source replacement or alteration. Same-author hostile audit only, independent-author R6/C9 NOT_RUN.
Working 33/88; Central 28/88; PhysicalFast 4/7; canonical delta 0. F4 PARTIAL, L4_READY=false, PRODUCTION HOLD, NO_MERGE, NO_FORCE_PUSH, NO_BUDGET_RESET, AUTO_NEXT_NODE=false.
