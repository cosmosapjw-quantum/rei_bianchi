# BASS_HE A2 — asymptotic structure

현재 authoritative 판정은 `RESULT.json` 및 `review/A2_INDEPENDENT_REVIEW.json`이다: **SMALL_LARGE_R_ASYMPTOTICS_CLOSED**, 명시한 exact R10R pair와 frame/projector 범위에 한정한다. 전체 프로그램 또는 수치 정확도 완료가 아니다.

## 읽는 순서

1. `BASS_HE_POST_R10R_THEORY_CLOSURE_REPORT_KO.md`: 새 결과·실제 검증·미수행 작업.
2. `A2_ASYMPTOTIC_DERIVATION_KO.md`: 통합 유도 및 새 coefficient, error order, global existential bound, ETF/PQ 구조.
3. `derivations/SMALL_R_AUTHOR_KO.md`, `derivations/LARGE_R_AUTHOR_KO.md`: 상세 proof components. 각 author note의 독립검토 전이라는 문구는 작성 당시 상태이며, 현재 admission은 review가 소유한다.
4. `review/`: 별도 reviewer의 수식·domain·phase·claim 심사와 exact final identities.
5. `NEXT_HANDOFF_KO.md`: 다음 단일 C1. C1은 준비 상태이며 이번에 실행하지 않았다.

한 번의 Wolfram exact CAS 입력은 `code/A2_EXACT_CHECKS.wl`, 실제 raw response는 `evidence/WOLFRAM_RAW_RESPONSE.json`이다. Stateless evaluator에서 입력 전체를 한 번 평가했으며 engine version은 도구가 공개하지 않았다. Exact algebra check는 functional proof의 대체물이 아니다. Physical Python/eigensolver/collision run은 없다. 변경 없는 이전 suites를 재실행하지 않았다.

`BASS_HE_COUPLING_DATABASE.csv`의 12행은 symbolic/analytic records다. 새 measured/predicted benchmark data를 생성하지 않았다. B1 matrix 및 uncertainty ledger는 A1b 바이트 그대로 유지했다. Global comparison weight는 bound의 증명을 위한 것으로, coupling 보간식이나 model fit이 아니다.

## Provenance와 공개 범위

Public namespace: `research/shared_c64/20261001/A2_ASYMPTOTIC_STRUCTURE_20261001T0318Z`.
Branch: `research/shared-c64-crossrepo-20260928`. Parent: `771b1fe1b70930196a0f812bdb118bec04049c8c`.
Scientific source pin: `1a83a67e12de1ddc2aede0ff67168f7071450ab3`.

`PUBLIC_MANIFEST.json`의 payload와 manifest 자체를 게시한다. Self-reference를 피하여 manifest는 자신의 payload 목록에서 제외한다. 원문 PDF 및 private input은 게시하지 않는다. Source notes는 원전 위치와 identity 및 허용된 주장만 기록한다. Literature-only remainder gap 판정과 이번 새 direct proof의 closure는 서로 다른 근거 상태다.

Private 전체 archive는 이전 A1b ZIP을 `private_dependencies/`에 그대로 포함한다. 이전 ZIP SHA256는 `419edbfcc6d36a396831b7279ab16d5aee16fbc6dede324f770ffcb771d6aa2f`이고 그 안에 A1/B1/source v3가 중첩되어 있다. 새 GK1961 원문 PDF도 private-only다. BHL2008은 web fulltext 열람만 했으며 local-byte backup을 주장하지 않는다.

새 archive의 MANIFEST/CRC/SHA256는 전송 무결성 증거다. Git remote blob·size, provider upload ACK·metadata, 실제 raw restore, scientific validation을 구분한다. Publication과 provider object ID는 별도의 delivery receipt에 둔다.

CODE_I02_CLOSED=true; full_certificate_fail_closed=true; scientific_PROMOTE=HOLD; Eq55_next_node_authorized=false; Eq55=NOT_RUN; production_default_change=NOT_AUTHORIZED.
