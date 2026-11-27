# HE18 C3: warm P01 second-cell numerical interval research

Use verified private input ZIPs and public code. The scripts create a private runtime in a **new path**; no native rei_bianchi producer is changed or run. Python dependency: NumPy, mpmath (the originally used `iv` interval primitives). Scientific scope is an exact-real discrete warm P01 source; the consumed interval library is a trusted dependency, not formally independently verified. Do not import cold AXBI rates.

## Commands

```bash
python checks/stage_inputs.py --c1 /path/BASS_HE_HE18_C1_SECOND_CELL_AND_AXBI_20261015_v1.zip \
 --r5 /path/BASS_HE_HE17_R5_FIRST_CELL_CERTIFICATE_20261014_v1.zip \
 --r8 /path/BASS_HE_HE17_R8_ADOPTION_INTEGRATION_20261014_v1.zip \
 --output /tmp/HE18_C3_RUNTIME_FRESH
cd /tmp/HE18_C3_RUNTIME_FRESH
PYTHONPATH=src python src/run_evaluations.py mid
PYTHONPATH=src python src/run_evaluations.py whole
PYTHONPATH=src python src/assemble_certificate.py
python checks/verify_c3.py
python checks/propagate_endpoint.py
```

Typical 12-core CPU task: each of the first two interval evaluations ~12 seconds in our sandbox; assembly ~7 seconds. Do not infer identical runtime on the user's Ubuntu. The output path must be new to preserve the original. The staging tool pins all 3 archived ZIP hashes, private P01 state/emissivity/source, R7 incoming memory and original R8 first-cell result, and calculates second-cell endpoint slopes by two RHS calls only.

`results/CERTIFICATE.json` contains numerical rational enclosures; `results/RESIDUAL_COUPLING.json` contains all 2904 source-node bounds; `results/TWO_CELL_VALIDATION.json` contains exact rational two-cell tau/P; `results/SECOND_ENDPOINT_MEMORY.json` contains the complete photon error vector to be used in the NEXT physical cell, not the old fixed-B four-component compression. End-to-end outputs were independently reproduced from a new private directory. Do not claim `full_history_tau` or `observer_foreground` from the first two cells.
