# Validation report

| Gate | Result | Requirement | Verdict |
|---|---:|---:|---|
| Photon partition | 5.229e-16 | <1e-10 | PASS |
| H nuclei | 6.774e-16 | <1e-12 | PASS |
| He nuclei | 6.431e-16 | <1e-12 | PASS |
| Reaction limiter | 5.351e-02 | <1e-4 | FAIL |
| Energy limiter | 3.219e-03 | <1e-4 | FAIL |
| Sink volume filling | 2.769e+06 | <=1 | FAIL |
| First-interval dt refinement | 4.503 ratio | ->1 | FAIL |
| dt/4 and dt/8 | no capacity solution | success | FAIL |
| Post-photo cloud mass | 2.467e+08 cosmic H | <=1 | FAIL |

The requested node-resolved history gate is not closed.
