# SciSpace literature-role lock — successor Section-0 read-only preflight

## Admitted methodology

1. Peter Ivie and Douglas Thain, *PRUNE: A Preserving Run Environment for
   Reproducible Scientific Computing*, IEEE e-Science 2016,
   DOI `10.1109/eScience.2016.7870886`.

   Admitted for immutable task/environment provenance and append-only derived
   evidence.  It supports keeping historical failures while creating a new
   successor-host attestation.

2. Ludovic Courtès and Ricardo Wurmus, *Reproducible and User-Controlled
   Software Environments in HPC with Guix*, arXiv `1506.02822`.

   Admitted for exact software-environment description and redeployment.  It
   does not imply that two hosts have byte-identical context; the REI policy
   therefore requires a distinct raw successor receipt with exact semantic
   toolchain fields.

3. Akash Dhruv, Anshu Dubey, Lorena A. Barba, and Sandra Gesing, *Managing
   Software Provenance to Enhance Reproducibility in Computational Research*,
   Computing in Science & Engineering 25 (2023),
   DOI `10.1109/MCSE.2023.3314288`.

   Admitted for recording executable, dependency, configuration, and result
   provenance in HPC scientific workflows.

4. Luis Oliveira, David Wilkinson, Daniel Mosse, and Bruce R. Childers,
   *Supporting Long-term Reproducible Software Execution*,
   DOI `10.1145/3214239.3214245`.

   Admitted for the distinction between retaining binaries and preserving a
   complete, replayable execution process.

5. Ana Trisovic et al., *Provenance Tracking in the LHCb Software*,
   arXiv `1910.02863`, DOI `10.1109/MCSE.2020.2970625`.

   Admitted for embedding machine-readable provenance with outputs rather than
   relying on mutable external recollection.

## Consequence for this node

The methodology supports the following order:

```text
verify immutable package and release
→ inspect global state read-only
→ re-attest the successor toolchain under a new raw identity
→ audit the new receipt
→ stop before any execution lease
```

A read-only `404` is a time-local observation and is never authorization for a
single-use execution.  The atomic create-only lease remains a separate later
node.

## Authority boundary

These publications do not own REI bytes, hashes, Formula IDs, attempt budgets,
physics equations, numerical tolerances, or scientific claims.  They support
only the provenance and reproducibility design.  The exact Git objects and
project contracts remain the authority.
