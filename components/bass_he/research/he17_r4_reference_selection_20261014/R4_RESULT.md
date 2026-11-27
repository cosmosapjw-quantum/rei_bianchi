# HE17 R4: continuous reference selection and filtered photon defect

2026-10-14, Asia/Seoul. Selected **R4 only**, following actual HE48 head `8acae2b459d23140e0436e07f277c68d11f4424b`. Same warm P01 target at rei_bianchi `a5c958c414dea41216b445c05f58df837f05cacb`: exact dyadic saved inputs, exact-decimal FT03/HM12/Verner model, Case A, prescribed normal-comoving Bianchi I, CR/RCT/HH OFF. No new nonlinear history ODE or native source run.

## Decision and substantive new result

Select **RHS-Hermite plus positive filtered photon residual** for the next whole-cell proof. Keep PL/finite-difference cubic as controls and first-cell forced Duhamel as an alternative. New screening uses the real recovered source, not a manufactured physics model. The selected sample gas defect is about35019.7times smaller than PL and18.24times smaller than finite-difference cubic. Those ratios are sampled-defect ratios, NOT true-error or runtime improvement factors.

The new reference and saved RHS slopes are explicit immutable objects. They are not the historical DOP853 dense polynomial. Keep R3's coarse true-IVP bound unchanged; no fine residual certificate is issued here.

## Exact reference representation and domain

Use gas g=(xHII,yHeII,zHeIII,w_eV/H), photon N_ref in cm^-3 reference-volume stock, and all2904photon coordinates. Only the5feedforward ledgers are omitted in this mathematical prototype, so Y has2908coordinates; no native pruning. Proper seconds, signature(-,+,+,+), x0=ct and physical c,hbar,kB retained.

At each of17saved nodes, evaluate the same source with the new numerical reference evaluator, round the slope once to binary64 and preserve that dyadic slope in results/RHS_SLOPES.npz. h_i=6250000000s, s=(t-ti)/h_i, DeltaY=Y_(i+1)-Y_i:

    P_i(s)=Y_i+h_i*v_i*s
      +[3DeltaY-h_i(2v_i+v_(i+1))]s^2
      +[-2DeltaY+h_i(v_i+v_(i+1))]s^3.

Shared slopes make the reference C1. It need not have exact-RHS endpoint derivatives; the final residual includes any derivative mismatch. The equivalent Bernstein controls are Y_i, Y_i+h_i*v_i/3, Y_(i+1)-h_i*v_(i+1)/3, Y_(i+1).

Exact Fraction evaluation of all16*2908*4=186112scalar controls proves photon positivity and the same inherited gas box/simplex/affine thermal guards over WHOLE cells. This count is not186112independent scientific claims. Max gas-box usage is10950408726875/17592186044416=.6224586699588031... . Since Pi=1+f+x+f(y+2z)>0 and T=C_T*w/Pi, temperature inequalities become C_T*w-Tmin*Pi>=0 and Tmax*Pi-C_T*w>=0. This verifies the polynomial's domain, not its error to the IVP or the ideal photon lift's full supplier box.

## Actual numerical discriminator

Same evaluator and sample locations s=0,1/4,1/2,3/4,1 for every cell; S=diag(1,1,1,32eV/H). Define d=max_sample h_i||S^-1(P_g'-F_g(P_g,P_N,t))||infinity.

| Reference | sampled d | sampled local h_i^2/2 photon-to-gas indicator |
|---|---:|---:|
| PL |5.86179368929850e-12|2.25948752241025e-15|
| finite-difference cubic |3.05297082113001e-15|1.38106593304545e-18|
| RHS-Hermite |1.67385769245326e-16|3.71738718710390e-23|

The second indicator uses actual point |partial F_g/partial N_j|. It is neither a whole-cell maximum nor a carried-memory bound. All240raw sample records are retained. The screen made257fresh reference point RHS calls, observed1.18994seconds; no ODE. The numerical lane is NumPy longdouble with64mantissa bits on this host, despite its float128 dtype name.

A distinct mpmath65-digit gas/source evaluation at3selected points confirms the small residual. At the worst screen point (cell index1, midpoint), h-scaled norm is1.67385807943058667434e-16. Max longdouble-versus65digit absolute discrepancy at those3points is3.86977323554e-23. This is numerical cross-checking, not a directed all-roundoff bound. Actual original endpoint gross-event comparisons give relative maxima1.92405e-13 and9.51715e-13; near-equilibrium net cancellation is not normalized by the tiny net source.

A useful exact counterexample: y'=4t^3,y0=0 on[0,1] has y=t^4. Endpoint value/slope Hermite is P=2t^3-t^2, with residual r=6t^2-2t-4t^3. r(0)=r(1/2)=r(1)=0 but r(1/4)=-3/16,r(3/4)=3/16. Midpoint/endpoint agreement cannot certify the interior. Even the five-point screen above remains a screen. A fixed-slope endpoint perturbation epsilon changes P' by6epsilon*s(1-s)/h; node quantization is a possible small-defect component, not a proven exclusive explanation.

## First-cell Duhamel alternative actually computed

For the same gas cubic and actual initial photons, evaluate

    Nbar_j(t)=exp(-K_j(t))*N0_j
      +integral_0^t exp[-integral_s^t kappa_j(u)du]*source_j(s)ds.

Only first-cell quarter/mid/three-quarter points were computed with Gauss6/10. This made6conditional integrals,504kappa evaluations,9gas point RHS calls; observed3.79773seconds for a different workload. No nonlinear IVP was solved. Max change to h-scaled gas RHS versus the photon cubic was2.17236e-23 while gas defects there are approximately1.2e-16..1.6e-16. Gauss6/10 photon relative difference<=6.34e-19 is NOT a quadrature remainder certificate.

This pilot supports first bounding the already small photon-cubic residual rather than recomputing an entire forced history. The Duhamel option stays available.

## Exact positive-filter connection for R5

Let Ntilde be the cubic photons and Nbar the IDEAL forced solution for the same gas reference. With

    r_N=Ntilde'+kappa(ghat,t)Ntilde-source,
    e_N=Nbar-Ntilde,

we have e_N'=-kappa*e_N-r_N,e_N(0)=0. Source cancels in the difference but remains in Nbar. Gas F is affine in N at fixed g, so

    r_g,ideal=r_g,computed-B(ghat,t)e_N,
    |r_g,ideal|<=|r_g,computed|+|B|*|e_N|.

The actual source-derived photon column B_j is

    c_cm/V * [(1-x)sigma_H,
       (1-y-z)sigma_1-y*sigma_2,
       y*sigma_2,
       (1-x)sigma_H(E-chiH)
         +f(1-y-z)sigma_1(E-chi1)+f*y*sigma_2(E-chi2)]^T.

Here f3/38, V=a_rel^3, energies in eV. It is not an invented factorization of inherited BC. For valid whole-cell constants kappa>=lambda>=0, |r_N|<=rho, the nonnegative error filter obeys

    z_out<=exp(-lambda*h)z_in+h*phi1(-lambda*h)rho,
    integral_cell z<=h*phi1(-lambda*h)z_in+h^2*phi2(-lambda*h)rho.

phi1(0)=1 and phi2(0)=1/2. Thus transparent channels use z_in+h*rho and h*z_in+h^2*rho/2, without a false positive decay floor. Carry z_in between cells, never reset it to0. Whole-cell gas residual, photon residual, B and provider/background evaluation bounds are NEXT work. Then the same-source R3 resolvent cap1.03830 and S-infinity electron factor47/38 apply under their original premises. The inherited ideal-photon box premise remains explicit.

## Preserve the old observable reference

New65digit scalar quadrature of exact-model nH(t)*chi_Hermite gives

    C_old_ne_PL=1.92407524182795857872518825067696e21m^-2,
    C_new_ref approximately1.92407524182773452546271423458296e21m^-2,
    C_new_ref-C_old_ne_PL approximately-2.24053262474016094e8m^-2.

At diagnostic sigma6.6524587051e-29m², DeltaTau approximately-1.49050507635132353e-20. The column split is Hermite-versus-gas-PL -1.81280356520817e8 plus exact-geometry-gas-PL-versus-old-proper-ne-PL -4.27729059531988e7m^-2. These are numerical reference changes, not true-IVP error or isolated physical geometry effects. Preserve C_true-C_old=(C_true-C_new)+(C_new-C_old). R3 coarse interval remains and fine true-IVP interval remains null. Fixture-final tail0 is distinct from unknown physical continuation.

## Latest sources, actual evidence and limits

HE48 head and actual AGENTS read. NEW HH65 at15a9ee97d7c1b27f65e289e61c614ce3a1ab894c full COMPACT_RESULT read: changed two-centre operator restores overlap and eliminated-space terms; no new full rate certificate or old-rate transfer. Retain existing same-P01 base-F0 tube/A/BC from HH64. HH next PHYS33_TWO_CENTRE_MULTIPOLE_RESOLVENT_CONTROL. Current CR58 metadata retains808d11c1869c6334572554edcb24370e35c69f44 and NT_COULOMB_MATCHED_PARTITION_DECISION; prior full compact is reused without numeric import. REI115 current R8 head39dce6702dcadbb516fc8e25e7ba5a6991f64c22 unchanged; next R9_SOURCE07_SAME_TARGET_CUBIC_RETURN_CONTRACT. No foreign source numbers or external-repo edits.

Exa/SciSpace searched primary Hermite/defect-control literature. Lang-Verwer doi10.1137/050646950 publisher metadata/abstract and official SciPy CubicHermiteSpline definition read. The polynomial/filter/counterexample identities here are directly derived; no unexamined collocation theorem is assigned to DOP853.

New actual numerical counts:271longdouble point RHS,3mpmath65 gas point RHS,6conditional first-cell integrals,504kappa evaluations, scalar reference-bias quadrature. Zero nonlinear ODE/native RHS/HPC/old science-suite calls. Helper2tests have genuine intentional-PL RED exit1 then cubic GREEN exit0; other research code is tests-after. Final helper2tests and45read-only source/assembly/record conditions passed, including13input identities.

Two actual Wolfram15.0.1 calls: first13scalar groups returned12True, one equivalent unexpanded zero False, and4actual xTensor1.3.0 residuals0. First all_pass=False and Power/Infinity warnings are preserved. A targeted Expand and direct transparent integral yielded3zeros; it closes the missing algebraic group without replaying xAct or claiming a single combined all-pass run. Official xAct archive7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be and xTensor.m04e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36 matched. Submitted scripts preceded calls; observed records are normalized transcriptions, not raw connector bytes. Same author plus separate arithmetic/CAS; external independent review and native subagents NOT_RUN.

## Complete durable research package

[Full Korean report](https://drive.google.com/file/d/1BfAQaJvEpydNVD1icaBNAj05lHo0OBHP/view).
[Complete code/inputs/fixed slopes/results/failures/CAS ZIP](https://drive.google.com/file/d/1PNLzArTHZxysmK9AyBMuhRFQUp9191r9/view):787458bytes,74members/73manifest payloads, SHA2564f5d874865e3563d495b2f4de68450aaea7ed957ea90ef3a7c90b85d59a294c2. Dropbox completed same787458-byte file in existing dossier directory, id:BSpOijBcT10AAAAAAD5SFQ. Standalone report17353bytes also completed both providers; Dropbox id:BSpOijBcT10AAAAAAD5SFg, SHA2562efc24ed753c9f368a8c1e5767f8fcbb50a24e2f39b04f8a1f67e05ba9ced193. Drive names/existing parent acknowledged. Local CRC/all73hashes and relocated verifier exit0; altered-copy source rejected exit1 then restored exit0. No new remote restore test or permissions change.

Read START_HERE_KO.md/REFERENCE_SELECTION.json/NEXT_ACTION.json and run `python checks/verify_package.py` from BASS_HE_HE17_R4_20261014. It makes no source calls. Numerical producers write results, so use a separate copy/new identity for any deliberate rerun; do not overwrite frozen slopes. Full tested sources are in the ZIP, not all expanded into Git.

Next selected **R5_HERMITE_FILTERED_WHOLE_CELL_CERTIFICATE**. Actual continuous residual/evaluation bounds remain; coarse R3, native/global/physical owners unchanged. R5-R10 were not executed. No merge, production switch, heavy queue or new global gate.
