# C3 manufactured local source probe

This is the finite implementation of the frozen C3 contract, under the selected
C3 design / C5 implementation / C6 targeted verification scope. It uses only
Python's standard library and the supplied 21-slot index/A/Z/q binding. All event
coefficients and endpoint declarations are **MANUFACTURED**.

`local_source.py` evaluates unary/binary event polynomials using positive-product
logs and exact-zero branches. The identical-reactant factorial stays in the
coefficient convention. Raw underflow retains a finite log rate; fixed-scale
sources and Jacobians are evaluated directly in log space. The Jacobian uses
reduced integer exponents at zero rather than dividing a rate by abundance.
Signed accumulated contributions use `math.fsum`. Applicability is independent
of abundance: SUPPORT_ZERO and ABSENT remain distinct; UNRESOLVED raises an
explicit input exception. Exact integer event bookkeeping rejects baryon loss.

`run_probe.py` defines the frozen finite fixtures, an independent direct-product
Decimal oracle at precision 100, analytic endpoint and bookkeeping references,
the moderate central-difference control, both required failure-mechanism negative
controls, and the 17-to-21 projection with retained Li6 inventory deficit. No
normalization is applied to the projection. Near-unity projection subtraction is
checked within four binary64 ulps at unity, with its exact Decimal deficit also
checked. Finite differences use only positive moderate reactant coordinates;
their tolerance covers subtraction roundoff and polynomial truncation, and does
not validate boundary, underflow, off-grid rate, or trajectory behavior.

One scientific invocation is authorized, bounded by 30 seconds wall/CPU and
256 MiB address space. No historical diagnostic, rate builder, integration,
installation, NCP operation, production edit, or Git mutation is performed.
RESULT.json preserves fixture inputs, outputs, reference values, errors,
tolerances, statuses and controls; EXECUTION.json records actual timing, exit,
Python identity and source/input hashes. stdout.txt and stderr.txt are raw.
Substantive failure stops for parent interpretation without automatic rerun.

Requested execution model: gpt-6.1-sol. Actual runtime model identity is not
exposed by the available tools. The current skill read was
physmath-research-loop 1.3.0, POLICY_INTEGRATION plus C3/C5/C6 guidance.

A local PASS supports the manufactured representation controls only. Root owns
the independent Astra decision and any publication. Physical branch providers,
off-grid coefficients, thermal/fast dependencies, and coupled production remain
outside this implementation.

Observed execution: one invocation returned exit code 0 and local test status
PASS for seven finite fixtures, nine applicability controls and five additional
controls. EXECUTION.json records 0.100463153 seconds measured wall time,
0.094889168 seconds CPU time and 19,968 KiB maximum RSS. Raw stderr is empty.
No rerun occurred. This reports the prescribed runner's outcome; independent
scientific admission remains the controller's responsibility.

Publication transport stores the exact raw RESULT.json as deterministic gzip
(mtime 0). RESULT_SUMMARY.json contains exact counts, recorded maximum errors,
scope and original/compressed hashes and lengths. Binary publication encoding
for RESULT.json.gz is base64. Decode the raw evidence with:

```sh
gzip -dc RESULT.json.gz > RESULT.json
```

Decompression was verified byte-identical to the original. This packaging
step read existing evidence and did not rerun the scientific probe.
