# PHYS-MATH review: native Bianchi V calibration

First sequential review by Host Codex, 2026-09-05, after the single native run
and before the PHYS-MATH-CODE review. This is not an independent reviewer.
Task layers: validate, review, document. The existing BASS CONTRACT.json is
the execution contract; this evidence publication introduces no new gate.

## Short verdict

PASS for the declared generic exponential Bianchi V component calibration.
The actual native and process receipts both pass. All 12 required booleans
are true; the stored residual arrays contain 416 exact integer-zero entries,
including the package predicate and two calibrated counterexample residuals.
This is a bounded component identity result, not the general abstract bridge.

Source: BASS commit `477371143f15ef2625a7de21a5d178b09ffc1c32`, tree
`fe4c9f9b6deae0bf072dd553cd046c0a4a7801e3`. Source identities are in
SOURCE_IDENTITY_BEFORE.json; native raw output is in native/native.json.

## Assumptions and conventions

- Signature `(-,+,+,+)`, future unit normal `n=(1,0,0,0)`, unit lapse and zero
  shift, `tau=c*t`; all four coordinates have length dimension.
- `epsilon_123=+1` is retained as the REI convention. This coordinate-based
  native diagnostic does not separately exercise an epsilon/orientation map.
- Positive extrinsic curvature `K=+h h nabla n`, `q=-h T n`,
  `kappa_G=8*pi*G/c^4`, and `M=-C-kappa_G*q`, where `C=div K-grad tr K`.
- The metric is diagonal with spatial entries `exp(2 H1 tau)`,
  `exp(2 H2 tau-2 a0 x)`, `exp(2 H3 tau-2 a0 x)`. The full checks retain
  independent real `H1,H2,H3,a0`; each has dimension inverse length.
- Arbitrary symbolic normal-frame flux, density, pressure and Lambda are
  algebraic probes. No EOS, energy condition or Einstein evolution is imposed.
- The sentinel alone sets `a0=H1=1/ell`, `H2=H3=0`, `tau=x=0`, `ell>0`.

## Equation-by-equation audit

| Obligation | Exact-zero entries | Review |
|---|---:|---|
| PACKAGE_DEFINITIONS | 1 | Actual xTensor/xCoba package definitions are present. |
| NORMAL_POSITIVE_K | 10 | `n.g.n=-1`; `K_ij=(partial_tau h_ij)/2=Gamma^0_ij`. |
| RAW_TO_BASS_RIEMANN | 256 | Native all-lower X plus derivative-first coordinate B vanishes. |
| PHYSICAL_RICCI_BASS | 16 | Physical native Ricci equals the B-view contraction. |
| PHYSICAL_RICCI_XACT | 16 | Physical native Ricci equals the X-view contraction. No Ricci negation is used. |
| GAUSS_POSITIVE_K | 81 | Full spatial array uses positive K and the explicit X-to-B sign. |
| CODAZZI_POSITIVE_K | 27 | Full spatial/normal array agrees with the spatial covariant derivative of K. |
| MIXED_RICCI | 3 | `R_i0=C_i` for the specified normal and curvature slots. |
| MOMENTUM_MATTER | 3 | Direct native Einstein projection equals `-C-kappa_G*q`. |
| HAMILTONIAN | 1 | `E_nn=(R3+K^2-K_ij K^ij)/2-Lambda-kappa_G*rho`. |
| NONZERO_BIANCHI_V | 1 | Actual new-minus-old geometric momentum discrepancy is `4/ell^2`. |
| WRONG_RICCI_SIGN | 1 | The nonzero Ricci sum is `-4/ell^2`, detecting a wrong physical-Ricci negation. |

## Dimensional, sign and limit checks

Curvature, the K wedge, and a spatial derivative of K have dimension `L^-2`.
`kappa_G*q`, `kappa_G*rho`, and Lambda have that same dimension. The native
routine keeps kappa_G symbolic; it neither sets c=1 in the contract nor
substitutes a Hubble-normalized matter flux.

The matter tensor is `rho n_flat n_flat + n_flat q + q n_flat + p h`, so
`T_i0=-q_i` and `E_i0=R_i0+kappa_G*q_i`. Applying the negative projection
therefore gives `M_i=-R_i0-kappa_G*q_i`. This checks the unchanged matter sign
separately from the corrected geometric sign.

For this metric, the spatial divergence calculation gives
`C_x=a0*(H2+H3-2 H1)` and zero y/z components. At the sentinel, `C_x=-2/ell^2`;
the new and old geometric projections are respectively `+2/ell^2` and
`-2/ell^2`. Their difference is the actual receipt's `4/rEll^2`.
The Ricci sum counterexample is consequently `-4/ell^2` before its offset.

The symbolic family includes the flat limit `a0=H1=H2=H3=0`; taking `a0=0`
removes the mixed geometric carrier. These are analytic consequences of the
reviewed family, not additional executed runs. No initial/boundary-value
problem is solved. Full Gauss/Codazzi checks precede sentinel substitution,
so their PASS is not inferred from a rank-one-K zero-wedge sentinel alone.

## Fatal blockers and high-priority fixes

None found within this native calibration's declared mathematical scope.
No BASS source repair was made or is proposed for this successful first run.

## Safe claims and required limits

Safe: native xCoba curvature for this metric family agrees with the separately
assembled coordinate-Christoffel calculation under the explicit view and
physical-Ricci contractions, including positive K and the matter momentum sign.

Not established: the abstract four-projection bridge, all homogeneous types,
the exceptional VI_-1/9 native bridge, arbitrary lapse/shift, constraint
propagation, background evolution, or a cosmological prediction. REI #64/#65
remain separate oracle anchors, and BASS #129 is the reference anchor, not this
run's source. BASS owner registry/consumer adoption is not implied by this PASS.

## Minimal next action

Publish the unchanged first-run evidence and complete the sequential code and
visual readbacks. The next distinct mathematical integration task is a
versioned BASS-owner registry/consumer amendment; it is not executed here.
