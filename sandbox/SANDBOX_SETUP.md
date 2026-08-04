# Sandbox setup

Tested baseline: Linux, Python 3.12+; current artifact runtime used Python 3.13.5, NumPy 2.3.5, SciPy 1.17.0, pandas, SymPy, mpmath, and optional JAX 0.9.0.1.

```bash
./scripts/bootstrap_sandbox.sh
source .venv/bin/activate
python scripts/verify_repo.py
```

Environment variables for authenticated GitHub operations:

```bash
export REI_BIANCHI_REMOTE=https://github.com/cosmosapjw-quantum/rei_bianchi.git
export REC_BIANCHI_REMOTE=https://github.com/cosmosapjw-quantum/rec_bianchi.git
# Use a credential helper, gh auth, or SSH agent. Do not commit tokens.
```

Wolfram:

```bash
command -v wolframscript || command -v WolframKernel
```

If unavailable, keep the `.wl` reproduction script and mark the native crosscheck pending. A symbolic fallback may audit exact identities but must not be reported as native Wolfram execution.

Large artifacts on `archive/full-history` are chunked. Reassemble with:

```bash
python scripts/reassemble_artifact.py artifacts/archive/<name>.parts.json /target/directory
```
