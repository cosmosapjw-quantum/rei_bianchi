# R10C literature notes

SciSpace was used to separate embedded quadrature/discretization error from
surrogate/model approximation error.

- Favati, Fiorentino, Lotti & Romani, ACM TOMS 23 (1997),
  DOI 10.1145/244768.244772: local error estimates and regularity diagnostics for
  adaptive quadrature.
- Zhang, Chowdhury, Mehmani & Messac, Journal of Mechanical Design 136 (2014),
  DOI 10.1115/1.4026150: spatially varying uncertainty attributable to surrogate
  predictions.
- Bect et al., arXiv:2103.14559 / WCCM-ECCOMAS 2020: discretization uncertainty is
  treated as a distinct numerical uncertainty source.
- Michel & Siegle, arXiv:2403.07618: a modern example of stepwise perturbation bounds
  in stochastic transition dynamics.

SciSpace add-column returned no methodology/conclusion expansions for the selected
quadrature/surrogate papers, so no stronger paper-specific claim is made.

These references do not prove the BASS_HE 2e-4 threshold. Their relevance is the
error-budget architecture: surrogate/model discrepancy and embedded quadrature error
must remain separate channels.
