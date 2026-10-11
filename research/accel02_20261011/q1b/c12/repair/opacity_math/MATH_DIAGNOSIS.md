# Attempt66: positive quadrature refinement is the appropriate numerical candidate

The preserved C2_FULL002 attempt66 failed before any native gas call at the first-map incident response comparison for angle0, cell66. The saved64/128 response errors are approximately1.94e-7 in HeII K0,1.95e-7 in HeII KE, and3.236469e-7 in both direct and ABI HeII photoheat, against the unchanged1e-7 criterion. This lane only inspected saved failure/code and the independently extracted cell; no source integration, native SIGMA call, gas call, map, or old test was executed here. The68 immutable dependencies match.

## Threshold and support analysis

The incident support is q in[54.42,58.10903285705145] eV with R=0.9982358115277721. Therefore the physical HeII threshold54.42 eV is at q_t=54.42/R=54.51617681067934, strictly inside the cell. The unchanged code explicitly splits the probability integral at this threshold. Its CDF coordinate is0.17987328151299256. HI and HeI thresholds lie below the entire support. The pinned Rust Verner formula has no additional branch, resonance or internal data knot inside this cell: HeII sigma is exactlyzero below54.42 and the same smooth active fit at/above54.42. Chemical chi_HeII=54.41776 is a heat subtraction constant, not another opacity branch.

The observed traceback is the ordinary probability-quadrature path, not the C11 thin-support certificate. The coordinate indicator4.66962944467772e-13 is far below1e-7. Agreement of the direct and ABI heat *errors* near3.236469e-7 identifies common integral underresolution rather than an ABI subtraction-only defect. These observations do not justify removing threshold splits or weakening a heat denominator.

## Derived conditioning mechanism

The two-moment reconstruction gives p=-112.222779898321 and L=ln(b/a)=0.06558938927989415, so pL=-7.3606235968228555. For p !=0 its inverse CDF is

q(v)=a*[1+v*(exp(pL)-1)]^(1/p),  0<=v<=1.

For this negative p, the analytic continuation has a branch singularity at

v_star=1/[1-exp(pL)]=1.0006362063530523.

Although the physical opacity is smooth on each threshold side, q(v) becomes rapidly varying close to the upper probability endpoint. The singularity is only0.00063620635305237 above1. On the threshold-active piece[v_t,1], mapping to[-1,1] puts this singularity at x_star=1.001551483054292. The associated candidate ellipse parameter is rho=x_star+sqrt(x_star^2-1)=1.0572773586261641. This explains why64/128 can converge slowly in a cell whose physical-energy fit is smooth. The numbers rho^(-128),rho^(-256),rho^(-512) in `QUANTILE_CONDITIONING.json` are conditioning indicators only: constants and all complex singularities were not bounded, so they are not error certificates.

## Consistency of increasing positive quadrature order

For fixed strictly interior moments, finite p and fixed positive R,N, q(v) is continuous on[0,1], and each native response has finite one-sided limits on the threshold-split pieces. Positive Gauss rules on these compact pieces converge for the resulting continuous integrands. The construction normalizes positive weights and applies an exponential moment fit exp(eta*xi), where xi=(q-a)/(b-a).

In the limiting continuous distribution, eta=0 has the required mean. The derivative of the tilted mean with respect to eta is Var_eta(xi)>0 for a nondegenerate strict-interior cell. Consequently, as the uncorrected quadrature moments converge, the local fitted eta converges to0 by the implicit-function argument. Moment-fitted positive rules therefore converge to the same underlying power-law closure rather than a different physical distribution.

For finite h>=0 and finite nonnegative absorber densities, the backward-Euler survival factor1/[1+h*c*sum(n_i*sigma_i)] is finite, positive and continuous separately on the same threshold pieces. The same consistency statement applies to survivor number/energy, ionization kernels, direct heat and absorbed counters. This argument is conditional on the already enforced finite-domain and strict moment-fit checks; it does not assert uniform finite-order accuracy over all later gas states or global trajectory accuracy.

Thus increasing the positive quadrature pair, retaining actual moment fitting, threshold splits, exact-zero handling, direct/ABI heat comparisons, pointwise pairing and1e-7 component thresholds, is a mathematically valid repair candidate. A128/256 pair is the natural next bounded evaluation. It is not automatically accepted: actual new incident and attenuated comparisons must pass. Any retry must preserve the first failure and use a new declared quadrature policy; no hidden global tolerance change or photon state change is justified.

## Decision and exclusions

**Derived conclusion:** there is no identified missing physical breakpoint. The dominant concrete mechanism is probability-coordinate underresolution caused by a steep reconstructed power law and a nearby inverse-CDF branch singularity. A positive-order refinement is consistent with the same provider/closure and should be judged by the unchanged actual gates.

**Not claimed:**128/256 necessarily passes, a rigorous finite-order error bound, full gas/newton acceptance, full-history convergence, or permission to replay completed intervals. Those decisions belong to the separate exact-cell implementation evidence and subsequent genuinely new continuation.

## Separately supplied exact-cell evidence

The implementation owner subsequently supplied `opacity_candidate/evidence/ORDERS66/RESULT.json`: the saved64/128 maximum3.2364693116791835e-7 was reproduced, while128/256 gives1.397079568220693e-10. Fitted eta decreases from7.441958869847144e-6 at64 to2.9188189277352895e-9 at128 and-1.1259601856248816e-13 at256, consistent with the same-closure limit above. That lane used3 SIGMA calls/896 energies and zero gas/maps. These are independently supplied numerical results, not new calls by this mathematical lane. The bounded fallback implementation and attenuation checks remain the implementation owner's responsibility.
