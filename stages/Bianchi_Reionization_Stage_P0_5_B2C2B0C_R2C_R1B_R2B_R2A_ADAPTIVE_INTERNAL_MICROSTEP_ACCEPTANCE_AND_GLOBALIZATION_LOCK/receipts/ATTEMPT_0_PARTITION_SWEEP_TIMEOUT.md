# ATTEMPT 0 — broad partition sweep timed out

The first unbuffered science-scale partition sweep attempted multiple levels in
one process before the thermal and owner hot paths had been isolated.  It hit
the 900-second foreground limit while evaluating the first coarse partition.
The empty `PARTITION_PROBE.log` reflects buffered output loss, not a numerical
verdict.  This attempt is non-load-bearing and is preserved only as performance
provenance.

Root cause investigation subsequently separated owner evaluation, chemistry
matrix assembly/solve and the thermal root.  No science claim, timestep
certificate or convergence classification is inherited from this timeout.
