# Runner repair1 diagnosis and diagnostic result

The initial launcher failed before scientific output or controls: child -9, launcher 1, actual full runner plus waited-child CPU 0.045071 s and wall 0.006065 s. Its namespace-local PID was compared to host /proc process groups, producing unrelated CPU attribution. Original evidence remains untouched.

The first prescribed parent-children/NSpid diagnostic failed because this host does not expose /proc task children files. This is an INPUT_ENVIRONMENT capability fact; that failed diagnostic and source are preserved. Root then authorized the child self-report alternative and one additional tiny diagnostic within this same runner repair.

The repaired runner uses a single-threaded preexec handshake after setsid. The child writes host/local PID and PGID from /proc/self and os APIs before exec. The parent validates local PID/PGID equals the actual subprocess PID and host PID equals host PGID, then monitors the host process group. Failure to read or validate the handshake is an explicit monitor error. Independent final CPU remains full RUSAGE_SELF plus waited children; CPU/wall override values must be positive and no larger than the original mode cap.

The one additional science-free diagnostic PASSED: child local PID=PGID=7; child host PID=PGID=298233, independently confirmed by the executed child raw self-report. Parent local PID2/host298228. Observed group CPU0.0 s, full regression runner plus waited child CPU0.067687 s, wall0.131496366 s, exit0. Limits CPU2s/wall5s/AS768MiB/threads1. No scientific imports or calls occurred.

Changed production source only scripts/run_once.py, SHA256 5abdfd0bd1136a8adc3b8fede30434e399d864c663f92ebe2eaf16bf421e3571. Static compile PASS; scientific producer, certificate reader, eight controls and plotter unchanged. Scientific targeted retry NOT_RUN. Ready for root repair pin publication and independent review before separate GO; original failed primary evidence retained.
