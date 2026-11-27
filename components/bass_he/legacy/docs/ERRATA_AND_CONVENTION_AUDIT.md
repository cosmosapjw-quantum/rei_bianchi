# R2 convention and transcription audit

Status labels:
- `SOURCE_VERIFIED`: directly supported by the cited source.
- `DERIVED_CHECK`: obtained by internal mathematical consistency / limiting cases.
- `REIMPLEMENTATION_POLICY`: choice made for this clean-room implementation.

## 1. CPC 2023 Eq. (1)-(2) block contains transcription errors

The attached CPC 2023 paper prints, immediately below the separated equations,

`a=(Z2+Z1)/R`, `b=(Z2-Z1)/R`.

This is inconsistent with:
1. the coordinate transformation itself,
2. dimensional/scaling structure of the two-center Coulomb equation,
3. the primary Solov'ev 1981 formulation used by ARSENY,
4. the later independent CPC 2023 two-center continuum formulation.

The primary formulation is

`p = R sqrt(-2E)/2`,
`a = (Z2+Z1) R`,
`b = (Z2-Z1) R`.

R2 uses this primary convention.

Verdict:
`CPC23_A_B_OVER_R__TRANSCRIPTION_ERROR`
`PRIMARY_A_B_TIMES_R__ADOPTED`

## 2. Separation-constant signs in the CPC separated equations are reversed

The CPC paper prints radial `+lambda` and angular `-lambda`.
Solov'ev 1981 gives radial `-lambda` and angular `+lambda`.

The recurrence coefficients published in the older primary formulation are
consistent with the latter convention and with the united-atom limit
`lambda -> l(l+1)`.

R2 therefore uses the Solov'ev/Komarov convention and names the value
`separation_lambda` to avoid silently mixing conventions.

Verdict:
`CPC23_LAMBDA_SIGN_BLOCK__TRANSCRIPTION_ERROR`
`PRIMARY_SOLOVEV_LAMBDA_CONVENTION__ADOPTED`

## 3. CPC 2023 recurrence coefficients are not internally consistent

For the Jaffe radial recurrence the older source gives

`beta_s = 2s(s+2p-sigma) -(m+sigma)(m+1) -2p sigma + lambda`.

For the asymmetric Baber-Hasse angular recurrence it gives

`rho_s = (s+2m+1)[b-2p(s+m+1)]/[2(s+m)+3]`,
`chi_s = (s+m)(s+m+1)-lambda`,
`delta_s = s[b+2p(s+m)]/[2(s+m)-1]`.

The CPC 2023 text has sign/index changes in these expressions.  Those printed
variants fail the united-atom limit numerically and are not used.

Verdict:
`CPC23_RECURRENCE_TRANSCRIPTION__REJECTED`
`PRIMARY_RECURRENCE__ADOPTED`

## 4. United-atom seed

For R -> 0 the physical Hamiltonian becomes a hydrogenic united atom with
charge Z1+Z2. Therefore

`E_N -> -(Z1+Z2)^2/(2 N^2)` Hartree,
`lambda -> l(l+1)`.

This factor 1/2 is also required by `p=R sqrt(-2E)/2`.

The CPC small-R energy expression as typeset omits that factor in its leading
term. R2 does not use that leading term as printed.

Verdict:
`UNITED_ATOM_HYDROGENIC_LIMIT__DERIVED_AND_NUMERICALLY_CHECKED`

## 5. Identity policy

This is still:
`PAPER_DERIVED_REIMPLEMENTATION`
`NOT_AUTHOR_CODE`
`NO_AUTHOR_SOURCE_BYTES_USED`

The correction of transcription errors does not establish implementation
identity with the unavailable author code.
