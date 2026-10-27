# R1–R10 / C1–C10 단계별 게시·백업

이번 유한 단위의 이론10단계와 코딩10단계의 근거를 완료했다. 원본 DAG 완료수는 모든 단계에서 **32/88**이며 중앙 별도 branch는 **27/88**이다. 단계 수를 원본 노드 완료수에 더하지 않는다.

| 단계 | 수행 내용 | 완료/전체 | 게시·이중 백업 |
|---|---|---|---|
| R1 | 연구 위치·계약 | **32/88** | A · 8057f121 — source 및 Drive/Dropbox ACK 완료 |
| R2 | 근거·재사용 | **32/88** | B · fdc782b5 — source 및 Drive/Dropbox ACK 완료 |
| R3 | 주장·전제 정렬 | **32/88** | B · fdc782b5 — source 및 Drive/Dropbox ACK 완료 |
| R4 | 가설·표현 탐색 | **32/88** | B · fdc782b5 — source 및 Drive/Dropbox ACK 완료 |
| R5 | 구성적 유도 | **32/88** | B · fdc782b5 — source 및 Drive/Dropbox ACK 완료 |
| R6 | 독립 검증 | **32/88** | B · fdc782b5 — source 및 Drive/Dropbox ACK 완료 |
| R7 | 판별 검증 | **32/88** | D · 600503e5 — source 및 Drive/Dropbox ACK 완료 |
| R8 | 결과 판정 | **32/88** | D · 600503e5 — source 및 Drive/Dropbox ACK 완료 |
| R9 | 정식 결과·코딩 연결 | **32/88** | D · 600503e5 — source 및 Drive/Dropbox ACK 완료 |
| R10 | 종료·재개 | **32/88** | D · 600503e5 + 최종 전달 metadata — source 및 Drive/Dropbox ACK 완료 |
| C1 | 목표·baseline | **32/88** | B · fdc782b5 — source 및 Drive/Dropbox ACK 완료 |
| C2 | 식–데이터–코드 | **32/88** | B · fdc782b5 — source 및 Drive/Dropbox ACK 완료 |
| C3 | 수치 설계 | **32/88** | B · fdc782b5 — source 및 Drive/Dropbox ACK 완료 |
| C4 | 실행 DAG·자원 | **32/88** | B · fdc782b5 — source 및 Drive/Dropbox ACK 완료 |
| C5 | 구현 | **32/88** | C · 20b91606 — source 및 Drive/Dropbox ACK 완료 |
| C6 | 구현 검증 | **32/88** | D · 600503e5 — source 및 Drive/Dropbox ACK 완료 |
| C7 | 과학 검증 | **32/88** | D · 600503e5 — source 및 Drive/Dropbox ACK 완료 |
| C8 | 수치·재현성 | **32/88** | D · 600503e5 — source 및 Drive/Dropbox ACK 완료 |
| C9 | 독립 검토 | **32/88** | D · 600503e5 — source 및 Drive/Dropbox ACK 완료 |
| C10 | 판정·인계 | **32/88** | D · 600503e5 + 최종 전달 metadata — source 및 Drive/Dropbox ACK 완료 |

각 단계의 실제 근거는 stages/ 문서에 있다. 같은 immutable source를 사용하는 단계는 하나의 검증된 checkpoint를 공유한다. 단계별 추가 과학 실행은 뜻하지 않는다.

| Checkpoint | 범위 | ZIP SHA256 | Drive ID | Dropbox ID |
|---|---|---|---|---|
| A | R1 | 80f62074885041a5b2d1d314a40611c1254eb9a0024330d9aa859c9ca21e3346 | 1T1PhuhmqdA-bmUIY8XiqBfpz21kHgw35 | id:BSpOijBcT10AAAAAAEC3hw |
| B | R2–R6,C1–C4 | 85110ebc845b8c0041b0f92bb9030e5513fa1805244ad3bd362c319fe97f2801 | 1jpOGQ9k-xWpGNUxD2rWXsPaSo0e3CMqf | id:BSpOijBcT10AAAAAAEC3oA |
| C | C5 | cc772e1de0b2b73a357a54df7f7913a2556de33004a17c960f1ffd9f7377b068 | 1GdVd144CTIrDO3IAH3pgEuZxO223qvxu | id:BSpOijBcT10AAAAAAEC3pw |
| D | R7–R10,C6–C10 source | 61d8e954c661d2c1d2f204bdf81f81414a892514b19464d6a676ec9376ec4122 | 1U-r38TGeJsGGF4xoEd8AewCNkutGUToz | id:BSpOijBcT10AAAAAAEC4PQ |

D 이후 최종 ACK·예산·handoff metadata를 별도로 보존한다. 그 자체의 관측된 ACK는 delivery/FINAL_DELIVERY_RECEIPT.json에 추가한다. Source ZIP 자기 hash나 자기 upload ACK를 그 이전 snapshot 내부에 주장하지 않는다.

최종 전달 metadata도 이중 백업 ACK를 받았다: REI_THERMAL_ASSIMILATION_DELIVERY_20261027_600503e5.zip, 58,759 bytes, SHA256 8244a2d199759f1f33749585066f01df06480c60161132b85b084008505e7582. Drive 1XjFho8O3A2GIzo0Rk1HH7ReDZaJNIPto, Dropbox id:BSpOijBcT10AAAAAAEC4Tw. 실제 post-upload ACK는 최종 Git 전달 영수증에 보존한다.
