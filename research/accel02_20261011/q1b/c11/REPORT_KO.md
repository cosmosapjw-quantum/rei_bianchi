C11R4에서는 C10R4의 source-entry 정밀도와 시간 제어 문제를 새 C11 구현으로 국소 해결했다. 독립 판정은 `PROMOTE_LOCAL_PRODUCTION_PREREQUISITES`다. 이는 전구간 실행을 위한 수치적 전제의 승격이며, 전체 reionization history의 과학적 허용 또는 production 실행기 완성을 뜻하지 않는다. 전구간 판정은 `HOLD_NOT_EVALUATED`다.

| 항목 | 실제 결과 | 판정 범위 |
|---|---|---|
| FLRW source 정밀도 | 새 두 구간 order-pair 최대 1.3540e-15, born-cell MP80 비교 최대 1.4866e-15 | 동일 HM12/FLRW 식과 binary64 입력, r=0만 |
| 얇은 native cell conditioning | 최초 실패 cell bound 7.2117e-12를 기존 1e-7 budget에서 차감 | 같은 smooth branch의 strict-interior, 명시적 50000 eV cap provenance |
| PILOT02 | 3 accepted macro, 6 half boundaries, 마지막 t=4.539815858150909e9 s | 선언된 macro 예산 종료; 요청한 1e10 s endpoint도 아직 미도달 |
| 보존량 | accepted 최대 energy/initialE=4.8945e-16, number/initialnH=1.9961e-19 | 국소 accepted prefix |
| 실제 cold restart | 새 Python/native 프로세스에서 gen1→gen2; 9 state arrays, 전체 R/support prefix 및 cursor/trial 정확히 일치 | 한 macro endpoint continuation; remote restore 검증 아님 |
| 전구간 / Bianchi / 새 BASS receiver | 실행·허용 미완료 | 기존 HOLD 유지 |

source는 `log1p`/`expm1`, 상대 에너지 좌표와 FLRW prefactor의 해석적 상쇄를 사용한다. 물리식·provider endpoint R은 바뀌지 않았다. D=∫(q−a)source는 진단량이며 authoritative state는 여전히 N/U다. floor, seed, clipping, nextafter, provider 대체는 사용하지 않았다.

PILOT01에서는 첫 시간 오차 trial이 거부된 뒤, 다음 midpoint의 기존 일반 conditioning guard가 1.65536e-7로 실패했다. 이 첫 실패와 as-run 코드는 `integration/evidence/PILOT01`에 보존했다. 얇은 support에서 확률좌표의 민감도가 실제 native response 오차를 과대평가하는 경우를 구분하기 위해 pinned native 단면적의 1·2차 미분 bound와 attenuation logsumexp bound를 유도했다. 새 경로는 양의 moment-matched measure에 대한 native value bound를 사용하며 기존 1e-7에서 그 bound를 차감한다. endpoint, threshold crossing, 임의 provider는 이 우회 경로로 허용되지 않는다. 독립 리뷰의 중요한 cap provenance 지적은 explicit caller cap 인자와 rejection test로 해결했다.

PILOT02는 PILOT01의 실제 rejected cursor를 이어받았다. 완료된 첫 h=5e9 trial은 반복하지 않았다. 새 4개 complete trial 중 1개를 거부하고 3개 macro를 수용했다. 누적 cursor는 attempts=5, accepted_macros=3, rejected_macros=2이며, next_step_s=1708897821.8075385다. 새 계산 비용은 12 maps / 108 gas RHS / 7536 SIGMA calls, 40.2273초였다. 종료 상태 `BUDGET_BOUNDARY`와 driver exit 1은 선언된 예산 종료 의미이며 수치 실패로 재분류하지 않는다.

시간 제어는 full-step과 두 half-step의 고정 수치 scale 결함을 비교해 양의 fine path를 수용한다. local target 2e-7과 고정 scale은 solver 단위다. 최종 과학적 비교의 분모를 대체하지 않는다. 65와 129 출력 집합마다 각 field의 해당 fine-history 최대 절댓값으로 별도 정규화하며, fine 최대가 정확히 0이면 차이도 정확히 0이어야 한다. 시간 9 fields 2e-6, spectral/angular 24 fields 1e-3, energy/initialE 및 number/initialnH 1e-9, geometry 1e-11을 유지한다.

새 cold worker는 PILOT02 gen1에서 gen2까지 한 macro를 별도 프로세스로 실행했다. 실제 native 27 RHS / 1884 SIGMA calls가 필요했다. 물리 상태와 전체 저장 이력 및 controller cursor/trial이 정확히 일치했다. harness source pins 및 명시적인 remaining runtime budget metadata는 다르므로 metadata 전체의 byte identity를 주장하지 않는다. C10의 saved continuation에 대한 cold-process 속성 검사도 따로 완료했으며 기존 trajectory family를 반복하지 않았다.

독립 검토는 저장된 153개 frozen inputs, 41개 PILOT02 dependency closure, 51개 review input hash, 새 cold evidence, trial domains/ledger 및 20개 defect component를 확인했다. source MP 비교 10개도 저장 값으로 재계산했다. 남은 경미한 구현 사항은 `run_precision`의 성공 flag가 MP discrepancy를 보고만 하고 assert하지 않는다는 점이다. 관측 값은 모두 1.49e-15 이하였고 독립 재계산과 일치했다. 이 사항을 숨기거나 검산 반복으로 덮지 않는다.

현재 수용 이력은 약 143.9년이며 목표 z=15.9→4의 elapsed time 4.011926941800233e16 s(약 1.2713 Gyr)와 구분해야 한다. 짧은 pilot 비용으로 전체 run 완료 시각을 추정할 근거는 없다. 3개 신규 trial chunk는 현 비용 기준 약 30초이지만, 45초 cooperative wall limit은 hard wall bound 또는 full-run ETA가 아니다.

다음 anchor는 `Q2_FULL_HISTORY_BINDING`이다. `integration/production_design/`에 실행 가능한 작업 명세를 작성했지만 해당 production 코드와 명령은 아직 존재하지 않는다. 다음 세 작업은 병렬 가능하다.

1. 기존 gen3의 상태·prefix·cursor를 그대로 보존하는 명시적 child identity 전환. 기존 checkpoint의 end=1e10, events=[]를 제자리에서 바꾸지 않는다.
2. 저장된 129 output epochs/65 indices, source-band/cell-birth/z hard events, source 내부 energy-kink 적분 분할을 구분하는 schedule 연결.
3. actual attenuated K0/KE 및 direct heat를 보존하는 24-field cell exporter. 9-field 출력이나 post-step power-law Gamma를 24-field 결과로 재명명하지 않는다.

이후 accepted/rejected cursor를 단조롭게 저장하는 chunk runner로 결합하고 새 연결부만 검증·독립 검토한다. PILOT02 gen3부터 전구간 target으로 이어서 C2/C3 및 동일 grid 시간 refinement를 수행한다. full-prefix checkpoint의 누적 저장량이 O(n²)가 될 수 있어 storage 구현도 검토해야 한다. 전구간 허용 후에만 별도의 Bianchi 구현·비교와 새 BASS receiver를 진행한다. 현재 source는 r≠0를 거부하며 BASS의 기존 reduced RUN002/N4 receipt를 새로운 native history로 이전하지 않는다.

원자물리의 기존 장기 lane과 CR/RCT/secondary cascade는 보존했다. 현재 OFF는 완료 또는 물리 provider 구현을 의미하지 않는다. source/physics/criteria와 C10 checkpoint-bound 파일은 변경하지 않았다. 완료된 RUN002·EVENT003·Q0 및 무변경 C10/C11 검산은 재실행하지 않는다.

재개 시 `HANDOFF.json`, `NEXT_DAG.json`, `RESUME_PROMPT_KO.md`를 사용한다. 독립 판정은 `review/INDEPENDENT_DECISION.json`, 계산 증거는 각 component의 `evidence/`에 있다. 단계별 Git와 Drive/Dropbox 업로드 영수증은 `PUBLICATION_RECEIPTS.json`에 기록한다. 업로드 확인과 원격 복원 시험은 구별하며 후자는 수행하지 않았다.
