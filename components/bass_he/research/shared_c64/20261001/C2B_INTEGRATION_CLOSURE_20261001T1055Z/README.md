# C2b frozen-state integration closure

Paper-derived independent implementation; not the authors' ARSENY code.

Start with RESEARCH_REPORT_KO.md, CONTRACT.json and NEXT_HANDOFF_KO.md. Scientific result: SCOPED_FROZEN_STATE_INTEGRATION_CLOSED; zero new eigensolves. This closes only the registered frozen-state integration dependency. Full C2 and physical promotion remain on hold.

Public Git content contains source code, mathematical derivations, exact contracts, selected audit evidence and independent review. The complete private archive additionally contains immutable frozen state NPZ files, all per-task inputs/results/logs, both execution source snapshots and private provenance. Attached source PDFs are neither included nor redistributed publicly.

Execution evidence distinguishes the interrupted initial launch (resource preflight noncompliance), its verified35-result subset, and the fresh preflight-approved20-result remainder. Never label the original55-task batch as wholly completed. The optional serial replay was rejected before launch. Existing parent evidence and failure records are preserved.

Native builds: run native/build_prolate.py and native/build_inner.py with the intended Fortran compiler. Build mode strict uses binary64, -O3, OpenMP, no-fast-math and no FMA contraction. Archives carry the tested local binaries/manifests; another host must rebuild and validate compatibility rather than assume binary portability. Explicit native selection fails on source/binary/ABI mismatch and does not fall back silently.

For a newly authorized batch, code/launch_ncp.py emits a validated OpenMPI command or executes it with --execute only after resource checks. It defaults to core binding. provenance/run_validated_local.py is a prepared local sandbox helper with a recorded no-binding exception and launch gating; it has not executed a successful scientific replay in this node. Source identities in recorded runs precede postprocessing/replay-manifest additions; use provenance/*CODE_SNAPSHOT.zip for exact source recovery. Do not overwrite recorded output directories.

Local upload receipts are produced after this immutable archive is finalized and are stored externally to avoid a self-referential hash. Provider acknowledgment and metadata checks are not provider restore tests.
