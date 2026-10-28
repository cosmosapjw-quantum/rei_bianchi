# Runtime and figure review addendum — DR finite-temperature unit

Unit: `rei_dr_finite_temperature_enclosure_20261028`. Native reviewer: **`/root/current_repo_census`**. This is the actual distinct-author runtime reviewer with shared filesystem and earlier source-census/static context; it is not a blind review.

The closed R6 and static reports remain unchanged and are reused. R6 was PASS_SCOPED_INDEPENDENT_THEORY; the targeted F-ZERO/F-FAMILY source repairs and F-PLOT1 formatting correction were CLOSED_STATIC. Those verdicts did not claim executed controls or an inspected figure. The controller supplied science pin `f43eaf9b16b98e1799f21a93b4555fe7d0ffaf9a` and then-current publication `872bf10bb05e8e625da54f475e97d4af0ed0347f`; no source census or remote-ref refresh was performed for this runtime review.

The controller reports the user's concrete 22/62 cumulative approval and owns dispatch. This reviewer neither grants resources nor executes scientific code. The actual attempt and any authorized productive repair are assessed from returned artifacts.

## Attempt 01 — actual environment/supervision failure

Read completed at **2026-10-28 11:49:00 UTC**. `RUNTIME_ATTEMPT_01_READ_LEDGER.json` preserves the complete seven-file read, byte counts, line ranges and SHA256 values:

- `execution/attempt_01/PROCESS.json`, full lines1–60;
- `execution/attempt_01/STDOUT.json` and `STDERR.txt`, both completely read and empty;
- `execution/outer_numerical_01/PROCESS.json`, full lines1–96;
- `execution/outer_numerical_01/STDOUT.txt` and `STDERR.txt`, both completely read and empty;
- `execution/outer_numerical_01/SOURCE_IDENTITIES_BEFORE.json`, full lines1–37.

All seven recorded prepared source identities match the final accepted static source set. In particular the scientific implementation is `bd307b1f4710911c5047f393cfc3128354a303a2cf05498414c54fa19302f7b0` and the test suite is `c31699f56af6f83a7758c6607f29ce8e9a611e835a2dfb65c53898f57ad11bee`. No changed scientific formula or source coefficient explains this failure.

| Actual observation | Inner worker | Outer waited command |
|---|---:|---:|
| Exit code | −9 | 1 |
| Watchdog stop recorded | CPU_watchdog | null |
| CPU from OS wait4 | 0.000687 s | 0.041656 s |
| Wall time | 0.0010906210009125061 s | 0.04282803200476337 s |
| Separate supervisor-prefix CPU | 0.0020142330000000007 s | 0.020125761000000002 s |
| Raw stdout/stderr | both0 bytes | both0 bytes |

The outer family scan recorded zero maximum ticks and an empty PID list. The inner watchdog nevertheless declared its0.38 CPU-s threshold reached after a worker whose entire measured CPU was0.000687 s. These are actual recorded observations, not a scientific failure or evidence that the DR calculations exceeded their intended CPU target.

The controller's separately reported self-process diagnostic gave namespace `os.getpid()=5`, `/proc/self/stat` PID474236, `/proc/self` link474236 and `NSpid:474236 5`. That diagnostic establishes the controller-observed namespace/view discrepancy. This reviewer did not rerun it; at this initial addendum its raw persisted diagnostic path has not been supplied.

The static control path explains the observations: the old inner watcher addresses `/proc/<namespace child PID>/stat` while this mounted `/proc` exposes host-visible process IDs. It can therefore read the wrong process. Likewise, the outer watcher compares a namespace session identifier with host-visible `/proc` session fields. This is the bounded **F-PID: ENVIRONMENT_INTERFACE / PID_NAMESPACE_SUPERVISION_FAILURE** diagnosis. It is separate from F-FAMILY, whose prior source repair correctly kept the leaf within its parent's session but did not translate the mounted `/proc` identity view.

### Scientific and cost judgment for attempt 01

**C6 execution attempt: FAILED_ENVIRONMENT_SUPERVISION_BEFORE_SCIENTIFIC_OUTPUT. No scientific FAIL is issued.** There is no interval, oracle, zero-step or test completion output to admit. F-ZERO remains source-closed with runtime verification pending. C7/C8 have no returned numerical/figure evidence, and C9 runtime admission remains pending. The closed analytic proof remains valid.

For accounting, preserve outer whole waited-command CPU0.041656 and separate outer supervisor prefix0.020125761. The inner worker0.000687 and inner supervisor-prefix0.002014233 are nested in the outer waited command and must not be added again. Startup, final serialization, tool/host/model and remaining administrative tails stay UNKNOWN_NOT_ZERO. The controller owns allocation of the observed supervisor component against its shared tail reservation; this report does not reset or silently enlarge a budget.

The controller has requested one diagnostic-driven host-PID/SID pipe-handshake correction, preserving all attempt01 artifacts and leaving the scientific module and test suite unchanged. This is a targeted productive repair under workflow1.0.0, rather than an automatic identical retry. The revised wrapper/input-path diff will be inspected when returned. No full proof/source re-review, new census, reviewer scientific execution or live watchdog experiment is authorized or performed here.

## Subsequent targeted repair and returned execution

Pending actual author diff and controller-provided execution artifacts. This section will receive only the bounded changed-control inspection and actual returned numerical/figure evidence. The original static judgment and this failed-attempt record remain preserved.

### F-PIDNS targeted static closure — 2026-10-28 11:51:18 UTC

Verdict: **PASS_SCOPED_STATIC_ENVIRONMENT_REPAIR; READY_FOR_CONTROLLER_DISPATCH**. This is execution readiness for the specific changed controls, not numerical, figure or C9 runtime acceptance. No additional concrete repair finding was identified in this bounded delta.

The complete initial failed-attempt judgment is now byte-preserved separately as `RUNTIME_ATTEMPT_01_INITIAL.md`, SHA256 `eaf1f702b7f807cbcc442feb81703935b7f8777dc88518f8791da507b0b3a079`. The preceding narrative remains intact. The author retains all original wrappers and failed outputs and adds three distinct repaired files.

`PIDNS_REPAIR_READ_LEDGER.json` records full reads of `AUTHOR_PIDNS_REPAIR.diff`1–251, `AUTHOR_PIDNS_FINDING.md`1–11, `REPAIRED_IDENTITIES.json`1–49, `execution/PID_NAMESPACE_DIAGNOSTIC_20261028.json`1–26, `run_once_pidns.py`1–128, `execute_bounded_pidns.py`1–167 and `plot_saved_pidns.py`1–73. The persisted root diagnostic has now actually been read; its observed values match the earlier controller message. No diagnostic was rerun.

The actual text delta matches the supplied three-file diff. All7 repaired-manifest identities and all7 original-manifest identities match their files. In particular the scientific module, source coefficients, test suite, original wrappers and initial failure artifacts remain unchanged.

| New file | SHA256 |
|---|---|
| `code/run_once_pidns.py` | `745921ccc1705b58b7fe42a660e42d31e53581aed416b632bfc38d8a2258e97e` |
| `code/execute_bounded_pidns.py` | `8a345e7fbc3d768d5a3189fbaf0e3377e7eb0c80cd025fd1db4b357162ef95fe` |
| `code/plot_saved_pidns.py` | `287d4eed51dd8c32b9e00edc65ccadd3df544f93984403340d1f65da5c20f539` |

#### Identity, timing and termination path

Each child obtains its own host-visible PID, host session and start ticks from `/proc/self/stat`, paired with its namespace PID from `os.getpid`, and transmits the small record through an inherited pipe before exec. The addressed `/proc` reads then use the transmitted host PID, not the namespace PID. The parser uses the fields after the closing process-name parenthesis: index3 is session, indices11/12 are own user/system CPU, and index19 is start time. The addressed reads check PID, SID and start ticks before using those counters.

The parent waits at most two seconds for the pipe identity, checks the namespace PID against the fork result and validates the expected session. The outer child calls setsid before sending, and the outer parent checks hostSID=hostPID for that session leader. The inner leaf inherits that same session and its parent verifies the inherited hostSID. The overall wall clocks start before fork, so the handshake wait is included in the existing10/12/15-second elapsed limits. An invalid or missing identity follows the recorded stop path and cannot yield successful wrapper return.

CPU family aggregation now compares host-visible `/proc` SID fields with the received hostSID. Kernel kill/wait operations correctly continue to use namespace PID/group identifiers: inner direct kill targets its known leaf; outer killpg targets the new namespace session leader's group. This resolves the diagnosed identifier-view mismatch while preserving the prior F-FAMILY source correction.

The fractional CPU thresholds, hard backstops, address-space limits, no-retry rules and explicit poll/abort-accounting limitations are unchanged. This static closure does not assert a strict whole-host CPU guarantee or measured runtime feasibility.

#### Artifact routing and scientific invariance

The numerical invocation now creates `execution/attempt_02` and `execution/outer_numerical_02`, refuses existing attempts, verifies `REPAIRED_IDENTITIES.json`, and executes the same scientific worker/test body once through `run_once_pidns.py`. The saved-data presentation remains the first figure attempt and reads only `execution/attempt_02/STDOUT.json`, requiring success before using it. Its only source change is that input path; it performs no scientific recomputation.

The controller may publish this bounded repair and issue its already authorized specific dispatch. The reviewer will then assess actual returned values and process identity/CPU records, followed by the actual figure. Until that return, the attempt01 environment failure remains the only execution outcome, and scientific/figure runtime admission remains pending.

### Attempt 02 — actual bounded-resource stop; host mapping now observed

Read completed at **2026-10-28 11:56:56 UTC**. The complete previous report is preserved as `RUNTIME_BEFORE_ATTEMPT_02_RETURN.md`, SHA256 `78cc08c3d3fc123a19b27c2c403d0db11c4932605f5672b28c47bee5112aa3e6`. `RUNTIME_ATTEMPT_02_READ_LEDGER.json` records full reads of outer PROCESS1–105, source identities1–37, all outer streams, and both inner streams, plus the verified absence of inner `PROCESS.json`.

The actual outer handshake records hostPID=hostSID=481633, namespacePID=5 and start_ticks=4710411. Its live-family observation contains host PIDs481633 and481634. The monitor now records36 ticks at100 Hz and terminates with `aggregate_CPU_watchdog` at its unchanged0.36 CPU-s threshold. Thus F-PIDNS's host/session translation is **CLOSED_FOR_THE_OBSERVED_RUNTIME_MAPPING**: the expected runner/leaf family is seen, rather than the empty family in attempt01. The inner handshake receipt did not survive the group abort, so no complete inner runtime receipt is claimed.

All seven attempt02 source identities match the reviewed PIDNS preparation. In particular the original scientific implementation and tests retain their accepted hashes. The inner stderr contains only the selected test method's start line; stdout is empty. Both outer streams are empty. There is no test-return summary, interval record, oracle value or scientific assertion failure.

**Actual attempt02 result: FAILED_BOUNDED_RUNTIME_RESOURCE_LIMIT_BEFORE_RESULT_RETURN.** This is a performance/execution outcome under the specified bound, not a failed physical or mathematical assertion. C6 has not completed; C7/C8 scientific/figure evidence and C9 runtime acceptance remain pending.

The outer process exited−9 after wall0.3537373469953309 s. Its waited-command field is0.065662 CPU-s, with separate outer supervisor prefix0.188753228 s. Because the group kill terminated the intermediate parent before it reaped the scientific worker, the0.065662 field does **not** measure the full job family. The receipt's abort caveat applies. The36-tick family observation must not be added to that overlapping parent counter or mistaken for an exact final whole-family value.

The controller retains the full planned0.4 numerical reserve for attempt02 and accounts for the separately measured supervisor prefix; unknown un-reaped tail remains explicit. The controller-reported conservative pre-next-attempt planning balance is21.654823051, with a prospective0.25 reservation yielding21.904823051 under the current22 ceiling. These are controller accounting/reservation values, not a reviewer whole-session resource certificate. No prior allowance or failed reservation is reopened.

The controller's bounded performance diagnosis identifies repeated kernel and curvature-bound work across the same36 Taylor controls. The proposed correction is per-instance memoization with complete immutable operand/context keys and fresh interval wrappers, retaining all original formulae, precision, input coefficients, tests and acceptance criteria. Separate attempt03 files and the failed artifacts are to be preserved. Poll intervals may change to reduce monitoring overhead, with a smaller numerical target and explicit guards. This is a new diagnosis-driven preparation, not an automatic identical retry.

The reviewer has not executed or benchmarked this optimization. Its actual diff must be inspected for cache purity, key completeness, object aliasing and routing before the controller dispatches it. The closed D1–D5 proof will be reused; no new source census or full theory audit is undertaken.

### F-RECOMPUTATION cache and final control closure — 2026-10-28 12:00:18 UTC

Verdict: **PASS_SCOPED_STATIC_MEMOIZATION_AND_CONTROLS; READY_FOR_CONTROLLER_DISPATCH**. No concrete cache-purity, identity or routing defect was found in the returned bounded change. This does not claim a measured speedup, completed test or runtime PASS.

The pre-cache report is preserved as `RUNTIME_BEFORE_CACHE_REPAIR.md`, SHA256 `755e2a2992e695a5dd761a0b488b1a9e198b96909e42ed635a4a1d013b0b3906`. Initial and final preparation reads are recorded in `CACHE_REPAIR_READ_LEDGER.json` and `CACHE_FINAL_CONTROL_READ_LEDGER.json`. The full original cache diff1–180, finding1–25 and manifest1–48 were read; actual changed source ranges were read in the new model1–9,120–264, runner13–31,75–128, outer wrapper1–6,87–167 and plot1–16. Unchanged code is reused through exact text-diff identity, not re-audited.

Before execution, the controller chose a larger reservation within the same22 cap. I then read the final finding1–27 and full final manifest, plus runner103–124 and outer87–105,124–141. `CACHE_FINAL_RESOURCE_DELTA.diff` contains only the final resource edits relative to the preserved unexecuted draft: numerical target0.25, outer guard0.22 and inner guard0.23. The final complete author diff matches the actual four new files, and all7 final prepared identities match. The prior original and PIDNS sources, scientific tests and coefficient file remain unchanged.

#### Why the cache preserves the computation

The two OrderedDict caches are per model instance and bounded to256 entries each. A kernel key contains the exact energy and both exact temperature endpoints. Its context signature includes precision, Emin, Emax, clamp, rounding, capitals and all trap settings. A second-derivative-bound key additionally contains freshly decoded coefficient and energy tuples, current s and k, both interval endpoints and the loss selector. It therefore identifies the actual operands rather than merely a species name or mutable source-container identity.

Domain/species validation occurs before a second-bound lookup, and the kernel checks the exact Arithmetic instance before lookup. Changing an admitted row, conversion-factor value, domain, precision/exponent setting or trap configuration changes the corresponding key; a different model owns different caches. The unchanged arithmetic uses local context copies, so unrecorded persistent flags are not a numerical input to these cache results.

The stored values are tuples of immutable Decimal endpoints, not mutable Interval objects. Both cache hits and new stores construct fresh Interval wrappers. Changing a caller's returned interval cannot replace the stored endpoint tuple. Eviction only causes a future recomputation and changes no result.

On a miss, the kernel and curvature-bound expressions are textually unchanged apart from storing/returning their results. On a hit, the same endpoint values for the same operands/context are reused. Thus the optimization preserves the represented source function, outward arithmetic, signed coefficients, positive lower-bound construction, curvature bound and zero-step shortcut. The fixed tests and90-digit oracle retain SHA256 `c31699f56af6f83a7758c6607f29ce8e9a611e835a2dfb65c53898f57ad11bee`; no cases, tolerance or precision were relaxed.

#### Final identities and dispatch boundary

| Final source | SHA256 |
|---|---|
| `code/dr_enclosure_cached.py` | `be32fe17982ec9d1e9a6d506e37296d11cbe39fd6bc66690e6563ee62e2fb59c` |
| `code/run_once_cached.py` | `e4069c97b9e027bcba1db28353303d0ac4646fc8c8bc52f15dfd457c48e86b00` |
| `code/execute_bounded_cached.py` | `691d8b7af9bf3cad17223ec4cdfc0834601a1f1514d8127f12fc00ff672bae8f` |
| `code/plot_saved_cached.py` | `a6f88d76d4968b5636b64696b69e9705562b612b158ee505795c3729c684a5d7` |

The worker aliases the cached module into the same `code_dr` test dependency and writes only attempt03. The outer wrapper verifies `CACHED_IDENTITIES.json` and writes outer_numerical03. The plot reads only successful attempt03 JSON and retains the first presentation attempt. All failed attempts remain intact.

The PIDNS handshake and namespace kill/wait rules are unchanged. Poll intervals are0.01 s outer and0.005 s inner; presentation target/guard remain1.5/1.4 CPU-s. Numerical target/guards are0.25/0.22/0.23 CPU-s, with hard per-process backstop1 s and unchanged memory/wall limits. These are recorded monitoring targets with the existing tick/poll/abort limitations, not strict whole-host bounds.

The controller's conservative pre-attempt planning view21.654823051 plus the fresh0.25 target and0.05 tail reservation is21.954823051 under22. This final reservation supersedes the earlier unexecuted0.2/0.16/0.18 draft; it is not an additional attempt or a new cumulative ceiling. Old closed reserves are not reused, and UNKNOWN_NOT_ZERO remains.

No benchmark, import, compilation, test, numerical evaluation, CAS or renderer was run by the reviewer. The controller can now publish the exact final preparation and issue the bounded attempt03 dispatch. C6–C9 scientific/runtime acceptance still requires the actual returned data and figure; the previous two execution outcomes remain part of this record.






## Attempt 03 — actual numerical return after the bounded cache repair

Read and judgment completed at **2026-10-28T12:11:48.209508+00:00** by native reviewer **`/root/current_repo_census`**. The exact pre-return report is preserved as `RUNTIME_BEFORE_ATTEMPT_03_RETURN.md`, SHA256 `881bc58f147e7b669e8e5ad66f80ca7f35d47fae59e75443c886408bc9d9e495`. This section appends a new actual-runtime judgment. It does not rewrite the initial theory/static verdict, the two failed attempts, or the unexecuted preparation decisions.

**Result: the selected numerical return is accepted for C6, C7, the numerical portion of C8, and the numerical portion of C9. The required figure is NOT_RUN; full C8/C9 and complete C10 are not admitted here.** Root reports a separately verified presentation-ledger overrun and owns any further authorization. The successful numerical evidence remains valid independently of that outstanding presentation obligation.

### Complete actual intake and source binding

`RUNTIME_ATTEMPT_03_READ_LEDGER.json` records full text/empty-file reads, line coverage, byte counts, hashes and actual source-identity comparisons. The numerical stdout was read in full, lines1–2103: **95,637 bytes**, SHA256 **`b5548d5c34c3a37423db88485f8feb62568a3102ddcbb5f87020ca0e43e658f8`**. The reviewer also read all six inner stderr lines, all 66 inner receipt lines, all 104 outer receipt lines, all 37 before-identity lines, and both empty outer streams. A transport-truncated part of the first combined read was explicitly reread; it is not treated as unseen evidence.

All seven current source byte identities match the frozen cache manifest, the outer before-invocation identities, and the outer process receipt. The five sources recorded by the inner runner match too. The scientific cache implementation is `be32fe17982ec9d1e9a6d506e37296d11cbe39fd6bc66690e6563ee62e2fb59c`; the original unchanged test suite is `c31699f56af6f83a7758c6607f29ce8e9a611e835a2dfb65c53898f57ad11bee`; coefficient source is `38397e6b560f463f09a5923eaa5902a24312e5246abc158694451c631cd4d6bc`. The final inner/outer wrappers are `e4069c97b9e027bcba1db28353303d0ac4646fc8c8bc52f15dfd457c48e86b00` and `691d8b7af9bf3cad17223ec4cdfc0834601a1f1514d8127f12fc00ff672bae8f`. No scientific source or criterion substitution was found. The preparation manifest's historical PREPARED_NOT_RUN label is retained; the separate actual receipts establish this later run.

This was a source-and-return review with shared filesystem and earlier intake/static context, **not a blind review**. The reviewer ran no scientific code, imports, tests, benchmarks, CAS, recomputation, or figure generation. Previously closed R6 and static reasoning are reused; actual output values below were read and assessed against those references.

### C6: the selected worker completed normally

The inner and outer receipts both record exit 0, raw wait status 0 and watchdog null. Stderr records the selected method completing `ok`, one method in 0.071s, followed by OK. That summary establishes ordinary return, but is not the scientific acceptance criterion; the underlying numerical records were inspected separately.

| Actual process observation | Recorded value | Interpretation |
|---|---:|---|
| Outer runner host PID / host SID / namespace PID | 494076 / 494076 / 5 | Own monitored session established |
| Inner worker host PID / host SID / namespace PID | 494077 / 494076 / 6 | Worker retained the runner's host session |
| Runner / worker start ticks | 4788798 /4788800 | Distinct observed process births bound to their identities |
| Outer whole waited command CPU | **0.178144s** | Normally reaped runner and its waited descendant |
| Outer wall | 0.1805866889990284s | Actual returned duration |
| Outer supervisor prefix CPU | **0.028516684s** | Separate from whole waited command |
| Inner worker CPU / supervisor prefix | 0.13549s / 0.003893202999999998s | Already nested in outer whole cost; do not add again |
| Maximum observed family ticks | 15 at 100 Hz | Sampled live observation, not a replacement whole-cost receipt |
| Maximum RSS | 14,720KiB | Linux receipt |

The outer final live-family list contains the runner after the child was reaped; the inner handshake separately records the child and common SID. Unlike the aborted second attempt, both normal receipts are present and the runner reaped its scientific child before its own normal return. Thus the outer 0.178144s is the normal whole waited-command charge within the stated OS scope. The separate prefix is not silently omitted and the nested counters are not charged twice. Unknown startup/finalization/model/network costs remain UNKNOWN_NOT_ZERO.

### C7 and C8 numerical evidence: what the values establish

The immutable parameter-image section records the exact represented binary64 constants and all coefficient/energy inputs, including the negative third coefficients for 2:1 and 3:1. Energies are exact integer images. The 3:2 control row is all positive; the phrase “signed rows” does not mean this row contains a negative coefficient. The claim remains the represented real DR sums and the conditional energy-weighted loss, with nominal Decimal precision 60 and independent scalar-oracle precision 90. The independently written higher-precision scalar oracle shares the Decimal/libmpdec backend; it is not a second arithmetic-library verification. The accepted enclosure is not a bound on the entire rounded native callback or physical fit uncertainty.

**Finite-temperature enclosure and positivity.** All 30 saved range records were read: three rows, alpha/L, and five intervals including [100,101], [14000,16000], the interior-peak region [300000,400000], [900000,1000000], and the whole [100,1000000] domain. Every saved lower bound is strictly positive; the saved direct oracle at the stated temperature lies between the recorded endpoints. The signed rows use exact positive rewrite margins, while 3:2 uses positive terms. This is numerical support for the previously proved continuum construction; sampled oracle containment alone is not substituted for that proof.

For example, He+ alpha on [14000,16000] is enclosed by approximately `[3.632820494298700e-30, 1.861653335575842e-28]`; the 15000 K oracle is `2.975054740918015e-29`. On [300000,400000] its enclosure is approximately `[1.964762810521159e-18, 2.057712555093809e-18]`, containing the 350000 K value `2.035188369983457e-18`. The whole-domain He+ alpha lower bound remains `1.143631859914245...e-2024`, despite the negative term. The whole-domain Li+ alpha lower bound is `7.217801951456896...e-2770`, and the Li2+ conditional-loss lower bound is `1.364622905362912...e-3734`. These very small positive endpoints are retained as decimal strings rather than rounded to binary64 zero.

**Interior maximum.** The saved kernel control uses `E=463300` and peak temperature `308866.666...K =2E/3`, which lies inside [300000,400000]. Its peak `1.2998753717685775829...e-9` is larger than the endpoint-only maximum `1.2990404456014165911...e-9`. The interval upper endpoint `1.2998753717685775829...e-9` rounds outward beyond the 90-digit peak. This directly exercises the previously derived interior-critical-point branch; an endpoint-only envelope would miss this observed maximum.

**Signed sums and clipping.** All four actual comparisons at 1,000,000 K show the expected positive bias from removing a negative coefficient. The following values are abbreviated display copies; the full precision is in raw stdout. Alpha has units m^3/s and L has units J m^3/s throughout these tables.

| Row / quantity | Signed result | Clipped result | Positive clipping bias |
|---|---:|---:|---:|
|2:1 alpha|1.011133652752769e-18|1.020118153212391e-18|8.984500459622124e-21|
|2:1 L|6.574534962222602e-36|6.684773234500310e-36|1.102382722777078e-37|
|3:1 alpha|4.531471076267092e-20|4.565376159744528e-20|3.390508347743585e-22|
|3:1 L|4.242457570650662e-37|4.281174964960199e-37|3.871739430953750e-39|

The unmodified signed result remains positive. These observations support retaining the actual signed source representation, not clipping its coefficients as a positivity shortcut.

**Underflow and structural absence.** At 100 K, the separately recorded binary64 scalar value is 0.0 for all six row/quantity controls. The high-precision mathematical values remain strictly positive:

| Row | alpha at 100 K | Conditional L at 100 K |
|---|---:|---:|
|2:1|1.161542734113526e-2024|7.429862478703350e-2042|
|3:1|7.413227845667924e-2770|6.494149130746473e-2787|
|3:2|1.158860765512523e-3717|1.364622905362912e-3734|

Those records explicitly retain `structural_absence:false`. In contrast, source-absent 1:1 has exactly [0,0] for both quantities and `structural_absence:true`. The result therefore distinguishes a small nonzero represented function from an absent source row. It does not infer absent physics from floating-point underflow.

**Directional Taylor return.** All 36 saved Taylor records were read, including signed h intervals, scalar actual h, f0 and derivative endpoint intervals, direct target values, direct residuals, radii and final enclosures. The six targets for each row/quantity stay within the supplied [14000,16000] box. The exact recorded background anchor is `14919.863839279505555168725550174713134765625K`; its provenance remains “interpolation of saved background only.” It is not promoted to an actual recipient temperature.

For each record, the saved 90-digit actual h lies within the directed h interval, the direct value lies within the returned Taylor enclosure, and the positive direct residual is below the recorded remainder radius. The following largest-step pairs show the scale of the margin without relying on a boolean count:

| Row / quantity | Residual at h=-1/128 | Residual at h=+1/128 | Remainder radius, approximately |
|---|---:|---:|---:|
|2:1 alpha|6.088406462382708e-31|7.022878771907329e-31|5.483990563669276e-30|
|2:1 L|3.894891281063742e-48|4.492709617578653e-48|3.508427276059406e-47|
|3:1 alpha|2.549836571164039e-37|3.124985057636846e-37|5.164119413788057e-36|
|3:1 L|2.239917579639147e-54|2.745337961406956e-54|4.540985284646007e-53|
|3:2 alpha|9.625384597821388e-43|1.272602957651808e-42|5.368308540977442e-41|
|3:2 L|1.133462329828520e-59|1.498588819642681e-59|6.321767785632739e-58|

The saved radii decrease by the expected factor of about four as |h| halves, with outward-rounding differences in the final digits. For He+ alpha the positive-h residuals at 1/128, 1/256, 1/512 are `7.022878771907329e-31`, `1.692733371985544e-31`, `4.156104890063989e-32`, while the respective radii are `5.483990563669276e-30`, `1.370997640917319e-30`, `3.427494102293298e-31`. The negative-h values also contract. This is observed finite-step agreement with the closed quadratic remainder argument, not a new extrapolated error theorem.

Some Taylor enclosures are deliberately broad and cross zero. For example 3:1 alpha at h=-1/128 has a lower endpoint `-1.366012691302504e-36` while its direct value is `4.053090379601957e-36`; 3:2 has similarly broad large-step intervals. This is not a negative actual DR result or a failure of the positive finite-range construction. It limits how tightly the standalone Taylor interval can certify a positive value at that step size. The reviewer does not report every Taylor interval as strictly positive.

**Precision and rejected inputs.** The four 50/70-digit He+ comparisons enclose the same 90-digit alpha/L oracle values and preserve the leading interval endpoints ; 70-digit bounds are visibly consistent with the directed 60-digit and 50-digit results. This checks the recorded precision changes, not every possible Decimal context mutation. All nine saved input-refusal cases identify their intended boundary: unknown key, coefficient hash mismatch, bool, complex, NaN, infinity, lower-domain violation, upper-domain violation and reversed interval. The unchanged previously inspected suite establishes which call raised; raw return records the actual refusal. No selected criterion was relaxed after failure.

### Observed repair closure and its limits

- **F-ZERO — CLOSED_RUNTIME_FOR_THE_SELECTED_COLD_ZERO_STEP.** Both He+ alpha and L at `T0=target=100` return exactly `h.lo=h.hi="0"`, radius `"0"`, and enclosure endpoints identical to f0. The positive f0 intervals are approximately `[1.161542734113525...e-2024,1.161542734113525...e-2024]` and `[7.429862478703349...e-2042,7.429862478703349...e-2042]`; the full endpoint strings differ in their outward final digits and are preserved in stdout. Nonzero derivative intervals are returned normally. The previously identified cold zero-step underflow path no longer prevents the selected run from completing.
- **F-PIDNS and F-FAMILY — CLOSED_RUNTIME_FOR_THE_OBSERVED_PROCESS_TREE.** Both handshakes now identify the host-visible processes and common host SID while retaining distinct namespace PIDs for fork/wait semantics. The inner worker returns, is reaped, and the outer normal receipt follows. This actual tree supports the bounded interface repair; it is not a claim about every future PID namespace arrangement.
- **F-RECOMPUTATION/cache — ACCEPTED_EXECUTED_SELECTED_PATH.** The source-bound cached implementation completed the unchanged selected suite within the final prepared target and returned all scientific records. The previously accepted operand/context and fresh-return static reasoning is reused. There is no separate cache-hit counter, adversarial mutation campaign or controlled speedup benchmark in this return, and none is inferred. The earlier aborted execution is preserved, not converted to a completed baseline timing.
- **F-PLOT1 remains CLOSED_STATIC only.** No actual SVG, PNG or outer presentation receipt exists at the planned paths. Numerical acceptance does not close the visual inspection obligation.

### C9 numerical verdict, remaining figure obligation and accounting boundary

| Stage / portion | Current distinct-author verdict | Remaining limitation |
|---|---|---|
|R6 and earlier static preparation|REUSED_CLOSED_EVIDENCE|Original reports unchanged|
|C6 selected numerical execution|PASS_SCOPED_ACTUAL_EXECUTION|Only the frozen selected DR controls|
|C7 numerical interpretation and productive repair return|PASS_SCOPED_NUMERICAL_RETURN|Both earlier failures remain classified and charged separately|
|C8 numerical consistency portion|PASS_SCOPED_NUMERICAL_CONSISTENCY|Actual figure still NOT_RUN|
|C8 complete stage|INCOMPLETE_FIGURE_NOT_RUN_RESOURCE_BLOCKED|Needs the required saved-data figure and inspection|
|C9 numerical source/result review|ACCEPTED_SCOPED_NUMERICAL_RETURN|Distinct-author, shared context; not blind|
|C9 complete stage|INCOMPLETE_FIGURE_REVIEW_PENDING|No full runtime-plus-figure admission|
|C10 complete handoff|NOT_ADMITTED_BY_THIS_REVIEW|Root owns publication/backups; required figure obligation remains|

The controller reports the reconciled pre-attempt planning view `21.654823051`, replaces the new numerical reservation by actual whole cost `0.178144`, and retains the fresh shared tail `0.05`, yielding **21.882967051**. The separately observed outer prefix `0.028516684` is inside that retained tail and must not be added again to that conservative view. This statement records the controller's reconciliation and the read actual receipt; it is not an independent whole-session cost certification.

Root separately reports that the verified PR248 closeout adds planning 0 and presentation `4.555332`, taking current presentation to **64.673305870>62**; PR249 changes the main ledger only. Those external ledger findings were supplied by the controller and were not remotely reread in this runtime task. Accordingly the planned presentation invocation is **NOT_RUN_RESOURCE_BLOCKED**. The reviewer grants no new allowance and transfers no foreign or closed budget. The existing valid numerical result is retained while the incomplete figure obligation is stated explicitly.

No original gate, EOS/caloric certificate, native recipient coefficient binding, physical temperature or radius is admitted by this review. Raw `physical_fit_uncertainty` and `actual_recipient_T` remain null and `L4_ready` remains false. The accepted domain is the three supplied represented DR rows on the contracted temperature domain, their conditional weighted losses and the selected tested Taylor construction. There is no new science defect found in the returned numerical records and no request for another numerical run.
