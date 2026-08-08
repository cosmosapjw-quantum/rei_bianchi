# Verification design and results

The verification stack separates mathematical rank proof, conditional coherent-auditor numerics, and repository regression.

- exact SymPy/Wolfram determinant factorization: PASS;
- stage tests: `8 passed`;
- independent result replay: PASS;
- research harness validation: PASS;
- file-isolated repository suite: `61 files, 249 tests, 0 failures`;
- coherent training/withheld runs: all inherited hard gates pass in all three shape lanes.

A failed eight-chunk suite run is preserved separately: all implicated files passed in fresh interpreters, identifying cumulative runtime state rather than a scientific assertion failure.
