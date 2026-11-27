# BASS_HE EXFOR 동일 D 사건 정규화 연구 결과 (2026-10-29)

본 연구는 BASS_HE PR104 `89325f8510d2af3abe675326720068d0693845b8`의 조건부 D 생성원 뒤에 source-locked 330 MeV 각도 적분을 추가한다. 중앙 물리 DAG28/88, 선행 HE14/18, 선행 조건부2/2는 변경하지 않는다. 새 조건부 수학/구현 노드2/2는 실물리 생성률 승인과 무관하다.

## 원자료 검증

IAEA-NDS/exfor_master@939a14d7bba1ddce51975cb5e8711ce96b3b0871 `exforall/M04/M0475.x4`를 원격에서 읽고 Git blob c49433293921dbb012d7f1b0387745732a598efa, SHA256 b2c1c52931e813dd63fb0e98edfc90088bc2eca497fd9142277e748f0935a82f가 로컬 원문과 정확히 일치함을 확인했다. Arends et al., Phys. Lett. B62(1976)411–412, DOI10.1016/0370-2693(76)90671-7.

M0475002의330MeV CM 46/61/73/87도 미분단면적은 각각0.14±0.03/0.16±0.05/0.07±0.05/0.19±0.05 nb/sr다. M0475003의 총단면적은320MeV0.61±0.16nb,359MeV0.55±0.15nb이며330MeV 직접 SIG는 없다. 원문에는 coincidence/TOF, ERR-S statistical이 기록돼 있다. 네 DA 점만으로 실제 full angular law, photon flux/history, exclusive event/particle convention을 정하지 않는다.

## 직접 유도한 결과

실측 각도별 [DA−ERR-S,DA+ERR-S]를 단순 감도구간으로 보고, 선언한 전역 angular Lipschitz L[nb/sr/degree] 아래 비음수 대칭 함수족의 sharp 적분을 구성했다. 가능한 함수가 존재할 필요충분 Lmin=1/700, 중앙값 정확통과 Lmin=3/350이다. 최적 pointwise f_-/f_+는 측정값과 L을 이용한 거리 원뿔 envelope이며 두 함수가 실제로 feasible하므로 sharp하다.

| 조건부 L | I_min [nb] | I_max [nb] |
|---|---:|---:|
| 1/700 | 1.3666090712348561 | 1.8797733398108844 |
| 1/200 | 1.0068860482429433 | 2.4235391725370239 |
| 1/100 | 0.7007525029209273 | 3.0180382306937155 |

여기서 I=full-sphere angular integral이다. 가상의 inclusive-D full-sphere convention은 I=2sigma_event, 가상의 randomly-oriented-one-D convention은 I=sigma_event이다. EXFOR 자료가 어느 쪽인지 이번에 확정하지 못했다. L=1/200에서 전자 convention의 조건부 event sigma는[0.5034430241,1.2117695863]nb이지만 실측 총단면적이라고 부르지 않는다. 수치 endpoint는 고정밀 근사이며 외향반올림 인증 interval은 아니다. exact piecewise geometry/최적성 정리는 별도 성립한다.

## 구현 및 검증

`src/exfor_envelope.py`는 정확 원문 SHA/블롭 검사, Fraction source parser, sharp L, exact affine breakpoint/envelope, mpmath 해석적 삼각 적분, 명시적 가상 multiplicity 및 manufactured-only nHe Phi sigma를 구현했다. `tests/test_exfor_envelope.py` 신규19개 검사는 Python3.13.5에서 exit0,19/19 PASS, test wall0.374s(최종 패치), 전체 process wall 약1.17s/RSS 약100MB였다. 원 source/test Git blob은 로컬과 원격이 동일하다. 독립 pointwise mpmath quad와의 차는1e-45nb 미만이고, Wolfram은 Lmin과 적분 원시함수 항등식을 확인했으며 독립 NIntegrate는 약1e-20nb 수준에서 일치했다. scipy double quad는 약1e-16nb 수준에서 일치했다. 60/90digit 차이는 약1e-48nb다.

C9 self review에서 고정밀 decimal endpoint를 외향반올림 interval로 오해할 위험을 발견해 `numeric_rounding_certified=false`로 고치고 영향 테스트를 재실행했다. 독립 native subagent reviewer는 도구 미노출로 NOT_RUN이므로 C9 독립심사 완료를 주장하지 않는다. 기존 HE science/IVP와 28개 이전 테스트는 재실행하지 않았다.

## 물리 경계 및 다음 노드

EXFOR의 event/inclusive, coincidence efficiency, full/half sphere, azimuth/polarization, target motion 및 systematics/covariance는 아직 source-qualified되지 않았다. 인접 에너지 SIG나 Rice150–250MeV를330MeV normalization으로 차용하지 않는다. R_event=null, actual photon history=null, physical fast-D pool=null, stopping/deposition/Cv=null, activation=false, L4=false, production=HOLD.

다음 물리 노드는 원 논문/공급자의 event/particle 정규화 및 acceptance convention 확인, 330MeV 실제 photon-field/target-frame 적분, 이후 비열적 D pool과 독립 stopping/heat를 연결하는 것이다. 조건부 이론 10/10, 코딩 9/10(C9 독립심사 pending), 새 조건부 과학 노드2/2다. 단계별 GitHub+Drive+Dropbox 로그는 별도 기록을 따른다.
