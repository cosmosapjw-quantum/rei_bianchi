# SciSpace methodology lock — container identity versus executable-environment identity

The literature search was used only to constrain evidence boundaries.

Relevant methodological roles:

1. Vallet, Michonneau & Tournier, *Toward practical transparent verifiable
   and long-term reproducible research using Guix* (Scientific Data, 2022),
   DOI `10.1038/s41597-022-01720-9`.
   - Environment descriptions consisting only of software names, versions or
     opaque container images are insufficient for the full dependency graph.

2. Ivie & Thain, *PRUNE: A Preserving Run Environment for Reproducible
   Scientific Computing* (eScience, 2016), DOI `10.1109/eScience.2016.7870886`.
   - A task must be coupled to a strictly defined environment and immutable
     provenance tree rather than reconstructed from an informal description.

3. Vahi et al., *Custom Execution Environments with Containers in
   Pegasus-Enabled Scientific Workflows* (eScience, 2019),
   DOI `10.1109/ESCIENCE.2019.00039`.
   - Containers help preserve execution environments, but distributed runtime
     endpoints and their identity remain part of the workflow provenance.

4. Youngdahl, Ton-That & Malik, *SciInc: A Container Runtime for Incremental
   Recomputation* (eScience, 2019), DOI `10.1109/ESCIENCE.2019.00040`.
   - Container engines do not automatically capture the provenance needed to
     verify computation; creation inputs and change propagation must be
     observed explicitly.

Project inference:

```text
container tag
!= immutable image digest
!= Docker daemon/context authority
!= signed package-repository state
!= canonical installed-file closure
!= executable runtime closure
```

This supports binding the exact H1A seed and daemon context, signed Snapshot
metadata, package/DEB/installed-file manifests, and the full pre-start ELF
closure.  The literature does not own REI hashes, GitHub state, the attempt
budget, native outcome or any physics claim.

```text
authority_effect=NONE
```
