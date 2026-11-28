# BASS_HE C2c: small-R scaled numerical audit

Paper-derived independent implementation, not ARSENY authors’ code.

The preregistered finite sequence at x=1/8,1/16,1/32 passed spatial, quadrature, independent spherical anchor, six local fixed-m continuation and four parity checks. This is empirical finite-discretization evidence, not a continuum or asymptotic remainder certificate. full C2 remains open; scientific_PROMOTE=HOLD.

See RESEARCH_REPORT_KO.md, CONTRACT.json, CLAIMS.json and evidence/FINAL_AUDIT.json. New states28, scientific tasks40, active batch wall320.103s; no fallback or scientific-task failure. NCP64 scaling was not run.

Native paths use strict binary64 Fortran/OpenMP/SIMD plus explicit OpenMPI tasks. The direct operator streams32 patches and keeps a Python lane. No fast-math or implicit fallback. Build scripts and recorded compiler flags are in native/. Binaries and frozen/new STATE archives are in the private delivery archive, not the public source subset. The archive also preserves exact executed source snapshots and all worker logs.

Run scalar analysis only with `python code/analyze_all.py --output NEW_AUDIT.json` in a complete archived package. The create-only output must not exist. It performs no new physical integrations or solves. Rebuild native libraries with the recorded strict flags for a new host; compare identities and use launch_ncp preflight before an authorized new workload. Do not rerun the completed manifests as a benchmark.

The original sphere8-case transcript is preserved with its original paths in provenance/ANCHOR_SCALAR_TEST_TRANSCRIPT.*; it is provenance, not a portable test command. Public PDFs are excluded.
