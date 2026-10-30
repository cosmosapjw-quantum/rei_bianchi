# REI F4: 2026-10-31 저에너지 전자 에너지 분배의 원전 기반 물리 계산

주요 결과: Ferrett 측정구간 원래 BASS193 source를 PR287의 원래 연속 redshift first-flight 연산자로 재구성했다. 총 193 epoch 중 source 99.4806418%를 차지하는 30개 epoch를 선택하여 3,554 emission–arrival kernel 물리행을 새로 생산했으며, 192개 arrival 구간의 5개 energy-band × 4 absorber 종별 이벤트와 운동에너지 표를 만들었다. 나머지 source는 원래 PR297의 총 광자/전자 에너지 장부로 상하한을 설정했다.

## 새 수치 결과 (조건부, PR287 16-point/4-substep 분해능)

- 선택 30 epoch의 입사 일차 전자 운동에너지: `6.715789387452955e-11 eV/baryon`.
- PR297 전 epoch의 원래 운동에너지: `6.749242464433259e-11 eV/baryon`.
- 선택 epoch의 `E_e < 10.2eV` 전자 운동에너지: `8.540689041108780e-12 eV/baryon`.
- 전 epoch의 `E_e <10.2eV` 모델-배정 열 에너지 범위: **`[8.540689041108780e-12, 8.875219810911833e-12] eV/baryon`**, 전체 kinetic 대비 **`[0.1265429281303,0.131499495798]`**.
- 선택 epoch의 1차 전자 사건 수: `E<10.2`: `1.67825017137717e-12`; `10.2≤E<13.598`: `4.650270805272214e-13`; `E≥13.598`: `2.2095660261253222e-12` per baryon.
- 원래 relaxation bound secondary H ionization `4.963249567403269e-12/baryon`; 독립 전자별 문턱으로 강화한 전체 source **보수적 상한 `2.953300056205549e-12/baryon`** (기존 대비 약 40.50% 축소), 희귀 LiI 네 번째 H 이온화 항과 미계산 0.5194%를 포함.
- H/He 흡수에서 생성된 1차 전자의 He II secondary collision-ionization 가능 사건 수는 kinematics상 0. 그러나 Li I 흡수의 매우 희귀한 가능 사건은 선택 epoch에서 `6.967915325328239e-26/baryon`이며, 이 경로를 0으로 놓지 않는다.
- 원본 PR287 최초 흡수 kernel과 재구성된 종별 event-count 및 일차 전자 kinetic 합계 상대차: `≤1.2e-15` (source-scoped numerical identity).

출처의 물리적 의미: `f_heat=1`은 Furlanetto–Stoever 모델의 `E<10.2eV` 종료 규칙에 따른 **deposition classification**, 실제 IGM 온도 진화가 아니다. 실험적으로 규명되지 않은 LiII 1S source 양의 하한, BASS native K vs Ferrett denominator, 시간 의존 전자손실, 전체 Furlanetto–Stoever 표, REI17 네트워크, anisotropic K 및 CMB는 미해결이다.

실행은 원본 source PR297 ZIP 및 사용자가 제공한 Ferrett/Langer/FS2010 세 PDF SHA-256을 고정한 격리 워크스페이스에서 이루어졌다. 본 연구에서 완료된 것은 하나의 scope-limited physical auxiliary node이지 canonical DAG 노드가 아니다.

최종 상태 `WORKING=33/88`, `CENTRAL=28/88`, `F4_FAST=4/7`, `CANONICAL_DELTA=0`, `AUXILIARY=1/1_SCOPED`, `NO_NEW_IVP`, `PRODUCTION=HOLD`, `NO_MERGE`, `NO_FORCE_PUSH`, `AUTO_NEXT_NODE=false`.
