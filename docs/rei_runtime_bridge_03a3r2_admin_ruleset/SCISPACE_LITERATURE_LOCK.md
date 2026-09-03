# SciSpace methodology role lock

Search question: which peer-reviewed methods support an irreversible exactly-once scientific workflow step whose remote reservation, live policy readback, immutable execution provenance, and retrospective outcome audit must remain distinct but strongly linked?

Relevant methodology:

1. Wang, Lu, Fei & Ram, *A Dataflow-Oriented Atomicity and Provenance System for Pipelined Scientific Workflows* (2007), DOI `10.1007/978-3-540-72588-6_42`.
   - Role: combines atomic commit/abort regions with failure-aware provenance.

2. Dubey et al., *Using Runtime Verification to Design a Reliable Execution Framework for Scientific Workflows* (2009), DOI `10.1109/EASE.2009.13`.
   - Role: checks execution-time invariants against the actual running workflow rather than inferring them from a static plan.

3. Koop et al., *Bridging Workflow and Data Provenance Using Strong Links* (2010), DOI `10.1007/978-3-642-13818-8_28`.
   - Role: strengthens persistent links between provenance records and the data or artifacts they claim to describe.

Project inference:

```text
ruleset intent
!= ruleset mutation receipt
!= GET-only effective-rule readback
!= global attempt reservation
!= native execution outcome
```

The admin handoff therefore emits separate mutation and GET-only protection receipts. The literature does not own REI source bytes, GitHub ruleset IDs, toolchain hashes, the one-attempt budget, runtime outcomes, first-interval status, or provider/scientific claims.

```text
authority_effect = NONE
```
