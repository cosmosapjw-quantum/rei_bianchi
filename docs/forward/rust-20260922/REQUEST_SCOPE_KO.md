# Approved source-only forward scope

REPO=cosmosapjw-quantum/rei_bianchi
BASE_COMMIT=ae3402713c4b6530ab2b27f008f5f5d5c6a999ed
TARGET_BRANCH=forward/rust-reion-kernels-20260922
CRATE=rei_microphysics

The user approved source port and candidate publication here, with compilation/parity delegated to local Codex. C1 is an uncompiled candidate, not tested delivery.
Whitelist: transform_z_to_y, pchip_eval inside its finite closed domain, opacity_cMpc_inv, photon_rates, gamma_species, positive_mass_projection, signed_transfer_lift; directly necessary pure arithmetic and typed/protocol adapters only.
Preserve CGS, proper/comoving density, cMpc, lowgroup effective HI ownership, explicit G2a HeI/highgroup species, redshift transfer, four independent sites and exact reference pins.
Do not port residual/ODE/optimizer/additional rate fits/bernoulli or capacity projections. A7/A6 is boundary provenance only. D86 remains canonical; S3 accepted, S4 partial, S5 gated, G10 open, G11-G13 gated, P0 physical OPEN, HOST4 physical HOLD, HH propagation unauthorized.
No default-branch mutation, merge/release/force push, PR creation, workflow changes or workflow_dispatch. No bass dependency edit before final tested delivery.
