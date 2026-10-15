# Native AXBI signed covariant free-flight versus repeated energy-node projection

2026-10-15 KST. Source-scoped Rust execution; EXPLORATORY/NUMERICALLY_CHECKED, not a replacement for original collision and chemistry.

## Source identity

- Separately built original-repository crate: librei_microphysics-2db3552c92b16edc.rlib, SHA256 44b7ea58b04b58e521a2db2686a4b248040414a733120c22689e857ed40d2a3f.
- Reference photon: rei_microphysics::axbi_q_reference::CovariantPhoton, preserving covariant spatial k_i=a_i E n_i without intermediate grid reprojection.
- Production comparator: rei_microphysics::axbi_driver::Driver::geometry_map, performing two-neighbor barycentric energy-node projection at every call.
- Compiled signed experimental probe binary SHA256 82aadb598530178494350109244230866228411d0b7bdafa308a92a8d903e6fb.
- Production source, compiled closure, original histories and live owner HEAD were not edited.

## Direct native experiment

From mean zbar=20 to 19.8, initial photon energy 16.3651518618212 eV at energy-grid index 5. The exact unprojected characteristic endpoint energy remains above 13.6 eV for all q.

| Signed q | Exact E at endpoint [eV] | One-map relative bias | 4096-map surviving mean bias | 4096-map photon boundary loss |
|---|---:|---:|---:|---:|
| -0.005 | 16.2086009979861 | 0 | +1.40120e-6 | 8.63203e-6 |
| 0 | 16.2092932726610 | 2.19e-16 | +1.37193e-6 | 8.45016e-6 |
| +0.005 | 16.2099855983144 | 0 | +1.34313e-6 | 8.27129e-6 |

The six signed-q run rows independently check original Driver::residuals photon-number and energy ledgers to less than 1e-12. Despite correct ledgers and correct single-map first energy moment, repeated remaps remove photons below fixed spectral support and shift the surviving mean. This is numerical free-flight spectral error, not physical photoabsorption.

## Analytic witness, not an exact Bianchi error formula

For uniform additive grid spacing ΔE, shift αΔE twice with projection each time (0<α<1/2): node masses ((1-α)^2, 2α(1-α), α^2). A single projection after shift 2αΔE gives (1-2α, 2α, 0). Both conserve total number 1 and mean shift -2αΔE.

Variance difference: Var(Rα ◦ Rα) - Var(R(2α)) = 2α²(ΔE)² > 0.

Wolfram and Python fractions.Fraction confirmed exact 2/25 for α=1/5, ΔE=1. This is a local mathematical counterexample to projection semigroup preservation, not an analytic bound on the true anisotropic null transport errors.

## Evidence and scope

- axbi_exact_characteristic_vs_remap.rs: source for signed native probe.
- results/REMAP_VS_COVARIANT_CHARACTERISTIC.csv: six original crate executions.
- results/REMAP_SEMIGROUP_LEDGER.csv: 48 independent geometric reprojections, maximum count ledger residual 3.1086244689504383e-15 and energy ledger residual 1.4635341549773528e-13 eV/H.
- remap_semigroup_identity.py and results/EXACT_REMAP_NON_SEMIGROUP.json: mathematical proof witness.
- results/RAW_SOURCE_SHA256_MANIFEST.json: 167 raw evidence file identities including nine real native ODE runs.

Unresolved: global ODE error, source thermal and photon collision closure, true role of reprojection in x_HII drift. Do not infer that this defect alone causes the noncontracting tolerance-refinement results.

Constructive next lane: exact covariant photon energy characteristics with controlled absorption/ionization and threshold ledgers, compared with frozen two-neighbor projection under the same physical rates; run two-dimensional convergence in proper-time steps and photon energy-grid resolution before changing production source.
