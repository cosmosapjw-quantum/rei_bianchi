# Research contract

## Primary research question

Can the four missing operator inputs identified by R1B—time-resolved four-group forcing, a state-derived dynamic-opacity law, a canonical macro-to-node partition, and optical-depth-dependent heating moments—be reconstructed uniquely enough from the existing canonical artifacts to authorize the next fixed-point-history stage without endpoint interpolation, source/fesc refitting, opacity inversion, or cloud-mass inversion?

## Candidate hypotheses

- **H1 — canonical-input pass:** the B2C2A-R1 BDF dense trajectory identifies a time-resolved global forcing; state-derived H/He absorption measures plus common incident macro flux identify a conditional Radon–Nikodym node partition; Verner moments and the dense thermal ledger identify bounded hardening coordinates.
- **H2 — partial pass:** time-resolved forcing and opacity are identifiable, but either node partition or thermal moment remains nonunique.
- **H3 — fail-closed:** one or more required inputs cannot be reconstructed without an additional prior or a post-hoc fit.

## Success criteria

1. Canonical BDF replay matches inherited endpoints and exact ledgers within the locked replay gates.
2. A globally predeclared nested Chebyshev–Lobatto/Clenshaw–Curtis schedule selects the smallest common node count satisfying dense-integral and nested-refinement gates.
3. Opacity is constructed only from material species state, finite cell geometry, and group cross sections.
4. One shared nonnegative Radon–Nikodym density closes both opacity and current moments under common macro incident flux.
5. Heating moments remain inside thin/thick physical envelopes and reproduce the canonical dense thermal forcing without source refitting.
6. H/He support and primary exact zeros are structural.
7. Independent symbolic, high-precision, adversarial, and repository checks pass.

## Forbidden repairs

- endpoint interpolation as a physical forcing history;
- node-wise free fitting;
- defining dynamic opacity as `J/Phi`;
- cloud-mass or geometry inversion to meet opacity;
- clipping or inter-macro moment transport;
- post-result quadrature-schedule changes;
- source/fesc calibration;
- recombination surrogate or adapter work.
