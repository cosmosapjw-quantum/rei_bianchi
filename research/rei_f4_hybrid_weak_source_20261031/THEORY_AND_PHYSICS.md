# REI F4 | Frozen full-21 common-electron source replacement and weak-inflow preservation (2026-10-31)

Parent REI Draft PR #296 exact HEAD `b89069aae6866d58f63822d072f98cf424ec5370`; source owner archive is PR #295 exact 25,577,615-byte ZIP SHA256 `156cad079282f8418530d1b38af8a4cc44e0a8711ed9c9e23367fff4db3fb7e9`. Original BASS AtomicNetwork owner commit `cc602e209e7deeb511ab2a1f3b2268d55206c43c`. PR #297 `0f41c8f0d3ddc7f8af67765f09cd37ae885768bf` is an **unmodified sibling** with already computed Li II causal 2E1 H/He source. No 2E1 source is added here.

On **193 original archived** BASS21 states Y=n_species/n_b, frozen T, n_b, UV, original H(t), original BASS full-21 `F_B,J_B`, and inherited REI source-translated H/He five-row `F_R,J_R` at shared electron `n_e=n_b q·Y` (not native full REI17), define the insertion U for (H1I,H1II,He4I,He4II,He4III).

```
F_naive  = F_B + U (F_R - U^T F_B)
J_naive  = J_B + U (J_R - U^T J_B)
F_hybrid = F_naive + e_H1II lambda_n Y_n
J_hybrid = J_naive + lambda_n e_H1II e_n^T
lambda_n = 1/(878.4 seconds)
```

The preserved original BASS neutron beta reaction is `n -> H1II + e + anti-neutrino` (original source-model weak_decay record). All saved 193 points have `Y_n=0`, **but the off-manifold Jacobian `∂F_H1II/∂Y_n=lambda_n` is nonzero**. Blind replacement deletes this and leaves the neutron sink: `max |A^T J_naive|=1.138433515482696e-3 s^-1` (actual strong counterexample). Preserving the weak inflow yields `max |A^T J_hybrid|=1.6543612497579586e-24 s^-1` and `max |A^T F_hybrid|=4.930380657631324e-32 /baryon/s`. Other 16 BASS rows and tritium beta transitions remain untouched.

Cross-owner electron derivative is rank-one for charged isotopes outside HHe: `J_R[:,j]/q_j=n_b(M_R X)`. Source REI common `F` direct reconstruction max difference `7.395570986446986e-32 /baryon/s`. The 193×21 F and 193×21×21 J matrices contain **4,053 and 85,113 physical point entries**, with max rate replacement `4.961566427478634e-17 /baryon/s` and max J replacement `1.4706069707402491e-15 s^-1` after weak restoration.

A second controlled source evaluation applies REI HHe thermal kinetic/CI/RR/DR/CMB formula to original shared BASS electron bath. It is explicitly **translated HHe partial RHS**, not native full REI17 or all-isotope thermodynamics: max full-versus-local `|Delta Q_micro|=1.153561148030574e-36 erg cm^-3 s^-1`; diagnostic ideal 21-state capacity ratio Cv21/Cv_HHe is [1.000031759547062,1.0000356602346778]. Saved H and clock used; inherited `K_trace=-3H` is only a convention-based axisym proxy, not dynamical BASS K. The BASS vs REI photo-threshold signed frozen energy-exposure defect is `-1.7857619737074874e-14 erg/Href`, not gas heating.

The signed source exposure `0.22141551605625187` electron/baryon integrated on the frozen background is **NOT** an evolved Delta x_e, optical depth or observable. Secondary-electron deposition, true Li 1s singlet branching, full native REI17 F/J and common IC/background/radiation are still unbound. This is scientific auxiliary 1/1_SCOPED only, **Working 33/88, Central 28/88, Physical Fast 4/7, canonical delta=0, F4 PARTIAL, L4=false, PRODUCTION HOLD**.

Verification in the source-inclusive master ZIP: clean restore manifest **44/44**, 15/15 targeted tests, 9/9 deterministic outputs; original source archive SHA exact. A deliberate finite-difference tiny-rate relative-error failure (z=20 tiny J) is documented in the same-author adversarial audit and corrected with separate analytic original BASS+REI J construction at all 193 epochs, not by silently relaxing physical tolerance. Distinct-author R6/C9=NOT_RUN; native subagent=NOT_RUN; no new IVP, merge or force push.

Master original 26,674,534-byte source ZIP SHA-256 `012635501cc5d9717ae775e9482b351b239003aa6c7db4dd2035ffa4760b7f2d` is a local sandbox artifact; cloud upload acknowledgement is presently BLOCKED by `container_session_expired` and is **not** asserted. Full code, source package, 193×21×21 NPZ, 193-row CSV and six real PNG plots are inside this master.
