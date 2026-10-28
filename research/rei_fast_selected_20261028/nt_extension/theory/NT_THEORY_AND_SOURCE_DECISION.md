# n/T result, constructive derivation and source decision

The fastest useful result is now an actual recovered conditional n/T history, not a newly fabricated source or a generic response library. `NT_SAVED_PROJECTION_CONTRACT.md` is the execution authority. The earlier constant-source derivation is retained, with its numerical implementation cancelled because the full accepted coupled history already exists.

## What the recovered physics supplies

The source's `NUCLEAR_NETWORK_CONTRACT.json` and `nuclear_network.py` define a two-component fast state `u=(Y_T,Y_n)^T`, with six other isotope reservoirs fixed for coefficients and18 nuclear families. Both n and T start at zero. Thermal DD channels create them with per-baryon event rates `r_DDp=(n_B/2)<sigma v>_DDp Y_D^2` and the analogous DDn expression. The1/2 counts identical-pair events, while deuterium depletion per event is2. Conversion/capture/decay are included. Positive sources and positive recurrence give finite positive log populations after the start, although their linear-scale values may be tiny.

Recovered original primary-source intake qualifies constant zero-energy S inputs50.8keV b (DDp) and51.0keV b (DDn) from Viviani et al., [J. Phys. Conf. Ser.2586 (2023)012076](https://doi.org/10.1088/1742-6596/2586/1/012076). Original SOURCES.md records direct primary-paper retrieval and scope. This is a **conditional constant-S continuation to low thermal energies**, not laboratory validation at100–10000K. The optional DDp source is Li et al., [Phys. Rev. C92,025805](https://arxiv.org/abs/1503.08672); its several-keV data limit does not remove the extrapolation. Those existing rate evaluations are reused, not rerun or refitted.

Canonical thermal neutron-capture inputs are p(n,gamma)0.3326b, D(n,gamma)0.000519b, and He3(n,p)5328b at2200m/s, with1/v continuation. Use5328 from the frozen JENDL5 source; the earlier intake's5327 number is a different input, not an interchangeable rounding repair. Li6(n,alpha)940b is explicitly a dominant-branch approximation. DDn emits energetic neutrons; using these thermal capture coefficients therefore depends on the source's declared instantaneous thermalization. Actual stopping transport remains missing.

The restored decay input fixes tau_n=878.4s (mean lifetime), t_half,T=12.312y with365.24219878days/year. The original atomic donor's12.32 Julian-year convention is retained historically and is not mixed into this result. This is source reuse with its original evaluated uncertainty, not a new lifetime measurement.

## Coupled equation and exact interval solution

With `Y_i=n_i/n_B` and `dot n_B=-3Hn_B`, dilution cancels. Every nuclear event contributes `dot Y=nu*r`, where r is events/baryon/proper-second. Because the frozen registry has at most one n or T among reactants, the fast system is linear:

`du/dt=M(t)u+s(t)`,

`M=[[-a,b],[c,-d]]`, with a,d>0 and b,c>=0.

Here b includes n→T conversions such as He3(n,p)T and D(n,gamma)T; c includes T→n channels such as T(D,n)He4. The diagonal hazards include those conversions and decay/capture losses. Independent source terms include DDp/DDn and admitted reactions among frozen reservoirs. Counting a conversion as both a diagonal loss and an off-diagonal gain gives the correct coupled stoichiometry. The source code explicitly rejects nonlinear fast reactants rather than hiding them in this matrix.

For a frozen interval of width h, with M the midpoint of its endpoint matrices and `s(t)=s0+(t/h)(s1-s0)`, variation of constants gives

`u1=exp(hM)u0+h*phi1(hM)s0+h*phi2(hM)(s1-s0)`,

where `phi1(Z)=sum_(k>=0) Z^k/(k+1)!` and `phi2(Z)=sum_(k>=0) Z^k/(k+2)!`. Equivalently use endpoint weights `W0=h(phi1-phi2)`, `W1=h phi2`. Integral definitions `W0=int_0^h exp(M(h-v))(1-v/h)dv`, `W1=int_0^h exp(M(h-v))(v/h)dv` prove nonnegativity since M is Metzler. Thus u0,s0,s1>=0 imply u1>=0. The existing code evaluates positive weighted terms in log space. Its a*d>b*c check gives both eigenvalues negative and bounded frozen-system relaxation; this is a source-model fact, not a universal nuclear-network theorem.

In the scalar limit `dy/dt=s-k*y`, `y(t)=y0 exp(-kt)+(s/k)(1-exp(-kt))`, and `int y dt=y0(1-exp(-kt))/k+s[t/k-(1-exp(-kt))/k^2]`. This supplies the exact no-source survival and source-fed balance. Wolfram independently returned zero differential/integral/conservation residuals, correct zero-hazard limits and the stable small-x series; intermediate singular-limit warnings are preserved in `SOURCE_AND_SYMBOLIC_EVIDENCE.json`. No new numerical trajectory was calculated.

Propagated stocks and cumulative event counts are distinct numerical reconstructions in the source. Events use positive log-linear flux interpolation in proper time. C9's repaired result makes saved `log_T_n` authoritative for stocks; do not subtract near-cancelling event production/destruction to recreate them. Existing maximum event refinement difference0.00484398118851426dex passed0.02dex, and gross reservoir changes1.4388714811204898e-80 were below1e-6. Reuse those scoped facts without claiming a new convergence run or physical rate accuracy.

## n→p feed, charge states and conserved events

For integrated neutron beta event count `B_n=int lambda_n Y_n dt`, the direct changes are `Delta Y_n=-B_n`, `Delta Y_HII=+B_n`, `Delta Y_e,fast=+B_n`, with anti-neutrino count+B_n. No immediate H I appears. For T I, preserve the original bound electron to obtain He3 II; for T II, obtain He3 III. Later recombination changes ion stage through its own rates. The cumulative plotted beta counts therefore show a **daughter production contribution**, not total daughter abundance.

All-bare DDn has `nu=-2DII+He3III+n`; DDp has `nu=-2DII+TII+HII`; n+p capture has `nu=-n-HII+DII`; He3+n conversion has `nu=-He3III-n+TII+HII`. Each gives A·nu=0 and heavy charge conservation. Beta gives heavy-charge increase1 balanced by the new electron. Assemble these columns in the full17 displayed-state order, retaining hidden Li6 columns when source closure events require them. The symbolic equalities are exact integer identities. Source charge-branch labels remain unresolved for general neutral/partially bound nuclear targets; the bare/spectator examples do not supply missing probabilities.

Energy conservation tracks available nuclear Q/absorbed photon energy once across daughter kinetic/recoil, fast electrons, radiation, neutrinos, ionization/excitation and heat. Counting beta in both the nuclear source and atomic donor decay matrix double counts it; recovered BINDINGS assigns the coupled beta owner to the evaluated nuclear source and omits atomic D. Existing escaping capture photons remain escaping in this conditional source. Plotting events adds no heat/stress/Einstein feedback.

## Production sources, survival and reverse weak processes

[ACROPOLIS](https://arxiv.org/abs/2011.06518), author paper Table1/Section2.2 retrieved through Exa, supplies the relevant primary framework and channel thresholds: D(gamma,n)p approximately2.22MeV, He4(gamma,p)T19.81MeV, He4(gamma,n)He3 20.58MeV, Li7(gamma,alpha)T2.47MeV. The current recovered nuclear source's external photons are5–60eV, so these photodisintegration channels have zero support for that input. This is a statement about its finite source spectrum, not about the universe. Its8 support-zero photo directions are distinct from2 absent inverse-beta bath directions.

Cosmic-ray fragmentation can produce n/T, for example baryon/charge-allowed p+He4→p+He3+n and p+He4→2p+T. An actual source requires incident species, differential intensity/phase-space measure, target density/ion state, energy-dependent cross sections/yields and daughter slowing/escape. A family name or cosmic-ray energy density alone is not an event rate. The existing reserved CR owner work is reused only at its supplied scope; no unspecified flux is invented here.

At a fixed thermal bath, `kcap=sum_j n_j<sigma v>_(n,j)`. Mean time to any loss is1/(lambda_n+kcap); decay/capture probabilities are respectively lambda_n/(lambda_n+kcap) and kcap/(lambda_n+kcap). The environmental ratio kcap/lambda_n, not tau_n alone, decides whether capture wins. For variable conditions, no-source survival is `exp[-int (lambda_n/gamma+kcap+escape)dt]`, with gamma relevant to genuinely relativistic transport. In the thermalized source gamma=1. T's analogous survival uses ln2/t_half. Sustained late populations therefore require sustained source terms under this closure; initial relic abundance is not a constant reservoir of free n/T.

Free-proton electron capture `p+e−→n+nu_e` has the stationary-target kinetic threshold `K_e,thr=[(m_n^2-m_p^2-m_e^2)/(2m_p)-m_e]c^2` (negligible neutrino mass), about0.783MeV including recoil. Inverse beta `anti-nu_e+p→n+e+` has `E_thr=[(m_n+m_e)^2-m_p^2]c^2/(2m_p)`, about1.806MeV; [Strumia & Vissani (2003)](https://arxiv.org/abs/astro-ph/0302055) gives the latter threshold and energy-dependent cross sections. The exact time reverse of three-body neutron beta decay is a three-body absorption process and is not synonymous with either two-body crossing channel. Kinematic accessibility does not establish a practical rate: each needs its actual nonthermal lepton distribution and phase-space integral. Thermal eV gas cannot be assigned a large inverse weak source by reversing an arrow. Absent bath data is recorded as absent/unresolved, not an empirically established zero.

## Scoped decision and three axes

Symmetry/gauge: abundance scalars, same local tetrad/proper-time/source volume; x-time RHS divides by H once; integrated events already carry time integration. Invariants: isotope mass number and electric charge per event, positive linear response, single ownership of decay/electron/energy sources. Observable: recovered same-case Y_T/Y_n and cumulative beta counts, on its actual saved elapsed clock, separate from the17-state atomic baseline.

Decision: reuse complete source, derive the mechanism, project the saved conditional dynamics, and stop optional kernel work. Numerical extraction/render and independent acceptance are separate recorded steps. F4 has concrete conditional n/T evidence and an explicit next dependency: qualified nonthermal source/transport plus charge/energy daughter mapping for physical coupling. F4 physical completion remains open. Original working33/88, central28/88 and mainNO_MORE_IVPs remain unchanged.
