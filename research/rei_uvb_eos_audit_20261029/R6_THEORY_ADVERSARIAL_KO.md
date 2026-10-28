# PR252의 R6 이론심사용 부록: 온도–밀도 EOS nuisance와 UVB redshift slope

**선택된 범위:** `REI_UVB_ONE_TILT_IDENTIFIABILITY_NEXT`의 기존 고정 EOS(θ=0) GLS를 재작성하지 않는다. 이미 게시된 PR252의 18/20 과학·코딩 결과를 재사용하고, 심사 위험인 EOS response 방향 하나만 수학적으로 검산한다. 이 문서는 **독립 작성자 R6 PASS가 아니다**.

## Source와 단위

- Source: Becker–Bolton (2013), *New measurements of the ionizing ultraviolet background over 2<z<5*, Table 1/2 (https://academic.oup.com/mnras/article/436/2/1023/1118137); observation source Git blob `61c1ecdcb1be05d47bb59165fb4cac8bb14deb52`.
- Template source: PR251 Puchwein2019 fixed model observed-seven-point vector Git blob `abd45812fb38691bcc76b5bddd33c55e2e5e4be3`; raw Puchwein template Git blob `218d81f68447da438228a7b102e1cec96a8e8a1a`.
- Reused source projection: `source/FROZEN_INPUT.json`, SHA256 `3cd87261e719751228f463c1d5ba71162d0eb4e33620a12176fa56429a6902bf`, 7 points z 2.4..4.75 and supplied full correlated statistical C (dex²), source gamma0=1.4 and printed v=(.084,.086,.083,.077,.071,.066,.064) dex for gamma1.6.
- Parameter τ here is **θ_EOS=(γ_TDR−1.4)/.2**, not conformal time, optical depth, physical Bianchi global tilt, or local boost. Constraint θ∈[−1,1]. Original selected model remains θ=0. No Jeans/source/thermal nuisance covariance or posterior is supplied.
- This supplement treats frozen BB/C/model JSON-decoded floats as **exact binary64 real images**, while v is the source's **exact printed decimal** response vector, not a claim of full published fixed-width byte identity. The linear interpolation d(θ)=d+θ v within theta bounds is a model assumption, not new observational measurement.

## Exact identity and proof

Write r=d−m, x=z−3.6, X=[1,x], W=C⁻¹ and M=XᵀWX. For C SPD and rank(X)=2, M SPD. Let θvec=(β,κ) and v the EOS response. GLS with EOS correction is

θvec(η) = M⁻¹ XᵀW(r+η v) = θvec(0) + η M⁻¹XᵀWv.

Define P=I−XM⁻¹XᵀW; P is W-orthogonal projector onto the GLS residual complement, and

Q₂(η)=(P(r+ηv))ᵀW(P(r+ηv)) = Q₂(0)+2η(Pr)ᵀW(Pv)+η²(Pv)ᵀW(Pv).

Since W SPD, its quadratic coefficient is nonnegative. This exact polynomial is valid for all real η algebraically; physical interpretation is restricted to the source's declared η∈[−1,1] and its linearized EOS shift. Common shifts of every d_i change β but not κ. The nested amplitude→slope ΔQ remains nonnegative at fixed η under the same W. None of these properties proves physical source-history identifiability.

## Actual tiny audit, one exact-rational run plus external CAS

`code/eos_linear_audit.py` used Python `Fraction.from_float` for exact source binary64 images, rational Gaussian elimination for C and M, and exact rational residual quadratic identities. It did not call or reexecute the original PR252 worker or 24-test suite. Exit=0. Measured self-contained command user CPU 0.03 s, system CPU 0.01 s, wall 0.04 s. Five prior saved values matched the frozen tolerance rtol1e-10, atol1e-12.

Independent **computational engine** Wolfram Language used the two immutable Git source JSON tables, inverted the same 7×7 matrix and independently returned theta0, EOS direction, and Q-polynomial coefficients. Mathematica numerics match the Python rational result at displayed precision. This is external CAS corroboration, **not a separate Astra-tier authored native R6 reviewer**.

The exact-represented-input results are:

θvec(0)=(−0.04591874303144475, +0.06866173948059068).

∂(β,κ)/∂η=(+0.07822682984779859, −0.00930263027377626).

Q₂(η)=11.347835208970780 −1.698503066588484 η +0.067714436241483 η².

| η | γ_TDR | κ (dex/redshift) | Q₂ (5 nominal dof) |
|---:|---:|---:|---:|
| −1 | 1.2 | +0.077964369754367 | 13.114052711800746 |
| 0 | 1.4 | +0.068661739480591 | 11.347835208970780 |
| +1 | 1.6 | +0.059359109206814 | 9.717046578623779 |

Within this **single** reported EOS response direction, κ retains positive sign and Q₂ monotonically decreases. This is not proof of a positive *physical* UVB spectral tilt: the dataset/template have already been examined, the full Jeans and thermal/source-model systematics are not in C, the direction is not independently validated, and the source authors report that IGM temperature assumptions can dominate rate inference.

## Review gates / remaining obligations

- THEORY_MATH_CHECK: `PASS_SCOPED_SAME_AUTHOR_PLUS_WOLFRAM_NUMERIC`, restricted to saved seven data, fixed W and linear EOS response.
- R6_INDEPENDENT_AUTHOR: `NOT_RUN`, so original PR252 **18/20 is unchanged**.
- C9_INDEPENDENT_AUTHOR: `NOT_RUN`.
- C10 original science's final release remains `HOLD`; this supplemental handoff is not scientific signoff.
- Original DAG working **33/88**, central last **28/88**, IDs 88/edges17, delta0. No new H–Li provider, native25, L4, actual physical T or IVP.
