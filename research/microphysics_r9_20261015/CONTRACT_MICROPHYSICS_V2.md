# R9 balanced common-basis contract V2

Frozen ID: R9-FCI-BO-QUENCH-RESPONSE-v2, 2026-10-15. This addendum inherits V1 numerical gates, full Coulomb Hamiltonian, infinite-mass point-nucleus scope, output provenance, resource caps and physical limitations. V1 is immutable. This specification is not an execution receipt.

Mandatory He→Li+ union: concatenate element-specific He and Li aug-cc-pVDZ shells at one origin; then aug-cc-pVTZ if resource-feasible. Z2→3, charges0→1, nelec(1,1), singlet. Retain original Li-only results as basis-imbalance diagnostics. Union-DZ has priority over extending that inadequate Li-only series.

Mandatory Li→Be+ union: concatenate element-specific Li and Be cc-pVDZ shells at one origin; then aug-cc-pVDZ, and aug-cc-pVTZ if feasible. Z3→4, charges0→1, nelec(2,1), doublet. This is the correlated three-electron sudden electronic quench relevant to Li8/Li9 beta decay; no finite isotope mass, nuclear recoil, weak-current correction or complete nuclear decay branching is included. The ground projection does not supply all electronic final channels.

Construct S and X only once per union: S=U diag(s) U^T, retain s>1e-10*smax, X=Uret diag(sret^-1/2). Transform both charge Hamiltonians and shared ERIs with identical X. Preserve expanded shells, AO ordering and determinant ordering. No separate parent/daughter MO optimization before a direct CI dot product. Repeat smallest union with cutoff1e-9 as a conditioning diagnostic.

For three electrons the CI tensor shape is (binom(norb,2),binom(norb,1)); do not hardcode a two-electron square matrix. Check spin²=3/4, normalized vectors and original-Hamiltonian residuals. Spin penalties may select a state but final physical energy and residual exclude the penalty.

A0=vdot(Cf,Ci), P0=|A0|², q=Ci−A0 Cf. Export P0, ||q||², their closure, <Cf,q>, <Ci|Hf|Ci>, <Ci|Hf²|Ci>, variance, both energies/CI vectors/residuals/spin values, common X, retained rank, expanded basis and overlap spectrum. The complement includes excited bound states and continuum; it is not an ionization probability. Compare parent/daughter energies with independent element-specific atomic targets as basis-quality diagnostics. Exact finite-space closure alone is not physical convergence.

Promote Li and Li+ cc-pCVDZ/cc-pCVTZ all-electron FCI to active resource-gated work. Retain all electrons and all independent orbitals, compute matched-basis ionization energy, and keep existing valence-basis series. Basis-loading failure must be explicit; no silent substitution.

V2 JSON provides nine explicit execution_cases and three pilot_execution_cases. Pilot4 threads/16GiB/1800s; standard production12 threads/24GiB/7200s per case. Pre-estimate retained n, determinant count and ERIs: D<=10m, ERI<=8GiB, predictedRSS<=75%allocation, aggregate<=48CPUs/96GiB. Resource deferrals retain completed cases and estimates. V1 numerical gates are unchanged. Molecular and response tasks are unchanged.

Primary physics reference supplied by root's literature intake: Ruiz and Frolov, https://arxiv.org/abs/1305.5696. It motivates Li8/Li9→Be+ final-state scope; its numerical values are not substituted for these independent calculations.
