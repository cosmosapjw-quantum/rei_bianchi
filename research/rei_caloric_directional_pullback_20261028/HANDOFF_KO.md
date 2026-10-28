# 다음 스레드 인계 — caloric directional 단위

현재 결과는 [PR244](https://github.com/cosmosapjw-quantum/rei_bianchi/pull/244)의 draft로 게시했다. 이론은 완료했고 구현의 실제 실행은 남아 있다. 이 문서는 최종 PR243 원장 갱신을 반영한다. 이전20/56 실행 제안은 현재 제안이 아니다.

## 복사 가능한 인계

```text
$physmath-research-loop
PROJECT=cosmosapjw-quantum/rei_bianchi
UNIT=rei_caloric_directional_pullback_20261028
BRANCH=research/rei-caloric-directional-20261028
PR=244
BASE_PIN=3f299062a0d0d35c17f83a9e6081ca515e9d4c4c
FROZEN_SOURCE_PIN=9c2d0d286747d6e74f863a77c92f2f7cd03a3aa4
LATE_SOURCE_PR=243
LATE_SOURCE_PIN=48c5656c3ff396edf61390214c40cbdcc203f172
RESUME_STAGES=C6,C7,C8,C9,C10
AUTO_NEXT_NODE=false

사용자가 제공한 physmath1.0.0 절차를 우선한다.
완료: R1–R10=10/10, C1–C5=5/10, 새 단위15/20.
C6–C8=NOT_RUN; C9=static PASS_SCOPED_STATIC_PREPARATION,
runtime NOT_COMPLETE; C10=pending.
기존 finite_thermal_endpoint20/20와 supplied_caloric_branch20/20은
실제 PR242 근거의 재사용이다. 합산하지 않는다.
원래 DAG 작업33/88, 중앙28/88,88IDs/17edges,delta0.
실제 REI temperature/native25/physical radii=null.
L4_ready=false; global_physical_completion=null.
81-check와158-check는 동일 C8의 별도 근거이고 atomic-storage20/20은 다른 단위다.

먼저 research/rei_caloric_directional_pullback_20261028 안의
HANDOFF_KO.md, FINAL_DELIVERY_RECEIPT.json,
execution/CURRENT_EXECUTION_AUTHORITY.json,
delivery/CLOSURE_STORAGE_ACK.json을 읽어라.
현재 branch head와 아래 코드 identity를 대조하라.
반복 전수조사, 이미 닫힌 R6/theory 재검토, 기존 suite 재실행은 하지 마라.
구체적으로 변경된 source/권한이 있으면 해당 의존성만 갱신한다.

핵심 결과:
D1: dT=(1-w)a_i+w*a_(i+1)
    +[v-(1-w)b_i-w*b_(i+1)]/s_i.
D2 at E=U_j: q=v-b_j; q>0 right, q<0 left, q=0 dT=a_j.
Lower endpoint q>=0; upper q<=0; outward refusal.
Unequal adjacent slopes에는 하나의 Frechet derivative가 없다.
Equal-slope interior knot는 공통 differential을 갖는다.
D3: df=J_z*dz+f_T*dT; f_T는 명시적으로 공급되어야 한다.
Fixed-rate chemical 결과에서 physical f_T=0을 추정하지 마라.

관측 가능한 독립 reviewer task=/root/current_repo_census.
실제 독립 유도 후 코드/테스트/runner/plot을 읽었다.
R6=PASS_SCOPED_INDEPENDENT_THEORY.
보고서 SHA256=9094988ff115861688f458f807150dc1be1ef96a754d0e8d903dd52dfbda53fa.
이 작업은 source-census context와 공유 filesystem이 있으므로 blind라고 부르지 않는다.
별도 backend model/process UUID는 관측되지 않았다.

아직 새 numerical/presentation allowance는 승인되지 않았다.
PR243 최신 charged: planning17.295332885, presentation54.561494494.
이 값은 PR242 inherited charge를 포함한다. PR242 값을 다시 더하지 마라.
PR24318/55 임시승인은 종료했고 원래10/30으로 복원됐다.
현재 제안: planning 누적cap20/reserve2; presentation 누적cap60/reserve4.
AGENTS의 원래 기준 대비50% 이상 증액 조항 때문에 명시적 새 승인이 필요하다.
이전cap56 제안은 superseded이다.
Main595.225063/600 NO_MORE_IVPs, UNKNOWN_NOT_ZERO, 닫힌 예약을 보존한다.
별도 native F1 display0.037과 다른 chain F1 child0.026759를 임의 합치지 마라.
타 owner 예산 이전이나 cumulative debit reset을 하지 마라.
현재 승인 메시지가 있다면 그 범위만 기록하고 실행하라.

승인 뒤 단위 root에서 단일 수치 명령:
python -B -S execution/run_once.py --execute-authorized
한 worker,1 CPU-s/10 wall-s/256MiB, A–G만.
Optional H는NOT_SELECTED이다.
원시 STDOUT.json, STDERR.txt, PROCESS.json과 실제 exit/accounting을 보존하라.
Runner의 historical PR242 비용 필드는 과거 snapshot이다.
현재 누적 원장은 CURRENT_EXECUTION_AUTHORITY를 기준으로 additive 기록하라.
실패시 원자료를 보존하고 원인·범위를 특정하라. 같은 상태 자동 retry는 하지 마라.

성공한 저장 결과와 presentation 승인 뒤 단일 명령:
timeout --signal=TERM --kill-after=1s 30s prlimit --cpu=4:4 --as=536870912:536870912 -- python -B figures/plot_saved.py --execute-authorized
한 invocation,4 CPU-s/30 wall-s/512MiB.
전체 command의 외부 OS accounting을 남기고 prefix/child/전체를 중복 합산하지 마라.
실제 생성 그림을 열어 확인하라. 원래 science를 다시 실행하지 마라.

실제 출력 공개 후 기존 static 판단과 구분된 독립 runtime 판단을 받는다.
기존 native reviewer가 살아 있으면 후속 task를 사용하고,
다른 세션이면 실제 새 distinct-author reviewer를 생성하라.
도구 없는 역할극/외부봇/CAS를 native reviewer로 부르지 마라.
실제 finding이 있을 때만 그 범위의 수정과 표적 검증을 한다.
검사 수만으로 과학적 수용을 정하지 마라.
C6–C10의 실제 완료 단계마다 게시·Drive/Dropbox 백업과 실제 ACK,
새 단위수 및 원래33/88·중앙28/88·delta0를 기록하라.
```

## 재개할 정확한 파일

| 대상 | SHA256 |
|---|---|
| THEORY_AND_CONTRACT.md | 92e067c1cd6cc81cddbd1bd1e91fbc5025ea78914f041db69f42fe7ead2f5758 |
| deps/caloric_branch.py | ac5e5d50a454185550ba5614e50e914b7dad613795cf743347bd8b0b41c61aef |
| implementation/directional_pullback.py | 13f26afa9ecbfa367609f0391367ca11c0a9991154c02a6d6ba19d9add1ff753 |
| tests/test_directional_pullback.py | 336b3d9dabbe21d42f9797cb1566c98a08fbe397ea66d6f856ef787f0accfd4f |
| execution/run_once.py | a3f25b697171a15929a906a25037a647202d85407bf4611daaec37861c3c3c52 |
| figures/plot_saved.py | 4a3f94682d7ed809e2ccfc0d8f87b2a2f2304c5155be672ee3e299d73f28a4b6 |

Dependency Git blob은 bc3ebd682c363afc7d5c36d164406086145b6964다.
현재 local source projection은 /workspace/scratch/cc0531120bc9/rei_loop_continuation_20261028/unit/ 이며, 다른 세션에서는 게시된 source/백업으로 복원한다. 이 경로를 Git checkout으로 간주하지 않는다.

## 저장 근거와 조사 범위

완료15단계 각각은 별도 capsule로 두 provider에 저장했고, 별도 metadata 크기가 일치했다. delivery/STAGE_DELIVERY_ACKS.json이 각 commit/Drive ID/Dropbox ID/SHA/bytes를 담는다. 34개 frozen 게시 파일의 Git blob 대조는 delivery/PUBLICATION_READBACK.json에 있다.

전체 관련 조사 보존 파일은11,248,557bytes, SHA256 cda51e1b0fcbf06942d620d9be97d0813f650a11f0668da517c3db960b5fef00, Drive1JrhoRLfG6g-IU39ESOke3QDmgUxu4T5T, Dropboxid:BSpOijBcT10AAAAAAEFUzQ다. PR243 후속 자료와 이 handoff는 별도 final capsule에 보존하며 실제 ACK는 delivery/CLOSURE_STORAGE_ACK.json을 따른다. 자기 자신의 ACK를 포함시키려고 고정 capsule을 재포장하지 않는다.

당시 관련15repos/1469refs/1442tips/최근698commits/70PRs 조사와 후속PR243 판독을 구분한다. 모든 비공개 대화·삭제 refs·미push 작업·모든 backup 본문을 읽었다는 주장은 없다. Drive dossier1000개 이후 페이지 제한과 대화 전체 열거 미제공을 보존한다. 실제 source 원문/읽은 구간과 남은 의무는 SURVEY_SYNTHESIS_KO.md, survey_summaries/PRIMARY_READ_LEDGER.md 및 supplements/PR243_UPDATE.md를 따른다.

다음 physical application의 입력은 동일 reference-volume/thermal-store의 실제 recipient EOS·state/composition·discrepancy certificate와 해당 callback의 temperature derivative다. 새 mathematically exact adapter의 완료를 이 입력의 공급으로 취급하지 않는다.
