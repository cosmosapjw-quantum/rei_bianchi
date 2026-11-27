# Representation and simplification decision

The selected route is original source-coordinate finite-mass ionization. Incoming V,g are used for the common-T Gaussian factorization; the original g1,g2 define final velocities and the transfer Υ. This preserves the same differential law in the heavy-target limit.

| Candidate | Decision | Reason |
|---|---|---|
| Replace only m_e by μ in the old total STF rate | Rejected as incomplete | Rate scales as ζ^(-1/2), whereas the electron-input total STF coefficient scales as √ζ; target stress contributes independently |
| Reassign uniform G and the old transfer distribution to an electron-pair Jacobi coordinate | Not selected | Coordinates transform, but reassigning the same isotropy/energy law in new coordinates changes the physical model |
| Original source Jacobi coordinates and explicitly uniform G | Selected | Exact event momentum/energy, same-kernel gain/loss, source-coordinate heavy-mass limit |
| Add a new production two-dimensional sharing quadrature | Algebraically removed | Λ=β−θα, U1=θα, U2=β−(I+θ)α, so existing moments suffice |
| Compute a tiny heavy combined heat or total STF by subtracting large species/full-pressure terms | Avoided in scientific outputs | Direct Q_heavy, Q_total and J_total preserve their respective scales |

The positive U2 oracle is x∫t exp(−t)/(x+t)²dt. It is retained only as a new independent numerical check. Production species heat uses already simplified expressions. This is an optimization by the adopted physics and algebra; it does not relax tolerances or replace the source normalization.
