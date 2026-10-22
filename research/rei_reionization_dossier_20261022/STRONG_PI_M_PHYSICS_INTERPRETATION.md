# Interpretation of the measured strong matter-stress response

The new calculation answers the enlarged question affirmatively within its stated model: sufficiently stronger, positive-distribution matter stress produces ionic-fraction changes separated from the observed numerical-control discrepancy. The previous unresolved response was a finding about the original cold component and its small admissible stress range. It was not a general absence of matter-stress influence.

This note reads the completed `strong_pi_m/STRONG_RUN_RECEIPT.json` and the frozen transport/atomic equations. It adds no integration or parameter search. The receipt records exactly five new IVPs, zero old reruns and 128.4184 CPU seconds. It is an interpretation of the measured experiment, not a substitute for the independent implementation review.

## Measured result and resolution language

Every difference below is measured at common saved redshift relative to the **new semi-relativistic family's own zero-stress anchor**. The initial component parameters are f_m=.3 and m/Tref=3, with zero initial shear and radiation stress. All nominal cases matched initial density, mean pressure, particle number and H to rounding; the largest reported relative mismatch was 4.44e-16.

| Initial Pi_m | max over z and charge channels of abs(Delta f) | max abs(Delta f) / Pi_m² | Ratio to declared comparison scale |
|---:|---:|---:|---:|
| .01 | 5.4664637e-8 | 5.4664637e-4 | 16.11 |
| .05 | 1.3657044e-6 | 5.4628175e-4 | 402.52 |
| .1 | 5.4551783e-6 | 5.4551783e-4 | 1607.81 |

The strongest nominal/refined control difference is 2.3126512e-10 in conditional fractions. The frozen comparison scale is the larger inherited control discrepancy, 3.3929271e-9, whose different-family provenance remains explicit. All three tested nonzero cases exceed the frozen ten-times-scale criterion. Thus .01 is the **smallest tested initial Pi_m** meeting that rule; it is not an inferred detection threshold for untested values, an observational detection, or an all-domain convergence result.

The leading difference peaks at the saved redshift z=10.695792370889016. It is a paired Li I increase and Li II decrease. The maximum channel index alternates between these two numerically equal conservation partners; this is not a physical reversal of the response. At Pi=.1, the Li II peak is -5.4551783e-6 in the nominal run and -5.4550770e-6 in the refined run, with the same sign and a 1.0125656e-10 difference. Hydrogen and helium also respond; their largest channel differences at Pi=.1 are about 2.43345e-6 and 3.20300e-6 respectively. The maximum electron-per-baryon difference is 1.98264e-6, and the endpoint optical-depth difference is 2.04403e-6.

These are absolute conditional-fraction differences. The largest per-isotope conditional Li response is not the largest absolute charge inventory: primordial lithium is scarce. Late endpoint fractions mostly reconverge, so the small final ionic difference must not be used to erase the larger transient response.

## Why a leading quadratic response is expected in these equations

The following is a local perturbative interpretation around this family's isotropic zero-stress solution. Let epsilon=A_m. Its relation to the initial signed physical stress is linear, P_m0=0.07660059131801567 epsilon, so the same power counting applies to small Pi_m0 on the chosen positive branch.

1. **Matter quadrupole and shear begin at first order.** The initial angular distribution is 1+epsilon P2(mu), while initial b, shear and radiation quadrupoles are zero. The anisotropic massive pressure is first order in epsilon. In `CompactTransport.rhs`, b'=s/H and the shear equation is sourced by the sum of massive, photon and neutrino anisotropic pressures. Consequently b and s are O(epsilon). Radiation quadrupoles induced by this shear are also O(epsilon). Their backreaction changes the first-order shear evolution but does not directly create a first-order scalar monopole.

2. **The massive energy monopole has no first-order perturbation about the isotropic anchor.** At b=0 the particle energy depends on q, not direction, so its integral against P2 vanishes. The derivative of particle energy with respect to b at b=0 is proportional to (1-3mu²), whose isotropic angular average also vanishes. Therefore both partial derivatives rho_epsilon and rho_b vanish at epsilon=b=0. Since b=O(epsilon), the first nonzero density differences are of the forms epsilon*b and b², hence O(epsilon²). The same angular argument applies to the scalar mean pressure. It is valid for the actual finite-mass momentum integrals; it does not require a cold-fluid approximation.

   Equivalently, the collisionless energy equation includes the anisotropic-work term 6 s pi_s in the present LRS convention, where sigma_ij=diag(-s,-s,2s) and anisotropic pressure is diag(-pi_s,-pi_s,2pi_s). Both factors are first order. The changed isotropic pressure between the cold and semi-relativistic families is already part of the new zero-anchor solution; it is not counted as an anisotropy perturbation.

3. **Radiation energy monopoles change at second order.** The implemented even hierarchy has the exact monopole identity E0'=-2(s/H)E2 and no Thomson damping of the monopole. Initial E2 is zero; the induced E2 and s are each first order, so the energy-monopole correction is second order. Photon Thomson damping and neutrino free streaming give different quadrupole histories but preserve this power counting. Radiation number monopoles are conserved by the declared hierarchy.

4. **The expansion-rate correction is second order.** `CompactTransport.geometry` evaluates H² from dust, the actual massive energy monopole, photon/neutrino energy monopoles, the cosmological constant and s². The specified dust/baryon background is unchanged. Every anisotropy-induced correction just listed, including s², is O(epsilon²). Thus delta H is O(epsilon²) around this matched isotropic anchor. The elapsed-time correction is also second order because dt/dx=1/H.

5. **The atomic fraction equation transmits that scalar correction.** `AtomicQuotient.point` evolves f'=G(f,T(x),gamma_UV(x),n_B(x))f/H. The prescribed gas temperature, baryon density and external UV source are common to the matched cases, and the nonbaryonic quadrupole has no direct atomic-rate coupling. Linearization around the zero-anchor atomic trajectory has a homogeneous first-order equation for delta f with zero initial perturbation, because delta H has no first-order part. Its first-order solution therefore vanishes. The leading forced atomic response is O(epsilon²), with electron-density/recombination feedback included in that same atomic Jacobian.

This argument checks the massive monopole and the radiation closure, rather than assuming that only the explicit shear-squared term matters. It is a formal local consequence of the specified equations and matched isotropic initial data. It does not establish that the leading coefficient must be nonzero for every observable or redshift.

## Relation between the argument and the finite measurements

The measured values of max abs(Delta f)/Pi_m² differ by about 0.21% across the three tested nonzero stresses and are close to 5.46e-4. They are consistent with the leading quadratic response derived above. This is a finite-range numerical pattern, not a globally fitted law or a uniform analytic error bound. The statistic is a maximum over a saved grid, so it is not itself an analytic local observable; here its dominant Li I/Li II peak occurs at the same saved redshift in all three cases.

Exact evenness under A_m to -A_m is not implied. In this LRS geometry the positive and negative quadrupoles are not generally related by a rotation that exchanges all principal stresses, and higher-order mixed terms can occur. The quadratic leading term does not authorize a universal sign symmetry or exclude cubic corrections. A nonzero initial shear/radiation quadrupole, a changed scalar source at first order, a different angular distribution, direct anisotropic atomic couplings or solved nonthermal/thermal feedback could alter the leading power counting. None of those changes was part of this test.

## Required dossier conclusion

A suitable conclusion is: “The original cold-component sweep did not resolve its small matter-stress response. A separate, density- and mean-pressure-matched semi-relativistic component family with initial Pi_m=.01,.05,.1 gives maximum conditional ionic-fraction shifts from 5.47e-8 to 5.46e-6, separated from the declared observed numerical-control scale. Their near-quadratic growth is consistent with stress inducing shear at first order and scalar expansion/ionization changes at second order around the isotropic anchor.”

The new component is a controlled physical-distribution experiment, not an observationally admitted replacement cosmology. The independent nuclear tracer remains a separate conditional all-bare/instantaneous-thermalization calculation, with unresolved T charge partition. The displayed ionic response and its quadratic interpretation do not improve that nuclear transport closure or create a fully coupled reionization prediction.
