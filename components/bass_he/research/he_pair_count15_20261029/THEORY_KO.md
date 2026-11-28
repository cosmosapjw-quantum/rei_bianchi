# BASS_HE PAIR-COUNT15: signed daughter covariance versus event-count fluctuations

## Pinned source and domain

Owner reference: BASS_HE `de6bcbd95d25f9686997ad7eadbd62ea4e917d59`, predecessor `HE-BIRTH-MOMENT15`, 15 saved rows from 5 samples × 3 aperture families, source JSON SHA256 `1fb9f1479863ecffd072a4b7c762de8d5c8e80b18d6571dfb417d42c945e5264`, source Git blob `c9f7c088096fe54f9adbd31f3969a5959530b554`. All source angular references are conditional on target-at-rest, incident 330 MeV and a fixed even nonnegative sextic angular family; neither new event normalization nor an actual D bath is provided. Old EXFOR/geometry/vertex campaigns have not been run again.

## Derivation

Set A=3727.3794118 MeV, M=1875.61294500 MeV, e=330 MeV, s=A²+2Ae, K0=(A+e)/2−M=153.0767609 MeV, B²=e²(s/4−M²)/s>0. For the two daughters from one event K±=K0±Bμ with symmetric angular μ. Their per-event mean is (K0,K0) and covariance Σ=v[[1,-1],[-1,1]], where v=B² E[μ²]. Pair total kinetic is exactly 2K0=e+A−2M=306.1535218 MeV, hence conditional event-pair total variance zero. Exact K0²>B² ensures positive single-deuteron kinetic energy for physical μ.

Reuse FULL fixed-witness E[μ²]=24377/71485 and exact v=62574503954512379344012665/48306809029441085611817 MeV², approximately1295.355773062462 MeV²; no new integration was run to reconstruct these numbers. Remaining 14 row intervals are read only when the exact pinned source file is supplied and SHA-confirmed.

For an event count N independent of iid identically distributed pair marks Y_i, lambda=E[N]≥0, nu=Var(N)≥0, and total S=Σ_i Y_i, the law of total covariance gives
```
E[S] = lambda (K0,K0)
Cov(S) = lambda*v [[1,-1],[-1,1]] + nu*K0^2 [[1,1],[1,1]]
eigenvalues = 2*lambda*v and 2*nu*K0^2
Var(S_+ + S_-) = 4*nu*K0^2
Var(S_+ - S_-) = 4*lambda*v
```
For N fixed, nu=0 and the cross covariance is −lambda v. For N Poisson with mean lambda, nu=lambda and the cross covariance is lambda(K0²−v)>0. This sign reversal is NOT a physical Poisson assertion: no observed event-count law is supplied.

For Fano F=nu/lambda, the off-diagonal sign changes at F*=v/K0², which is 0.0552803185541635 for the saved FULL witness; a uniform upper bound is B²/K0²=0.1621082812423341. For existing intervals v∈[lo,hi], diagonal covariance lies in [nu*K0²+lambda*lo,nu*K0²+lambda*hi] and off-diagonal in [nu*K0²−lambda*hi,nu*K0²−lambda*lo].

## Physics interface and gates

Event normalization must distinguish exclusive event rate from inclusive daughter counts. If and only if an actual qualified exclusive R_event [m^-3 s^-1] is provided, daughter birth number source=2R_event and kinetic source=2R_event*K0*(MeV in J), with separate photon and rest/binding owners. The birth kinetic energy is **not** automatically thermal heat. Source rate, photon flux/history, named physical D pool, charge/birth electronic state, heating/Gamma_thermal/Cv, and independent_binding_RHS remain null; activation=false, L4=false, production=HOLD, global physical completion=null.

The diagram is a saved mathematical Fano illustration; exact-symbolic Wolfram check returned six literal zero identities, and isolated Python Fraction tests 19/19 PASS. Native distinct-author reviewer unavailable; R6/C9 scientific independent admission HOLD. Owner local scientific DAG14/18, central DAG28/88 delta0.

Source caution: Rice et al PRC61 064612 (2000) DOI 10.1103/PhysRevC.61.064612 measured 150–250MeV and is NOT a normalization at 330MeV. IAEA EXFOR M0475002 DCS cannot be silently multiplied by a different-energy M0475003 total cross section.
