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

