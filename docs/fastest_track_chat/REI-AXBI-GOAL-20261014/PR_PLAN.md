# 목표 개발 PR 묶음

현재 문서·machine goal 변경은 기존 [draft PR117](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/117)의 codex/rux-science-delivery-20261014에 nonforce append한다. 확인한 base는 477f3756044df89ff63cceb6b432e63015c07f0a이며 actual publication SHA는 최종 반환으로만 채운다. 동시 원격 변경이 있으면 덮어쓰지 않고 관련 diff를 확인한다. 이 문서 작성자가 git mutation을 수행한 것은 아니다.

| Local planned ID | 범위 | 노드·산출물 |
|---|---|---|
| AX-GOAL-UPDATE | 사용자 채택 abundance 목표, 실행 전이 복구, 기존 metadata 두 항목 정정 | GOAL/DAG/state/packets/campaign/output contract, goal prompt, retained 감사 reuse; 기존 PR117 update |
| AX-P0 | 실제 source-backed 입력/provider/domain/background 결정 | AX01/02/03, 지원 전체 구간·species/normalization·μ-even/non-tilted·feedback budget |
| AX-P1 | source callback/coupled driver/first supported intervals | AX04/05/06, actual emissivity와 ray/packet/RHS/ledger, new-seam targeted tests·CSV/plot/pilot |
| AX-P2 | 전체 FLRW/AXBI abundance histories·signed cases·error/robustness | AX07/08/11/12, checkpoints/raw data, convergence/paired abundance and source/IC sensitivity |
| AX-P3 | abundance plots·보고서·독립 판정·release | AX13/14/15/16, abundance_vs_time/Tgas, tex/PDF/CSV/figures·reproduce commands |
| AX-SECONDARY | τ/visibility receiver 또는 추가 supported isotope/precision | AX09/10은 default OFF; 실제 요청·source/domain에 따라 독립 활성화 |

AX-*는 planned local ID이며 GitHub PR 번호가 아니다. 앞으로 node마다 PR를 하나씩 만들 의무는 없다. 실제 준비·구현·결과가 잘 묶이는 단위로 small diffs를 게시하고 actual number/URL을 반환한다. sibling supplier 변경은 그 owner의 확인된 checkout/scope에서 수행하며, repo 또는 branch 이름만으로 mutation 허가를 확장하지 않는다.

기존 101 open PR snapshot은 [이전 inventory](../REI-CODEX-SCIENCE-20261014/PR_INVENTORY.json)로 보존한다. PR117 추가와 현재 updates 때문에 live count는 달라졌다. 전체 PR를 merge하는 계획이 아니며 selected immutable source와 필요한 delta만 가져온다. main의 stale source를 base로 쓰지 않는다.

같은 checkout에서 coordinator 한 명만 checkout/stage/commit/push한다. shared Rust 파일 owner는 하나고 independent writers는 disjoint paths를 쓴다. dirty/untracked와 scientific old receipts를 보존하며 자동 worktree/clone·force push·타 branch merge를 하지 않는다. 과거 budget 예외/CI fmt FAIL·test skip을 green이라고 재서술하지 않고 이번 docs 변경으로 CI retry/Rust rerun을 하지 않는다.

각 implementation PR는 actual source/config/commands·exit·raw output과 new-seam scope를 제시한다. 과학 independent decision과 Git publication은 구분한다. abundance goal의 actual 전체 history/plots가 없으면 scientific goal IN_PROGRESS/HOLD이며 문서 push 자체는 goal 완료가 아니다. 결과가 나올 때 report를 갱신하고 준비된 next task로 자동 전이한다.
