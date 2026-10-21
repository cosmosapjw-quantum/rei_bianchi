# 단계별 DAG·게시·보존 기록

기준일은2026-10-21UTC/2026-10-22KST다. 각 단계의 당시 상태와 뒤에 실제로 닫힌 보존 상태를 구분한다. Immutable P1/P2 archive 안의 packing-time pending 문구를 소급 수정하지 않았다.

| DAG 단계 | 실제 완료 증거 | 게시 | 백업·검증 | 다음 |
|---|---|---|---|---|
| I0 최신 결과 조사 | 798refs/38sourceblobs, runtime probes, coverage 한계 | P1 | P1 이중 전체 회수 PASS | O1 |
| O1 최적화 coding loop | exact HE32 source pin, prepared moments, prior parity 재사용 | P1 donor/계약, P2 결합 구현 | P1/P2 | P1 physics |
| P1 physics R1–R10 | frozen PHYSICAL_CONTRACT, 독립 PHYS-MATH PASS | checkpoint0d795da7… | Drive/Dropbox172736B/80members PASS | C1 |
| C1 implementation | source-backed rates,61-state joint RHS, light checks | scientific S | P2 | C7 |
| C7 bounded execution | 79nominal+3controls=82IVPs, 실패0,21,074epochs | S의 raw/receipts | P2의 전체 raw | C8 |
| C8 independent review | PHYS-MATH-CODE/raw/PNG10종, controller·layout 수정 | S의 감사 파일 | P2 | C10 |
| C10 scientific delivery | 419전체 파일 GET,494tree identity,501archive members×2provider | S2fd46785… | P2 이중 전체 회수 PASS | NEXT1 |
| Portable extraction | 실제 CLI exit0,0신규IVP, raw/core/PNG/CSV 불변 | 본 metadata의 receipt | terminal metadata capsule | 종료 |
| Final metadata/ACK | source와실행 및provider identity 연결 | 이후 expected-head metadata commit | terminal capsule의 실제 ACK/fullGET으로 닫음 | NEXT1 source intake |

## Scientific source와 immutable archive

S=2fd46785ef2e7af8c25c01387c89e00b3edf9e9b
Tree=51ef238f3d3fc0a14c6018c4674ab6a636977158
P1 parent=0d795da7f9114f89353c72a5829e5efcb64dfa44

P2=REI_HHELI_P2_SELFCONTAINED_20261021T154136Z.tar.gz
Bytes23591727; SHA256 ea6eafef3e982a8983cf4cf46dcbb9924bd3d6dc43cdba0e087bdaacb6d05841
Drive1yVhYWgDxirGL533iFzrZzvN1AMnWZ6tY; Dropboxid:BSpOijBcT10AAAAAAD_hnw
각 provider에서 HTTP200 전체 GET, 정확한 byte/SHA256/501members/modes를 확인했다.

Git은419개 delta 파일을 전체 회수했다. 실제 S의 tree가 P1에서 상속한75개 경로의 기존 byte 검증 증거와 연결되어 총494개 path/blob/mode/size identity가 닫혔다. No force/no merge/draft를 유지했다.

## 포장 이후의 terminal 기록

Metadata commit은 자기 SHA를 파일 안에 순환 참조하지 않는다. 그 commit의 실제 SHA/tree/readback과 위 archive/provider 증거를 하나의 마지막 delivery capsule에 담는다. Capsule 자체의 provider IDs 및 full-readback receipt는 최종 응답·terminal receipt에 남기고 ACK-of-ACK 반복은 하지 않는다.

최초 P1의 child upload 호출은 ACK 없이 정지하여 UNCERTAIN_NO_ACK로 보존했다. 삭제하거나 성공/실패로 추정하지 않았다. 이후 고유한 R1 이름의 실제 두 객체가 전체 검증을 통과했다. P2는 root의 순차 업로드로 완료했다.

기존 Rust cargo fmt workflow 실패는 기록했고, cargo test는 skipped였다. Python의 실제 실행·독립 감사·portable saved-data 검증과 서로 다른 상태다. 추가 수치 실행은 필요하지 않다.
