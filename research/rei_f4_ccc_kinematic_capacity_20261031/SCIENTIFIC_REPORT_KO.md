# REI F4 | Original BASS193 electron secondary-channel accessibility (2026-10-31)

Immutable parent PR #307 HEAD `6b5ab8a243f31004306b22041c2ec03baf1e009e`. Sibling PR #306 HEAD `940d13b18a657f7d0aeb44961e48a5cef7e742b4` is read-only. No merge, force push, owner source switch, new IVP, temperature/CMB prediction, or canonical DAG promotion.

## Primary sources and widely used codes

- **Original BASS193 physical source SSOT:** PR302 source arrival 192 CSV SHA-256 `155c70c1c4363d75db46b6898eca6bbf9496bc3cdd586b6cf0994fa2384df6df`; PR303 chemistry 192 CSV SHA-256 `dd0b2ba58effb6ee5929a7091b4b2a91fa172e2d26df7a85dc858ff53f7c1a09`. Original frozen source energies and original species states are unchanged.
- **Future genuine fast-electron collision-data authority:** original author **Curtin CCC** H I `e-H_XSEC_LS.zip` (Aug 2026), He I `e-He_sig.zip` (Apr 2026), He II `e-HeII_XSEC_LS.zip` (May 2026). Primary site https://atom.curtin.edu.au/CCC-WWW/index.html . H I: Bray & Stelbovics, *Phys. Rev. A* 46, 6995 (1992), DOI 10.1103/PhysRevA.46.6995; He I: Fursa & Bray, *Phys. Rev. A* 52, 1279 (1995), DOI 10.1103/PhysRevA.52.1279; He II: linked original DOI 10.1088/0953-4075/26/23/006. **CCC numeric files NOT fetched nor used for this kinematic calculation**.
- **Published-code cross-check, not fast-electron source:** Grackle thermal collisional k1(H I), k3(He I), k5(He II), `grackle-project/grackle/src/clib/rate_functions.c` Git blob `dfbab661e7c45981eed750baebff140849917152`. Grackle, Smith et al. (2017), DOI 10.1093/mnras/stw3291. These are Maxwellian rate coefficients; substituting them as monoenergetic fast-electron cross sections is invalid. NIST SRD 107 DOI 10.18434/T4KK5C is a BEB independent comparison, not CCC identity.

## Constructive, source-owned physical bound

Use immutable 192 arrival bins × 4 first absorbers × 5 original kinetic bands and four target channels = **15,360** physical channel/energy budget records plus **192** arrival summary rows. Every band has original count `N=∫dμ` and kinetic moment `M=∫E_e dμ` (eV/b). The emitted Li II 2E1 paired source E_pair=60.922559447552 eV, so first-photoelectron energy obeys `0≤E_e≤E_pair−χ_absorber`. First absorber thresholds (eV): H I 13.598434599702, He I 24.587389011, He II 54.41776, Li I 5.390 (neutral Li valence, not Li K). Channel energy thresholds (eV): H I n=2 excitation **10.2** (NOT automatically Lyα photon), H I ionization 13.598434599702, He I ionization 24.587389011, He II ionization 54.41776.

For any target threshold θ, put `g(E)=floor(E/θ)`. This gives the *maximal possible number of events if kinetic energy is spent solely in that channel*, not actual electron-collision yield. At fixed N, M and band support, the infimum/supremum of the expected **capacity** follows from two-point measures (moment problem); candidate points are all included endpoints and multiples nθ, using left limits at a threshold for the lower infimum. A band upper end exactly equal to θ is **excluded** for half-open bands [a,b): treating it as included falsely creates He II events in the preceding Li I band. This observed defect was fixed before acceptance.

## New result (original baryon units)

- Photoelectrons `4.374110632809568e-12/b`; original kinetic energy `6.749242464433259e-11 eV/b`.
- Source kinetic potential **H I 10.2-eV excitation capacity** `[3.735822569488451e-12, 5.56303171141713e-12]/b`.
- **H I secondary ionization capacity** `[2.4885343668808715e-12,3.4116837261287396e-12]/b`.
- **He I secondary ionization capacity** `[9.443536642467272e-13,9.443536642926018e-13]/b`.
- **He II secondary ionization capacity** `[6.979531299794241e-26,6.979531299794241e-26]/b`, arising ONLY from rare Li I-first-absorption electrons in E_e ≥54.41776 eV last band. This source-conditioned maximum corresponds to 1.5956458091027218e-14 of all original first electrons; actual yield can be zero. Energetic exclusion is EXACT for H I/He I/He II first absorbers: their E_max are respectively 47.3241, 36.3352, 6.5048 eV.
- The minima above are lower bounds on **kinematic capacity** under unknown spectral distributions, NOT positive lower bounds on actual collisions. Channel maxima are marginal counterfactual budgets and cannot be added.

## Verification, limits and gate

Local original CSV SHA check and 17/17 Python tests PASS including 1600 random source-distribution adversarial counterexamples, exact band boundary/He II rare tail and source count-energy closure. **This is NOT a CCC-calibrated electron cascade or native multi-species collision source**. CCC numerical ZIP datasets remain a useful *future* measurement input, not an unresolved blocker to the present work; no private Langer correspondence needed.

`WORKING_DAG=33/88; CENTRAL_DAG=28/88; F4_FAST_DAG=4/7; CANONICAL_DELTA=0; AUXILIARY=1/1_SCOPED; F4=PARTIAL; L4_READY=false; PRODUCTION=HOLD; NO_MERGE=true; NO_FORCE_PUSH=true; AUTO_NEXT_NODE=false; NEW_IVPS=0`.

Next bounded physics: ingest publicly available original CCC H I/He I/He II cross sections, verify ground-state and excitation/ionization labels, evaluate `ν_s(E,t)=n_s(t)σ_s(E)v_e(E)` and e-e Coulomb electron bath (He III contributes free electrons rather than a bound-electron ionization channel), and propagate source kinetic energy without adding an existing photon RHS.
