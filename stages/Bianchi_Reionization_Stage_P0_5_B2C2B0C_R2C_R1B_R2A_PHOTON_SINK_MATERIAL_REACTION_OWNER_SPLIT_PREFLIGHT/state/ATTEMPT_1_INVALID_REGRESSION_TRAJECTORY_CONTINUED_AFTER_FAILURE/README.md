# Attempt 1 — invalid regression lane continued after first capacity failure

The intentionally invalid unsplit G1+G2a-to-resolved-H comparison failed its
first material-capacity certificate, as expected.  The audit driver then
continued that rejected trajectory with a negative neutral reservoir, causing
the generic nonnegative-input guard to stop the run.

This is an audit-driver control-flow bug, not a failure of the owner-correct
physics.  The repaired driver terminates a rejected comparison trajectory at
the first certificate violation and records later substeps as unreachable.  No
negative reservoir is clipped or reintroduced.
