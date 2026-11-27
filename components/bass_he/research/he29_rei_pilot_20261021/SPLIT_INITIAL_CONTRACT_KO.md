# Matter/radiation 독립 초기값: 사용자 변경에 따른 작은 추가 pilot

2026-10-21 사용자 pi_ab 분리 지시의 구성적 추가 범위다. 기존28case를 재실행하지 않는다. 추가 범위는 새12case와 재사용6case의18point finite grid다. 이전28case와 이18point를 단순합산하지 않으며 전체 unique integration은28+12=40이다.

## 고정 grid와 재사용

Sigma_F0={0,.03}, Pi_m0={0,.0003}, Pi_r0={0,.0006}; 각 nonzero stress의 sign은±1. shear sign은 Sigma>0에서+1, Sigma0에서0. Pi_m0=0의6개는 기존 s00_p00_zero,s00_p02_minus,s00_p02_plus,s02_p00_zero,s02_p02_minus,s02_p02_plus 결과를 실제 identity에 연결해 재사용한다. 새12개만 Pi_m0=.0003, sign_m±, radiation0/±.0006로 적분한다.

## 초기 angular amplitude 역변환

upstream source4파일과 canonical solver는 그대로다. 초기 source density/Href와 shear q_s=Sigma_F/sqrt(6-Sigma_F²)는 기존 inverse다. radiation은 기존 initial_mapping(Sigma_F,Pi_r,sign_r,source)를 사용한다.

massive initial weight W_m=1+A_m P2(mu), allowed -1<=A_m<=2. isotropic radial weight와 Gauss3 angular integration에서 initial energy monopole은 A_m와 독립이고 pressure difference는 A_m에 선형이다. finite quadrature 자체의 source로 coefficient를 계산한다:

    M1 = CanonicalMomentumFV(30, amplitude=1, radial_cells=24,
         angular_cells=12, gauss_order=3).moments(0,0).pi_s
    mass_pref = Omega_m*.1/a_ref³
    Hinit = Href*sqrt(1+q_s²)
    C_m = kappa_t*sqrt(6)*rho_crit_J_m3*mass_pref*M1/Hinit²
    A_m = sign_m*Pi_m/C_m.

원래의 finite quadrature normalization을 사용하며 continuum radial approximation으로 바꾸지 않는다. roundoff residual은 실제 model.fields(0,initial_state)에서 다시 읽는다. abs error of Sigma_F, signed v_m, signed v_r 각각<=1e-12인 새 initialmapping검사. Am가 원래양성성domain을 벗어나면 임의로clip하거나gate완화하지 않고 parent에돌려보낸다.

## 실행·근거·코드 경계

massfraction.1,mass/T30,radial24,angular12,Gauss3,L8,Tcmb2.7255,ne_sourceNone,a1/21→.2,n101,DOP853rtol3e-11atol3e-13 동일. 기존N0<=5e-11/nonnegativecells 그대로. sandboxmax2workers, 누적compute60s이내. detailedbenchmark0.

새 split_pilot.py API는 case_grid/case_identity/completed_result/run_case/write_case로 기존runner와호환. 기존 source/coordinates/pilot guarded bytes는 수정하지 않는다. 새 API own source-binding+identityversion을 분리한다. 공유runner는 명시적 campaign choice만 추가, default기존pilot동작유지. 동시다른세션은 actualavailableCPU/RAM/lease로공존, samecase중복금지. old28fullsuite/science재실행0.

신규12개 raw40×101state+101diagnostics를 보존.18pointview에는재사용6개원본경로/identity를 참조하여재실행으로세지않는다. Pi_m,Pi_r,signedv_m/v_r,Pi_total,alignment를전부보존. 원래initialPi_m0slice그림도역사기록으로유지하고새독립grid그림을추가한다.

검증은 새initialmapping과source/oldresultreuse에필요한targetedfixture만. 기존독립검토를재개하지않고 사용자changedscope의delta를1회검토한다. 일반triaxial/fullEoR/continuousconvergence/HPCspeedup주장은변경하지않는다.
