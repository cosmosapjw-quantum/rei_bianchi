# BASS_HE R8 source-normalization audit: Eq.(52), Eq.(55), Eq.(56) and upstream hidden-crossing theory

## 0. Scope and state

R7 recovered the original CODE-I02 review and froze the runtime gate as closed. R8 does not reopen that audit. The question is now narrower: what does the authorized CPC 2023 source actually say about the hidden-crossing probability normalization, and what is the smallest evidence needed before any Eq.(55) numerical lane or default change?

Current gates remain `CODE_I02_CLOSED=true`, `full_certificate_fail_closed=true`, `scientific_PROMOTE=HOLD`, `Eq55_next_node_authorized=false`, `Eq55=NOT_RUN`.

## 1. Authorized source identity

The Library copy `1-s2.0-S0010465523000073-main.pdf` was materialized without redistributing it. It is 961,962 bytes and SHA256

`1367f5ab3239cad1b3ea377edb28a9b9e6975f4cec27fb6d289fdb1d601b1c55`,

exactly matching the identity previously pinned in the repository. Therefore the following page audit is no longer inherited transcription; it is direct inspection of the authorized source bytes.

## 2. Direct CPC source audit

### Page 12: Eq.(50)–(54)

Eq.(50) writes the total probability matrix as a symmetric product of hidden-crossing matrices around the rotational matrix,

`P_kmax ... P_1 P_rot P_1 ... P_kmax`.

Eq.(51) uses a two-state stochastic block with entries `1-p_k` and `p_k`. Eq.(52) then defines

`p_k = exp[-Delta_k(rho)/v]`

inside its support and explicitly calls `p_k` the **probability of elementary transition**. Thus, within the printed Eq.(50) construction, `p_k` is not presented as a complex amplitude.

For the absorbing upper shell, Eq.(53) modifies the matrix topology, while Eq.(54) integrates the resulting probability matrix over impact parameter.

### Page 13: Eq.(55)–(56)

Immediately after the summary says that a Q-series branch point connects two surfaces, the paper calls

`P^Q_{beta,alpha} = exp[-2 Delta_{beta,alpha}/v]`

the **associated single-pass transition probability**, Eq.(55). Eq.(56) defines `Delta_{beta,alpha}` by the absolute value of a contour/action integral of the energy difference around the branch point.

The inspected text does not print either `Delta_k(Eq52)=Delta_{beta,alpha}(Eq56)` or `Delta_k=2 Delta_{beta,alpha}`. Both are called Stückelberg parameters, so a normalization map cannot be invented silently.

### Program-description pages

The program description says STCKLBR2 computes the Stückelberg parameter Eq.(56); the output parameter file is used in subsequent calculations, and CR_SECTION computes Eq.(54). This strongly connects the Eq.(56) quantity to the cross-section pipeline, but the paper prose does not expose the exact line of source code that turns that stored quantity into the matrix probability. That data-flow step is now the decisive missing authority.

### Appendix A

At Nmax=3, the printed charge-exchange shell n=3 equals the printed ionization result at both test energies, confirming directly that the upper-shell export and ionization export alias in the test desk. This supports the existing truncation-bookkeeping interpretation and does not license double-counting as disjoint physical channels.

## 3. A second printed inconsistency: CPC Eq.(43)

CPC page 10 prints the Landau-Zener approximation to the Stückelberg parameter as

`Delta = pi DeltaE_min/(4 DeltaF)`

without a square on the minimum gap.

Richter & Solov'ev, Phys. Rev. A 48, 432 (1993), in the same advanced-adiabatic/hidden-crossing lineage, prints instead

`Delta = pi (DeltaE_min)^2/(4 DeltaF)`

and uses a factor-two probability exponent. The squared-gap form also gives the standard Landau-Zener scaling. This makes the 2023 Eq.(43) omission a strong source-level inconsistency. R8 does **not** silently patch Eq.(43) or declare an erratum; it records the conflict and sends it to the author-code audit.

This matters because the Eq.(52)/(55) factor-two discrepancy is therefore not isolated: the same paper contains at least one nearby Stückelberg-normalization formula that conflicts with established upstream theory.

## 4. Fresh Wolfram checks

For `Delta = pi g^2/(4 F)`, Wolfram gives

`|exp[i(S+i Delta)/v]|^2 = exp[-2 Delta/v] = exp[-pi g^2/(2 F v)]`.

Thus Eq.(55) is exactly the modulus-square probability associated with an imaginary complex action of magnitude Delta.

Wolfram also verifies that if Eq.(52)'s `p` is used as the stochastic probability in Eq.(51), applying the same reversible matrix twice gives off-diagonal transfer `2 p (1-p)`, not `p^2` in general. For an absorbing upper state it gives `p(2-p)`. Therefore the repeated approach/receding matrices in Eq.(50) do **not** themselves explain the factor of two in Eq.(55).

## 5. Literature status

SciSpace searches recover the established advanced-adiabatic/hidden-crossing chain, including Grozdanov–Solov'ev 1990, Richter–Solov'ev 1993, Solov'ev 2005, and Grozdanov–Solov'ev 2014. SciSpace did not supply extra methodology/conclusion fields for the selected records, so equation-level claims are not inferred from metadata alone.

A primary/open copy of Richter–Solov'ev 1993 gives direct equation-level support for factor two and the squared-gap Stückelberg parameter. This is independent literature support for the Eq.(55) convention, but it cannot tell us whether CPC 2023's Eq.(52) is a typo, uses an undocumented doubled Delta, or reflects the actual 2023 program implementation.

## 6. Converged interpretation

The evidence now supports the following separation.

**SOURCE-VERIFIED:** CPC Eq.(52) is a factor-one elementary probability inside a stochastic matrix. CPC Eq.(55) is a factor-two Q-series single-pass probability. Eq.(56) is the branch-point action parameter.

**DERIVED/LITERATURE-SUPPORTED:** factor two is consistent with modulus-square of the complex action and with the 1993 advanced-adiabatic formulation. CPC Eq.(43)'s missing square conflicts with that upstream formulation.

**UNRESOLVED:** what the actual CPC 2023 ARSENY code uses when turning the Eq.(56) parameter into `p_k` in CR_SECTION, and whether the paper's Eq.(52) or Eq.(43) contains transcription/normalization errors.

Therefore R8 admits Eq.(55) as a source-faithful **theory/analysis formula**, but does not authorize an Eq.(50) factor-two substitution, production default change, or heavy Eq.(55) numerical run. The fastest discriminating evidence is the public author program, not another benchmark.

## 7. Next node

The CPC paper identifies the public Program Library dataset DOI `10.17632/n43srxwdnm.1`, Version 1, CC BY 4.0, FORTRAN 90/95. The next node is a read-only static provenance audit of those author source bytes.

Trace, without importing author code into the clean-room implementation:

`STCKLBR2 / stuckelberg data -> CR_SECTION / SECTION -> probability exponent -> Eq.(51)/(53) matrix`.

Classify exactly one of:

1. author code uses `exp(-Delta/v)` on the Eq.(56) parameter;
2. author code uses `exp(-2 Delta/v)`;
3. author code rescales Delta before exponentiation;
4. source path is ambiguous or differs by branch type.

Only after that trace should the project request a decision on `Eq55_next_node_authorized` or a default exponent policy.
