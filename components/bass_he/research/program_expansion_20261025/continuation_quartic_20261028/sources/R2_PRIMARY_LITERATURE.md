# Primary-source evidence for QUARTIC12
Search/read date2026-10-28. This is a scoped review of relevant methods, not an exhaustive literature novelty claim.

1. Jürgen Garloff, The Bernstein Algorithm, Interval Computations2(1993),154–168.
Primary full text: https://interval.louisiana.edu/reliable-computing-journal/1993/interval-computations-1993-2-pp-154-168.pdf
Read§1.1 range enclosure and§1.2 subdivision, including Theorem2.
Relevance: Bernstein coefficient bounds and subdivision improvement are established. QUARTIC12 derives its particular quadratic cell formula and O(N^-2) nodal residual directly.

2. Larry Allen and Robert C. Kirby, Bounds-constrained polynomial approximation using the Bernstein basis, arXiv:2104.11819v2; Numerische Mathematik(2022), DOI10.1007/s00211-022-01311-1.
https://arxiv.org/abs/2104.11819 ; https://arxiv.org/pdf/2104.11819
Read abstract/introduction and constraint formulation.
Relevance: separate true univariate positivity from linear coefficient constraints; mass constraints are compatible with approximation. This study does not copy their optimization algorithm.

3. Mitchell Tong Harris and Pablo A. Parrilo, Improved Nonnegativity Testing in the Bernstein Basis via Geometric Means, arXiv:2309.10675v1(2023).
https://arxiv.org/abs/2309.10675 ; https://arxiv.org/pdf/2309.10675
Read abstract/introduction comparing conservative coefficient positivity with stronger certificates and conic alternatives.
Relevance: negative Bernstein coefficients alone do not prove a polynomial negative.

Discovery: one Exa search (five returned results), one SciSpace search (ten candidates) actually completed. Additional2025/2026 candidate metadata was not promoted to read full-text evidence.
Current Wolfram context response: successful documentation, semantic NoResultsFound; not a numerical result. A distinct bounded evaluator will check the new formula identities.
All mathematical claims used for certification are rederived in THEORY.md; no PDF full text is placed in source/backups.

