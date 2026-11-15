# AXBI recovery 002: independent read-only Rust/allocation review

Reviewer: source_thermal agent, independent of geometry_solver author. This is not a blind review: the reviewer received the author's scope and candidate paths. No continuation or native solver was executed.

Verdict at this stage: PASS_SCOPED_RUST_AND_ALLOCATION; external launcher and native preflight remain to be checked before execution.

Reviewed wrapper SHA256 36a6bd889db2c76dca259057c6732237975836a59c8eaa19b966a67f3cfbbd6a and allocation SHA256 3d3815257c4258621c6e25480b3935cb4cccba838a44aefc49f4d9bcdad1f72f. Both match BUNDLE_MANIFEST.json. Actual checkpoint SHA256 7af4071c8267f349c0a1d106759aa39d5fa47423ecbb76137692d31d1f5f82a2 and original source corpus SHA256 d7676b9309ac9b084499bbf599e803baecd661c80765489be45839ef5a7cf185 match allocation and wrapper. Python byte-hash and counter checks executed successfully (PYTHON_PASS).

The six checkpoint counters are accepted=240480, attempts=721494, rejects=18, consecutive_rejects=0, RHS=5050500, comparisons=240498. Scale factor is 0.107527522059568434 and saved elapsed wall is 7347.101283315 s. The wrapper restores these without resetting them. Native ceiling minus checkpoint equals exactly 90000 accepted, 360000 attempts, 3000000 RHS and 2695 native wall seconds. The original Driver::adaptive_step checks tentative-start counters before each of its three trial starts, and Driver::evaluate checks the RHS counter before increment, so these caps do not rely only on a loop-top check.

The original Driver::read_checkpoint also verifies shape, photon count, initial-energy reference, proper clock and background state, then validates the restored state. compiled_identity is the original complete physics/configuration source corpus; the new wrapper's source/binary identity is recorded separately. The wrapper changes only resource ceilings, exact resume identity, segment label and preflight mode. The original numerical kernel, source fields and scientific tolerances remain unchanged.

The interrupted predecessor has no terminal RETURN; this absence is explicitly recorded instead of inventing a successful terminal receipt. The 47 later history rows are excluded from resume state and their cost is not erased: allocation preserves the full old reservation and marks unknown actual cost, with lower orphan debit separately. These choices prevent treating orphan rows as a checkpoint or new unspent budget.

The wrapper refuses an existing output path and create_dir protects the selected output directory. A global one-start marker and external wall/CPU/memory/output limits are responsibilities of the pending launcher. The native --mode check path performs identity and state validation without starting run_segment. The operational claim remains a bounded original baseline continuation, not AX11/AX12 convergence or resolved signed response. External launcher verification and actual native preflight must be recorded separately.

Nonblocking wording issue: metadata calls the duplicated first row a predecessor 'terminal checkpoint'; here it is the predecessor's last durable interrupted checkpoint. The exact hash and state checks make the operational meaning unambiguous; final reporting should use 'last durable checkpoint'.
