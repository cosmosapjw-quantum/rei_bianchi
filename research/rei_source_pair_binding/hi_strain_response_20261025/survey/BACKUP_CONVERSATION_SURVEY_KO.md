# 최신 백업·대화 근거 조사 — 2026-10-25

## 물리 입력에 대한 결론

새로 읽은 백업은 **H1 바닥상태 spontaneous RR의 조건부 유한 사슬 소비자**, **PHYS90의 조건부 공분산 셀**, **VigilODE D5의 strict callback 계약**을 추가한다. 선택한 원문의 범위에서 실제 HI 주입·밀도·초기 stock·기하의 시간 이력은 추가되지 않았다. 완료된 HI massive-stress의 입력이나 물리적 주장을 변경하지 않는다. 전역적인 입력 부재나 불가능성의 증명으로 사용하지 않는다.

RR 자료에는 z=2.479 source 행이 실제로 있다. 그 계약의 T=10000 K, ne=.14 cm^-3, HI/HII/HeI/HeII/HeIII=(.9,.1,.07,.02,.01) cm^-3는 고정된 bath 입력이며, exposure=10000 proper s는 impulsive 초기 population의 정의다. 실제 방사장 occupation, stimulated/total RR hazard 및 포획 뒤 PI feedback은 null/OPEN이다. 새 RR 사건의 photon/internal-energy 분배는 유용한 제공자 구성요소로 보존한다. 이 숫자를 실제 HI 시간 이력에 대입하는 별도의 결속은 이 조사에서 확보하지 않았다.

## 확인 범위

| 표면 | 이번 관측 | 이전 대비 | 종료 상태와 범위 |
|---|---:|---:|---|
| Drive 지정 폴더 | 214 항목 | 추가·변경·누락 0 | 직접 자식 목록, 요청 상한 1000 미만, 자식 폴더 0. 도구가 end cursor를 노출하지 않음 |
| Dropbox `/bianchi/research_backups` | 171 항목 | 추가 11, 변경·누락 0 | recursive, `has_more=false`, cursor 빈 값 |
| 최근 파일 목록 | 562 고유 항목 | 추가 64, 변경·누락 0 | `modified_after=2026-10-22T00:00:00Z`, 200+200+162의 3페이지, `next_cursor=null` |
| 최신 대화 검색 | 실제 요청 1회 | 현재 이용 불가 | 응답: `Personal context is unavailable for this conversation.` |

목록은 2026-10-25T03:10:51Z 무렵 시작했다. 최근 목록의 실제 수정시각 범위는 2026-10-22T00:42:38.549362Z–2026-10-25T03:10:39.305127Z다. 페이지 수신 시각과 요청 원문은 비공개 영수증에 보존했다. 순회 시작 뒤의 동시 변경까지 포함한다고 주장하지 않는다.

최근 추가 64항목 중 35항목이 이 연구 관련 파일이다. RR 2개, PHYS89/90, VigilODE D4/D5, 완료된 HI stress의 단계·최종 파일 및 진행 보고를 분류했다. 나머지 29항목은 이 연구 범위 밖이다. 각 항목의 정확한 이름·식별자·수정시각과 선택 이유는 `RELEVANT_NEW_FILES.json`에 있다. 목록 열람은 모든 payload의 완독이나 모든 백업 저장소의 전수조사를 뜻하지 않는다.

## 새로 읽은 내용과 정확한 경계

| 자료 | 직접 읽은 범위 | 사용 가능한 새 정보 |
|---|---|---|
| `BASS_CR_N5_RR_MILNE_EXECUTION_20261025_V1.zip` | 실제 18,214,054 B 수신, 156개 멤버의 directory, 선택한 10개 텍스트·JSON | ground spontaneous H1 RR, zero-recoil stationary-heavy-target convention, 고정 bath의 새 유한 사슬 소비자. 실제 HI history는 결속되지 않음 |
| `VIGILODE_D5_CALLBACK_FINAL_20261025.zip` | 실제 611,081 B 수신, 113개 멤버의 directory, 선택한 6개 텍스트·JSON | strict full-write RHS/Jacobian gateway, manufactured 2-species input, scoped 20/20. 실제 BASS/native physical provider 결속은 OPEN |
| `PHYS90_NEXT_THREAD_HANDOFF_FINAL_KO.md` | 전체 169행, `has_more=false` | FINAL `9d32d115c0b8c5d5b2ce3a66ebc4a7f277334fcc`, science `60d062104438b3f99553a74d210e9c2b48ed2dd3`. 공분산 pair-cell/envelope의 조건부 결과; actual nuclear consumer ACK 없음 |
| `PHYS89_NEXT_THREAD_HANDOFF_FINAL_KO.md` | 전체 107행, `has_more=false` | FINAL `480baabc73ebaaba735d285d969e79177f5545ed`. bare-kernel source/consumer parent는 `PARTIAL_INPUT_DEPENDENCIES` |
| `D4_NEXT_THREAD_HANDOFF_KO.md` | 전체 82행, `has_more=false` | FINAL `3c8877ea0409495752dcfab42426e679e3ba92d3`, scoped 20/20 전달. 실제 native owner/physics 결속은 별도 |
| `rei_bianchi_IGM_progress_20261025_0100_KO.pdf` | 전체 추출 텍스트 13페이지/668행, `has_more=false`, 이미지·render 0 | nominal 01:00 UTC 보고가 재사용한 실제 evidence cutoff는 전날 23:49:54.850 UTC. 여섯 물리 입력을 명시하며 후속 stress 완료나 새 donor를 덮어쓰지 않음 |

RR archive freeze는 2026-10-25T03:07:35.895579Z다. 그 안의 T0 publication은 `386f4d304eda5ba9a53d17b446ca1289789460dd`이며 S/M1 pending은 당시 상태다. 현재 Git의 후속 게시 여부는 별도의 repo 조사에 따른다. 이 백업의 pending 문구로 더 최신 Git 상태를 되돌리지 않는다.

RR의 `inputs/reused/c23d/ATOMS_2.479.csv`는 43,485 B이며 manifest SHA256은 `2a330ffcd520eec96dae5b24658b3c8d801ced37e392b6f3f46a0a9155ed85f7`다. 계약은 세 개의 384-atom source table을 재사용한다. native HI 4368-atom 입력과의 동일성을 이 조사에서 주장하지 않는다.

D5 최종 publication receipt는 `a01f1c5c78e6b06e23565cd4e482716f99efbe97` / tree `aae39da3b00d4070a03db29aaa65c49613684bc9`를 기록한다. 실행 source는 `0c73202734a52f30e4214d455be0fa9c47d37e0f`다. 이 값은 실제 읽은 archive receipt의 핀이며, 이번 agent가 새로 Git ref를 관측한 값은 아니다.

## 대화와 기존 근거의 재사용

현재 Personal Context 호출은 이용 불가였다. 이전 조사에서는 실제로 이용 가능했고, 보존된 `PERSONAL_CONTEXT_RAW.json`에 `[c0]`–`[c7]`의 검색 참조와 당시 파일 단서가 있다. 그 원문을 역사적 단서로 읽었으며 최신 대화를 전수 열람한 것으로 세지 않았다. 이전 단서는 HI의 proper t/z(t), nHI/nref/Href, 초기 stock/epoch, ai/Hi/frame, stopping/secondary heat/photon supply를 OPEN으로 기록한다. 최신 원문을 확인한 새 백업도 이 결속을 제공하지 않는다.

이전 498개 파일의 식별자·메타데이터는 이번 목록에서도 변하지 않았다. 기존 CR104 및 D4 S1 아카이브의 이전 선택 열람을 재사용했고 다시 다운로드하지 않았다. 별도 source-intake가 맡은 사용자 첨부파일은 이 조사에서 다시 열지 않았다.

## 남아 있는 물리 입력

1. t0/t1/z(t)/source(t)의 실제 cohort 이력.
2. nHI/nref/XHI와 물리적 부피 또는 동등한 정규화.
3. 초기 ν0 또는 N0/U0/L0와 epoch.
4. frame/clock과 실제 ai(t)/Hi(t).
5. 공통 μ_t(k,Ω), support L(t), angular model의 시간별 결속.
6. transport/collision/photon supply 및 그 에너지·ownership 결속.

현재 확보한 정적 입력에 대한 순간 strain response를 선택할 경우, 위 이력을 새로 가정했다고 기록하지 않고 현재 native 입력의 범위에서 계약을 세울 수 있다. 이 문서는 그 선택에 필요한 R1/R2 근거만 제공하며 새 과학 채택·계산을 수행하지 않았다.

## 실행·복구 영수증

이번 조사: 목록 호출 5회(Drive 1, Dropbox 1, 최근 목록 3), Personal Context 1회, 파일 본문 read 1회/4파일, 선택 archive 수신 2개, 선택 멤버 16개. 과학 실행·시험·CAS·render·Git 변경·provider 쓰기·새 clone은 모두 0이다.

Archive의 whole SHA는 수신한 bytes에서 측정했다. 선택한 멤버만 실제로 읽었으며 전체 멤버 CRC/payload 복원이나 모든 provider 사본의 복원을 주장하지 않는다. 최초 다운로드 helper 시작은 필요한 current companion 미배치로 import 단계에서 실패했고, 해당 current companion을 배치한 같은 두 파일의 요청은 성공했다. 과학 재시도는 0이다.

공개 요약·입력 색인은 이 폴더에, raw 대화/목록/소유자 메타데이터·다운로드·선택 원문은 `private/`에 분리했다. 복구 사본은 `/tmp/rei_next_recovery_20261025/survey/backups/`에 보존한다.
