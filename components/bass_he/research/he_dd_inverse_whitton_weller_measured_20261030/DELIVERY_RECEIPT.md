# BASS_HE PR121 | original EXFOR inverse DD radiative capture, 2026-10-30

Draft PR121: https://github.com/cosmosapjw-quantum/BASS_HE/pull/121 ; immutable parent PR120 HEAD 83596b913a08dd31496b7abbb7d5a9972fff5cc1. Add only, no merge or force push. The exact final HEAD of this receipt is query-dependent, do not guess.

## Original experiment evidence
IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871 original snapshot Git byte-identical and locally SHA-locked:
C0122 Whitton1993 PhysRevC48 2355: SHA256 d8607f894d437ae8113f2c230b7d08b13ff49521c589791200564f1ff1a943c7; Git blob ac638ddbea7795b281ab8494d3e75a62606b3f6d; 29 source rows = 14 REL capture DA +15 dual-component polarization rows. REL means NO-DIM, never absolute.
A1256 Weller1984 PhysRevLett53 1325: SHA256 456fe18134fec0a25d981148989c9af3faae447f4881dddb6f6f7dd102bfe9e4; Git blob b4dba8ecb9ce5eb44501b9afba4c40db329b826b; 12 source rows = 6 PAR DA curve-digitized partial capture plus 6 TAP tensor polarization. Partial capture is not an unpolarized total.
Historical pre-existing forward low-E donor M0011 original Git blob 20804471fb7584e07ab979ecad6a3e96cba0c6a2; M0826 original Git blob 95010842754215e98eea8d99eff5f3de0799c666; source content is preserved byte-identically and is not counted as new measurement.
Forty-one source experiment rows contain 56 scalar components; they are not forty-one independent experiments. Original sources kept in sources/*.x4. For exact M0011 authority refer SOURCE_IDENTITY.json.

## Actual physical outputs
Exact invariant-s alpha-rest photon energies for D lab 9.7,20,30,50 MeV are 28.80378755500563,33.98673546536357,39.01872372784700,49.08270025281387 MeV; equivalent kinetic source crosswalk, not measured photon energies.
Source C0122 measured 30 MeV REL near90/shoulder ratio 0.0260638297872 with source error Cartesian box [0.0113300,0.0433526]; 50 MeV ratio 0.0375 with [0.0294118,0.0466667]. Seven mirror pairs possibly source-symmetrized and not independent checks.
Source A1256 9.7MeV, theta51.4deg original partial capture DA 1.405e-05 mb/sr =14.05nb/sr, ERR-S 7.176e-07mb/sr =0.7176nb/sr, source CURVE and MONITOR, not unpolarized photonuclear total.
No spin/identical-D detailed-balance event factor promoted from kinematic q^2/k^2; sigma_event unknown. No gamma field f_gamma(t,x,p), no D_fast stopping and heat source.

## Actual verification and backup
Local Python 19/19 targeted tests including source-tamper fail-closed, compileall PASS. Wolfram independent numeric 4 energies, q2/k2 and two ratios and error boxes PASS. Source/code/test/data output Git blobs checked exact against original or local tested bytes.
Twenty real distinct stage Git commits R01-R10/C01-C10, full SHA and per stage Central28/88, HE14/18 and new 0/2 to2/2 in STAGE_LEDGER.json. Google Drive and Dropbox Paper source stage text receipt 20/20 SHA readback each. Two grouped text uploads per provider, not twenty separate provider operations.
Full source-inclusive local ZIP BASS_HE_PR121_WHITTON_WELLER_REAL_EXFOR_20261030.zip, size 67607B, SHA256 61ad4b2002f79a88e96826a74e5b227db62f1d0df8b66a1406b2b423a3fbd442, 24 entries=23 payload + manifest. Clean isolated extraction: CRC and all payload SHA PASS; original source Git blobs PASS; Python 19/19 and compileall PASS; 3 JSON/CSV/crosswalk outputs byte-identical regenerated. Nested original PR120 ZIP SHA256 703bcef62463d794bd60f0902d1db829084907808fd8bea6e29133a2b5cf4b9f.
ChatGPT Library original ZIP upload ACK under /BASS_HE_PR121_INVERSE_WHITTON_WELLER_20261030/. Google Drive full ZIP upload ACK ID 1uW1-0lRGygZT_sqHz0d5OsMiZmYg9XmR, https://drive.google.com/file/d/1uW1-0lRGygZT_sqHz0d5OsMiZmYg9XmR/view . Actual Drive raw 67607B download and cmp, SHA256, ZIP CRC PASS.
Google Drive stage text https://docs.google.com/document/d/1wBzwKFNMTSdYIWBLIsb8_7oYebQHndu8-rprcppqv5k/edit ; Dropbox Paper text https://www.dropbox.com/scl/fi/ojpzfkw535vapzbk1pye4/BASS_HE-PR121-source-owned-Whitton-Weller-inverse-DD-stage-git-receipts-20261030.paper?rlkey=o93dxuq38qn5zxu4gkty0g85q&dl=0 . Dropbox full ZIP binary upload/readback NOT_RUN.
Independent fresh-context R6/C9 native subagent NOT_AVAILABLE; GitHub CI status cannot be described PASS if absent; old IVP, 4501-node LP not rerun.

## Gate / scoped DAG
Canonical Central28/88, HE physical14/18, PR114 lowE3/4, PR119 Angular2/3, PR120 Shape2/2 unchanged. NEW source-only Whitton Weller 2/2 scoped (41 original records plus typed invariant-s physical crosswalk), physical delta 0, kappa=null, R_event=null, heat_rate=null, L4=false, physical_activation=false, production=HOLD.
NEXT: authenticate original Whitton REL normalization and beam/covariance, Weller PAR cross-section monitoring, identical D event-count convention and Rice high-E original numeric data; use source-qualified target-rest gamma phase-space and D_fast stopping before physical DAG promotion. No automatic merge or next node.
