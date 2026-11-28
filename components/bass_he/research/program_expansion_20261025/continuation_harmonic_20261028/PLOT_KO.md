# HARMONIC10 S08 — R8/C8 원 저장값 그림과 자원 결과

## 실제 실행과 자료 출처

그림은 S07 local `425b18c2057fe3dadccfdd5cc765ec595a3ac0a2`,
remote same-tree `cd5f3c6e51955978c79214f913b69f9049b5ff65`,
tree `e48d0c1341706107143b0314d7ada030cce40daf`에서 한 번 만들었다.
입력은 이미 저장된 `evidence/SAVED_PLOT_DATA.json`,
SHA256 `2e75d564afb030225ebb2e48cd142c2edcbcee1f45c7530dd800c57e5d10b6ae`다.
이 파일은 최초 검증과 승인된 targeted 검사 두 raw JSON의 값만 기계적으로 결합한다.
원 실패와 원 empty-fixture 행도 provenance에 남는다.

Whole-process CPU **2.806525/10s**, wall **2.835772674/30s**, peak RSS **74096KiB**.
Outer orchestration CPU0.005892607s는 별도 기록했다.
Font cache는 실제 cold이며 warmup0, render1, rerender0,
scientific imports0/calls0, tests0다.
PNG와 SVG는 같은 한 rendering에서 나왔고 원본을 그대로 보존했다.

## 원 그림의 네 패널

**A — 방향 의존성.** 고정된 manufactured law에서 검출기 orientation을 변화시킨
저장17개 지점이다. 선은 이 지점들의 독립 closed-form 값들을 연결하고,
점·error bar는 certified event enclosure다.
작은 폭은 그림 해상도에서 보이지 않을 수 있으므로 exact bounds는 JSON을 사용한다.
연결선의 모양 자체를 추가 continuum 수치 인증으로 세지 않는다.

**B — 비분리 polar–azimuth 사례.** 결합 측도를 직접 적분한
\(Y\simeq0.0406887195198952\)와 독립식을 비교한다.
Global marginal modulation을 곱한 naive 진단값은 약0.03268204043794395다.
차이 \((k-k^3)/(12\pi)\), \(k=40/51\)는 양수이므로
이 허용 사례에서 단순 분리화가 틀림을 보여 준다.
이 수치는 실제 experiment yield나 calibrated event rate가 아니다.

**C — 저장 mass의 세 incident energy.** 213,258,330MeV에서
동일한 선언형 angular law와 detector를 사용한 저장 결과다.
왼쪽 축은 coincidence measure \(Y\), 오른쪽 축은
\(\int_C(E_++E_-)\,dm=G Y\)인 selected pair energy moment다.
이 energy moment는 rest energy를 포함한다.
축이 다르므로 두 곡선의 시각적 중첩을 물리량의 동일성으로 읽지 않는다.
조건부 한 사건의 총에너지 \(G\), population energy, heating은 서로 다르다.

**D — actual width와 경계 분해.** 수정된 positive fixture의
기본 delta actual width는 \(5.5063741233403325\,10^{-15}\),
polar+arithmetic bound는 \(9.473903143468246\,10^{-15}\)다.
Manual delta1/16은 actual0.02421728950198976,
bound 약0.041666666666666664다. 기본 epsilon 보장을 수동 예에 소급하지 않는다.
Degree8/N8 coincidence는 이 geometry에서 exact0이며,
그 사례의16root×49=784 bisections는 실제 boundary 연산을 검증한 것이다.
비영 worst-case event 폭을 검증한 예라고 확대하지 않는다.
Symlog 축은0을 함께 표시하며 저장된 모든 폭은 비음수다.

## 전체 그림 캡션과 시각 관찰

**Rest energy is included. Manufactured law; exact stored masses; measurement
uncertainty is outside this declared calculation.**

Parent와 독립 reviewer는 원 PNG를 직접 읽었다. 네 패널의 데이터·축·범례는 읽을 수 있다.
원 PNG 하단 footer 일부가 경계에서 잘리는 cosmetic observation이 있어,
위 문장과 이 문서에 scope 전체를 보존한다. 수치·자원 판정의 blocker는 아니며
이미 완료한 그림을 재렌더링하거나 예산을 추가하지 않는다.

원 PNG SHA256:
`5286cbc29d1fcf8f52b36243068a61a9f1c739bb4438d225bb9af0a95c0a27a2`.

원 SVG SHA256:
`f5058dbc0fb9c5f7571e930afbfb11406ae4ef55b058b0c7ff22a6beb8f6d371`.

본 단계는 저장 결과 해석과 plot resource 완료다.
독립 최종 scoped 판정은 S09에 결속한다. **현재9/14 · 중앙28/88**.
