# Shared DR dependency: narrow static scope addendum

Reviewer task: `/root/rr_mao_native_reviewer`  
Related preserved finding: F-CODE-1 in `R6_PHASE2A_STATIC_CODE.md`.  
Review type: static source reasoning only; no DR suite, import, CAS, oracle, IVP, or plotting execution.

## Conclusion

The same exact-logarithm endpoint issue affects the inherited `DRModel.taylor` path for a present DR channel. The current RR/Mao local `natural_log` repair does not modify that old DR path. Therefore the unmodified DR implementation cannot claim successful finite Taylor returns for every pair of arbitrarily close unequal admitted Decimal temperatures. Its mathematical Taylor theorem is unaffected; selected historical returned cases are not contradicted merely by this wider API counterexample.

I did not read the prior DR numerical result set or its stage-admission records. This addendum does not regrade those records or assert that any selected historical case failed. It identifies the exact shared dependency and the necessary limit on a general implementation-totality claim.

## Source identity and affected path

The already-read `deps/dr_interval_original.py` has SHA256 `be32fe17982ec9d1e9a6d506e37296d11cbe39fd6bc66690e6563ee62e2fb59c`. Mechanical hashing of the original path

`/workspace/scratch/cc0531120bc9/rei_approved_continuation_20261028/unit/code/dr_enclosure_cached.py`

returned the same SHA256. I did not re-read that original file; the identical inherited file had already been read completely in phase two A.

The relevant inherited source is:

- `Arithmetic` at lines 25–36: precision 60 by default, `Emin=-999999`, and enabled underflow/subnormal traps.
- `Interval.transcend` at lines 86–92: unconditional adjacent expansion of the logarithm endpoints.
- `DRModel.first_log_derivative` at lines 225–231: a nonzero derivative for the present `2:1` channel at 100 K.
- `DRModel.taylor` at lines 252–264: exact endpoint equality check followed by the logarithmic interval and `linear=f0+d0*h`.

## Concrete valid-input witness

Use DR key `2:1`, quantity alpha (`loss=False`), default precision 60, domain `[Decimal('100'),Decimal('101')]`, anchor `Decimal('100')`, and target `Decimal('100.' + '0'*99 + '1')`. In the old method's argument order, the unexecuted reproduction specification is

```python
model.taylor(
    "2:1", Decimal("100"), Decimal("101"), Decimal("100"),
    Decimal("100." + "0" * 99 + "1"), loss=False,
)
```

The target is exactly `100+10^-100`, so it is admitted and unequal to the anchor. The exact ratio is `1+10^-102`; the directed ratio lower endpoint is exactly 1. Expanding `ln(1)=0` downwards creates `-10^-1000058`. The final interval linear term multiplies it by a nonzero derivative endpoint whose magnitude is below 1, causing trapped subnormal/underflow behavior.

The `2:1` DR derivative is nonzero at this anchor: its positive leading resonance term is separated exponentially from the negative higher-energy contribution, with all actual energies far above `3T/2`. The endpoint magnitude is small, not an exact structural zero. Key `1:1` would be an unsuitable witness because the DR channel is structurally absent there and the derivative path returns zero.

This is an analytic source-path counterexample. It was not executed. The shared source's value-preserving real mathematics, positivity construction, and prior selected separated-step results are not themselves falsified by the arithmetic corner case.

## Scope action

Until the old DR path receives the same exact endpoint-identity repair or an explicitly narrower accepted interface, withdraw its blanket return guarantee for arbitrary near-equal unequal exact Decimal inputs. A statement restricted to selected returned cases and appropriately separated log steps can remain, with its actual evidence identified by the owner of those records. Do not represent the new RR-local helper as having repaired the unchanged DR implementation.

The existing pinned DR bytes remain unchanged. No additional DR execution was requested or performed by this reviewer, and no numerical acceptance is inferred from this static addendum.

## Read ledger addition

No new scientific source contents were read for this addendum. It reuses the phase-one coefficient JSON and the full phase-two-A inherited source read. The original old DR path was only hashed to establish byte identity. The parent supplied the affected-path question and prior-status context; the latter remains unverified by this reviewer. Mechanical hashing/writing overhead is unknown, not zero.
