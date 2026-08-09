# Preserved failed attempt — one fixed branch pair per node and substep

The first sparse representation retained the full node-local source rank but
used one fixed `(theta_v_i,theta_f_i)` pair over a complete accepted substep.
This was falsified by an explicitly localized upper-to-lower schedule. The
schedule passed all physical/numerical gates but escaped the static four-corner
endpoint hull in `x_HeIII` by `6.979149463209877e-12`, or about 3.31% of the
local static width. The representation remains valid as an instantaneous source
model and conditional static-policy auditor, not as a source-safe flow
certificate.
