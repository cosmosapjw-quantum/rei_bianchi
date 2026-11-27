# DR7 source audit

## Eq. (52) support

Direct inspection of CPC 286 (2023) 108662 p.12 gives

`rho <= Re(Rc) + Im(Rc)`

and describes `Im(Rc)` as the semi-width of the non-adiabatic-coupling matrix
element.

Earlier internal wording `Re Rc + DeltaRc` was a transcription error and is
superseded by this node.

## Eq. (52) versus Eq. (55)

The paper also prints:
- Eq. (52): `p_k = exp[-Delta_k(rho)/v]`
- Eq. (55): `P^Q_beta,alpha = exp[-2 Delta_beta,alpha/v]`

Both use the Stückelberg terminology.  The factor-of-two is therefore preserved
as a source/convention discrepancy.  DR7's Eq50 lane follows Eq52 literally,
and exports the Eq55 value as a diagnostic.

Later hidden-crossing literature uses the conventional single-pass form
`exp(-2 Delta)` as well, which supports retaining this discrepancy rather than
silently rewriting Eq. (52).

No author-source code was used to infer an undocumented convention.
