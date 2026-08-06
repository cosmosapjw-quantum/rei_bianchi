# R2C-R1B dimension, sign, and limiting audit

## Conventions

- Metric signature: `(-,+,+,+)`.
- Spatial orientation: `epsilon_123=+1`.
- Natural units are not used.
- `c`, `hbar`, and `k_B` remain explicit.  The present local chemistry audit
  does not activate the spacetime metric or `c`; photon energy remains
  `E=h nu=2 pi hbar nu` and thermal energy retains `k_B`.

## Dimensions

| quantity | dimension |
|---|---|
| `N_HI`, `N_HII`, integrated absorbed count | `cMpc^-3` |
| `J_g`, `Q_coll`, `R_rec`, transfer event rates | `s^-1 cMpc^-3` |
| `Gamma_g`, `alpha n_e`, `beta n_e` | `s^-1` |
| `kappa_g` | `cMpc^-1` |
| `Phi_g` in the inherited current-Gamma representation | `s^-1 cMpc^-2` |
| `J_g=kappa_g Phi_g` | `s^-1 cMpc^-3` |
| photon excess energy | `eV` or `erg` with `1 eV=1.602176634e-12 erg` |
| photoheating density rate | `erg s^-1 cMpc^-3` |

The perturbation coordinates `s=t/T`, `f(s)`, and `g(s)` are dimensionless;
their amplitudes carry the units of `J_g`.

## Signs

The neutral equation uses

\[
\dot N_{\rm HI}=-\sum_gJ_g-Q_{\rm coll}+R_{\rm rec}
+S_{N,+}-S_{N,-}.
\]

Photoionization and collisional ionization reduce neutral H; recombination and
neutral inflow increase it.  The integrated ledger in
`proofs/FORCING_IDENTIFIABILITY_NO_GO.md` follows from this sign convention.

For `u,r>=0`, the H generator has nonnegative off-diagonal entries.  At
`N_HI=0`, `dot N_HI=r N_HII>=0`; at `N_HII=0`,
`dot N_HII=u N_HI>=0`.  Wolfram and SymPy independently confirm zero column
sums and these inward boundary signs.

## Limits

1. **Temporal resolution:** as `Delta t -> 0`, endpoint values and an interval
   integral do not converge to a unique forcing unless a boundary/source law
   supplies additional information.
2. **One node:** a known pointwise total fixes the only node current, but an
   endpoint-plus-integral representation still has nullity `K-3` unless the
   pointwise history itself is supplied.
3. **Many nodes:** fixed endpoints and pointwise macro total leave nullity
   `(N-1)(K-2)`.
4. **Optically thin HI:** `[1-exp(-sigma N)] ~ sigma N`; absorbed excess energy
   is cross-section weighted.
5. **Optically thick HI:** `[1-exp(-sigma N)] -> 1`; absorbed excess energy is
   number weighted.
6. **Primary G3:** source occupation is exactly zero.  Nonzero G3 atomic
   moments are operator-only auditors and may not be promoted to source
   heating.
7. **Zero current:** the positive null witness is local to strictly positive
   support.  Exact-zero support remains fixed and is not perturbed.

No unit, sign, or limiting check converts missing input information into a
unique forcing.
