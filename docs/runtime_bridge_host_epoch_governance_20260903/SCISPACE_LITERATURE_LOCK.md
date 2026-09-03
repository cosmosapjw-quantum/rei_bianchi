# SciSpace methodology lock — successor-host governance

## Admitted sources

1. Peter Ivie and Douglas Thain, **PRUNE: A Preserving Run Environment for Reproducible Scientific Computing**, IEEE e-Science 2016, DOI `10.1109/eScience.2016.7870886`.
   Admitted for immutable derived-data lineage and explicit execution-environment binding.

2. Joseph Wonsil et al., **Reproducibility as a Service**, *Software: Practice and Experience* (2023), DOI `10.1002/spe.3202`.
   Admitted for the distinction between proactive preservation of an extant environment and retroactive recreation after that environment has been lost.

3. Andrew Youngdahl, Dai-Hai Ton-That and Tanu Malik, **SciInc: A Container Runtime for Incremental Recomputation**, IEEE e-Science 2019, DOI `10.1109/eScience.2019.00040`.
   Admitted for provenance-aware replay and change propagation across execution contexts.

4. Luis Oliveira et al., **Supporting Long-term Reproducible Software Execution**, ACM REP 2018, DOI `10.1145/3214239.3214245`.
   Admitted for the distinction between preserving binaries and preserving an independently re-creatable execution process.

5. Haiyan Meng et al., **Conducting reproducible research with Umbrella**, IEEE e-Science 2016, DOI `10.1109/eScience.2016.7870889`.
   Admitted for persistent, deployable environment specifications and archived environment inputs.

## Governance implication

The missing historical raw receipt must remain a historical identity, not be fabricated. A successor host may be admitted only through a new raw receipt that exactly matches the project-owned semantic toolchain lock. Historical attempt outcomes must live in durable append-only evidence rather than depend on an ephemeral `/tmp` file. A global create-only reservation must precede the host-local lease and native dispatch.

## Authority boundary

These papers do not own REI hashes, runtime semantics, Formula IDs, attempt budgets or scientific claims. They support the governance design only. No source here authorizes native execution, first-interval promotion or provider export.
