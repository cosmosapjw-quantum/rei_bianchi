# source005 FLRW 전구간 후처리 결과

두 기존 계산은 원래 epoch/deadline을 유지한 채 z20→4를 완주했다. Q512/Q1024 종료 코드 0과 원본 source/config/binary binding이 확인됐다. 새 물리 계산은 실행하지 않았다.

이미 완료된 CLI 수리(3 focused tests)와 ZIP 복구(8 tests)를 재사용했다. 최초 CLI 실패와 후속 NCP numpy 미설치 실패는 보존했다. 로컬 설치 환경으로 기존 입력을 한 번 처리하여 그림과 진단을 완성했다.

| 항목 | Q512 | Q1024 |
|---|---:|---:|
| 저장 accepted-state 행 | 442147 | 262661 |
| 전체 ledger 행 | 13706557 | 8142491 |
| PASS ledger 행 | 1326441 | 787983 |
| 종료 zbar | 4 | 4 |
| 종료 Tgas [K] | 7660.490580439394 | 7660.567381227177 |

모든 PASS 행은 자체 기록된 tolerance로 검사됐고 FAIL 행은 없었다. 후처리 wall 87.98996 s, CPU 78.86205 s, peak RSS 222785536 bytes; 누적 공유 후처리 사용량 91.14746/300 s. solver/watcher 재시작과 deadline 초기화는 0회다.

## 독립 판정

`PASS_SCOPED_CONDITIONAL_FULL005_POSTPROCESS_PUBLICATION`. 다섯 PNG와 binding/작은 checkpoint/끝점 photon moments를 독립 확인했다. 원소 내 H/He ionic fraction 대 z20 이후 경과 proper time 및 실제 gas temperature이며, 온도 축은 시간 순서를 유지한다. per-baryon BBN 표시 단위는 별도 presentation 산출물로 연결한다.

## 해석 경계

공통 n_mu=8, local_target=1e-5에서 energy grid 두 개를 비교했다. 1001개 ln(a) 표본에서 xe 차이 1.06410e-5, HeII fraction 차이 1.30944e-4, Tgas 차이 0.249191 K다. 연속 supremum, true-IVP 오차 상한, 시간·각도 전구간 수렴이나 source/model 정확도 판정이 아니다. 기존 UNKNOWN/tail/null/HOLD를 유지한다. D cosmological activation, signed Bianchi, isotope-native 완주와 64-core adequacy는 미완료다.

외부 수정의 적용 범위와 정확한 supplier commit은 `../../external_update_intake_20261016_001/INTEGRATION_DECISIONS.json`에 기록했다. 현재 Rust driver의 total-proper-density 및 outer energy veto는 HE23 adapter의 과거 실패 경로와 다르며, 실제 source005 자체 ledger가 통과했다.

## BBN 형식 abundance 표시

추가 4개 로그 그림은 실제 CSV의 Ybaryon=ni/nb이며 nb=nH+4nHe, electron은 별도 Ye panel이다. 정확한 0은 원시 CSV에 보존하고 mask하며 floor를 만들지 않는다. 시간·온도 좌표 모두 경과 proper time의 순서를 유지한다. 독립 구현 검토 PASS_SCOPED_YI_PRESENTATION_AND_DELIVERY를 받았다. 재계산한 raw SHA라고 주장하지 않고 직전 strict 검증을 재사용하며 electron extrema 보존은 미보장이다.
