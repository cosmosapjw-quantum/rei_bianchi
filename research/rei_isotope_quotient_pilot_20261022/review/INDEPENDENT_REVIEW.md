# Independent quotient review

Reviewer role: independent theory/code/result review; implementation and repair authorization remain with the controller. Requested tier: Astra; runtime model identity is not exposed. This reviewer executed zero IVPs and did not modify implementation, input, solver policy, or production paths. Initial review reads the inherited and new frozen contracts, repository AGENTS.md, actual atomic/transport/runner code, point-check JSON and both profile NPZ/JSON files.

## Theory decision

PASS for bounded execution under the selected atomic test-fluid closure. Same-element electronic generators and identical initial conditional fractions define an invariant equality subspace even with the shared electron density. Summing isotope abundances before forming the common electron functional gives exactly nine conditional entries, with the six populated isotope vectors reconstructed into eighteen entries and the absent neutron/tritium slots retained in the twenty-one-population census. This is not an isotope-spectroscopic model or a nuclear network.

For F=(P+n_e R)f/H, differentiation at fixed transport state gives J_ff=(P+n_e R+(R f)w^T)/H. The outer product is essential across elemental blocks. Transport dependence gives J_fy=-F d(log H)/dy; the only direct fraction-to-transport derivatives enter the photon towers through Thomson damping, plus the optical-depth row. The reviewed implementation contains these terms and uses correct charge/recombination direction and the elemental abundance weights.

The metric convention fixes sigma=diag(-s,-s,2s), pi=diag(-p,-p,2p), contractions 6s^2, 6p^2 and 6sp, and dot(s)+3Hs=K sum(p). Thus full signed S=sqrt(6)s/H and P=sqrt(6)Kp/H^2 are correct. Signed stresses must be summed before taking norms.

The requested initial Sigma range 0..0.6 is physically admissible in the frozen background: its maximum shear contribution to H^2 is Sigma^2/6=0.06. The selected angular distributions W=1+A P2 are positive at amplitudes -0.8..1.6, with continuum minimum 0.2 initially. This initial positivity does not replace evolved finite-tower sampled positivity or L24 controls.

The matter/radiation stress axes are much smaller than the shear range. Actual point-check initial values are:

| Sigma0 | P_m minimum | P_m maximum | P_r minimum | P_r maximum |
| --- | --- | --- | --- | --- |
| 0 | -0.0005468874345897007 | 0.0010937748691794015 | -0.002388555339655477 | 0.004777110679310954 |
| 0.6 | -0.0005140741885143187 | 0.0010281483770286375 | -0.0022452420192761485 | 0.004490484038552297 |

Therefore plots may show Sigma0 up to 0.6 and these actual signed component axes. A demand for independently imposed Pi_m/Pi_r=0.6 would require changing the frozen source distribution/background and is not admitted here.

## Original-source checks

The reviewer reopened the authors' primary pages and table descriptions:

- https://www.pa.uky.edu/~verner/rec.html
- https://www.pa.uky.edu/~verner/dima/rec/table.txt
- https://www.pa.uky.edu/~verner/photo.html
- https://www.pa.uky.edu/~verner/dima/photo/photo.txt

The RR description identifies coefficient a in cm^3/s and temperatures in K, and explicitly gives HeI a validity 3 K<T<10^6 K with 2.5% rms. The photo table description gives threshold/maximum energy in eV and cross-section normalization in Mb. The code uses the selected HeI a row, total RR, six product-labelled charge transitions, and 1e-22 m^2/Mb in the spectral integrals. The supplied 5..60 eV UV lies below LiII/LiIII thresholds and below the LiI fitted upper bound 64.39 eV. Zero nominal high-Li photo channels do not remove their recombination operators. None of these sources validates isotope-specific equality beyond the expressly selected approximation, a closed thermal model, or the nuclear target.

## Existing profile evidence

The reported point checks contain 24 deterministic positive-fraction points; maximum scaled quotient RHS mismatch is 4.66e-16, photon spectral 64/128 relative difference 4.92e-14, and chemical-column Jacobian mixed difference 2.63e-8. These are below their frozen numerical thresholds, subject to the targeted evidence/gate repairs below.

Read-only reanalysis of saved arrays, without rerunning either solver, found:

- All eighteen reference conditional fractions versus the duplicated nine-vector: maximum absolute difference 3.902483336482021e-9, below 2e-7.
- Same-element reference vectors differ by at most 4.440892098500626e-16.
- Massive comoving number relative drift: 7.771561172376096e-16 in both profiles.
- Saved state arrays are finite and have dimensions 257x49 and 257x58.
- Reported tau difference is 6.229318449957333e-11; shear/stress differences are below 5e-21.
- Quotient run: 6.1291 s wall, 6.0439 s CPU, nfev3383/njev163/nlu342, peak RSS65568 KiB. Reference: 13.6250 s wall, 13.4240 s CPU, nfev3473/njev170/nlu354, peak RSS66080 KiB. Pair total: 19.7781 s wall/19.4920 s CPU.

These existing profiles may be retained. The measured pair supports the resource estimate for a bounded sweep, and does not establish a general speedup claim.

## Bounded findings and minimum repair

1. **Reference shared-electron consistency and full-vector comparison.** `Coupled.details` computes reference transport/chemistry ne from all18 fractions but constructs the point used by tau and diagnostics from representative9 fractions. `profile` compares only representative9. Impact: the reference operator is inconsistent away from the invariant equality subspace, and its comparison did not explicitly exercise every reference fraction. Minimum repair: carry actual reference ne into tau/diagnostics and compare all18 against duplicated9. Existing-profile same-element mismatch4.44e-16 and all18 agreement close the practical profile impact; no repeat IVP is required.
2. **Duplicate massive moments in hybrid Jacobian.** Each transport perturbation calls `transport.rhs` and then separately `transport.geometry`. Impact: duplicated expensive moments undermine the explicitly required optimization. Minimum repair: obtain the perturbed geometry from `rhs(...,with_geometry=True)` and reuse H. No physical/solver change.
3. **Point-check evidence and relative denominator.** `electron_rel` uses max(1,abs(ne)), becoming absolute error at these densities. The Jacobian numerical comparison covers chemical columns but not analytic J_fy/tau_y, and only maxima/config subsets are saved. Minimum repair: use a genuine nonzero-density relative denominator, check the analytic geometry cross blocks, save exact point vectors and residual arrays in one compact artifact. Include explicit RR row/formula checks and high-charge recombination direction in the existing finite gate; no extra campaign.
4. **Massive-number trajectory gate.** The receipt's number gate covers photon/neutrino monopoles but not saved `matter_number_comoving`. Minimum repair: add its relative drift to the existing gate. Existing profiles already satisfy it by saved-array reanalysis.

These are finite implementation/verification repairs, not a reason to change source, closure, tolerances, angular policy, or claim ceiling. Controller authorization routes any repair to the implementation worker. Once those concrete items are checked, proceed directly to already-authorized controls and missing nominal cases. Final scoped result admission waits for actual trajectory/control outcomes and readable data-backed plots. Maximum possible admission remains PASS_SCOPED_PRELIMINARY_ATOMIC_TEST_FLUID; full nuclear/thermal/observational/native-production claims remain outside scope.

## Targeted-repair readback and execution transition

The reviewer subsequently read the repaired code and immutable `point_checks_v2.json`, without executing new point checks or IVPs. The genuine relative electron maximum is 3.49e-16. The mixed Jacobian maximum remains 2.63e-8, including explicit atomic-to-geometry cross-block checks at 1.54e-8 and optical-depth-to-geometry checks at 2.72e-12. Full residual arrays and conditional point vectors are preserved. Reference tau now uses the all18 electron closure, Jacobian perturbations reuse the geometry returned by the transport RHS, and the massive-number gate is present. Exact atomic input hashes are checked. These close the substantive pre-sweep findings.

Decision: **PASS_TO_BOUNDED_CONTROLS_AND_MISSING_NOMINALS**, retaining the existing profile. Final runner assembly must consume the current point evidence and compare all18 in future profile commands; this is the same finite implementation completion, not a new scientific gate or reason to rerun the valid saved profile.

One nonblocking diagnostic issue was returned to the controller: `background_J_m3=3H^2/K` includes shear and Lambda as an effective critical density, whereas the frozen equation separates material epsilon, Lambda, and s^2. The requested test-fluid energy ratio should use an explicitly declared material/background denominator, or publish a correctly labelled critical-equivalent ratio and the material ratio separately. This can be derived from saved states and does not alter any trajectory.

## Final result and figure admission

**PASS_SCOPED_PRELIMINARY_ATOMIC_TEST_FLUID.** The completed sweep receipt and strict summary establish 79 nominal trajectories, three tighter L24 controls, and one full18 reference: 83 IVP attempts, no failed or unlaunched cases. The three controls have maximum shear discrepancy 8.702705847629666e-10 and maximum fraction discrepancy 3.3929270504273745e-9, below the frozen 2e-5 criterion. The retained profile's all18 discrepancy is 3.902483336482021e-9, below 2e-7.

The final saved-output summary reports minimum populated fraction 0; maximum isotope sum residual 1.7763568394002505e-15, baryon sum residual 1.3322676295501878e-15, electron closure relative error 6.313513717271623e-16, and massive-number relative drift 7.771561172376096e-16. Minimum brightness over the sampled outputs/257-angle grid is 0.05703690384369109. This is sampled finite-cutoff evidence, not continuum positivity. The cumulative per-case CPU sum is 211.722562001 s; bulk-stage wall is 46.815131249 s and the receipt's conservative cumulative stage-wall sum is 80.381213379 s. Import/check/render overhead is not included in the CPU sum; no general speedup claim is admitted.

The final renderer reads all79 nominal and3 control raw files and produces thirteen PNG/PDF figure pairs, selected-source CSV, control-difference CSV, and a plot report under `pilot/figures_final`. The reviewer visually inspected the shear/stress history, full signed stress, five-slice final-S maps,21-census redshift panels, three-control panel, energy panel, a cancellation history, a negative-orientation history, and the isotropic-response panel. These preserve signed addition, realized axes, exact zero/absent populations, elapsed-time/redshift meaning, and the prescribed-thermal/UV claim boundary. The one lithium-charge caption error was repaired to LiIII/IV = q2/q3 = Li2+/Li3+; the overlapping map ticks were repaired. Both corrected images were visually read back. No further figure repair is required for this scope.

The final energy figure now distinguishes atomic thermal+binding energy divided by declared material density from UV divided by critical-equivalent density. The selected strong-case material ratio reaches 2.8979336435676505e-9. The all-case summary value 3.441216023624155e-9 retains the original critical-equivalent denominator and must be described as such; neither ratio is a trajectory error bound.

All bounded review findings are closed for this task. Stop review expansion and proceed to the controller's authorized delivery/publication steps. This decision does not issue native-production admission and does not establish nuclear reactions, independent thermal/radiation closure, isotope-resolved spectroscopy, observational reionization validity, global angular convergence, or a continuous-domain certificate. No further IVP, test rerun, or process-only review cycle is requested.
