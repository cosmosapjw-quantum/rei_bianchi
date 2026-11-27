# BASS_HE → REI IGM | Original accepted HeII Lyα causal-window absorption *capacity*, not a fabricated RT map
2026-11-02 KST | One bounded R1–R5 theory unit | original source immutable | DRAFT/HOLD

## Physical objective, source and anti-drift
Parent: BASS_HE PR #151 HEAD eed3b50d2985ec4fb562032f9473cf31495d945d (accepted original tick0→160 138,240 HeII Lyα local escape upper-source records). Original REI PR #355 HEAD 70bb906fcfd6b7c5b0f4c356f44c03ad7164ff00, original REI F05 source TAR SHA256 a861278201313c55e08ba6323b5c1d2ad97bf5765f429807b4eba0a1c2465d0b and accepted tick160 array SHA256 cc031a04f5b7b13ccb9ffddf95ec0ced4a9274a9ab999a9e7e3508a5161edb01. REC #195 native source archive ZIP SHA256 ed08c131cb61b8cb5c5a52a8dadeb4fc7350945eefc5c2e1c1bf12c1a2052657 stores actual original accepted REIADP1 at ticks 64/128/160. BASS_HE PR151 escaped source CSV SHA256 13e05ff26adfb8eec5c2e0d0d028a1106f190771c642c2bb4306db79d9a80daf. Other contributions already cover REI #366/#367 source thermochemistry and REC #196 184,320 original events, BASS #328 F08 coupled transport, BASS_CR #164 CaseB reaction budget. Do NOT repeat them.

New targeted scientific result: On *one original accepted F05 time series* quantify whether **source-owned HeII Lyα local escape photon injection can be reabsorbed in the same source-clock causal window**, without inventing a 46k spatial mesh. Compute upper-capacity and a comparison uniform-time emission reference under a **precisely declared source-endpoint frozen homogeneous absorbing-gas assumption**, using actual original HI/HeI numbers and original proper gas volume. Output THREE physical interval records and photon/ionization-energy consequences, not another 46k opacity atlas. The key scientific boundary is whether physical first-collision transfer is already identified by the available REI source geometry.

## Geometry obstruction and what is and is not known
The native F05 TensorizedInputs has state0 H/He populations, proper volume (from comoving W_node), macro_index, node_weight, delta_total, but no source physical coordinate x_i, adjacency, path length or photon direction. W_node ranges about 2.66e-213..0.00934, and macro_index labels 18 macro bins. Treat these as integration nodes / material-phase weights rather than a certified 46,080-cell spatial mesh. An invented cube or equivalent sphere radius from W_node is NOT an authorized photon-flight path. The physical optical depth needs tau[ray]=∫_ray[nHI(x,t) sigmaHI(E)+nHeI(x,t) sigmaHeI(E)] dl. Two geometries with identical source integration nodes/volumes but distinct ray densities can give different tau. Therefore **actual cross-node causal transport cannot be identified** from these inputs. This is a constructive source-data ambiguity (not a novel mathematical-physics no-go theorem).

## Derivation: causal horizon homogeneous reference; never claim actual source transfer
Metric signature (-,+,+,+). Source proper tetrad and proper time t in seconds, c=2.99792458e10 cm/s, energy Eα=40.81332 eV, ε=1.602176634e-12 erg/eV. H I χ=13.598434599702 eV, He I χ=24.587389011 eV, He II χ=54.417760 eV. The original **OTS at 40.8 eV** cross-sections are original reduced RHS constants sigmaHI41=2.884642817876362e-19 cm² and sigmaHeI41=3.0402144676144673e-18 cm². The line may ionize H I and He I but not He II at its birth energy.

At accepted endpoint b∈{64,128,160}, extract original same-source N_HI,j(b), N_HeI,j(b) from pinned private REC195 REIADP1 state; use the midpoint of source interval bounds as **one representative material point**, not a certified correlated-state realization. Use source proper volume V_j(b)=W_node,j Mpc_cm³/(1+z_source)^3 with source forcing z=5.95. Define physical absorption coefficients kappa_H,j=N_HI,j(b)*sigmaHI41/V_j(b), kappa_He,j=N_HeI,j(b)*sigmaHeI41/V_j(b), kappa=kappa_H+kappa_He [cm^-1], lambda=1/kappa [cm] and t_abs=lambda/c [s]. This is a local microphysical scale, NOT a null geodesic.

Let Δt_ab=source_original_duration*(b-a)/131072 s. Every source OTS escaped-line photon emitted at t∈[ta,tb] can travel at most L_max=c Δt_ab in that proper time interval, **only if** we posit a locally homogeneous, static absorber at the endpoint density along its trajectory. Its probability of a first H/He absorption by tb is:
p_j(t)=1-exp(-c kappa_j*(tb-t)).
For any unknown nonnegative temporal source distribution with *original source interval upper count* Nesc,j^+, this conditional frozen-ray model yields
0 ≤ Nabs,j^{frozen} ≤ Nesc,j^+*(1-exp(-tau_j)), tau_j=c kappa_j Δt_ab.
Here the zero is physically genuine because the original local escape branching f includes 1, so escaped emission may be zero. This inequality is a **MODEL-CONDITIONAL CAPACITY** only; the actual IGM ray may traverse denser or emptier gas, so it is not a certified upper bound on actual REI transport.

Species competition in that same frozen-ray model:
N_HI,abs^+ = Nesc^+*(1-exp(-tau))*kappa_H/kappa,
N_HeI,abs^+ = Nesc^+*(1-exp(-tau))*kappa_He/kappa.
Identity Nabs=N_HI,abs+N_HeI,abs and source line electronic energy:
Bpotential^+=ε[χ_H N_HI,abs+χ_HeI N_HeI,abs],
Qelectron^+=ε[(Eα-χ_H)N_HI,abs+(Eα-χ_HeI)N_HeI,abs],
Bpotential^++Qelectron^+=Eα ε Nabs.
These are **potential receptor energy channels**; no receiver cell is specified, and no source chemical/thermal original RHS was modified. Original f absorbed OTS photons are already present in 26-event material reactions and must NOT be counted again as new ionizations.

An explicit optional example, NOT source-owned, is a photon emitted uniformly in [ta,tb] at constant frozen kappa, for which averaged p_uniform=1-(1-e^-tau)/tau, with small-tau expansion tau/2−tau²/6+tau³/24+O(tau⁴). Wolfram symbolic check: zero species-partition residue, zero binding-plus-heat residue, correct tau→0. This is a secondary sensitivity reference, never presented as actual original source photon emission-time law.

## Scientific testing and stop
Read and SHA-verify original REC195 state archive and original PR151 source counts (not alter them). Compute 3 genuine accepted interval source-weighted absorption-time diagnostics on all 46,080 material integration nodes each, but publish only 3 compact interval scientific rows plus weighted λ quantiles, endpoint start/end sensitivity and a source-free independent second calculation. No artificial node positions, no invented path lengths from W_node, no screen/gauge or Bianchi ray metric invented. Do not claim rigorous continuum time-varying opacity or photon transfer. Test kappa≥0, p∈[0,1], atom threshold, dimensional consistency, species splitting, line energy ledger, zero-source and tau limits, and exact source hashes. For source-frozen endpoint reference, monitor different source epochs; where endpoint opacity sensitivity is large report it instead of hiding it.

REI canonical DAG 28/88_REPORTED, working 33/88_REPORTED, Physical Fast 4/7_REPORTED, BASS_HE physical 14/18_REPORTED. Canonical delta 0; no original F05 tick161 admission; production HOLD; no merge or force push; do not loosen original 2e-4 local-error gate. This is a physical *causal-timescale bridge* and constructive geometry blocker classification, NOT a fourth static photoionization opacity atlas. Stop this bounded unit after actual data and verified handoff to central RUX03/RUX04.

Literature: Mellema et al. (2006) C2-Ray doi 10.1016/j.newast.2005.09.004, Friedrich et al. (2012) coupled He OTS doi 10.1111/j.1365-2966.2012.20449.x, Pawlik & Schaye (2011) photon-conserving multifrequency TRAPHIC doi 10.1111/j.1365-2966.2010.18032.x. Source equations and σ are locked to original REI, not the articles.
