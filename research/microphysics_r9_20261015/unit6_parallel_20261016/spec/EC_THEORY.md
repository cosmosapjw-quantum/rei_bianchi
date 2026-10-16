# Unit 6 lane C: charge-resolved Be7 electron-capture bridge

Frozen scope: conservative event maps and prescribed-hazard exposure families using the actual R5 BBN donor. This is a five-state auxiliary Be reservoir attached to the existing 17-state adapter, not completion of native 17-state evolution. No cosmological time history, T4 daughter electronic distribution, plasma rate table or heat deposition history is inferred. Baseline: no spectator shakeoff; a daughter charge state denotes a charge bin, not a proven electronic ground state.

## Actual donor and admission boundary

Read `../REI_R9_NCP_HANDOFF_20261016/unit2/bridge_code/inputs/R5_DONOR_BBN.json` relative to the workspace, using the absolute path in the JSON contract. SHA256 `47f93645a4c4fbcba0a6c3d1a9f8290adf847f011ab04d29b448633ec8525417`. Source commit `4bf97d5082eee54b9df50d88f43182bb651fea80`; name `large_bareBe7_donor_fullcosmology`. Values are number abundances per donor baryon: Be7 = 3.784994236672219e-10, direct Li7 = 2.1819521581308123e-11. The endpoint is t=1315640.6195682916 s, z=4257756.520289892; its overlay removes neutral Be decay and neglects continuum EC. Preserve those facts. Assigning this bare donor to Be4 is consistent with its model; moving it to another charge bin is explicitly a conditional initial-state fixture, not recombination. Keep all other excluded nuclides unchanged and subtract Be7 from the old excluded reservoir exactly once before adding the five auxiliary states.

The earlier bridge's Li assignment is Li1; its other 13 tracked states are spectators. The physical 22-population adapter is 17 existing + Be0..Be4. Its evolving mass-seven subsystem can be represented by nine nuclear populations (Be0..4, Li0..3). Neither adds Li-minus, and neither claims a native Rust change.

## Events derived by electron counting

Write Y for abundances, Z for nuclear charge, q for ionic charge and N=Z-q for bound electrons. Electron capture lowers Z:4→3 and A remains 7.

| Channel | Input | Daughter | Delta free e | Delta bound e | Delta nuclear Z |
|---|---|---|---:|---:|---:|
| bound, q=0..3 | Be^q, N=4-q | Li^q, N'=3-q | 0 | -1 | -1 |
| continuum, q=1..4 | Be^q + free e, N=4-q | Li^(q-1), N'=4-q | -1 | 0 | -1 |

Each event also produces one electron neutrino (possibly a nuclear excited daughter followed by gamma emission). Bound q=4 is forbidden because N=0. Continuum q=0 would give Li-minus with N'=4: explicitly excluded, never silently redirected to Li0. A supplied nonzero continuum q0 hazard must fail with EXCLUDED_CHANNEL, rather than lose events.

For accumulated counts Cb=sum Cb_q and Cc=sum Cc_q, Delta YBe=-(Cb+Cc), Delta YLi=Cb+Cc, Delta nuclear Z=-(Cb+Cc), Delta e_bound=-Cb, Delta e_free=-Cc, Delta ionic charge=-Cc. Therefore baryons, heavy-nucleus count and net electric charge Qnet=sum(qY)-e_free are conserved; electrons themselves are not conserved because one is annihilated per EC. Electron-plus-neutrino lepton number is conserved when the emitted neutrino count is retained. For an initially neutral supported inventory, e_free+e_bound=sum(ZY) remains true. Do not claim sum(ZY) is conserved through weak decay. Full baryon inventory includes unchanged non-Be excluded reservoirs; retain the original normalization defect.

Event update with count c: subtract c from its Be bin, add c to its daughter Li bin and apply the table's electron/count rewards. An arbitrary finite event update is valid iff 0<=c<=available parent and continuum consumption<=available free-electron ledger. Never clip or renormalize a failed update.

## Exact frozen prescribed hazards

Inputs on an interval of duration dt>=0: lambda_b[q] and lambda_c[q] in s^-1, finite nonnegative, lambda_b[4]=lambda_c[0]=0. A continuum hazard may be explicitly supplied or computed from prescribed proper density n_e [m^-3] times kappa_c[q] [m^3/s]. This is a reservoir-driven hazard approximation. It is not a self-consistent closed plasma when n_e changes with the reaction. Report its prescribed n_e separately from the stoichiometric electron ledger. Reject intervals whose event counts exhaust that ledger unless an explicit external electron-supply ledger is modeled; this contract does not model such a supply.

With Lambda_q=lambda_b[q]+lambda_c[q],

    d_q = YBe_q * (-expm1(-Lambda_q*dt))
    YBe_q' = YBe_q-d_q
    Cb_q = d_q*lambda_b[q]/Lambda_q
    Cc_q = d_q*lambda_c[q]/Lambda_q

For Lambda_q=0 define d_q=Cb_q=Cc_q=0 exactly. Deposit Cb_q into Li_q and Cc_q into Li_(q-1). These formulas are exact for frozen prescribed hazards without charge exchange. Compose intervals in order; changing the freeze sequence changes the specified approximation, not the model into a cosmological solution. Dimensionless exposure u=Lambda*dt supports conditional families without fabricated physical time. No finite exposure is exactly complete conversion; u→infinity is an analytic endpoint, not infinity passed to a finite numeric solver.

For y=(Be0..Be4,Li0..Li3)^T define column generator G: G[Be_q,Be_q]=-Lambda_q; G[Li_q,Be_q]+=lambda_b[q]; G[Li_(q-1),Be_q]+=lambda_c[q]. All other entries vanish. Off-diagonal entries are nonnegative, column sums zero; exp(dt G) is positive and column-stochastic. Thus sum Y and 7 sum Y are invariant for this subsystem. Charge and electron accounting require signed event rewards and cannot be inferred from column stochasticity alone. Do not put free electrons into this one-particle Markov generator and claim the same linear closure.

Uniformization: choose nu=max Lambda; if nu=0 identity. Otherwise P=I+G/nu and exp(dt G)=exp(-nu dt) sum_k (nu dt)^k/k! P^k. Exact infinite series conserves populations. For numerical checks use step splitting so nu*dt_step<=10, and a compensated Poisson series whose omitted probability <=1e-14. Finite truncation loses that tail: report it and do not claim machine-exact column sums. The analytic event formula is the production reference and avoids this truncation entirely. Numerical entrywise nonnegativity is accepted down to roundoff tolerance, never silently fixed. Optional ionization/recombination edges need their own rate/energy contracts and are not included here.

If closing n_e=n_b e_free dynamically, continuum rate is kappa_q n_b e_free YBe_q and e_free_dot=-sum_q kappa_q n_b e_free YBe_q. This is nonlinear and the frozen linear formulas are not an exact solution. A future nonlinear solver needs its own positivity/convergence contract. This lane makes no such implementation claim.

## Shakeoff boundary and thermal ledger

For k spectator electrons ejected after bound capture, daughter charge is q+k, Delta bound=-1-k, Delta free=+k. For continuum capture, daughter charge is q-1+k, Delta bound=-k, Delta free=k-1. In both cases Delta ionic charge equals Delta free; nuclear Z drops by one. Allowed k cannot exceed remaining bound electrons, and daughters must fit Li0..3. A real distribution requires a normalized nonnegative kernel K(k, electronic_state, nuclear_branch | parent,captured_state), with column sums one and energies. Missing outcomes must be represented as excluded probability, not renormalized away. This is the unresolved T4 input. The baseline k=0 event bookkeeping can execute independently; it does not predict shakeoff. A same-N overlap alone is not the bound-capture operator: bound EC annihilates an electron and acts between N and N-1 sectors.

Use bare nuclear masses consistently: Q_nuc=(M_Be,nuc-M_Li,nuc+m_e)c^2. Let E_el(Be,i), E_el(Li,f) be electronic energies relative to their respective bare nucleus plus the correct number of free electrons at rest. For an actual transition, Delta E_el=E_el(Li,f)-E_el(Be,i). Energy available to neutrino, recoil, radiation and remaining excitation is Q_nuc-Delta E_el for bound capture, and Q_nuc+K_captured-Delta E_el for continuum capture. Equivalently, for ground states with positive total binding B, it is Q_nuc+B_Li-B_Be (+K_captured). The two electronic energies have different N for bound capture and equal N for continuum; a generic same-charge ionization energy is not their difference.

If using a neutral-atomic Q instead, convert exactly once: Q_atom=Q_nuc+E_el(Be0)-E_el(Li0). Never add neutral binding corrections twice. Excited nuclear branch energies must be assigned either to daughter excitation then its gamma, or to final emitted products, not both. Atomic electronic excitation similarly remains in an explicit reservoir until relaxation; a charge-only endpoint provides no unique value.

Thermal implementation is deliberately blocked pending actual electronic energies and energy partition. Neutrino energy is an escaping ledger, not gas heat; nuclear recoil/gamma deposition requires transport or an explicitly supplied deposition fraction. Captured continuum kinetic energy is removed from the initial thermal electron pool once; do not add it again as fresh heating. For complete bookkeeping from an initial thermal state, Delta U_thermal + Delta E_el + E_neutrino + Delta E_nonthermal = Q_nuc per event, where E_nonthermal includes emitted/stored radiation, unthermalized recoil and nuclear excitation. This equation already accounts for removal of the captured electron's kinetic energy from U_thermal. Merely reducing particle count at fixed T is not energy conservation. This contract returns heat=null with status NEEDS_ENERGY_PARTITION; synthetic energy fixtures test the identity without claiming a physical energy.

## Rates and physical inputs still needed

In a nonrelativistic isolated hydrogenic approximation, |psi_ns(0)|^2=Z^3/(pi*a_mu^3*n^3), Z=4 and a_mu the reduced-mass Bohr radius. Only s orbitals contribute at a point nucleus in that approximation. A conditional rate can be written sum_(branch,orbital,spin) Phi_branch,spin(Q_eff)*occupancy*|psi(0)|^2; Phi has units volume/time and includes the nuclear matrix element, neutrino phase space and spin weights. It is not supplied by hydrogenic wave functions. Multi-electron screening/correlation and hyperfine populations remain external. No neutral half-life is applied across all q. Khatri–Sunyaev's hydrogenic 106.4 day example assumes statistical hyperfine populations and their stated atomic approximations; it is not adopted as a universal input.

Needed for an actual history: Be ionic initial fractions/evolution, charge-specific bound/continuum rates and their electronic/hyperfine state definition, n_e(t), n_b(t), temperatures/radiation field and t(z), daughter electronic/shakeoff kernel, consistent nuclear mass/branch data, electronic energies, and energy deposition/escape treatment. Until then the result is an exact conditional kernel plus actual-donor endpoint family.

## Executable contract and stopping rule

Implement only the JSON contract in task-owned code/tests/evidence paths. Do not change this theory, model, donor or tolerances to repair failures. Under 30 seconds total CPU/wall budget for local validation; standard library plus NumPy/SciPy already available is sufficient, no downloads. Test all eight channels one at a time at unit population to prevent tiny donor values from hiding mistakes, plus actual donor mixtures, forbidden channels, zero hazard and positivity. Require scaled relative conservation <=1e-12 on mass-seven quantities, channel stoichiometry <=5e-14 at unit population, cross-method <=1e-12 with 1e-15 absolute floor on unit fixtures, and donor event accounting <=1e-12 relative with 1e-25 absolute floor. These are scientific numeric checks, not byte checks for generated outputs. Immutable donor SHA must match. PASS means proceed to independent scientific review; any model/input ambiguity or failed numerical invariant returns raw output for one targeted authority review, never an invented rate or relaxed tolerance.

## Optional literature-conditioned clock

For a deliberately prepared Be3 ensemble with statistical hyperfine populations, no ionization/recombination or continuum capture, adopt only the approximate hydrogenic half-life 106.4 days from Khatri–Sunyaev. Then lambda=ln(2)/(106.4*86400) s^-1. At 106.4 and 212.8 elapsed days, surviving Be3 is respectively B/2 and B/4, and Li3 increments are B/2 and 3B/4; existing direct Li remains in Li1. This supplies physical elapsed-time conditional anchors without identifying a cosmological conversion epoch. The literature approximations and frozen prepared charge population are part of the input; this is not a universal half-life or a recombination calculation.

Numerical electron ledgers: retain delta_free=-Cc independently from the absolute background. For a unit background and a 1e-10 donor, subtracting two rounded background values cannot support 1e-12 relative accuracy on the donor signal. Apply donor-relative tolerance to the stored event/delta values; absolute ledger updates use 5e-14*max(1,abs(initial)) tolerance. Check electron availability before subtraction with tolerance 1e-12*max(free_initial,Cc)+1e-25; report any roundoff-level negative without clipping, and reject a larger deficit. Exact physical admissibility remains free_initial>=Cc.
