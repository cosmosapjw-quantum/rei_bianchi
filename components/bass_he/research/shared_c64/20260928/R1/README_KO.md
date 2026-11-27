# SHARED_C64_R1 연구 게시본

이 디렉터리는 2026-09-28의 공통 R-contour·공유 c64-g3 연구를 보존한다. Production solver 교체가 아니며 src/, 기존 tests/, cloud runner는 변경하지 않는다.

## 정확한 원본

전체 증명, 14개 complex trace, 56개 reweighted action, 128-panel 비교, 실패 로그, scoped dependency snapshot 및 활성 research/coding harness는 다음 immutable archive에 있다.

- BASS_HE_SHARED_C64_RESEARCH_20260928_v1.zip
- 668774 bytes
- SHA256 b70fbd51736d6e3004c27793cb1c47e50878fc72bad090de83e2a57aa94522a2
- 게시 준비 시 ZIP CRC 및 270개 manifest 항목의 크기/SHA256 확인.

여기에는 직접 읽을 수 있는 방법·결과 요약과 원본 research_kernels.py/test_research_kernels.py를 게시한다. 대형 raw trace와 과거 dependency/harness 전체는 위 archive가 소유하며 별도 이중백업 receipt가 provider object identity를 제공한다. 원본 REPORT_KO.md와 RUN_RETURN.json의 당시 미게시·미백업 상태는 역사적 기록으로 수정하지 않는다.

## 조건부 수학적 결과

Static two-centre spectrum G(R)=E_j(R)-E_i(R), straight-line X=vt=sqrt(R^2-rho^2)를 사용한다. dX=R/sqrt(R^2-rho^2)dR이므로

A(rho)=integral_Gamma G(R)(1-rho^2/R^2)^(-1/2)dR, Delta=abs(Im A).

rho_max<Re Rc이고 같은 두 sheets 위에서 원래 경로와 Gamma 사이에 다른 spectral/geometric singularity 없는 homotopy가 존재하며 실수축 bridge의 integrand가 실수라면 imaginary action은 보존된다. 단순 fold의 gap은 sqrt(R-Rc)이고 R(s)=Re Rc+i Im Rc(2s-s^2)에서는 integrand가 O((1-s)^2)다. 이는 조건부 유도이지 전역 homotopy 인증이 아니다.

공통 trace를 32/64 panels에서 독립 계산하고 rho별 kernel을 다시 가중한다. 64 trace의 subsampling을 독립 32 trace라고 하지 않는다. 서로 다른 rho 출력은 spectral 오차를 공유한다.

K=sum c_n(rho/R)^(2n), c_n=binomial(2n,n)/4^n. q=(rho_max/min_Gamma|R|)^2<1일 때 M차 뒤 tail은 c_(M+1) q^(M+1)/(1-q) 이하이다. 적분 tail에는 integral |G| |dR|를 곱한다. 현재 코드는 동일 이산 trace의 polynomial truncation만 bound하며 CF/quadrature/roundoff/homotopy 오차는 별도다.

Column-stochastic event들의 telescoping으로 observable error<=sum_event abs(delta p_event)를 얻는다. 왕복 crossing은 두 번 센다. Coherent amplitude 문제에 이 bound를 자동 적용하지 않는다.

Rotation은 finite R_cut에서 l, epsilon*rho^3/(hbar*v), R_cut/rho 및 basis convention에 의존하므로 하나의 무차원 매개변수만으로 보편화하지 않는다.

## 원본 실행 증거의 범위

- 8개 research test: 기록된 RED 뒤 GREEN 8/8. 이번 게시 작업에서 미변경 과학 테스트를 재실행하지 않음.
- 7 branches, 14 independent traces, 56 weighted actions, 28 panel pairs.
- 최대 동일-panel 원래 값과 상대차 3.831444849318289e-5.
- 새 32/64 최대 상대차 3.768142283141257e-5.
- 최대 complex residual 1.9997643305817628e-11; 최소 normalized sheet gap .020370734851517677.
- 가장 큰 차이의 2개 branch를 128 panels에서 비교: 상대차 2.72028e-8 및 5.54003e-8.
- 대표 Q3p_sigma/4d_sigma 단일 동일-sandbox 비교: 원래8action19.5322s, 공통2trace+8reweight5.08748s, 3.83926배. 1회이며 c64-g3 성능 또는 전체 solver 배수가 아니다.
- original numerical kernel 27개 불변; production integration/independent review/live three-session measurement 미실행.

## 운영 정책

사용자는 후속 요청에서 bass_cr, BASS_HE, WU088_HH가 모두 유휴라고 알렸다. 이는 사용자 보고이며 live process census가 아니다. 이전 16/16/16은 세 single-thread CPU형 job에 대한 시작 제안이지 실측 공동 최적값이 아니다. 공통 CPU/memory 예산을 한 번만 계상하고 조정자는 한 명이다. 작업중인 디렉터리 삭제, reset/clean, process kill 또는 강제 cgroup 이동을 하지 않는다.

Source execution checkout과 moving evidence publication checkout을 분리한다. 기존 PR16 CODE-I02 original-method fresh replay/review 의무를 이 연구로 대체하지 않는다.

## Claim ceiling

COMMON_CONTOUR=RESEARCH_CANDIDATE; scientific_PROMOTE=HOLD; Eq55=NOT_RUN; continuum_ionization=NOT_ADMITTED. 다른 물리 모형의 행렬/채널/에너지를 이 프로젝트에 직접 이식하지 않는다.

Primary provenance: Gusev/Solov'ev/Vinitsky CPC286(2023)108662 DOI10.1016/j.cpc.2023.108662, 제공 원문 p11/p13; Linux cgroup-v2/PSI 공식 문서; Ghodsi et al. NSDI2011 Dominant Resource Fairness. 특정 contour 및 tail 증명은 본 연구의 조건부 유도다.
