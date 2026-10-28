# Source-bound DR preparation — NOT_RUN

All source is authored without importing/compiling/running the implementation, tests or plot. Exact coefficient bytes are copied under source/atomic_coefficients.json and match SHA25638397e6b560f463f09a5923eaa5902a24312e5246abc158694451c631cd4d6bc.

API: load_source(path) verifies bytes; parameter_images preserves float hex/exact numerator-denominator/exact decimal images; DRModel.range, positivity, first_log_derivative, second_bound and taylor implement D1–D4. Valid retained keys come from source rr keys; absent DR rows return structural zero; unknown keys reject. The conditional loss uses exact-image products, signed coefficients and the source-specific D2 lower bound. Decimal basic operations are directed; correctly-rounded HALF_EVEN transcendental endpoints are expanded with next_minus/next_plus. Underflow/subnormal traps prevent a false zero support certificate. Precision60; independent scalar oracle90.

One future command from unit root, only after root freezes the remaining allowance:

```bash
python -B -S code/run_once.py --execute-authorized
```

The worker records all requested interval/oracle/scalar/positivity/parameter-image/Taylor/rejection/precision outputs, not just method counts. The one selected unittest method covers30 row/interval/quantity ranges,36 Taylor cases, present-underflow/absence distinctions, signed-clipped controls, the interior kernel maximum,50/70 precision comparison and malformed-input rejections. H/RR/whole callback/old suite/IVP/CAS are not invoked.

Subsecond CPU cannot be expressed by Linux RLIMIT_CPU alone. The prepared Linux supervisor therefore reads worker /proc counters and kills at0.38CPU-s, leaving tick/poll margin toward the0.4CPU-s worker target; hard CPU1s is a backstop, wall10s, address-space256MiB. It preserves wait4 whole worker counters and separate supervisor prefix. This is a preparation target, not an observed runtime guarantee or permission. Root must reserve actual budget before invoking; if the selected suite exceeds it, preserve actual failure and stop without auto-retry.

Future output-only figure command:

```bash
timeout 10s prlimit --cpu=1:1 --as=268435456:268435456 -- python -B -S code/plot_saved.py --execute-authorized
```

The tiny stdlib SVG uses saved signed/clipped alpha values and saved Taylor residual/bound ratios. It imports no rate functions and executes no tests. Hard CPU1s plus external caller accounting fits the proposed<=1.5CPU-s presentation target, subject to actual frozen reservation. Actual SVG/raster inspection is still required; a filename is not visual acceptance.

Prior planning19.339367062/presentation58.083046308 and remaining0.660632938/1.916953692 are retained pending root's current reconciled budget freeze. No grant/reset/reopening/foreign transfer is inferred. Unknown overhead remains UNKNOWN_NOT_ZERO; main595.225063/600 NO_MORE_IVPs unchanged.
