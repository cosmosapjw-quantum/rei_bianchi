# External source support and scope

Accessed 2026-10-12 UTC.

- Python 3.12 decimal documentation: https://docs.python.org/3.12/library/decimal.html . The Decimal.exp entry states correctly rounded ROUND_HALF_EVEN results, and the Context API documents the corresponding context methods. This supports the inherited directed-interval implementation's use of neighboring Decimal values around an exponential evaluation. It does not prove the application source, coefficient model, or physical assumptions. The actual runtime version remains the version recorded in execution receipts, not the documentation site's current patch number.
- NIST DLMF §3.5: https://dlmf.nist.gov/3.5 . Used as context for quadrature rules and derivative-dependent remainder contracts. The signed C2 midpoint bound in this work is derived explicitly in theory/THEORY_OPTIONS.md; no higher-derivative theorem is imported from a search snippet.
- BASS_HE AGENTS.md at immutable commit b35891fc2063f6621a91d52968e67c768fecf563 was read through the GitHub connector and matches the restored execution policy in the predecessor source tree. Its HPC reference is included as HPC_POLICY_KO.md, fetched at the same immutable commit from research/shared_c64/20261001/NCP64_NATIVE_MPI_20261001T0520Z/HPC_POLICY_KO.md.

The shared HPC policy concerns measured parallelism and preserved scientific semantics. Its real64 native-kernel examples do not authorize replacing the P60 outward interval lane by binary64. A native enclosure backend would require a separate mathematical and numerical parity argument. Actual physical-core topology, affinity/quota, memory, rank/thread layout and speedup have not been measured on a new NCP job in this loop. No hardware-utilization claim is inferred from a 64-core specification.
