# SciSpace Methodology Role Lock — REI 03A3

The literature search was restricted to execution provenance and exactly-once governance methodology.

Relevant methodological roles include:

- prospective versus retrospective scientific-workflow provenance: the workflow plan and the actual run are distinct but linked records;
- Workflow Run RO-Crate-style run packaging: code, inputs, environment, outputs, and run-level provenance should be related explicitly;
- PRUNE-style immutable execution lineage: task inputs and environment identities should be preserved with derived outcomes;
- distributed/HPC provenance methods: heterogeneous execution activities and environment state require explicit capture rather than silent equivalence.

Project inference:

```text
one-shot authorization must bind
  fixed remote authority
  exact executing code bytes
  exact environment attestation
  exact input and path identities
  retrospective outcome
```

The literature does not determine REI source bytes, Git hashes, the number of remaining attempts, the global-ref name, toolchain-lock values, runtime outcome, first-interval status, provider admission, or a scientific claim.

```text
authority_effect = NONE
```
