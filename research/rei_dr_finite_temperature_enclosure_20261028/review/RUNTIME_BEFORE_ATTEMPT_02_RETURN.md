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


