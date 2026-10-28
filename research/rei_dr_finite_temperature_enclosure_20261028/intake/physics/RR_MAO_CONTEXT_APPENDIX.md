# RR/Mao definitions retained as context, outside the narrowed DR enclosure

This appendix records the actual source definitions inspected during intake. It does not authorize or claim an RR enclosure. All code/data identities and full paths are in `SOURCE_IDENTITIES_AND_QUERY_LEDGER.json`; no function was evaluated for this note.

## RR number rates and derivatives

Native `atomic_network_REI237.py:233–263` and `recombination_moments.py:102–131` use

\[
u=\sqrt{T/T_0},\quad v=\sqrt{T/T_1},\quad z=T_2/T,\quad
b=B+Ce^{-z},\quad
\alpha=10^{-6}\frac{A}{u(1+u)^{1-b}(1+v)^{1+b}}.
\]

Here the 10^-6 factor converts cm³/s to m³/s. Source parameter lexemes are:

| Initial Z:q | A (cm³/s) | B | T0 (K) | T1 (K) | C | T2 (K) | Source-declared support K |
|---|---:|---:|---:|---:|---:|---:|---|
| 1:1 | 7.982e-11 | 0.748 | 3.148 | 703600 | 0 | 0 | 3–10⁹ |
| 2:1 | 3.294e-11 | 0.691 | 15.54 | 36760000 | 0 | 0 | 3–10⁶ |
| 2:2 | 1.891e-10 | 0.7524 | 9.37 | 2774000 | 0 | 0 | 3–10⁹ |
| 3:1 | 8.7e-12 | 0.364 | 147 | 7153000 | 0.1508 | 715400 | 10–10⁷ |
| 3:2 | 9.349e-11 | 0.6916 | 34.7 | 7329000 | 0.0351 | 629300 | 40–4×10⁷ |
| 3:3 | 2.867e-10 | 0.7493 | 21.08 | 6268000 | 0 | 0 | 90–9×10⁷ |

H/He rows cite VF1996_RR; Li rows cite Badnell_RR_20230511. The shared runtime domain remains 100–10⁶ K. `atomic_coefficients_REI237.json:129–217` is the actual data, not a reconstructed coefficient fit.

With D=d/d ln T, define

\[
b_1=Ce^{-z}z,\quad b_2=Ce^{-z}z(z-1),\quad
g_u=\frac{u}{2(1+u)},\quad h_u=\frac{u}{4(1+u)^2},
\]

and analogously g_v,h_v. The helper's logarithmic slope and curvature are

\[
s=-\frac12-(1-b)g_u-(1+b)g_v+b_1[\ln(1+u)-\ln(1+v)],
\]
\[
Ds=-(1-b)h_u-(1+b)h_v+2b_1(g_u-g_v)
+b_2[\ln(1+u)-\ln(1+v)].
\]

It supplies Dalpha=alpha s. Its alternate rate-derivative kinetic closure is

\[
L_{RR,deriv}=k_BT\alpha(3/2+s),\qquad
DL_{RR,deriv}=k_BT\alpha[(1+s)(3/2+s)+Ds].
\]

The Maxwellian energy-moment identity requires a temperature-independent collision kernel. Applying it to an empirical number-rate fit is the source's declared conditional closure; fit accuracy alone supplies no derivative error bound. These are actual helper definitions and explicit source caveats, not a new physics certificate.

## Selected Mao-factor hybrid

`check_thermal_join.py:212–215` constructs `ThermalSources(net, rr_closure="mao2017")`. `thermal_sources.py:22–33,65–85` uses the numerical electron temperature in eV,

\[
t=k_BT/(1\,\mathrm{eV}),\quad x=\ln t,\quad U=a_1e^{-b_1x},\quad V=a_2e^{-b_2x},
\]
\[
f(t)=a_0e^{-b_0x-c_0x^2}\frac{1+V}{1+U},\qquad
Df=f\left[-b_0-2c_0x-\frac{b_2V}{1+V}+\frac{b_1U}{1+U}\right].
\]

The b1/b2 in this formula are Mao fit parameters, unrelated to the RR derivative symbols above. The code uses natural logarithms. Its selected loss is

\[
L_{RR,Mao}=k_BT\alpha_{native}f,\qquad
DL_{RR,Mao}=k_BT[(\alpha_{native}+D\alpha_{native})f+\alpha_{native}Df].
\]

| Initial Z:q | Recombined sequence s | a0 | b0 | c0 | a1 | b1 | a2 | b2 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1:1 | 1 | 8.655 | 0.5432 | 0 | 10.18 | 0.5342 | 0 | 0 |
| 2:1 | 2 | 2.354 | 0.3367 | 0 | 62.8 | 0.8875 | 21.33 | 0.5675 |
| 2:2 | 1 | 17.82 | 0.5398 | 0 | 20.61 | 0.5318 | 0 | 0 |
| 3:1 | 3 | 4.166 | 0.311 | 0.007567 | 65.17 | 0.9634 | 10.19 | 0.7434 |
| 3:2 | 2 | 65.58 | 0.6439 | 0 | 78.78 | 0.6317 | 0 | 0 |
| 3:3 | 1 | 27.33 | 0.5385 | 0 | 31.43 | 0.5309 | 0 | 0 |

The source-selected mapping is q_initial=Z−s_recombined+1. These six coefficient rows were read in both the selected JSON and the frozen original `mao2017_pars.dat` lines 1–3,31–32,60; corresponding `calc.dat` rows were also read. The source-selected fit-deviation percentages and prior numerical comparisons are not physical uncertainty radii and were not reevaluated. `MAO_SOURCE_LOCK.json` pins both full catalog byte streams and selected JSON; their local hashes match the lock.

## Surrounding model differences

`coupled_BASS241.py:49–60` prescribes z=21 exp(−x)−1, Q=(1+tanh((7−z)/0.8))/2, T=100+11900Q K and UV scale Q. Its diagnostics infer the net gas input needed by that prescribed path; they do not supply a separate escape/bath closure. The six-variable chemical polynomial uses this finite model's frozen supplied effective rates, and retains missing rate/clock/geometry/rounding obligations. [Coupled source:121–159; chemical source:97–137]

`pw19_rec_callback.py:62–133` instead replaces the photo coefficients by one saved HeII PW19 source at z=2.479; other native photo routes are off by exclusive selection. PR237's source join uses only thermal electrons n_e=n_b(q·Y−zeta), keeps fast count/kinetic energy separate, and uses prescribed constant-in-energy nu. The source-only join sets pressure-work-related terms to zero. Identical recombination code/data do not erase these differences, identify the two physical state carriers, or qualify nu.

The actual constructor reuses a saved interpolated background; its fast moments are manufactured as zeta=(q·Y)/4 and w_nt=zeta K_photo/Gamma_photo, with nu=8.160348695705333e-18 s^-1. This is explicitly not a source-matched evolved fast-pool history. [Checker:209–246]
