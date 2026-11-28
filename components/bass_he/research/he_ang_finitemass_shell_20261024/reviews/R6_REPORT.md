# Independent R6 — HE-ANG-FINITEMASS-SHELL

Date: 2026-10-24. Reviewer: separate `independent_review` Astra role requested by the user; actual runtime model identity is not independently observable.

**Verdict: PASS for the declared nonrelativistic kinematic shell contract.** No current mathematical blocker or required theory correction was found. The root may freeze this snapshot and proceed through its existing R7/B1 gates. This receipt does not admit a physical amplitude, recoil distribution, or event cross section.

## Snapshot, method, and source scope

- `THEORY_KO.md` SHA256: `9a2d927f5a04bbac6e0e6db759dad39fe950c08aae31fa948d2ca9ea47343a7b`.
- `FROZEN_CONTRACT.json` SHA256: `1e19f1f91f7003f60427f616c0be4473f8d0e97867bc92f81cc6667fcfc6a2b1`.

I read the actual next3 BASS_HE AGENTS, the next3 source report, theory, and contract. I independently performed algebraic substitutions, sign classifications, delta-measure integrations, moment contractions, and rational hand checks. I visually read the private Kadyrov source renders for journal pp.1527–1528 (PDF pp.12–13). No scientific code, test, import, quadrature, renderer, remote evaluator, or old suite was executed by this reviewer. No theory or contract was edited; no budget was allocated or changed.

The primary source is Kadyrov et al., Annals of Physics 324 (2009), DOI 10.1016/j.aop.2009.02.003, §3.1; the supplied published-PDF identity is `c7627a718193fc1ab0181d1c7fbabdc334bcf53a28e3a0870c45cd9827da9165`. The page images confirm the two reduced masses, canonical Jacobi convention, internal free Hamiltonian, and the energy identity immediately following Eq.79. That identity is unnumbered: Eq.79 itself defines the pair potential. The source does not supply this unit's lab detector Jacobian, counting factor, spin prescription, or hydrogen-specific physical amplitude. Those boundaries are correctly retained.

The decimal mass is treated as a declared fixed numerical fixture, with uncertainty explicitly not propagated. After the root supplied its actual NIST retrieval receipt, I read `finitemass_ops/private_survey/NIST_WEB_SEARCH_RAW.json` and the selected `source/MASS_CONSTANT.json`. The official NIST result explicitly reports the 2022 CODATA proton-electron ratio 1836.152673426 and standard uncertainty 0.000000032, matching the contract. The receipt also preserves the later malformed bare-CGI access as an access failure, not a contradictory value. This is independent inspection of the retained primary retrieval, not a duplicate web query. Neither the exact kinematic derivations nor the fixture semantics depend on a latest-constant claim.

## Independent derivation assessment

### Lab, COM, and Jacobi maps

The affine momentum map has per-component linear matrix `[[1,0],[1/(M+1),1]]`; determinant one gives unit six-dimensional Jacobian. Substituting the inverse map recovers both input electron momenta and `Q=P-pA-pB`. It gives the total momentum P exactly. Expanding the kinetic energy cancels the mixed k/q and internal/COM terms, leaving `P^2/(2T)+k^2/(2mu)+q^2/(2nu)` with `mu=M/(M+1)`, `nu=(M+1)/(M+2)`, and `T=M+2`.

Since `P^2=2E0`, internal available energy is `E0-B-E0/T=nu E0-B`. Thus the support threshold is `B/nu`, not the fixed-center B. For the separate binding mode `B=mu/2`, this becomes `M(M+2)/[2(M+1)^2]`. The source internal E must therefore be identified with epsilon, not laboratory projectile kinetic energy. Electron atomic units and the explicit exclusion of the binding mass defect keep this Galilean transformation consistent.

For epsilon>0 the scaled internal coordinates cover S5 without an extra label quotient. Below threshold there is no shell. At threshold the support collapses to common velocity `P/T`, and the dimension-six delta-shell measure tends to zero. The stated zero threshold volume is the natural limiting shell measure; it does not assign a nonzero point weight at a critical energy.

### Conditional sphere and radial roots

Completing the square in `pB` independently gives center `c=(P-pA)/(M+1)`, quadratic coefficient `alpha=(M+1)/M`, and residual H as written. For H>0, translation to the sphere center gives radial delta integral `rho^2/(alpha rho)` times area `4pi`, hence `4pi rho/alpha`. H<0 is empty, while the collapsed H=0 conditional shell has zero limiting measure.

On a detector ray, the equation is `alpha p^2/2-beta p+gamma=0`. The discriminant is `beta^2-2alpha gamma`; root product is `2gamma/alpha` and root sum `2beta/alpha`. These establish all listed cases:

- Negative discriminant: no real radial roots.
- Positive discriminant and negative gamma: opposite root signs, hence one positive root.
- Positive discriminant and positive gamma: equal root signs, determined by beta; two positive roots only for beta>0.
- Zero gamma: one zero endpoint and root `2beta/alpha`; its positive-interior status follows beta.
- Zero discriminant: the double root is `beta/alpha`, with the stated positive, zero, or negative classification.

There is no omitted beta=0, gamma>0, positive-discriminant case: it is algebraically impossible. At each simple root `|dF/dp|=sqrt(D)`, so the outgoing radial measure is `p_j^2/sqrt(D)`. Since `d^3pA=pA dEA dOmegaA`, the full density is exactly `pA sum_j p_j^2/sqrt(D)`. Its dimension is that of the declared momentum-six per energy measure after division by the selected differential coordinates. Branch-specific W must be evaluated separately; symmetry or a single outgoing energy label does not justify discarding one branch.

### Fold fixture and regular integral

For the rational stress fixture I independently obtain `pA^2/2=1/16`, `r^2=9/8`, `gamma=1/8`, `H=5/32`, `c0^2=9/32`, and `rho^2=5/32`. Consequently the forward tangent satisfies `t_c=2/3`, and the axial roots are `(3sqrt(2) +/- sqrt(10))/8`, both positive. At the tangent the common positive root is `sqrt(2)/4`. The backward real roots, where present, are negative rather than outgoing branches.

For the general outside-origin sphere let `A=c0^2-rho^2>0`. Then `c0 t=sqrt(h^2+A)`, and `dt=h dh/[c0 sqrt(h^2+A)]`. The branch sum satisfies `p_plus^2+p_minus^2=2(2h^2+A)`. The proposed transformed integrand is therefore proportional to `(2h^2+A)/sqrt(h^2+A)`, with elementary primitive `h sqrt(h^2+A)`. Evaluation from h=0 to rho gives exactly `4pi rho/alpha`. The apparent radial divergence is integrable for constant W because the angular change of variables cancels the inverse h. This is not a proof for an arbitrarily singular amplitude; the theory explicitly avoids that extension.

### Full volume and sharing density

In mass-scaled six-dimensional coordinates the Jacobian is `8(mu nu)^(3/2)`. The radial integral of `r^5 delta(epsilon-r^2)` is `epsilon^2/2` and the unit S5 area is `pi^3`, giving `Phi=4pi^3(mu nu)^(3/2)epsilon^2`. As `mu nu=M/(M+2)`, the alternative form follows.

Independently integrating k first yields `4pi mu sqrt(2mu) sqrt(epsilon-q^2/(2nu))`; multiplying by `4pi q^2 dq` gives precisely the proposed one-dimensional integral. With `u=q^2/(2nu epsilon)`, its normalized factor is `sqrt(u(1-u))/B(3/2,3/2)=(8/pi)sqrt(u(1-u))`. This distribution belongs to W=1 kinematic measure, not ionization dynamics.

### Positive 76-node rule and recoil moments

The axis weights sum to 1/4 and the cube weights to 3/4. Sign symmetry removes every monomial with an odd coordinate exponent. For a fixed coordinate, the second moment is `2/48+(3/4)/6=1/6`; its fourth moment is `2/48+(3/4)/36=1/16`. For two distinct coordinates the mixed square moment is `(3/4)/36=1/48`. These are exactly the isotropic fourth-moment tensor coefficients on S5, so all polynomials of total degree at most four are covered. This finite positive rule is not a general-amplitude accuracy certificate.

For the recoil vector, the inverse map gives `Z=-sqrt(2mu epsilon)u-[M/(M+1)]sqrt(2nu epsilon)v`. Thus `LL^T=2epsilon[mu+M^2 nu/(M+1)^2]I=(4M epsilon/T)I`, agreeing with c*. The S5 moments then give `<Z^2>=c*/2`, `<(Z^2)^2>=5c*^2/16`, and `<(a.Z)^2>=a^2 c*/6`. Odd cross terms vanish. Dividing the variance of `2a.Z+Z^2` by `4M^2` yields exactly

`Var(ER)=2M P^2 epsilon/(3T^3)+epsilon^2/(4T^2)`.

The electron and recoil means follow from the same second moments. In particular their sum is `P^2/(2T)+epsilon=E0-B`, checking energy conservation without a fitted constant. Both terms in the recoil variance are nonnegative and have energy-squared units.

### Counting, infinite-mass limit, and physical scope

At fixed B and interior allowed outgoing energy, the infinite-mass limit yields one positive outgoing momentum and radial weight `pA pB`. The volume and recoil-energy moment limits are correct. A vanishing recoil energy does not imply a vanishing recoil momentum; that distinction is correctly explicit. Threshold and fold neighborhoods do not inherit a uniform convergence certificate from this interior limit.

The labelled-domain definition has no implicit amplitude, flux, spin, Fourier factor, or event-count correction. For symmetric W on the full labelled domain, division by two gives unordered events; energy-order restriction already performs that quotient except on a measure-zero tie surface. No automatic factor is appropriate for a fixed detector-labelled value. The finite-mass kinematics therefore cannot simply be inserted into prior fixed-center dynamics and called a source-consistent finite-mass amplitude. Parent SOURCE_INPUT_PENDING remains appropriate.

## Numerical contract assessment and disposition

The cancellation-avoiding quadratic formula correctly uses the root product for its companion root. Keeping zero endpoints separate and avoiding arbitrary merging is appropriate. The explicit unresolved discriminant band prevents silently classifying a near-fold binary64 result as either no support or a finite regular branch. In particular exact or rounded zero discriminants fall into the unresolved numerical route; mathematical double-root fixtures can still be checked symbolically or with exact coefficient tests. The contract must not be read as promising a finite binary64 coarea value at the fold.

This guard is a declared numerical policy, not outward-rounded interval arithmetic or a proof of correct classification under every possible overflow, underflow, or earlier coefficient cancellation. Its adequacy and the stated tolerances must be assessed on actual implementation outputs and the selected near-caustic controls in C9. The constant-weight conditional sphere gives a regular independent representation for the declared validation integrals. Direction normalization with recorded input norm keeps the detector-ray convention explicit.

No current actionable theory defect was found. No added execution, broadened suite, or new budget is requested. Existing costs, old failures and unknowns, other-owner OPEN items, prior source limitations, and future partial-mu-window metadata obligations remain unchanged. This PASS covers derivations and the frozen finite-fixture verification plan; it is not an observed numerical PASS or a full physical-event admission.
