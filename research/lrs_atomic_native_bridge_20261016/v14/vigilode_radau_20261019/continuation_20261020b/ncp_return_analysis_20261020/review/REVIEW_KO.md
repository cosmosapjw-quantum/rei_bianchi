# 독립 Astra 검토 — 현재 source NCP 반환과 유한 저장 출력 비교

**판정: PASS_SCOPED_NCP_EXECUTION_AND_FINITE_SAVED_OUTPUT_AGREEMENT. 차단할 과학·구현 결함은 발견하지 않았다.**

검토자는 `/root/independent_review`이며 native borrowed 구현, 비교 inspector, 인계 문서 수정을 수행하지 않은 별도 agent다. 이번 검토는 실제 저장된 입력·결과·source snapshot과 제안 diff의 읽기 및 유한 자료 비교로 수행했다. native 재실행과 build는 0회다. 실행 source는 `5248822167e3fbe374f4333f7f2efdcdbfdaeeaf`, metadata 기준 HEAD는 `90c46b3d305ae7d1c3a6d54cd5de6b55dfdc70ec`로 구분한다.

## 인정한 실행과 일치 범위

반환된 locked release build exit 0, Rust unit 4 + integration 6 PASS, 기존 cell-cache 19설정 모두 exit 0·completed true·failure null을 확인했다. 19설정은 10 Radau와 9 SSPRK 대조이고, 새 과학 설정 수는 0이다. 모든 cache 입력에 기록된 native binary SHA256은 `c93db685071037797d057f58d2fc88d5dccd5255b3d6441cd1a55d9a2d7f7992`다. 누적 RHS 시도는 38,840이다.

| 비교 | 유한 수치 leaves | 기타 leaves | containers | 물리·구조·공통 work 차이 |
|---|---:|---:|---:|---:|
| C10 v2 **borrowed** 19 대 NCP cache 19 | 316,559 | 114 | 24,346 | 0 |
| 기존 cache N16 fixed/birth/disabled 3 대 NCP cache | 154,411 | 18 | 11,864 | 0 |
| NCP cache N2 대 반환 borrowed N2의 독립 직접 비교 | 3,397 | 6 | 237 | 0 |

첫 19개 baseline을 cache라고 해석하지 않았다. 세 supplemental cache 대조는 기존 19설정에 포함되는 재비교이며 22개의 unique 설정이 아니다. inspector 전체와 실제 실행 outcome을 읽고 script/result hash를 확인했으며, 별도 구현으로 fixed Radau N2, birth Radau N16, disabled SSPRK N16의 config·initial·마지막 record를 직접 비교했다. 이 선택된 세 subtree에서도 값·타입·구조 차이는 없었다. 물리적 `dt_s`는 비교에 포함되고 timing과 evaluation mode/clone 계수는 따로 분류된다.

이번 결과는 해당 유한 저장 자료의 일치다. 일반 정확성, 일반 차수, stiff 안정성, 양수성 정리 또는 새로운 모델의 admission으로 확대하지 않는다. 저장 JSON의 signed-zero difference 0도 C10 전체의 bitwise 검증으로 소급하지 않는다.

## source 근거의 두 층

637 source payload, native 원본 152, pin에 해당하는 VigilODE 477의 전체 closure는 **90c46b에 게시된 이전 독립 검토를 재사용**한다. 이번 reviewer가 그 전체를 새로 재감사했다고 주장하지 않는다.

이번에는 실제 `sources.tar.gz`의 mapping과 bytes를 읽어 adapter `src/lib.rs`, `src/main.rs`, native addon `axbi_native_rhs.rs`의 세 SHA256을 직접 확인했다. 정확한 hash와 원본 read path는 동반 JSON에 기록했다. inspector에 남은 “full closure is independent reviewer responsibility” 문구는 이 명시적 근거 재사용으로 충족하며 추가 의무 감사나 native 재실행을 만들지 않는다.

## borrowed N2의 provenance 제한

borrowed 폴더에는 raw·stdout·stderr·exit가 있고, own argv·inputs·outcome·binary hash receipt는 없다. exit 0과 `CellBorrowed` raw, finite physical equality는 직접 확인했다. 같은 source/binary라는 연결은 상위 delivery receipt의 진술이다. 이를 borrowed 각 process의 독립 executable-hash binding으로 바꾸어 쓰지 않는다.

이것은 **유한 저장 출력 일치와 반환 완료를 막지 않는 provenance 제한**이다. native 실패로 분류하거나 누락된 command를 추정하지 않으며, 이 기록 한계만으로 완료된 실행을 다시 요구하지 않는다. N2의 RHS 395, preparations 2,680, node visits 252,800은 같고 지정 state/node clone은 cache 338/216,320 대 borrowed 0/0이다. 이 계수는 zero allocation이나 RSS 감소를 뜻하지 않는다.

## timing과 packaging 해석

raw `wall_s`의 19설정 합은 4.937230308 s다. 실제 source는 초기화 전에 clock을 시작하고 JSON serialization 전에 raw `wall_s`를 저장하며, 파일 기록 후 stderr COMPLETE clock을 다시 읽는다. 따라서 cache raw 0.041180299 s, borrowed raw 0.061808789 s, borrowed stderr COMPLETE 0.091509 s는 서로 다른 측정 경계다. 모순이나 독점 RHS CPU 시간으로 해석하지 않는다. 이 단일 N2 및 cross-host 저장 출력에서 speedup을 주장하지 않는다.

archive 내부 historical delivery JSON의 terminal literal backslash-n은 원본 bytes를 보존한 채 해석했다. 게시된 corrected JSON은 별도다. 이 packaging 한계는 물리 실행 실패가 아니다. 현재 source의 repository CI cargo fmt 실패·cargo test skipped는 NCP adapter의 실제 build/test PASS와 구분하며 green CI를 주장하지 않는다.

## inspector와 문서 diff

최종 inspector v2는 explicit evidence/output 경로, 정확한 19 + 3 입력 집합, case identity, source suffix 집합, physical/work/classification/source mismatch의 diagnostic escalation을 갖는다. v1 증거는 보존됐고 v2는 저장 raw만 재분석해 exit 0을 기록했다. script SHA256은 `971b12b4be7b44ddd6930ef94f99ceb84b416d8f09cec9ec007e3249fa8fe2ae`, result SHA256은 `2b4889c7c5a3c4ac5122783836461cd03f9b8d3e1ceba6a70b05409dadc06fd4`다.

제안 19파일은 기존 상태·인계 9개 수정, 반환 분석 문서 5개, inspector 증거 5개다. manifest와 실제 bytes가 일치했다. Rust/native/numerical source 수정은 없다. 이전 C10 NOT_RUN을 이력으로 보존하면서 현재 source를 COMPLETED_SCOPED로 연결하며, 과거 ROOT_ADMISSION·ACK·CI·원본 raw를 다시 쓰지 않는다. DAG는 반환→회수→분석→독립 검토→root admission→Git 게시→archive→양쪽 full readback→ACK/최종 Git의 상태를 분리한다.

이 판정은 검토 당시의 **게시 전 snapshot**을 대상으로 한다. root가 이 판정과 실제 게시·백업 receipt를 반영하여 pending 필드를 닫는 것은 정상 후속 절차다. 아직 수행되지 않은 Git 게시나 provider full readback을 이 검토가 대신 인증하지 않는다.

## 유지할 한계와 다음 행동

default legacy, 성능 경로와 batch cell-cache, borrowed는 명시적 실험 옵션이다. total-H 기준과 `e=x+Y(y+2z)`, `Y=.2454/[4(1-.2454)]`, 원시 P/C/R/D 및 binding/heat/cooling/escape/CMB/work의 분리를 유지한다. source-on 일반2차, uniform stiff, 일반 양수성, Case B/full EoR/signed Bianchi, 넓은 positive-CMB/비영 boundary, continuous global certificate와 CSV에 없는 photon-energy/boundary-photon 완전 회계는 인정하지 않는다. speedup·memory reduction은 NOT_ESTABLISHED, production은 NOT_ISSUED다.

승인된 단계별 게시와 백업을 실제 receipt로 완료한다. 완료된 native build·시험·19설정·borrowed N2를 반복할 필요는 없다. 실제 profile이 병목을 특정할 때에만 후속 optimizer 하나를 고른다.
