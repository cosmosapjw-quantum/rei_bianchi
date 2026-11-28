# HE-ANG-PWBE-SPIN-AZIMUTH independent R6 review

**Verdict: PASS. The root theory can freeze as a source-defined fixed-center PWBE model with an independently derived unpolarized spin trace.** No current blocking mathematical or source-normalization finding. The six specified finite fixtures and tolerance are suitable for implementation; their numerical success must be established by actual C6–C8 results, not by this review.

Reviewer: separate `/root/independent_review`, Astra requested; actual backend identity is not independently observable. Date: 2026-10-24 UTC. Read-only scientific review under the previously read physmath-research-loop 1.0.0 common policy and R6 definition. No local scientific calculation, test, quadrature, solver, remote evaluator, old-suite replay, budget allocation, or recursive reviewer was used. Hand derivation, primary-document reading, and document SHA256 checks only. Written files are confined to this unit's reviews directory. Earlier TDCS54/CCC reviews are reused, not reopened.

## 1. Source identity and citation scope

Initial reviewed THEORY_KO.md SHA256: `a99d5fa6cea857f91b2d7a09a52d217e498571c36e60fd588585217c9ba2d960`. The six fixed numerical geometries and exact nodal prototype were additionally supplied directly by root for this review; they are assessed explicitly below.

Final freeze readback: root incorporated those same six geometries and the exact-zero prototype without changing the reviewed formulas. Final THEORY_KO.md SHA256 is `ba074c0750478230700c5b3df35c89814db41b786ae071e701ec25793a57ac9e`; FROZEN_CONTRACT.json SHA256 is `215b62de28cb840c55846e8936f777b4d32dba22d9e35d44da8503250d2267f0`. Read the final fixture paragraph and complete contract. Its APIs, source/count/measure restrictions, oracles, finite-fixture targets, no-clipping rule, preserved old budgets/unknowns, and root-controlled execution gate agree with this review. No code or scientific execution is claimed at freeze. Existing R6 conclusions stand unchanged.

Primary source checks:

- The actual Weigold PDF is FIAS-R-39, June 1978, despite the intake filename `weigold1979.pdf`. The title page text confirms authors/report/date. PDF SHA256 `aaa750d5d5f0652ba7e6090878f938174fc26268265c256022c4d9437c3a96a8` matches the record.
- Visually inspected `weigold_p21.png`, printed report page 18. Equations (19) and (20) show the direct nuclear subtraction and exact outgoing-argument swap. Equation (21) visibly prints the real bracket f²+g²−2fg, together with transition prefactor (2π)^4 k_A k_B/k_0 and differential energy dE_A. This review does not assert an intended author correction or equivalence to the unread 1979 journal text.
- Buică arXiv v1 PDF SHA256 `33c4a4c91244313dddd90d99fed986344d479cb0c1a91135a42f77d2f8345755` matches the source record. Read its extracted Eq. (19), Eq. (46), and accompanying statement of unpolarized incident projectile/hydrogen and unresolved final spins. Eq. (46) supplies the 1/4,3/4 decomposition and transition prefactor as a separately versioned cross-check. Its later erratum remains unread and is not presumed irrelevant; no step of the independent spin derivation requires that presumption.

The model retains exact-swapped PWBE exchange with its own nuclear subtraction. Buică's Born–Ochkur exchange lacks that swapped subtraction and is not substituted or treated as the same approximation. No source experimental angular table is transcribed or used for numerical accuracy admission. The report's adverse plane-wave comparisons in its measured range remain evidence about those comparisons, not a global exclusion theorem.

## 2. Independent transition-normalization derivation

For normalized hydrogen 1s, the unnormalized Fourier integral is 8π/(1+p²)². Multiplying by 1/√π from the bound state and (2π)^−3/2 from the outgoing plane wave gives 2√2/[π(1+p²)²], as in root Eq. (3).

The incoming/outgoing projectile plane waves contribute (2π)^−3. Fourier transforming 1/|r_0−r_1|−1/r_0 in r_0 gives 4π[exp(iΔ_A·r_1)−1]/Δ_A². Multiplying the projectile factor 4π/(2π)^3=1/(2π²) by the bound-state transform coefficient 2√2/π gives √2/π³. The two momentum-space arguments are q=k_0−k_A−k_B, up to an irrelevant sign for this s-wave transform, and k_B. Thus D=(√2/π³)α(t−h_B), exactly matching source Eq. (19), since 8√2/(2π)^3=√2/π³. Swapping A and B yields X with β(t−h_A), matching source Eq. (20).

With the declared scattering-amplitude convention F_D=−(2π)²D, the coefficient is −4√2/π, consistent with the independently versioned direct-amplitude cross-check. The source transition prefactor times |√2/π³|² is (2π)^4(2/π^6)=32/π². This establishes root Eq. (6)'s normalization without borrowing the source's disputed spin coefficient.

Source dE_A can be expressed as dE_B on the fixed-center shell E_A+E_B=E_0−I because |dE_A/dE_B|=1. No additional Jacobian magnitude enters. Atomic-unit K restores to physical density (a_0²/E_h)K with measure dE_B dΩ_A dΩ_B. The dimensionless spin/angle moments and normalized conditional law have the stated dimensions. No rounded 13.6 eV value is used as an exact binding-energy constant.

## 3. Spin trace, exchange symmetry, and event counting

For M=D I−X P, direct multiplication gives MM†=(|D|²+|X|²)I−(D X*+D*X)P. Since Tr I=4 and Tr P=2, division by four produces |D|²+|X|²−Re(D X*). The swap has eigenvalue −1 on the one-dimensional spin singlet and +1 on the three-dimensional triplet, so the same expression is 1/4|D+X|²+3/4|D−X|². Both derivations independently establish root Eq. (5), including complex amplitudes and the interference sign.

For real reduced amplitudes, w=d²+x²−dx=(d−x/2)²+3x²/4, strictly positive unless d=x=0. In contrast, the source's real f²+g²−2fg equals the triplet square. At D=X≠0 it vanishes while the independently defined unpolarized average is |D|². The theory correctly preserves the printed source equation and separately declares its adopted spin average; it does not attribute this new interpretation to the authors.

Swapping outgoing arguments exchanges d and x and leaves both the kinematic prefactor and w invariant. The shell's energy exchange is E_B↦E_0−I−E_B, with absolute derivative one. Hence a full labeled domain counts each unordered pair twice, and an ordered fast/slow half-domain counts it once. The 1/2 belongs to a full labeled-domain integral, not the pointwise TDCS on the ordered domain. The equal-sharing boundary has zero energy measure and receives no extra pointwise half factor. Spin averaging has already occurred once. No energy/global-angle event integral or total-event normalization is claimed here.

## 4. Azimuth integrals and positive mean representation

The transverse components of q are the negatives of both outgoing transverse vectors, giving q_perp²=R_A²+R_B²+2R_A R_B cosφ. Thus 1+q²=a+b cosφ, with the plus sign in root Eq. (7). Moreover a−b=1+z²+(R_A−R_B)²≥1, so there is no real-axis denominator singularity.

For a>|b|, the tan(φ/2) integral gives I_1=1/√(a²−b²). Differentiating locally under a uniformly positive denominator yields I_(n+1)=−∂_a I_n/n. This independently gives I_2=a/ρ³, I_3=(2a²+b²)/(2ρ^5), and I_4=a(2a²+3b²)/(2ρ^7). Using a I_n+b J_n=I_(n−1) gives J_2=−b/ρ³. For J_4, the numerator reduces to −b²(4a²+b²), yielding −b(4a²+b²)/(2ρ^7). The final explicit formulas are regular at b=0 and do not divide by b.

Expanding α²(t−h_B)²+β²(t−h_A)²−αβ(t−h_B)(t−h_A) gives exactly the stated A_2,A_1,A_0. Therefore the M_0 and M_1 formulas in root Eq. (9) follow by averaging t², t, and their cosine moments; the constant term contributes nothing to M_1.

For the positive variance identity, write

I_4−I_2² = a[2a²+3b²−2aρ]/(2ρ^7).

Using b²=a²−ρ² factors the bracket as (a−ρ)(5a+3ρ). Rationalizing a−ρ=b²/(a+ρ) gives precisely a b²(5a+3ρ)/[2ρ^7(a+ρ)]. Consequently M_0 equals A_2 Var(t) plus the positive quadratic evaluated at the mean t. Since A_2=(α−β/2)²+3β²/4>0, root Eq. (10) is an exact nonnegative representation, not a clipping prescription. It avoids subtracting nearly equal fourth- and second-moment terms for the variance. The signed moment M_1 can still suffer cancellation; its actual finite-case accuracy and conditioning must be inspected in C9.

## 5. Conditional measure and boundary cases

Kbar is the azimuthal average, so ∫K dφ=2π Kbar and the normalized density is K/(2π Kbar). Reflection φ↦2π−φ leaves K unchanged and reverses sinφ, proving E[sinφ]=0. The cosine moment is M_1/M_0. Dotting the two unit direction vectors gives μ_A μ_B+√(1−μ_A²)√(1−μ_B²)cosφ, which proves the last relation in root Eq. (12). Restoring both azimuths gives one factor 2π from overall rotation and one from undoing the relative average. Positive solid-angle measure is dμ dvarphi; theta parametrization requires its sine Jacobian.

On-shell ε_0>1/2 and ε_A,ε_B>0 imply k_i<k_0, making both Δ_i² positive. Endpoints with a zero outgoing kinetic energy are outside the domain; equal energy is an allowed diagnostic boundary of the ordered domain. At μ=±1 the transverse direction vanishes without creating a denominator singularity. Near-threshold/highly cancelling relative accuracy is explicitly restricted to actual fixtures, not promised globally.

If b>0, t varies with φ, so Var(t)>0 and M_0>0. If b=0, all J_n and the variance vanish, and w is constant in φ. The conditional distribution is uniform if that constant is positive; if d=x=0 it is undefined. Since α,β>0 and h_i is strictly monotone in k_i², simultaneous d=x=0 requires k_A²=k_B²=q². Root's separate exact prototype ε_0=9/14, ε_A=ε_B=1/14, μ_A=μ_B=1 gives k_0=3/√7, k_A=k_B=1/√7, α=β=7/4 and t=h_A=h_B=49/64; hence M_0=0 exactly. This prototype verifies the mathematical undefined case outside the high-energy numerical demonstration. Binary64 evaluations need not represent that irrational cancellation exactly: the stated rule of reporting a numeric exact-zero denominator as undefined and retaining tiny nonzero values with conditioning diagnostics is preferable to an invented near-zero clipping threshold.

## 6. Independent hand oracles and six-fixture assessment

All stated hand oracles check independently:

- d=1+2i,x=3−i gives d+x=4+i and d−x=−2+3i, hence singlet 17, triplet 13, and weighted 14.
- d=x=2+i gives triplet zero and weighted 5.
- a=5,b=3,ρ=4 yields I_2=5/64, I_4=385/32768, J_2=−3/64, J_4=−327/32768, and variance (385−200)/32768=185/32768.
- Vector fixture (0,0,5),(0,0,4),(2,0,2) gives q=(−2,0,−1), q²=5, Δ_A²=1, Δ_B²=13 and the shell 25=16+8+1. Therefore d=1/36−1/81=5/324 and x=(1/36−1/289)/13=253/135252.

Root supplied six fixed high-energy geometries, all ε_0=100:

| Fixture | ε_B | μ_A | μ_B | Independent assessment |
|---|---:|---|---|---|
| G1 | 40 | 1 | 0.2 | b=0, unequal energies prevent a simultaneous d=x=0 node; conditional cosine mean zero |
| G2 | 40 | 0.8 | 0.6 | b>0, positive variance and M_0 |
| G3 | 40 | −0.4 | 0.75 | b>0, positive variance and M_0 |
| G4 | 40 | 239/(2√23800) | 161/(2√16000) | z=0; R_A²=R_B²=38079/800; b=38079/400=95.1975; a−b=1 and q=0 at φ=π |
| G5 | 49.75 | 0.5 | 0.5 | Exact exchange symmetry d=x, triplet zero for all φ; b>0 keeps unpolarized M_0 positive |
| G6 | 49.75 | 1 | −1 | b=0; q²=200 differs from k_A²=k_B²=99.5; positive constant w and zero cosine mean |

For all these energies, b≤2k_A k_B≤k_A²+k_B²=199, while a−b≥1. When b>0 the nearest complex azimuth poles have distance arcosh(a/b)≥arcosh(200/199), approximately 0.10, from the real axis. Periodic trapezoidal convergence is therefore plausibly rapid at N=2048 even for the fourth-power denominator; G4 is less narrow, with b=95.1975 and a−b=1. This analyticity assessment supports the fixed acceptance targets relative M_0 error≤1e−10 and absolute conditional-cosine difference≤1e−10. It is not a global floating-point error proof, nor a claim that an unexecuted quadrature passed. The N=64,256,1024,2048 sequence should expose the expected finite-fixture convergence in the actual evidence. G5's triplet node must not be confused with a node of the unpolarized conditional law.

## Freeze recommendation

Freeze the reviewed equations, explicit source/version qualifications, spin/count/measure conventions, positive formula, exact hand oracles, and the six root-specified fixtures. R6 requires no mathematical correction. C9 should examine the actual implementation's direct-amplitude quadrature versus analytic formulas, exact-zero/conditioning behavior, and finite-fixture results without importing old suites or changing the fixed tolerances. The reviewed admission is model-only; SOURCE_INPUT_PENDING remains the physical-provider state, and no empirical error certificate or finite-mass law is supplied.
