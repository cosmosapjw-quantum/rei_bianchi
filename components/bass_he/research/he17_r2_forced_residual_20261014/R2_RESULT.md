# HE17 R2: warm-source evidence recovery and forced residual reuse

2026-10-14, Asia/Seoul. Selected **R2 only**, following actual HE46 `d9a60904225f90d0e139c9b220dbd583413ccb51`. Receiver is the same warm P01_EVENT_BRIDGE02_17_NODE_0_1e11s at rei_bianchi `a5c958c414dea41216b445c05f58df837f05cacb`. This delivers recovered inputs, source applicability and a mathematically explicit reuse map, not a completed warm trajectory-error certificate or new source solve.

## Recovered evidence

The original EVENT_BRIDGE02 archive,2024590bytes SHA25633745d9234a0ee2fe771c0c37329b889c551b05dc008eab41f360232938539bb, contains both the selected native NPZ and retained reference NPZ. They are byte-identical:188284bytes, SHA2563cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be. This establishes identity, not two independent accuracy estimates.

Actually recovered six arrays: q_eV/mu0/weights(2904,),initial_state(2913,),times_s(17,),states(2913,17). State rows are4gas+2904photon+5ledger. All17gas states/times match the selected JSON, and both archived full endpoint STAGE/RHS/EVENTS probes match the relevant states/photon stocks. Original HM12 UVB/emissivity tables, acquisition metadata, provider contract and Rust source snapshots are preserved in the new package.

Actual pinned writer `rust/rei_microphysics/python/source_bound_interval.py`, Git blob56031a19c7f139d59158aa7509c2fbaf57e5bbbd, stores only those six arrays. It invokes DOP853 with t_eval but without dense_output=True. Historical dense polynomial coefficients and all RK internal stages are NOT serialized in the selected output; only two complete endpoint probe sets are recovered. A call count is not a stage history. The statement is scoped to inspected sources/archives, not all user storage. A legacy Drive metadata search excludes ZIPs and is not treated as exhaustive archive discovery.

The related old BASS warm sampled-visibility contract atd520c5e47ebf5cf218351082430ae3ef5e1ab3ec was read. It uses the same provider/background but a different execution/NPZ77a144..., and explicitly lacks physical time/continuum error certification. Reuse its mapping definitions, not a nonexistent same-run forward-error bound.

## Whole-interval spectral regularity, actually checked

Keep prescribed dust+Lambda LRS Bianchi I, proper seconds and signature(-,+,+,+). With v=a_abs^3,

    H^2=D_G+B_G/v+C_G/v^2, s=s0/v, v_dot=3Hv.

Expansion makes H,s decrease and s^2/H^2=C_G/(D_Gv^2+B_Gv+C_G) decrease. Initial s/H=.001 implies H-s>0. Exact Fraction evaluation of the original constants proves(H0+2s0)^2<(3e-17/s)^2. For every null direction,

    E_dot/E=-H-s(3mu^2-1),
    q_j(1-3e-6)<=E_j(t)<=q_j, 0<=t<=1e11s.

The last inequality uses exp(-x)>=1-x, not endpoint sampling. All726unique stored energies/2904rays were compared with exact-real and original-binary64 knot hulls. No crossing of the377emissivity knots or556UVB knots occurs. Minimum relative margins are approximately5.41325e-5 and3.26035e-5. No activation crossing at the ACTUAL Verner thresholds13.60,24.59,54.42eV; minimum margins exceed3.30823e-4,5.51790e-4,4.73375e-4eV. Binding-energy thresholds are not substituted. The50000eV provider ceiling is respected. Redshift remains in the slab5.488..5.807; at initial5.807 use the lower-z one-sided branch.

784photon nodes remain below all photoactivation thresholds, hence kappa=0 there. A uniform strictly positive decay floor for the whole photon block would be invalid. Their forcing still remains. These are source-regularity results, not a proof that background quadrature/roundoff or warm state errors vanish. The original b(t) evaluator uses scipy.quad; its evaluation error is a distinct later term.

## Constructive reuse map

A new continuous reference can be constructed from the recovered gas4x17 values without recovering historical DOP853 internals. Piecewise linear ghat is already absolutely continuous; a later cubic choice needs its own reconstruction/positivity statement. Do not call the new curve the historical dense polynomial. Current from nH(t)*chi_hat(t) also need not equal R1's linearly reconstructed stored proper-ne curve; preserve that older diagnostic.

Set g=(x,y,z,w), f=3/38, chi=x+f(y+2z), Pi=1+f+chi, T=C_T*w/Pi with C_T=2eV_J/(3kB). Use a fixed positive normalization n_* to write p_j=N_ref,j/n_* and source s_j=S_ref,j/n_*.

    p_j'=s_j(t)-kappa_j(g,t)p_j,
    kappa_j=c_cm*nH_cm3*[(1-x)sigma_H+f(1-y-z)sigma_1+fy sigma_2].

The source s is the actual HM12 emissivity after the ray Jacobian: S_ref=emissivity.photon_emission_log(qR,z)*weight/R^3. It is not the initial UVB field. Given ghat, the conditional exact lift is

    Khat_j(t)=integral_0^t kappa_j(ghat(s),s)ds,
    phat_j(t)=exp(-Khat_j(t))*p0_j
              +integral_0^t exp[-Khat_j(t)+Khat_j(s)]s_j(s)ds.

It has the correct initial condition and zero IDEAL photon residual; finite quadrature/provider approximation must retain its actual residual. This lift was not numerically integrated here. Deleting the source integral gives residual -s, not zero; both stored endpoint probes contain positive source. At kappa=0 the correct expression is p0+integral s.

Define r_g=ghat'-F(ghat,phat,t) and r_p=phat'+kappa(ghat,t)phat-s. The exact photon error identity is

    e_p'=-kappa(g,t)e_p-[kappa(g,t)-kappa(ghat,t)]phat-r_p.

Different source evaluations add(s-shat). Equal prescribed forcing cancels from this error equation but cannot be omitted from the lifted reference.

Warm thermal feedback is retained:

    grad_g T=(-T,-fT,-2fT,C_T)/Pi,
    T-T_hat=[C_T(w-w_hat)-T_hat(chi-chi_hat)]/Pi(g),
    grad_g kappa=c_cm*nH*(-sigma_H,f(sigma_2-sigma_1),-f sigma_1,0).

The directly temperature-independent opacity block does not remove temperature dependence of CI/RR/DR and captured-energy moments in F. The actual same-source HE31 report1-155 supplies consistent gas/event coordinates; its backward-Euler elimination is not a continuous-history certificate.

For fixed gas scaling S_g=diag(1,1,1,w_*), Eg=||S_g^-1(g-ghat)||1 and Ep=||p-phat||1, valid tube-wide coefficient bounds give

    D+[Eg,Ep]^T <= [[alpha,C],[K,-kappa_min]] [Eg,Ep]^T+[rho_g,rho_p]^T.

Alpha is the weighted logarithmic norm of the FULL warm gas Jacobian. C,K are coupling bounds. For the whole photon set kappa_min=0 is the safe source-wide choice. No source-free SHEAR12 numeric coefficient or alpha=0 premise is transplanted. Actual warm tube/rho/coefficient values remain uncomputed. With same geometry, the resulting electron-column error is bounded by c_SI*1e6*integral nH_cm3*Eg dt since||(1,f,2f,0)S_g||infinity=1. Different nH/clock evaluations need their own terms.

Primary method support: Neumaier,Computing52(1994),315-336,doi10.1007/BF02276880, primary parsed Theorems3.5/4.1 and Proposition4.3; reconstructed residual plus stability/tube closure, not solver tolerance alone. SciPy1.17.0 official solve_ivp docs establish t_eval/dense-output semantics. These are known method ingredients; no novelty priority is claimed. Primary PDF screenshots failed and are not represented as successful visual inspection.

## Current related work

REI115 advanced to39dce6702dcadbb516fc8e25e7ba5a6991f64c22. Actual R8_SELECTION_AND_HANDOFF read: same SHEAR12 target's R7-A cubic certificate selected, R7-B and PL preserved as distinct alternatives. Its own node/bin certificate remains complete. Next R9_SOURCE07_SAME_TARGET_CUBIC_RETURN_CONTRACT. Only method structure is reused here, not source-free/thermal-independent numerical constants.

HH63 at13869fbd0ab6849613be694af3b0841c85a68b14 now has full fixed-model finite-rate enclosure[2.20545380e-12,2.21081970e-12]cm3/s. Actual compact1-62 and metadata read. Next PHYS31_COULOMB_RATE_SOURCE_BOUND_TRANSFER. No HH coefficient is applied to the HH-OFF warm source.

CR57 atef27d056b2f65e46fca3ba1bc8729015877b6f54 has scoped smooth-front/right-limit closure; actual compact1-60 and metadata read. Next NT_FINITE_RATE_ANGULAR_THERMALIZATION. Its cold source/closure/numeric bounds remain separate. REI116 was discovery-metadata only, not selected warm dense evidence.

## Actual checks and durable output

36new source/data/branch conditions passed; tests-after, including identity groups, not36scientific theorems. One actual Wolfram15.0.1 call:12scalar zero groups,3True conditions and4actual xTensor1.3.0 zero residuals, including current divergence. Official xAct archive SHA2567a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be; xTensor.m04e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36. Submitted WL SHA256daf7261d4cc2e583140ee5ff843c8e9249f71439e8b75d85a7f35ecdbeb53246. Observed output is normalized transcription, not raw transport bytes.

[Full Korean report](https://drive.google.com/file/d/1eGwQL_1LtoYPE36yhBZ_ZGJQ7WnK4I2L/view).
[Full original-input/check/reuse archive](https://drive.google.com/file/d/1cV9X2qDvh19xnBpmK06_Wp7vbyK5AM1v/view):822984bytes,37members/36manifest payloads, SHA256d68277a74c54ee25473f63275e68dd4838e63228ae007404811d7cbafefa3aa4. Local CRC/all payload hashes and relocated read-only verification passed. Dropbox completed same822984-byte ZIP,id:BSpOijBcT10AAAAAAD5QvQ. No new remote restoration test.

Run python checks/audit_sources.py for the new source checks; python checks/verify_package.py is read-only packaging/record verification. Sources include exact selected NPZ/tables/probes and explicit connector-source excerpts, not an invented complete source-tree restoration. No fonts or source-paper PDFs distributed.

Next **R3** aligns the reconstructed exact target, full thermal Jacobian, provider evaluation and tube conditions using these recovered inputs. True-IVP column/probability intervals remain null; actual residual/tube numbers are the remaining science, not a newly missing whole source. No old science-suite/source RHS/ODE/native/HPC run, production switch, main merge or external-repo mutation. Same author plus CAS; native subagents and external independent scientific review NOT_RUN.
