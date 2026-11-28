# HE35 preparation: WU088_HH / rec_bianchi latest donor survey

Observation date: 2026-10-22 UTC. This survey obeys the receiving BASS_HE workflow1.0.0 / approval0.2. It performs read-only source/metadata retrieval and byte verification. Scientific suite, IVP, rendering, benchmark and remote mutation counts are all **0**.

## Coverage

The GitHub API branch and all-state pull-request lists were paginated to exhaustion for both repositories. WU088_HH: **145 branches, 136 PRs**; rec_bianchi: **143 branches, 125 PRs**. Every list required two pages; the second page contained fewer than100 entries. All branch names/HEADs and all PR metadata/bodies are preserved in metadata/. This is a complete inventory of these two collections as observed; it is **not a claim to have read every historical file on every branch**.

The33 branch heads not represented by a PR HEAD were additionally read as commit metadata. Their latest date was2026-10-14, so no newer unmatched atomic/thermal successor was found. The focused content corpus covers the two new HH successors, six recent REC thermal/orchestration units, the unchanged PHYS79 provider and relevant handoff/delivery evidence. **49 file readbacks** have exact matching Git blob SHA1 and SHA256/byte-size records in READBACK_MANIFEST.json.

For HH135/136 and REC120–125, issue-comment, review-comment and review collections were fully queried. REC120 has4 issue comments (source freeze, code checkpoint, failed archive recovery and final recovered return); the other23 collections were empty. These are accessible PR conversations. Private ChatGPT conversation histories were not accessible through this assignment and are not claimed as read.

Each of9 selected latest branch tips was refreshed after content retrieval; all matched the pinned readbacks. Older valid HE32/33/34 scientific evidence is reused by the receiving unit and was not replayed.

## Latest source identities and useful scope

| Donor | Latest pin | Reusable substance | Remaining limitation |
|---|---|---|---|
| WU088_HH PR134 PHYS79 | 3304d16db1dc9bf868c185a8eeb6cc9dbc270e50 | Domain-guarded CI and D/H ground-state CX stoichiometry/potential ledger, unchanged source/collisional.py | low-temperature/high-stage CI, He/Li CX, isotope-specific microscopic rates, reactive pressure tensor absent |
| WU088_HH PR135 HH1 | 6c3b12554288893d5d7e221d77be943324285ceb | Conservative C99 PI/RR event-energy adapter and variable-particle-number T chain rule | D potential is modeled H13.6eV +43k_B K; no independently admitted D cross section/rate/capture moment, finite recoil or STF source |
| WU088_HH PR136 PHYS80 | 951182dd59bbb59dba454bbaab78ad56d029355a | Exact isolated22→4 CI/CX and22→1 CX continuous-model reduction, analytic Jacobian, generic log-domain Bell Maxwellian kernel | fixed density/inventory, no expansion or PI/RR; no default H/He/Li Bell coefficient admission, no cooling adapter |
| REC PR120 THERM01 | 7c4af579be508cccf203d3e2a3a5aa16a4b28e38 | Completed thermal34/full63 5–60eV source quadrature and per-baryon gas/ionic/escape ledger; later documentary/recovery closure | differentiated-rate energy moment conditional; Li resonances excluded; source/cosmic energy feedback incomplete |
| REC PR121 thermal moments | 892aad5c3e9fb0b2abd021154b62a42c39277125 | Mao2017 six-row RR energy-loss factors with CDS data/locks, analytic first/second log derivatives for RR/DR, eight completed nativefull63 restarts | Mao-factor hybrid keeps old number rates; common-T isotropic gas, heavy-ion approximation, no nuclear or reactive tensor source |
| REC PR122 omitted budget | 04c0b10c1f1ec38d57c751369c553b638979e453 | Saved-path CI/CE/Compton diagnostic and source-domain distinctions | fixed-path ranking is not coupled physical closure |
| REC PR123 REC1 | 02f3286ee39d99444777ed029844b74bc00cb053 | Saved-history Compton budget and C kernel, separate orchestration component | scalar diagnostic; no baryon tensor or spectrum inference |
| REC PR124 native Compton | e6ecef7624e39bee66b39e09d99fe355f76e2eae | Current-state63D source+analytic Jacobian, eight completed 5–200eV restart IVPs, gas/bath transfer bookkeeping | test-fluid, actual-hot versus external Planck are different models; no Compton photon/Einstein backreaction |
| REC PR125 THERM02 | 407a280aff51abefc10374cb6e21c4224140328c | Source-bound Mao hybrid and Compton scalar contractions, compact34/full63 invariance, eight completed5–60eV z20→2 IVPs | same missing reactive STF/recoil/nuclear sources and spectral feedback; no total closure |

These pins are independent donor lanes. Their original workflow/version and all historical HOLD/production statuses do not automatically change BASS_HE policy or mark BASS_HE B1–B5 complete.

## What changed since HE34 intake

**HH1 now closes the event-local D energy bookkeeping component.** Its C99 function constructs one potential, rejects PI below that modeled threshold, and assigns PI kinetic/binding/radiation changes as (E-I,+I,-E); Case-A RR assigns (-e_capture,-I,+I+e_capture). Source energies and event rates remain caller inputs. It does not make unchanged H rates isotope-correct. Its thermal chain rule accounts for particle creation once; evolving thermal energy already contains that capacity change. The producer records72event+8invalid/domain+27temperature+1cycle cases, all passed, with no ODE. These are reused producer claims, not new survey execution counts.

**The independent RR energy-loss witness now exists.** REC121 imported Mao, Kaastra & Badnell2017, A&A599A10, DOI10.1051/0004-6361/201629708; source fits use T_eV and natural logarithm, with recombining initial charge q=Z-s_recombined+1. The six H/He/Li rows have a selected-file and original-CDS SHA lock. Producer validation covers114published values. Their L_RR=k_B T alpha_parent f_Mao is explicitly a hybrid; source-fit accuracy and hybrid differences are not statistical error bounds. Isotope rows still share electronic factors. The fitted-rate identity L=k_B T(3alpha/2+dalpha/dlnT) is already derived and coded; repeating it would not advance the current missing source bridge.

**Scalar Compton and source contractions are completed donor work.** THERM02 computes U_UV and M_UV once from actualGL4 weights, then an affine source B-Aw from current-state composition/geometry. It evolves5nominal+2tight34+1full63=8new histories; source and geometry couple through T,RR/DR,n_e,opacity and current photon monopole. PR124 is a distinct8-IVP family at a saved z7.9637 restart and5–200eV. Do not merge cohort counts or use either as the missing baryonic pressure-tensor calculation. Their passive bath debits are not evolved radiation energy densities.

**PHYS80 mathematical reductions are narrowly reusable.** Fixed-density thermal+ionic energy permits removing a thermal coordinate, and fixed isotope inventory/shared electronic rates permit exact species reduction. Expansion, different isotope thresholds, nuclear transformations or unclosed sources generally break this particular reduction. The generic Bell kernel accepts explicit coefficients with a provenance label, provides rates/incident-energy moments/log-underflow status, and admits no physical species automatically. H Bell Table5 B1 transcription conflict remains unresolved; near-threshold rates cannot be assigned the polynomial fit's domain/uncertainty by assumption. Incident electron energy in CI is not the net common-pool cooling; the ground-state nonradiative chemical defect is.

## Constructive next BASS_HE scope

The useful new unit is an **explicit reaction moment/energy-owner adapter**, not another scalar thermal or Compton derivation. It can reuse HH1 event accounting, REC thermal normalizations, PHYS79 stoichiometry, and the HE33 tensor convention while adding:

1. One SI contract from per-reference-H and per-conserved-baryon rates to R_part, Q and kinetic second-moment source S_ij, with J=S-(tr S)/3 I. Nucleus-changing processes require R_part=R_nuclei+R_e, not R_e alone.
2. Reaction-based energy ownership that separates nuclear rest/binding changes, ionic potential, kinetic heating/cooling, escaping photons/neutrinos and unresolved stopping. An algebraically closed ledger cannot authorize unavailable physical branching.
3. Explicit source moments for the selected modeled reaction distribution; scalar rates and energies alone do not specify STF moments. Parent anisotropy removal can be nonzero even under isotropic incident photons.
4. A structural isotope-lift test R_full(Lz)=L R_reduced(z), including thermal/source projection. Isotope-specific defects/kinetics and nuclear sources are potential counterexamples, so the nine-fraction lift is conditional.
5. A finite independently checkable source-level control. This can advance B2 without repeating a completed cosmological IVP or pretending B1/B3/B4/B5 are complete.

Finite-mass reaction kinematics, differential/velocity-resolved inputs and a selected closure must be explicit if a tensor model is actually implemented. Provider absence should remain unknown/conditional, with an executable guard.

## Relevant preserved backup facts

PHYS80 PR136 records final ZIP PHYS80_FINAL_20261022_951182dd59bb.zip,1,746,247bytes,SHA256 a4957818f64038bd32548d9ac6fc0557271ab4333f4a3c42b5a802cc11bf3464,Dropbox id:BSpOijBcT10AAAAAAD_i9g,Drive172xnGvjitnsM7f5QiS93xArBdvQHiT3B. Producer reports actual full readbacks on both providers; this survey did not redownload that archive.

THERM01 final archive is REC_REI_THERM01_FINAL_RECOVERED_20261022_5445e15edb1d.zip,12,639,251bytes,SHA2565445e15edb1d580af8b819e8d6a1b73fc2b9958d76bae92967c38ee0763bf0e0,Dropbox id:BSpOijBcT10AAAAAAD_h4A. The producer's Git receipts distinguish actual full Dropbox readback from Drive size/ACK-only. The earlier12,257,739-byte StageC ZIP lacking central directory remains failed evidence; source/payload recovery did not rerun science. This survey read those actual receipts and PR discussion, not a newly performed full restore.

## Files to reuse

READBACK_MANIFEST.json maps every exact source to an absolute local path and Git/SHA256 identity. The HH1 C/h files, PHYS79 collisional.py, REC121 moment/source modules and Mao selected JSON are ready for selected source reuse subject to the receiving unit's explicit assumptions. Their imported dependencies must either be included by exact identity or replaced by a clearly derived small adapter; do not import a large runner only to call a scalar formula.

