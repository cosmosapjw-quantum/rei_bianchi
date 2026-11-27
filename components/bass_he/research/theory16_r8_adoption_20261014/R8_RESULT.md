# THEORY16 R8: scoped adoption and current supplier integration

2026-10-14, Asia/Seoul. Selected stage: **R8 only**, following actual PR42 NEXT_ACTION at `a4874b6483e66c310b76d645b2326f3b71721b49`. No unchanged R6/R7, source, ODE or native suite was replayed. This is an author-owned scoped adoption decision, not external independent scientific review or whole-cycle/production promotion.

## Decision

Retain and adopt R7's constant-flow/source-age current/opacity reference consumer in its original scope. Receive the NEW CR53 moving-source current certificate as a separate source-bound supplier result, with its original proof/execution status. Receive HH59's completed tight near-rate certification without inserting an HH coefficient into CR. Keep REI CR/RCT/HH OFF and existing native ownership.

The old static R7 interval and new moving CR53 interval are disjoint. Do not attach the new moving radius to the old static center. New exact reference completion and geometry/source definitions remain separately identified; this comparison is not an isolated geometry-only physical response.

## 1. Continuous-sky clock admission

Signature(-,+,+,+), x0=ct, U=c*u, u.u=-1, dx^a=c*k^a*ds, k.k=0. The source-age scalar theta is in seconds, q_a=c grad_a theta and u.q=1. Let D=-u.k>0 and A=q.k=dtheta/ds. For the same proper volume and bulk electron current, J_e^a=c*N_e*u^a/V and

    tau_T = c sigma_T integral [D/(V A)] N_e dtheta,

on a monotone A>0 source-age chart. R7 used the constant-weight D/A case and total free-electron census, not thermal-only count.

Write q=-u_flat+b with u.b=0, and k=D(u+s), u.s=0,s.s=1. Then A/D=1+s.b and q.q=-1+r^2, r=sqrt(b.b). Rest-space Cauchy-Schwarz gives the exact all-sky condition and bound:

    A>0 for every future null direction iff r<1,
    1/(1+r) <= D/A <= 1/(1-r).

Both extrema occur at s parallel/antiparallel to b. Uniform bounds on a region require sup(r)<1. The R7 beta3/5 normal-homogeneous case has r3/5, hence the continuous-sky range[5/8,5/2], not merely three sampled rays.

For r>=1 some age charts can stall/reverse on a ray. The original s-integral remains available; this is not a physical no-go. Example u=(1,0,0,0),q=(1,2,0,0),k=(1,-1,0,0) has u.q=1 but A=-1.

## 2. Orthogonal proper-age field: existence, not every clock

Let a_b=u^c nabla_c u_b be geometric acceleration (1/length; physical acceleration c^2*a). The standard1+3 split gives

    C_ab=2 nabla_[a u_b]=-u_a a_b+u_b a_a+2 omega_ab,
    u^a C_ab=a_b,
    h_a^c h_b^d C_cd=2 omega_ab.

On a smooth locally contractible torsion-free patch, there exists theta with c grad theta=-u_flat iff a=0 and omega=0. Necessity follows from commuting scalar derivatives and these projections; sufficiency follows from the closed one-form and the local Poincare lemma. Shear need not vanish. This does NOT force every independently synchronized proper-age field to be orthogonal, and is not a global topological assertion.

Irrotational alone implies hypersurface orthogonality with a lapse, not a normalized proper-time gradient. Flat spacetime u=(cosh eta(t),sinh eta(t),0,0) is an explicit accelerating irrotational counterexample: C_01=cosh(eta)*eta_dot/c. A nonorthogonal proper-age field still exists, theta(t)=integral dt/Gamma(t), q=(1/Gamma,0,0,0). The formula t/Gamma(t) would add the incorrect derivative -t*Gamma_dot/Gamma^2; R7's t/Gamma remains valid for its constant Gamma premise.

These are standard local geometric facts, checked here for the R8 scope boundary, not claimed novel. Primary comparison: Ellis and van Elst, gr-qc/9812046v5, Eq11 and the irrotational-flow section. Parsed primary text and Exa passages were read; two PDF screenshots failed with Cache miss, so no visual-inspection claim.

## 3. NEW CR53 source-bound intake

Current source commit `cc3249947a1fc93f2bacf2190604371dfde2f42f`, actual source ZIP SHA256 `5e48631308ff68dc89287463094cb04561735fcd26fea1e3309b558ed555e4d8` was restored and checked. Full report, CONTRACT, NEXT_DAG and RESTORED_CERTIFICATE were read. No upstream producer was imported or executed.

Retain prescribed inversion-symmetric Bianchi I, H=(2,4,6)e-15/s, h=100000 proper seconds and V(t)=V0 exp(Theta t), Theta=sumH. Its initial opposite P/S pairs and isotropic daughter marginals preserve zero spatial electron current. The source's non-tilted normal clock has A=D=1, but its changing volume/source prevents reuse of a static numerical center.

Full source residual B and total-energy difference Delta obey the supplier theorem

    |delta Nfree| <= (B+|Delta|)/(2B_H),
    |Delta(t)| <= g* integral_0^t B(s)ds + C_U*t^2/2,
    g*=max(2Hmax,2Theta/3)=1.2e-14/s.

With B1=integral B and B2=integral(h-t)B,

    Delta1 <= g*B2+C_U*h^3/6,
    R_tau <= c sigma_T/(2V0 B_H) [B1+Delta1].

The bound uses exp(-Theta t)<=1; the actual source reference center keeps that discount:

    tau_ref=c sigma_T/V0 integral exp(-Theta t)(3+x_H+x_He)dt.

This reference integral was supplied by CR53's positive uniformization, not newly integrated here. R8 actually recomputed the bound assembly from stored outward endpoints using exact Fractions.

B1 is approximately2.09820844353966e-4eV s; Delta1<=8.65504335467646e-10eV s. R_tau<1.528609867904e-25. Within this NEW source the certified radius improvement over the energy-only projection is1.99999175009739409572636933505..., not exactly2. Static R6 still gives exactly2 when Delta=0. The separated stopping-event norm remains2Eparent; the invalid2DeltaE norm is not reinstated.

Outward short displays:

    tau_ref approximately5.94727990495093831576e-15,
    tau_full in[5.9472799047980773e-15,5.9472799051037994e-15],
    tau_full-tau_initial in[1.2367901235e-23,1.2673623210e-23]>0.

Full-minus-reference sign remains unresolved. The old static lower endpoint minus the new moving upper endpoint is3.2830040186031967913697824391216e-24>0. The centers differ by3.56836793938814527e-24. This shows they are not interchangeable, not that a fully matched physical geometry effect was measured. CR53 also carries a separately declared exact NPZ mass completion; originals remain unchanged.

The full CR53 source theorem and its135checks are inherited supplier evidence, not independently reproduced by this R8. Source/model/atomic uncertainties and production admission remain distinct.

## 4. Correct current successors

The actual CR53 NEXT_DAG marks NT_GEOMETRY_TEMPORAL_BINDING as DERIVED_AND_EVALUATED_SCOPED_NO_EVENT_INTERVAL and the primary restoration as scoped complete. Its next node is **NT_ACTUAL_PREFIX_EVENT**, not replay of the completed no-event result. The new HE supplier offer is CR-IR-04 / results/RESTORED_CERTIFICATE.json. An older static-rebind filename retained elsewhere in the source DAG is not selected as the new moving-current authority. No external DAG was edited.

NEW HH59 at `200bcc3e8c815d3426b850c6adc1f9b583d84049` supplies the completed near-window/T-box interval[7.6320925e-12,7.6326272e-12]cm3/s. Actual R5_RESULT and NEXT_DAG were read. Its exact endpoint width5.346110465403657e-16 is distinct from subtraction of the short printed endpoints. This is an analytic-remainder/directed-arithmetic result in the fixed S65 restored model, not atomic calibration or a high-energy physical tail. Next: **PHYS27_RESTORED_NEAR_RATE_EXPOSURE_TRANSFER**. No HH coefficient is imported into CR.

REI114 current head remains `a5c958c414dea41216b445c05f58df837f05cacb`: warm FT03 CaseA, proper rates/comoving stocks, redshift/shear work, escape and exactly-once ownership; CR/RCT/HH OFF unchanged. Conservation alone does not exclude event duplication.

## 5. Actual R8 evidence and preservation

-26read-only source/Fraction checks passed, exit0; some are source/status checks, not26theorems.
-2actual cloud Wolfram15.0.1 calls:11scalar groups True and7actual xTensor1.3.0 tensor residuals0.
-Official xAct archive SHA2567a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be; xTensor.m SHA25604e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36.
-Submitted scripts were saved before calls. Outputs are normalized observed transcriptions, not raw connector transport bytes. Scalar Ga[t] pre-analysis warning retained.
-Same author, separate arithmetic/CAS; native subagents and external independent review NOT_RUN. No old suite/source RHS/ODE/generator/native/HPC execution.
-Optional raw Git acquisition in the container failed DNS; actual connector text/blob IDs and restored computation inputs remain available. No extra Git raw-byte claim. A pre-upload nested-manifest coverage filter was corrected; no scientific source/result changed.

[Full Korean report](https://drive.google.com/file/d/1ykKu6kC7S3cKXT-pYV81jkIoKZYSPt77/view).

[Complete reproducible R8 archive](https://drive.google.com/file/d/1PiXvkfoGMgYPn97Y0QVKpP1cGscfRTob/view):182957bytes,86members including85manifest-bound payloads, SHA256 `9652a354e4ce693c1971bbecd10cc9e2be88afdbee535284687451b52ba34286`. Local CRC/all payload SHA256 verified. Dropbox same182957-byte completed object `id:BSpOijBcT10AAAAAAD47Mg`, existing BASS_DERIVATION_DOSSIERS_20260912 directory. Standalone report17721bytes also completed: Dropbox `id:BSpOijBcT10AAAAAAD47Mw`; report SHA256aa334eb4134c72da78c97899151e41b25bd58bbc30d5a9f4c72d96c3a4ad7ab8. Drive acknowledgements returned correct names/parent. No separate R8 remote restore test.

Full proof, exact input/result files, check scripts, failures, source registry and decision are in the archive. Run `python checks/check_reuse.py` or read-only packaging check `python checks/verify_bundle.py` from BASS_HE_R8_20261014. No fonts or source-paper PDFs redistributed.

Next selected stage: **R9**, formal result/code connection using existing evidence and the actual CR53 moving supplier, not a new old-suite campaign. HE native provider/moments/moving-stage/certificate-adapter, actual receiver binding, RUX/all-Bianchi/D2.3, independent review and R10 remain outside this completion. No new global gate, merge, production switch or external-repo mutation.
