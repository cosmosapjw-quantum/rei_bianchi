# Scope-matched parent check

Read source lorentz_l2.py, lorentz_power.c, hh1_energy_adapter.c and hh1_energy_adapter.h after the production verification runs. The parent independently requested Wolfram integration of the Maxwellian moment and algebraic PI/RR and variable-particle-number temperature identities. Actual CAS outputs are recorded in theory/WOLFRAM_CHECK.json.

HE1: angular kernel 2pi(1-P2)=3pi(1-mu^2); denominator Gamma(7/2) and numerator Gamma(4+r/2) match the Grad pressure weight. C and Python power-law functions use the same stated infinite-domain model, convergence r>-8 and explicit nonrepresentability failure. Finite-domain quadrature returns partial results and only an assumed-global-cross-section tail bound. Its quadrature error is not an interval certificate. The tested nonexponential finite-time Lorentz evolution correctly limits interpretation to an instantaneous projected rate. PASS_SCOPED for this functional.

HH1: header binds eV, proper seconds, rates per reference H1, particles per reference H1; this agrees with the temperature implementation and its -2HT term for an untilted homogeneous background. The source computes E-I before rate multiplication, retains binding/radiation signs, gates photon energy at the threshold, and does not fabricate cross sections. RR is explicitly the supplied case-A event ledger. PASS_SCOPED for the adapter, with modeled isotope defect inherited from the pinned owner convention; this is not isotope-rate admission.

This is one parent verification pass with CAS, not a fresh-context independent-model review. No historical campaign was rerun. New broad production or finite-mass transport claims are not made.

