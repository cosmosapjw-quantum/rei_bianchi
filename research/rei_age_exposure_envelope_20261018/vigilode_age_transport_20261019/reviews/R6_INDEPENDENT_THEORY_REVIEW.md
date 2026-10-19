# R6 independent theory review: frozen native packet age transport

Reviewer: /root/fresh_backup_intake, Astra. Review recorded 2026-10-19 UTC.
Decision: **PASS_SCOPED for the stated mathematical construction, conditional on the arithmetic postconditions below.** This is an independent derivation, an actual read of the root's `THEORY_KO.md`, and a source/export review. It is not a final implementation audit of the Rust evaluator. The reviewer ran no native RHS, scientific history, benchmark, or test campaign. The companion JSON binds the exact reviewed `THEORY_KO.md` SHA-256.

`PRODUCTION_SCIENTIFIC_ADMISSION=NOT_ISSUED`.

## 1. The exact object being certified

Let i label a native-derived quadrature node, retaining its source-cohort, cell and node identity. Its frozen inputs are a nonnegative mass w_i, a positive endpoint energy E_i, and nonnegative species rates lambda_is. Define Lambda_i as the **exact real sum of the represented binary64 lambda_is**. Birth times b_i and observation time T are likewise the exact real values represented by their input binary64 numbers. Require T >= b_i for every compared packet.

For each packet after birth, the new mathematical model is

\[
\dot N_i=-\Lambda_iN_i,\quad
\dot A_{is}=\lambda_{is}N_i,\quad
N_i(b_i^+)=w_i,\quad A_{is}(b_i)=0.
\]

Thus

\[
N_i(T)=w_i e^{-\Lambda_i(T-b_i)},\qquad
A_{is}(T)=w_i\frac{\lambda_{is}}{\Lambda_i}
  \left(1-e^{-\Lambda_i(T-b_i)}\right)
\]

when Lambda_i>0; for Lambda_i=0 use N_i=w_i and every A_is=0. The latter is an exact branch, not evaluation of 0/0. Since all species rates are nonnegative, their sum is zero only when all are zero.

The identities

\[
N_i+\sum_s A_{is}=w_i,\qquad N_i\ge0,\quad A_{is}\ge0
\]

hold exactly for this model. Endpoint energy is U_i=E_i N_i. Raw age moments are M_pi=(T-b_i)^p N_i, p=1,2.

This model freezes gas, geometry, node reconstruction and the species absorption rates at the archived endpoint. It is not the original solver's evolving reconstructed distribution, its backward-Euler cache evaluation, or a nonlinear gas/transport trajectory. Coarsening changes only the birth-clock labels of the original 64 source templates; it does not regenerate a native age8/16/32 source quadrature with different injection weights and birth geometry.

## 2. Actual exporter and units

I read `vigilode_age_transport_20261019/prepare_export.py`, its derived `vigilode_export.rs`, the original native source sections used for injection, absorption and background clocks, and the actual `model.json`/`EXPORT_RECEIPT.json`.

The exporter calls native `setup(0.0,64,8,8,16)`, uses the original injection templates, and calls `transport.prepare(template, endpoint_geometry)`. It exports `node.number`, q, cross sections, excess energies and E=q*ray.scale. Consequently the records are native-derived endpoint-frozen quadrature nodes. Their weights are source injections reconstructed at the endpoint geometry, **not already attenuated endpoint survivor weights**.

The source injection owner divides the comoving emissivity by n_H0 and records `added_photons_per_h`. Therefore the correct units are:

| Quantity | Unit |
|---|---|
| w_i, N_i, A_is | photons or events per H |
| E_i | eV |
| U_i | eV per H |
| T, b_i, age | s |
| M_1, M_2 | s per H, s² per H |
| absorber density | cm^-3 |
| sigma_is | cm² |
| c | cm/s |
| lambda_is=c n_s sigma_is, Lambda_i | s^-1 |
| optical depth Lambda_i(T-b_i) | dimensionless |

The actual endpoint input is x=ln(a)=-3.0425224377234232, T=16924302009133.814 s. Native `geometry_point` supplies a proper clock by quadrature of dx/H; x itself is not a time measured in seconds. The present certificate conditions on the represented clock values. It does not enclose the background quadrature error or the error between those values and a continuous exact cosmological clock.

Source receipt comparisons of `births`, `birth_times_s`, `physical_births`, `source_inventory`, and `encoded_births` against the archived age64 setup are all true. The endpoint gas values are inherited numerical data; no new bound on the accuracy of that gas state follows.

There is a deliberate floating-definition distinction: exported individual rates use represented products c*n_s*sigma_is, whereas native aggregate loss code forms c times a compensated sum of n_s*sigma_is. Exact summation of the exported individual rates need not equal the binary64 aggregate native coefficient bit for bit. The certified system is defined by the exported rates and their exact sum. It must be described as native-derived, not as byte-identical native RHS execution.

Observed identities:

| Read artifact | SHA-256 |
|---|---|
| prepare_export.py | ad40d26c3d76ca6cf474302f428e2b196c17367127a0fbc374994d6e7eceebda |
| model.json | d5ba5169a291996e31de3d0b8b4c4c6c75081f06e183bee571498eb5d4d3de0d |
| EXPORT_RECEIPT.json | b3441d15d89f6b82d9862f5a655bdac9a4044fda2b31f6f8b531cd0ae4edbb54 |
| derived vigilode_export.rs | 5f3ec82adef9941c78e22eab54102bfe16318b2eec9b852b8f0056d9a9da7d1e |
| nodes.csv, as bound by the actual export receipt | b83f5c07d83d9a6a04ca8120e8fcbe11dab67efb41cbcdd000e4f7eb6a25c17a |

The native input ancestry is 35d9747a0bbedcafdb568467ce7c1e7a25f965b6. The receipt records one export and zero native RHS calls. Those are the implementer's recorded actions, not new reviewer executions.

## 3. Exponential gain enclosure

For rational tau>=0 below 752, halve exactly until r=tau/2^k lies in [0,1/2]. The terms r^n/n! decrease, so the alternating-series theorem gives

\[
S_{19}(r)=\sum_{n=0}^{19}\frac{(-r)^n}{n!}
\le e^{-r}\le
S_{18}(r)=\sum_{n=0}^{18}\frac{(-r)^n}{n!}.
\]

Also 0<=S_19<=S_18<=1. The exact interval width before conversion is r^19/19!. Rational evaluation avoids cancellation or premature underflow in this stage.

Convert S_19 downward and S_18 upward, checking the **final represented rational postconditions**

\[
\operatorname{Rat}(\ell)\le S_{19},\qquad
S_{18}\le\operatorname{Rat}(u).
\]

A comparison before a guessed one-ULP correction is not the postcondition; the final stored endpoints must satisfy it. A correctly checked conversion does not need an assumption that a particular library conversion always rounds exactly to nearest.

Because squaring is increasing on [0,1], k directed lower/upper squares enclose

\[
e^{-\tau}=(e^{-r})^{2^k}.
\]

Intersecting each enclosure with [0,1] is safe. Exact tau=0 should retain[1,1]; passive-rate branches can then remain exact.

For tau>=752, [0,eta], eta=2^-1074, is rigorously sufficient. A minimal positive Taylor witness is degree 3:

\[
e^{7/10}>
1+\frac7{10}+\frac{49}{200}+\frac{343}{6000}
=\frac{12013}{6000}>2.
\]

Degree 2 is 389/200<2, so degree 3 is the first truncation with this property. Hence ln2<0.7 and 1074ln2<751.8<752. Therefore

\[
0<e^{-\tau}\le e^{-752}<2^{-1074}.
\]

This cutoff is an enclosure of a positive real value; it does not declare the packet physically absent. The upper endpoint eta must continue through outward multiplication by packet mass. Plain rounding-to-nearest multiplication could otherwise erase a nonzero error upper bound.

The enclosure certifies the exact dyadic-input model, not unrounded cross sections, source integrals or exact background clocks.

## 4. Paired endpoint defect and causal affine recurrence

For equal-mass pairs with the same lambda vector, let

\[
t_i^*=\max(b_i^A,b_i^B),\quad
\delta_i=|b_i^A-b_i^B|,\quad
d_i=w_i(1-e^{-\Lambda_i\delta_i}).
\]

At or after the later birth,

\[
|N_i^A(t)-N_i^B(t)|
=d_i e^{-\Lambda_i(t-t_i^*)}.
\]

This follows directly by factoring the exponential of the younger packet's age. Therefore, when T is after every birth,

\[
|\Delta N_{\rm total}(T)|\le
D(T):=\sum_i d_i e^{-\Lambda_i(T-t_i^*)}.
\]

D is a sharp sum of packetwise absolute differences; it is not generally the absolute signed total difference because packets with different directions of clock shift can cancel.

Define only the resolved-pair metric

\[
E(t)=\sum_{t_i^*\le t}d_i e^{-\Lambda_i(t-t_i^*)}.
\]

Order the distinct t_i^* as t_j. For Lambda_min no greater than every positive Lambda_i with a nonzero possible defect,

\[
E(t_{j+1})\le
e^{-\Lambda_{\min}(t_{j+1}-t_j)}E(t_j)
+\sum_{t_i^*=t_{j+1}}d_i.
\]

All coefficients are nonnegative. Passive Lambda_i=0 pairs have d_i=0 and need not determine the decay rate. Their mass must still be included in the physical totals and age moments. If there are no nonzero defects, return the exact zero-error case without taking a minimum of an empty set.

The final interval from the last resolution time to T must also be included. Equal resolution times can be grouped, or treated as consecutive zero-duration maps.

For maps F_j(e)=g_j e+d_j, chronological composition is

\[
F_2\circ F_1(e)=(g_2g_1)e+(g_2d_1+d_2).
\]

Thus a nonnegative upper gain and upper defect at each stage, combined using outward multiplication and addition, give an upper enclosure after an ordered parallel prefix. The order is causal and cannot be permuted: affine composition is associative over real arithmetic but is generally not commutative.

A different outward-rounded reduction tree may produce different bytes while remaining mathematically valid. Separate outward upper endpoints for D and for the affine result need not preserve their exact-real ordering when their interval widths differ. Both upper endpoints remain valid bounds; their minimum is also a valid bound on the final number difference. An implementation test should not mistake upper-endpoint ordering for the underlying real inequality.

### 4.1 Exact-hazard grouped affine prefixes

Partition the sensitive packets into groups G whose exact total rate is a common positive value Lambda_G. Grouping by the entire exact species-rate tuple is sufficient: identical represented tuples necessarily have the same exact rational sum. It is not necessary to maximally coalesce distinct tuples that happen to have an equal sum.

For each group define

\[
E_G(t)=\sum_{i\in G:\,t_i^*\le t}
d_i e^{-\Lambda_G(t-t_i^*)}.
\]

At consecutive resolution times u_j of that group,

\[
E_G(u_{j+1})=
e^{-\Lambda_G(u_{j+1}-u_j)}E_G(u_j)
+\sum_{i\in G:\,t_i^*=u_{j+1}}d_i.
\]

This is an **exact real equality**. After each group's final decay interval to T, the groups partition the nonzero defects and therefore

\[
\sum_G E_G(T)=D(T).
\]

Apply VigilODE's ordered outward affine prefix to each group, then add the nonnegative group upper bounds outward. The result encloses D without the extra analytical looseness from the global minimum rate. The numerical enclosure still has nonzero width. The direct and grouped upper endpoints have no required ordering; both enclose the same D. A minimum of independently established valid upper endpoints remains valid.

A rounded aggregate-rate key must not merge mathematically unequal rates and then silently use one representative rate as though this equality held. Approximate grouping can instead use a certified lower rate for every member and produces an inequality, like the global-min construction. The implemented exact species-rate tuple grouping avoids that issue. Chronology within each group, event insertion at the later birth, and the final interval to T remain required.

E(t) is not the full population difference before both members of every pair have appeared. A full intermediate-time bound would additionally require

\[
U_{\rm unresolved}(t)=
\sum_{\min(b_i^A,b_i^B)\le t<t_i^*}
w_i e^{-\Lambda_i(t-\min(b_i^A,b_i^B))}.
\]

Then the whole population difference is bounded by E+U_unresolved. The planned endpoint certificate does not need this extra term because all compared births precede T.

## 5. Labels, W1, and a concrete joint-association guard

The always-valid label-preserving birth cost is

\[
C=\sum_iw_i\delta_i.
\]

Since 1-e^-z<=z,

\[
D(T)\le
\sum_i w_i\Lambda_i\delta_i
e^{-\Lambda_i(T-t_i^*)}
\le\Lambda_{\max}C.
\]

For emission mass M=sum_i w_i>0, the prescribed pairing gives only W1<=C/M in general. This direction alone cannot replace C by M*W1 in the response bound.

Keeping every packet's rate unchanged is insufficient to justify an unlabelled age-W1 statement. Set T=1,w_1=w_2=1,Lambda=(0,1). Compare b^A=(0,1) with b^B=(1,0). Both runs have exactly the same age marginal and the same rate marginal. The association between them differs. Their photon totals are

\[
N_A=2,\qquad N_B=1+e^{-1},
\]

although their unlabelled age W1 is 0. This is a semantic guard against losing joint labels; it is not a strong no-go theorem about positive photon methods.

The association issue also occurs with strictly positive rates: keeping the same T, weights and birth assignments but setting Lambda=(1,2) gives N_A=1+e^-1 and N_B=1+e^-2. Thus it is not an artifact of the passive branch.

For the **specified contiguous order-preserving clock coarsening**, the paired cohort masses occur in the same temporal order on both sides. The coupling is monotone, including ties, and is therefore an optimal one-dimensional coupling. In this restricted family C/M equals ordinary W1. The proof requires checking that the implementation maps consecutive 64-cohort groups to ordered8/16/32 clocks while preserving every packet mass.

The natural more general object is the joint measure in(b,Lambda). Its response kernel is

\[
\Phi_T(b,\Lambda)=e^{-\Lambda(T-b)},\quad
\partial_b\Phi_T=\Lambda\Phi_T,\quad
\partial_\Lambda\Phi_T=-(T-b)\Phi_T.
\]

Alternatively push the mass to optical depth tau=Lambda(T-b). Since e^-tau is1-Lipschitz on[0,infinity), an optical-depth W1 controls photon total for equal mass. This common response function exists on optical depth even when it does not exist on unlabelled age.

For positive rates, the logarithmic rate derivative has the useful bound

\[
|\partial_{\log\Lambda}\Phi_T|
=\tau e^{-\tau}\le1/e.
\]

A log-rate comparison excludes the passive Lambda=0 branch and must handle it separately. Species event and photon-energy observables require their species fractions and energy labels as well; optical-depth marginal equality alone does not determine these observables.

## 6. Observable extensions and passive packets

For fixed endpoint energy E_i, energy differences admit the weighted analogue

\[
|\Delta U|\le\sum_i E_i d_i e^{-\Lambda_i(T-t_i^*)}.
\]

For species s, fixed lambda_is/Lambda_i gives

\[
|\Delta A_s|\le
\sum_{\Lambda_i>0}
\frac{\lambda_{is}}{\Lambda_i}
d_i e^{-\Lambda_i(T-t_i^*)}.
\]

These are valid because the pair masses and coefficients are fixed. Exact total photon/event conservation does not automatically certify an energy ledger assembled from independently rounded excess and threshold energies.

The number-defect contraction does **not** directly control raw age moments. A passive packet has d_i=0 but its age and age moments change when its birth is moved.

The following independent analytical extensions hold for A_max covering both ages at T:

\[
|\Delta M_1|\le C,\qquad
|\Delta M_2|\le2A_{\max}C.
\]

Indeed, the first derivative of A e^-Lambda A is e^-Lambda A(1-Lambda A). For x>=0, |1-x|e^-x<=1: on [0,1] this is immediate, and on [1,infinity) its maximum is e^-2 at x=2. The first derivative of A²e^-Lambda A is A e^-Lambda A(2-Lambda A). Similarly |2-x|e^-x<=2: on [0,2] this is immediate, and on [2,infinity) its maximum is e^-3 at x=3. Its magnitude is therefore at most 2 A_max throughout the interval joining the two ages. Applying the mean value theorem per packet and summing nonnegative weights proves both bounds, including passive contributions.

If both survivor masses are certified at least N_min>0, normalized mean-age differences satisfy

\[
|\Delta\langle A\rangle|
\le\frac{C+A_{\max}D}{N_{\min}}.
\]

Without a positive lower bound on the denominator, a normalized-age certificate cannot be inferred from small absolute number or moment errors. These moment/mean statements are theoretical extensions in this review; they are not assertions that corresponding code outputs have already been implemented or verified.

For completeness, the normalized bound follows by writing

\[
\frac{M_{1A}}{N_A}-\frac{M_{1B}}{N_B}
=\frac{M_{1A}-M_{1B}}{N_A}
+\frac{M_{1B}}{N_B}\frac{N_B-N_A}{N_A}.
\]

Use |Delta M_1|<=C, M_1B/N_B<=A_max, |Delta N|<=D and N_A>=N_min. In a numerical certificate, C and A_max require upper endpoints and N_min requires a strictly positive lower endpoint; central floating estimates alone do not supply these hypotheses.

## 7. Numerical and scientific limits to retain

1. Every input rate, mass, energy and clock must be finite and in its declared domain. Preserve exact rate sums and exact time differences/products before exponential enclosure.
2. An exact positive tau may be far below binary64 range. Do not form tau by a premature floating product or interpret an underflowed tau as zero.
3. Computing 1-exp(-tau) from already rounded survival intervals remains valid with directed subtraction, but can be very loose for tiny tau. Report interval width; a small number is not evidence that cancellation has been bounded sharply.
4. Signed sums may cancel. D and the affine bound enclose a sum of absolute packet discrepancies, rather than claim to equal the signed total discrepancy.
5. Native preparation has its own reconstruction and omitted-tail diagnostics. Certification of the exported finite node family does not enclose errors between that family and a continuous source spectrum.
6. The 64 source templates are held fixed. Their coarsened clock experiment does not replace the separately READY source-matched native age32/block-max/diagnostics execution or prove native time-grid convergence.
7. Frozen endpoint gas and geometry suppress opacity feedback, spectral redshifting along the path, changing reconstruction and threshold crossings. A nonlinear Grackle response bound would need additional state/geometry/opacity control and residual or stability evidence.
8. Reusing VigilODE's nonnegative affine transport machinery is mathematically appropriate for this conditional bound. It does not establish a performance comparison or accuracy claim for VigilODE's general stiff ODE integrators.

The reviewed theoretical construction is useful as a rigorously enclosed, native-derived controlled experiment that isolates clock movement and preserves packet labels. Existing completed native campaigns remain reusable, and their unresolved accuracy questions remain unresolved.

## 8. Review provenance

This review uses direct elementary derivations and the actually read project sources/export records. External search/CAS work is handled separately by root; I did not repeat those queries or claim a CAS proof. The exact exponential remainder sign, cutoff witness, paired defect, recurrence, association counterexample and moment derivative bounds above are independently derived here.

Implementation-level checks still belong to the final source review: actual directed arithmetic postconditions; safe nonnegative operations; all-birth endpoint coverage; zero-rate/zero-defect branches; chronology of affine composition; and the exact data identities consumed by the executable.

The actually read root `THEORY_KO.md` includes the exact-tuple grouped-prefix equality, the independent-upper-endpoint caveat, the age-marginal association counterexample, and the separate moment/normalized-age hypotheses. These match the derivations above. **No unresolved mathematical blocker was found in that scoped theory document.** Counts, execution status, and final Rust behavior remain subjects of the execution records and C9 review, not a mathematical conclusion from this R6 review.

