# EXFOR11 independent review — preexecution component

**Disposition: the core mathematics and implementation pass static review.** One bounded science campaign is admissible after actual S05 publication and source pinning. Two small wording corrections are required before their respective outputs are sealed. This is the preexecution component of one nonauthor review; actual results, timing, certificates and PNG are still pending.

## Scope and independence

I did not author the new contract, implementation or tests. I read the frozen contract, all new Python sources, the original official EXFOR file, the publication-safe Rice/Arends summary and the inherited Bernstein primitive. I compared literal rows and reviewed proofs and code without importing scientific modules or running science, tests, CAS or plots. The exact inspected file digests are in `PREEXEC_REVIEW.json`. Actual runtime model identity is not observable here and is not asserted.

## Two precise corrections

| ID | Target | Evidence and impact | Minimal repair |
|---|---|---|---|
| REV001 | `scripts/plot_saved.py:35` | The black interval uses outward geometry coefficients and therefore encloses the inner family's range; its endpoints need not be attained. Calling it “inner family range” overstates that result. | Change the caption to “inner family enclosure” before the single plot invocation. |
| REV002 | `CONTRACT.md:62` | Each objective is conditioned on one fixed energy. A common positive factor eta(e) cancels at that energy even if it varies between energies. | State cancellation separately at fixed energy; angle-dependent response or energy-dependent weighting inside an energy-integrated observable does not generally cancel. Correct before the execution pin. |

Neither finding changes the scientific computation. The reviewer has made no implementation or contract edits; repairs belong to the parent scientific authority and designated coding executor.

## Mathematical and implementation findings

The twelve DCS/ERR-S rows match M0475002 exactly. The six M0475003 total-cross-section rows remain separate on a disjoint energy grid. Source bytes are pinned by SHA256, and the parser additionally checks exact literal tables. The model correctly identifies the error boxes as sensitivity windows, nominal angles as record coordinates, reflection-even nonnegative Bernstein coefficients as a sufficient positivity cone, uniform azimuth as declared, and endpoint zero as an extrapolation assumption. The Rice discussion is not promoted to an independently recovered original Arends normalization convention.

The paired Bernstein basis and its normalization are correct, including the undoubled middle basis and removal of the endpoint coefficient. The inherited primitive is in mu and matches the new basis. The separate manufactured-cap control expands in x and supplies a useful independent algebraic check. Cosine evaluation uses the correct phase theta/720. Interval products and outward grid rounding remain conservative.

For nonnegative coefficients, the inner inequalities imply feasibility at the exact nominal cosine, and exact feasibility implies the outer inequalities. A strictly positive lower basis row bounds every coordinate; a positive lower observation excludes the origin. Thus denominators are positive and polytopes compact. Exhaustive exact active-set enumeration includes every vertex; singular systems are skipped without numerical tolerance. The fractional-objective vertex principle follows from denominator-weighted convex combinations. Nonnegative basis integration over inherited inner/outer coincidence sets gives the required ordered geometry coefficients.

The saved certificate reader independently checks all stored inequalities, denominators, inner-to-outer inclusion, geometry ordering and objective witnesses using exact arithmetic. It does not independently certify completeness of the vertex list. Completeness instead rests on the reviewed exhaustive enumeration and known-polytope controls; no second independent optimizer should be claimed. The static enumeration comprises 3,984 candidate inversions, shared over three energy right-hand sides. This count is not a timing measurement.

The wrappers check the exact source/dependency manifest and input hash, bound one contracted science campaign, preserve raw output and record resource use. No execution or published pin was inspected at this phase. Timing, memory, control counts, nonempty/empty outcomes and acceptance values must all be reported from the upcoming actual receipts.

## Requirements for the same review's continuation

Read the actual pinned source identity, primary validation report, saved exact result, resource receipts and raw stdout/stderr; inspect the actual PNG and its input digest. Interpret an empty outer family as incompatibility of this finite family and sensitivity window only. An empty inner family with nonempty outer family does not settle true feasibility. Outer extremizers need not be physically feasible nominal fits; inner witnesses are feasible nominal fits but retain geometry enclosures.

This unit does not close any of the three open physical inputs. Central completion remains 28/88 with HE physical delta zero; global physical completion remains null, L4 false and production NOT_APPROVED. No HARMONIC10 science, tests, CAS, plots or backups were rerun.

## Actual result continuation — same independent review pass

**Result review: PASS; no new defect found.** This adds actual-result evidence to the preceding static review. The figure, CAS response and final metadata remain pending components of this same review. No scientific function, test suite, optimizer or plot was rerun by the reviewer.

Both earlier wording findings are closed. The executed contract explicitly permits cancellation of a common positive factor at each fixed energy, and the plot caption now calls the black interval an inner-family enclosure. The corrected contract and plotter hashes are in the S05 execution pin. All eleven current source/dependency hashes match the pin, START and RESOURCE receipts. The seven new owned pinned files also match the actual S05 publication payload. Stored GitHub ref readback confirms publication commit `fc9fc9c2590ff52af247353c29e04c15162b3ae7`, tree `ca144ebe6c730a52a5e3e9b375916ac65ce019b5`, with force=false. The input file and saved source digest match the official frozen EXFOR digest.

The primary invocation's raw stdout, stderr and JSON report consistently record six named control methods passing, zero control failures/errors, one science campaign and twelve cases. Its independent saved-data reader reports 274 checked vertices: 137 inner and 137 outer. The complete saved certificate is 309,187 bytes, SHA256 `5a13b55d1e8f9a0960cddb7c8c06ae08fcb6212425d71642e41d5a311a9b2243`. Matrices, right sides, vertices, normalization vectors, geometry coefficients and extremizing witnesses are retained as exact fractions. This review relies on the already executed reader and reviewed enumeration; it does not claim a second optimization or completeness computation.

At 330 MeV, three outer families are empty: degree4 with either endpoint choice, and degree8 with endpoint zero. Each of the other nine cases has both a nonempty inner and outer family, so there are no unresolved inner-empty/outer-nonempty cases. FULL is exactly one for every nonempty family; empty families retain null bounds. The surviving 330 MeV degree8 endpoint-free model has approximate outer coincidence enclosures CAPS 0.4646734–0.5698242 and HEMISPHERES 0.8028835–0.8431149. These decimals summarize the saved exact-fraction certificate.

The three exclusions concern the declared finite coefficient cone, endpoint assumption and ERR-S sensitivity windows. They are not a rejection of the experiment, a confidence statement, a theorem about all positive angular functions or a strong no-go. The endpoint choice visibly matters; its extrapolation status must remain explicit in the final result.

The complete bounded subprocess used **2.416516 CPU seconds and 2.4720696399999724 wall seconds**, with peak recorded RSS **17,200 KiB**, exit0, no timeout, no prior attempt and no budget reset. This is below the contracted 60 CPU seconds/180 wall seconds/768 MiB per-process limit. The inner receipt's smaller timing has a different scope; the full receipt includes startup, waited descendants, inner final receipts and shutdown. Outer orchestration metadata serialization is explicitly excluded rather than recursively audited.

The remaining review items are the actual saved-data PNG and its input/resource receipts, the bounded CAS response, and final scoped admission/central metadata. Physical-open count remains three, central28/88 with HE delta0, global physical completion null, L4false and productionNOT_APPROVED.

## Final science continuation — CAS and actual figure

**Final scientific recommendation: PASS_SCOPED — admit the data-conditioned aperture reference.** This is the completion of the same independent nonauthor science review, following source inspection and actual-result inspection. No science, tests, optimizer, CAS or plots were rerun by the reviewer, and no implementation was edited. Final central publication metadata remains a delivery continuation.

The actual Wolfram response is consistent with the submitted `CAS_SUBMITTED.wl`. Its 21 literal zero residuals comprise five degree-elevation identities, eight even-symmetry identities and eight full-integral identities. The eight Boolean checks are True, including endpoint vectors, ratio weighting and derivative identities, a common-factor7 control and both partitions of unity. This is one evaluator call with a20second constraint and8.625second client round trip. Provider CPU remains null. The separate context SERVICE_ERROR does not negate the observed evaluator PASS, and the evaluator is not claimed to establish experimental uncertainty coverage or physical completeness.

I opened and visually inspected the actual PNG. The upper panels display the twelve literal DCS points and ERR-S bars at the correct energies and nominal angles. The lower panels correctly display degree and endpoint variants, saved HEMISPHERES/CAPS enclosures and the three330MeV empty families. The footer accurately calls the bands sensitivity windows, the black intervals inner-family enclosures and endpoint zero an extrapolation assumption. At330MeV, the first and last empty-family annotations touch the panel border; they remain legible and cause no scientific ambiguity. This cosmetic observation does not justify another rendering.

The PNG is SHA256 `ab05f115982d120afb737a01e2716bf3aa4cdf501055d75c5d1916443a5fd664`; SVG is SHA256 `7ed20bb2c8e1ce1eaa0eec033b3a238dc8b5d46a3766f907854c6df4b71b343a`. The plotting receipt consumes the reviewed saved-input hash `5a13b55d1e8f9a0960cddb7c8c06ae08fcb6212425d71642e41d5a311a9b2243`. Plot source and dependency manifests still match the S05 pin. Its single saved-only invocation has zero scientific imports/calls and empty stdout/stderr. Whole subprocess use was2.3532899999999994CPU seconds,2.3739040689979447wall seconds and78,536KiB peak RSS, within10CPU/30wall seconds and768MiB perprocess.

The Korean interpretation faithfully describes the213/258MeV endpoint sensitivity and the330MeV exclusions/surviving family. It preserves the distinction between a finite cone exclusion and a global no-go, between sensitivity windows and confidence, between Rice's documented convention and the unresolved original Arends normalization, and between fixed-energy common scaling and unresolved actual response.

The evidence supports completing one new scoped local node: **11complete+1inherited partial+3physical open/15** after parent admission. It does not increment central physical completion: **28/88, HE delta0**. All thermal/deposition and independent-binding ports remain null, `population_rest_energy_witness` remains the sole binding owner, birth_pool remains UNASSIGNED, global physical completion null, L4false, productionNOT_APPROVED and activationfalse. No strong global no-go is admitted.

No scientific repair is required. The remaining task for this review is final HE-only central metadata/ACK inspection when that candidate is supplied. Completed science, tests, CAS and plots should remain closed.
