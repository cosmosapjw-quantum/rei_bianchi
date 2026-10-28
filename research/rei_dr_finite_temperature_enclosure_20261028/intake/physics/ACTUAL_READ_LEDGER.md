# Actual-read ledger: refreshed native thermal/rate intake

Date 2026-10-28. Task `/root/finite_thermal_blind_reviewer`, reused as a collaborative source/physics intake role. This is not a blind audit or a completion decision. Shared files and parent messages are observable; no hidden runtime identity is inferred. The instruction model label is GPT-6 Astra Pro, with no independently exposed backend label.

Base directory: `/workspace/scratch/cc0531120bc9/rei_approved_continuation_20261028/survey/physics/`.

## 1. Exact-source reads

All listed source bodies were retrieved through the GitHub read connector at explicit commit refs. Full query arguments, original tool returns, metadata and errors are preserved in `raw/` and `SOURCE_IDENTITIES_AND_QUERY_LEDGER.json`. `SOURCE_SHA256SUMS.txt` records local-byte hashes. Hashing, filename/line searches, JSON metadata selection and artifact writing were filesystem work only; no science module was imported or run.

| Local source copy | Actual semantic read scope | Role / omission |
|---|---|---|
| `source/atomic_network_REI237.py` | Full 1–308 | Native constructor, preparation, number-rate functions and abundance Jacobian; only rates are selected for the new scalar-functional question. |
| `source/atomic_network_BASS241.py` | Full 1–308 | Same blob and local SHA256 as REI copy; confirms shared functional source. |
| `source/atomic_coefficients_REI237.json` | Full 1–288 | All six RR rows, all three signed DR rows, supports, units, runtime domain and omitted-process statement. |
| `source/atomic_coefficients_BASS241.json` | Full content compared to REI copy; identical 1–288 | First read returned RemoteProtocolError; one read-only retry succeeded. Both raw outcomes are retained. |
| `source/atomic_model_BASS241.json` | Full 1–86 | Inventory, state convention, source field and excluded processes. |
| `source/atomic_model_REI237.json` | Full content compared to BASS copy; identical 1–86 | Does not mean the later saved PR237 background is the same state as the BASS initial inventory. |
| `source/recombination_moments.py` | Full 1–153; 122–153 reread with line numbers | Actual RR derivative helper and signed DR rate/loss/JVP, structural/present-zero masks; source comments explicitly qualify the empirical-fit moment closure. |
| `source/thermal_sources.py` | Full 1–118 | Mao fit function, helper constructor/data locks, RR replacement and unchanged DR coefficients. Its prompt-thermalizer `evaluate` is read for ownership context, not proposed for execution. |
| `source/pw19_rec_callback.py` | Full 1–180 | Native subclass, pinned photo moments, exclusive route and no primary-heat identification. Its spectrum and moments files were not newly retrieved, because the narrowed DR functions do not depend on them. |
| `source/check_thermal_join.py` | 1–180 and 205–246; additional isolated `rg` hits at named functions/calls through 521 | Constructor and actual source-state preparation read. Full 522-line body is saved, but unshown test/control regions were not independently examined or admitted. No test was run. |
| `source/CALLBACK_PR237_BACKGROUND.json` | The complete `/snapshot` object, original lines 3–230; top-level key names inspected | Original saved temperatures, native Y, density, geometry and interpolation provenance. Other numerical result objects at 231–1761 were not assessed; full bytes are saved. |
| `source/chemical_polynomial.py` | Full 1–318 | Actual six-variable polynomial construction and explicit external-rate/clock/geometry/rounding scope. No prior-matrix helper imports or executions. |
| `source/coupled_BASS241.py` | Full 1–255 | Actual prescribed thermal/UV path, proper-time clock conversion and required-energy diagnostic. Its BDF/run code was read only. |
| `source/compact_system_BASS241.py` | Full 1–111 | Constant coordinate restriction and inherited isotope equality. No eligibility checks or thermal-anchor evaluations were executed. |
| `source/atomic_sources_REI237.json` | Full 1–197 | Original attribution, source domains and exact data-lock fields; cited upstream code/data not all reread because the new unit binds the frozen source fit. |
| `source/MAO_SOURCE_LOCK.json` | Full 1–22 | Full frozen catalog/selected-file identities. |
| `source/mao2017_selected.json` | Full 1–453 | All six selected parameter arrays and source grids. Embedded prior comparisons are author-preserved results, not new calculations or physical errors. |
| `source/mao2017_pars.dat` | Lines 1–8,31–32,60 | Six relevant H/He/Li parameter rows are 1–3,31–32,60. Initial output additionally exposed rows 4–8. All 255 lines were byte-hashed; unrelated rows were not semantically inspected. |
| `source/mao2017_calc.dat` | Lines 1–8,31–32,60 | Corresponding rounded source f tables; no formula/table evaluation or new comparison was performed. Unrelated rows were not read. |
| `source/MOMENT_FROZEN_CONTRACT.md` | Full 1–38 | Historical REC thermal closure/validation scope. Old allocation, IVP plan, flags and execution claims are not current authority or new evidence. |
| `raw/VIGIL95_SOURCE_BYTE_IDENTITY.json` | Entire returned source manifest body, original lines 1–75 | Exact BASS code/data paths and provenance. It guided reads of the actual native/compact/coupled bodies; the separate `affine_system.py` body was not needed for the scalar DR question and was not fetched. |

Directory listings were read for the PR237 unit, implementation directory and vendor subtree (vendor tree `truncated=false`). Listing a path is not reading its body. No new original-source census was attempted by this task; current_repo_census owns freshness and overlap checking.

The prior dependency map, earlier PR237 `thermal_join.py` full 1–358, PR241 owner return, PR242 caloric contract and earlier thermal-interface literature synthesis were reused. Their earlier actual-read ledger remains in `rei_loop_continuation_20261028/survey/literature/NEXT_PHYSICS_DEPENDENCY_MAP.md`. Closed R6/C9/F1 reports and closed numerical campaigns were not reopened or modified.

## 2. Narrow primary-source follow-up

This was a named-definition lookup, not a new recent-literature sweep. No relative date window was used. Current task date is 2026-10-28; paper identification is by explicit DOI/version, not an index's refresh date.

The Exa Search skill and its searching, papers, source-quality and synthesis references were used. The task's explicit honest-read accounting controls: requested result counts are not counted as papers read.

| Query / retrieval | Actual return and selected scope |
|---|---|
| `SCISPACE_MAO_DEFINITION` | One natural-language question about Mao/Kaastra/Badnell's energy-loss definition; 10 returned records, preserved in raw JSON. Selected records `35l1dgy6aj`, `4wqqms7deh`, `0haere80r6dm` refer to one paper/preprint, not three independent studies. Other results were discovery candidates only. |
| `EXA_MAO_AND_DR_PRIMARY` | One fetch call, two requested URLs, two returned primary/official contents. No Exa search call or new broad survey. |

Primary extraction is saved in `literature/MAO_AND_DR_PRIMARY_EXTRACT.txt` (615 lines), retaining the source URLs:

1. **Mao, Kaastra & Badnell:** DOI `10.1051/0004-6361/201629708`, arXiv `1612.01017`. Direct DOI URL retrieved. Deliberate detailed reads: extracted lines 48–85,104–150,230–236,562–564; additional indexed snippets in the introduction/Section 4 were exposed by the output/search. This covers Maxwellian definitions, Eqs. (1)–(7), temperature units, Table 2 indexing, fit-quality meaning and Section 4.4's transfer assumption. Figure images, all plot data and the rest of the article were not independently assessed. The extraction's equation formatting is imperfect; the native formula's explicit logarithm basis is attributed to actual code, not inferred from the paper's `log` notation.
2. **Badnell official DR page:** `https://amdpp.phys.strath.ac.uk/tamoc/DATA/DR/`. Lines 574–591 were deliberately read for the total-fit formula, units, initial-target indexing and tabulation convention; the remainder of the returned page was visible in the original fetch output. No current author table was fetched or substituted for the frozen project data.

Quality basis: original calculation paper and author-maintained formula documentation. The paper's author fit comparison and transfer assumption do not supply a physical discrepancy certificate for the project's hybrid closure. The official page supplies formula/index conventions, not proof of accuracy for each frozen coefficient or of callback rounding.

**Read counts:** 10 discovery records; one distinct primary paper's relevant content; one official documentation page. Existing literature is reused and is not counted as new reading. The full raw query arguments/results are in the common query ledger.

## 3. Execution and remaining limits

No rates, thermal functions, matrix routines, scientific tests, integration, CAS, Wolfram evaluation or new numerical plotting were executed. The only calculations presented are written algebraic differentiation/interval construction and exact source-literal transcription. Proposed <1 CPU-second validation and <1.5 CPU-second presentation are planning targets pending root's allocation and actual timing, not observed performance or inherited allowance.

The available actual source point is a saved interpolated background with continuum interpolation error null; the PR237 fast pool and nu are manufactured/prescribed. Neither it nor the matching source code/data supplies a physical recipient, a qualified stopping law, an actual energy interval, a physical fit-discrepancy radius or a full REI25 binding. The narrowed DR scalar-functional question can proceed without inventing those inputs.

## 4. Subsequent root-contract source-convention read

At root's request, `/workspace/scratch/cc0531120bc9/rei_approved_continuation_20261028/unit/THEORY_AND_CONTRACT.md` lines 1–146 were read after saving the intake. Its selected DR formula, loss weights, binary64 parameter/constant basis, runtime domain, saved-point interpretation and exclusion of full callback rounding/physical error match the inspected source. A small clarification was sent: admit the six recombining keys `{1:1,2:1,2:2,3:1,3:2,3:3}` explicitly; their retained absent DR subset is `{1:1,2:2,3:3}`. An unknown key must not be inferred absent. No unit file was changed, no numerical expression evaluated, and no independent R6/C9 assessment was issued. That review belongs to the designated separate reviewer.
