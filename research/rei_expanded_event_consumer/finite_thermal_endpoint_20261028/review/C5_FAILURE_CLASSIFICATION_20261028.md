# C5 failure classification: one source-level correction

2026-10-28 KST. Unit finite_thermal_endpoint_20261028, cosmosapjw-quantum/rei_bianchi, branch research/rei-causal-prefix-consumer-20261027, Draft PR240. Base HEAD66878795aa14f79b32be0cd532c31b3a4a036985. Original C5 sourcefc265415b8011863f2cc3e4af851bb27ce8db4c7.

## Scope and result

The owner-approved controller-direct C5 authoring permission is retained. The latest general continuation request does not supply the separately required numerical execution ceiling. This is one targeted correction to the already authored runner, not a new theory, test campaign, independent review, or completed C6. Status: PATCH_AUTHORED_NOT_EXECUTION_VERIFIED. R5/10 plus C5/10 preparation remains10/20. Working DAG33/88, central28/88,88IDs/17edges, delta0. Old atomic-storage20/20 is separate and unchanged.

## Actual defect and direct control-flow witness

Original run_once.py, blob35d6503fd55d817abbe4a51b9e794e446d6e0ca1, has `except BaseException` set a single stop_reason. The subsequent budget_ok conjunction requires both stop_reason is None and usage is not None; every false result is labelled RESOURCE_STOP_OR_OVERRUN.

Take the reachable conditional case that os.fork() raises OSError before a child starts, while observed CPU and wall counters are below their limits. The exception branch sets stop_reason, leaves usage=None, and the old result is RESOURCE_STOP_OR_OVERRUN. No measured resource limit violation was needed. The implication from a supervisor error to a budget violation is unsupported. The same conflation affects a captured KeyboardInterrupt. This witness is derived by reading the published source, NOT produced by an executed fault-injection test. No actual fork failure is reported for this turn.

A second aspect of the same classifier is that a negative worker exit can fall into ordinary EXECUTION_FAILED without recording the actual terminating signal. Python's official os.waitstatus_to_exitcode documentation defines negative exit status as minus the signal number. The signal documentation identifies SIGALRM and SIGPROF for the respective interval timers. Linux getrlimit(2) identifies SIGXCPU/CPU-soft-limit and SIGKILL/CPU-hard-limit behavior. A signal alone does not prove its sender or distinguish an external SIGKILL, OOM and a configured limit. The revised record retains that uncertainty instead of guessing.

Primary API sources inspected:
- https://docs.python.org/3/library/os.html#os.waitstatus_to_exitcode
- https://docs.python.org/3/library/signal.html#signal.ITIMER_PROF
- https://man7.org/linux/man-pages/man2/getrlimit.2.html

## Smallest correction and future controls

The existing runner now calls a pure classify_outcome function. It receives the already observed exit, terminal-usage presence, supervisor error kind and whether a limit overrun was actually observed. Explicit BudgetStop or a recorded overrun retains RESOURCE_STOP_OR_OVERRUN. Other supervisor exceptions retain EXECUTION_FAILED, operator interruption retains INTERRUPTED, and an absent terminal observation retains INCOMPLETE_OBSERVATION. Worker SIGALRM/SIGPROF/SIGXCPU is WORKER_RESOURCE_SIGNAL with cause unconfirmed; other negative exits preserve signal_cause_unconfirmed. Nonzero normal exit is nonzero_exit_unadjudicated. Exit zero remains EXECUTION_EXIT_ZERO_NOT_SCIENTIFIC_ADMISSION.

Raw wait status, supervisor exception type, termination signal and each individual limit observation are retained in RESULT.json. Missing worker CPU and the aggregate including that unknown worker CPU remain null, not zero. If an actual overrun and another error coexist, the overrun is the primary status and the other raw evidence is still preserved. The record remains pre-final-serialization accounting; external complete-command timing and the existing tail reserve remain required.

Six authored pure classifier controls cover supervisor exception, explicit resource stop/observed overrun, operator interruption, timer-related signal, SIGKILL/incomplete measurement and zero/nonzero exits. They deliver no signal and launch no process. The18 original mathematics/representation methods and3 authorization methods are retained unchanged; the total is27 authored methods, executed0. All controls still await their first separately authorized C6. There is no red/green test claim.

Only run_once.py, test_finite_thermal.py and README.md change, with this source-review note added. The repair does not change timers, limits, authorization policy, exact worker command, attempts, science inputs, tolerances or equations. It does not try to make every hard-kill/cleanup path receipt-proof, install new security machinery, or start another review cycle. The classifying function itself is not runtime validated.

## Physics and evidence preservation

The finite_thermal.py source remains byte-identical:20532bytes,SHA2568482189fb3f7fd66d7b164517d0cce11431d315a5492ed3632643ff5100cf14d,Git blob880a074f793ba6bb3aa3e1d7958d8116eb239c0e. Its definitions, positive-domain caloric map, r0/r_balance/rE/rN, exact JVP, inert-He bath, source binary64/hex/MP-decimal decoding and gas Q/W ownership are untouched. This preservation is source identity, not new validation of those formulas or actual-source execution.

The frozen BASS input remains634c3046ffccc5d00f1ab7588b5834a6eb8053ad,sourceSHA256a0fa9b5237481e66f178f19eb1589607412d9d1188d7fb571e5df03b67fd93ac. No replacement with CR/HE/REC/WU/Vigil input occurs. Physical temperature/native25/nb/radii staynull,L4false,globalnull. The historical final-ZIP failure remains runtime_environment/resource_budget; this static classifier defect neither changes that historical classification nor refutes the physics.

## Fresh related-source observations

| Surface | Current observation | Reuse boundary |
|---|---|---|
| REI working |66878795aa14f79b32be0cd532c31b3a4a036985 before this patch|C5 original source/receipts reused|
| BASS restart |f834101d3292f304681349db5d435c6f0c6b559e|Selected ref unchanged, not a new revalidation|
| HE azimuth |307fee38cb65b957deea84c3308f59e972049362|Selected ref unchanged|
| CR He-event union |729cb95164697d8122b0a85ae6e403b57392e724|New documents; owner science406783036c26e71f3b85568adcfb5e163b012ab1|
| REC QSS regularity |5438f2a082f7ed204603e441866ca63d1e0bf9de|Selected contract ref unchanged|
| WU registry |c92e63787ed7f6b50cbec06dd0b8dd2a00ace518|Selected ref unchanged|
| VigilODE PR92 |7eb2dd0ffda39afb2871d76700a720986ff09fe0|Scoped implementation versus incomplete full CI retained|
| REI central |3d8bcdb79a7062459adaad9be6d7fe951f86a17a|New CR_HE_EVENT_UNION owner-return directly read|

The central CR return reports its own R10/10,C10/10,total20/20 and central count authority28/88 with completion effect0. Its actual exclusive measure,Ccross,EOS/temperature and full native25 remain null. This is the supplier's scoped result and published evidence, not our new run, actual BASS bath input, independent review, or transferable execution budget. The same-pin CR HANDOFF_KO.md is explicitly a preimage and refers readers to later receipts; its earlier null publication fields are not the final current delivery status.

Coverage is seven selected repository lanes plus one central ref, selected actual producer/consumer files, indexed prior-conversation retrieval and exact existing backup metadata. It is NOT all current branches/files, all private conversation transcripts or all backup bytes. The historical1417branch census is not relabelled as a fresh exhaustive census. No exact-unit C6 numerical authorization or distinct-author review was established by conversation retrieval. The current PR240 review endpoint returned an empty list; this does not prove that no off-platform review exists. Prior conversation summaries about unrelated units are not imported as authority.

Original C5 source capsule remains63289bytes on Drive1ZQ_3dkVwVNREA9CgwoIKXIsFxeB2QvSr and Dropboxid:BSpOijBcT10AAAAAAEDJFg,with fresh metadata readbacks at both IDs. Original capsuleSHA256731eac2b184c695e0660b10a545c27ee8100e7a738e762b0424f3a6cce9e022e is reused from the original receipt; this turn did not download those remote bytes. New patch backup is a delta source capsule, not a rebuilt old capsule or ZIP. Actual new upload ACKs belong in the later handoff, not fabricated here.

## Work and resource observations

Science tests, imports of project modules, syntax/AST/compile checks, CAS evaluations, actual-source evaluations, ODE/provider solves, plots, old bundles restored and ZIP executions:0. Native subagents:NOT_RUN; this is same-context source review and controller authoring. No fresh-independent R6/C9 or new scientific PASS is claimed. No new SciSpace/Exa/Wolfram scientific result was needed or manufactured for this process-classification correction.

Current-turn Python metadata/text-processing execution succeeded, PYTHON_PASS,Python3.13.5; it did not import the runner or science module. C++ was not probed and no unavailability is inferred. Two observed outer metadata commands displayed respectively user0.02/system0.02/wall0.04s and user0.01/system0.02/wall0.04s. These rounded displays are not exact full-turn totals. Shell reads, subsequent report/capsule/hash preparation, model/network/connectors and recording tails are additional nonzero or unmeasured costs. Exact aggregate CPU and whole-turn cap compliance are not asserted.

Historical planning15.929490885/lastcap16,presentation lower48.263016494/lastcap47,original baselines10/30,main595.225063/600 NO_MORE_IVPs and all subsequent separately recorded costs remain. Unknown costs remainUNKNOWN_NOT_ZERO; no reset, transfer or foreign allowance is used. Research cap20/reserve3 and ZIPcap60/reserve8 remainNOT_APPROVED. Controller-direct C5 permission remains approved, not re-requested.

## Next boundary

Publish this limited correction and preserve its actual dual backup. Keep workflow10/20 and canonical counts unchanged. C6 remainsNOT_RUN awaiting the separate quantified authorization. Any future approval must use the revised runner/test hashes and retain historical debit; the old hash-bound command cannot silently authorize a changed file. The same27-method fixture suite is the next execution target. Actual-source mode remains separate. Do not use the absent numerical authorization to generate another survey/metadata loop.
