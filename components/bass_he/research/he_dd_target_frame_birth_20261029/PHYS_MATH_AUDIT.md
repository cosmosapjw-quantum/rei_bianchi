# Single bounded adversarial audit

- **Math:** All-moment identities use two *correlated* daughters per event; the one-D marginal mean does not require a symmetric artificial daughter label. Negative test `mu=1` distinguishes `Var_labelled=0` from pair-centered negative cross moment `-Delta²`.
- **Covariance:** Distinguish true centered labelled covariance `-Delta²(b-a²)` from the cross moment about K0 `-Delta² b`; code returns both. This is necessary under non-even manufactured angular weights.
- **Dimensions:** `M,m,E,q` are energy in MeV; `s,q²,Delta²` are MeV². Proper n_alpha [m^-3], normal n_gamma [m^-3 J^-1 sr^-1], gamma(1-beta dot n) dimensionless, c [m/s], sigma_event [m²], R [m^-3 s^-1]. No MeV-to-J conversion hidden in rate integrals.
- **Frame:** Only kinematic moving-target E'^2 is implemented. It does not transform number-density measures/polarization or run a rate kernel. Formula for local cold-target flux is derived but `NOT_IMPLEMENTED`.
- **Threshold:** E=E_thr allowed with q²=0, pair moment K=0; reciprocal differential formula at q=0 remains invalid and is not evaluated.
- **Physics:** Birth kinetic ≠ heat. Angular shape affects nonlinear stopping. EOS/Cv, nonthermal transport, 330-MeV real photon history and source-qualified total event σ all absent.
- **Numerical:** Fraction exact in algebra; Decimal sqrt 90 digits and C++ decimal100 are finite precision without directed rounding. A plot near E_thr initially failed because rounded binary64 `float(E_thr)` may land below exact threshold; plotted grid now starts 1e-8 MeV above threshold. Neither affects exact source computation.
- **Independent:** Wolfram CAS exact four symbolic residuals zero; an independent C++ implementation compiled after fixing expression-template initializer ambiguity. This is *algorithmic* independence, not native distinct-author R6/C9 approval.
- **Claim:** No strong literature novelty or no-go admission. Math is a reusable kinematic lemma. Real event rate, fitted total SIG and cosmological heating explicitly HELD.
