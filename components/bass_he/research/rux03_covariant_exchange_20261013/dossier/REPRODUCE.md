# Reproduce the accepted theory checks

## 1. Exact xAct input

The complete input sent to the Wolfram evaluator is
`evidence/XACT_COVARIANT_EXECUTED.wl`. It downloads the official xAct 1.3.0
archive to a temporary directory, verifies SHA256, loads xTensor, selects the
supported pure Wolfram xPerm backend, and evaluates the embedded program.
The readable embedded program is `derivations/XACT_COVARIANT_PROGRAM.wl`.
The final independent review compares that program to the exact string in the
executed wrapper.

In a licensed Wolfram installation with access to the official archive:

```bash
wolframscript -file evidence/XACT_COVARIANT_EXECUTED.wl
```

Expected scientific output: `tensor_check_count=24`, `scalar_check_count=5`,
all booleans True, all 24 tensor residuals `0`, `all_pass=true`.
The package archive hash is
`7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be`.

If an identical xAct installation is already available, the readable program
can be loaded after xTensor, with `$xpermQ=False`. Read the program only after
`Needs` so package function names resolve in the loaded xAct contexts. The
archived self-contained input is the actual execution evidence.

## 2. Independent geometry algebra

```bash
wolframscript -file evidence/geometry_exact.wl
```

Expected: `check_count=16`, all booleans True, `all_pass=true`.
This script uses exact rational/matrix algebra and differentiation, not xAct.
Its input is byte-identical to `derivations/GEOMETRY_EXACT_CHECK.wl`.

## 3. Inspect the existing results

The original tool responses are retained as JSON. Each accepted calculation
prints a JSON string; the parsed objects are the neighboring `*_RESULT.json`
files. `EXECUTION_RECORD.md` explains the assumptions supplied to xAct,
backend selection, actual failed attempts and counts. The initial smoke and
pre-metadata-correction runs are not extra scientific groups.

The symbolic calculations prove algebraic consequences of the stated
kinematics/constitutive closure. The written derivations justify those premises
and the transition to spatial flux divergence. Atomic fits and their previous
verification use REUSE_IDENTITY.json; rerunning them is unnecessary while those
inputs and conventions remain unchanged.

## 4. Current-source correspondence

`source_map/CURRENT_SOURCE.json` records exact Git heads/trees and source
hashes. `STATIC_INPUT_PARITY.json` records the selected initial NPZ hash and
the static 1,452-pair comparison. The raw NPZ and full primary-source PDFs are
not copied into this dossier. The source map contains their authoritative
locations and the scope of the comparison.

No native build, source RHS or history integration is required to reproduce
these theory checks. Follow CODING_CONTRACT_KO.md for the separate future
implementation verification at its actual source and runtime.
