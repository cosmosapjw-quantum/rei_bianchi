# 다음 pilot 노드의 현재 source·담당·예산 확인

관측 종료: 2026-10-25T13:04:01.107Z. 이번 조사는 기존 51개 저장소·2,272개 ref 전수조사(2026-10-25T10:35:51.970Z)를 보존한 뒤, 실제 다음 노드에 관련된 변경분과 현재 ref를 새로 읽은 비원자적 delta다. 모든 브랜치 내용을 다시 읽었다거나 접근할 수 없는 대화를 전수 조사했다고 주장하지 않는다.

## 현재 권위

| 대상 | 실제 확인 | 이번 의미 |
|---|---|---|
| REI owner PR221 | `8d10231b1f0f788164d5eadbe1bcee0b802cceca`, open draft | 이전과 같음. ANGTHERM02 담당 예약 보존, 읽기만 |
| REI central PR222 | `78f7ac5864d5817ceb79b48cb5e298cc30006510`, open draft | 기존 c5050305…보다 3 commits 진행 |
| Central tree | `e3397a0cd7cc7f9732a71d9273aee8b07926fc7d` | 이번 게시 후보의 고정 base |
| Root AGENTS | blob `429a5a13ee75b1222bc50627f8d5973d01dd21c4`, 9351 bytes | 이전과 같음. Astra 권위/독립 검토, lower-tier 구현·실행 분리 |
| REI task assignment | blob `bdc56f36312356a19a7ea0d5b998b6719baa4f44` | 정확한 원본을 SOURCE 파일로 저장 |
| Canonical DAG | blob `b6ecc8cd9285e772e8649afe0155fc22a2256f37`, 87 nodes | 전역 완료율 null, L4_ready=false |
| WU compiler owner | `34dd7d1d018abff8a0a4ebd1d3f3579ac46d2fad` | REI-CHEM-LEDGER-01은 WU 소유, REI는 소비자 |

WU, REC, HE, CR, bass, VigilODE의 확장 브랜치 ref를 새로 읽었으며 중앙 인계의 각 최종 commit과 모두 일치했다. 상세 SHA는 SOURCE_AUTHORITY.json에 있다. 중앙 Git compare의 파일 목록은 300개에서 끝났으므로 전체 변경 파일 완전성 근거로 쓰지 않았다. 필요한 실제 handoff/AGENTS/task assignment/DAG/소유 경로는 별도로 회수했다.

## 이번 실제 실행 노드의 범위

원 pilot 전체 DAG의 현재 위치는 **N3 source response → N4 선택된 collision residual/Jacobian 검산**이다. 전체 N6 실행은 HOLD다. 최신 중앙 DAG에는 **REI-EXP-SCENARIO → REI-EXP-OPACITY-CONSUMER → EVENT-CONSUMER/L1 → L4 → L5/OBSERVABLE** 관계로 연결한다. 선택 모형의 필요한 조건만 적용하며, 모든 미래 핵종·반응의 완료를 이번 작은 단위의 선행 AND gate로 만들지 않는다.

기존 18/18 PASS opacity 응답, 원 atomic provider `d870ce943005bf93e332ca32ca8c945798b1331c`, 알려진 25×23 target/source-template Jacobian을 재사용한다. 새 계산은 선언한 photon/target/energy 상태의 coupled collision residual 및 그 상태 변수들에 대한 전체 국소 Jacobian을 검산하는 최소 child로 제한할 수 있다. 이것은 동역학적 우주 진화, history/geometry coupling, stopping 또는 관측된 실제 n/T abundance를 자동 승인하지 않는다.

대칭성·게이지 축은 관측자/프레임·시간·단위·고정 comoving reference를 명시하는 일이다. 불변량 축은 isotope/charge, 한 번만 배정한 photon/internal/primary-electron energy와 그 Jacobian 상쇄다. 관측가능량 축은 선택된 source support와 명시한 state에서의 rate/energy response이며, 아직 시간적 abundance trajectory나 전 우주 관측량이 아니다.

새 중앙 정책의 기본 reference는 고정된 comoving Nref와 nref=nref0*a^-3이다. 외부 주입·핵변환을 실제 H/baryon 수의 변화와 함께 계산하더라도 이 bookkeeping reference는 자동 변경하지 않는다. 바뀌는 physical reference를 선택한 경우에만 Sref와 (S_s−x_s Sref)/nref 및 그 미분을 별도 공급한다.

## 예산과 예약

- Main: 595.225063/600 CPU s, NO_MORE_IVPs, N6 HOLD.
- Source continuation: 8.001104/10 CPU s, 8.029615335010021/20 wall s. 남은 1.998896 CPU s 자체는 새 query set의 승인서가 아니다. 현재 사용자의 다음 loop 요청에 대해 root가 새 bounded query/command/stopping 계약을 먼저 고정한다.
- Render: 15.533337507/16 CPU s. 기존 cap 확대 없음.
- Packaging: 보수적 과거 미계측 debit을 포함한 4.978747874/30 CPU s와 4.988865237/60 wall s를 보존.
- 이 intake 담당자의 과학 실행·IVP·완료 과학 재실행·외부 변경은 모두 0. Metadata read/hash 비용은 미계측이며 0으로 주장하지 않는다.
- ANGTHERM02는 current owner branch를 읽기만 한다. Owner live dirty/unpushed 상태는 관측되지 않았다.
- 중앙의 별도 compiler 30 CPU s allowance는 이미 끝난 다른 단위의 계약이며 이번 pilot에 이식하지 않는다.

## 게시 후보

사용자가 이번 턴에 backup/publication/자동 실행 권한을 명시 승인했다. 다음 위치는 아직 존재하지 않는 것으로 실제 tree와 ref에서 확인했다.

- 새 branch: `research/rei-grid044-coupled-collision-20261025`
- base branch: `research/orchestration-sandbox-20261022`
- 고정 base commit: `78f7ac5864d5817ceb79b48cb5e298cc30006510`
- 추가 소유 경로: `research/rei_grid044_opacity_consumer/coupled_collision_20261025/**`
- additive draft PR, force=false, merge=false. 게시 직전 HEAD를 새로 확인한다.
- 기존 `research/rei_chem_ledger_20261025`는 중앙 mirror로 보존하며 새 compiler를 만들지 않는다.
- 공개 Git/전달 archive에는 원본 private 대화, 관련 없는 외부 metadata, 전문 저작물과 무필터 intake dump를 넣지 않는다. Task-filtered scientific summary, 필요한 source identity와 유한 fixtures만 공개한다.

전역 과학 완료율은 **null**이다. n/T의 물리 생성·분기·daughter/stopping 입력, 실제 coupled history, geometry feedback와 최종 all-selected-isotope/ion pilot 관측량 gate는 열린 상태로 보존한다.
