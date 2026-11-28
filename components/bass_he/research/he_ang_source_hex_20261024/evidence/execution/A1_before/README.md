# Hex intake implementation usage

This new unit reads generated source-format SQL without executing SQL.
`hex_intake.py` uses only the Python standard library. Its run-scanning lexer
supports generated numeric/BLOB VALUES statements, quoted text/identifiers,
semicolons, `#`/`--` line comments and `/* */` comments. Unsupported INSERT
syntax or source field order fails closed. This is not a general SQL engine.
Ordinary text, quoted content and comments are consumed in bulk through compiled
searches and `bytes.find`; source bytes are not visited one at a time in Python.
The decompressed input cap is 128 MiB and the individual statement cap is 8 MiB.
The catalogue CLI applies 256 MiB address-space and 8 CPU-second limits; the owner
wrapper additionally enforces 20 wall seconds and the cumulative unit ledger.
No previous scientific suite is a dependency.

Proposed commands, **not executed by the implementation author**, from the unit
directory after owner preflight and using the owner's accounting wrapper:

```sh
python -B tests/test_hex_intake.py
python -B code/hex_intake.py /workspace/scratch/47d8070ffff8/source_intake/Hex-170210.sql.xz
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MPLCONFIGDIR=/tmp/he_hex_mpl python -B code/plot_synthetic_tail.py figures/synthetic_tail.png
```

All test rows and amplitudes are manufactured controls. An independent forward
rational recurrence checks the Clenshaw convention and exact coefficient
truncation bound. SQL fixtures reproduce upstream writer shapes using synthetic
values. No physical provider values are inferred, including in the plot.

## Generic decoder versus H1 catalogue

`decode_ionf_row(row, endian='little', layout='binary64-real-imag')` accepts the
generic source schema `ni,li,mi,L,S,Ei,l1,l2,cheb`; explicit `'big'` is also
supported. Endianness and complex layout must be external provenance assertions,
not guesses based on plausible values. This generic utility can decode valid
non-H1 initial states; it does not admit them as H1 physical evidence.

The catalogue's availability decision is specifically for initial
`(ni,li,mi)=(1,0,0)`. It separately counts all ionf rows and H1 rows. Absent H1
ionf yields `SOURCE_INPUT_PENDING`, even when some non-H1 ionf exists. Absence
never becomes a zero cross section. Presence remains
`RAW_H1_IONF_PRESENT_ABI_UNCONFIRMED`: the catalogue does not decode or promote
physical BLOBs. Energy ranges are literal incident `Ei` values in Ry from the
matching raw rows, not an assertion of coverage or accuracy.

Incident `Ei` must exceed `1/ni²` in the decoder. The upstream polynomial domain
is `k1 ∈ [0,sqrt(Ei-1/ni²)]`; `normalized_coordinate(k1)` maps it to `x ∈ [0,1]`.
This concerns only the polynomial argument. **The radial-division convention
between the upstream ionf and tdcs consumers remains unresolved.** In particular,
ionf.cpp evaluates the polynomial and divides by `(k1*k2)^2`; this unit does not
assume that expression reconciles the tdcs construction. It applies no radial
division to decoded coefficients and provides no physical cross section,
complete angular distribution, finite-proton-mass correction, or recoil model.
Any physical amplitude or TDCS promotion must first resolve that source mismatch.

## Exact represented-coefficient remainder

`evaluate(C,x)` retains all coefficients by default and implements
`C0/2 + sum_{j=1}^{N-1} Cj*Tj(2*x-1)` with floating Clenshaw arithmetic.
`exact_tail(C,m)` returns the exact rational number
`sum_{j=m}^{N-1} (|Re Cj|+|Im Cj|)` for `1 <= m <= N`. Finite represented
binary64 components are converted to exact fractions. On this domain this bounds
coefficient omission alone; it does not certify floating evaluation roundoff or
physical uncertainty. `select_terms(C,absolute_tolerance)` requires an explicit
nonnegative exact/rational or binary64 tolerance and examines the entire omitted
suffix. There is no implicit `1e-8` cutoff. With `C=[2,0,2]`, retaining two
coefficients gives `1` at `x=.5`, while the full series is `-1`: an interior small
coefficient cannot establish a small remaining tail.
