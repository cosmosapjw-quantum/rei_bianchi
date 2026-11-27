# TANGENT13 targeted runner repair — independent review

**PASS_SCOPED_REPAIR_PREEXEC; F5 closed for the next execution; zero open blockers.** This is a continuation of the original independent nonauthor pass. It does not erase the initial launch failure or the first diagnostic failure.

The repaired runner obtains host PID/PGID from the owned child itself, after its new session starts and before exec. The parent checks its local child identity and new-session invariants, accounts through the verified host process group, and retains caller-local process-group signaling. Full cumulative runner CPU plus waited-child CPU and the final wall cap remain enforced. Limit overrides cannot exceed the frozen caps.

The saved science-free diagnostic passed: executed-child stdout independently confirms host PID=PGID 298233 and local PID=PGID 7. Actual diagnostic CPU was 0.067687 s and timed wall 0.13149636599700898 s; scientific imports/calls were zero. The missing parent-children proc interface is documented as the cause of the earlier diagnostic failure.

All scientific source hashes still match PREEXEC_REVIEW. Only the production launcher changed. The original launch used 0.045071 s of actual runner plus waited-child CPU and failed before controls; its 711.220077 s monitor reading was misattributed host CPU. Both failures remain evidence.

After actual publication/readback of the repaired source pin, root may authorize the one targeted scientific retry in `evidence/validation/repair1` with CPU 119 s and wall 299 s. This decision admits execution only; actual result, plot and final publication review remain pending in the same pass. The reviewer executed no science, tests, CAS or plot.
