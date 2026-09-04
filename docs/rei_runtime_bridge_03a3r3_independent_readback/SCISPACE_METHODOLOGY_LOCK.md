# SciSpace methodology lock — prospective versus retrospective provenance

The literature query was restricted to workflow provenance and runtime verification for irreversible or partially irreversible state transitions.

## Stable supporting sources

1. Lim, Lu, Chebotko and Fotouhi, *Prospective and Retrospective Provenance Collection in Scientific Workflow Environments*, IEEE SCC (2010), DOI `10.1109/SCC.2010.18`.
   - Supports distinguishing a workflow specification from provenance recorded for a particular execution.

2. Prabhune et al., *Establishing provenance-based semantic similarity between scientific workflows: a comparison of language-agnostic methods*, Distributed and Parallel Databases 36 (2018), DOI `10.1007/S10619-017-7216-Y`.
   - Supports linking prospective and retrospective provenance through a common model without identifying them.

3. Butt and Fitch, *A provenance model for control-flow driven scientific workflows*, Data & Knowledge Engineering 131 (2021), DOI `10.1016/J.DATAK.2021.101877`.
   - Supports recording execution history and contextual control-flow information for later inspection and auditing.

4. Bao et al., *Differencing Provenance in Scientific Workflows*, ICDE (2009), DOI `10.1109/ICDE.2009.103`.
   - Supports comparing executions and identifying where two provenance traces diverge.

## Project inference

The following are distinct facts:

```text
prospective admin operation contract
historical mutation receipt
historical GET-only source receipt
retrospective operation audit
current live GitHub readback
new current protection receipt
```

An expired historical receipt may remain valid evidence that the original operation was coherent, provided the operation completed before its expiry. It cannot establish present authorization. Present authorization requires a new live readback and a newly time-bounded receipt.

The literature does not determine REI schemas, GitHub endpoint semantics, ruleset IDs, source hashes, attempt budgets, native outcomes, first-interval admission, or scientific claims.

```text
authority_effect = NONE
```
