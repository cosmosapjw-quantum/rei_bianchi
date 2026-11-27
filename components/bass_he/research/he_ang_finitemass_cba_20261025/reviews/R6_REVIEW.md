# Independent R6 review — HE-ANG-FINITEMASS-CBA

## Decision and identity

**PASS, scoped to the stated finite-mass labelled direct C1 Coulomb–Born model.** No blocking mathematical defect was found in Eqs. (1)–(14) or the frozen numerical contract. Numerical accuracy and implementation admission remain pending the bounded execution and separate C9 review. This decision does not admit a physical provider, exchange-complete event law, total event cross section, or exact three-body Coulomb asymptotics.

Reviewer `/root/fm_cba_review5` is separate from the theory author and implementer. Requested model: `gpt-6-astra`; observed runtime identity: `NOT_OBSERVABLE`. Review used independent analytic reasoning and read-only inspection. No science execution, numerical suite, Wolfram call, or remote mutation was performed. Only these R6 review files were written.

Read in full: this unit's `THEORY_KO.md` and `FROZEN_CONTRACT.json`; central and BASS_HE AGENTS captured in `next5_ops_20261025/entry`; parent PR100 theory and `code/cba.py`; parent PR99 theory and `code/shell.py`. Reviewed the actual primary PNGs `kadyrov2009_page_12.png` and `kadyrov2009_page_13.png` (printed pp. 1527–1528), and `attaourti2004v2_page_3.png` and `attaourti2004v2_page_4.png`, with Appendix page 7 text. Parent review evidence was inspected as inherited context, not substituted for the independent checks below.

## Independent mathematical assessment

### 1. Canonical coordinates, units and energy

The inverse position map follows from the pair COM, `x_pair=X-R/T`, and from `r=x_B-x_N`. Taking the differential one-form gives

`p_A.dx_A+p_B.dx_B+P_N.dx_N=P.dX+q.dR+k.dr`,

where `q=p_A-P/T` and `k=p_B-(P-p_A)/(M+1)`. This proves the canonical momentum convention without importing a mass-scaled momentum from another source. In the ordered coordinates `(X,R,r)`, the inverse Cartesian determinant is +1; absolute Jacobian one is independent of coordinate ordering. At fixed P the map `(q,k)->(p_A,p_B)` is triangular with determinant one. Squaring the three momenta cancels the cross terms and leaves coefficients `1/T`, `1/nu`, and `1/mu`, establishing Eq. (2).

The explicit electron scales `a0,p0,Eh` are consistent. The written physical Hamiltonian uses physical distances in its Coulomb terms and physical derivatives in its kinetic terms; the subsequent dimensionless Hamiltonian uses the declared scaled coordinates. An invariant shell measure has units `p0^6/Eh`, so W must have units `a0^2*Eh/p0^6`. Its fixed-p_A integral has units `a0^2/p0^3`, and both displayed TDCS charts have units `a0^2/Eh`.

For a target initially at rest, incoming relative momentum is `qi=nu P`, so the incident relative speed is `qi/nu=P`. Subtracting the total-COM kinetic energy `E0/T` gives available internal energy `nu E0-mu/2`. The threshold and strict interior Jacobi-energy domain are consequently correct.

### 2. Hamiltonian partition and recoil signs

The geometric separations are `x_A-x_B=R-a r` and `x_A-x_N=R+b r`. Their charge products give `V=+1/|R-a r|-1/|R+b r|`. In the projectile Fourier integral with `exp(+i Delta.R)`, the substitutions `R'=R-a r` and `R''=R+b r` give respectively `exp(+i a Delta.r)` and `exp(-i b Delta.r)`. Eq. (5), including its signs and prefactor, is therefore correct. Screening supplies a well-defined transform and the unscreened result is taken at nonzero Delta, rather than treating the unscreened absolute integral as convergent.

The H0 pair problem has kinetic mass mu and charge product -1. Its normalized 1s exponent is mu, its binding is mu/2, and its attractive Coulomb parameter is mu/k. These three choices cannot be varied independently within the selected model. The theory and frozen contract consistently match them.

### 3. Continuum overlap and normalization

For a continuum labelled by momentum k, the delta normalization is `delta^3(k-k')`, not an energy normalization. Changing the reduced mass changes eta but does not insert an extra power of mu into the plane-wave asymptotic normalization `(2*pi)^(-3/2)`. The stated Nc is consequently appropriate. The initial bound normalization contributes `sqrt(mu^3/pi)`.

In the inherited integral put `q_integral=s-kvec`. Its denominators become `A_s=|s-kvec|^2+mu^2` and `B_s=s^2+(mu-i k)^2`. Differentiating the parent integral at fixed eta before imposing `eta=mu/k` gives exactly the polynomial in Eq. (6). Since `Im(B_s)=-2 mu k<0` and `A_s>=mu^2>0`, the same principal log branch applies. Hence the finite-mass amplitude requires `L(a Delta)-L(-b Delta)`, with no constant nuclear term substituted at finite M.

At small Delta the linear coefficient carries `a+b=1`. At transverse Delta the quadratic coefficient carries `a^2-b^2=(M-1)/(M+1)`. For M=1 and `Delta.k=0`, A, B and C are identical for the two shifts, so the difference is exactly zero for every transverse Delta. This is a synthetic symmetry identity of the stated model. The two stable overlaps avoid cancellation internal to either overlap; they do not guarantee uniform relative accuracy near zeros of their difference. The theory correctly excludes that stronger numerical claim.

### 4. Flux, invariant weight and detector coefficients

The projectile bra and ket contribute `(2*pi)^(-3)` to T_delta, and F already includes the pair continuum normalization. Therefore

`(2*pi)^4 * |4*pi/(2*pi)^3|^2 = 4`.

Division by `vi=qi/nu` gives `W=4nu/qi |F|^2/Delta^4`, establishing Eq. (10) without an omitted reduced-mass or Fourier factor. The box-state argument gives the same coefficient: squared matrix element scales as V^-3, two final densities as V^2, and inverse incident flux as V, cancelling V exactly. A spin-diagonal labelled direct amplitude has four allowed final/initial spin combinations against the initial average 1/4, giving one. No exchange interference or unordered 1/2 follows from this calculation.

In Jacobi variables `k^2 dk=mu k dEr` and the q radial energy delta contributes `nu q`. Their product with W gives `4mu nu^2 qk/qi`, as in Eq. (11). In the lab chart `p_A^2 dp_A=p_A dEA` and the outgoing B radial derivative is `|alpha p-beta|=sqrt(Droot)`. Each positive simple root therefore contributes `p_A p_j^2 W_j/sqrt(Droot)`. W must be separately evaluated at each root; the frozen wrapper requirement is correct. An unresolved parent caustic must remain unresolved, and no clipping or inferred finite pointwise density is justified.

### 5. Weighted fold and integrability

At fixed p_A, `k=p_B-c` and `F=H-alpha |k|^2/2`, so direct radial integration gives `mu rho dOmega_k`. Because `c=Delta/(M+1)`, the model's angular dependence is axially symmetric about the same axis as the fold construction. This justifies extracting the azimuthal factor 2*pi; it would not be justified for an arbitrary anisotropic weight.

For the two-root cone `Droot=alpha^2 h^2` and `dt/dh=h/[c0 sqrt(h^2+c0^2-rho^2)]`. Multiplying the branch radial measure by this derivative cancels h exactly and gives the first Eq. (14), with no extra factor two. The two branches together cover the pair sphere, establishing the second form. In the frozen fixture, direct substitution gives `c0^2=81/200`, `rho^2=67/200`, and their difference `7/100`, so the stated forward two-root geometry is correct.

The convergence condition is satisfied for this actual weight: fixed M>0, rho>0 and Delta!=0 give mu>0, finite eta, nonzero B_s and positive A_s on a compact sphere. Thus W is bounded and smooth there. The h denominator is additionally bounded away from zero by `sqrt(c0^2-rho^2)` in the strict outside-sphere fixture. Both integrals are finite. This argument is local to the specified conditional slice; it neither establishes integrability at k=0 nor a total cross section.

### 6. Infinite-mass link and validity

At fixed E0, Er and Jacobi directions in the open interior, `mu,nu,a->1`, `b->0`, and the second overlap tends to L(0)=0. The continuum and bound normalizations approach the parent values; so do the available energy, outgoing q, transfer and Jacobi prefactor. This proves the stated pointwise PR100 limit. No uniform threshold estimate or finite-M lab-to-Jacobi relabelling is implied.

The closure is explicitly one plane-wave spectator and one Coulomb pair, with V inserted once. It is a well-defined direct Born channel approximation. Kadyrov's exact three-body asymptotic treatment does not by itself justify this approximate final state or establish its quantitative accuracy. The theory preserves that distinction and keeps applicability, uncertainty, exchange and physical provider admission open.

## Primary-source correspondence

The actual Kadyrov page 1527 defines pair reduced mass `m_beta m_gamma/(m_beta+m_gamma)` and spectator reduced mass `m_alpha(m_beta+m_gamma)/(m_alpha+m_beta+m_gamma)`, with canonical pair/spectator momenta. Setting masses `(1,1,M)` gives precisely mu and nu. Page 1528 gives the COM kinetic decomposition, pair Coulomb interaction and energy identity used here. Its H0 denotes the free kinetic Hamiltonian, whereas the new unit's explicitly defined H0 includes the pair Coulomb potential. This is a legitimate new channel partition, not literal reuse of the source's H0 notation. The source does not supply the derived lab detector coefficient or finite-M C1 amplitude.

The actual Attaourti pages confirm the outgoing-bra signs, Gamma(1-i eta), `exp(-i k.r)`, and fixed-centre transfer difference. Eq. (16) and the displayed Eq. (18) retain their recorded inverse-radius discrepancy. The new construction correctly reuses the independently derived no-extra-1/r K overlap and does not claim published-version equivalence or copy the relativistic spinor coefficient into the scalar model. No private source images or PDFs are reproduced in this review.

## Frozen numerical and resource contract

The generic, independent quadrature, tiny-transfer, fold and illustrative domains are explicit. Scaled residuals use `abs(value-ref)/max(1,abs(ref))`, while nonzero tiny cases use true relative errors. Thus the 1e-35 quadrature target is a scaled target, not automatically a relative target for a small difference. The M=1 exact symmetry zero uses an absolute criterion, and the frozen tiny tests avoid M=1 cancellation. No tolerance is relaxed or inferred by this reviewer.

The planned child CPU caps sum to 11 seconds against a 12-second new-science cap, leaving the declared one-second targeted repair reserve. Child wall caps sum to 33 seconds against 35. Adding the maximum new cap to recorded PR100 consumption remains below the declared additional-lineage ceilings. This is not an end-to-end cost certificate: inherited unknown costs and provider/model I/O remain explicitly unknown. Whether all prescribed quadratures fit the analysis child is empirical; hitting its cap must preserve partial evidence and return for root diagnosis rather than silently rerunning or relaxing tolerances.

## Closed clarity notes

**R6-NB-01, CLOSED:** The root added the boundedness argument beside Eq. (14) and in `CONTRACT_ADDENDUM_01.json`. The reviewer reread both additions: `A_s>=mu^2` and `|B_s|>=2mu rho`, finite Nc, and compactness suffice for bounded smooth W. No new test or tolerance change is required.

**R6-NB-02, CLOSED at contract level:** The lab energy-angle chart is an interior chart with `|p_A|>0`; at p_A=0 the A direction is undefined. The root added the explicit `LAB_A_ZERO_ENDPOINT` status with `density=None` to the theory and pre-execution addendum, which the reviewer reread. The invariant weight retains its independent domain. This precise endpoint rule does not change Eq. (12), the model, tolerances or budget, and the first targeted tests include it. C9 will verify implementation conformance; no broad endpoint campaign is requested.

## Next transition and stopping rule

R6 is complete. Proceed to the prescribed implementation/execution gate after the existing R7 and backup prerequisites, then review the actual changed code, raw outputs and generated figures at C9. Do not repeat unchanged parent scientific suites. Keep `HE_ANG=SOURCE_INPUT_PENDING`, `physical_provider_admitted=false`, `event_sigma=false`, `physical_recoil_distribution=false`, and the inherited OPEN obligations. No new strong no-go or novelty claim is made.
