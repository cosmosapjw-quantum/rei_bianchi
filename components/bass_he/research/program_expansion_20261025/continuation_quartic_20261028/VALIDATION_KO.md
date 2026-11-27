# R6/C6 — actual single-campaign validation
Actual execution sourceS05=2f66fbe31e6d52adb19f6701f58c14c67f6ac204, tree92f2941c65e890eab31adc3043e1cb169abf2e00.
Current status before finaladmission: local11/16,central28/88,HEdelta0.

## Observed execution
One new primary campaign, exit0,7control methodsPASS,0failures,0errors. No repair/retry/predecessor rerun.
All12unique cases ran once. Independent exact saved-certificate reader checked132vertices(inner66+outer66) and12nestedcaseinclusions. It is not a second optimizer.
Actual exact inversecalls24,810;singular1,026;invertible23,784;RHS candidates71,691.
Whole run_bounded process including startup, waited descendants, innerreceipts andshutdown: CPU4.0939380000000005s,wall4.132059788000333s,RSS17,812KiB.
Limits120CPU/300wall seconds;768MiBaddressspaceperprocess,threads1. Both resourcecapsPASS.
Innerreceipt CPU4.047864s,wall4.077105s is a narrower measurement and is not added to the whole-process number.
Outer orchestration CPU0.008362128000000003s is separately scoped and excludes its finalwrite/startup/shutdown.
Runtime model identity unexposed=null; requested executor gpt-6.1-sol.

## Exact finite cases
| Family | 213MeV inner/outer vertices | 258MeV | 330MeV |
|---|---:|---:|---:|
| FreeN1 |8/10|6/4|0/4|
| FreeN4 |10/10|6/4|4/4|
| FreeN16 |10/10|10/8|4/4|
| Endpointzero exact |4/4|4/4|0/0|

A smaller contained polytope may have more vertices than a containing polytope; the vertex counts are not set-volume comparisons.
330MeV N1 has no inner witness at that coarse resolution. N4/N16 supply a positive witness, so the full endpoint-free quartic family is feasible.
330MeV endpointzero has an exhausted empty outer polytope, a fixed-family exclusion.
FULL is identically1 for any genuine feasible distribution; an outer-only FULL row by itself does not prove existence.

## Central scientific discriminant
At330MeV N4/N16 the exact stored same witness is approximately
b=(0.140838303,-0.308117512,0.752692956).
Its exact rational global minimum is positive; displayed qmin≈0.109306056 atz≈0.204676761.
Old folded Bernstein a≈(0.585413747,-0.611854653,0.996237097), hence a1<0.
This is a constructive counterexample to reading EXFOR11's sufficient-cone EMPTY as full-quartic infeasibility. The previous result remains correctly scoped and unchanged.
These rounded coefficients are explanatory displays; exact fractions in SAVED_PLOT_DATA.json are the certificate and should be used to reproduce boundary fits.

## Evidence identities
Exact savedJSON SHA256=a8fbe269d3941706a510796963f059d7404f3f4655a6a3163042e85011aa0d45.
Official input SHA256=b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f.
Prior EXFOR11 savedSHA256=5a13b55d1e8f9a0960cddb7c8c06ae08fcb6212425d71642e41d5a311a9b2243; read-only comparison, no recomputation.
RawSTART/logs/partialprogress/test/certificates and whole-resource receipt are preserved.
R6 review is the same distinct nonauthor pass begun before execution; actual review is in review/VALIDATION_REVIEW.json.
CAS, actual figure and final admission are later gates.

