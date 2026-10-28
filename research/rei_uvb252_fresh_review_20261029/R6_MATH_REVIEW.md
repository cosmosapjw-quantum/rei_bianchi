# R6: fresh mathematical review of PR252 fixed-template GLS (2026-10-29)

**Scope**: reviewed PR252 `eecd9b2c1c95f9319c1da41951b814855b0feb11` with frozen BB13 7×7 full correlated statistical covariance and Puchwein2019 fixed template. Parent PR251 `c5ab42c8673db614e7fb16695ad071c65becb81b`. PR254 is a separate entrypoint repair, and PR253/PR255 own the EOS-response research.

The original observable is the **scalar redshift trend of log10 H I photoionization-rate residuals**, not spatial Bianchi global tilt or observer boost. Let `r=d-m`, `X=[1,z-3.6]`, `W=C^{-1}`. For `a=1ᵀW1,b=1ᵀWx,c=xᵀWx,u=1ᵀWr,v=xᵀWr,D=ac-b²`:
```
beta=(c*u-b*v)/D; kappa=(a*v-b*u)/D
Cov(beta,kappa)=[[c,-b],[-b,a]]/D
DeltaQ=Q0-Q2=(v-b*u/a)^2/(c-b*b/a)=kappa^2/Var(kappa)
```
An actual new Wolfram evaluator call returned four exact symbolic zeros for the normal-equation/profile identities. A new, separately written QR-whitened Python evaluation of the **numerically transcribed** frozen inputs (no producer import or rerun) returned `beta=-0.04591874303144474`, `kappa=0.06866173948059072` dex/redshift, `Q0=19.381736839571932`, `Q2=11.347835208970784`, `DeltaQ=8.033901630601148`, `Var(kappa)=0.0005868175495880132`. Min eigenvalue of C = `0.00023317628835885996`; normal residual max `6.99e-14`. These agree with PR252's saved values, and the source array was checked against its Git text, not restored as byte-identical raw input.

**Derived exact affine sensitivity**: `wᵀ=e_kappaᵀ(Xᵀ W X)^{-1} XᵀW` obeys `wᵀ1=0,wᵀx=1`. Therefore `kappa(r+δ)=kappa(r)+wᵀδ`. For coordinate box `ell_i≤δ_i≤u_i`, choose `ell_i` for positive `w_i` and `u_i` for negative `w_i` to attain the minimum, reversing for maximum. Two explicit corner controls PASS.

- The BB13 **Jeans-smoothing coordinate box** yields the conditional algebraic interval `[0.0629201350416918,0.08992270939234213]` dex/redshift.
- The distinct PR253/PR255-owned EOS direction gives `[0.05935910920681447,0.07796436975436696]` (rechecked, not claimed new).
- Their formal independent product-box enclosure is `[0.05361750476791556,0.09922533966611836]`. This is **not** a nuisance joint law, simultaneous confidence interval, physical significance, held-out detection or an observed directional dipole. Printed BB13 Jeans shifts do not establish independent physical attainability of all 7 corners.

Source: Becker & Bolton 2013 https://academic.oup.com/mnras/article/436/2/1023/1118137 ; tomographic dipole response comparison: https://doi.org/10.1103/PhysRevD.111.123547.

**Verdict**: `R6_SCOPED_MATH_VALIDATION_PASS` as a fresh mathematical and separate algorithmic check; formal distinct-native-agent R6/C9 publication authority is **not claimed**. PR252's authoritative `18/20` remains unchanged until review admission. Original canonical DAG `28/88`, separate working `33/88`; physical F4 PARTIAL, L4=false, no new IVP. No descendant source or chemical coverage promoted.

Local reviewer evidence: `review_gls.py`, `test_review_gls.py`, `RESULT.json`, `tests_actual.log`, `R6_THEORY_REVIEW_KO.md` in the separately delivered ZIP. This PR contains a scope-bounded record; it does not import or overwrite the frozen scientific source.
