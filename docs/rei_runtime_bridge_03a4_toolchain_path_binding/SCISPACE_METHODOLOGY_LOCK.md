# SciSpace methodology lock — compiler provenance and runtime concordance

Search question:

> Which peer-reviewed methods support distinguishing exact compiler-binary identity from reproducible-build equivalence, while ensuring that an attested preflight toolchain is the same toolchain actually used at runtime?

Relevant methodological roles:

1. Rosenblum, Miller & Zhu, *Extracting compiler provenance from program binaries* (PASTE 2010), DOI `10.1145/1806672.1806678`.
   - Role: compiler identity is a material component of program provenance rather than an incidental implementation detail.

2. Benoit, Marion & Bardin, *Binary level toolchain provenance identification with graph neural networks* (SANER 2021), DOI `10.1109/SANER50967.2021.00021`.
   - Role: compiler family, version and optimization provenance are distinct recoverable properties; family-level equivalence does not imply byte or version identity.

3. Chen et al., *DIComP: Lightweight Data-Driven Inference of Binary Compiler Provenance with High Accuracy* (SANER 2022), DOI `10.1109/SANER53432.2022.00025`.
   - Role: compiler and optimization settings can materially change binary appearance and therefore must be included in provenance claims.

4. Hugenroth, Lins, Mayrhofer & Beresford, *Attestable builds: compiling verifiable binaries on untrusted systems using trusted execution environments* (2025), arXiv `2505.02521`.
   - Role: source-to-binary correspondence and build-pipeline attestation are separate from ordinary reproducible-build claims; sandboxed or isolated build contexts can bind the actual build environment.

Project inference:

```text
same compiler family
!= same compiler version
!= same compiler file bytes
!= same canonical runtime path
!= same full build/runtime closure
```

and:

```text
identified historical package
!= reconstructed target-host epoch
!= successor Section-0 PASS
!= native-runtime authorization
```

The path-binding GREEN therefore requires a single canonical runtime-path snapshot to be validated before Section-0 emission, immediately before global reservation, in every lease/dispatch record, and again in the post-lease worker.

The literature does not own REI source bytes, GitHub state, semantic-lock values, attempt count, runtime outcomes, provider admission or scientific claims.

```text
authority_effect = NONE
```
