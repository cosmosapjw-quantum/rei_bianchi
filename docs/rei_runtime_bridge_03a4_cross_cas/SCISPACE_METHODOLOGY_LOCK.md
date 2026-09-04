# SciSpace methodology lock — successor-host preflight and provenance

Search question: which peer-reviewed methods support exact environment
re-attestation, immutable execution provenance, and separation of read-only
preflight from an irreversible one-shot scientific computation?

Relevant methods returned by the literature search:

1. Courtès, *Reproducing software environments: a prerequisite for
   reproducible research* (2022), arXiv `2112.04384`.
   - Source archival alone is insufficient; the executable environment must be
     redeployable and identified.

2. Ivie and Thain, *PRUNE: A Preserving Run Environment for Reproducible
   Scientific Computing* (IEEE e-Science 2016), DOI
   `10.1109/ESCIENCE.2016.7870886`.
   - A task is coupled to a strictly defined environment and produces an
     immutable provenance tree.

3. Oliveira et al., *Supporting Long-term Reproducible Software Execution*
   (2018), DOI `10.1145/3214239.3214245`.
   - Preserving a binary or prebuilt environment is not equivalent to
     preserving source-to-execution reproducibility.

4. Sacco, Sopranzetti and Fiore, *Enabling Provenance Tracking in Workflow
   Management Systems* (2024), DOI `10.1109/BIGDATA62323.2024.10825405`.
   - Detailed transformation and workflow provenance supports traceability and
     integrity in complex HPC workflows.

Project inference supported by these methods:

```text
source identity
!= successor-host environment identity
!= read-only preflight evidence
!= current protection readback
!= lease acquisition
!= native execution outcome
!= retrospective result audit
```

The literature does not determine the REI Git head, toolchain hashes, GitHub
ruleset ID, one-attempt budget, native outcome, first-interval result, or any
physics/provider claim.

```text
authority_effect = NONE
```
