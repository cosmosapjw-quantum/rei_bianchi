# HE-FAST-IGM-RCT03C: photon/source 두 모멘트의 같은-stage 연결

FROZEN_PHOTON_STAGE_OWNER_BINDING_CHECKED__COUPLED_HISTORY_OPEN. 기존 source-free midpoint N1600의 7PASS는 보존하고 재실행하지 않았다. 원격 receiver 채택은 아직 수행하지 않았다. 이번 결과는 기존 native radiation kernel의 적분 사건수·흡수 에너지를 실제 IGM/RCT point에 연결하는 bounded adapter와 다음 coupled residual의 설계 검산이다. 새로운 photon-coupled root나 이력을 완료한 것이 아니다.

## 실제 사용한 코드

Supplier8212fc029f0cfa0d4c49f81e21b6dfe27b5b674c, receiver39c39eab1cc2f1a215723680accc123e67ef13b6을 읽었다. 부모 RCT03B의750payload를 확인하고 staged receiver36source+Cargo2를 불변 재사용했다. owner의 continuous-boundary-prototype-v2/src/primitives.rs blob f0a360c2be7f8530a0ed87ce87758c253e7c56a8을 실제 원본 바이트로 호출한다. short-hhe-midpoint의 radiation/material/coupled 원문도 읽어 계약을 결속했다. 현재 production의 source 수정이나 전체 라이브러리 재채택이 아니다.

## 결속한 두 모멘트

s=ln(a/a0),ell=Delta ln(a)>0, stage의 alpha_i=c*n_i*sigma_i(E_mid)/H를 고정한다. N'=q-alpha*N, E=E0 exp(-s), alpha=sum alpha_i에서 I0=integral N ds, I1=integral exp(-s)N ds다. 원 kernel의 A_i=alpha_i I0[events/H], B_i=epsilon_eV*E0*alpha_i I1[erg/H]를 각각 보존한다. N1+sumA=N0+q*ell, U_gamma1+sumB+redshift_loss=U_gamma0+injected_energy다.

기존 division-free material::photo_delta는 P=[A_H,(A_HeI-A_HeII)/fHe,A_HeII/fHe,sum(B_i-epsilon_eV*chi_i*A_i)]다. 다음 coupled residual은 U1-U0-dt*F_nonphoto+RCT(M)-P(Owners[U0,U1]), M=(U0+U1)/2다. F에는 photo input0을 주고 후보변경마다 원 affine radiation path/Owners를 다시 계산한다. photo RHS와 P를 둘다 가산하면 중복이고, 예전 후보의 Owners를 고정해도 다른 방정식이다. 최종 같은 stage에서만 상태와 전장부를 함께commit한다.

## 수학적 반례와 zero-absorber 경계

source0에서 exact survivor와 arithmetic endpoint mean 사건을 섞으면 A_trap/A=(z/2)coth(z/2),z=alpha*ell이다. 실제 동결 cell의 z403.8504233657453에서는201.9252116828726배였다. implicit midpoint 전체를 부정하는 반례가 아니라 서로 다른 quadrature를 섞는 오류의 반례다.

흡수 에너지에도 E_mid*A를 대신 쓰면 안 된다. 계획된 source0 cell의 실제 mean79.9980191176eV, E_mid79.6009983354eV에서 에너지가0.4962883% 작아진다. 다른 injection-only cell에서는0.00720263% 커졌다. 실제 He 스펙트럼이나 장기 이력이 아닌 frozen coefficient 검증이다.

rho_i=n_i/nH>0에서는 Gamma_eff=A_i/(dt*rho_i), heat_eff=(B_i-epsilon_eV*chi_i*A_i)/(dt*rho_i)로 actual point와 P의 동일성을 검사할 수 있다. 그러나 rho_i=A_i=B_i=0에서는 per-capita rate가 식별되지 않는다. 초기 adapter의 zero-fill을 실제 RED regression으로 잡고 radiation이 있으면 ABSENT_ABSORBER_REQUIRES_SPECTRAL_INPUT으로 거절했다. 따라서 production 연결 권고는 원 division-free P이며, 이 interior adapter를 생멸계수의 일반 공급자로 승격하지 않는다.

## 실제 수행과 제한

Native11tests통과: 원stub8runtimeFAIL, zero-absorber 추가RED1, 나머지2tests-after. gas2 x ell3 x (N0,q)3 x RCT3=54고유stage,18고유radiation입력. 같은mean35eV와KF96/GM25선택을 actual point에 넣었다. 13기호식과972고정밀비교의 최대상대차5.17361295257e-14는 고정한5e-13+1e-290 기준안이다. 직접구적6경우도 대조했다. material/photonenergy/photonnumber 장부 최대정규화편차는1.28493e-16/1.42502e-16/1.08850e-16이다.

최종zero-boundary수정후54point를다시실행해이전CSV와byte-identical임을확인했다. 총probe2회/108stage/216pointcalls이며독립성과로두번세지않는다. checker의ResourceWarning를명시적파일close로고치며재실행했지만수치결과는byte-identical이다. 전체sourcefree/원자/기존과학suite나ODE/Newton은재실행하지않았다. 독립과학심사/구간인증은NOT_RUN이다.

전체 source/tests/원필요의존성/context/실패와성공로그/정식결과는 DELIVERY_RECEIPT.json의 ZIP에 있다. Git은 요약·입력·계약·반환·source identity를 보존한다. wrapper는 구성명령과syntax를확인했고추가wholewrapper replay는없다. Rust1.94.1 archive SHA는기존pin과일치하나GPGauthenticity는미검증이다.

다음 RCT03D는 기존 coupled::evaluate의 nonphoto material RHS에 RCT를 넣고 별도 RCT sidecar를 함께 누적하는 한 단위다. 원 photo_delta/transaction_path/실패gate를 유지한다. source-free결과는ownerdecision대기이며 원격채택을수행하지않았다. root/TASKS/remote receiver변경0,baselineRCTOFF,actualatomicmomentsnull,HE-F2globalfalse,HE-F3/F09open,physicalHOLD를유지한다.
