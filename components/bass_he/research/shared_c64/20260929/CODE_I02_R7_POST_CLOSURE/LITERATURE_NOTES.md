# R7 primary-source notes

SciSpace was used for discovery. Specific claims below were checked against primary author abstracts or official documentation; this is not a full-text paper review.

1. Revol and Theveny, Numerical Reproducibility and Parallel Computations: Issues for Interval Algorithms, arXiv:1312.3300v1; IEEE TC DOI 10.1109/TC.2014.2322593. https://arxiv.org/abs/1312.3300
   The abstract separates bitwise reproducibility from the interval inclusion property and warns that implementation issues can invalidate inclusion. It does NOT establish a BASS_HE cross-platform error bound.
2. Becker et al., A Verified Certificate Checker for Finite-Precision Error Bounds in Coq and HOL4, arXiv:1707.02115v2. https://arxiv.org/abs/1707.02115
   The v2 author list/title differ from SciSpace's older three-author indexing: Becker, Zyuzin, Monat, Darulova, Myreen, Fox. The author abstract describes a verified checker for roundoff bounds; it does NOT validate our solver or our proposed two-record workflow.
3. Python documentation, Default Argument Values. https://docs.python.org/3/tutorial/controlflow.html#default-argument-values
   Defaults are evaluated at definition time, once. Replacing literals by named constants prevents duplicated spelling but does not make defaults follow later mutation of module globals.
4. NumPy documentation, numpy.show_runtime. https://numpy.org/doc/stable/reference/generated/numpy.show_runtime.html
   This exposes useful runtime/BLAS/SIMD information. Such metadata is diagnostic provenance, not proof that all numerical behavior is captured or reproducible.

Repository authorities read through GitHub:
- PR15 b8b2fe47a367459f6faf6796eb2f251feacbbd7c, AGENTS.md and src/bass_he/spectral.py.
- Same commit, evidence/DR9B_EXPONENT_CHANNEL_AUDIT.json. Its unresolved Eq52/Eq55 normalization and forbidden default promotion are existing repository claims, not independently rederived here.
- PR17 7b276609e828078826ad1969a264c5604c332c3f at R7 intake.

Original screenshots are primary evidence of what the user supplied. Their raw reviewer JSON/commands/attack script were not available in the inspected PR15/PR17 research namespaces. They are not reconstructed and mislabeled as a verbatim raw report.
