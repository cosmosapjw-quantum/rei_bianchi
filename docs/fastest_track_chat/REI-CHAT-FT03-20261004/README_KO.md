# REI-CHAT-FT03-20261004: 재결합 kinetic moment와 열·사건 closure

판정: SCOPED_CONTROLLED_MODEL_CLOSED__PHYSICAL_ACCURACY_AND_PRODUCTION_OPEN.
이론/경량 수치 연구이며 원 Grackle, 원 synthetic fixture, canonical REI-F00~F09, production code는 변경하지 않았다. 다음 ready node는 REI-CHAT-FT05_BIANCHI_I_TRANSPORT다. FT04의 실제 잔차식/source-site parent 연결은 대기한다.

## 전체 재현 패키지

- REI_CHAT_FT03_20261004.zip, 78707 bytes, 48 entries.
- 로컬 봉인 SHA-256: 0d8d28b5e4d63a9013b5c57f785680d2f3344b94127f2510b4037417356f5480
- Drive: https://drive.google.com/file/d/1NONTS4Y8KXWJ6RPCiCwAiJllJMBTSTC7/view?usp=drivesdk
- Dropbox: /BASS_DERIVATION_DOSSIERS_20260912/ATOMIC_REIONIZATION_HANDOFF_20261004_v1/REI_CHAT_FT03_20261004.zip
- ZIP root: rei_chat_ft03_20261004/. REPORT_KO.md, MODEL_POLICY.json, SOURCE_TO_MODEL_MAP.json, SOURCE_TRACE.json, 7 research scripts, inherited inputs, detailed results, failure logs, manifest/checksums가 들어 있다.
- 양쪽 저장 완료 및 ID/path/size 확인. R1 metadata verification이며 원격 checksum/전체 restore는 하지 않았다. 로컬 CRC 및 ZIP 내부 모든 manifest 파일의 hash/size는 검사했다.

## 1. 새 일반 항등식

비상대론적 Maxwell 상대속도 분포, 온도에 직접 의존하지 않는 capture 단면적, 고정 초기/최종상태 집합, 미분-적분 교환 가능성을 가정한다. alpha(T)=sqrt(8/(pi*mu))*(kB*T)^(-3/2)*integral E*sigma(E)*exp[-E/(kBT)]dE에서

Lambda_kin(T)=kB*T*[1.5*alpha(T)+T*alpha'(T)]

를 얻는다. g=dln(alpha)/dln(T), q=1.5+g이면 capture당 kinetic loss는 kB*T*q이며 분산/(kBT)^2=q+dg/dlnT다. q>=0, q+g'>=0은 필요조건이지 비음성 역 Laplace kernel 존재의 충분조건은 아니다. 공명 DR에서는 q>1.5도 가능하므로 원 q=3.573 하나만으로 모든 재결합을 반박하지 않는다.

alpha_fit=alpha_true*(1+delta)일 때 q_fit-q_true=dln(1+delta)/dlnT다. 따라서 문헌 rate의 경험적 오차가 differentiated cooling의 동일 오차 보증으로 옮겨가지 않는다. 새 cooling은 선택한 fit과 일관된 MODEL DEFINITION이지 atomic physical accuracy certificate가 아니다.

## 2. HeIII 소스 불일치의 위치

Grackle 3.4.1 pin af7939494ce65007887ada7b98d1813df6843346의 initialize_rates.c와 cooling/electron-event consumer를 추적했다. k6와 reHeIII에 별도 종별 factor 보정은 없다. cooling의 HeIII*de/4와 electron-capture의 HeIII*de/4는 같은 mass-to-number 변환이므로 사건당 비율 reHeIII/k6에 /4를 추가할 수 없다.

Hui-Gnedin arXiv v1 Appendix A printed28의 원 cooling도 8*A*T이며 Grackle만의 C 전사 오타로 판정하지 않는다. 같은 Case의 hydrogenic scaling alpha_Z(T)=Z*alpha_H(T/Z^2)와 moment 항등식은 Lambda_Z(T)=Z^3*Lambda_H(T/Z^2)를 준다. Lambda_H(t)=A*t*F이면 실제 T에서 Z*A*T*F이며 Z^3*A*T*F가 아니다. Z=2에서 whole-function factor8은 옳지만 actual-T prefactor는2다. literal8*T와 약4배 차이가 난다. lambda를 맞춘 정확 비교는1263030/315614=4.001818677244989...이며 threshold rounding만으로 설명되지 않는다. 원 source/정오표/저자의 의도를 전수판정한 것은 아니다.

10000K CaseA: 원 Grackle pair q=3.573089082962036; HG rate moment q=0.837132160055933; raw cooling/HG moment cooling=3.910080396542976. 원 k6와 HG rate가 다르므로 이 비율들을 섞지 않는다. 원 source는 보존했다.

## 3. 선택한 controlled model

REI_FT03_HG_RATE_MOMENT_CASE_A_CONTROLLED_V1:
정지·균질 gas rest frame, H/He5종, primary photon3군, source0. HG CaseA RR3의 kinetic cooling을 위 미분식으로 정의하고 CI3는 동일 binding chi를 thermal에서 한 번만 제거한다. PI는 inherited Verner3와 fit-threshold/binding-threshold 구분을 유지한다. HeII DR은 pinned Grackle k4 고온 식을 두 양의 공명으로 분리한다.

alpha_D=A*T^-1.5*[exp(-B1/T)+0.3*exp(-(B1+B2)/T)]
A=1.54e-9*11605^1.5; B1=40.49664394833662*11605 K; B2=8.099328789667*11605 K.
각 항 alpha1/alpha2에 대해 Lambda_D=kB*[B1*alpha1+(B1+B2)*alpha2]. raw reHeII2를 추가하지 않는다.

네 energy reservoir는 primary/binding/thermal/escape다. PI의 변화(-Eg,+chi,Eg-chi,0), CI(0,+chi,-chi,0), RR/DR(0,-chi,-eps,chi+eps)의 합은 각각0이다. 재결합 cascade는 즉시 ground로 가며 에너지 전부 escape에 쓴다. Capture event count는 emitted-photon multiplicity가 아니다. CaseB/cross-species reprocessing은 본 모델에 없다.

ceHI/ceHeII/ceHeI/ciHeIS/brem/Compton/HH/CX/분자/금속/secondary는 명시적 controlled truncation으로0이다. 실제 IGM에서 작다는 판정이 아니며 source admission의 우회도 아니다.

## 4. 연속 ODE의 finite-domain 비교와 수치 기준해

nH=1e-4 cm^-3, He/H=.083; initial fractions(.9,.3,.6), T0=50000 K; photons/H=(.05,.005,.001), energies=(20,35,70)eV; t_end=1e14s; guard[30000,110000]K.
RR 단조감소, DR 단조증가, population/광자 양성, event 보존식, escape상계로 first-exit를 배제했다. 50자리 interval로 계수 ceiling을 확인한 뒤 비교부등식은 exact rational 계산이다. escape<=0.25910790700517206eV/H이고
34368.348358887764 <= T(t) <= 106192.75165363487 K.
이는 선언한 연속 모형의 비교증명이며 numerical flow/root/remainder enclosure나 physical uncertainty bound가 아니다. 제외된 cooling/팽창을 추가하면 재사용할 수 없다.

DOP853 endpoint: xHII=.9996103763929391, xHeII=.34353587128805174, xHeIII=.6036005180228474, T=46683.88048061334K. DOP853-Radau 최대 fraction/logT 차이1.3300471835008492e-13. DOP energy ledger 최대잔차1.4210854715202004e-14eV/H.

다른5종 population+lnT state와 독립 RHS, mpmath.diff cooling으로 50자리 RK4(128/256/512/1024)를 수행했다. 격자차이비18.1434350589554,17.500507296256; Richardson-DOP 차이8.573499611254617e-12. 50자리는 working precision이지 해의 정확도 보증이 아니다.

온도 의존 rate를 고정한 control의 T_end=46629.30856232851K, xHeII=.34703975802233267로, 본 실험은 FT01의 상수율 triangular toy와 달리 실질적인 thermal feedback을 포함한다. HeIII raw cooling만 치환한 ablation은46670.01395177317K. 이 control들은 별도 domain-certified되지 않았고 전체 Grackle/IGM sensitivity 결과가 아니다.

## 검증·실패 기록

Maxwell positive-kernel15적분; source-pair30점; actual RHS energy80점; symbolic energy4종 및 nuclear/charge left-null; invalid temperature6조건; API2시험. 4단계 재현 runner 모두 exit0. 초기 HeIII ceiling1e-12는 실패하여 상계1.2e-12로 수정했고 실패 로그를 보존했다. 기준/guard를 완화하거나 FAIL을 삭제하지 않았다. 제한적 API red-green도 보존했다.

heavy solver, full Grackle build, Rust production, actual Bianchi history는0. physical_provider_admitted=false; first_physical_interval_certified=false. strict local<2e-4/public width<2e-3, 과거[160,161]FAIL=2.1245050576368385e-4 및 tick160 보존.

원전: Hui-Gnedin https://arxiv.org/pdf/astro-ph/9612232 Appendix A; Nahar2021 DOI10.3390/atoms9040073 Eq48; pinned Grackle source locations and byte/read status in SOURCE_TRACE.json. 논문 전체 PDF를 이 패키지에 재배포하지 않았다.
