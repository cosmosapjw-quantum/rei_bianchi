# BASS_HE | Original Arends 1976 angular-shape science from measured differential cross sections

2026-10-30. Target: source-owned **normalization-robust** physical angular contrasts and conditional angular-shape tests using the 12 *actual* EXFOR M0475002 DA points. Parent is Draft PR119 (exact head checked at execution time). Original Central 28/88, HE physical 14/18, PR119 angular 2/3 remain unchanged. New *scoped measured-angle scientific unit* has exactly two objectives: (D1) 30 exact measured-point contrasts with source-owned ERR-S boxes, (D2) nine source weighted conditional angular model fits, not a new canonical DAG branch. No old 4501 LP, no IVP, no optimization.

## Exact original physical source and definition

IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871:exforall/M04/M0475.x4, 3349 bytes, SHA256 `b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f`, Git blob `c49433293921dbb012d7f1b0387745732a598efa`. Differential cross section `DATA-CM` [nb/sr_CM] with source `ERR-S` [nb/sr_CM], three laboratory incident photon energies E=[213,258,330] MeV and measured θ_CM=[46,61,73,87] deg, exactly 12 points. Source `M0475003` reported integrated SIG at other energies and **no measured 330 MeV total SIG**. No detector per-angle efficiency, covariance, or source-owned event normalization imported.

For two *measured* cross sections at coordinates a,b, construct dimensionless angular/energy contrast C(a,b)=(σ_b−σ_a)/(σ_b+σ_a). Any common multiplicative unknown normalization factor cancels identically, although angle-dependent detector acceptance does NOT cancel. No extrapolation of angular distribution or interpolation between nuclear energies is used. There are 3×C(4,2)=18 within-energy angle contrasts and 4×C(3,2)=12 fixed-angle energy contrasts: 30 deterministic functions of only 12 source measurements, **not independent measurements**.

## Exact source ERR-S Cartesian boxes and statistical distinction

For reported σ_a±e_a and σ_b±e_b with σ_a−e_a>0 and σ_b−e_b>0, monotonic derivatives ∂C/∂σ_a=−2σ_b/(σ_a+σ_b)^2, ∂C/∂σ_b=+2σ_a/(σ_a+σ_b)^2 give the EXACT extremum of a Cartesian coordinatewise ERR-S box:

C_min=((σ_b−e_b)−(σ_a+e_a))/((σ_b−e_b)+(σ_a+e_a)),
C_max=((σ_b+e_b)−(σ_a−e_a))/((σ_b+e_b)+(σ_a−e_a)).

These are deterministic *source-reported error boxes*, NOT a joint confidence interval and do not include detector normalization/angle systematics. Each endpoint retains exact rational arithmetic from the printed original decimals.

If pointwise error bars are treated as standard deviations and the unknown correlation is ρ∈[−1,1], a **first-order delta-method** standard deviation has lower/upper limits ||u|−|v|| and |u|+|v| with u=(∂C/∂σ_a)e_a,v=(∂C/∂σ_b)e_b; for independent errors the nominal width is sqrt(u²+v²). These are linearized uncertainty bounds, not full likelihood claims.

Source-valued results for θ=46°→87°:

| E_gamma (MeV) | exact C | source ERR-S box [Cmin,Cmax] | source ratios σ87/σ46 |
|---:|---|---|---:|
| 213 | 8/19 = 0.421052632 | [9/35,23/41] | 27/11 = 2.454545 |
| 258 | 17/33 = 0.515151515 | [7/29,27/37] | 25/8 = 3.125 |
| 330 | 5/33 = 0.151515152 | [−3/31,13/35] | 19/14 = 1.357142857 |

The error boxes overlap; no high-significance difference is admitted from these two angles alone. A common detector efficiency uncertainty cancels for ratios, while differing angle efficiencies can still bias contrasts.

## Conditional angular-shape falsifiers, not event normalization

For each E, use the four source cross sections y_i=DA_i and reported ERR-S e_i with diagonal W=diag(1/e_i²) **only as a working independence hypothesis**. Three competing angular bases are:

1. Constant: y(θ)=a_E.
2. Symmetric sin²: y(θ)=a_E sin²θ.
3. Symmetric even quartic: y(θ)=sin²θ[a_E+b_E cos²θ].

Solve (XᵀWX)β=XᵀWy, with χ²=(y−Xβ)ᵀW(y−Xβ), dof=4−dimβ and nominal p=SurvivalFunction[χ²_dof](χ²). For the third basis positive inferred coefficients on θ∈[0,π] satisfy a_E>0 and a_E+b_E>0; no positivity projection was needed. The source contains ONLY forward hemisphere θ=46..87°, so values outside measured support and total integrated σ are hypothetical extrapolations. Photodisintegration into two identical deuterons motivates exchange-symmetric trial bases, but original counting/acceptance must still be source-qualified.

| E_gamma | χ² constant (dof 3) | χ² sin² (dof 3) | χ² even quartic (dof 2) |
|---:|---:|---:|---:|
| 213 MeV | 11.52231749 | 0.87614624 | 0.32177395 |
| 258 MeV | 7.41090363 | 2.16434651 | 1.37746787 |
| 330 MeV | 3.12 | 6.25466946 | 3.44106073 |

Under the diagonal statistical model, 213 MeV constant is disfavored relative to sin² (nominal p_constant 0.0092 vs p_sin² 0.8312), while at 330 MeV constant fits better than sin² in the same one-parameter comparison. The 330-MeV sin² shape still has p≈0.10, so the data DO NOT reject sin² at 5%. This is *hypothesis discrimination at measured coordinates only* and has unquantified angular-acceptance, covariance and model-selection uncertainty. The paper Rice et al. Phys Rev C 61 (2000) 064612 reports a sin² trend at 150–250 MeV, but its actual numeric six-angle tables were not acquired and are not combined or double-counted.

## Independent checks, admission and next physics

Python implements source-identity fail-closed and tests the three exact-rational contrasts; 15/15 targeted tests PASS, compileall PASS, 30 contrast + nine fit records reproduce from raw source. Wolfram independent stateless least-squares check matches all 9 χ² and the exact contrasts/boxes numerically. Distinct-author native R6/C9 **NOT_RUN** (no exposed native delegation). Original input, results, implementation and packaging are separate evidence types.

Central **28/88**, HE physical **14/18**, parent angular **2/3** UNCHANGED, new measured shape micro-objective **2/2 scoped** when source files/tests/outputs actually published; physical delta=0. `kappa=null; R_event=null; heat_rate=null; L4=false; physical_activation=false; production=HOLD`.

The decisive remaining physical issue is original Arends/Rice detector-angle acceptance and exclusive versus inclusive deuteron counting, followed by a real target-rest f_gamma(t,x,E,Ω) and nonthermal D_fast stopping/secondary energy ledger. This shape product cannot by itself unlock production or cosmic rates.
