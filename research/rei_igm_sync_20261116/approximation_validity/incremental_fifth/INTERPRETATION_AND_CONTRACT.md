# Incremental fifth-case contract and interpretation

Status: EXECUTED ON THE ADMITTED COMPLETE FIFTH HISTORY; independent fifth-case review pending. The four reviewed diagnostics remain unchanged and are reused. The new results establish complete baseline data generation but do not independently assert AX08 owner admission, AX11 convergence, or AX12 robustness.

The consumer requires the geometry owner's `rei.axbi.plus_complete_composition.v1` manifest, with an explicit `COMPLETE_COMPOSED_HISTORY` admission. It checks the complete-history bytes and SHA-256, case and q, z20→4 domain, boundary/checkpoint/physics identity declarations, and row count equal to observed terminal accepted count plus one. It independently rechecks all native fractions, charge, comoving density, scale factor, proper time and background H,s. The predicted row count is not an acceptance condition. A missing terminal or failed composition cannot create five-case outputs.

Only the new +0.01 history is reduced. The frozen four-case summary is hash-pinned and reused without recomputation. Existing PR374 sample arrays and the original interpolation, milestone and species-normalization methods are hash-pinned. The new product includes normalized species and electron abundances, proper time and temperature, +0.01 versus ZERO/−0.01 response, and odd/even estimates for q=0.005 and 0.01 on matched scale factor and matched elapsed proper time. The latter is elapsed time from each model's zbar20 surface, not a common cosmic-age assertion. Sample maxima are not continuous extrema. Response floors are not numerical-resolution certificates.

For any scalar X define O(q)=[X(+q)−X(−q)]/2 and E(q)=[X(+q)+X(−q)]/2−X(0). O(.01)−2O(.005) and E(.01)−4E(.005) are diagnostic amplitude comparisons. They do not prove a Taylor order, exact sign parity, or resolved signal. AX11 is required to compare paired time, angle and energy refinement errors against the original response targets.

## Forced fixed-background scope

The measured integral solves

\[
\dot{\delta s}+3H\delta s=\frac{8\pi G}{3c^2}\Delta P_{\rm omitted}[a,b],
\qquad\delta s(t_i)=0,
\]

with the saved a,b,H and source state held fixed. It is a forced fixed-background diagnostic. Varying the full shear equation at fixed proper-time coordinate instead gives

\[
\dot{\delta s}+3H_0\delta s=
\frac{8\pi G}{3c^2}[\Delta P_0+\delta\Delta P_{\rm response}]-3s_0\,\delta H.
\]

A closed linearized coupled calculation must determine δH, the matter/radiation responses and their initial constraints consistently. The subscript zero denotes the prescribed stress-free geometry; ΔP₀ is the omitted stress evaluated on it, while δΔP_response denotes the additional response to perturbed geometry and matter. Adding an algebraic δH or clock estimate after the forced integral does not supply the missing −3sδH feedback. The present package computes neither this coupled solution nor an abundance/temperature error bound. All four-case numerical values remain unchanged; this statement sharpens their scope.

## Why tiny scalar odd responses do not establish exact parity

The pinned original `axbi_driver.rs` source uses directional ray redshifts in `geometry_map` (lines372–391), local solid-angle Jacobians in `inject` (404–423), and energy-dependent absorption/photoheating summed over the angle-resolved stocks in `evaluate` (427–469). It does not replace that radiation operator by mean H alone. Its prescribed H(a) and clock are even in q, while b is odd; these are background identities, not a symmetry theorem for all scalar radiation or chemistry states.

The original half-sign histories have identical a/time nodes and opposite b. Direct targeted consumption finds max |Uγ(+)-Uγ(−)|=1.4090773e−10 eV/H, max |ΓHI(+)-ΓHI(−)|=1.0411651e−23 s⁻¹, and max |J2(+)-J2(−)|=0.0118999084 eV/H. Scalar chemistry differences are much smaller than the original scientific floors. These data do not support exact implementation-enforced parity.

A separate single angular-kernel calculation, with zero new trajectories, gives M(.005)−M(−.005)=−1.9047575761e−7, consistent with the analytic cubic term −32b³/21. Thus even a scalar energy monopole need not be exactly even in b. Axisymmetry only guarantees the appropriate direction-reflection symmetry; reversing shear eigenvalues (−s,−s,2s) is not an axis relabeling of the same tensor. Whether the observed small gas odd response is physically suppressed, numerically suppressed, or both remains unresolved pending AX11. No cause is inferred solely from its small magnitude.

## Execution and publication

Run the prepared consumer only after the complete composition manifest exists:

```sh
python incremental_fifth_case.py --history /absolute/path/to/SHEAR_PLUS_composed_002/history.csv --composition /absolute/path/to/PLUS_COMPLETE_COMPOSITION_MANIFEST.json --owner /absolute/path/to/research/rei_axbi_owner_loop_20261115 --four-summary ../results/FULL_SUMMARY.json --out results_five --full-abundance-out /absolute/private/path/SHEAR_PLUS_full_normalized.csv.gz
```

The output directory and full-abundance output must not already exist. A separate compressed full-native table retains all time-ordered species/electron/Y/proper-time/temperature rows and its normalization registry; the public manifest pins its exact bytes. The 5005-row aggregate is explicitly an inspection sample and does not replace this complete history. A new fifth-case independent review must consume the actual admitted native data. The existing independent four-case review is preserved and is not silently extended. Publication is owned by the parent and recorded with its actual receipt.
