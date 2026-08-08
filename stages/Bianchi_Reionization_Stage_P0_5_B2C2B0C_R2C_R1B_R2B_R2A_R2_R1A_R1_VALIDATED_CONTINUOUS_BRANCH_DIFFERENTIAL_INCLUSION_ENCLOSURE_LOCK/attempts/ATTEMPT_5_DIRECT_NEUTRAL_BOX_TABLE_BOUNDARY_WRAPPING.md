# Attempt 5 — direct-neutral componentwise box reaches a spurious table boundary

The final componentwise coordinate choice was `(x_HI, x_HeI, r_HeIII, log T)`.  It preserves H nuclei and the He simplex structurally and avoids the singular amplification seen in the previous logit/log-reservoir attempts.

Nevertheless, the outward-rounded Picard tube for every locked partition (16, 32, 64) expanded during the first self-mapping iteration until its temperature component crossed `T=10^5 K`.  The authoritative Hummer--Seaton policy forbids extrapolation there, so the attempt failed as `TABLE_TOPOLOGY_EVENT_UNLOCALIZED`.

This is a dependency/wrapping failure of a componentwise box.  It is not a physical temperature excursion, not a failure of the 24 numerical corner trajectories, and not evidence that the continuous family lacks solutions.
