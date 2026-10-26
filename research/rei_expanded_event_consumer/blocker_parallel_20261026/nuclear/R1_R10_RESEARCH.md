# n/T production, beta daughter feedback, and inverse-beta resolution

2026-10-26; theory author nuclear_blocker26. T=tritium (3H); gas temperature is T_gas. Internal operating skill 1.0.0 and current tiered AGENTS read. Root owns independent admission and publication. Local scientific numerical execution: NOT_RUN. No new IVP or allowance. This report and CONTRACT.md are an additive theory packet, not new DAG nodes.

## Result and claim boundary

The recurring blocker contains two separable problems. Conditional parent-to-daughter transfer is analytically closed for prescribed source, decay and competing loss. Cosmic source amplitudes, charge-state-resolved tritium branches, beta spectra and thermal stopping remain physical inputs. Missing CR amplitudes therefore do not obstruct implementation and independent review of the transfer kernel. They do obstruct its use to predict a cosmic abundance or heating rate. The full existing REI-L2 and CR_BETA_FULL_OWNER gates remain open; no existing canonical node is declared achieved by this author.

A second concrete correction is necessary: a laboratory neutral/molecular tritium half-life is not automatically the rate of a fully stripped triton continuum-beta branch. Bound-state beta produces a bound electron, so the rule 'every tritium beta decay adds one free electron' fails outside a specified continuum branch. The kernel exposes lambda as an explicit input and labels its branch.

## R1 — Fixed problem and invariants

Complete the n→p and T→He3 transfer algebra, source/destruction separation, charge and energy conventions, and an implementable finite map without spending the exhausted/restricted science campaigns. State uses proper seconds and number per fixed Href or comoving counts. For physical densities one must include expansion/transport separately: dn_i/dt+theta*n_i=(S*v)_i, with theta=d ln(volume)/dt, reducing to 3H for an isotropic background. Passing physical densities to the no-expansion map would be a convention error.

Completion for this subproblem is a reproducible exact map and measured-input provenance with explicit remaining physical qualifications. Scientific acceptance follows fresh review. Neither source-row count nor new document count changes central achieved/88.

## R2 — Actual evidence intake

Current root source anchors: H1 PR233 science8219a0205adc5beccbb399c1c67699e1895354a0, metadata833837745c1bfb902f5c09ae00373eaace35038a, central DAG basea5db4bac9dafadae29685bbea3cec7f43ab990b2. authority26 checked WU PR150 HEAD87933da5654bb2e4d93f7de4341df5e0fa0f8716 and CR PR106 HEADb11b2e9255f2b10fb5582376412e045bd1e9151c unchanged. Read local actual WU_PROVIDER_HANDOFF_KO.md and WU_NEXT_SOURCE_INTAKE_KO.md, central REI-L2/WU_NUCLEAR_PARTICLE_OWNERSHIP/CR_BETA_FULL_OWNER entries. WU's recovered nuclear inputs improve source identity but all rate/Q/consumer flags remain false. Reuse their existing integer event-column checks; do not rebuild their 24 columns.

Measured anchors recovered through SciSpace and Exa, with primary-paper locations:

1. Gonzalez et al., UCNtau 2021, PRL127162501, arXiv2106.10375v2, https://arxiv.org/abs/2106.10375v2 ; https://doi.org/10.1103/PhysRevLett.127.162501 . Rest-frame mean lifetime tau_n=877.75 s; statistical uncertainty0.28 s and systematic +0.22/-0.16 s. This is an explicitly pinned experiment, not a claimed latest world average. Its trapping measurement is interpreted as beta lifetime within its stated standard-decay framework. lambda_n=1/tau_n; neutron half-life=tau_n*ln2. Do not apply ln2/tau_n.
2. Lucas/Unterweger, NIST2000, https://nvlpubs.nist.gov/nistpubs/jres/105/4/j54luc2.pdf ; https://doi.org/10.6028/jres.105.043 . Evaluated tritium half-life t_half=4500±8 days, one standard uncertainty, motivated by tritiated-water standards. lambda_T=ln2/(4500*86400 s). This anchors a laboratory evaluation, not a fully stripped plasma branch. No ambiguity from the length of a year is needed.
3. Akulov/Mamyrin2005, https://doi.org/10.1016/j.physletb.2005.01.094 . Primary abstract distinguishes bare-triton continuum-only and bound-state-inclusive half-lives; it supports the charge/branch distinction. Its abstract was retrieved, not its full numerical table. Do not introduce its numerical bare-ion rate without the actual branch-specific source and convention.
4. Vogel/Beacom1999, https://arxiv.org/pdf/hep-ph/9903554 ; https://doi.org/10.1103/PhysRevD.60.053003 . AppendixA EqA2 gives proton-rest-frame antineutrino inverse-beta threshold; angular/recoil cross sections are valid in their stated low-energy domain.
5. Xu et al. NACREII2013, https://doi.org/10.1016/j.nuclphysa.2013.09.007 ; native collaboration reaction list https://www.aanda.org/articles/aa/full_html/2013/01/aa20537-12/T1.html . Explicit D(d,n)He3, D(d,p)T, T(d,n)He4, T(alpha,gamma)Li7 families. WU's already recovered native table rows retain source-domain authority; do not extrapolate to arbitrary cold gas.

SciSpace's first search also returned unrelated alternative lifetime determinations. They were not combined or adopted. Wolfram's semantic context returned generic median isotope lifetimes; those were irrelevant and not used. Measured values above come from primary publications, not Wolfram entity defaults.

## R3 — Claim, source and closure alignment

The following are derived conditions, not cosmic assumptions: parent source s(t)>=0; decay lambda(t)>=0; competing loss kappa(t)>=0; frozen rates for the exact finite-step implementation. lambda=lambda_rest/gamma for a monoenergetic relativistic parent evolved in a lab/cosmological time; a broad CR parent spectrum requires energy-resolved survival or a correctly weighted integral. The laboratory rest lifetime cannot directly multiply a relativistic parent number with gamma silently set1.

For state-dependent rates, event form is dy/dt=S*v(y,t). Nuclear baryon row A*S=0; full signed-charge row q*S=0; lepton row l*S=0 after neutrinos are included. Source injection into an open parcel carries the matching incoming baryon/charge/energy flux. A positive parent source alone is not a closed-universe baryon creation term.

## R4 — Production/destruction representation and discriminant

Separate relic homogeneous solution from later source-driven solution rather than assuming survival decides production:

P(t)=P(t0)*exp[-integral(t0,t) k(u)du] + integral(t0,t) s(u)*exp[-integral(u,t)k(v)dv]du, k=lambda+kappa.

This is useful because the first term can vanish while the second remains finite. With constant lambda>0, kappa>=0, s<=s_max, P(t)<=P0*exp[-lambda*dt]+s_max*(1-exp[-lambda*dt])/lambda. With no later source, an interval of 1000 half-lives gives survival2^-1000<10^-300. This inequality says nothing about a freshly produced stellar/CR population. A numerical relic bound in the REI epoch still requires its start time and parent distribution; do not create an initial abundance from decay algebra.

Physical source/loss families and current usable scope:

| Family | Number effect | Actual status/next input |
|---|---|---|
| D+D→T+p; D+D→He3+n | Creates T or n, consumes two D | NACREII family verified; WU native rates require appropriate thermal domain and densities |
| T+D→He4+n; T+alpha→Li7+gamma | Destroys T; first creates n | Source families present; no cold-gas constant-S extrapolation |
| D+gamma→p+n | Creates n | WU target8 exclusive ENDF channel exists; photon spectrum fold missing |
| He4+gamma→He3+n / T+p | Creates n or T | WU response-averaged measurements cannot become monoenergetic cross sections without response mapping |
| Li7+gamma→T+alpha | Creates T | WU inclusive yield does not yet establish this exclusive branch |
| n+p→D+gamma or other capture | Removes free n | Needs target-density-weighted qualified capture rate; not beta daughter p |
| CR fragmentation/secondary reactions | Source and destruction may both occur | Parent flux, target composition, exclusive yields, energy/domain, propagation and normalization required |
| Weak p↔n channels | See R5 channel table | Requires actual electron/positron/neutrino distributions; generic CR label is insufficient |

For an isotropic CR number density spectrum f_a(E) [volume^-1 energy^-1], event rate density r_ab=n_b*integral f_a(E)*v_rel(E)*sigma_ab(E)dE. For a differential intensity J_a [area^-1 time^-1 sr^-1 energy^-1], the corresponding isotropic expression is r_ab=4pi*n_b*integral J_a(E)*sigma_ab(E)dE when target/kinematic assumptions support it. Mixing these two normalizations loses v or4pi. Source perHref is s_i=sum_r nu^+_ir*r_r/nHref; losses depend on consumed-parent rates. No missing flux is set to zero.

## R5 — Constructive solution, stoichiometry, Jacobian and energy

With constant s,k over duration h, integrating the R4 expression yields E=exp(-kh), A=(1-E)/k, C=(h-A)/k. P1=E*P0+A*s, integrated parent I=A*P0+C*s. Beta events B=lambda*I; competing-loss events R=kappa*I. Since kI=P0+sh-P1, P1+B+R=P0+sh exactly. k→0 gives A=h,C=h²/2. Positivity follows directly from their nonnegative integral representations; no numerical clipping is needed.

For (P1,I,B,R) versus (P0,s), the exact frozen-input Jacobian is [[E,A],[A,C],[lambda*A,lambda*C],[kappa*A,kappa*C]]. Full-state beta RHS Jacobian is S*diag(lambda_r)*parent-selector. If s/lambda/kappa depend on state, add their chain-rule terms; the frozen map is an exponential subflow, not the exact nonlinear coupled solve.

Continuum beta columns in (n,p,T,He3,e_minus,antinue) are (-1,+1,0,0,+1,+1) and (0,0,-1,+1,+1,+1). The bare-charge row (0,1,1,2,-1,0), baryon row(1,1,3,3,0,0), lepton row(0,0,0,0,1,-1) annihilate both. For neutral atomic T retaining its spectator, daughter He3+ has charge+1. For bare continuum T+, daughter He3++ has charge+2. For bare bound-state beta T+→He3+ + antinue, there is no free beta electron. Thus number transfer to isotope He3 is simpler than plasma electron/charge-state feedback; branches with extra shake-off must carry their own event columns.

For bare continuum neutron Q_n=(m_n-m_p-m_e)c²; for bare continuum triton Q_T=(M_T^nuc-M_He3^nuc-m_e)c². Atomic masses obey M_atom=M_nuc+Z*m_e-B_e/c², hence Q_T,bare=Q_T,atomic+B_T-B_He3. The energy for neutral T→He3+ + free electron also differs from neutral-atom mass difference by daughter ionization/excitation. A frozen energy branch must use the actual initial/final ionic states; no numerical Q has been admitted here.

In the parent rest frame, each continuum beta event obeys Q=K_e+K_daughter+E_antinue+E_excitation+radiation (with excitation/radiation terms not double counted). The emitted electron is initially nonthermal. The thermal fraction is a later stopping/transport output, not Q. In a boosted parent frame transform the full daughter/electron/neutrino four-momenta and include incoming parent kinetic energy; Q alone is not total lab energy. Unit event energy vector epsilon can be multiplied by B once branch-resolved moments are qualified. The energy derivative is then epsilon times the B Jacobian; no spectrum or epsilon is invented by the count map.

Actual weak channels are distinct:

| Channel | Physical process | Proton-rest-target threshold or convention |
|---|---|---|
| n→p+e−+antinue | Ordinary beta decay | Q_n>0; rest-frame lifetime |
| antinue+p→n+e+ | Antineutrino inverse beta | E_nu,thr=[(m_n+m_e)^2-m_p²]c²/(2m_p), about1.806MeV (Vogel/BeacomA2) |
| e−+p→n+nue | Continuum electron capture | E_e,total,thr=[m_n²-m_p²-m_e²]c²/(2m_p); kinetic threshold is this minus m_e*c² |
| nue+n→p+e− | Neutrino capture | Different neutrino species and target; do not use antineutrino-proton source |
| e++n→p+antinue | Positron capture | Different charged lepton; requires positron population |
| p+e−+antinue→n | Exact time reverse of three-body decay | Three incoming particles; not the usual two-body inverse-beta channel |

Threshold derivation uses invariant squared center-of-mass energy s=m_target²*c⁴+m_projectile²*c⁴+2*m_target*c²*E_projectile and final invariant threshold. Electron capture's final massless neutrino approaches zero energy at threshold; above threshold its cross section and phase-space distribution are still required. None of these thresholds supplies a CR or neutrino flux.

## R6 — Verification actually performed and independent review boundary

Wolfram Language evaluated symbolic conservation, ODE substitution and integral derivative; outputs were {0,0,0}. It returned limits A→h,C→h²/2 and parent derivatives E,lambda*A,kappa*A. Intermediate 1/0/indeterminate warnings occurred in Limit evaluation, so they are retained in TOOL_EVIDENCE.md and not reported as a clean warning-free run. A separate bounded Series evaluation returned the expected regular expansions and exact baryon/charge/lepton products{0,0} each without warning. This targeted check addresses the removable-singularity route; it does not rerun a cosmological solution.

Fresh review26 must examine the physical branch/clock/mass convention and implementation evidence. Author tool checks are not self-admission. No new strong no-go is proposed; lack of a source is an input dependency, not a theorem of physical absence.

## R7 — Discriminating execution

Exact Wolfram checks are completed and are independent external symbolic-service evidence; their unreported provider CPU/money is UNKNOWN_NOT_ZERO and they do not reset or transfer either local campaign allowance. Local scientific code execution by this author is0. Root-controlled lower-tier tests are specified in CONTRACT.md; implementation26 has received it. New tests check source-generated parents even from P0=0, competing loss versus beta daughter accounting, stable zero/stiff limits, composition and analytic Jacobian. These tests discriminate the real failure modes without a new IVP. Actual execution status and measured local debit must come from root/implementation receipts.

## R8 — Provisional scope decision for independent reviewer

Derived and tool-checked: exact prescribed-source transfer, conservative continuum stoichiometry, Jacobian, finite survival/source bound, inverse-channel threshold distinction. Literature-supported inputs: pinned neutron mean lifetime and neutral/molecular tritium half-life convention. Implementation admission: pending independent review/execution receipt. Physical count use of free-neutron beta can be qualified separately after normal-frame clock/parent-distribution/consumer binding. Physical tritium electron feedback additionally requires charge-state and continuum/bound branching. Full REI-L2 energy/stopping and CR_BETA_FULL_OWNER remain OPEN_PHYSICAL_INPUTS. Cosmic evolution/late stellar abundance is not computed.

## R9 — Frozen handoff

CONTRACT.md is executable guidance for lower-tier implementation. It defines scalar API inputs/outputs, stable phi evaluation, exact Jacobian scope, concrete finite tests, 5e-13 implementation residual, allowed paths, zero empirical defaults, and root GO before runtime. After PASS and fresh scoped acceptance, the next executable action is to bind a named neutron count consumer with an explicit rest-frame/boosted clock. Tritium and energy branches can advance with their own qualified inputs; they do not recursively block the independent count kernel.

## R10 — Resume and canonical progress

Preserve this report, CONTRACT.md, and TOOL_EVIDENCE.md. Next actual obligations: (1) lower-tier source/tests and root-budgeted raw outcomes; (2) independent review; (3) select and qualify the physical parent/charge-state branch, lab/normal clock and initial/source populations; (4) obtain evaluated beta spectrum and daughter/neutrino/recoil ownership for full energy ledger; (5) CR/stellar amplitudes require source spectra, target densities, cross sections and propagation. Use current WU source rows without rerunning their completed compiler. Central DAG denominator remains88; this author adds0 achieved canonical nodes. Root authority26/review26 decides any existing-node status change from actual acceptance, not number of artifacts.

## Source-completion note: neutron bound beta

The continuum-branch restriction also applies to neutrons. Faber et al., PRC80,035503(2009), https://doi.org/10.1103/PhysRevC.80.035503 ; https://arxiv.org/abs/0906.0959, analyzes both continuum and bound-state n→H+antinue decay. Its primary abstract was retrieved by Exa. Therefore the UCNtau mean disappearance lifetime is an actual measured anchor but does not alone qualify an exact free-electron yield of one per disappearance. A declared continuum approximation may be scoped according to the consumer accuracy; an exact branch-resolved model requires lambda_c/lambda_b. With k=lambda_c+lambda_b+kappa_other, events B_j=lambda_j*I share the same exact parent integral. The existing scalar interface remains unchanged (lambda=lambda_c, kappa=lambda_b+kappa_other); additional product columns are separate. Theoretical historical branching ratios were not adopted as empirical inputs. Nuclear-isotope hydrogen production is distinct from free-proton injection. This qualification narrows only the physical rate/yield binding, not the proven transfer map or its tests.
