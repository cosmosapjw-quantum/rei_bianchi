# HE-ANG-TDCS54-ANCHORS independent R6 review

**Verdict: PASS for THEORY_KO.md equations (1)–(8), their specified positive-input scenario, and the pinned source interpretation.** No current blocking finding. C9 implementation acceptance awaits actual code and execution evidence.

Reviewer: separate `/root/independent_review` agent, requested Astra scientific reviewer; actual backend model identity is not independently observable. Date: 2026-10-24 UTC. This is a new-contract review, not a reopening of the earlier CCC-EXCHANGE/PR95 review. One read-only review pass; no implementation edit, scientific child, solver, test replay, CAS call, or new reviewer delegation. Only the requested review artifacts were written. The previously read physmath-research-loop R6 and common research policy apply unchanged.

## Evidence identity and source readback

- THEORY_KO.md SHA256: `ad7c75393f88346ff2891686275b9ed248dc7b7c10df4c841a8355d8f9264bf7`.
- FROZEN_CONTRACT.json SHA256: `8cf068da56addb699e18700d86a054666b301fe89da8f3c39ff5ae48b22211dc`.
- Jones–Madison PDF SHA256: `4e7b8d86cd9d29200f9de736b09215b045ceb592ef86b82a26c82a68e20864d3`, matching the pinned source identity.

Read the theory and frozen contract, relevant original extracted paper text, and visually inspected `jones_page-09.png` and `jones_page-10.png`. The image filenames correspond respectively to printed article pages 042701-8 and 042701-9. The first visibly supplies Fig. 10's angle convention, 54.4 eV incident/5 eV slow energies, the 210° statement for the 4° and 10° recoil entries, and the rounded scale summaries. The second visibly supplies Table IV and references [9] and [11]. Original text additionally confirms the infinitely massive nucleus on article page 2 and neglected electron exchange, peak-specific <2% numerical uncertainty, and ±10%/±35% experimental normalization statements on page 4.

Table IV has eight columns of feature values and three producer rows, hence 24 cross-section cells, plus 16 printed theory/experiment ratios. The two recoil entries for fast angles 4° and 10° have slow angle 210° explicitly supplied by page 8. The other six columns are peak-height comparisons with no numerical slow angle supplied in this table/text mapping. Consequently only two joint coordinates, containing six producer values, are admitted. No graph digitization or peak-angle inference was used.

The two anchor rows are independently confirmed as CDW-EIS 1.83/0.99, CCC99 2.58/1.51, and experiment 1.52/1.24. Reference [9] reads I. Bray (unpublished); the paper acknowledges receipt of CCC results before publication. Their reproduction in Jones–Madison supplies the numerical provenance but does not identify them with another CCC calculation. Reference [11] is the 1997 Ehrhardt–Röder book chapter. Its original measurements are not newly retrieved here. The CDW exchange-neglect and infinite-nucleus conventions are source approximations, not newly supplied physical laws.

## Independent mathematical review

### Equations (1)–(2): feasible common scale

For strictly positive m_i and d_i, r_i=m_i/d_i>0. The declared scale multiplies the experimental nominal density: m_i=A u_i d_i. Thus u_i=r_i/A. Since A>0 and 1−δ>0, the two inequalities 1−δ≤r_i/A≤1+δ are exactly equivalent to r_i/(1+δ)≤A≤r_i/(1−δ). Intersecting over a finite nonempty index set gives the proposed maximum lower endpoint and minimum upper endpoint. Intersecting with a separately specified positive scale box adds precisely its endpoints. The witness u_i=r_i/A proves sufficiency, including a touching interval. There is no probability statement in this construction.

At δ=0 the interval is nonempty precisely when all ratios agree; it then contains their common value. A single ratio behaves identically. δ=1 requires division by zero in the proposed form and is properly excluded. Negative or zero density input would invalidate the declared positive-input ratio problem and is excluded by contract.

### Equations (3)–(4): minimax and clipped optimum

The maximum of |r_i/A−1| over r_i in a finite positive set is attained at an extreme, yielding max(r_max/A−1,1−r_min/A). Their difference is (r_max+r_min)/A−2. The first term is the active term below A*=(r_max+r_min)/2 and strictly decreases there; the second is active above A* and strictly increases there. Their common value at A* is (r_max−r_min)/(r_max+r_min). This proves the free optimum without importing a statistical median argument. Restriction to a closed positive interval therefore clips A* to the nearest endpoint when needed. If the upper allowed scale is far below the ratios, the optimal q can exceed one; returning it unchanged is consistent with its definition, whereas δ<1 is only the separate feasibility-model input restriction.

### Equations (5)–(6): pair contrast and sharpness

Taking the ratio of the two m=A u d equations cancels common A exactly. Dividing by the experimental ratio leaves Q=u_4/u_10. On the positive Cartesian-product box [1−δ,1+δ]^2, this ratio is increasing in its numerator and decreasing in its denominator; opposite corners attain both proposed endpoints. This is deterministic independent variability, with no inference of stochastic independence. With Q>0, applying the two-extreme minimax formula yields |Q−1|/(Q+1), independent of the absolute pair scale. Multiplication by the positive experimental ratio gives the stated experimental pair sensitivity interval.

### Explicit rational oracle verification

Hand arithmetic from the printed decimal inputs gives:

| Quantity | Independently checked exact result |
|---|---|
| Experimental anchor ratio | 152/124 = 38/31 |
| CDW anchor ratio | 183/99 = 61/33 |
| CCC anchor ratio | 258/151 |
| CDW Q | (61/33)(31/38) = 1891/1254 |
| CCC Q | (258/151)(31/38) = 3999/2869 |
| CDW minimum free deviation | (1891−1254)/(1891+1254) = 637/3145 |
| CCC minimum free deviation | (3999−2869)/(3999+2869) = 565/3434 |
| CDW free scale | ((183/152)+(99/124))/2 = 9435/9424 |
| CCC free scale | ((129/76)+(151/124))/2 = 1717/1178 |
| CCC clipped scale | 27/20, since 1717/1178 > 27/20 |
| CCC clipped deviation | (129/76)/(27/20)−1 = 44/171 |

For the nominated δ=1/10, independent interval endpoints provide extra implementation controls: CDW gives L=915/836 and U=55/62, hence L>U; CCC gives L=645/418 and U=755/558, again L>U. These failures already occur before imposing the absolute-scale box. They concern only this declared deterministic scenario, not a statistical rejection or general physical no-go.

### Equation (7): angle sense, geometry, and dimensions

With fast CCW declared toward +x and slow angles measured CW, the directions are (sin θ_f,0,cos θ_f) and (−sin θ_s,0,cos θ_s). Both are unit vectors. Their scalar product is cos θ_f cos θ_s−sin θ_f sin θ_s=cos(θ_f+θ_s). At 210°, the slow direction is (1/2,0,−√3/2), whose polar angle is 150°. The directed sums 214° and 220° correspond to smaller interelectronic angles 146° and 140°. Using a simple difference of the two positive reported angles would violate the source senses. Reflecting the entire scattering plane is merely a common coordinate convention and preserves these scalar products.

Every r, A, u, Q, and δ is dimensionless. The reported TDCS has dimension area/(energy·solid-angle²), preserved in native atomic units. No SI constants are needed for the ratios. No recoil-energy calculation, finite-mass frame transformation, spin reconstruction, or full-distribution normalization enters these equations. The source's recoil peak names an angular lobe; it does not supply an ion recoil distribution.

### Equation (8): conditional printing compatibility

For the positive table entries and h=0.005, the hypothesized original-value boxes have positive numerator and denominator bounds. Their ratio is monotone in each argument with opposing signs, giving exactly the displayed endpoints. Comparing that interval with the printed ratio's own [ratio−h,ratio+h] interval is a valid compatibility check for the stipulated nearest-0.01 model. It is not an experimentally calibrated uncertainty interval. In particular, 91/109 differs from the printed ratio 0.84 by slightly more than 0.005; treating only the printed ratio as rounded while treating numerator and denominator as exact underlying values would impose the wrong test.

The all-feature CDW nominal extrema are 183/152 and 42/61, which yield A*=17547/18544 and δ*=1593/5849 (about 27.24%). The paper instead summarizes approximately 0.95±0.25 and 26%. This exact recomputation supports the contract's choice to report nominal table arithmetic beside the original summary rather than force agreement or adjust inputs. The source summary's discrepancy does not invalidate equations (1)–(8).

## Claim boundary and conclusion

The mathematical scenario is explicitly nominated and conditional; the source provides no covariance or probabilistic confidence model supporting it. Source <2% numerical uncertainty is peak-specific and is not promoted to a certified anchor error. All already-reported densities retain their original weights/count normalization without importing equal-sharing raw-amplitude factors into these unequal-sharing anchors. Two sparse coordinates do not determine the continuous H1 joint law, spin/amplitude payload, finite-mass dynamics, or complete support/measure/event contract. These remain SOURCE_INPUT_PENDING, with no physical completion percentage or new no-go claim.

**R6 PASS.** All stated hand oracles were independently checked, and no correction is required. C9 should review the later exact-rational implementation and actual tests under the frozen acceptance criteria; this R6 review itself authorizes or consumes no scientific execution budget.
