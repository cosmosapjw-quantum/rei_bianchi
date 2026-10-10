# N2: source birth/remap chronology의 실제 이식과 전 구간 진단

상태는 `IMPLEMENTED_COMPONENT; WHOLE_HISTORY_HOLD`다. 기존 RUN002, HE E13C3,
HH PHYS03를 재실행하지 않았다. 보존량만으로 정확도를 승인하지 않았다.

`rust/rei_microphysics/src/paired_runtime.rs`의 실제 endpoint 경로는 에너지
격자로 반복 hat remap을 시행한 뒤 `dt*SOURCE`를 마지막 시각에 전부 넣고,
새로 태어난 광자까지 전체 dt 동안 backward-Euler 흡수를 받는다. HH PHYS03의
활성 threshold weight 차이는 이 경로의 물리적으로 유효한 경고다. 현재 warm
provider의 고정 q RHS는 이미 반복 remap을 피하지만, 짧은 고온 guard와 명시적
DOP853은 cold broad history의 허용 근거가 아니다. 두 기존 경로의 guard나
기록은 변경하지 않았다.

새 native `characteristic_source` 모듈과 Python `characteristics.py`는
고정 공간 covector에서 실제 에너지를 계산하고 연속 photon source의 체류시간을
적분한다. 각 광자의 나이는 endpoint deposit으로 대체하지 않는다. 고정계수에서
N1=exp(-k dt)N0+S dt phi1(k dt), 흡수는 종별 k_j I다. phi1과 phi2의
작은 광학깊이 급수 및 expm1 계산으로 상쇄를 피한다. Number/energy hat remap을
실행하지 않으므로 threshold는 실제 E(q,mu,t)로 평가한다. 이 식 자체는
`derived`; Rust/Python의 경계·종별 ledger 검증은 `implementation-verified`다.
새 Rust tests 3개와 Python tests 3개가 통과했다. Python 독립 oracle은 60자리
Decimal 지수식이고 optical depth=0..1e6이다. Native 경로는 chemistry를
자동 연결하거나 HE의 고정 affine-path 정리로 전체 history를 승인하지 않는다.

실제 HM12 emissivity/UVB와 기존 exact Bianchi background를 사용해 z15.9→4
전체 구간을 실행했다. 흡수 bath는 xHII=.1,xHeII=.1,xHeIII=0을 고정하고
밀도만 팽창시키는 외부 prescribed bath다. 이는 photon 전달을 검사하는 진단이고
재이온화 해가 아니다. 현재 source band는10..50000eV이며 최종50keV source를
놓치지 않도록 qmax=169000eV(FLRW),178718eV(r=.05)로 확장했다. 최초 q>50keV
점은 비어 있고, current E>50keV에서는 source=0이며 원자 단면적을 외삽하지
않는다. 10eV 아래로 redshift한 기존 광자는 제거하지 않는다.

TRANSPORT001의 6개 실행은 각각2048/4096 step,512/1024 energy 및4/8 angle을
사용했다. 각 실행시간은 약2.6–10초 수준이다(개별 정확한 값은 JSON 참조).
Photon/energy ledger는 최대3.4e-15로 닫히지만 선언한 관측량 기준은 실패했다.
FLRW에서 temporal Gamma 차이는7.18e-4(목표2e-6), spectral/angular Gamma
차이는2.27e-2(목표1e-3)였다. Bianchi에서도 각각6.57e-4,1.52e-2다.
엄격한 ledger와 물리 관측량 정확도가 다르다는 사실을 실제 broad source에서
확인했다. 실패를 허용 기준 완화로 처리하지 않았다.

첫 번째 원인은 stiff order reduction이다. k dt≫1에서 frozen-midpoint 식은
S(t_mid)/k(t_mid)로 수렴하지만 필요한 endpoint는 S(t1)/k(t1)다. 선도 상대
오차는 -(dt/2)d ln(S/k)/dt로 일차다. 고정계수 지수식이 정확하다는 사실은
시간 의존 provider에 대해 uniform second-order를 뜻하지 않는다. 두 번째는
고정 q quadrature에서 움직이는 H/He threshold와 spectrum jump의 해상도다.
반복 remap은 제거됐어도 continuum spectral accuracy는 자동 확보되지 않는다.

이에 같은 물리 입력의 continuous BDF+analytic sparse Jacobian을 별도로
실행했다(TRANSPORT_BDF001). r=0,.05,128 energy,1/4 angles,
rtol=1e-6/1e-8의 네 실행은 각각 약5.2,13.3,7.3,20.9초였다.
이는 큰 explicit absorption-step 제약을 피하지만 선언한2e-6 wholehistory
시간 기준은 아직 실패했다. 작은 음의 값도 숨기지 않았다. 별도 mesh 진단에서
q=139736.8eV,current E=54002.93eV,t=2.4378e16s인 **source=opacity=N_initial=0**
비활성 점에 accepted solver mesh상의-1.8552e-23 scaled 값이 생겼다.
단순 dense-output 보간의 문제만은 아니다. 이 점은 해석적으로 정확한0이므로
다음 구현은 dormant coordinates를 동역학 변수에서 제외하고50keV 진입 event에서
정확한 영 초기값으로 추가하는 방식이 적절하다. 일반 음의 해를 clipping하는
방식과 구분해야 한다. 현재 결과에는 clipping을 적용하지 않았다.

이 진단 뒤 `events.py`를 추가했다. 실제 Bianchi geometry로 source50keV 진입,
Verner13.60/24.59/54.42eV, lower source10eV 및 HM12 native spectral jump의
crossing을 root solve하고, 각 open time segment의 active index를 반환한다.
Root coupled driver의 source-entry restart와 dormant-coordinate 제거에 이
API를 전달했다. 순수 FLRW a_rel=exp(t)의 해석적 event 시간과 active support
순서에 대한 새 targeted test1개가 통과했다. Event API 구현·전달 자체를
실제 event-segmented coupled trajectory의 성공으로 표기하지 않는다.

Root integration이 N1의 실제 CaseA H/He/열·source provider를 연결해
coupled broad history를 수행한다. 여기서 만든 고정-q API는 즉시 사용할 수 있지만
N2의 최종 DONE은 그 coupled history의 xHII/xHeII/xHeIII/T/tau 시간·스펙트럼
오차와 positivity가 기존 budget을 만족할 때만 가능하다. 현재 단계의 출력은
유용한 native component와 실패 원인이 좁혀진 전 구간 실행 증거다.

실패 분류: TEST_RED는 구현 전 missing module, TEST_ENVIRONMENT_FAILURE는
mpmath 부재(독립 oracle을 표준 Decimal로 교체), RUST_FIRST_COMPILE_FAILURE는
test float literal 문법 오류(수정 후 통과), TRANSPORT001 말미 JSON 실패는
numpy.bool 직렬화 오류(계산은 재실행하지 않고 저장된6case를 요약), refinement와
BDF positivity는 수치해석 실패다. 물리 입력 부재와 혼동하지 않았다.
