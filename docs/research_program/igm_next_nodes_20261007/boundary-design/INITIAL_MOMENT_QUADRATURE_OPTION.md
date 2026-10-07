# Optional initial-moment-exact quadrature construction

Exploratory mathematical implementation option for the proposed pure-radiation prototype, not an implemented or empirically validated method. It is separate from the frozen reviewed design.

For a positive reconstruction f0 on one geometry-split eta interval J, compute its initial moments analytically (or with independently certified error):

    nJ = integral_J f0 d eta,
    mJ = integral_J exp(eta)*f0 d eta.

If nJ>0, the mean tJ=mJ/nJ lies inside the interval's energy-coordinate bounds. A one-point quadrature with positive weight nJ and etaJ=ln(tJ) integrates the functions 1 and exp(eta) exactly under the measure f0 d eta. These are constructed physical moment weights, not ordinary Gauss weights rescaled after a failed budget. Refining J or using higher-order positive quadrature improves absorption/spectral-shape accuracy. The one-point rule alone is not a convergence certificate.

Use the linearity of the frozen characteristic equation to keep the two contributions distinct:

1. Initial-stock contribution: q=0 and unit initial density at etaJ, then multiply the entire characteristic transaction (survivor, species absorption number/energy, redshift, export) by nJ. Its initial number and comoving energy are exactly nJ and mJ in the represented arithmetic. Repeat on all disjoint topology/swept subintervals. No persistent physical photon atom is introduced: quadrature is rebuilt for each panel integral over the current continuously cut subinterval.
2. Continuous-source contribution: f0=0 and the declared continuous q on each exact source-active time segment, integrated with a positive spectral quadrature. Each source quadrature sample contributes its full same-owner characteristic transaction. Its emitted ledger must equal the source approximation actually injected; do not replace only that ledger by the analytic continuum total. The source remains continuous in time within each subinterval; this construction does not require discrete source-birth pulses.

Sum the two positive transactions. The local number/energy identities hold for each contribution, and exact initial moment quadrature removes the initial-moment drift that ordinary fixed Gauss2 can introduce. Source quadrature accuracy, topology splitting, initial subinterval integration, moment arithmetic, redshift/cutoff handling and higher spectral moments still need their own tests and error accounting. If the source contribution itself is also made moment-exact, construct that positive rule from the source measure before evaluating owners; do not add an after-the-fact normalization.

When initial support is empty, retain the zero-source state without computing mJ/nJ. When moments are stored as logs/tails, form the mean by a stable log ratio; no underflowed readout may be reclassified as exact emptiness. Tiny subinterval geometry still needs stable analytic integration. For source-front panels the reconstruction must retain its interior front-vanishing shape and causal support.

A future implementation should directly test whether this construction is simpler and more stable than generalized weighted Gauss quadrature. Its stage cost can exceed current Gauss2 because geometry subdivision, source and initial contributions, and moment reconstruction are additional work.
