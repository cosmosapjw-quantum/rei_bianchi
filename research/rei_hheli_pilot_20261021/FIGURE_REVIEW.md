# H/He/Li figure review — PASS_SCOPED_FIGURES

All10 actual PNG families were visually inspected, with matching plotting code and underlying saved-data mapping. Repaired plots were read back. Matching PDFs are present; the visual inspection claim concerns the PNG renders at delivered dimensions.

Three layout findings are closed: scaled axes remove scientific-offset/x-label collisions; plain cancellation tick labels remove the title collision; the shortened Li note sits away from the legend and curves. A fourth scientific wording correction is closed: Li q2/q3 are analytic zeros under the selected source and initial state, but the saved unclipped Radau fractions contain residual magnitudes below5e-28. The final isotope plot, abundance census title and plot manifest state this accurately; n/T remain exactly absent.

The new component-response map subtracts the separately computed actual zero-initial-stress case at the same initial Sigma. Baseline IDs and values are exported, and no trajectory-superposition, fit or interpolation claim is made. The electron/optical-depth/forcing figure uses actual saved isotropic-case n_e and tau, prescribed T and Gamma_HI/H; its forcing midpoint marker does not claim that ionization must occur at that redshift.

Signed sources, norm cusps, paired-isotope closure equality, trace abundances and zero states are visible. Symlog is used with an explicit linear interval, without replacing zero with epsilon. The energy-ledger and diagnostic captions preserve their limited scientific meaning. No further figure repair or numerical run is required. Exact final hashes are in FIGURE_REVIEW.json.
