# HE17 R3: exact warm target, observable projection and recovered stability bounds

2026-10-14, Asia/Seoul. Selected R3 only, following actual HE47 head dff95caa7fabb2a38acf73ba0946a1d88a125f3d. No R4+, source RHS/ODE, native consumer or old scientific suite was executed. Same-author arithmetic/CAS, external independent scientific review and native subagents NOT_RUN.

## Main progress

The NEW HH64 archive contains the actual same-warm-source whole solution tube and base-F0 A/BC derivative bounds. They were recovered and read, rather than inferred from its small differential response. Exact NPZ and emissivity identity, initial gas and number semantics match the selected P01. The original tube covers all lambda in[0,1], so includes the lambda0 OFF baseline. Original interval proof is inherited supplier evidence, not independently rerun here.

Current exact-rational assembly gives weighted gain0.03688471538571052845775948450009794 and residual amplification<1.03830. The actual residual remains to be bounded. Separately, the already certified whole-source tube gives a NEW coarse absolute finite-model Thomson interval with full relative width about6.917104448ppm. Do not keep all absolute intervals null merely because the sharper residual certificate is unfinished.

## 1. Three different objects and a fixed target

Receiver: rei_bianchi a5c958c414dea41216b445c05f58df837f05cacb, P01_EVENT_BRIDGE02_17_NODE_0_1e11s. Keep warm FT03/Hui-Gnedin, Verner, HM12 initial UVB and ongoing emissivity, CaseA escape, prescribed dust+Lambda LRS BianchiI, normal-comoving gas, CR/RCT/HH OFF, no scattering/diffuse/backreaction.

Exact target uses frozen NPZ binary64 inputs as exact dyadic rationals and scientific coefficients/source-table decimal tokens as exact decimal values, with the original interpolation and branches. This matches the recovered supplier's explicit mathematical source. The compiled binary64 evaluator, its quadrature and guards are not defined as a smooth exact ODE. Physical calibration, continuum-energy and measured-constant uncertainties remain separate.

The new gas reference is PL through the actual4x17gas nodes, not historical DOP853 dense output. Its current nH(t)*chi(ghat(t)) also differs from R1's PL interpolation of saved proper ne. Preserve the original sampled diagnostic and account for the reconstruction bias explicitly:

    Ctrue-C_R1PL = (Ctrue-C_ghat)+(C_ghat-C_R1PL).

For an evaluated RHS, use the exact decomposition

    r*=ghat'-F*=(ghat'-Ftilde)+(Ftilde-F*).

Provider/background/forced-lift arithmetic belongs in the second term exactly once, unless already included in an interval evaluation of the first exact residual.

## 2. Same-source identity and whole-cell reference admission

Restored HH64 archive200932bytes SHA2561193878b63a18ab39daeb033447cbb10ffcf68633757d145dbfefbae4c58c323. Actual p01_comparison.json, PHYS22 source README, PHYS27 proof and input identity were read. The common NPZ SHA256 is3cbf35cf7910c37083de4c5b9db443c71b272f3877a48f74fb9f852fd70fe2be; emissivity88743ec9041a47fd12f47bf50a75a06903089e1afd992b5460a4af471249469b. All4exact initial gas values agree.

Inherited box: |g-g0|<=(1e-7,2e-7,2e-7,1e-4eV/H). Original whole-time Picard/box maximum ratio0.622721134601399982165596881662289<1. Actual saved-node box usage maxima are approximately0.0003522261,0.0072406659,0.0074742665,0.6224586700.

With f=3/38, chi=x+f(y+2z), Pi=1+f+chi and T=CT*w/Pi, CT=2eV_J/(3kB), the thermal inequalities CT*w-Tmin*Pi>=0 and Tmax*Pi-CT*w>=0 are affine. Together with Pi>0, species simplex and the box, they define a convex domain. Thus checked exact endpoints imply whole PL segments lie inside the same domain, without inferring an interior bound from samples. Equivalently, the ratio along a segment is the positive Pi-weighted average of endpoint temperatures.

The actual PL temperature range has outward short display[49999.77707704470,50000.00000000000]K, inside the inherited approximately49999.63846..50000.36154K tube. This does not prove its differential residual is small.

## 3. Exact transparent-photon projection for this observable

R2's inherited all-time branch bound q*(1-3e-6)<=E<=q and actual13.60/24.59/54.42eV activation thresholds imply784photons stay below every photoactivation. They have kappa=0 and zero gas photoionization/heat columns. All2120remaining photons stay above HI activation.

Read actual axisym_conditional.rs, ft03_controlled.rs, ft03_rates.rs and axisym_coupling.rs. The gas thermal equation uses -5H*u+Qthermal; photon energy uses -4H*rho-2s*DeltaP+Qphoton. With prescribed geometry, the latter does not feed the gas. The5ledger coordinates are feedforward. Thus

    (g,pA)'=FA(t,g,pA), pZ'=sZ(t), ledger'=H(t,g,pA,pZ).

The closed electron-relevant dynamics has4+2120=2124variables. This exact triangular projection preserves gas/current/column on the selected mathematical domain. It is not a changed native solver or a speedup measurement. Transparent forcing, radiation energy/pressure/work and validation data remain necessary for full radiation outputs. Native2913states are unchanged. Scattering/Compton, backreaction, new subthreshold channels or changed threshold coverage can break the projection.

R2's full-photon strict decay floor0 remains valid. No positive absorbing-block numerical damping floor is newly asserted.

## 4. Full thermal/electron-density Jacobian

Let L=(1-x,f(1-y-z),fy), U=(x,fy,fz), ne=nH*chi. Per-H net edges are

    j_a=ne*(beta_a(T)*L_a-alpha_a(T)*U_a)+L_a*Gamma_a
        -delta_(a,HeI)*ne*U_HeI*(delta1+delta2).

The fraction RHS is(jH,(jHeI-jHeII)/f,jHeII/f). Keep original binding, photo-excess and captured kinetic moment terms in the fourth component; w is eV/H, so its dilution is-2H*w.

If Fbar treats ne,T as independent intermediates, the exact4x4Jacobian is

    Jg = partial_g Fbar|ne,T + (partial_ne Fbar)*nH*ell^T
         +(partial_T Fbar)*(grad T)^T,
    ell=(1,f,2f,0), grad T=(-T,-fT,-2fT,CT)/Pi.

Actual Wolfram checks all16residual components. For the source RR moment kR=kB*T*alpha*(3/2+g), g=dln(alpha)/dln(T),

    kR'=kB*alpha*[(1+g)*(3/2+g)+dg/dlnT].

The last slope derivative is retained. Direct temperature-independent opacity does not remove CI/RR/DR/kinetic cooling feedback. Raw Grackle coefficients are not substituted for controlled FT03.

## 5. Residual-to-error gain from admitted A/BC

The recovered A and BC are nonnegative absolute-majorant arrays of the SAME base warm source. BC alone does not determine B and C individually. With an ideal forced photon lift, the same initial state and both references in the admitted boxes, define D_i(t)=sup_(s<=t)|g_i(s)-ghat_i(s)| and d(t)=integral_0^t|r_g|. Nonnegative diagonal photon damping and two time integrations give

    D(t)<=d(t)+P(t)D(t), P(t)=t*A+t^2*BC/2.

The actual forced lift retains HM12 emissivity; identical forcing cancels only in the difference equation. Transparent nodes remain forced. A finite lift must retain its evaluation residual or be enclosed relative to the ideal lift.

Using S=diag(1,1,1,32eV/H), infinity norm:

    eta=||S^-1 P(h)S||inf=0.03688471538571052845775948450009794...,
    ||S^-1 D||inf <= ||S^-1 d||inf/(1-eta),
    1/(1-eta)=1.03829730041142707068339860233966... <1.03830.

This is an amplification factor, not an error radius. Actual new cell residuals and finite evaluator/lift error are still uncomputed. In this infinity norm the electron dual coefficient is47/38, not the coefficient1 from the earlier l1 route. Componentwise ell^T D avoids this scalar relaxation.

## 6. New coarse absolute finite-model interval

The inherited positive whole-time density/box bounds yield

    c*1e6*h*nHlo*chi_lo <= Ctrue <= c*1e6*h*nHhi*chi_hi.

Exact Fraction endpoints are in results/ALIGNMENT.json. Short outward displays:

    Ctrue in[1.9240685872207397,1.9240818962501526]e21m^-2,
    tau in[1.27997868222660,1.27998753600347]e-7,
    P=1-exp(-tau) in[1.27997860030933,1.27998745408507]e-7.

Use passive diagnostic sigma6.6524587051e-29m2 once. Probability lower is B_lo-B_lo^2/2 and upper is B_hi-B_hi^2/2+B_hi^3/6, valid for0<B<1. The depth full width/midpoint is6.91710444799ppm. R1's exact stored-PL column lies inside this box but is not made exact by it.

This is newly derived coarse coverage of the exact-real finite-source IVP, conditional on the inherited supplier whole-tube proof. It is not atomic calibration or a fine residual certificate. Fixture observer is h, extra fixture tail0; physical continuation remains null. Current coarse interval is nonnull; fine residual interval and native-evaluation-error certificate stay null. The historical R2 status is not rewritten.

## 7. Actual checks and current sources

39new exact/source conditions passed, including4input identities and elementary controls. One actual Wolfram15.0.1 call:11scalar zero groups+3negative/domain conditions+5actual xTensor1.3.0zero groups. Submitted WL SHA2562fd85d4f7c930748a61282671c5c0791de2573131d96f8a426b85633439be062. Official xAct archive7a6c5f600868a3922668b020a15c0692f76574ff2a559808c62d460cef1b07be and xTensor.m04e1cf3c7e81f1eff61ca633c84537c3f3cbb0fdd42ea01441e89172086d8b36 verified. Outputs are normalized observed transcriptions, not raw connector bytes.

Same author/CAS, not independent scientific review. Tests-after, no fullTDDclaim. No source RHS/ODE/native/HPC or old science-suite calls. Optional container raw-Git DNS failure retained; successful full connector reads used instead. Primary Neumaier1994 parsed text and actual PDF page5 image inspected for standard residual/stability context; no theorem novelty claimed. Exa/SciSpace were used; approximate DAE reduction papers were not used as proof of this exact projection.

HH64 at6320b23c... contributes actual same-source tube/A/BC; next PHYS32_TWO_CENTRE_CONTINUUM_DEFECT. REI115 at39dce670... remains at selected same-SHEAR12 cubic; nextR9_SOURCE07_SAME_TARGET_CUBIC_RETURN_CONTRACT, no foreign numerical bound. NEW CR58 full compact at808d11c... gives finite-rate completion/projection context; nextNT_COULOMB_MATCHED_PARTITION_DECISION, no cold tau/L bound imported.

## Full evidence and next stage

[Full Korean report](https://drive.google.com/file/d/179V5ezurQ9fRVLDJyzkV_v5eyi2gscT2/view).
[Full original-input/contract/check/CAS archive](https://drive.google.com/file/d/1vk3UcTKkfgnqM-tQhQn-VaVfASOpnFKN/view):271210bytes,27members/26manifest payloads, SHA256c5a823691c52bfeed38d9815a45e0c1c365b062c204b198d2c4dcd12219e76cf. Local CRC/all hashes and relocated read-only verifier passed. Altered-copy input failed, restoration passed. Dropbox completed same271210bytes,id:BSpOijBcT10AAAAAAD5REA. New remote-output restoration not performed. Full report, exact rational results, identity witnesses, source snapshots, submitted CAS and actual outputs are in the archive; this compact file is not byte-identical to that longer report.

Next selected stage R4 compares practical same-source continuous reference/residual representations from the RECOVERED tube/states. Do not restart recovery or old ODE/atomic proof campaigns. Preserve the old ne-PL bias and account for evaluator/forced-integral errors once. Existing native source/current/bin and global owner obligations remain open. No production switch, merge, external-repo edit or new global gate.
