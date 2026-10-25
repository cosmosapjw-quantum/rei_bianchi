# Independent expanded-programme plan review — numerics authority

Date: 2026-10-25. Reviewer scope: root scope/assembly contract; atomic EXPANDED_NODE_CONTRACTS.json; thermal COMMON_CONTRACT, legacy/current contracts, charters, TASK_ASSIGNMENT and H5 derivation; REI DAG_DELTA; molecular data registry and scientific note. I did not review my own numerics plans as independent authority. No scientific tests, solver run, heavy execution or remote mutation occurred.

Decision at this read: **PASS for expanded ownership/catalog principles and scoped source status; targeted corrections required for specific thermal readiness edges and cross-document ownership wording before authoritative DAG publication.** These findings do not block the separately authorized finite chemistry compiler execution. Its implementation/raw/plot still require its own fresh independent review.

## Passed scope

1. Root makes prospective scope expansion explicit. All configured nuclides (Z,A,isomer), charge states, molecular isotope constituents and source products are covered by process responsibility. The inspected n/H/D/T/He/Li 21-population set is an initial historical view. Atomic target_set_complete=false and molecular candidate/coverage gaps correctly preserve this distinction.
2. Atomic contracts preserve legacy objects and distinguish declared/implemented/executed/admitted/delivered states. PHYS91 exhausted allowance, CR lineage overlap uncertainty and old failures remain visible; no automatic new execution grant.
3. ROOT_SCOPE_AND_ASSEMBLY_CONTRACT separates WU reaction identity/elementary channels, REC spectroscopy/populations/radiation, HE collision moments/thermal closure, CR nonthermal sources/transport, BASS geometry and VigilODE numerics. All-target ambition is not an AND over every provider for a selected physical model.
4. REI DAG_DELTA preserves L0 admitted scope, L1 finite HI children with actual-history open, L2/L3/L4/L5 remaining physical obligations, and GRID044 18/18 instantaneous response with N6 HOLD/no more IVPs. Local child completeness is not global completion.
5. H5 derivation is mathematically constructive: defect/Lipschitz Gronwall bound requires tube closure; endpoint Lipschitz map plus interpolation curvature error; source discrepancy and eta/proper-time conversion explicit. Physical epsilon remains null and execution NOT_RUN. This is useful scientific content for the next source-binding PR.
6. Molecular registry separates paper-cited resources, newer recommendations, discovery-only aggregators and actual downloaded HD fixture. Units, isotope/spin/collider states, finite temperature/support and uncertainty/licence gaps remain explicit. HD arithmetic is a finite reference check, not molecular network admission.
7. Molecular formulae preserve isotope-count conservation for chemical reactions, nuclear-specific conservation for transmutation, Einstein conventions and possible negative net absorption from inversion. Thermal coefficients do not manufacture differential angular kernels. The proposed HD adapter and WU molecular-rate extraction have concrete scientific outputs.

## Findings requiring targeted correction

### P1 — Conditional selected-model dependencies are unconditional in current machine lists

Observed:
- thermal/rec_bianchi_LONGTERM_CONTRACTS.json: REC-COUPLED depends_on REC-HISTORY, REC-LI, REC-FIELD.
- thermal/BASS_HE_LONGTERM_CONTRACTS.json: HE-CLOSURE depends_on HE-ANG, HE-EXCHANGE, HE-RESERVOIR.
- thermal/BASS_HE/.../TASK_ASSIGNMENT.json: HE-EXP-CLOSURE depends_on HE-EXP-PAIR, HE-EXP-STOPPING, HE-RESERVOIR.

Impact: a generic AND interpretation would force Li physics for a selected non-Li model and injection/stopping/anisotropic providers for models that do not activate them, contradicting root's selected-model policy and the charters.

Minimal repair: preserve historical dependency objects; current wrappers list conditional_dependencies with explicit predicates. REC-LI only when Li channels are selected; angular source only when that angular/anisotropic closure is used; nonthermal stopping and external reservoir only when those populations/sources are active. Requirements genuinely needed by every instance remain unconditional. PASS transition is a named selected-model readiness result, not full future-catalog completion.

### P2 — Aggregate-parent completion and downstream consumer readiness can block their own source production

Observed:
- REC-H5-DEFECT-BOUND01 and REC-H6-TRACE depend_on REC-HISTORY, whose remaining obligations include H5/H6.
- Revised HE-EXP-NUCLEAR is WU-led but depends_on HE-EXP-STOPPING; its nuclear daughter source is an input to the downstream stopping task.
- Revised REC-EXP-EXTERNAL is CR-led but depends_on REC-EXP-SPECTRAL; generating an external distribution does not require completed absorber spectroscopy.

Impact: even if the syntactic graph has no explicit reverse edge, completion-based scheduling waits on a parent that the child is supposed to finish or on a consumer that lacks that producer's source.

Minimal repair: type REC-HISTORY as parent/containment, not completion prerequisite. H5/H6 consume exact completed PB01/KS01/source/history identities and actual physical bound/geometry inputs. Nuclear generator depends on species/mass/branch/source input; its stopping consumer conditionally depends on the generator and stopping kernel. External source production depends on declared source spectrum/clock/domain; spectral coupling depends on both source and selected absorber. Preserve aliases and historical records.

### P3 — Role repair must cover prose and machine assignments together

Latest TASK_ASSIGNMENT read already assigns species and nuclear source tasks to WU and external/stopping tasks to CR. Earlier charter read still says HE owns nonthermal evolution/stopping and its REC responsibility table assigns WU level/transition operator and CR radiative cascade broadly.

Impact: implementation may be handed to a different repo depending on whether it reads charter or TASK_ASSIGNMENT.

Minimal repair: apply root's artifact-level split consistently: HE produces differential collision/energy-momentum response and thermalization coefficients; CR owns nonthermal distributions/cascades/stopping evolution; REC owns level populations/spectral emission/absorption/cascade; WU owns elementary reaction identities, state/branch source physics. A single physical channel retains one canonical microscopic event record with explicit consumer links. Recheck only repaired paragraphs and owner fields.

## Small precision corrections

- Atomic CR_HE4_GROUND_RR_CONSUMER_NEXT has specific He4 ground-state outputs but a copied domain string saying “All configured target species”. Replace this node domain with the chosen He4 capturing ion/state, source support, mass/recoil and statistical-weight convention. The repository-wide mandate remains all-target.
- Thermal initial seven-isotope lists should explicitly reference the extensible WU target catalog as a current view, not a future hardcoded ceiling. Nuclear daughters/isomers/anions/molecules must retain arbitrary supplied IDs and explicit missing data.
- Molecular Leiden_photo lists REC cross-section authority while WU owns elementary destruction channels. This can be consistent if REC owns the single ingestion/opacity object and WU consumes its qualified stoichiometry/branch identity; record this artifact distinction before two adapters import and qualify the same source independently.

## Preservation and scope of this review

ROOT_SCOPE requires keeping all40 original nodes,17 cross edges,7 authority objects and31 current returns at central c5050305f84a051cb797cd84c84768c76bcb18b9. REI DAG_DELTA explicitly preserves original contracts/observations. This review assesses that instruction and source plans; the final assembled package was not yet available for a semantic equality/31-return preservation review. Mechanical assembly must retain verbatim source objects with wrapper pointers and use typed external dependencies. Structural validation cannot replace scientific admission.

The copyrighted full Tielens extraction and raw personal/Library metadata must remain outside public payloads. Task-filtered summaries, source identifiers and permitted finite fixtures are the appropriate release objects.

No overall programme percentage is justified. New model/data scope, source availability, actual execution, scientific admission and publication remain separate. Once P1–P3 are repaired in the affected fields, these planning findings close without repeating completed scientific reviews or calculations.

## Targeted repair readback

The thermal author reported repairs during this review. I reread the affected JSON nodes and charter paragraphs.

- **P1 CLOSED:** REC-FIELD, REC-COUPLED and HE-CLOSURE now retain historical_source_dependencies and use explicit selected-model conditional_dependencies. HE-EXP-CLOSURE and REC-EXP-COUPLED use the same principle.
- **P3 CLOSED:** both charters now consistently assign WU elementary identity/branching, REC level populations/spectra, HE differential kernels/thermalization, CR nonthermal evolution/stopping, BASS geometry and REI scenario assembly. External-lead task fields match.
- **P2 PARTLY CLOSED:** REC-EXP-EXTERNAL no longer requires absorber completion to construct a source. REC-H5/H6 still depend on aggregate REC-HISTORY and HE-EXP-NUCLEAR still depends on downstream stopping at this read; these remaining edges need the small supplier/parent corrections described above.

Current decision: planning publication is ready after the remaining P2 edges are corrected; no scientific rerun is required. This does not impede the independent finite chemistry compiler unit.

## Final changed-field decision

The final targeted read confirms **P2 CLOSED**. H5/H6 now use REC-HISTORY as parent_containment, with explicit completed PB01/KS01/original-history input identities and actual bound/geometry inputs still pending. Nuclear production depends on the species/source/mass/branch inputs; downstream stopping conditionally consumes that nuclear producer. External source generation retains only downstream consumer qualification as conditional. The thermal charters also explicitly make seven isotopes an initial view of the extensible WU catalog, closing that precision comment.

**Final independent plan verdict: PASS_SCOPED for reviewed cross-author ownership, catalog semantics, selected-model readiness and scientific next-unit content. P1/P2/P3 material findings are closed.** Existing source/admission/budget states are unchanged. The He4 node domain wording and molecular artifact ownership clarification remain small editorial precision items for their authors; neither is a new scientific obstacle. Final assembled historical-object/31-return preservation remains the mechanical assembler's explicit required check, not a completed check by this reviewer. No rerun or extra review cycle is needed for these closed findings.

