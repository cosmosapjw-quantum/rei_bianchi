# HE17 R5: whole-cell residual, first-exit closure and electron column

2026-10-14 Asia/Seoul. Selected R5 only. **COMPLETE_SCOPED_FIRST_CELL_CONSTRUCTIVE_CERTIFICATE** on t in[0,6250000000] proper seconds. Other15cells and native receiver remain open. Original R3 whole-history coarse certificate is unchanged.

## Two real R4 variants, one explicit target

The conversation predecessor is the411210-byte first-cell R4 pilot, SHA2568120b32e9fd2e58f1b899645ab1be3b268e33094336be0362878aafe8f0fa0b2. Its immutable FIXED_REFERENCE.npz SHA256 is **7a2015398e7857ecb8dccb05482e246d7c412816eace6153f1c47eceb9b983be**. The same left/right2913-source state agrees with remote PR49, but gas slope indices1and2 differ at BOTH endpoints.

Actual PR49 head40659a752b9348fb7919cf5afcf42f310e05d064 and its787458-byte archive SHA2564f5d874865e3563d495b2f4de68450aaea7ed957ea90ef3a7c90b85d59a294c2 were restored/read. This branch stacks on that head for publication but certifies the **attached first-cell coefficients**, not the different remote all-cell slopes. Both original archives and exact hex slope comparison are preserved. No original overwritten.

The formerly unbacked-up attached R4 archive was preserved first on both providers: Drive1n7C5U3JXqqqlY9zKBVn9xIhZzS4wjIac and completed411210-byte Dropbox id:BSpOijBcT10AAAAAAD5WXQ. That is upload acknowledgement/size, not a new restoration test.

## Exact source and observable

Preserve rei_bianchi a5c958c414dea41216b445c05f58df837f05cacb warm FT03/Hui-Gnedin CI/RR/DR/captured kinetic moments, Verner photoabsorption, HM12 forcing, CaseA escape, prescribed dust+Lambda LRS BianchiI, normal-comoving gas and CR/RCT/HH OFF. Exact dyadic NPZ/slopes and exact-decimal scientific/table tokens; source branches unchanged.

P01_STATE.npz SHA2563cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be; emissivity SHA25688743ec9041a47fd12f47bf50a75a06903089e1afd992b5460a4af471249469b. Signature(-,+,+,+),x0=ct,u.u=-1,c=299792458m/s,kB and epsilon_eV retained. N_j is the original reference-volume photon stock; ne=nH*chi is already proper.

For g=(x,y,z,w[eV/H]), f=3/38:

    chi=x+f(y+2z), Pi=1+f+chi, T=2epsilon_eV*w/(3kB*Pi).

The new column is C=c_SI*1e6*integral nH_cm3*chi dt. Sigma is applied once. Pcond=1-exp(-tau_cell) is a first-cell conditional probability; the remaining15cells are NOT set transparent to fabricate the full P01 observer probability.

## Actual whole-cell residual construction

Let h=6250000000s and z=t/h. The fixed cubic is yhat=y0+z(a+z(b+zc)), with a=h*m0,b=3(y1-y0)-h(2m0+m1),c=-2(y1-y0)+h(m0+m1). Slopes are data, not assumed exact true derivatives.

    r_g=yhat_g,z-h*F_g(t,ghat,Nhat),
    r_Nj=Nhat_j,z-h*(S_j-kappa_j(ghat)*Nhat_j).

For each gas/photon residual, an interval Taylor jet at z1/2 supplies c0,c1,c2. A separate jet with base point z in[0,1] supplies M3>=sup|r'''|/3!. Thus

    r(z)=c0+c1(z-.5)+c2(z-.5)^2+R3,
    |R3|<=M3|z-.5|^3.

The quadratic is bounded with16exact Bernstein subintervals. These are polynomial ranges, not16sampled source evaluations. On a local delta interval[a,b], controls are q(a),q(a)+(b-a)q'(a)/2,q(b). Exact remainder weights are1/8(sup),1/32(integral),1/64(integral weighted by1-z). All2904photon and4gas coefficient intervals are stored.

With S=diag(1,1,1,32eV/H), scaled gas residual suprema over the ENTIRE first cell are below

    (4.105455440421100e-27,
     2.546373344693415e-26,
     4.352920287861580e-28,
     1.983767658956963e-27) /s.

Midpoint values agree with the separately preserved R4 mp80 calculation to its55exported significant digits. That agreement is a check, not the supremum proof.

## Provider/background arithmetic and domain

Actual mpmath1.3.0 iv70decimaldigits/236bits basic real arithmetic,exp,log,sqrt,pi is used. Powers/hyperbolics are constructed from these operations. All endpoints are extracted as exact Fractions before matrix/observable assembly. The overall iv library is experimental; only the stated supported primitives are used/tested. No blanket formal-library-verification claim.

Background volume uses its exact hyperbolic formula. The b integral does NOT call scipy.quad: midpoint b is enclosed by a degree7 Taylor integral plus its whole-interval eighth-coefficient remainder; b_n=h*si*(1/Vrel)_(n-1)/n. Whole-cell b0 lies in[0,h*si] since Vrel>=1. The column itself is integrated by degree6 midpoint Taylor with whole seventh-coefficient remainder/1024; that remainder is below1.695328e-25m^-2, and all coefficient arithmetic is included.

Actual photon energy intervals stay strictly inside the selected HM12 knots and Verner branches13.60/24.59/54.42eV;50000eV ceiling and one-sided initial redshift slab are retained. Candidate float indices are admitted only after strict interval branch checks. Positive source follows nonnegative convex table interpolation.784nodes have kappa=0, so no artificial uniform positive decay floor.

## Fresh A,B,C and a closed first-exit proof

Do not assume the old photon moment box contains the new reference. Before gas-box exit, photon positivity/nonnegative loss gives

    0<=N_true,j(t)<=N0,j+h*Smax,j,
    0<=Nhat_j(z)<=max4 Bernstein controls.

The true envelope and the reference envelope have different roles. A bounds the FULL warm gas Jacobian over the original gas box and a NEW positive moment box from N_true upper. Population,ne,T,CI/RR/DR and captured heat derivatives are all included in4interval derivative-seed evaluations.

B_j is derived directly from the actual per-H RHS:

    c_cm/Vrel * ((1-x)sH,
       (1-y-z)s1-y*s2,
       y*s2,
       (1-x)sH(E-chiH)+f(1-y-z)s1(E-chi1)+fy*s2(E-chi2)).

C_j=|grad_g kappa_j|*Nhatmax,j, with

    grad_g kappa=c_cm*nH*(-sH,f(s2-s1),-f*s1,0).

Scale B rows by S^-1 and C columns by S. Transparent B/C columns are exactly0, while their source/radiation diagnostics remain. BC is summed from these actual columns, not factored from an inherited product.

For scaled gas sup error D and exact matching initial values,

    D<=P D+dg+dN,
    P=h*A+h^2*BC/2,
    dg=integral_0^1 |S^-1*r_g| dz,
    dN=h*Bbar*integral_0^1(1-z)|r_N| dz.

The single h in dN is essential: r_N is normalized-time residual. The photon damping propagator is bounded by1. Actual exact rational assembly gives

    ||P||infinity<.002305049865369801,
    scalar amplification<1.002310375395865.

(I-P)^-1 is nonnegative, computed by exact rational elimination. Physical gas errors are below

    (1.867341162183303e-17,
     1.156664096490416e-16,
     1.887246415248591e-18,
     2.883559638060174e-16 eV/H).

At every time, reference Bernstein range plus these errors uses at most.03890518536952801 of the original box radius. Entire gas box is inside the positive simplex and30000<T<110000K. Therefore a first gas-box exit contradicts the new error bound; nonnegative photons remain bounded byN0+hSmax. Local existence, continuation and uniqueness close the entire FIRST cell. This does not require rerunning or independently reviewing the old supplier whole-history proof. The old box is reused as a domain; the local first-exit closure is newly evaluated.

## Concrete true-model first-cell observable

Uniform electron error<2.810295655442819e-17/H; temperature error<1.683149832273425e-12K.

    reference C approximately1.20255077156020833000192525036e20m^-2,
    column radius<3125.496134708492m^-2,
    depth radius<2.079223396909791e-25,
    sigma_T=6.6524587051e-29m^2.

Outward short displays:

    tau_firstcell in[7.99991934859042920576e-9,
                      7.99991934859042962162e-9],
    Pcond_firstcell in[7.99991931659107441379e-9,
                        7.99991931659107491497e-9].

Exact rational endpoints are in results/CERTIFICATE.json. This is finite-model numerical accuracy, not atomic fit/calibration, measured constants, continuum-energy or physical cosmological accuracy. Native evaluator/receiver is unchanged.

The explicit new-reference minus old first-cell proper-ne-PL column is approximately-14086545.283074173577886885233949m^-2. It is a representation bias, not a physical effect or permission to silently change the R1 whole-history center. The new reference error and this bias are counted once each.

## Actual checks and failures

54new validation conditions,6local first-exit conditions and4jet unit tests passed. Counts overlap and are not independent scientific reviews. A narrow exp-jet RED->GREEN is recorded; other tests are tests-after. The final archive is relocated and read-only checked; altered fixed-reference input is rejected and restoration passes.

Two ACTUAL Wolfram15.0.1 calls:13scalar groups+3domain conditions in the main call;4actual xTensor1.3.0 final zero residuals. First tensor attempt had3nonzero expressions because scalar OwnValue a=aa contaminated indices; fresh symbol context repaired identical expressions. First failure and Limit warnings remain. xAct archive SHA2567a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be; xTensor.m SHA25604e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36.

Other preserved issues: optional FLINT install DNS failure(no FLINT result claimed), unsupported streaming API before execution, interval-left coercion repaired by equivalent Jet-left expressions, checker precision for55digit exported data, and an environment metadata probe initially observing default53bits before actual module236bit initialization. Input/model/certificate values were not relaxed to fix these issues.

Source ODE/native/HPC/old science suites:0. New interval source evaluations:2, each all2904photons+gas4; direct gas Jacobian seeds:4. Same author plus distinct arithmetic/CAS; native subagents and external independent scientific review NOT_RUN.

## Latest-source use and next

Read actual CR60 compact at2c404479469cb0e1bf1dd073a50c1e2123809606: its moment-ODE certificate is distinct from kinetic shape error, no numbers imported. Next NT_CORE_TAIL_KINETIC_DEFECT_PROPAGATION. HH66 detailedPR atdb88ed7c4054094bcff62668bafc0fef927f559d retains PARTIAL global outgoing control and PHYS33B continuation. REI115 actual R10 compact at7301cca7ab8452e96b21947d84a12726f84e13f8 retains its completed same-SHEAR12 cubic/native-component return; do not send its completed certificate back to null. Its prepared owner intake is separate. REI117 goal metadata is abundance-first; this HE optical proof is not a new mandatory global prerequisite.

Primary method context from SciSpace/Exa and official mpmath/Neher-Jackson-Nedialkov metadata; explicit Taylor/first-exit derivations above. No novelty claim for general methods and no source-paper PDF/font redistribution.

## Durable code and evidence

[Complete executable first-cell certificate](https://drive.google.com/file/d/1VGQyQViQ6f9nzPZEgWe4beRfY6wdCisk/view):4384604bytes,73members/72manifest payloads, SHA256 **2f29435ea39adb4aa136075a201a2904767798b4ef2a966bae452a134462ae08**. Dropbox completed same4384604-byte object id:BSpOijBcT10AAAAAAD5crw. Local CRC/all72hashes, relocated verifier, altered-input rejection/restoration are observed. No new R5 remote restore.

[Full Korean report](https://drive.google.com/file/d/1pErrttCw0iGZQxNcuH8Vlu_3LlyxTE2G/view),22804bytes,SHA2569cc3ac839482527997b80396f80e166e5d0d167f7cca02079c4beeeef2ecee71. Its complete bytes are also inside both successful ZIPs. Standalone Dropbox report status is recorded separately in delivery, not presumed here.

Git contains the substantive proof and resume entrypoint. The full tested interval/Taylor code, all coefficient intervals, exact inputs, comparison matrices, failures, observed CAS and both R4 archives are in the immutable ZIP. Run python checks/verify_package.py for a read-only check. The README lists exact new-R5 regeneration commands, which do not call the old source ODE.

Next selected stage **R6** reviews this first-cell claim and its implementation, reusing existing evidence. Remaining15cells, error memory, actual native source/clock/current/bin integration and original global/source calibration duties remain open. No R6-R10 completion, new global gate, main merge, force push, production switch or external-repo mutation is claimed.
