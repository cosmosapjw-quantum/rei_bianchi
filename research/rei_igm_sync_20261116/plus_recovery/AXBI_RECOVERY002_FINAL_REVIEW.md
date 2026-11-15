# AXBI recovery 002 final independent review

PASS_SCOPED_PREPARATION_AND_ONE_START_LAUNCHER. This review is independent of the author but not blind. The reviewer did not compile or execute the native solver.

The Rust/source/counter findings are in AXBI_RECOVERY002_RUST_REVIEW.md. Since that snapshot the author corrected its nonblocking interrupted-checkpoint wording. Final wrapper SHA256 is 3e5d3c9e91cad6b2a5dfcd292ffad730622806bdcf8dfa93598c7c3d0285f4e5; final launcher SHA256 is 26c262bd75ebd4f96c29945be8d2edddfd4aa272259c85053bdd4f08f0dd7971. Allocation SHA256 remains 3d3815257c4258621c6e25480b3935cb4cccba838a44aefc49f4d9bcdad1f72f.

Two launcher findings were corrected: --output now must resolve to a strict descendant of the isolated stage, and the manifest binds the launcher's own bytes. Seven independently written tests passed in 0.007 seconds: exact bundle identity, changed-launcher rejection, original-owner output rejection, original-owner stage rejection, default output containment, existing-lock rejection before preflight, and one-start/receipt/external-cap behavior. Native process creation was mocked; the test observed exactly one mocked Popen across two execute requests and verified all cap arguments and the unadmitted terminal receipt.

The launcher retains a nonblocking flock for the selected stage, reserves the start with exclusive file creation before Popen, refuses reused raw/output paths, pins one CPU, and applies 2699-second timeout plus one-second kill grace, 2700-second CPU cap and 2-GiB address-space cap. Native wall is separately 2695 seconds beyond the saved cumulative checkpoint wall. The original numerical source enforces attempt and RHS counters before increment. No automatic retry occurs.

Output semantics are explicit: native source enforces the 1920-MiB aggregate scientific cap; prlimit fsize is a per-file limit. The terminal receipt counts scientific and raw launcher bytes together and reports whether they fit the 2048-MiB allocation. The fixed native wrapper has no per-step stdout stream; its diagnostics and /usr/bin/time output use the reserved launcher allowance. The terminal total check is not described as a live filesystem quota.

Actual preparation/build and native --mode check remain execution obligations. A science launch is admissible only after their successful pinned receipts and under the existing exactly-one-start allocation. This review is not a new accuracy certificate, full-history completion, or AX11/AX12 admission.
