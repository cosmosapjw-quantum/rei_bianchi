Publication note: hash declarations in this historical report identify archived original bytes. Relocated publication hashes are recorded in ../PROVENANCE.json. Some historical guard/run artifacts are summarized rather than copied; use ../README.md for the supported replay boundary.

# Exact stored-event energy-anchor corrective slice

The original CONTRACT.md and frozen V2 source remain unchanged. The first A attempt is retained as a failed conditional gate, not reclassified as passing. The dated additive arithmetic correction (2026-10-07) addresses the recorded failure: an exactly stored HeI crossing reconstructed E_end=24.589999999999996, so the unchanged V2 kernel rejected it.

An exact event is identified only by binary64 equality with the predeclared tau_i=eta-ln(CUTOFF_i), never a distance tolerance. For a segment ending at that exact event, compute e_start=CUTOFF_i/exp(-(b-a)). Require that e_start*exp(-(b-a)) equals CUTOFF_i exactly. Otherwise reject; no epsilon, nextafter, clipping, altered threshold or repair is allowed. For a segment starting at an exact event, use that event's exact CUTOFF. Ordinary endpoints use the existing exp(eta-a) representation. A segment with incompatible exact start/end anchors rejects.

Pass the selected start energy into the unchanged V2 kernel so its final energy, species absorption energies, source energy and redshift energy share one convention. Never replace a final energy or ledger afterward. Carry the last kernel's energy result through characteristic aggregation, and verify support and cross-segment continuity. Midpoint sigma and q remain exactly the frozen contract's ordinary E_mid=exp(eta-(a+b)/2). Quadrature and all original gates, thresholds, physics, resource limits and exclusions remain unchanged.

Focused tests precede green numerical execution: exact HI/HeI/HeII event identity; adjacent binary64 times receive no special status; no absorption below cutoff; cross-segment event continuity; radiation and photo-material energy identities. A rounding failure in division/multiplication is a new honest blocker, not permission to broaden this rule.
