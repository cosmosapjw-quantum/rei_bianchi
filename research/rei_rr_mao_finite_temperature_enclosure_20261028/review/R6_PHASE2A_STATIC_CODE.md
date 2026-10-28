# R6 phase two A: static implementation findings before test-source contrast

Unit: `rei_rr_mao_finite_temperature_enclosure_20261028`  
Actual reviewer task: `/root/rr_mao_native_reviewer`  
Host observation retained from phase one: `0e9a46d15332`, Linux 6.18.55 x86_64.

## Boundary and conclusion

The phase-one mathematical report remains frozen at SHA256 `9349123bcf8302c19f228425070e1a8a3be1cad342a82ee8de4ee9da82216cb8`. Its final ledger remains frozen at `46b4149f0b8d7856b3aadbe3e92c5d1c8979a365c955e545c8a87f8fdc0fb5b2`. The prior root-observed ledger version was recovered by deleting only the known final metadata paragraph and its blank separator; its hash exactly matches `472c30a107046288e2f14f48881fd6bc5575d67fb90727bf8f1407012fbf77d6`, and its bytes are preserved in `R6_PHASE1_READ_LEDGER_ROOT_SNAPSHOT.md`.

After that seal, I read the actual new core implementation and inherited arithmetic in full. I have not yet read new test source, runners, wrappers, figures, CAS request/return files, or unit numerical output. Only the parent's post-seal metadata about a failed CAS tool call has been exposed: internal error -32603 and no scientific result. It provides no algebraic verdict.

The implementation follows the reviewed derivative and range equations. However, a concrete valid-input path can fail under the inherited subnormal traps: unconditional predecessor/successor expansion of the exact logarithmic value zero creates a minimum subnormal, which the Taylor linear term then multiplies by a nonzero small derivative. This prevents the implementation from fulfilling its all-admitted-decimal, finite-step contract. This finding is deduced from source and standard arithmetic semantics, not observed in an executed run.

C9 remains pending actual execution and the subsequent evidence review. This document preserves the static implementation findings before test-source contrast.

## F-CODE-1: exact ln(1) expansion can reject a valid tiny nonzero step

### Sources and path

- New implementation: `code/rr_mao_enclosure.py`, original reviewed SHA256 `1ecd1459f06853069162902ea839e9a513c1f807c68c0267b690cfb5323b7f09`.
- Inherited arithmetic: `deps/dr_interval_original.py`, SHA256 `be32fe17982ec9d1e9a6d506e37296d11cbe39fd6bc66690e6563ee62e2fb59c`.
- Inherited arithmetic lines 29–31 set `Emin=-999999` and enable `Underflow` and `Subnormal` traps.
- Inherited arithmetic lines 86–92 expand every transcendental lower/upper result using `next_minus` and `next_plus`, including exact `ln(1)=0`.
- New implementation lines 153–156 compute `h=(point/center).transcend('ln')` and return an enclosure containing the product `d0*h`.

### Concrete exact admitted input

Use precision 60, key `1:1`, quantity `alpha`, anchor `100`, domain `[100,101]`, and the exact decimal target `100 + 10^-100`. The following source expression specifies its finite decimal string unambiguously:

```python
target = "100." + "0" * 99 + "1"
model.taylor("1:1", "100", target, ("100", "101"), "alpha")
```

This code is a reproduction specification and was not executed by this reviewer. All inputs are admitted by the declared contract. In particular, target differs exactly from the anchor, so the exact zero-step branch does not apply.

### Analytic failure trace

1. The exact target/anchor ratio is `1 + 10^-102`. The reciprocal of the anchor is exactly `0.01` in Decimal. At precision 60, the directed lower endpoint of their product is exactly 1; the directed upper endpoint is the next precision-60 decimal above 1.
2. The inherited logarithm lower evaluation is exactly `ln(1)=0`. The unconditional `next_minus` changes this to the least negative representable subnormal. With the configured precision and exponent range, its value is `-10^-1000058`, since `Etiny=Emin-prec+1`.
3. The RR first-derivative enclosure at the 100 K anchor has nonzero negative endpoints of magnitude far below 1. For the actual hydrogen row, `C=0`, `-3/2<r_1<-1/2`, and alpha is much smaller than 1 in the declared units; the precision-60 outward point calculation is separated from the threshold 1 by many orders of magnitude.
4. The interval product `d0*h` therefore includes a scalar endpoint product of that minimum subnormal with a nonzero factor of magnitude less than 1. The exact product is nonzero and smaller than the minimum representable subnormal. Directed scalar multiplication consequently signals underflow/subnormal; the configured traps raise instead of returning the Taylor enclosure.

The quadratic radius computation does not prevent this path. It uses the magnitude of the other h endpoint, which is of ordinary precision-scale size, and then the failing linear product is evaluated. The mathematical Taylor theorem remains true. The implementation refusal is caused by its arithmetic treatment of an exact endpoint zero that did not require widening.

### Effect and minimal repair

The claim “returns an enclosure for every admitted exact-decimal anchor/target in every closed domain interval” is not established by the current implementation. A legitimate extremely small nonzero step can be rejected. This is an implementation/primitive issue, not a counterexample to R5's theorem.

The minimal scope-preserving repair is an interval natural-log primitive that keeps the bound exactly zero whenever the corresponding input endpoint is exactly 1, while retaining outward adjacent rounding for other endpoint values. Use it wherever the new implementation forms logarithm intervals, including log-temperature h. The pinned inherited file can remain unchanged if the new layer supplies and documents this primitive. Any alternative repair must explicitly justify its subnormal arithmetic behavior; a zero-step tolerance would change the exact-input contract and is not an equivalent repair.

Add a discriminating finite-decimal tiny-step record to the authorized bounded test run after source repair. Also cover the opposite sign and distinguish exact equality from a nonzero step smaller than the working relative precision. These are proposed checks following this preserved source finding, not executed results.

## Other static findings and open interface question

### Supported formula paths

The actual code retains `bp=correction*z` and `bpp=bp*(z-1)`, the full `bp*(p-q)` term in r2, the Mao `c0*square(ell)` term, both U and V contributions, and the correct m2 signs. The loss factor includes T, and `w=1+r1+m1` is used in both derivatives. Alpha's finite range is assembled from the decreasing endpoint images after an exact rational actual-row monotonicity certificate. The zero-crossing square primitive uses the correct interval-square range structure with directed scalar multiplication. No equation mismatch was found in these paths.

Input decoding preserves decimal-string values and exact float images. Boolean and complex inputs fail the inherited exact-type check; nonfinite values fail its finite check. Reversed/domain-exterior temperatures are rejected. Exact equality in the Taylor branch compares exact decoded values, not a tolerance.

The cache keys contain all coefficient tuples, the three conversion constants, both exact temperature endpoints, and the numerical context settings that affect values and traps. Cached payloads are immutable Decimal endpoint pairs; returned Interval wrappers are fresh. The omitted context `capitals` setting changes formatting rather than numerical value, so its omission does not supply a numeric stale-cache counterexample. No cache failure is asserted.

### Standalone output provenance question

R5 requires returned numeric records to retain source identity and scope. The standalone `range` and derivative methods return Interval/Decimal values, and the inherited `wire()` gives only `lo` and `hi`; the Taylor dictionary itself does not carry source identity, key, quantity, domain, units, or represented-real scope. A later saved-record wrapper may supply that context. Since wrappers have not yet been read, this is an open interface-contract question rather than a conclusion that the final saved deliverable loses provenance.

After test/runner contrast, either demonstrate the complete record envelope that carries this information or explicitly document that the core numerical API is internal and the provenance-bearing wrapper is the contracted return format. No numerical equation change is implied by this question.

## Standard-library semantics consulted

I consulted the official Python Decimal documentation read-only at [https://docs.python.org/3/library/decimal.html](https://docs.python.org/3/library/decimal.html). The retrieved page identified itself as Python 3.15.2 documentation; I did not infer that this is the installed interpreter version. The documented exact conversion, directed modes, adjacent-number operations, and trapped signals support the static arithmetic analysis. Its exp/ln descriptions support the predecessor/successor enclosure strategy away from problematic exact-zero endpoints. Its power documentation has a weaker C implementation guarantee, but the new implementation does not use Decimal power for the RR real exponent.

Only this standard-library source was consulted after the phase-one seal. Its numerical documentation examples are not results for this scientific unit. No runtime interpreter version, installed libmpdec behavior, or numerical operation was measured by this reviewer.

## Exact phase-two-A read ledger

| Resource | Semantic content read | Identity/disposition |
|---|---|---|
| `/workspace/scratch/cc0531120bc9/rei_post_dr_continuation_20261028/unit/code/rr_mao_enclosure.py` | Lines 1–156, entire original implementation | SHA256 `1ecd1459f06853069162902ea839e9a513c1f807c68c0267b690cfb5323b7f09`; read as text only. |
| `/workspace/scratch/cc0531120bc9/rei_post_dr_continuation_20261028/unit/deps/dr_interval_original.py` | Lines 1–264, entire inherited implementation | SHA256 `be32fe17982ec9d1e9a6d506e37296d11cbe39fd6bc66690e6563ee62e2fb59c`; unused DR class methods were exposed by the full read but were not run. |
| `https://docs.python.org/3/library/decimal.html` | Tool-returned initial text through line 466; returned find excerpts concerning sqrt, next_minus/next_plus, power rounding, context limits/modes/signals and libmpdec | Official documentation only. Requested patterns: `sqrt(context`, `next_minus`, `almost always correctly rounded`, `sqrt(x`. No code examples were executed. |
| Final phase-one ledger | Mechanical copy transformation only, deleting the single known final paragraph and separator | Recovered prior root snapshot hashes exactly to `472c30a107046288e2f14f48881fd6bc5575d67fb90727bf8f1407012fbf77d6`. No scientific source was added by the recovery. |
| New tests, `run_once.py`, `execute_bounded.py`, `plot_saved.py`, `PREPARED_IDENTITIES.json` | Not yet read | Their paths were disclosed, but contents remain outside this stage. |
| `CAS_ACTUAL_RETURN.json`, CAS reservation, unit numeric/figure returns | Not read | Parent supplied failure metadata only. No mathematical result was inferred. |

Mechanical source hashing and report writing are the only local executions in this stage. No scientific execution, CAS call, source import, test run, plot, or external write occurred. Unmeasured review/model/tool/network overhead remains unknown, not zero.
