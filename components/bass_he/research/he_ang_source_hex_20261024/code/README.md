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

The commands below were the original execution requests. Their actual results
and the approved A1 retry are recorded below; direct replay is not authorized.
Execution used the owner's bounded accounting wrappers.

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

## Actual execution state and A1 dialect amendment

`POLICY_AMENDMENT_A1.json` adds explicit `--dialect hex-lines` for the published
newline-oriented dump. Source `hex-db/src/db.cpp::hex_import_` executes each
getline record even without a semicolon; the bounded diagnostic observed 937 LF
and zero semicolons in the first 65,536 decoded bytes. The default semicolon
reader, 128 MiB total decoded cap and 8 MiB statement/line cap remain unchanged.
The explicit dialect accepts one numeric/BLOB literal INSERT row per physical
line with an optional final semicolon, blank/full-line `#`/`--` comments, source
BEGIN/COMMIT/END transaction markers, and opaque one-line known-table CREATE TABLE
records for counting only. Multiline records and multiple VALUES/statements fail.

Observed receipts, including failures, are preserved in `evidence/execution/`:

| Invocation | Observed result | CPU seconds | Wall seconds |
|---|---|---:|---:|
| Original new-unit synthetic controls | 15 tests passed | 0.066586 | 0.116157034 |
| Original actual catalogue | Failed at 8 MiB statement buffer | 0.237953 | 0.267004024 |
| Limited input-format diagnostic | Completed; prefix only | 0.030270 | 0.034098648 |
| A1 line-dialect controls | 5 tests passed on executed source identity | 0.057385 | 0.065872864 |
| A1 actual catalogue retry | SIGKILL (`rc=-9`); empty output | 8.349479 | 8.393597169 |
| A2 prefix old/new literal parsing profile | Identical output on 3,627 completed INSERT rows | 0.153919 | 0.166433897 |
| A2 focused grammar controls | 3 tests passed | 0.058323 | 0.066195771 |
| A2 actual catalogue retry | **Completed with pinned input identity; ionf rows 0** | 8.144439 | 8.193171290 |
| Synthetic two-panel plot | Completed; manufactured coefficients only | 1.270026 | 1.320363137 |
| A3 exact existing word-boundary test method | Passed after whitespace/EOF guard correction | 0.065932 | 0.116505090 |
| **Final same-unit cumulative** | **All failed and successful attempts retained** | **18.434312** | **18.739398924** |

The first two catalogue attempts failed, and availability was unknown at that
point. Root's explicit A2 amendment authorized one cost repair and a third
catalogue attempt under the same cumulative 20 CPU/60 wall-second budget. A2
replaced repeated token validation on all-numeric rows with one compiled
whole-row match using the identical numeric grammar. The BLOB/NULL fallback,
schema count/order, initial-integer and finite-H1-energy guards were preserved.
On the single authorized 262,144-byte completed-line prefix, old/new parse
outputs were exactly equal; profiled old/new CPU times were 0.043939912 and
0.035929797 seconds. This prefix comparison makes no availability inference.

The completed A2 catalogue found **948,557 tmat rows and zero ionf rows**. H1
initial `(1,0,0)` accounts for **86,457 tmat rows**, with literal incident-energy
range **1e-7 through 0.9374 Ry**. These are source catalogue counts/ranges, not
numerical scattering or ionization predictions. The final raw-input status is
**SOURCE_INPUT_PENDING** for H1 ionization, because the inspected dataset contains
no ionf payload. This does not mean that ionization amplitude or cross section is
zero. No physical BLOB ABI was inferred or provider value promoted.

Input identity from the successful full stream:

| Stream | Bytes | SHA256 |
|---|---:|---|
| Compressed XZ | 7,880,672 | `afa8d83ada688ecf91c40340da669e204885ec5c52d04fc55b48837b52135101` |
| Uncompressed newline SQL | 69,441,007 | `82def29890bba56bb31f31524dcbea58bd0a0f5b39441ee7b6594bd28fc54896` |

`figures/synthetic_tail.png` was generated once and visually inspected. It is
explicitly labelled as a manufactured amplitude and contains no provider values.
No previous scientific suite was replayed. The final invocation counts are
algebra **4** (the fourth is the root-authorized A3 single-method regression),
catalogue **3** (two failures retained), diagnostic **2**, plot **1**.

CPU RLIMIT soft/hard was configured to 8 seconds for the catalogue attempts, but
measured CPU was 8.349479 seconds for A1's SIGKILL and 8.144439 seconds for A2's
successful exit. The actual measured overshoot is preserved; configured limits
must not be described as proof that every child consumed at most 8 CPU seconds.
The same-unit cumulative cost stayed below 20 CPU and 60 wall seconds. A3 used a
1 CPU-second limit and consumed 0.065932 seconds. The failed A1 SIGKILL is
consistent with CPU-limit termination, but its exact kernel cause is unconfirmed.

The executed A1 core has SHA256
`012809cd4d2141c9e505dfd8a43aa0fc0d754d79d980403384c3a44fa54da0f7`;
its exact source is preserved at
`evidence/execution/A1_before/retry_executed_hex_intake.py`.
Independent review subsequently identified malformed INSERT prefixes that could
bypass the literal parser. The final one-line guard requires `INSERT` followed by
whitespace or EOF. Under explicit A3 authorization, exactly the existing method
`A2LiteralTests.test_schema_integer_finite_and_word_boundary_gates` ran once and
passed, including `INSERTfoo`, `INSERT(foo)`, `INSERT;` and comment-adjacent
prefixes. The final core SHA256 is
`3552737bcd6cd488756f3ae5c70d1e28882bb6163d8fc4f48606689c6ef6f93e`.
The successful catalogue used the earlier A2 core SHA256
`2196134dbfd7b757eaef3a83618af86c66332a550d9008166d13ac88e8b4935d`,
preserved at `evidence/execution/A1_before/pre_A3_hex_intake.py`.
The final guard is a fail-closed lexical restriction; the full catalogue and plot
were not replayed after it. Exact source identities, before/after diffs and raw
receipts preserve the executed versions. `evidence/execution/RESOURCE_LEDGER.json`
is the aggregate accounting authority and links the unchanged historical ledgers.
