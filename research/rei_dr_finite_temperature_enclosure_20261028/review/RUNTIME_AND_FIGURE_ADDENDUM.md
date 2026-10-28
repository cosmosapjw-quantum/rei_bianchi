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




