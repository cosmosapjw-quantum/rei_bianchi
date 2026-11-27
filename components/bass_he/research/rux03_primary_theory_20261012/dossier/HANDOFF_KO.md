# BASS_HE 이론 인계 — 다음은 PRIMARY_PROVIDER_03

## 확보한 결과

`HERE_RUX03_PRIMARY_THEORY_03`은 기존 implicit primary와 Case A event provider의
연결을 위한 수학적 선행 단위다. 현재 코드의 광자 소거·양성 H/He proposal·네 변수
interval/root를 재사용하고 다음 구성을 얻었다.

1. nonnegative source를 포함한 reference/proper/per-H 광자 소거와 정확한 Schur 미분.
2. finite photon supply를 배분하는 absorption Jacobian, 역함수와 응답 모드.
3. root 밖에서도 성립하는 `F_E=F_w+b_chi·F_v`와 일정 잔차/야코비안 행 변환.
4. 영밀도 경계에서 정의되는 coefficient-level provider, moment를 포함한 C² 미분.
5. endpoint-energy BE history의 정확한 photon geometry work와 product-rule 보정.
6. 단일 HeIII RR 사건의 constant witness와 T² companion의 실제 미분 기대값.
7. native w residual을 T 좌표로 바꿀 때 유지할 유한 단계 식.

정리의 근거는 두 전체 유도, 세 Wolfram exact 계산의 47개 검산 group, source 지도와
독립 검토다. 최종 채택은 `../review/DECISION.json`을 따른다.

## 정확한 출발점

- 수신 코드: rei_bianchi PR114 `a5c958c414dea41216b445c05f58df837f05cacb`.
- 그 부모 PR97: `1400093cdd121d8e6adb51ffeb360102a48653bf`.
- 이론 게시의 base: BASS_HE PR30 `6b337be443d0fbe8f07d99e7b3ff1cc210294bcb`.
- PR83은 별도의 owner/planning branch다.
- source identity: `../source_map/CURRENT_SOURCE.json`; 실제 callsite: `SOURCE_MAP.md`.

## 다음 최소 구현

작업 ID는 직전부터 이어진 `HERE_RUX03_PRIMARY_PROVIDER_03`을 사용한다.

`CODING_CONTRACT_KO.md`를 읽고 공통 coefficient/event 표현을
`raw/endpoint`, ordinary point, conservative point, `interval_rhs/root` 및 paired
caller에 연결한다. 같은 source에 맞춘 계수 선택과 moment 미분을 사용한다.

현재 paired caller는 birth를 primary 입력에 이미 더한다. 해당 경로는 그 입력과
source=0인 primary로 유지할 수 있다. 직접 source adapter를 만들면 birth 전 입력과
stage source를 사용한다. `Phi(p+hs,0)=Phi(p,s)`에 따라 한 번만 합산한다.

실제 single-channel witness는 상수 증분과 T² 증분을 각각 사용한다. 전자는 한 번
소비와 population/전자수 의존성을, 후자는 kinetic coefficient의 T 미분을 판별한다.
수용할 새 interval 결과는 실제 공통 provider field에서 계산한다.

구현과 그 변경 의존성의 최소 검증이 닫히면 RUX02 physical input과 RUX03 domain을
맞춰 RUX04 scenario lock으로 진행한다. 원 의존성은

`RUX02 + RUX03 → RUX04 → RUX05`

다. 현 요청은 이론 루프이므로 실제 Rust wiring은 위 후속 코딩 단위의 행동으로
명시했다.

## 재사용과 재개 파일

직전 conditional 사건 경로의 source·실행 근거를 재사용한다. 변경 없는 native
176-test 결과나 이전 history 캠페인의 재실행을 기본 작업으로 삼지 않는다.
새 실행이 필요한 변경에는 그 source/build/input identity를 연결한다.

재개 시 다음을 읽으면 된다.

- `REPORT_KO.md`, `CLAIMS.json`, `RESULTS_SUMMARY.json`.
- `CODING_CONTRACT_KO.md`, `NEXT_DAG.json`.
- `../review/DECISION.json`, `../review/REVIEW_KO.md`.
- `../source_map/CURRENT_SOURCE.json`과 `SOURCE_MAP.md`.
- 필요한 식의 전체 유도와 exact `.wl` 입력·raw 출력.

초기 검산 도구의 SymPy 의존성 오류와 검토의 witness 범위 지적은 원래 관측과
해결을 각각 보존했다. 다음 작업은 그 해결된 문제를 반복 점검하기보다 위 실제
provider 연결을 진행한다.
