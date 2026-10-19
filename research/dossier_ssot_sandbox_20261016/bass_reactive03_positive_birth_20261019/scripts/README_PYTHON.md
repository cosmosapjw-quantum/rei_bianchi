# Independent Python/CAS reproduction

The independent analyses use Python standard-library Decimal (precision 90 for
the scalar integrals and 80 for the second native science review). NumPy and
Matplotlib are needed only for the figure generator. No Wolfram installation is
required to reproduce the Python checks; the actual Wolfram expressions and
returned results are retained as a separate CAS record.

Copy the independent-theory scripts and rust_rule_probe.rs into a new analysis
directory before running scripts that write results beside themselves. Preserve
the archived evidence directory. Supply the actual package and toolchain paths:

    python3 /new/analysis/independent_birth_study.py
    python3 /new/analysis/compare_rust_rule.py \
      --candidate /package/crate/fitted_birth.rs \
      --toolchain /actual/rust-1.94.1-prefix
    python3 /new/analysis/frozen_source_restore_check.py \
      --input /package/evidence/frozen/AP_FROZEN_SOURCE_INPUTS.csv

The scalar source was formatted after the first independent derivation/probe.
The original report preserves that historical hash. The final formatted bytes,
SHA-256 d138643622ffa3399245db562331d0ff69874d81cb7251f533200c75b9c76a24,
were actually probed again; see evidence/independent_final_scalar.

The independent native auditor reads final CSV/receipt pairs and creates a new
report without changing data:

    python3 /package/evidence/independent_native/audit_native_outputs.py \
      /package/evidence/native --output /new/analysis/NATIVE_AUDIT.json
    python3 /package/evidence/independent_theory/review_native_science.py \
      /package/evidence/native /new/analysis/SCIENCE_REVIEW.json

The first tool recomputes ledgers from exported primitive quantities, not from
the driver's maxN/maxE diagnostics. The second separately analyzes contraction
and the limitations of the time/birth/spectrum sequence. Both preserve the
expected Cx(WorkLimit) zero-row outcome. They do not validate unexported species
populations or certify convergence of the full evolving solution.
