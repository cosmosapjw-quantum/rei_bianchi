# SciSpace methodology role lock

Search question:

> Which peer-reviewed methods bind distributed scientific-workflow executions to exact code artifacts, environment attestations, authorization or immutable provenance records, while distinguishing prospective workflow plans from retrospective run provenance?

## Relevant roles

- Lim, Lu, Chebotko, and Fotouhi, *Prospective and Retrospective Provenance Collection in Scientific Workflow Environments* (2010): prospective workflow specification and retrospective execution/data provenance are distinct but linked records.
- Cruz, Campos, and Mattoso, *Towards a Taxonomy of Provenance in Scientific Workflow Management Systems* (2009): distributed workflow provenance has heterogeneous perspectives and requires explicit classification rather than silent equivalence.
- Guedes et al., *A Practical Roadmap for Provenance Capture and Data Analysis in Spark-Based Scientific Workflows* (2018): runtime data and execution provenance must be captured across distributed workflow activities.
- Bao et al., *Differencing Provenance in Scientific Workflows* (2009): executions of the same prospective specification can have materially different retrospective provenance and should be compared as executions, not conflated.

## Project inference

For the remaining one-shot REI runtime attempt, a prospective plan or clean repository checkout is insufficient by itself.  The authorization receipt must bind:

```text
fixed remote authority
exact executing package bytes
exact environment attestation
exact inputs and path identities
retrospective outcome
```

This literature supports the governance distinction only.  It has `authority_effect=NONE` on REI formulae, Git hashes, attempt count, toolchain-lock values, runtime outcome, first-interval status, provider admission, or scientific claims.
