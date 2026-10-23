# Sources actually used in this local-flow unit

Search/read date: 2026-10-22, Asia/Seoul. The numerical run uses copied
offline inputs. Literature search is a source check and method comparison,
not a runtime dependency or evidence that a numerical experiment succeeded.

## Adopted primary input and method sources

1. D. A. Verner and G. J. Ferland, *Atomic data for astrophysics. I.
   Radiative recombination rates for H-like, He-like, Li-like and Na-like ions
   over a broad range of temperature*, ApJS **103**, 467 (1996),
   [DOI](https://doi.org/10.1086/192284),
   [preprint](https://arxiv.org/abs/astro-ph/9509083),
   [PDF](https://arxiv.org/pdf/astro-ph/9509083).
   The controller read the fit in Eq. (4), the hydrogen row in Table 1 and
   the discussion of total versus partial recombination coefficients. The
   source supplies a total RR number-rate fit. Its derivative-of-fit energy
   moment and the thermodynamic first integral are the conditional model
   constructions explained in THEORY.md, not additional measured data.

2. [Author's recombination-data page](https://www.pa.uky.edu/~verner/rec.html)
   and its linked [Table 1](https://www.pa.uky.edu/~verner/dima/rec//table1.dat).
   The first row read directly is H I, Z=1, N=1,
   a=7.982e-11 cm^3/s, b=0.7480, T0=3.148 K, T1=7.036e5 K. These agree with
   the already preserved donor row. A direct single-slash table URL failed
   in the web tool; following the author's table link succeeded. No input
   was replaced after that access failure.

3. Gilbert Strang, *On the Construction and Comparison of Difference
   Schemes*, SIAM J. Numer. Anal. **5**(3), 506–517 (1968),
   [DOI/landing page](https://epubs.siam.org/doi/10.1137/0705041),
   [PDF](https://epubs.siam.org/doi/epdf/10.1137/0705041).
   The controller opened both and read the opening half-step construction
   and Taylor-order discussion. For the particular nonlinear beta/RR flows,
   THEORY.md and the recorded Wolfram calculation verify the second-order
   expansion directly; no unstated detailed-balance hypothesis is imported.

4. [NIST DLMF §10.25](https://dlmf.nist.gov/10.25),
   [§10.28](https://dlmf.nist.gov/10.28),
   [§10.29](https://dlmf.nist.gov/10.29): modified Bessel equation, Wronskian
   and derivatives used in the analytic beta/RR reference. Independent
   reviewer checked equations 10.25.1, 10.28.2 and 10.29.3.

The neutron mean lifetime 878.4 s and its original PDG 2025 attribution are
reused from the byte-preserved EVALUATED_DECAY_INPUTS.json. This turn did not
claim a new extraction of the current neutron evaluation. The model retains
the inherited selected-continuum-channel approximation. Source repository
pins and PR219 provider scope are in SOURCE_INTAKE.md and the contract.

## SciSpace and Exa search record

SciSpace was queried about deterministic chemical-reaction networks,
positive mass-conserving second-order splitting, exact unimolecular and
bimolecular subflows, and reaction-extent energy accounting. It returned ten
candidate records, including Liu/Wang/Wang, SIAM J. Sci. Comput. (2022),
[DOI 10.1137/21m1444825](https://doi.org/10.1137/21m1444825), and
Bruggeman/Burchard/Kooi/Sommeijer (2006) on positive mass-conserving methods.
The returned abstracts were read for method context. No theorem was adopted
from an unread full text.

Exa was queried for primary sources on exact reaction flows and positive
conservative splitting. Relevant returned material included
Liu/Wang/Wang, [arXiv:2402.03731](https://arxiv.org/abs/2402.03731), concerning
energy-stable detailed-balance mass-action schemes. Detailed-balance
variational results were not assumed for the irreversible beta/RR model.
The finite flow maps and their conservation/order properties are derived
explicitly here. This search establishes context, not a novelty claim.

## Wolfram verification actually executed

The initial Wolfram context-discovery call returned tool error -32603
(Internal error). The subsequent Wolfram Language evaluator succeeded with
timeConstraint=30 and returned:

```text
<|"VF_D_residual" -> 0,
  "thermal_energy_residual" -> 0,
  "Strang_order2_residual" -> {0, 0}|>
```

The symbolic expressions checked are recorded in WOLFRAM_CHECK.md. These
identities verify algebraic relations. Numerical accuracy, positivity under
floating-point execution, performance and source applicability are addressed
by their own evidence and independent review.
