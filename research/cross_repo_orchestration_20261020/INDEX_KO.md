# 저장소별 실행 인계와 실제 게시 기록

각 링크는 실행 코드를 바꾸지 않는 실제 전달 문서 commit에 고정했다. 최신 반환이 추가되었는지 현지에서 먼저 조사하고, 같은 source/config의 완료 결과를 재사용한다. 사용자의 파일 다운로드나 경로 입력은 필요하지 않으며 Codex가 Git와 문서의 provider ID에서 직접 확보한다.

[통합 과학 보고서](REPORT_KO.md) · [통합 DAG](DAG.json) · [게시 영수증](DELIVERY_PUBLICATIONS.json) · [백업 영수증](BACKUP_DELIVERY.json)

| Repo | 새 변경/채택 | 다음 실행·의존성 | 장문 인계 | PR |
|---|---|---|---|---|
| BASS_HE | 14 focused tests; absence-only continuation, group watchdog | HE29 pairs observed 0/4; host UNKNOWN | [고정 문서](https://github.com/cosmosapjw-quantum/BASS_HE/blob/38c10ef63667376ce56ec2e9e8c3022986555333/research/he29_survival_budget_20261018/orchestration_20261020/NCP_HANDOFF_KO.md) | [PR79](https://github.com/cosmosapjw-quantum/BASS_HE/pull/79) |
| WU088_HH | PHYS71 D3 reused; resolvent route | optimized L64 host check/run; HH_R10 OFF | [고정 문서](https://github.com/cosmosapjw-quantum/WU088_HH/blob/50fabaf48332549d368374c50baac40f334fadb0/research/hh_orchestration_20261020/NCP_HANDOFF.md) | [PR122](https://github.com/cosmosapjw-quantum/WU088_HH/pull/122) |
| bass_cr | 2269 exact recovered files published; H/I guards backed by real receipts | G/H native and conditional I pilot | [고정 문서](https://github.com/cosmosapjw-quantum/bass_cr/blob/edcf6cde39b64833fed231953cbb4f8731e272cc/research/cr_orchestration_20261020/NCP_ORCHESTRATION_KO.md) | [PR86](https://github.com/cosmosapjw-quantum/bass_cr/pull/86) |
| bass | 11 tests; compensated C99 source adapter | physical donor and proper paired export input dependent | [고정 문서](https://github.com/cosmosapjw-quantum/bass/blob/56137bcbe1f32ae6948a4992970bf652fc233f37/research/bass_orchestration_20261020/NCP_HANDOFF_KO.md) | [PR175](https://github.com/cosmosapjw-quantum/bass/pull/175) |
| rec_bianchi | 10 tests + actual final 2-step C/Python parity | h4 first event+2 and independent h2 low-z | [고정 문서](https://github.com/cosmosapjw-quantum/rec_bianchi/blob/1ad0380110621446c42df9d995fd85db3a6c7e7a/research/rec_r3q_h4_continuation_20261020/HANDOFF_KO.md) | [PR111](https://github.com/cosmosapjw-quantum/rec_bianchi/pull/111) |
| rei_bianchi | 11 tests + scoped Markov defect review | optimized LRS19 and age32; nonlinear tube remains open | [고정 문서](https://github.com/cosmosapjw-quantum/rei_bianchi/blob/84a87002dde79426c6202611699e9e4f9cb6cb8f/research/cross_repo_orchestration_20261020/NCP_HANDOFF_KO.md) | [PR212](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/212) |

장문의 실제 실행 명령은 각 PR 본문에도 실었다. CR은 PR85(H)→PR86(I)이며 실행용 I content는 `fe6bbaec2de5032b938aed0713623b9618ba70e6`, H content는 `40ea4bbd5b2eb1b0c82f8ec9d5fdc1c6324e44f8`이다. receipt/document HEAD로 실행 content pin을 대체하지 않는다. HE controller content는 `ed5adca43f474553a9bce7f5de45d464be5905cb`; REC R3Q content는 `8d6a9e40eb509f467b10a22d3a690c57b85b6131`이다.

S1 전체 새 코드/검토/REC raw 전달물: [Drive](https://drive.google.com/file/d/1_F5CobLmU-ltpS3Hp5q_pZRcUj7YLjZ-/view), Dropbox `id:BSpOijBcT10AAAAAAD_SYg`, `/BASS_DERIVATION_DOSSIERS_20260912/ORCHESTRATION_S1_REVIEWED_CODE_EVIDENCE_20261020.zip`, 19,546,220bytes, SHA256 `893c4dea262ed6f8c4dbcf35066b0d8197a0ad8cc5f922aec3c888ae6ee1d44f`. S1는 기존 대형 CR payload를 중복 수록하지 않는다. CR 전체 source는 이미 Git에 게시했고 원본 검증 archive는 [Drive](https://drive.google.com/file/d/1KlkxM5XII-v11hMCMGnjyEUnRaqKNpb1/view), SHA256 `3c30312161d06e85ab42bea38105b9ede26f97303441a47c6ce2aaccc7d0c537`를 사용한다.

BASS는 현재 compile/normalization 단계까지 준비됐다. 물리 donor closure와 actual paired event export 없이 NCP에서 전체 source-feedback 구현을 시작하라는 인계가 아니다. 나머지 인계도 원래 cap과 reviewer/owner 계약을 따른다. 재시작하지 않을 완료 항목은 보고서와 DAG에 기록했다.

한 host의 여섯 agent는 공통 allocation을 먼저 읽는다. age32 48worker와 다른 대형 campaign을 동시에 과대 배정하지 않는다. 원래 expired/closed allocation은 유지하고, 명시적으로 새로 정의한 REC event campaign만 별도 allocation으로 기록한다.

최종 통합 문서 capsule S2: [Drive](https://drive.google.com/file/d/1OZjEbwWhLBfhaiM3Us4DoCoJ3laJXcBL/view), Dropbox `id:BSpOijBcT10AAAAAAD_SYw`, 34,141bytes, SHA256 `63d8099d9663b1afb1fe5a02255bcae7e20b4739d41879915fc64f86cf45c25c`. 자신의 upload ACK는 immutable ZIP 이후 생성되므로 최종 Git BACKUP_DELIVERY에 기록했다. 세 단계 모두 provider ACK/size를 확인했고, 전체 remote archive를 다시 내려받았다고 주장하지 않는다.
