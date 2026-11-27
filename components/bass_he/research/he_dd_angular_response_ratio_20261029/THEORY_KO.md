# HE-DD: conditional angular-response ratio bridge

Date 2026-10-29. Parent Draft PR #110 immutable initial HEAD `57d2de80bb192c4358c773cc327b9fad5b1e2ed2`. Parent mathematical source: `research/he_dd_lipschitz_dual_fem_20261029/RESULTS.json`, Git blob `8eec0e162e5ded507a3af1259e60361ed474c376`.

## Precisely scoped mathematical theorem (derived; not detector-calibrated)
For the *already source-conditional* f(theta)>=0 in parent PR110, theta in [0,90] CM degrees, define a probability measure dmu=f(theta)sin(theta)dtheta/D (trig in radians), v(theta)=cos²(theta) in [0,1] and b=E_mu[v]. An *additional* positive angular multiplier q(theta) has 0<q_min<=q(theta)<=q_max and r=q_max/q_min>=1. Define b_q=E_mu[qv]/E_mu[q]. Then

    b/(b+r(1-b)) <= b_q <= r*b/(1-b+r*b).                      (T1)

Proof: A=E[qv] in [q_min*b,q_max*b] and C=E[q(1-v)] in [q_min*(1-b),q_max*(1-b)]. A/(A+C) increases with A and decreases with C; insert the respective endpoints. At b=0,1 the result holds by positivity. For r>=1 both maps are increasing in b, with derivatives r/[b+r(1-b)]² and r/[1-b+rb]². Thus any certified source outer b in [a,u] transports to

    b_q in [ a/(a+r*(1-a)), r*u/(1-u+r*u) ].                  (T2)

T1 is sharp in abstract two-point 0/1-valued v cases; not asserted sharp in parent PR110 cos²(theta) plus Lipschitz f family. At r=1 original b interval is recovered. A uniform displacement bound over b is |b_q-b| <= (sqrt(r)-1)/(sqrt(r)+1), also purely conditional.

## Numeric propagation; delta=5% is a hypothetical input
Only if q is externally assumed in [1-delta,1+delta] up to an arbitrary positive constant, r=(1+delta)/(1-delta). At delta=1/20, r=21/19, the parent GitHub exact Fraction outer endpoints give (display, not outward-rounded certificates):

| L [nb/(sr degree)] | parent source b outer | conditional response-weighted b_q outer |
|---|---|---|
| 1/700 | [0.280076632426714, 0.379702435107293] | [0.260347158423515, 0.403542069694256] |
| 1/200 | [0.185412106807344, 0.469103632064984] | [0.170769305851982, 0.494085357969346] |
| 1/100 | [0.130158754417117, 0.566885072005394] | [0.119240800093185, 0.591274581311069] |

The new `RESULTS.json` contains mathematically exact rational outputs evaluated directly from parent GitHub `RESULTS.json`, not empirical confidence bounds. No new 4501-node LP run. Python targeted 12/12 PASS in current runtime and Wolfram verified monotonicity. No independently authored R6/C9.

## Original experiment and anti-overclaim
IAEA-NDS `exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871` file `exforall/M04/M0475.x4` (Git blob `c49433293921dbb012d7f1b0387745732a598efa`) documents tagged bremsstrahlung photons, liquid-helium cell, two TOF scintillation spectrometers in coincidence, four 330 MeV angular DA rows (M0475002), and separate total SIG rows at 201/225/253/285/320/359 MeV (M0475003). It does not supply an accepted numerical angular efficiency/acceptance, beam-polarization response or clear identical-D event-vs-particle normalization. Arends (1976), Phys. Lett. B62 411-412, DOI 10.1016/0370-2693(76)90671-7, full original article methods not obtained. Silverman (1984), Phys. Rev. C29 35, DOI 10.1103/PhysRevC.29.35, measures inverse dd->alpha gamma at Td_lab=376 MeV, photon CM angles 73,91 degrees, same s as alpha-rest E_gamma ~213.1255 MeV, NOT 330 MeV (inherited PR107 already established this).

**Critical distinction:** q as detector selection makes b_q an observation-weighted moment, not the physical birth angular moment and not Delta² b for deuteron production unless a separate physical response equivalence is established. Conversely, if q is truly a production-law reweighting, it needs physical evidence absent here. If published DA is already efficiency-corrected, applying q as an additional correction would double-count unspecified systematics. Unknown delta cannot be replaced by an illustrative 5%.

Scalar identical-D normalization cancels from b and b_q but remains essential to event cross-section and rate. Physical photon history, helium proper target state, 330 MeV exclusive event sigma, D_fast stopping/deposition and C_V remain source blockers. Preserve `kappa=null; R_event=null; heat_rate=null; physical_activation=false; L4=false; production=HOLD`. Existing central DAG 28/88, HE 14/18, parent FEM 1/2 unchanged; physical completed increment zero.

## Reproducibility and stop condition
Only new simple algebra plus target implementation/tests; old IVPs/full science suite/4501-node LP NOT_RUN. Do not claim full-source ZIP dual byte-restored. Do not promote physical DAG, fit an experimental efficiency from four ERR-S coordinates, or merge/force push. Next physical unit: source-lock original detector efficiency, polarization and identical-D conventions; then same-s inverse measured DA and 330MeV event sigma/flux/stopping.