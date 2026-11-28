# HE_E13C5_FIRST2_PATH_CONTRACT01 branch cover

Mechanical execution completed; independent Astra review returned PASS_SCOPED.
The result covers exactly the 12 selected captured paths, with fixed
gas interpolation, masks, source branches and all energy anchors.

Base checkout: `48f648cd905cd8c232ae43abe97745ac6a96dec2`, tree
`b9a0ba328c8b6534849a601318574bd862f6aefe`; branch
`research/e13c5-first2-branch-cover-20261011` in isolated worktree
`/tmp/HE-E13C5-first2-branch-cover-20261011`. The starting worktree was clean.
The controller's frozen transcription was copied byte-identically to
CONTRACT.md. No commit, push, or source edit outside this task directory occurred.

One invocation ran `timeout --signal=TERM 180s /usr/bin/time -v python3 -B
cover.py > stdout.log 2> stderr.log`. Exit status was 0; wall time was 34.60s;
maximum RSS was 65,652KiB. N=128, Decimal precision=60, serial execution, and
1024MiB address-space bound were enforced. Controls consumed 0.000231s.

Exactly 36 segments were selected: three reviewed OFF/700 records were reused
without numerical integration, and 33 new segments were computed across the
other 11 paths. Every chronological path prefix, step prefix and whole path
count and anchored-energy ledger included zero. Subsequent incoming intervals
were previous corrected endpoint minus captured next initial stock; no extra
incoming radius was added. Every adjacency used the captured next energy minus
the current exponential endpoint, even when anchored=false.

START.json records the exact recovery/E13C4 archive hashes, unchanged helper
hashes, pilot/result hashes, and all nine capture/node/stage hashes. Each of those
nine files was compared bytewise by digest to its recovery-archive member before
use. Selected keys were checked for duplicates and exact set equality.

RESULTS.json retains continuous-minus-frozen intervals, frozen-minus-captured
moments, captured segment-to-node reductions by step, weighted reductions, and
the erg endpoint discrepancy epsilon*Eend*Pend-u_captured separately. The
weighted aggregates cover only this selected subset; no full AGGREGATE.csv
comparison was made. Interval widths have no new acceptance threshold.

Exact Fraction controls yielded final weighted stock 7/4, absorbed count 21/4,
B=Z=231/8 and anchor=7, with zero count/energy ledgers. Omitting anchors gave
7, resetting carry gave -7/2, swapped carries gave stock 5/4, and dropped weights
gave 3/4. h=0, total opacity=0 and nonzero outflow were rejected. This was an
algebraic control using exp(-ln2)=1/2, with no numerical reference solve.

No first failure occurred, and no repair or rerun was performed. stdout.log and
stderr.log preserve the complete raw invocation output; CHECKPOINT.json retains
the last prefix before RESULTS.json. Native runs, gas advances, old continuous
solves, six-control replays and full-first2 expansions all remained zero.

A01-A08 are recorded as mechanical PASS; A09 passed fresh read-only Astra review.
Full first2 remains HOLD_RESOURCE_AUTHORIZATION. Physical, production, new gas
evolution, actual photon/heat/recoil and receiver adoption remain HOLD.

Executed script SHA256:
`aaae27a0d053d42ce6727593df676352697dd042486aa448d1e9104b16f979f6`.
Contract SHA256:
`cbea11086727b06fac350451b433f10f344664bcdee85948901cac14b62b56dd`.
Results SHA256:
`418dcac9280947abc227c69f9178c0163bbdb00fa34bff1f9e34ab9eea35ece4`.
