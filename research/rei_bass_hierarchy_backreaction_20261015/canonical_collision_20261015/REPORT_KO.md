# REI C5: 조건부 양성 충돌 전이와 partner Q^a ledger

2026-10-15 KST. Source branch: rei_bianchi PR #145, HEAD 54e29dff5a90c0a785cb6dcfb004403614ca403b. This is one bounded next science/code loop. The earlier REI PR #141/#142 already implemented limited near-z4 H/He–Einstein two-way source coupling, and PR #143/#144 already studied UV/HHe Q0,Qz and escaped-photon moment bounds. We do not overwrite or claim to newly invent those results. Original dirty owner checkout, physics checkpoints and native REI production remain unchanged.

## 1. Exact conditional finite collision event

LRS signature (-,+,+,+): ds²=-c²dt²+a²[e^(-2b)(dx²+dy²)+e^(4b)dz²]. s=db/dt, Sigma=√3|s|/H, orientation=sgn(s). Massive sector is original positive canonical Fermi–Dirac cells of PR #145, a fraction fm=.1 of the original nonbaryonic Ωm; no extra mass budget.

For conserved canonical radial momentum node k and angular node j, source particle numbers N_kj>=0, normalized positive Gauss angle weights w_j>0, sum_j w_j=1, define a conditional scalar integrated optical depth tau>=0:

dN_kj/dtau = w_j sum_l N_kl - N_kj,
N_kj(tau)=exp(-tau)N_kj(0)+(1-exp(-tau))w_j sum_l N_kl(0).

The semigroup is exact, preserves each radial particle number and N>=0, with no numerical substepping. Its canonical angular Markov stationary weights w satisfy detailed balance K_jl=w_l; relative entropy D(p||w) decreases, with D(p(tau)||w)<=exp(-tau)D(p(0)||w). This *does not* imply physical thermal detailed balance with baryons, particularly for nonzero b, as discussed for collisional baths by Ehrich et al (2019), https://doi.org/10.1016/j.physa.2019.122108.

The collision is evaluated at a fixed eta=ln(a/aref) and fixed b, with massive cell energy and signed physical longitudinal momentum:
E_kj²=(m/Tref)²+q_k² exp(-2eta)[exp(2b)(1-mu_j²)+exp(-4b)mu_j²],
p_z,kj=q_k exp(-eta-2b) mu_j.

Let F*=rho_crit0*Omega_m fm/a_ref³ in SI J/m³, and norm the source FD initial energy integral. Actual massive collision event impulse:
Delta U_m=(F*exp(-3eta)/norm) sum_kj Delta N_kj E_kj,
Delta P_z,m=(F*exp(-3eta)/(c norm)) sum_kj Delta N_kj p_z,kj.
Gas compensating event variables are Delta U_g=-Delta U_m and Delta P_z,g=-Delta P_z,m, with gas energy AFTER required nonnegative and fail-closed otherwise. This is a checked eventwise source transaction and ledger contract, NOT native fully time-evolved GR four-momentum conservation. Even P2 source gives zero net directed momentum to float tolerance; odd distributions are rejected because the gas Euler/recoil owner is absent.

At b=0 every direction at fixed k has the same mass-shell E, so Delta U_m=0 exactly while the anisotropic scalar Pi_s=(P_parallel-P_perp)/3 decays exp(-tau) for an initial P2. At b != 0 this canonical angular reset generally changes massive kinetic energy; it cannot be applied to a cold gas without paying its energy cost. No physical cross-section, stellar source, collision rate Gamma(a), or HHe material state was invented to make it pass.

## 2. Source-executed experiment and important limitation

Exact PR #145 source history (968 rows), three unchanged source background cases at saved row 60 zbar≈9.24695076596, eta=.71754226264466:
massive_plus b=+5.184984338733324e-5; signed_shear_plus b=+0.004445708971301482; signed_shear_minus b=-0.004342000025740471. At each source geometry tau in {0,.02,.1,.7,3,30}; 18 actually executed collision event transactions. The massive FD source has 32 radial×16 angular canonical cells, third-order positive within-cell Gauss integration, equivalently 96×48 micro-packets; exact PR #145 reference energy normalization.

Maximum tested per-radial-shell number difference 1.3877787807814457e-17, matching opposite partner Q0/Qz impulses and decreasing relative entropy. At tau=.7:

| PR145 source case | b | massive Delta U_m J/m³ | conditional cold gas u_adia J/m³ | minimum energy cost / available |
|---|---:|---:|---:|---:|
| massive_plus | +5.184984e-5 | +4.593090388842181e-16 | 8.81989318482217e-21 | 52076.5 |
| signed_shear_plus | +.004445709 | +3.9210953269655165e-14 | 8.81989318482217e-21 | 4.44574e6 |
| signed_shear_minus | -.004342000 | -3.863343995059382e-14 | 8.81989318482217e-21 | 0; massive component heats gas |

The comparison gas is explicitly the OLD conditional REI original 8.098K z20 source internal energy 3.1885009560495904e-19 J/m³, adiabatically scaled exp(-5eta), NOT the actually heated and reacting gas in C15. Across all 18 test transactions the original conditional cold gas failed the energy-admissibility gate in 10 events; maximum required/available ratio 8.83116878720486e6. This is a scoped counterexample to unbounded stress isotropization at such a weak gas energy reservoir and arbitrary artificial tau, not a universal no-go theorem for matter interactions.

## 3. Implementation/validation/performance

Actual paired_collision.py has an independently implemented positive Markov source, immutable accepted-output arrays, zero-step identity, exact semigroup, radial shell count conservation, strong KL contraction, source kinetic pi_s, plus partner energy and longitudinal momentum. Negative optical depth, negative populations, odd-parity directed momentum, physically insufficient gas energy fail closed. It reuses *original* PR #145 CanonicalMomentumFV and PR137 SourceLock instead of copying scientific constants from results.

17 new tests and 50 inherited PR #145/PR #140/PR #137 tests were re-executed together: 67 PASS. Source three-case 18-event campaign generated COLLISION_EVENTS.csv, RESULTS.json, three PNG science plots, test and benchmark receipt. Vectorized angular generator versus an INDEPENDENT scalar Python row/column implementation (96×48 positive packets, matched outputs) measured 42.285261155339406× faster in 5 repeats, each with matched loop counts. This is generator only, not entire collision event, cosmological ODE, native Rust, or native HHe physics speedup.

## 4. Science claim and next honest step

SCOPED_PASS: positive number-conserving angular Markov semigroup, exact finite-event opposite partner energy/z-momentum book-keeping, entropy monotonicity, f64 source and negative-control tests, physical source-conditioned energy budget counterexample. Normalization is Sigma=|sigma|/H and separate orientation sign.

NOT_ADMITTED: microphysical differential HHe/nonbaryonic massive scattering cross section, physical Maxwellian gas detailed balance, collision-rate history tau(a), actual source gravitating gas Euler+thermal evolution, polarized photon Thomson E/B, C16 full stellar reservoir/escaped recombination Q^a closure, native complete HHe+RT+Einstein production z20→4, observational tau or measured particle mass.

Next source-scoped C6 task: identify actual physically allowed gas–radiation collision channel from BASS/REI source instead of giving generic dark massive particles a guessed baryon cross section. For a sourced channel implement detailed balance in full canonical phase space and a physical gas momentum/thermal Euler partner, then repeat this event conservation check and integrate with the existing PR141/PR142 C15 equations on a fresh state; no old production checkpoint substitution. If no such channel applies, leave massive nonbaryonic Vlasov strictly collisionless and move physical collisions to gamma/electron Thomson or H/He reactive photoionization with source-owned rates.
