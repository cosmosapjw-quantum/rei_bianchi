# Validation matrix

| Layer | Required evidence |
|---|---|
| Repository | baseline and final `scripts/verify_repo.py`, clean tree, `git fsck --full` |
| Unit/TDD | red and green logs for rate derivation, LP/Farkas, interval cone, two-mode theorem |
| Scientific | units, sign, limiting cases, endpoint and exact photon/H/He ledgers |
| Numerical | LP primal/dual/KKT, Farkas residual, interval certification, `dt/2,dt/4,dt/8` |
| Symbolic | Wolfram script plus executed plugin receipt when available; SymPy/Decimal fallback always |
| Independent | output validator that does not import production solver |
| Reproducibility | input hashes, manifests, SHA256SUMS, compact bundle, incremental git bundle |
| Remote | read-only probes recorded; no push claim |
