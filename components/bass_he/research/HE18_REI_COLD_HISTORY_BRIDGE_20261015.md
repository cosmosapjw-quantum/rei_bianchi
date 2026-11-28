# Cross-repository HE18 / rei_bianchi cold-history bridge, 2026-10-15

Authority boundary: This is a read-only downstream integration receipt, not a HE18 warm-source calculation or a replacement of the 16-cell certificate.

## Source tracks
- Warm BASS_HE HE18 P01 FT03/HM12 source-scoped 16-cell archive (SHA256 5c2f4c877b743924d0726c54a200d61f3182125337a00994c969ba020718f12d) and this repository branch research/he18-p01-remaining-cells-20261015 at b0af50b0.
- Cold rei_bianchi Plancklike_MD14_BB50K full AXBI history with Y_He=.2454, He/H=1227/15092 and original source-provenance SHA pins. Warm uses different temperature, opacity, H/He ratio and photon-stock conventions; their tau values cannot be swapped.
- Verified implementation and numerical receipts: cosmosapjw-quantum/rei_bianchi branch research/bass-he-optical-depth-transfer-20261015, commit e3921c3320f2bccd82661859365826ac4c72ae18, directory research/bass_he16_transfer_20261015.

## Cold post-processing observations (not native scientific admission)
- SHEAR_MINUS q=-0.01: 312238 rows, zbar20->4 tau=0.03196792354404614; original history SHA256 0c1d2479eebef9b1ec2d4ff56417ee3395ecd122c17326d4a8d827e2ead76d11.
- SHEAR_HALF_PLUS q=+0.005: 312238 rows, zbar20->4 tau=0.03196811801369409; original history SHA256 50efa302db22f58d55c17c0c18c4b0c94e2063cc729e12067a05b2337373031e.
- At fixed terminal mean scale zbar=4, difference=1.9446964795444277e-7; at common proper time=9.871560356644604e-8; endpoint clock contribution=9.575404438799673e-8. This decomposition is algebraic, NOT an isolated signed shear coefficient.
- End-to-end after source SHA, parse, H/He census and tau: user Ubuntu sequential median 4.711s; two independent processes 2.381s (1.979x). 21 Python regression tests passed on the Ubuntu host. Wolfram check of normal/tilted null contraction, electron derivatives and cm^-3 -> m^-3 gave zero residual.

## Admission gate
These two cases differ in q amplitude and sign, and terminal proper times; no claim of pure shear detection or full CMB optical depth z=20->0. Original source ODE whole-history error, continuity/geometry clock enclosure and native roundoff remain unresolved. Numerical source-ODE replay was not performed.

Preserve original BASS_HE HE18 proof and all cold AXBI result identities independently. Exchange algorithmic improvements (vectorization, bounded-memory streaming and exact decimal conditional bounds), not numeric outputs across incompatible models.